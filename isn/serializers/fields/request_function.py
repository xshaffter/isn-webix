from rest_framework import serializers


class RequestFunctionField(serializers.ReadOnlyField):
    def to_internal_value(self, data):
        pass
    def to_representation(self, value):
        return value(self.context['request'])