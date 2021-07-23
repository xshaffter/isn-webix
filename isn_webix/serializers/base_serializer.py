import six
from django.conf import settings
from rest_framework import serializers

from isn_webix.meta_classes import WebixSerializerMetaclass

RELATED_FIELDS = [serializers.SlugRelatedField, serializers.PrimaryKeyRelatedField]


@six.add_metaclass(WebixSerializerMetaclass)
class BaseSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        display = getattr(settings, 'DISPLAY_SUFFIX', 'display')
        super(BaseSerializer, self).__init__(*args, **kwargs)
        for field, value in self.fields.items():
            display_field = '{}__{}'.format(field, display)
            display_source = '{}.__unicode__'.format(field)
            if [1 for TYPE in RELATED_FIELDS if isinstance(value, TYPE)] and display_field not in self.fields:
                overriden_field_name = '{}__display'.format(field)
                self.fields[display_field] = serializers.CharField(source=display_source, allow_null=True)
