import sys

from api_auto_doc.utils import ReadOnly
from api_auto_doc.views import BaseViewSet
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from isn_webix.mixins import WebixListModelMixin
from isn_webix.serializers import SelectListSerializer, RejectionSerializer, ApproveSerializer, RequestApprovalSerializer


# noinspection PyProtectedMember,PyBroadException,PyAttributeOutsideInit,PyUnresolvedReferences
class WebixBaseModelViewSet(BaseViewSet):
    choice_fields = list()

    @action(detail=False, methods=['get'], serializer_class=SelectListSerializer)
    def select_list(self, __):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset[:10], many=True)
        return Response(serializer.data)

    # noinspection PyMethodMayBeStatic
    def get_choice(self, choices=tuple()):
        data = [dict(id=identifier, value=value) for identifier, value in choices]
        return Response(data)


    def get_serializer_class(self):
        try:
            serializer_class = getattr(self, sys._getframe(2).f_code.co_name).kwargs.get('serializer_class')
        except:
            serializer_class = self.serializer_class
        return serializer_class or self.serializer_class

    def dispatch(self, request, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        request = self.initialize_request(request, *args, **kwargs)
        self.request = request
        self.headers = self.default_response_headers
        caught_except = False
        exc = None
        response = None
        # noinspection PyBroadException
        try:
            self.initial(request, *args, **kwargs)
            handler = getattr(
                self, request.method.lower(),
                self.http_method_not_allowed
            )
            if request.method.lower() not in self.http_method_names:
                handler = self.http_method_not_allowed
            response = handler(request, *args, **kwargs)
        except Exception as exc:
            caught_except = True
        if caught_except:
            if self.action and "_choice_field_" in self.action:
                # noinspection PyBroadException
                try:
                    field_dict = next(item for item in self.choice_fields if item["name"] == self.action)
                    response = self.get_choice(field_dict['field'].choices)
                except Exception:
                    response = self.handle_exception(exc)
            elif exc:
                response = self.handle_exception(exc)
        self.response = self.finalize_response(request, response, *args, **kwargs)
        return self.response

    # noinspection PyProtectedMember
    def __init__(self, *args, **kwargs):
        super(BaseModelViewSet, self).__init__(*args, **kwargs)
        self.model = self.queryset.model
        fields = self.model._meta.fields
        choice_fields = list()
        choice_urls = dict()
        for field in fields:
            if len(field.choices) > 0:
                name = "{}_choice_field_{}".format(self.model._meta.model_name, field.attname)
                choice_fields.append(dict(name=name, field=field))
                choice_urls['/api/{}/choice_field/{}/'.format(self.model._meta.model_name, field.attname)] = {
                    'methods': ['get'],
                    'fields': ['id', 'value']
                }
                setattr(self, name, self.get_choice())

        self.choice_fields = choice_fields
        self.extra_urls = choice_urls


class WebixReadOnlyModelViewSet(mixins.RetrieveModelMixin,
                                WebixListModelMixin,
                                WebixBaseModelViewSet):
    permission_classes = [ReadOnly]


class WebixRetreiveOnlyModelViewSet(mixins.RetrieveModelMixin,
                                    WebixBaseModelViewSet):
    permission_classes = [ReadOnly]


class WebixDetailModelViewSet(mixins.RetrieveModelMixin,
                              mixins.CreateModelMixin,
                              mixins.DestroyModelMixin,
                              WebixBaseModelViewSet):
    pass


class WebixCRUDModelViewSet(mixins.CreateModelMixin,
                            mixins.RetrieveModelMixin,
                            mixins.UpdateModelMixin,
                            mixins.DestroyModelMixin,
                            WebixListModelMixin,
                            WebixBaseModelViewSet):
    pass


class WebixRUDModelViewSet(mixins.RetrieveModelMixin,
                           mixins.UpdateModelMixin,
                           WebixListModelMixin,
                           WebixBaseModelViewSet):
    pass


# noinspection PyUnresolvedReferences
class FlowModelViewSet(object):

    @action(detail=True, methods=['put'], serializer_class=RejectionSerializer)
    def reject(self, request, pk=None):
        model = self.queryset.model
        instance = get_object_or_404(model, pk=pk)
        serializer = self.get_serializer(instance=instance, data=request.data)
        if serializer.is_valid(raise_exception=True):
            comment = request.data.get('comment')
            message = instance.reject(comment)
            return Response(status=status.HTTP_200_OK, data={'message': message})

    @action(detail=True, methods=['put'], serializer_class=ApproveSerializer)
    def approve(self, request, pk=None):
        model = self.queryset.model
        instance = get_object_or_404(model, pk=pk)
        serializer = self.get_serializer(instance=instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        message = instance.approve()
        return Response(status=status.HTTP_200_OK, data={'message': message})

    @action(detail=True, methods=['put'], serializer_class=RequestApprovalSerializer)
    def request_approval(self, request, pk=None):
        model = self.queryset.model
        instance = get_object_or_404(model, pk=pk)
        serializer = self.get_serializer(instance=instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        message = instance.request_approval()
        return Response(status=status.HTTP_200_OK, data={'message': message})

    def get_queryset(self, user=None):
        queryset = self.queryset.all()
        if user and not user.has_perm(self.model().VIEW_ALL_PERMISSION):
            queryset = queryset.filter(attendant=user)
        return queryset


class FlowCRUDModelViewSet(WebixCRUDModelViewSet, FlowModelViewSet):
    pass


class FlowRUDModelViewSet(WebixRUDModelViewSet, FlowModelViewSet):
    pass
