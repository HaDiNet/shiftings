from django import template
from django.template import TemplateSyntaxError
from django.template.base import FilterExpression, Parser
from django.template.loader import render_to_string

register = template.Library()


# define simplemodal block
@register.tag('simpleformmodal')
def simpleformmodal(parser: Parser, token):
    nodelist = parser.parse(('endsimpleformmodal',))
    parser.delete_first_token()
    tokens = [parser.compile_filter(p_token) for p_token in token.split_contents()]
    if len(tokens) != 4:
        raise TemplateSyntaxError(f'\"{tokens[0]!r}\" simpleformmodal tag requires form id title and url as arguments')

    return SimpleFormModalNode(nodelist, tokens[1], tokens[2], tokens[3])


class SimpleFormModalNode(template.Node):
    """
    Render a sidebar menuitem containing several others as a collapse
    """

    def __init__(self, nodelist, form_id: FilterExpression, title: FilterExpression, url: FilterExpression) -> None:
        self.nodelist = nodelist
        self.form_id = form_id
        self.form_title = title
        self.form_url = url

    def render(self, context):
        return render_to_string('template/simple_form_modal.html', {
            'nodelist': self.nodelist.render(context),
            'form_id': self.form_id.resolve(context),
            'form_title': self.form_title.resolve(context),
            'form_url': self.form_url.resolve(context),
        })
