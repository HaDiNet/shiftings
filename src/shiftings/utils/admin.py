from django.contrib import admin, messages
from django.db.models import Model
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _

import csv
import io


class AdminActionMixin:
    """Reusable admin actions for many models.

    Actions are defensive: they detect required fields at runtime and
    notify the admin user if the action is not applicable for the model.
    """

    def _model_opts(self):
        return self.model._meta

    def _has_change_perm(self, request):
        opts = self._model_opts()
        perm = f"{opts.app_label}.change_{opts.model_name}"
        return request.user.has_perm(perm)

    def export_as_csv(self, request, queryset):
        if not queryset.exists():
            self.message_user(request, _('No items selected.'), level=messages.WARNING)
            return

        opts = self._model_opts()
        field_names = [f.name for f in opts.concrete_fields]

        pseudo_buffer = io.StringIO()
        writer = csv.writer(pseudo_buffer)
        writer.writerow(field_names)

        for obj in queryset:
            row = [getattr(obj, f) for f in field_names]
            writer.writerow([str(v) if v is not None else '' for v in row])

        resp = HttpResponse(pseudo_buffer.getvalue(), content_type='text/csv')
        resp['Content-Disposition'] = f'attachment; filename={opts.model_name}_export.csv'
        return resp
    export_as_csv.short_description = _('Export selected as CSV')

    def duplicate_selected(self, request, queryset):
        if not self._has_change_perm(request):
            self.message_user(request, _('Permission denied.'), level=messages.ERROR)
            return

        created = 0
        errors = 0
        for obj in queryset:
            try:
                obj.pk = None
                obj.save()
                created += 1
            except Exception:
                errors += 1

        msg = []
        if created:
            msg.append(_('%d objects duplicated.') % created)
        if errors:
            msg.append(_('%d objects failed to duplicate.') % errors)
        self.message_user(request, ' '.join(msg))
    duplicate_selected.short_description = _('Duplicate selected')

    def toggle_active(self, request, queryset):
        if not self._has_change_perm(request):
            self.message_user(request, _('Permission denied.'), level=messages.ERROR)
            return

        toggled = 0
        for obj in queryset:
            for name in ('active', 'is_active', 'enabled'):
                if hasattr(obj, name):
                    val = getattr(obj, name)
                    setattr(obj, name, not val)
                    obj.save()
                    toggled += 1
                    break

        if not toggled:
            self.message_user(request, _('No boolean active field found on selected models.'), level=messages.WARNING)
        else:
            self.message_user(request, _('%d objects toggled.') % toggled)
    toggle_active.short_description = _('Toggle active for selected')

    def send_email_to_selected(self, request, queryset):
        # Simple synchronous send; safe for small batches and dev environment.
        if not queryset.exists():
            self.message_user(request, _('No items selected.'), level=messages.WARNING)
            return

        sent = 0
        missing = 0
        from django.core.mail import send_mail

        for obj in queryset:
            email = getattr(obj, 'email', None)
            if not email:
                missing += 1
                continue
            try:
                send_mail(_('Message from admin'), _('There might be an issue with your account. Please contact us.'), None, [email])
                sent += 1
            except Exception:
                # Don't crash the whole action for one failing send
                missing += 1

        self.message_user(request, _('%d emails sent, %d missing/failed.') % (sent, missing))
    send_email_to_selected.short_description = _('Send a simple email to selected')


class BaseModelAdmin(AdminActionMixin, admin.ModelAdmin):
    actions = (
        'export_as_csv',
        'duplicate_selected',
    )


class RelatedObjectsFilter(admin.SimpleListFilter):
    related_model = None
    related_model_filter: dict[str, object] = {}
    related_label_field = 'name'
    queryset_filter_field = ''
    include_empty_choice = False
    empty_choice_label = _('No organization')
    empty_choice_value = 'none'
    empty_queryset_filter: dict[str, object] = {}

    def related_queryset(self):
        if self.related_model is None:
            raise ValueError('related_model must be set')
        return self.related_model.objects.filter(**self.related_model_filter).distinct()

    def lookups(self, request, model_admin):
        choices = [(
            str(obj.pk),
            getattr(obj, self.related_label_field),
        ) for obj in self.related_queryset()]
        if self.include_empty_choice:
            choices.append((self.empty_choice_value, self.empty_choice_label))
        return choices

    def queryset(self, request, queryset):
        value = self.value()
        if not value:
            return queryset
        if self.include_empty_choice and value == self.empty_choice_value:
            if self.empty_queryset_filter:
                return queryset.filter(**self.empty_queryset_filter).distinct()
            return queryset.filter(**{f'{self.queryset_filter_field}__isnull': True}).distinct()
        if not self.queryset_filter_field:
            raise ValueError('queryset_filter_field must be set')
        return queryset.filter(**{f'{self.queryset_filter_field}__pk': value})


def register_models(*models: type[Model], admin_class: type[admin.ModelAdmin] | None = None) -> None:
    """Register models with the site.

    By default models are registered with `BaseModelAdmin` so they receive
    the global admin actions. Pass `admin_class` to override.
    """
    if admin_class is None:
        admin_class = BaseModelAdmin

    for model in models:
        admin.site.register(model, admin_class)
