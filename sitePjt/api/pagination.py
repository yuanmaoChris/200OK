from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.conf import settings


class CustomPagination(PageNumberPagination):
    page_size_query_param = 'size'

    def get_paginated_response(self, query, data_name, data):
        response = {
            'query': query,
            'count': self.page.paginator.count,
            'size': self.page.paginator.per_page,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            data_name: data
        }

        if not query:
            del response['query']
            
        if not self.get_next_link():
            del response['next']

        if not self.get_previous_link():
            del response['previous']

        return Response(response)