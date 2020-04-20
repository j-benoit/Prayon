from django.shortcuts import render
import operator
from functools import reduce
from django.db.models import Q, Count
from django.views.generic import ListView, CreateView, UpdateView
from django.views import View
from django.contrib.auth.models import User, Group
from django.core.files.storage import FileSystemStorage
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.http import HttpResponse, HttpResponseNotFound, FileResponse, HttpResponseRedirect
from .models import ExtractSAP, Work_data, Project_history, communData
from .forms import UpdatedInfoForm, ShowDistinct
from django.contrib.auth.decorators import login_required
from itertools import cycle
from django.contrib.auth.mixins import LoginRequiredMixin
from .filters import Project_historyFilter
from django.utils.dateparse import parse_duration


from django_tables2 import SingleTableView
from .tables import ExtractTable, WorkTable

from PIL import Image
import img2pdf

import pandas as pd
from django_pandas.io import read_frame

import os.path
from .utils import has_group
from statistics import mean
import pygal
from datetime import date, timedelta
import random
import os

import logging

try:
    from io import BytesIO as IO # for modern python
except ImportError:
    from io import StringIO as IO # for legacy python

# Create your views here.
def Dispatch_Work (request):
    """
    Dispatch drawings among users in group 'Prod'
    :param request:
    :return:
    """
    drawings_per_user = int(request.POST["plans_nb"])
    already_dispatched_records = [record.id_SAP.pk for record in Work_data.objects.all()]
    record_to_dispatched = ExtractSAP.objects.all().exclude(id__in=already_dispatched_records).order_by('id')[:drawings_per_user]
    prod_user = User.objects.filter(groups__name='Prod').order_by('id')
    pool_user = cycle(prod_user)
    for record in record_to_dispatched:
        current_user = next(pool_user)
        print(current_user.username + " get " + record.num_cadastre)
        Work_data.objects.create(id_SAP=record, id_user=current_user, status='OPEN')

    return redirect('dash')

def Test (request):
    # Modify_drawing_status()
    # Modify_drawing_status_from_csv()
    # Delete_record_from_csv()
    # from .check import check_database
    # check_database()

    return redirect('Admin')


