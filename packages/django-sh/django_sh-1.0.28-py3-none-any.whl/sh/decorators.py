from django import forms
from django.template import RequestContext
from django.db.models import signals as signalmodule
from django.http import HttpResponse
from django.shortcuts import render
import json

__all__ = ['render_to', 'signals', 'ajax_request']


try:
    from functools import wraps
except ImportError: 
    def wraps(wrapped, assigned=('__module__', '__name__', '__doc__'),
              updated=('__dict__',)):
        def inner(wrapper):
            for attr in assigned:
                setattr(wrapper, attr, getattr(wrapped, attr))
            for attr in updated:
                getattr(wrapper, attr).update(getattr(wrapped, attr, {}))
            return wrapper
        return inner


def render_to(template=None, mimetype=None, beta_template=False):
   
    def renderer(function):
        @wraps(function)
        def wrapper(request, *args, **kwargs):
            output = function(request, *args, **kwargs)
            if not isinstance(output, dict):
                return output
            tmpl = output.pop('TEMPLATE', template)
            output['TEMPLATE'] = tmpl

            if beta_template:
                from admintotal.models import ConfiguracionGeneral
                from django.template.loader import get_template
                general = ConfiguracionGeneral.objects.get()
                if general.habilitar_beta:
                    try:
                        fname = tmpl.split('/')[-1]
                        template_beta = '%s__beta.%s' % tuple(fname.split('.'))
                        get_template(tmpl.replace(fname, template_beta))
                        output['TEMPLATE'] = tmpl.replace(fname, template_beta)
                        tmpl = tmpl.replace(fname, template_beta)
                    except Exception as e:
                        pass

            return render(request, tmpl, output, content_type=mimetype)
            
        return wrapper
    return renderer


class Signals(object):
    '''
    Convenient wrapper for working with Django's signals (or any other
    implementation using same API).

    Example of usage::


       # connect to registered signal
       @signals.post_save(sender=YourModel)
       def sighandler(instance, **kwargs):
           pass

       # connect to any signal
       signals.register_signal(siginstance, signame) # and then as in example above

       or 
        
       @signals(siginstance, sender=YourModel)
       def sighandler(instance, **kwargs):
           pass

    In any case defined function will remain as is, without any changes.

    (c) 2008 Alexander Solovyov, new BSD License
    '''
    def __init__(self):
        self._signals = {}

        # register all Django's default signals
        for k, v in signalmodule.__dict__.items():
            # that's hardcode, but IMHO it's better than isinstance
            if not k.startswith('__') and k != 'Signal':
                self.register_signal(v, k)

    def __getattr__(self, name):
        return self._connect(self._signals[name])

    def __call__(self, signal, **kwargs):
        def inner(func):
            signal.connect(func, **kwargs)
            return func
        return inner

    def _connect(self, signal):
        def wrapper(**kwargs):
            return self(signal, **kwargs)
        return wrapper

    def register_signal(self, signal, name):
        self._signals[name] = signal

signals = Signals()



class JsonResponse(HttpResponse):
    """
    HttpResponse descendant, which return response with ``application/json`` mimetype.
    """
    def __init__(self, data):
        super(JsonResponse, self).__init__(content=json.dumps(data), mimetype='application/json')



def ajax_request(func):
    """
    If view returned serializable dict, returns JsonResponse with this dict as content.

    example:
        
        @ajax_request
        def my_view(request):
            news = News.objects.all()
            news_titles = [entry.title for entry in news]
            return {'news_titles': news_titles}
    """
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        response = func(request, *args, **kwargs)
        if isinstance(response, dict):
            return JsonResponse(response)
        else:
            return response
    return wrapper

