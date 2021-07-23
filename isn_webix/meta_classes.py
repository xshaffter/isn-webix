from django.conf import settings
from django.db.models.fields.related_descriptors import ForwardManyToOneDescriptor, ForwardOneToOneDescriptor
from rest_framework.serializers import SerializerMetaclass, Field
from collections import OrderedDict


# noinspection PyProtectedMember,PyMethodParameters
class WebixSerializerMetaclass(SerializerMetaclass):
    @classmethod
    def _get_declared_fields(cls, bases, attrs):
        display = getattr(settings, 'DISPLAY_SUFFIX', 'display')
        fields = [(field_name, attrs.pop(field_name))
                  for field_name, obj in list(attrs.items()) if isinstance(obj, Field)]
        if 'Meta' in attrs:
            meta_class = attrs['Meta']
            auto_display_fields = []
            for field_name in meta_class.fields:
                attr = getattr(meta_class.model, field_name, None)
                display_name = '{}__{}'.format(field_name, display)
                if (isinstance(attr, ForwardManyToOneDescriptor) or isinstance(attr,
                   ForwardOneToOneDescriptor)) and display_name in dict(fields).keys():
                    auto_display_fields.append(display_name)
            attrs['Meta'].fields = tuple(auto_display_fields + list(meta_class.fields))
        fields.sort(key=lambda x: x[1]._creation_counter)

        for base in reversed(bases):
            if hasattr(base, '_declared_fields'):
                fields = [(field_name, obj) for field_name, obj
                          in base._declared_fields.items() if field_name not in attrs] + fields
        return OrderedDict(fields)
