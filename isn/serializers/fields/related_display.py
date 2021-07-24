from django.conf import settings
from rest_framework import serializers

DISPLAY_SUFFIX = getattr(settings, 'DISPLAY_SUFFIX', 'display')


# noinspection PyAttributeOutsideInit
class RelatedDisplayField(serializers.ReadOnlyField):
    def bind(self, **kwargs):
        super(RelatedDisplayField, self).bind(**kwargs)
        values = (self.source or self.field_name).split('__')
        self.source_attrs = values if values[-1] != DISPLAY_SUFFIX else values[0], '__unicode__'


    def to_internal_value(self, data):
        pass

    def get_attribute(self, instance):
        if len(self.source_attrs) > 2:
            raise AttributeError(
                'Got AttributeError when attempting to get a value for field '
                '`{field}` on serializer `{serializer}`.\nRelatedAttributeField '
                'only supports basic depth level to avoid performance problems.'.format(
                    field=self.field_name,
                    serializer=self.parent.__class__.__name__
                ))
        return super(RelatedDisplayField, self).get_attribute(instance)
