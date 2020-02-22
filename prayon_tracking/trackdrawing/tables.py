import django_tables2 as tables
from django_tables2 import A
from .models import ExtractSAP


class ExtractTable(tables.Table):
    num_cadastre = tables.LinkColumn('edit_data', args=[A('pk')])
    class Meta:
        model = ExtractSAP
        template_name = 'trackdrawing/TableRender.html'
        attrs = {"class": "table-striped table-bordered table-sm",
                 'tbody': {'id': 'ExtractTable'},
                 'search_form': {'id': 'ExtractTable_search_form_id'},
                 }
        fields = ("title", "num_cadastre")
