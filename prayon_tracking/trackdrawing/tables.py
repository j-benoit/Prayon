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
        fields = ("title", "num_cadastre",)


class ExtractTableExpanded(tables.Table):
    id_SAP__num_cadastre = tables.LinkColumn('show_image', args=[A('pk')], attrs={"a": {"target": "pdfview"}}, verbose_name='View drawing')

    class Meta:
        model = Work_data
        template_name = 'trackdrawing/TableRender.html'
        attrs = {"class": "table-striped table-bordered table-sm",
                 'tbody': {'id': 'ExtractTableExpanded'},
                 'search_form': {'id': 'ExtractTableExpanded_search_form_id'},
                 }
        fields = ("id", "id_SAP__title", "id_SAP__num_cadastre", "id_SAP__typ__code", "status", "comment")


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


class CheckExtractTable(tables.Table):
    num_cadastre = tables.LinkColumn('edit_data', args=[A('pk')])
    title =tables.Column(
        attrs={'td': {'class': 'record_title', 'data-pk': lambda record: record.id, 'data-name': 'title', 'data-type':'textarea'}})
    class Meta:
        model = ExtractSAP
        template_name = 'trackdrawing/TableRender.html'
        attrs = {"class": "table-striped table-bordered table-sm",
                 'tbody': {'id': 'ExtractTable'},
                 'search_form': {'id': 'ExtractTable_search_form_id'},
                 }
        row_attrs = {
            'data_id': lambda record: record.pk,
        }
        fields = ("title", "num_cadastre")

class LiasseTable(tables.Table):
    num_cadastre = tables.LinkColumn('show_image', args=[A('pk')], attrs={"a": {"target": "pdfview"}}, verbose_name='View drawing')
    class Meta:
        model = ExtractSAP
        template_name = 'trackdrawing/TableRender.html'
        attrs = {"class": "table-striped table-bordered table-sm",
                 'tbody': {'id': 'ExtractTable'},
                 'search_form': {'id': 'ExtractTable_search_form_id'},
                 }
        fields = ("title", "num_cadastre", 'typ')
