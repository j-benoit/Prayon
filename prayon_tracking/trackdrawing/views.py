import logging
import os
import os.path
import random
from datetime import date, timedelta
from itertools import cycle

import img2pdf
import pandas as pd
import pygal
from PIL import Image
from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User, Group
from django.db.models import ForeignKey
from django.db.models import Q, F
from django.http import HttpResponse, HttpResponseNotFound, JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.dateparse import parse_duration
from django.views import View
from django.views.generic import UpdateView
from django_tables2 import SingleTableView

from .filters import Project_historyFilter, ExtractSAPFilter
from .forms import UpdatedInfoForm, ShowDistinct, UploadFileForm, StampedDocumentForm
from .tables import ExtractTable, WorkTable, CheckExtractTable, ExtractTableExpanded, StampingTable, RetitleTable, \
    DivisionTable
from .utility import *
from .utils import has_group

try:
    from io import BytesIO as IO  # for modern python
except ImportError:
    from io import StringIO as IO  # for legacy python


# Create your views here.
def Dispatch_Work(request):
    """
    Dispatch drawings among users in group 'Prod'
    :param request:
    :return:
    """
    drawings_per_user = int(request.POST["plans_nb"])
    already_dispatched_records = [record.id_SAP.pk for record in Work_data.objects.all()]
    record_to_dispatched = ExtractSAP.objects.all().exclude(id__in=already_dispatched_records).order_by('id')[
                           :drawings_per_user]
    prod_user = User.objects.filter(groups__name='Prod').order_by('id')
    pool_user = cycle(prod_user)
    for record in record_to_dispatched:
        current_user = next(pool_user)
        print(current_user.username + " get " + record.num_cadastre)
        Work_data.objects.create(id_SAP=record, id_user=current_user, status='OPEN')

    return redirect('dash')


def Test(request):
    # Modify_drawing_status()
    # Modify_drawing_status_from_csv()
    # Delete_record_from_csv()
    # from .check import check_database
    # check_database()
    # from .PDFutils import RenamePDFFiles
    # RenamePDFFiles()

    # owork_data = Work_data.objects.filter(comment__contains='[POSTRAIT POMPE]')
    # for record in owork_data:
    #     print(record.comment)
    #     print(remove_duplicate(record.comment))
    #     record.comment = remove_duplicate(record.comment)
    #     record.save()
    # Modify_Multipages_drawing_from_csv()
    # create_new_drawing_id()
    # Modify_drawing_from_csv()
    # Modify_division_from_csv()
    # Modify_Num_Cadastre_from_csv()
    Maj20200604()

    return redirect('Admin')