def Export_Database(request):
    names = [
        'id',
        'id_SAP',
        'id_user__username',
        'id_checker__username',
        'status',
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
        'Nouveau numéro Ordre',
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
        'created date',
        'modified date',
        'comment',
        'time tracking',
        'check time tracking',
        'id SAP_sap',
        'status',
        'status_sap'
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

    response = HttpResponse(excel_file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="Export_SAP.xlsx"'
    return response


def Delete_Duplicate_Records(request):
    duplicates = ExtractSAP.objects.values(
        'num_cadastre'
    ).annotate(name_count=Count('num_cadastre')).filter(name_count__gt=1)
    records = ExtractSAP.objects.filter(num_cadastre__in=[item['num_cadastre'] for item in duplicates])
    print(set([item.num_cadastre for item in records]))
    for num_cadastre in set([item.num_cadastre for item in records]):
        record = ExtractSAP.objects.filter(num_cadastre=num_cadastre)
        for record_to_delete in record[1:]:
            record_to_delete.delete()

            print(str(record_to_delete.pk) + "[DUPLICATE] this record is duplicated with " + str(record[0].pk))

    return redirect('Admin')


def Send_Missing_Drawing_to_Backlog(request):
    fs = FileSystemStorage()
    listOfFiles = [f[:15] for f in os.listdir('Y:\\') if os.path.isfile('Y:\\' + f)]
    extract_without_draw = [record.pk for record in ExtractSAP.objects.all() if record.num_cadastre not in listOfFiles]
    for pk in extract_without_draw:
        recordSAP = ExtractSAP.objects.get(id=pk)
        recordSAP.file_exists ='N/A'
        recordSAP.save()
        record, created = Work_data.objects.get_or_create(id_SAP=recordSAP, id_user=request.user)
        if created:
            record.id_SAP = recordSAP
        record.id_user = request.user
        record.status = 'BACKLOG'
        record.comment = '[ERROR] No drawing for this record'
        record.save()
    return redirect('Admin')


def Modify_drawing_status():
    record_to_modify = Work_data.objects.filter(status='CLOSED', id_SAP__typ__isnull=True)
    for record in record_to_modify:
        record.status = 'BACKLOG'
        recordSAP = ExtractSAP.objects.get(id=record.id_SAP.pk)
        recordSAP.status = 'BACKLOG'
        # record.save()
        # recordSAP.save()
        print("status of Extract SAP id %d has been modified to BACKLOG" %record.id_SAP.pk)

def Modify_drawing_status_from_csv():
    import csv
    with open('D:\\sapToBacklog.csv', 'r') as file:
        reader = csv.reader(file, delimiter='\t')
        for row in reader:
            record = (int(row[0]))
            record_to_modify = Work_data.objects.get(id=record)
            record_to_modify.status = 'BACKLOG'
            recordSAP = ExtractSAP.objects.get(id=record_to_modify.id_SAP.pk)
            recordSAP.status = 'BACKLOG'
            record_to_modify.save()
            recordSAP.save()
            print("status of Extract SAP id %d has been modified to BACKLOG" %record_to_modify.id_SAP.pk)


def Delete_record_from_csv():
    import csv
    with open('D:\\sapToOpen2.csv', 'r') as file:
        reader = csv.reader(file, delimiter='\t')
        for row in reader:
            record = (int(row[0]))
            record_to_suppress = Work_data.objects.get(id=record)
            recordSAP = ExtractSAP.objects.get(id=record_to_suppress.id_SAP.pk)
            recordSAP.status = ''
            record_to_suppress.delete()
            # record.save()
            recordSAP.save()
            print("status of Extract SAP id %d has been modified to OPEN" %record_to_suppress.id_SAP.pk)
    record = Work_data.objects.get(id=53)
    record.save()


def Admin(request):
    # get number of drawing that remain not affected
    nb_plan_max = ExtractSAP.objects.all().count() - Work_data.objects.all().count()
    # set drawings quantity to be checked
    nb_plan_c_max = communData.objects.get(pk=1).nb_plan_check

    groupes = Group.objects.all().exclude(name='CP')
    usr = User.objects.all()

    old_user_list = Work_data.objects.filter(status__in=['OPEN', 'BACKLOG']).values('id_user', 'id_user__username').distinct()
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


def nbChecker (request):
   
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
                                                                       .get_level_values('id_user_id').to_list())}

        for key, value in list_user.items():
            df.rename(index={key: value}, inplace=True)
        # order df by descending index
        df.sort_index(level=('id_user_id','date'), ascending=False, inplace=True)
        # keep only the n top row for each user
        top = 1
        df = df.groupby(level=0).apply(lambda df: df[:top])
        df.index = df.index.droplevel(0)

        dfextract = df.iloc[ : , df.columns.isin({'open_drawings','backlog_drawings','closed_drawings','checked_drawings','invalid_drawings'})]
        # Transfer dataframe data to pygal Chart
        line_chart = pygal.StackedBar()
        line_chart.title = 'Users evolution   '
        line_chart.x_labels = dfextract.index.get_level_values('id_user_id').to_list()
        for col in dfextract.columns.to_list():
            line_chart.add(col, dfextract[col].to_list())
        # Render chart to html for template
        chart_line = line_chart.render_data_uri()

        dfextract = df.iloc[ :, df.columns.isin({'avg_closed_time', 'avg_backlog_time'})]
        dfextract['Avg'] = dfextract.apply(lambda row : (row.avg_closed_time + row.avg_backlog_time)/2, axis=1)
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
                     'Avg': lambda x: printNiceTimeDelta(x)})\
            .set_table_styles(styles) \
            .render()

        # print(df.groupby(level=[0]).sum())
        data = Project_history.objects.all()
        if len(history_filter.data) != 0:
            if history_filter.data['id_user']:
                data = data.filter(id_user__pk__in=[int(x) for x in history_filter.data.getlist('id_user')])
            if history_filter.data['start_date'] and history_filter.data['end_date']:
                data = data.filter(date__gte=history_filter.data['start_date'], date__lte=history_filter.data['end_date'])
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

        dfextract = dfextract.iloc[ : , dfextract.columns.isin({'open_drawings',
                                                                'backlog_drawings',
                                                                'closed_drawings',
                                                                'checked_drawings',
                                                                'invalid_drawings'})]
        # add column with closed/Checked & invalid data
        dfextract['Completed_drawings'] = dfextract.apply(lambda row: (row.closed_drawings + row.checked_drawings + row.invalid_drawings), axis=1)
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
                     'Avg': lambda x: printNiceTimeDelta(x)})\
            .set_table_styles(styles) \
            .render()

        return render(request, "trackdrawing/dashboradAdmin.html", locals())
    else:
        data = Project_history.objects.filter(id_user__pk=request.user.id)
        df = pd.DataFrame.from_records(data.values())
        df = df.sort_values('date', ascending=False)
        return render(request, "trackdrawing/dashboradUser.html", locals())


