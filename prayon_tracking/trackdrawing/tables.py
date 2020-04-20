import django_tables2 as tables
from django_tables2 import A
from .models import ExtractSAP, Work_data


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

class WorkTable(tables.Table):
    id_SAP__num_cadastre = tables.LinkColumn('edit_data', args=[A('id_SAP__pk')])
    class Meta:
        model = Work_data
        template_name = 'trackdrawing/TableRender.html'
        attrs = {"class": "table-striped table-bordered table-sm",
                 'tbody': {'id': 'WorkTable'},
                 'search_form': {'id': 'WorkTable_search_form_id'},
                 }
        #fields = ("id_SAP.title", "id_SAP.num_cadastre")
        fields = ("id_SAP__title", "id_SAP__num_cadastre", "status", 'comment')

