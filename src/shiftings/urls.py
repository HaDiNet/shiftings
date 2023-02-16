"""shiftings URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import RedirectView, TemplateView

from shiftings.utils.views.protected_content import serve_protected

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='base.html')),
    path('i18n/', include('django.conf.urls.i18n')),
    path('user/', include('shiftings.accounts.urls.user')),
    path('shifts/', include('shiftings.shifts.urls')),
    path('organizations/', include('shiftings.organizations.urls')),
    path('events/', include('shiftings.events.urls')),
    path('calendar/', include('shiftings.cal.urls')),

    # totally legit search
    path('search/', RedirectView.as_view(url='https://www.youtube.com/watch?v=dQw4w9WgXcQ'))
]

urlpatterns.extend(static(settings.STATIC_URL, document_root=settings.STATIC_ROOT, show_indexes=True))
urlpatterns.extend(static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT))

if not settings.DEBUG:
    urlpatterns.extend(re_path(r'^media/(?P<file>.*)$', serve_protected, name='serve_protected_media'),)
