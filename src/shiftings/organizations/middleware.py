from typing import Callable

from django.http import HttpRequest

from shiftings.organizations.models import Organization


class OrganizationPermissionMiddleware:
    def __init__(self, get_response: Callable):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        return self.get_response(request)

    def process_template_response(self, request, response):
        if 'organization' in response.context_data:
            setattr(request, 'organization', response.context_data['organization'])
            return response
        for key, obj in response.context_data.items():
            if isinstance(obj, Organization) and key == 'organization':
                setattr(request, 'organization', response.context_data['organization'])
                return response
        for obj in response.context_data.values():
            if hasattr(obj, 'organization'):
                setattr(request, 'organization', obj.organization)
                return response
        return response
