# -*- coding: utf-8 -*-
from __future__ import absolute_import  
from django.http import HttpResponseRedirect, HttpResponse
from django.db.models import Q
from django.core.paginator import Paginator, InvalidPage, EmptyPage

from .functions import to_int
from .decorators import render_to


@render_to()
def list_view(request, objects, template='utils/list.html' , title='', 
              edit_url='', variables={}, parent_template = 'base.html', 
              nodo_actual=None, pag_size=25):
              

    o = request.GET.get('o', '')

    if request.GET.get("page_size"):
        pag_size = int(request.GET.get("page_size"))


    if o > '':
        objects = objects.order_by(o)

    
    paginator = Paginator(objects, pag_size)
        
    try:
        page = int(request.GET.get('pag', '1'))
    except ValueError:
        page = 1
    
    try:
        list = paginator.page(page)
    except (EmptyPage, InvalidPage):
        list = paginator.page(paginator.num_pages)
        
    if page < 5:
        _page = page
        page_ = 10 - page
    else:
        _page = 5
        page_ = 5
    
        if (page+5) > list.paginator.num_pages:
            page_ = list.paginator.num_pages - page
            _page = 10 - page_

    pages_ant = page-_page if (page-_page) > 0 else 0
    pages = [p for p in list.paginator.page_range]
    page_range = pages[pages_ant:page+page_]
    
    
    variables['page_range'] = page_range
    variables['list'] = list
    variables['title'] = title
    variables['edit'] = edit_url
    variables['parent_template'] = parent_template
    variables['q'] = request.GET.get('q', '')
    variables['o'] = o

    variables['TEMPLATE'] = template
    if nodo_actual:
        variables['NODO_ACTUAL'] = nodo_actual
    return variables