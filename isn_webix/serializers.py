from rest_framework import serializers


# noinspection PyAbstractClass
class SelectListSerializer(serializers.Serializer):
    id = serializers.CharField()
    value = serializers.SerializerMethodField()

    def get_value(self, instance):
        return instance.__unicode__()


# noinspection PyAbstractClass
class RejectionSerializer(serializers.Serializer):
    comment = serializers.CharField(required=True, allow_blank=False)
