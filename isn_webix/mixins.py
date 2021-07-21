from api_auto_doc.views import LIST_SERIALIZER
from rest_framework.decorators import action

from isn_webix.utils import WebixPagination


# noinspection PyUnresolvedReferences
class WebixListModelMixin(object):
    list_serializer_class = None

    def get_list_serializer_class(self):
        return self.list_serializer_class or self.serializer_class

    def get_list_serializer(self, *args, **kwargs):
        serializer_class = self.get_list_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    @action(detail=False, methods=['get'], serializer_class=LIST_SERIALIZER)
    def wlist(self, request):
        queryset = self.filter_queryset(self.get_queryset()).order_by('-pk')
        paginator = WebixPagination()
        paginated = paginator.paginate_queryset(queryset, request, self)
        origin_field = None
        serializer_model = self.get_list_serializer_class().Meta.model
        if queryset.model != serializer_model:
            model_field = serializer_model().field_name()
            paginated = [getattr(item, model_field) for item in paginated if hasattr(item, model_field)]
            if paginated:
                origin_field = self.queryset.first().field_name()
        data = self.get_list_serializer(origin_field=origin_field, instance=paginated, many=True).data
        return paginator.get_paginated_response(data)
