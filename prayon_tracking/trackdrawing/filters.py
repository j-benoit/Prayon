import django_filters as filters
from .models import Project_history, ExtractSAP, Type, Work_data
from django.contrib.auth.models import User
from django import forms


class CustomCheckboxSelectMultiple(forms.widgets.CheckboxSelectMultiple):
    def get_context(self, name, value, attrs):
        context = super(CustomCheckboxSelectMultiple, self).get_context(name, value, attrs)
        for opt in context['widget']['optgroups']:
            opt[1][0]['attrs']['id_user'] = opt[1][0]['value']
            opt[1][0]['attrs']['checked'] = True
        return context


class Project_historyFilter(filters.FilterSet):
    date_choices = tuple(Project_history.objects.values_list('date', 'date').distinct())
    start_date = filters.ChoiceFilter(field_name='date', choices=date_choices, lookup_expr='gte')
    end_date = filters.ChoiceFilter(field_name='date', choices=date_choices, lookup_expr='lte')
    # date = filters.DateRangeFilter()
    id_user = filters.ModelMultipleChoiceFilter(queryset=User.objects.all().order_by('id'),
                                                  widget=CustomCheckboxSelectMultiple())
    class Meta:
        model = Project_history
        fields = ['id_user' ]

    def filter_date(self):
        # print(self.data['distance'])
        return self.data['date']


class ExtractSAPFilter(filters.FilterSet):
    TYPE_CHOICES = tuple(Type.objects.values_list('pk', 'desc'))

    typ = filters.ChoiceFilter(field_name='id_SAP__typ', choices= TYPE_CHOICES)
    comment = filters.CharFilter(field_name='comment', lookup_expr='contains')
    title_contains = filters.CharFilter(field_name='id_SAP__title', lookup_expr='contains', label='Title Contains')

    class Meta:
        model = Work_data
        fields = ['typ']