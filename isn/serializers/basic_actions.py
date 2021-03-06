from rest_framework import serializers
from isn.models import FlowModel


# noinspection PyAbstractClass
class RejectionSerializer(serializers.Serializer):
    comment = serializers.CharField(required=True, allow_blank=False)

    def validate(self, attrs):
        if self.instance.status != FlowModel.APPROVAL_REQUESTED:
            raise serializers.ValidationError("Only drafts that requested for approval can be rejected.")
        return attrs

    def __init__(self, *args, **kwargs):
        super(RejectionSerializer, self).__init__(*args, **kwargs)


# noinspection PyAbstractClass
class ApproveSerializer(serializers.Serializer):

    def validate(self, attrs):
        if self.instance.status != FlowModel.APPROVAL_REQUESTED:
            raise serializers.ValidationError("Only drafts that requested for approval can be approved.")
        return attrs

    def __init__(self, *args, **kwargs):
        super(ApproveSerializer, self).__init__(*args, **kwargs)


# noinspection PyAbstractClass
class RequestApprovalSerializer(serializers.Serializer):

    def validate(self, attrs):
        if self.instance.status != FlowModel.CREATED:
            raise serializers.ValidationError("Only drafts can request for approval.")
        return attrs

    def __init__(self, *args, **kwargs):
        super(RequestApprovalSerializer, self).__init__(*args, **kwargs)
