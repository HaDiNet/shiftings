from django.utils.translation import gettext_lazy as _


def not_implemented_text(method_name: str) -> str:
    return _('The function %(name)s has to be implemented.') % {
        'name': method_name
    }