# Define helper function
def fill_missing(grp):
    res = grp.set_index('date')\
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
        out   = ":".join(outAr)
        return out
    else:
        return ""


class ListBacklog(SingleTableView):
    model = Work_data
    context_object_name = "backlog"
    table_class = WorkTable
    template_name = "trackdrawing/Backlog_list.html"
    table_pagination = False
    # paginate_by = 10

    def get_table_data(self):
        if has_group(self.request.user, 'CP'):
            table_data = Work_data.objects.filter(id_checker__pk=self.request.user.id).exclude(status='OPEN')
        else:
            table_data = Work_data.objects.filter(id_user__pk=self.request.user.id).exclude(status='OPEN')
        return table_data


class ListeSAP(LoginRequiredMixin, SingleTableView):
    model = ExtractSAP
    context_object_name = "derniers_articles"
    table_class = ExtractTable
    template_name = "trackdrawing/ExtractSAP_list.html"
    paginate_by = 10

    def get_table_data(self):
        if(has_group(self.request.user,'Check')) :
            nb_plan_c_max = communData.objects.get(pk=1).nb_plan_check
            date_jour = date.today()
            date_veille = date_jour - timedelta(1 if date_jour.weekday() != 0 else 3)
            # date_veille = date_jour - timedelta(4 if date_jour.weekday() != 0 else 3)
            record_to_check = Work_data.objects.filter(id_checker__pk=self.request.user.id, modified_date=date_jour, status='CLOSED')
            if len(record_to_check) != 0:
                # La liste des plans à checker est déjà définie pour date_jour
                table_data = []
                for record in record_to_check:
                    table_data.append(ExtractSAP.objects.get(id=record.id_SAP.pk))
                return table_data
            else:
                # La liste des plans à checker n'est pas définie pour date_jour
                # Récupère les obj workdata CLOSED avec idchecker et date_modified < date_jour
                record_to_reset = Work_data.objects.filter(id_checker__pk=self.request.user.id, modified_date__lt=date_jour, status='CLOSED')
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
        else:
            user_drawing_list = [record.id_SAP.pk for record in Work_data.objects.filter(id_user__pk=self.request.user.id, status='OPEN')]
            table_data = ExtractSAP.objects.filter(id__in=user_drawing_list)
            if table_data.count() == 0:
                # Affect new drawing automaticaly
                # already_dispatched_records = [record.id_SAP.pk for record in Work_data.objects.all()]
                # for record in ExtractSAP.objects.all():
                #     if record.pk not in already_dispatched_records:
                #         records = record
                #         break
                # records = [record for record in Work_data.objects.all() if record.id_SAP.pk not in already_dispatched_records]
                next_drawing = ExtractSAP.objects.all().exclude(status__in=[
                        'OPEN',
                        'BACKLOG',
                        'CLOSED',
                        'CHECKED',
                        'INVALID',
                    ]).order_by('id')[:1]
                next_ref = next_drawing[0].num_cadastre[:7]
                # record_to_dispatched = ExtractSAP.objects.filter(num_cadastre__startswith=next_ref).order_by('id')
                record_to_dispatched = ExtractSAP.objects.filter(num_cadastre__startswith=next_ref).exclude(status__in=[
                        'OPEN',
                        'BACKLOG',
                        'CLOSED',
                        'CHECKED',
                        'INVALID',
                    ]).order_by('id')
                for record in record_to_dispatched:
                    Work_data.objects.create(id_SAP=record, id_user=self.request.user, status='OPEN')
                    sap = ExtractSAP.objects.get(id=record.pk)
                    sap.status ='OPEN'
                    sap.save()
                return record_to_dispatched

            return table_data


