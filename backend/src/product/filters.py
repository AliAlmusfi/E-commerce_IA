import django_filters
from .models import Product
from rest_framework import filters
from django.db.models import Q
class ProductFilter(django_filters.FilterSet):
    created_at = django_filters.DateFilter(field_name='created_at__date')
    updated_at = django_filters.DateFilter(field_name='updated_at__date')
    class Meta:
        model= Product
        fields = {
            'title': ['exact' , 'iexact' , 'icontains', 'contains'],
            'manufacturer': ['exact' , 'iexact' , 'icontains' , 'contains'],
            'created_at': ['exact' , 'lt' , 'gt' , 'range'],
            'updated_at': ['exact' , 'lt' , 'gt' , 'range'],
        }


class ProductSearchFilter(filters.SearchFilter):
    def filter_queryset(self, request, queryset, view):
        search_terms = self.get_search_terms(request)
        
        if not search_terms:
            return queryset
        
        # Custom search logic for email field
        conditions = []
        for term in search_terms:
            # For email field, search only the part before @
            title_condition =  Q(email__icontains=term )
            manufacture_condition = Q(username__icontains=term)
            conditions.append(title_condition | manufacture_condition)
        
        return queryset.filter(*conditions)