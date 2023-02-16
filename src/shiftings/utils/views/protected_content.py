import posixpath
from pathlib import Path

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils._os import safe_join


@login_required
def serve_protected(request, path: str):
    path = posixpath.normpath(path).lstrip("/")
    fullpath = Path(safe_join(settings.MEDIA_ROOT, path))
    response = HttpResponse()
    # nginx uses this path to serve the file
    response["X-Accel-Redirect"] = fullpath
    # apache uses this path to send a file
    response["X-SENDFILE"] = fullpath
    return response
