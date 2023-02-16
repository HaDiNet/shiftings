import mimetypes
import posixpath
from pathlib import Path

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.utils._os import safe_join


@login_required
def serve_protected(request, file: str):
    path = posixpath.normpath(file).lstrip("/")
    fullpath = Path(safe_join(settings.MEDIA_ROOT, path))
    content_type, encoding = mimetypes.guess_type(str(fullpath))
    content_type = content_type or "application/octet-stream"
    response = HttpResponse()
    response['Content-Type'] = content_type
    # nginx uses this path to serve the file
    if settings.SERVE_MEDIA_SERVER == 'nginx':
        response["X-Accel-Redirect"] = str(fullpath)
    # apache uses this path to send a file
    elif settings.SERVE_MEDIA_SERVER == 'apache2':
        response["X-SENDFILE"] = str(fullpath)
    else:
        raise Http404('File not found maybe you forgot to set setting')
    return response
