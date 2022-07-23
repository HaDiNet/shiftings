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
from django.urls import include, path
from django.views.generic import RedirectView, TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='base.html')),
    path('i18n/', include('django.conf.urls.i18n')),
    path('user/', include('shiftings.accounts.urls.user')),
    path('shifts/', include('shiftings.shifts.urls')),

    # totally legit search
    path('search/', RedirectView.as_view(url='https://www.youtube.com/watch?v=dQw4w9WgXcQ'))
]

if settings.DEBUG:
    urlpatterns.extend(static(settings.STATIC_URL))
    urlpatterns.extend(static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT))
