import re

from django.db import models


class GenericObjectsManager(models.Manager):
    def get_queryset(self):
        return models.QuerySet(self.model).filter(activo=True)


    def get_or_none(self, **kwargs):
        """
            para no utilzar try catch en cada busqeda regresamos
            none si no encontramos
        """
        try:
            return self.get(**kwargs)
        except self.model.DoesNotExist:
            return None

    def list(self, *args, **kwargs):
        qs = self.get_queryset().filter(*args, **kwargs)
        return qs.order_by('nombre')


class CommonModel(models.Model):
    objects = GenericObjectsManager()
    objects_all = models.Manager()
    activo = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated_on = models.DateTimeField(auto_now=True, auto_now_add=False)

    def __init__(self, *args, **kwargs):
        super(CommonModel, self).__init__(*args, **kwargs)
        self.classname = re.sub(r'((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))', r' \1', type(self).__name__)

    def __unicode__(self):
        pk = self.lead_id if hasattr(self, 'lead_id') else self.pk
        return '{} #{}'.format(self.classname.title(), pk)

    def field_name(self):
        return type(self).__name__.lower()


    class Meta:
        abstract = True