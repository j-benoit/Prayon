import django_filters as filters
from .models import Project_history, ExtractSAP, Type, Work_data
from django.contrib.auth.models import User
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Field, Layout, Row, Submit


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

    typ = filters.ChoiceFilter(field_name='id_SAP__typ', choices=TYPE_CHOICES, label='Type')
    comment = filters.CharFilter(field_name='comment', lookup_expr='contains')
    not_comment = filters.CharFilter(field_name='comment', lookup_expr='contains', exclude=True, label='Comment not contains')
    title_contains = filters.CharFilter(field_name='id_SAP__title', lookup_expr='contains', label='Title Contains')
    title_not_contains = filters.CharFilter(field_name='id_SAP__title', lookup_expr='contains', exclude=True, label='Title not contains')

    class Meta:
        model = Work_data
        fields = ['typ']

    def __init__(self, *args, **kwargs):
        super(ExtractSAPFilter, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.layout = Layout(
            Row(
                Column(
                    Field('typ',),
                    css_class="form-label-group col-8 mb-0"
                ),
                css_class="form-row",
            ),
            Row(
                Column(
                    Field('comment', ),
                    css_class="form-label-group col-4 mb-0"
                ),
                Column(
                    Field('not_comment', ),
                    css_class="form-label-group col-4 mb-0"
                ),
                css_class="form-row",
            ),
            Row(
                Column(
                    Field('title_contains', ),
                    css_class="form-label-group col-4 mb-0"
                ),
                Column(
                    Field('title_not_contains', ),
                    css_class="form-label-group col-4 mb-0"
                ),
                css_class="form-row",
            ),
            Submit("submit", "Valider")
        )
