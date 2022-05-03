from rest_framework.pagination import _positive_int,_get_displayed_page_numbers,_get_page_links,BasePagination
from base64 import b64decode, b64encode
from collections import OrderedDict, namedtuple
from urllib import parse

from django.core.paginator import InvalidPage
from django.core.paginator import Paginator as DjangoPaginator
from django.template import loader
from django.utils.encoding import force_str
from django.utils.translation import gettext_lazy as _

from rest_framework.compat import coreapi, coreschema
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.utils.urls import remove_query_param, replace_query_param

class PageNumberPagination(BasePagination):
    """
    A simple page number based style that supports page numbers as
    query parameters. For example:
    http://api.example.org/accounts/?page=4
    http://api.example.org/accounts/?page=4&page_size=100
    """
    # The default page size.
    # Defaults to `None`, meaning pagination is disabled.
    page_size = api_settings.PAGE_SIZE

    django_paginator_class = DjangoPaginator

    # Client can control the page using this query parameter.
    page_query_param = 'page'
    page_query_description = _('A page number within the paginated result set.')

    # Client can control the page size using this query parameter.
    # Default is 'None'. Set to eg 'page_size' to enable usage.
    page_size_query_param = None
    page_size_query_description = _('Number of results to return per page.')

    # Set to an integer to limit the maximum page size the client may request.
    # Only relevant if 'page_size_query_param' has also been set.
    max_page_size = None

    last_page_strings = ('last',)

    template = 'rest_framework/pagination/numbers.html'

    invalid_page_message = _('Invalid page.')

    def paginate_queryset(self, queryset, request, view=None):
        """
        Paginate a queryset if required, either returning a
        page object, or `None` if pagination is not configured for this view.
        """
        page_size = self.get_page_size(request)
        self.custom_page_size=self.get_page_size(request)
 
        if not page_size:
            return None

        paginator = self.django_paginator_class(queryset, page_size)
        page_number = self.get_page_number(request, paginator)

        try:
            self.page = paginator.page(page_number)
        except InvalidPage as exc:
            msg = self.invalid_page_message.format(
                page_number=page_number, message=str(exc)
            )
            raise NotFound(msg)

        if paginator.num_pages > 1 and self.template is not None:
            # The browsable API should display pagination controls.
            self.display_page_controls = True

        self.request = request
        return list(self.page)

    def get_page_number(self, request, paginator):
        page_number = request.query_params.get(self.page_query_param, 1)
        if page_number in self.last_page_strings:
            page_number = paginator.num_pages
        return page_number

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('status', True),
            ('total_records', self.page.paginator.count),
            ('current_page', self.page.number),
            ('record_per_page',  self.custom_page_size),
            ('next_page_link', self.get_next_link()),
            ('previous_page_link', self.get_previous_link()),
            ('results', data)
        ]))

    def get_paginated_response_schema(self, schema):
        return {
            'type': 'object',
            'properties': {
                'count': {
                    'type': 'integer',
                    'example': 123,
                },
                'next': {
                    'type': 'string',
                    'nullable': True,
                    'format': 'uri',
                    'example': 'http://api.example.org/accounts/?{page_query_param}=4'.format(
                        page_query_param=self.page_query_param)
                },
                'previous': {
                    'type': 'string',
                    'nullable': True,
                    'format': 'uri',
                    'example': 'http://api.example.org/accounts/?{page_query_param}=2'.format(
                        page_query_param=self.page_query_param)
                },
                'results': schema,
            },
        }

    def get_page_size(self, request):
        if self.page_size_query_param:
            # print(self.page_size_query_param)
            try:
                return _positive_int(
                    request.query_params[self.page_size_query_param],
                    strict=True,
                    cutoff=self.max_page_size
                )
            except (KeyError, ValueError):
                pass

        return self.page_size

    def get_next_link(self):
        if not self.page.has_next():
            return None
        url = self.request.build_absolute_uri()
        page_number = self.page.next_page_number()
        return replace_query_param(url, self.page_query_param, page_number)

    def get_previous_link(self):
        if not self.page.has_previous():
            return None
        url = self.request.build_absolute_uri()
        page_number = self.page.previous_page_number()
        if page_number == 1:
            return remove_query_param(url, self.page_query_param)
        return replace_query_param(url, self.page_query_param, page_number)

    def get_html_context(self):
        base_url = self.request.build_absolute_uri()

        def page_number_to_url(page_number):
            if page_number == 1:
                return remove_query_param(base_url, self.page_query_param)
            else:
                return replace_query_param(base_url, self.page_query_param, page_number)

        current = self.page.number
        final = self.page.paginator.num_pages
        page_numbers = _get_displayed_page_numbers(current, final)
        page_links = _get_page_links(page_numbers, current, page_number_to_url)

        return {
            'previous_url': self.get_previous_link(),
            'next_url': self.get_next_link(),
            'page_links': page_links
        }

    def to_html(self):
        template = loader.get_template(self.template)
        context = self.get_html_context()
        return template.render(context)

    def get_schema_fields(self, view):
        assert coreapi is not None, 'coreapi must be installed to use `get_schema_fields()`'
        assert coreschema is not None, 'coreschema must be installed to use `get_schema_fields()`'
        fields = [
            coreapi.Field(
                name=self.page_query_param,
                required=False,
                location='query',
                schema=coreschema.Integer(
                    title='Page',
                    description=force_str(self.page_query_description)
                )
            )
        ]
        if self.page_size_query_param is not None:
            fields.append(
                coreapi.Field(
                    name=self.page_size_query_param,
                    required=False,
                    location='query',
                    schema=coreschema.Integer(
                        title='Page size',
                        description=force_str(self.page_size_query_description)
                    )
                )
            )
        return fields

    def get_schema_operation_parameters(self, view):
        parameters = [
            {
                'name': self.page_query_param,
                'required': False,
                'in': 'query',
                'description': force_str(self.page_query_description),
                'schema': {
                    'type': 'integer',
                },
            },
        ]
        if self.page_size_query_param is not None:
            parameters.append(
                {
                    'name': self.page_size_query_param,
                    'required': False,
                    'in': 'query',
                    'description': force_str(self.page_size_query_description),
                    'schema': {
                        'type': 'integer',
                    },
                },
            )
        return 

class CustomPageNumberPagination(PageNumberPagination):
     page_size_query_param = 'limit' 
    
    
