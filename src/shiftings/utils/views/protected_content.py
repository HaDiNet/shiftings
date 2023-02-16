import posixpath

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse


@login_required
def serve_protected(request, path: str):
    path = posixpath.normpath(path).lstrip("/")
    _, name = path.rsplit('/', 1)
    response = HttpResponse()
    response["Content-Disposition"] = "attachment; filename=" + name
    # nginx uses this path to serve the file
    response["X-Accel-Redirect"] = path
    # apache uses this path to send a file
    response["X-SENDFILE"] = path
    return response
