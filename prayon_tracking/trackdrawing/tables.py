import django_tables2 as tables
from django_tables2 import A
from .models import ExtractSAP, Work_data
from django.utils.safestring import mark_safe
from django.utils.html import format_html


def f_render_comment(commentaire):
    commentaire = commentaire.replace('\n', '<br>')
    commentaire = commentaire.replace(
        '[POSTRAIT TYP INVALID]',
        '<SPAN class="error_type">[POSTRAIT TYP INVALID]</SPAN>')
    commentaire = commentaire.replace(
        '[POSTRAIT TYP LIASSE]',
        '<SPAN class="error_liasse">[POSTRAIT TYP LIASSE]</SPAN>')
    commentaire = commentaire.replace(
        '[POSTRAIT POMPE]',
        '<SPAN class="error_pompe">[POSTRAIT POMPE]</SPAN>')
    return commentaire


class ExtractTable(tables.Table):
    # Used on Home View
    title = tables.Column()
    num_cadastre = tables.LinkColumn('edit_data', args=[A('pk')])
    typ = tables.Column(verbose_name="Type")
    # comment = tables.Column(verbose_name="Commentaires", empty_values=())
    comment = tables.TemplateColumn('{{ record.text_field|linebreaksbr }}', verbose_name="Commentaires", empty_values=())

    def render_comment(self, record):
        commentaire = Work_data.objects.get(id_SAP__pk=record.pk).comment
        return mark_safe(f_render_comment(commentaire).replace('\n', '<br>'))

    class Meta:
        # model = ExtractSAP
        template_name = 'trackdrawing/TableRender.html'
        attrs = {"class": "table-striped table-bordered table-sm",
                 'tbody': {'id': 'ExtractTable'},
                 'search_form': {'id': 'ExtractTable_search_form_id'},
                 }
        fields = ("title", "num_cadastre",)


class ExtractTableExpanded(tables.Table):
    # Used on View DB
    id_SAP__num_cadastre = tables.LinkColumn('show_image', args=[A('id_SAP.pk')], attrs={"a": {"target": "pdfview"}}, verbose_name='View drawing')

    class Meta:
        model = Work_data
        template_name = 'trackdrawing/TableRender.html'
        attrs = {"class": "table-striped table-bordered table-sm",
                 'tbody': {'id': 'ExtractTableExpanded'},
                 'search_form': {'id': 'ExtractTableExpanded_search_form_id'},
                 }
        fields = ("id", "id_SAP__title", "id_SAP__num_cadastre", "id_SAP__typ__code", "status", "comment")


class WorkTable(tables.Table):
    # Used for Backlog View
    id_SAP__title = tables.Column()
    id_SAP__num_cadastre = tables.LinkColumn('edit_data', args=[A('id_SAP__pk')])
    status = tables.Column()
    comment = tables.TemplateColumn('{{ record.text_field|linebreaksbr }}', verbose_name="Commentaires", empty_values=())
    role = tables.TemplateColumn('{{ record.text_field }}', verbose_name="Role", empty_values=())

    def render_role(self, record):
        user = self.request.user
        role = ''
        if getattr(record, 'id_user', '') == user:
            role = role + 'Owner<br>'
        if getattr(record, 'id_checker', '') == user:
            role = role + 'Checker<br>'
        if getattr(record, 'id_rechecker', '') == user:
            role = role + 'Re-Checker<br>'
        return mark_safe(role)

    def render_comment(self, record):
        commentaire = record.comment
        return mark_safe(f_render_comment(commentaire).replace('\n', '<br>'))

    class Meta:
        # model = Work_data
        template_name = 'trackdrawing/TableRender.html'
        attrs = {"class": "table-striped table-bordered table-sm",
                 'tbody': {'id': 'WorkTable'},
                 'search_form': {'id': 'WorkTable_search_form_id'},
                 }
        #fields = ("id_SAP.title", "id_SAP.num_cadastre")
        fields = ("id_SAP__title", "id_SAP__num_cadastre", "role", "status", 'comment')


class CheckExtractTable(tables.Table):
    # Used On Filter view
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
    # Used on Modify SAP View
    Work_id = tables.Column(verbose_name='Id', empty_values=())
    title = tables.Column()
    num_cadastre = tables.LinkColumn('show_image', args=[A('pk')], attrs={"a": {"target": "pdfview"}}, verbose_name='View drawing')
    typ = tables.Column(verbose_name="Type")
    comment = tables.TemplateColumn('{{ record.text_field|linebreaksbr }}', verbose_name="Commentaires", empty_values=())
    status = tables.Column(verbose_name='Status', empty_values=())

    class Meta:
        model = ExtractSAP
        template_name = 'trackdrawing/TableRender.html'
        attrs = {"class": "table-striped table-bordered table-sm",
                 'tbody': {'id': 'ExtractTable'},
                 'search_form': {'id': 'ExtractTable_search_form_id'},
                 }
        fields = ('Work_id', "title", "num_cadastre", 'typ')

    def render_comment(self, record):
        commentaire = Work_data.objects.get(id_SAP__pk=record.pk).comment
        commentaire = commentaire.replace('\n', '<br>')
        commentaire = commentaire.replace(
            '[POSTRAIT TYP INVALID]',
            '<SPAN class="error_type">[POSTRAIT TYP INVALID]</SPAN>')
        commentaire = commentaire.replace(
            '[POSTRAIT TYP LIASSE]',
            '<SPAN class="error_liasse">[POSTRAIT TYP LIASSE]</SPAN>')
        return mark_safe(commentaire.replace('\n', '<br>'))

    def render_status(self, record):
        return Work_data.objects.get(id_SAP__pk=record.pk).status

    def render_Work_id(self, record):
        return Work_data.objects.get(id_SAP__pk=record.pk).pk

