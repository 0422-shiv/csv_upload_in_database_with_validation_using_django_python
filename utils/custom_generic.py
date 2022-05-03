from django.db.models.query import QuerySet
from django.template.context import ContextDict
from rest_framework import mixins, views
from rest_framework.settings import api_settings
from rest_framework.pagination import BasePagination,_positive_int,_get_displayed_page_numbers,_get_page_links
import warnings
from django.core.paginator import InvalidPage, Paginator as DjangoPaginator
from rest_framework.exceptions import NotFound
from django.utils import six
from rest_framework.utils.urls import (
    replace_query_param, remove_query_param
)
from rest_framework.response import Response
from django.template import Context, loader
# from rest_framework.compat import OrderedDict
from collections import OrderedDict
from django.utils.translation import ugettext_lazy as _

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

    # Client can control the page using this query parameter.
    page_query_param = 'page'

    # Client can control the page size using this query parameter.
    # Default is 'None'. Set to eg 'page_size' to enable usage.
    page_size_query_param = None

    # Set to an integer to limit the maximum page size the client may request.
    # Only relevant if 'page_size_query_param' has also been set.
    max_page_size = None

    last_page_strings = ('last',)

    template = 'rest_framework/pagination/numbers.html'

    invalid_page_message = _('Invalid page "{page_number}": {message}.')

    def _handle_backwards_compat(self, view):
        """
        Prior to version 3.1, pagination was handled in the view, and the
        attributes were set there. The attributes should now be set on
        the pagination class, but the old style is still pending deprecation.
        """
        assert not (
            getattr(view, 'pagination_serializer_class', None) or
            getattr(api_settings, 'DEFAULT_PAGINATION_SERIALIZER_CLASS', None)
        ), (
            "The pagination_serializer_class attribute and "
            "DEFAULT_PAGINATION_SERIALIZER_CLASS setting have been removed as "
            "part of the 3.1 pagination API improvement. See the pagination "
            "documentation for details on the new API."
        )

        for (settings_key, attr_name) in (
            ('PAGINATE_BY', 'page_size'),
            ('PAGINATE_BY_PARAM', 'page_size_query_param'),
            ('MAX_PAGINATE_BY', 'max_page_size')
        ):
            value = getattr(api_settings, settings_key, None)
            if value is not None:
                setattr(self, attr_name, value)
                warnings.warn(
                    "The `%s` settings key is pending deprecation. "
                    "Use the `%s` attribute on the pagination class instead." % (
                        settings_key, attr_name
                    ),
                    PendingDeprecationWarning,
                )

        for (view_attr, attr_name) in (
            ('paginate_by', 'page_size'),
            ('page_query_param', 'page_query_param'),
            ('paginate_by_param', 'page_size_query_param'),
            ('max_paginate_by', 'max_page_size')
        ):
            value = getattr(view, view_attr, None)
            if value is not None:
                setattr(self, attr_name, value)
                warnings.warn(
                    "The `%s` view attribute is pending deprecation. "
                    "Use the `%s` attribute on the pagination class instead." % (
                        view_attr, attr_name
                    ),
                    PendingDeprecationWarning,
                )

    def paginate_queryset(self, queryset, request, view=None):
        """
        Paginate a queryset if required, either returning a
        page object, or `None` if pagination is not configured for this view.
        """
        self._handle_backwards_compat(view)

        page_size = self.get_page_size(request)
        if not page_size:
            return None

        paginator = DjangoPaginator(queryset, page_size)
        page_number = request.query_params.get(self.page_query_param, 1)
        if page_number in self.last_page_strings:
            page_number = paginator.num_pages

        try:
            self.page = paginator.page(page_number)
        except InvalidPage as exc:
            msg = self.invalid_page_message.format(
                page_number=page_number, message=six.text_type(exc)
            )
            raise NotFound(msg)

        if paginator.count > 1 and self.template is not None:
            # The browsable API should display pagination controls.
            self.display_page_controls = True

        self.request = request
        return list(self.page)

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('status', True),
            ('total_records', self.page.paginator.count),
            ('current_page', self.page.number),
            ('record_per_page', self.page_size),
            ('next_page', self.get_next_link()),
            ('previous_page', self.get_previous_link()),
            ('results', data)
            
        ]))

    def get_page_size(self, request):
        if self.page_size_query_param:
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
        # print('template',template)
        context = (self.get_html_context())
        # print('context',context)
        return template.render(context)

class GenericAPIView(views.APIView,PageNumberPagination):
  
    queryset = None
    serializer_class = None

    lookup_field = 'pk'
    lookup_url_kwarg = None

    # The filter backend classes to use for queryset filtering
    filter_backends = api_settings.DEFAULT_FILTER_BACKENDS

    # The style to use for queryset pagination.
    pagination_class = PageNumberPagination

    def get_queryset(self):
      
        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method."
            % self.__class__.__name__
        )

        queryset = self.queryset
        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()
        return queryset

   
    def get_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def get_serializer_class(self):
        """
        Return the class to use for the serializer.
        Defaults to using `self.serializer_class`.
        You may want to override this if you need to provide different
        serializations depending on the incoming request.
        (Eg. admins get full serialization, others get basic serialization)
        """
        assert self.serializer_class is not None, (
            "'%s' should either include a `serializer_class` attribute, "
            "or override the `get_serializer_class()` method."
            % self.__class__.__name__
        )

        return self.serializer_class

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self
        }

    def filter_queryset(self, queryset):
        """
        Given a queryset, filter it with whichever filter backend is in use.
        You are unlikely to want to override this method, although you may need
        to call it either from a list view, or from a custom `get_object`
        method if you want to apply the configured filtering backend to the
        default queryset.
        """
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    @property
    def paginator(self):
        """
        The paginator instance associated with the view, or `None`.
        """
        if not hasattr(self, '_paginator'):
            if self.pagination_class is None:
                self._paginator = None
            else:
                # print(self.pagination_class())
                self._paginator = self.pagination_class()
        return self._paginator

    def paginate_queryset(self, queryset):
        """
        Return a single page of results, or `None` if pagination is disabled.
        """
        if self.paginator is None:
            return None
        # print(queryset, self.request)
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    def get_paginated_response(self, data):
        """
        Return a paginated style `Response` object for the given output data.
        """
        assert self.paginator is not None
        # print(self.paginator is not None)
        # print(data)
        # print(self.paginator.get_paginated_response(data))
        return self.paginator.get_paginated_response(data)




class ListAPIView(mixins.ListModelMixin,
                  GenericAPIView):
    """
    Concrete view for listing a queryset.
    """
    def get(self, request, *args, **kwargs):
        # print(self)
        # print(request)
        # print(*args)
        # print(**kwargs)
        # print(self.list(request, *args, **kwargs))
        return self.list(request, *args, **kwargs)