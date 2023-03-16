from typing import Any, TypeVar

from django import template
from django.template import TemplateSyntaxError
from django.template.base import TextNode
from django.template.loader_tags import BlockNode
from django.urls import reverse

register = template.Library()
T = TypeVar('T')


@register.filter
def concat(arg1: Any, arg2: Any) -> str:
    return str(arg1) + str(arg2)


@register.simple_tag()
def define(obj: T) -> T:
    return obj


@register.simple_tag(takes_context=True)
def active_param(context: dict[str, Any], param_name: str, param_value: Any) -> str:
    if context['request'].GET.get(param_name) == str(param_value):
        return 'btn-success'
    return ''


@register.simple_tag(takes_context=True)
def active(context: dict[str, Any], url: str) -> str:
    if str(context.get('request').path) == url:
        return 'active'
    return ''


@register.simple_tag()
def form_border(is_create: bool) -> str:
    return 'border-success' if is_create else 'border-primary'

# define breadcrumb block
@register.tag('breadcrumbs')
def do_breadcrumbs(parser, token):
    nodelist = parser.parse(('endbreadcrumbs',))
    parser.delete_first_token()
    tokens = token.split_contents()
    if len(tokens) != 1:
        raise TemplateSyntaxError(f'"{tokens[0]!r}" tag requires no argument.')
    nodelist.insert(0, TextNode('<ul class="breadcrumb">'))
    nodelist.append(TextNode('</ul>'))
    return BlockNode('breadcrumbs', nodelist)


@register.inclusion_tag('template/breadcrumb.html')
def breadcrumb(title, url_name=None, *args, **kwargs):
    return {
        'title': title,
        'url': reverse(url_name, args=args, kwargs=kwargs) if url_name else None
    }