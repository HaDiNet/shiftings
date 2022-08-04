from typing import Callable

from django.http import HttpRequest, HttpResponseForbidden
from django.template import loader

from shiftings.utils.exceptions import Http403


class Http403Middleware:
    def __init__(self, get_response: Callable):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        return self.get_response(request)

    def process_exception(self, request: HttpRequest, exception: Exception):
        if not isinstance(exception, Http403):
            return None
        template = loader.get_template('403.html')
        if exception is not None and len(str(exception)) == 0:
            exception = None
        return HttpResponseForbidden(template.render({'message': exception}, request=request))
