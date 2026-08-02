from django.contrib import admin
from django.db.models import Model


def register_models(*models: type[Model]) -> None:
    for model in models:
        admin.site.register(model)