def Export_Database(request):
    names = [
        'id',
        'id_SAP',
        'id_user__username',
        'id_checker__username',
        'id_rechecker__username',
        'id_retitle__username',
        'status',
        'division_status',
        'created_date',
        'modified_date',
        'comment',
        'time_tracking',
        'check_time_tracking',
    ]
    workdata = Work_data.objects.all().values_list(*names)
    workdata_column_names = [
        field.verbose_name for field in Work_data._meta.fields
    ]

    extractsap = ExtractSAP.objects.all().values_list()
    extractsap_column_names = [
        field.verbose_name for field in ExtractSAP._meta.fields
    ]
    extractsap_column_names[0] = "id SAP"

    df_work = pd.DataFrame.from_records(workdata, columns=workdata_column_names)
    df_sap = pd.DataFrame.from_records(extractsap, columns=extractsap_column_names)
    df_sap = df_sap.set_index('id SAP')

    df = df_work.join(df_sap, on='id SAP', rsuffix='_sap')
    df = df.set_index('ID')
    df.sort_values(by=['id SAP'], inplace=True)

    # print(df_work)
    # print(df_sap)
    # print(df)

    Extractsap_filter = [
        'ID',
        'Site',
        'Div.',
        'Ancien numéro Ordre',
        'Ordre',
        'typ',
        'Intitulé du type de document',
        'Num.',
        'Folio',
        'Rev',
        'ID Document',
        'Dernière version',
        'titre du projet',
        'Transfert vers ordre',
        'Lien vers le serveur',
        'Titre du document',
        'Division section sous section client',
        'Division section sous section AUSY',
        'Catégorie de document',
        'Date d émission',
        'Provenance',
        'Auteur',
        'Vérificateur',
        'Approbateur',
        'Validateur',
        'Entrepreneur/Fournisseur',
        'Référence externe',
        'Ancien numéro de plan',
        'Numéro Cadastre ENG',
        'Révision Cadastre Eng',
        'TAG',
        'Poste technique #1',
        'Libellé Poste technique #1',
        'Poste technique #2',
        'Libellé Poste technique #2',
        'Poste technique #3',
        'Libellé Poste technique #3',
        'Poste technique #4',
        'Libellé  Poste technique #4',
        'Poste technique #5',
        'Libellé Poste technique #5',
        'Poste technique #6',
        'Libellé Poste technique #6',
        'Poste technique',
        'Libellé Poste Technique',
        'Remarque',
        'N° d imputation',
        'N° de bon de travail',
        'Existance fichier tif/pdf/dwg',
        'id SAP',
        'id user',
        'id checker',
        'id rechecker',
        'id retitle',
        'created date',
        'modified date',
        'comment',
        'time tracking',
        'check time tracking',
        'id SAP_sap',
        'status',
        'status_sap',
        'division status'
    ]

    # my "Excel" file, which is an in-memory output file (buffer)
    # for the new workbook
    excel_file = IO()

    df = df.filter(items=Extractsap_filter)
    # df = df.style.format({"Date d émission": lambda t: t.strftime("%d/%m/%Y")})
    writer = pd.ExcelWriter(excel_file, engine='xlsxwriter', date_format='dd/mm/yyy')
    df.to_excel(writer, 'Extract_SAP')
    writer.save()
    writer.close()
    # important step, rewind the buffer or when it is read() you'll get nothing
    # but an error message when you try to open your zero length file in Excel
    excel_file.seek(0)

    response = HttpResponse(excel_file.read(),
                            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="Export_SAP.xlsx"'
    return response


def Admin(request):
    # get number of drawing that remain not affected
    nb_plan_max = ExtractSAP.objects.all().count() - Work_data.objects.all().count()
    # set drawings quantity to be checked
    nb_plan_c_max = communData.objects.get(pk=1).nb_plan_check

    groupes = Group.objects.all().exclude(name='CP')
    usr = User.objects.all()

    old_user_list = Work_data.objects.filter(status__in=['OPEN', 'BACKLOG']).values('id_user',
                                                                                    'id_user__username').distinct()
    new_user_list = User.objects.all()
    if request.method == 'POST':
        if 'transfer_task' in request.POST:
            old_user_id = request.POST.get('old_id')
            new_user_id = request.POST.get('new_id')
            if old_user_id != new_user_id:
                old_user = User.objects.get(pk=old_user_id)
                new_user = User.objects.get(pk=new_user_id)
                for record in Work_data.objects.filter(id_user=old_user, status__in=['OPEN', 'BACKLOG']):
                    record.id_user = new_user
                    record.save()
        elif 'Chg_Group' in request.POST:
            for key, value in request.POST.items():
                if key[:6] == 'group_':
                    user_to_modify = User.objects.get(pk=key[6:])
                    user_to_modify.groups.remove(Group.objects.get(name='Prod'))
                    user_to_modify.groups.remove(Group.objects.get(name='Check'))
                    user_to_modify.groups.add(Group.objects.get(name=value))
                    user_to_modify.save()

    return render(request, "trackdrawing/Admin.html", locals())


def nbChecker(request):
    tmp = communData.objects.get(pk=1)
    tmp.nb_plan_check = request.POST["plans_nb"]
    tmp.save()

    return redirect('dash')


def Dashboard(request):
    if has_group(request.user, 'CP'):
        # Extract history data from DB to Dataframe
        history_filter = Project_historyFilter(request.GET, queryset=Project_history.objects.all())
        data = history_filter.qs
        df = pd.DataFrame.from_records(data.values())
        # Modify dataframe indexes
        df = df.set_index(['id_user_id', 'date'])
        # Create list for comprehensive username (instead of user id)
        list_user = {record.pk: record.username for record in User.objects.filter(pk__in=
                                                                                  df.index
                                                                                  .get_level_values(
                                                                                      'id_user_id').to_list())}

        for key, value in list_user.items():
            df.rename(index={key: value}, inplace=True)
        # order df by descending index
        df.sort_index(level=('id_user_id', 'date'), ascending=False, inplace=True)
        # keep only the n top row for each user
        top = 1
        df = df.groupby(level=0).apply(lambda df: df[:top])
        df.index = df.index.droplevel(0)

        dfextract = df.iloc[:, df.columns.isin(
            {'open_drawings', 'backlog_drawings', 'closed_drawings', 'checked_drawings', 'invalid_drawings'})]
        # Transfer dataframe data to pygal Chart
        line_chart = pygal.StackedBar()
        line_chart.title = 'Users evolution   '
        line_chart.x_labels = dfextract.index.get_level_values('id_user_id').to_list()
        for col in dfextract.columns.to_list():
            line_chart.add(col, dfextract[col].to_list())
        # Render chart to html for template
        chart_line = line_chart.render_data_uri()

        dfextract = df.iloc[:, df.columns.isin({'avg_closed_time', 'avg_backlog_time'})]
        dfextract['Avg'] = dfextract.apply(lambda row: (row.avg_closed_time + row.avg_backlog_time) / 2, axis=1)
        # print(dfextract)
        styles = [
            {'selector': "th.blank", 'props': [('display', 'none')]},  # hide dataframe header (ie: the skill id)
            {'selector': "th.row_heading", 'props': [('display', 'none')]},  # hide dataframe header (ie: the skill id)
            {'selector': "th.col_heading", 'props': [('vertical-align', 'middle'), ('text-align', 'center')]},
            {'selector': "td.data", 'props': [('text-align', 'center'), ('vertical-align', 'middle')]},
            {'selector': "td.col0", 'props': [('text-align', 'left')]},
        ]
        AverageTimeTable = dfextract.reset_index(drop=False).style \
            .set_table_attributes('class="table table-hover table-bordered table-striped"') \
            .set_uuid('AverageTimeTable') \
            .format({'date': "{:%d/%m/%Y}",
                     'avg_closed_time': lambda x: printNiceTimeDelta(x),
                     'avg_backlog_time': lambda x: printNiceTimeDelta(x),
                     'Avg': lambda x: printNiceTimeDelta(x)}) \
            .set_table_styles(styles) \
            .render()

        # print(df.groupby(level=[0]).sum())
        data = Project_history.objects.all()
        if len(history_filter.data) != 0:
            if history_filter.data['id_user']:
                data = data.filter(id_user__pk__in=[int(x) for x in history_filter.data.getlist('id_user')])
            if history_filter.data['start_date'] and history_filter.data['end_date']:
                data = data.filter(date__gte=history_filter.data['start_date'],
                                   date__lte=history_filter.data['end_date'])
            elif history_filter.data['start_date']:
                data = data.filter(date__gte=history_filter.data['start_date'])
            elif history_filter.data['end_date']:
                data = data.filter(date__lte=history_filter.data['end_date'])

        df = pd.DataFrame.from_records(data.values())
        # df = df.set_index(['date', 'id_user_id'])
        df = df.set_index(['id_user_id', 'date'])
        # add missing date for all user
        new_index = pd.MultiIndex.from_product(df.index.levels)
        new_df = df.reindex(new_index)
        new_df = new_df.reset_index()
        # fill NA from new df with value from preceding date
        new_df = new_df.groupby(['id_user_id']).apply(
            lambda grp: fill_missing(grp)
        )
        new_df = new_df.reset_index()

        new_df = new_df.set_index(['date', 'id_user_id'])
        dfextract = new_df.groupby(level=[0]).sum()

        dfextract = dfextract.iloc[:, dfextract.columns.isin({'open_drawings',
                                                              'backlog_drawings',
                                                              'closed_drawings',
                                                              'checked_drawings',
                                                              'invalid_drawings'})]
        # add column with closed/Checked & invalid data
        dfextract['Completed_drawings'] = dfextract.apply(
            lambda row: (row.closed_drawings + row.checked_drawings + row.invalid_drawings), axis=1)
        xy_chart = pygal.DateTimeLine(x_label_rotation=35)
        xy_chart.title = 'Cumulé équipe'
        for col in dfextract.columns.to_list():
            xy_chart.add(col, [(index, row[col]) for index, row in dfextract.iterrows()])
        chart_xy = xy_chart.render_data_uri()

        df = df.reset_index()
        df = df.set_index(['date', 'id_user_id'])
        df_closed = df['avg_closed_time']
        df_closed = df_closed[df.avg_closed_time.notnull()]
        df_closed = df_closed.groupby(level=[0]).mean(numeric_only=False)
        df_backlog = df['avg_backlog_time']
        df_backlog = df_backlog[df.avg_backlog_time.notnull()]
        df_backlog = df_backlog.groupby(level=[0]).mean(numeric_only=False)

        df_summary = pd.DataFrame()
        df_summary['avg_closed_time'] = df_closed
        df_summary = pd.concat([df_summary, df_backlog], axis=1, sort=False)

        df_summary['Avg'] = df_summary.apply(lambda row: (row.avg_closed_time + row.avg_backlog_time) / 2, axis=1)
        Table_summary = df_summary.reset_index(drop=False).style \
            .set_table_attributes('class="table table-hover table-bordered table-striped"') \
            .set_uuid('Table_summary') \
            .format({'date': "{:%d/%m/%Y}",
                     'avg_closed_time': lambda x: printNiceTimeDelta(x),
                     'avg_backlog_time': lambda x: printNiceTimeDelta(x),
                     'Avg': lambda x: printNiceTimeDelta(x)}) \
            .set_table_styles(styles) \
            .render()

        return render(request, "trackdrawing/dashboradAdmin.html", locals())
    else:
        recheck_today = Work_data.objects.filter(id_rechecker__pk=request.user.id).exclude(
            modified_date__lt=date.today())
        recheck_before = Work_data.objects.filter(id_rechecker__pk=request.user.id, modified_date__lt=date.today())
        count_recheck_today = {stat: len(recheck_today.filter(status=stat)) for stat in
                               ['BACKLOG', 'CLOSED', 'CHECKED', 'INVALID', 'TO_RE-CHECK']}
        count_recheck_before = {stat: len(recheck_before.filter(status=stat)) for stat in
                                ['BACKLOG', 'CLOSED', 'CHECKED', 'INVALID', 'TO_RE-CHECK']}
        data = Project_history.objects.filter(id_user__pk=request.user.id)
        df = pd.DataFrame.from_records(data.values())
        df = df.sort_values('date', ascending=False)
        return render(request, "trackdrawing/dashboradUser.html", locals())


# Define helper function
def fill_missing(grp):
    res = grp.set_index('date') \
        .fillna(method='ffill')
    del res['id_user_id']
    return res


def printNiceTimeDelta(value):
    if not pd.isnull(value):
        delay = value
        if (delay.days != 0):
            out = str(delay).replace(" days ", ":")
        else:
            out = str(delay).replace("0 days ", "")
        outAr = out.split(':')
        outAr = ["%02d" % (int(float(x))) for x in outAr]
        out = ":".join(outAr)
        return out
    else:
        return ""


class ListBacklog(LoginRequiredMixin, SingleTableView):
    model = Work_data
    context_object_name = "backlog"
    table_class = WorkTable
    template_name = "trackdrawing/Backlog_list.html"
    table_pagination = False

    # paginate_by = 10

    def get_table_data(self):
        table_data = Work_data.objects.filter(
            Q(id_checker__pk=self.request.user.id) | Q(id_user__pk=self.request.user.id) | Q(
                id_rechecker__pk=self.request.user.id)).exclude(status='OPEN')
        return table_data

    def get_context_data(self, **kwargs):
        context = super(ListBacklog, self).get_context_data(**kwargs)
        retitle_data = Work_data.objects.filter(id_retitle=self.request.user.id).exclude(status='BACKLOG').values(
            division_client=F('id_SAP__division_client')).annotate(the_count=Count('division_client'))
        context['retitle_table'] = DivisionTable(retitle_data)
        return context


class RetitleView(LoginRequiredMixin, SingleTableView):
    model = ExtractSAP
    table_class = DivisionTable
    template_name = "trackdrawing/View_Div.html"

    def get_table_data(self):

        user_drawing_id = [record.id_SAP for record in
                           Work_data.objects.filter(id_retitle=self.request.user.id).exclude(division_status='CLOSED')]
        current_division = Work_data.objects.filter(id_retitle=self.request.user.id, division_status='OPEN').first()
        if not current_division:
            # Get list of drawing without owner
            new_division = Work_data.objects.filter(id_retitle__isnull=True).exclude(
                id_SAP__division_client='').exclude(status='BACKLOG').first()
            record_to_process = ExtractSAP.objects.filter(division_client=new_division.id_SAP.division_client).exclude(
                status='BACKLOG')
            for rec in record_to_process:
                oworkdata = Work_data.objects.get(id_SAP=rec.pk)
                oworkdata.id_retitle = self.request.user
                oworkdata.save()
            table_data = record_to_process.values('division_client').annotate(the_count=Count('division_client'))
        else:
            # Display division associated with current user
            table_data = ExtractSAP.objects.filter(division_client=current_division.id_SAP.division_client).exclude(
                status='BACKLOG').values('division_client').annotate(the_count=Count('division_client'))

        return table_data


class EditDivView(LoginRequiredMixin, SingleTableView):
    model = ExtractSAP
    table_class = RetitleTable
    template_name = "trackdrawing/Retitle.html"
    division_client = None
    table_pagination = False

    def get_table_data(self):
        self.division_client = self.kwargs['division_client']
        table_data = ExtractSAP.objects.filter(division_client=self.division_client).exclude(status='BACKLOG')
        return table_data

    def get_context_data(self, **kwargs):
        context = super(EditDivView, self).get_context_data(**kwargs)
        context['division_client'] = self.division_client
        return context


class StampView(LoginRequiredMixin, SingleTableView):
    model = ExtractSAP
    table_class = StampingTable
    template_name = "trackdrawing/Stamp_drawings.html"
    paginate_by = 10

    def get_table_data(self):
        table_data = ExtractSAP.objects.filter(status__in=[
            'CLOSED',
            'CHECKED',
            'INVALID',
        ]).exclude(stamped_document__isnull=False).order_by('id')
        return table_data


class ListeSAP(LoginRequiredMixin, SingleTableView):
    model = ExtractSAP
    context_object_name = "derniers_articles"
    table_class = ExtractTable
    template_name = "trackdrawing/ExtractSAP_list.html"
    paginate_by = 10

    def get_table_data(self):
        if (has_group(self.request.user, 'Check')):
            # L'utilisateur connecté fait parti du groupe checker,
            # On récupère sa liste de plan à checker
            nb_plan_c_max = communData.objects.get(pk=1).nb_plan_check
            date_jour = date.today()
            date_veille = date_jour - timedelta(1 if date_jour.weekday() != 0 else 3)
            # date_veille = date_jour - timedelta(4 if date_jour.weekday() != 0 else 3)
            record_to_check = Work_data.objects.filter(id_checker__pk=self.request.user.id, modified_date=date_jour,
                                                       status='CLOSED')
            if len(record_to_check) != 0:
                # La liste des plans à checker est déjà définie pour date_jour
                table_data = []
                for record in record_to_check:
                    table_data.append(ExtractSAP.objects.get(id=record.id_SAP.pk))
                return table_data
            else:
                # La liste des plans à checker n'est pas définie pour date_jour
                # Récupère les obj workdata CLOSED avec idchecker et date_modified < date_jour
                record_to_reset = Work_data.objects.filter(id_checker__pk=self.request.user.id,
                                                           modified_date__lt=date_jour, status='CLOSED')
                # set id checker to null
                for record in record_to_reset:
                    record.id_checker = None
                    # Cette action va mettre a jour le champ modified_date avec la date du jour...
                    # ces objet pourront donc etre selectionné pour le check du lendemain :(
                    record.save()

                # Récupère les obj workdata CLOSED sans idchecker et date_modified = date_veille
                record_list_check = Work_data.objects.filter(id_checker__isnull=True, modified_date=date_veille,
                                                             status='CLOSED')
                # Extract de la liste des utilisateurs à checker
                user_to_check = record_list_check.values('id_user').exclude(id_user__pk__in=[1, 2, 7]).distinct()
                # Nombre de plan à checker par utilisateur
                check_per_user = int(nb_plan_c_max / len(user_to_check))
                tmp_table_data = []
                # Sélection des plans pour chaque utilisateur
                for usr in user_to_check:
                    # print(usr['id_user'])
                    # print(len(record_list_check.filter(id_user__pk=usr['id_user'])))
                    # print(list(record_list_check.filter(id_user__pk=usr['id_user']).values('id')))
                    # Extract des plans de l'utilisateur
                    record_to_check = list(record_list_check.filter(id_user__pk=usr['id_user']).values('id'))
                    if len(record_to_check) > check_per_user:
                        user_record_to_check = random.sample(record_to_check, check_per_user)
                    else:
                        user_record_to_check = record_to_check
                    # Affectation du checker sur les plans de l'utilisateur
                    for plan in user_record_to_check:
                        checked_record = Work_data.objects.get(id=plan['id'])
                        checked_record.id_checker = User.objects.get(pk=self.request.user.id)
                        checked_record.save()
                        # Update de la table pour mise a jour de la vue
                        tmp_table_data.append(ExtractSAP.objects.get(id=checked_record.id_SAP.pk))

                return tmp_table_data
        elif not (has_group(self.request.user, 'postrait_gp')):
            # L'utilisateur connecté ne fait pas partie du groupe checker
            # On récupère sa liste de plan au status OPEN
            user_drawing_list = [record.id_SAP.pk for record in
                                 Work_data.objects.filter(id_user__pk=self.request.user.id, status__in=['OPEN'])]
            table_data = ExtractSAP.objects.filter(id__in=user_drawing_list)
            if table_data.count() == 0:
                # L'utilisateur n'a plus de plan affecté
                # On lui affecte automatiquement une nouvelle liasse
                next_drawing = ExtractSAP.objects.all().exclude(status__in=[
                    'OPEN',
                    'BACKLOG',
                    'CLOSED',
                    'CHECKED',
                    'INVALID',
                    'TO_RE-CHECK',
                ]).order_by('id')[:1]
                if next_drawing.count() != 0:
                    # ==> il reste des plans à produire
                    next_ref = next_drawing[0].num_cadastre[:7]
                    # record_to_dispatched = ExtractSAP.objects.filter(num_cadastre__startswith=next_ref).order_by('id')
                    record_to_dispatched = ExtractSAP.objects.filter(num_cadastre__startswith=next_ref).exclude(
                        status__in=[
                            'OPEN',
                            'BACKLOG',
                            'CLOSED',
                            'CHECKED',
                            'INVALID',
                            'TO_RE-CHECK',
                        ]).order_by('id')
                    for record in record_to_dispatched:
                        Work_data.objects.create(id_SAP=record, id_user=self.request.user, status='OPEN')
                        sap = ExtractSAP.objects.get(id=record.pk)
                        sap.status = 'OPEN'
                        sap.save()
                    return record_to_dispatched
                else:
                    # il n'y a plus de plans à produire, on passe à la phase POSTRAIT
                    user_drawing_list = [record.id_SAP.pk for record in
                                         Work_data.objects.filter(id_rechecker__pk=self.request.user.id,
                                                                  status='TO_RE-CHECK')]
                    record_to_dispatched = ExtractSAP.objects.filter(id__in=user_drawing_list)
                    if record_to_dispatched.count() == 0:
                        next_drawing = Work_data.objects.filter(id_rechecker=None, status='TO_RE-CHECK').order_by('id')[
                                       :1]
                        if next_drawing:
                            next_ref = next_drawing[0].id_SAP.num_cadastre[:7]
                            record_to_dispatched = ExtractSAP.objects.filter(num_cadastre__startswith=next_ref,
                                                                             status='TO_RE-CHECK')
                            for record in record_to_dispatched:
                                oWork_data = Work_data.objects.get(id_SAP=record.pk)
                                oWork_data.id_rechecker = User.objects.get(pk=self.request.user.id)
                                oWork_data.save()

                    return record_to_dispatched

            return table_data
        else:
            # Si rien de tout ca, on renvoie une liste vide
            return []


class FilterModDatabase(LoginRequiredMixin, View):
    template_name = 'trackdrawing/db_filter_view.html'
    table_class = ExtractTableExpanded

    def get(self, request, *args, **kwargs):
        db_filter = ExtractSAPFilter(request.GET, queryset=Work_data.objects.filter(status__in=[
            'CLOSED',
            'CHECKED',
            'INVALID',
        ]))
        if 'typ' in request.GET:  # and request.GET['typ']:
            table = ExtractTableExpanded(db_filter.qs)
            return render(request, self.template_name, {'filter': db_filter, 'table': table})
        else:
            return render(request, self.template_name, {'filter': db_filter})

    def post(self, request, *args, **kwargs):
        db_filter = ExtractSAPFilter(request.GET, queryset=Work_data.objects.filter(status__in=[
            'CLOSED',
            'CHECKED',
            'INVALID',
        ]))

        new_status = 'TO_RE-CHECK'
        SAP_log = logging.getLogger('StatusModification')
        SAP_log.setLevel(logging.INFO)
        SAPHandler = logging.FileHandler('StatusModification.log')
        formatter = logging.Formatter('%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')
        SAPHandler.setFormatter(formatter)
        SAP_log.addHandler(SAPHandler)

        for record in db_filter.qs:
            # Modify work_data status & save
            record.comment = request.POST['comment'] + '\n' + record.comment
            record.id_rechecker = None
            record.status = new_status
            record.save()
            # Modify Extract SAP status & save
            SAP_record = ExtractSAP.objects.get(id=record.id_SAP.pk)
            SAP_record.status = new_status
            SAP_record.save()
            SAP_log.info(
                'Workdata id ' + str(record.pk) + '(' + str(SAP_record.pk) + ')' + ' status changed to re-check')

        SAP_log.removeHandler(SAPHandler)
        SAPHandler.close()
        table = ExtractTableExpanded(db_filter.qs)

        return render(request, self.template_name, {'filter': db_filter, 'table': table})


class CsvModDatabase(LoginRequiredMixin, View):
    template_name = 'trackdrawing/db_csv_view.html'
    table_class = ExtractTableExpanded
    form_class = UploadFileForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES["file"]
            file_data = csv_file.read().decode("utf-8")
            lines = file_data.split("\r\n")
            reduced_list = []
            for line in lines:
                reduced_list.append(Work_data.objects.get(id=line))
            table = ExtractTableExpanded(reduced_list)

            new_status = 'TO_RE-CHECK'
            SAP_log = logging.getLogger('StatusModification')
            SAP_log.setLevel(logging.INFO)
            SAPHandler = logging.FileHandler('StatusModification.log')
            formatter = logging.Formatter('%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')
            SAPHandler.setFormatter(formatter)
            SAP_log.addHandler(SAPHandler)

            for record in reduced_list:
                # Modify work_data status & save
                record.comment = request.POST['comment'] + '\n' + record.comment
                record.id_rechecker = None
                record.status = new_status
                record.save()
                # Modify Extract SAP status & save
                SAP_record = ExtractSAP.objects.get(id=record.id_SAP.pk)
                SAP_record.status = new_status
                SAP_record.save()
                SAP_log.info(
                    'Workdata id ' + str(record.pk) + '(' + str(SAP_record.pk) + ')' + ' status changed to re-check')

            SAP_log.removeHandler(SAPHandler)
            SAPHandler.close()

            return render(request, self.template_name, {'form': form, 'table': table})


class UpdatedInfoCreate(LoginRequiredMixin, UpdateView):
    model = ExtractSAP
    template_name = "trackdrawing/UpdatedInfo.html"
    form_class = UpdatedInfoForm
    success_url = reverse_lazy('accueil')

    def form_valid(self, form):
        SAP_log = logging.getLogger('RecheckModifications')
        SAP_log.setLevel(logging.INFO)
        SAPHandler = logging.FileHandler('RecheckModifications.log')
        formatter = logging.Formatter('%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')
        SAPHandler.setFormatter(formatter)
        SAP_log.addHandler(SAPHandler)

        form.instance.user = self.request.user
        record = Work_data.objects.get(id_SAP__pk=form.instance.pk)
        if form.instance.old_num and not 'Ancien plan' in form.instance.remark:
            form.instance.remark = "Ancien plan: " + form.instance.old_num + "\n" + form.instance.remark
        data = form.cleaned_data
        if has_group(form.instance.user, 'Check') or record.status == 'TO_RE-CHECK':
            # drawing is checked
            status = 'CHECKED'
            drawing = ExtractSAP.objects.get(pk=form.instance.pk)
            for key in UpdatedInfoForm._meta.fields:
                if data[key] != getattr(drawing, key):
                    # One field has been modified by checker
                    status = 'INVALID'
                    if record.status == 'TO_RE-CHECK':
                        # log toute les modifs faites lors du re-check
                        if key == 'typ':
                            # Modification du type
                            SAP_log.info(
                                'ExtractSAP id ' + str(drawing.pk) + ' : champ ' + key + ' changed from ' + getattr(
                                    drawing, key).desc + ' to ' + Type.objects.get(id=data[key].pk).desc)
                        else:
                            try:
                                SAP_log.info(
                                    'ExtractSAP id ' + str(drawing.pk) + ' : champ ' + key + ' changed from ' + getattr(
                                        drawing, key) + ' to ' + data[key])
                            except:
                                SAP_log.info('ExtractSAP id ' + str(drawing.pk) + ' key error ' + key)
                                # break
            record.status = status
            # record.id_checker = form.instance.user
            record.check_time_tracking = parse_duration(data["chronotime"]) - record.time_tracking
        else:
            record.status = "CLOSED"
            record.time_tracking = parse_duration(data["chronotime"])
        if "backlog" in form.data:
            record.status = "BACKLOG"
            record.time_tracking = parse_duration(data["chronotime"])
        if 'validateAll' in form.data:
            SAP_log = logging.getLogger('StatusModification')
            SAP_log.setLevel(logging.INFO)
            SAPHandler = logging.FileHandler('StatusModification.log')
            formatter = logging.Formatter('%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')
            SAPHandler.setFormatter(formatter)

            SAP_log.addHandler(SAPHandler)

            liasse_ref = Work_data.objects.get(id_SAP__pk=form.instance.pk).id_SAP.num_cadastre[:7]
            record_to_dispatched = Work_data.objects.filter(id_SAP__num_cadastre__startswith=liasse_ref,
                                                            status='TO_RE-CHECK').exclude(id_SAP__pk=form.instance.pk)
            for rec in record_to_dispatched:
                # oWork_data = Work_data.objects.get(id_SAP=rec.pk)
                rec.status = 'CLOSED'
                rec.save()
                oExtractSAP = ExtractSAP.objects.get(id=rec.id_SAP.pk)
                old_status = oExtractSAP.status
                oExtractSAP.status = 'CLOSED'
                oExtractSAP.save()
                SAP_log.info(
                    'Workdata id ' + str(rec.pk) + '(' + str(
                        oExtractSAP.pk) + ')' + ' status changed from ' + old_status + ' to CLOSED')
            SAP_log.removeHandler(SAPHandler)
            SAPHandler.close()

        record.comment = form.data["backlog_comment"]
        record.save()
        form.instance.status = record.status

        SAP_log.removeHandler(SAPHandler)
        SAPHandler.close()

        return super(UpdatedInfoCreate, self).form_valid(form)


class FilterDatabase(LoginRequiredMixin, View):
    form_class = ShowDistinct
    template_name = 'trackdrawing/db_view.html'
    status = ['CLOSED', 'CHECKED', 'INVALID']

    def get(self, request, *args, **kwargs):
        form1 = self.form_class()
        return render(request, self.template_name, {'form': form1})

    def post(self, request, *args, **kwargs):
        # print(request.POST)
        form1 = self.form_class(request.POST)
        # if form1.is_valid():
        if "submit" in request.POST:
            if request.POST['contains']:
                search_field = request.POST['field_choice'] + '__contains'
                records = ExtractSAP.objects.filter(**{'status__in': self.status,
                                                       search_field: request.POST['contains']}).values(
                    request.POST['field_choice']).annotate(count=Count(request.POST['field_choice'])).order_by(
                    request.POST['field_choice'])
                First_ID = {record[request.POST['field_choice']]: ExtractSAP.objects.filter(
                    **{request.POST['field_choice']: record[request.POST['field_choice']]}).values('id')[0]['id'] for
                            record in records}
            else:
                records = ExtractSAP.objects.filter(status__in=self.status).values(
                    request.POST['field_choice']).annotate(count=Count(request.POST['field_choice'])).order_by(
                    request.POST['field_choice'])
                First_ID = {record[request.POST['field_choice']]: ExtractSAP.objects.filter(
                    **{request.POST['field_choice']: record[request.POST['field_choice']]}).values('id')[0]['id'] for
                            record in records}
            if request.POST['field_choice'] == 'title':
                search_field = request.POST['field_choice'] + '__contains'
                records = ExtractSAP.objects.filter(**{'status__in': self.status,
                                                       search_field: request.POST['contains']})
                table = CheckExtractTable(records)
                return render(request, self.template_name, {'form': form1, 'records': records, 'table': table})

            # print(records)
            return render(request, self.template_name, {'form': form1, 'records': records, 'First_ID': First_ID})

        if "Modify" in request.POST:
            # print(request.POST)
            list_to_mod = request.POST.getlist("queryselection", "")
            champ = request.POST.get('field_choice')
            search = request.POST.get('contains')
            new_value = request.POST.get('new_value')
            initial_dict = {
                "field_choice": champ,
                "contains": search,
            }
            # form1 = self.form_class(request.POST or None, initial=initial_dict)
            form1 = self.form_class(request.POST, initial=initial_dict)
            # print('I am Here')
            # print(list_to_mod)
            SAP_log = logging.getLogger('ExtractSAP')
            SAP_log.setLevel(logging.INFO)
            SAPHandler = logging.FileHandler('ExtractSAP.log')
            formatter = logging.Formatter('%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')
            SAPHandler.setFormatter(formatter)

            SAP_log.addHandler(SAPHandler)

            for item in list_to_mod:
                champ_exact = champ + '__exact'
                records = ExtractSAP.objects.filter(**{'status__in': self.status,
                                                       champ_exact: item})
                for record in records:
                    SAP_id = str(record.pk)
                    old_value = getattr(record, champ)
                    if new_value:
                        SAP_log.info(
                            'SAP_id: ' + SAP_id + ' champ ' + champ + ' ' + old_value + ' changed to ' + new_value)
                        # record.author = new_value
                        setattr(record, champ, new_value)
                        record.save()

            SAP_log.removeHandler(SAPHandler)
            SAPHandler.close()
            return render(request, self.template_name, {'form': form1})

        # return render(request, self.template_name, {'form': form1})


def UploadDrawing(request, num_cadastre):
    instance = ExtractSAP.objects.get(pk=num_cadastre)
    filename = instance.num_cadastre + ".pdf"
    if request.method == 'POST':
        form = StampedDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            instance.stamped_document = request.FILES['stamped_document']
            instance.save()
            # Suppress temporary file from TMP folder
            fs = FileSystemStorage()
            os.remove(os.path.join(os.path.join(fs.location, 'TMP'), filename))
            return redirect('StampView')
    else:
        form = StampedDocumentForm(instance=instance)
    return render(request, 'trackdrawing/model_form_upload.html', {
        'form': form
    })


def DownloadDrawing(request, num_cadastre):
    from .PDFutils import pdf_add_metadata
    fs = FileSystemStorage()
    record = ExtractSAP.objects.get(pk=num_cadastre)
    filename = record.num_cadastre + ".pdf"
    if fs.exists(os.path.join(os.path.join(fs.location, 'TMP'), filename)):
        return HttpResponseNotFound('The File is already in use')
    else:
        pdf_add_metadata(fs.location, filename, 'NumeroCadastre', record.num_cadastre, filename,
                         os.path.join(fs.location, 'TMP'))
        file_to_open = os.path.join(os.path.join(fs.location, 'TMP'), filename)
        if fs.exists(filename):
            with fs.open(file_to_open) as pdf:
                # Add metadata to the downloaded file
                response = HttpResponse(pdf.read(), content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename=' + filename
                return response
        else:
            return HttpResponseNotFound('The requested pdf was not found in our server.')


def DisplayDrawing(request, num_cadastre):
    fs = FileSystemStorage()
    # listOfFiles = [f[:15] for f in os.listdir('D:\\Prayon') if os.path.isfile('D:\\Prayon\\' + f)]
    # # print(listOfFiles)
    # print('Nb fichiers images',  len(listOfFiles))
    # nb_extract_with_draw = [record.pk for record in ExtractSAP.objects.all() if record.num_cadastre in listOfFiles]
    # print('Nb Extract with images', len(nb_extract_with_draw))
    # nb_extract_without_draw = [record.pk for record in ExtractSAP.objects.all() if record.num_cadastre not in listOfFiles]
    # print('Nb Extract without images', len(nb_extract_without_draw))
    # nb_image_without_record = [image for image in listOfFiles if not ExtractSAP.objects.filter(num_cadastre=image).exists()]
    # print('Nb image without record', len(nb_image_without_record))
    # print('Nb Extract without images', nb_extract_without_draw)
    # print('Nb image without record', nb_image_without_record)
    # filename = 'E53233081_A00_001.PDF'
    filename = ExtractSAP.objects.get(pk=num_cadastre).num_cadastre
    if fs.exists(filename + '.tif'):
        file_in = filename + '.tif'
        file_in_extend = '.tif'
    elif fs.exists(filename + '.tiff'):
        file_in = filename + '.tiff'
        file_in_extend = '.tiff'
    elif fs.exists(filename + '.pdf'):
        file_in = filename + '.pdf'
        file_in_extend = '.pdf'
        file_to_open = os.path.join(fs.location, filename + '.pdf')
    filenamein = file_in
    if fs.exists(filenamein):
        if file_in_extend != ".pdf":
            file_out = filename + '.pdf'
            file_to_open = os.path.join(fs.location, file_out)
            filenameout_tmp = os.path.join(fs.location, filename + '.tiff')
            # with open(filenameout, "wb") as f:
            #     f.write(img2pdf.convert(fs.path(filenamein)))
            # Image convert with PILLOW direct ==> produce large PDF
            image = Image.open(fs.path(filenamein))
            width, height = image.size
            col = image.getcolors()
            image.save(filenameout_tmp, format='TIFF', save_all=True)
            with open(file_to_open, "wb") as f:
                f.write(img2pdf.convert(filenameout_tmp))
            os.remove(filenameout_tmp)
        with fs.open(file_to_open) as pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = 'inline; ' + filenamein
            return response
    else:
        return HttpResponseNotFound('The requested pdf was not found in our server.')
    # return render(request, 'trackdrawing/ExtractSAP_list.html', locals())


def get_title(request):
    record_id = request.GET.get('id', None)
    data = {
        'record_title': ExtractSAP.objects.get(pk=record_id).title
    }
    return JsonResponse(data)


def xed_post(request):
    """
    X-Editable: handle post request to change the value of an attribute of an object

    request.POST['model']: name of Django model of which an object will be changed
    request.POST['pk']: pk of object to be changed
    request.POST['name']: name of the field to be set
    request.POST['value']: new value to be set
    """
    # print(request.POST)
    try:
        if not 'name' in request.POST or not 'pk' in request.POST or not 'value' in request.POST:
            _data = {'success': False, 'error_msg': 'Error, missing POST parameter'}
            return JsonResponse(_data)

        _model = apps.get_model('trackdrawing', request.POST['model'])  # Grab the Django model
        _obj = _model.objects.filter(pk=request.POST['pk']).first()  # Get the object to be changed
        old_value = getattr(_obj, request.POST['name'])
        # print(request.POST['model'], request.POST['pk'], request.POST['name'], request.POST['value'])
        fk_model = get_fk_model(_model, request.POST['name'])
        if fk_model:
            setattr(_obj, request.POST['name'],
                    fk_model.objects.get(id=request.POST['value']))  # Actually change the attribute to the new value
        else:
            setattr(_obj, request.POST['name'], request.POST['value'])  # Actually change the attribute to the new value
        #
        # Record modification to log file
        #
        from .utility import log_info
        # SAP_log = logging.getLogger('ExtractSAP')
        # SAP_log.setLevel(logging.INFO)
        # SAPHandler = logging.FileHandler('ExtractSAP.log')
        # formatter = logging.Formatter('%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')
        # SAPHandler.setFormatter(formatter)
        #
        # SAP_log.addHandler(SAPHandler)

        log_info('SAP_id: ' + request.POST['pk'] + ' champ ' + request.POST['name'] + ' ' + old_value + ' changed to ' +
                 request.POST['value'], 'ExtractSAP')

        _obj.save()  # And save to DB
        # SAP_log.removeHandler(SAPHandler)
        # SAPHandler.close()
        _data = {'success': True}
        return JsonResponse(_data)

    # Catch issues like object does not exist (wrong pk) or other
    except Exception as e:
        _data = {'success': False,
                 'error_msg': f'Exception: {e}'}
        return JsonResponse(_data)


def get_fk_model(model, fieldname):
    '''returns None if not foreignkey, otherswise the relevant model'''
    field_object = model._meta.get_field(fieldname)
    direct = not field_object.auto_created or field_object.concrete
    m2m = field_object.many_to_many
    if not m2m and direct and isinstance(field_object, ForeignKey):
        return field_object.related_model
    return None
