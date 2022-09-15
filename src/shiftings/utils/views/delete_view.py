from django.views.generic.edit import DeleteView as DjangoDeleteView


class DeleteView(DjangoDeleteView):
    template_name = 'generic/delete.html'
