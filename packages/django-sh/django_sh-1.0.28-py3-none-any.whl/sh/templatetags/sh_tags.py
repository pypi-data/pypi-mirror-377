from django import template
register = template.Library()

def easy_tag(func):
    """deal with the repetitive parts of parsing template tags"""
    def inner(parser, token):
        try:
            return func(*token.split_contents())
        except TypeError:
            raise template.TemplateSyntaxError('Bad arguments for tag "%s"' % token.split_contents()[0])
    inner.__name__ = func.__name__
    inner.__doc__ = inner.__doc__
    return inner   

class AppendGetNode(template.Node):

    def __init__(self, dict, complete):
        self.dict_pairs = {}
        self.complete = int(complete)
        for pair in dict.split(','):
            pair = pair.split('=')
            self.dict_pairs[pair[0]] = template.Variable(pair[1])
            
    def render(self, context):
        get = context['request'].GET.copy()
       
        for key in self.dict_pairs:
            get[key] = self.dict_pairs[key].resolve(context)
        
        from django.db.models import Model
        path = context['request'].META['PATH_INFO']
        if not self.complete:
            path = ""

        lista = []
        for key in get.keys():
            for value in get.getlist(key):
                lista.append("%s=%s" % (key, (value if not isinstance(value, Model) else value.id)))

        if len(get):
            path += "?%s" % "&".join(lista)
        
        
        return path

@register.tag()
@easy_tag
def append_to_get(_tag_name, dict, complete=1):
    return AppendGetNode(dict, complete)  