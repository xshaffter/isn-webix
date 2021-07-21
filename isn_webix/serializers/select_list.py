from rest_framework import serializers


# noinspection PyAbstractClass
class SelectListSerializer(serializers.Serializer):
    id = serializers.CharField()
    value = serializers.SerializerMethodField()

    def get_value(self, instance):
        return instance.__unicode__()