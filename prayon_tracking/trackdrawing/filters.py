import django_filters as filters
from .models import Project_history, Work_data
from django import forms


class Project_historyFilter(filters.FilterSet):
    date = filters.ChoiceFilter(choices=tuple(Project_history.objects.values_list('date', 'date').distinct()))
    class Meta:
        model = Project_history
        fields = ['id_user','date' ]

    def filter_date(self):
        # print(self.data['distance'])
        return self.data['date']