class UpdatedInfoCreate(UpdateView):
    model = ExtractSAP
    template_name = "trackdrawing/UpdatedInfo.html"
    form_class = UpdatedInfoForm
    success_url =reverse_lazy('accueil')

    def form_valid(self, form):
        form.instance.user = self.request.user
        record = Work_data.objects.get(id_SAP__pk=form.instance.pk)
        if form.instance.old_num:
            form.instance.remark = "Ancien plan: " + form.instance.old_num + "\n" + form.instance.remark
        data = form.cleaned_data
        if has_group(form.instance.user, 'Check'):
            # drawing is checked
            status = 'CHECKED'
            drawing = ExtractSAP.objects.get(pk=form.instance.pk)
            for key in UpdatedInfoForm._meta.fields:
                if data[key] != getattr(drawing, key):
                    # One field has been modified by checker
                    status = 'INVALID'
                    break
            record.status = status
            record.id_checker = form.instance.user
            record.check_time_tracking = parse_duration(data["chronotime"]) - record.time_tracking
        elif "submit" in form.data:
            record.status = "CLOSED"
            record.time_tracking = parse_duration(data["chronotime"])
        elif "backlog" in form.data:
            record.status = "BACKLOG"
            record.time_tracking = parse_duration(data["chronotime"])
        record.comment = form.data["backlog_comment"]
        record.save()
        form.instance.status = record.status
        return super(UpdatedInfoCreate, self).form_valid(form)


class FilterDatabase(View):
    form_class = ShowDistinct
    template_name = 'trackdrawing/db_view.html'
    status = ['CLOSED', 'BACKLOG', 'CHECKED', 'INVALID']

    def get(self, request, *args, **kwargs):
        form1 = self.form_class()
        return render(request, self.template_name, {'form': form1})

    def post(self, request, *args, **kwargs):
        # print(request.POST)
        form1 = self.form_class(request.POST)
        # if form1.is_valid():
        if "submit" in request.POST:
            if request.POST['contains']:
                search_field = request.POST['field_choice'] +'__contains'
                records = ExtractSAP.objects.filter(**{'status__in': self.status,
                                                       search_field: request.POST['contains']}).values(request.POST['field_choice']).annotate(count=Count(request.POST['field_choice'])).order_by(request.POST['field_choice'])
            else:
                records = ExtractSAP.objects.filter(status__in=self.status).values(request.POST['field_choice']).annotate(count=Count(request.POST['field_choice'])).order_by(request.POST['field_choice'])

            # print(records)
            return render(request, self.template_name, {'form': form1, 'records': records})

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
                        SAP_log.info('SAP_id: ' + SAP_id + ' champ ' + champ + ' ' + old_value + ' changed to ' + new_value)
                        # record.author = new_value
                        setattr(record, champ, new_value)
                        record.save()

            SAP_log.removeHandler(SAPHandler)
            SAPHandler.close()
            return render(request, self.template_name, {'form': form1})

        # return render(request, self.template_name, {'form': form1})


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
    if fs.exists(filename +'.tif'):
        file_in = filename +'.tif'
        file_in_extend = '.tif'
    elif fs.exists(filename + '.tiff'):
        file_in = filename + '.tiff'
        file_in_extend = '.tiff'
    elif fs.exists(filename+'.pdf'):
        file_in = filename + '.pdf'
        file_in_extend = '.pdf'
        file_to_open = os.path.join(fs.location, filename+'.pdf')
    filenamein = file_in
    if fs.exists(filenamein):
        if file_in_extend != ".pdf":
            file_out = filename + '.pdf'
            file_to_open = os.path.join(fs.location, file_out)
            filenameout_tmp = os.path.join(fs.location,filename + '.tiff')
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

