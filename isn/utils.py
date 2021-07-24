from collections import OrderedDict

from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.response import Response


class WebixPagination(LimitOffsetPagination):
    # Usage example @ https://isnstudio.myjetbrains.com/youtrack/articles/MIS-A-2/Listado-API-para-Webix(Backend)
    limit_query_param = 'count'
    offset_query_param = 'start'
    max_limit = None
    default_limit = 10

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('total_count', self.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('pos', self.offset),
            ('data', data)
        ]))