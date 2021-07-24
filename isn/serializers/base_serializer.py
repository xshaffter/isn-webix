import six
from django.conf import settings
from rest_framework import serializers

from isn.meta_classes import WebixSerializerMetaclass
from isn.serializers.fields import RelatedAttributeField, RequestFunctionField, RelatedDisplayField

RELATED_FIELDS = [serializers.SlugRelatedField, serializers.PrimaryKeyRelatedField]
DISPLAY_SUFFIX = getattr(settings, 'DISPLAY_SUFFIX', 'display')


@six.add_metaclass(WebixSerializerMetaclass)
class BaseSerializer(serializers.ModelSerializer):
    def build_property_field(self, field_name, model_class):
        if ('self', 'request', field_name) == getattr(model_class, field_name).__code__.co_varnames:
            field_class = RequestFunctionField
            return field_class, {}
        return super(BaseSerializer, self).build_property_field(field_name, model_class)

    def build_field(self, field_name, info, model_class, nested_depth):
        if '__{}'.format(DISPLAY_SUFFIX) in field_name:
            return RelatedDisplayField, {}
        if '__' in field_name:
            return RelatedAttributeField, {}
        return super(BaseSerializer, self).build_field(field_name, info, model_class, nested_depth)
