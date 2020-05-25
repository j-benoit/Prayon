import django_tables2 as tables
from django_tables2 import A
from .models import ExtractSAP, Work_data
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django.core.files.storage import FileSystemStorage
from django.utils.html import format_html
import os


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


def get_open(record):
    return Work_data.objects.filter(id_SAP__division_client=record['division_client'],
                                    division_status='OPEN').exclude(status='BACKLOG').count()


class DivisionTable(tables.Table):
    # division_client = tables.Column(default=' ')
    # division_client = tables.LinkColumn('EditDivView', args=[slugify(A('division_client'))],)
    division_client = tables.Column(linkify=('EditDivView', {'division_client': A('division_client')}))
    the_count = tables.Column(verbose_name='Count drawings')
    open_count = tables.Column(verbose_name='Open drawings', empty_values=())
    status = tables.Column(verbose_name='Status', empty_values=())

    class Meta:
        template_name = 'trackdrawing/TableRender.html'
        attrs = {"class": "table-striped table-bordered table-sm",
                 'tbody': {'id': 'DivisionTable'},
                 }
        fields = ('division_client', 'the_count')

    def render_open_count(self, record):
        return get_open(record)

    def render_status(self, record):
        if record['the_count'] == get_open(record):
            return 'OPEN'
        if get_open(record) == 0:
            return 'CLOSED'
        else:
            return 'IN PROGRESS'


class RetitleTable(tables.Table):
    title = tables.Column()
    division_ausy =tables.Column(default=' ', verbose_name='Division')
    num_cadastre = tables.LinkColumn('show_image', args=[A('pk')], attrs={"a": {"target": "pdfview"}},
                      verbose_name='View drawing')
    edit = tables.TemplateColumn(template_name='trackdrawing/Update_DivTitle.html')
    id = tables.LinkColumn('edit_data', args=[A('pk')], verbose_name='Edit SAP')
    id_workdata = tables.Column(verbose_name='id',empty_values=())
    division_status = tables.Column(verbose_name='Status', empty_values=())

    class Meta:
        # model = ExtractSAP
        template_name = 'trackdrawing/TableRender.html'
        attrs = {"class": "table-striped table-bordered table-sm",
                 'tbody': {'id': 'ReTitleTable'},
                 'search_form': {'id': 'ReTitle_search_form_id'},
                 }
        row_attrs = {
            'data_id': lambda record: record.pk,
        }

        fields = ("title",'division_ausy', "num_cadastre", 'edit','id', 'id_workdata')

    def render_title(self, record):
        subtitle = record.title.split("-")
        button_id = [s.strip().replace(' ', '_') for s in subtitle]
        pre='<button type="submit" class="mx-1 btn btn-secondary" onClick="setDiv(this)" cat="title" id="'
        button = [pre + id + '">' for id in button_id]
        post='</button>'
        final = [button[i]+title.strip()+post for i, title in enumerate(subtitle)]
        # post_pre = post + pre
        return mark_safe("".join(final))

    def render_division_ausy(self, record):
        subtitle = record.division_ausy.split("-")
        button_id = [s.strip().replace(' ', '_') for s in subtitle]
        pre='<button type="submit" class="mx-1 btn btn-secondary" onClick="setDiv(this)" cat="title" id="'
        button = [pre + id + '">' for id in button_id]
        post='</button>'
        final = [button[i]+title.strip()+post for i, title in enumerate(subtitle)]
        # post_pre = post + pre
        return mark_safe("".join(final))

    def render_division_status(self, record):
        div_stat = Work_data.objects.get(id_SAP=record.id).division_status
        if div_stat == 'CLOSED':
            div_stat = '<span class="badge badge-success">CLOSED</span>'
        else:
            div_stat = '<span class="badge badge-danger">OPEN</span>'

        return mark_safe(div_stat)

    def render_id_workdata(self, record):
        return Work_data.objects.get(id_SAP=record.id).id

class StampingTable(tables.Table):
    # Used on Home View
    title = tables.Column()
    num_cadastre = tables.LinkColumn('edit_data', args=[A('pk')])
    # Download = tables.TemplateColumn('<a class="btn btn-success" href={% url "DownloadDrawing" record.id%}>Download File</a>', verbose_name="Download", empty_values=())
    Download = tables.TemplateColumn('{{ record.html }}',
        verbose_name="Download", empty_values=())
    # comment = tables.Column(verbose_name="Commentaires", empty_values=())
    Upload = tables.TemplateColumn('<a class="btn btn-success" href={% url "UploadDrawing" record.id%}>Upload File</a>', verbose_name="Upload", empty_values=())

    class Meta:
        # model = ExtractSAP
        template_name = 'trackdrawing/TableRender.html'
        attrs = {"class": "table-striped table-bordered table-sm",
                 'tbody': {'id': 'StampingTable'},
                 'search_form': {'id': 'StampingTable_search_form_id'},
                 }
        fields = ("title", "num_cadastre",)

    def render_Download(self, record):
        fs = FileSystemStorage()
        obj = ExtractSAP.objects.get(pk=record.id)
        filename = obj.num_cadastre + ".pdf"
        if fs.exists(os.path.join(os.path.join(fs.location, 'TMP'), filename)):
            html_txt = '<a class="btn btn-danger" href=/prayon/Stamp/Download/' + str(record.id) + '>Download File</a>'
        else:
            html_txt = '<a class="btn btn-success" href=/prayon/Stamp/Download/' + str(record.id) + '>Download File</a>'
        return mark_safe(html_txt)


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

