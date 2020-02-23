from django.shortcuts import render
import operator
from functools import reduce
from django.db.models import Q, Count
from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth.models import User, Group
from django.core.files.storage import FileSystemStorage
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.http import HttpResponse, HttpResponseNotFound, FileResponse
from .models import ExtractSAP, Updated_info, Work_data, Project_history, communData
from .forms import UpdatedInfoForm
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
import datetime
import os

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
 
    return redirect('dash')

def GroupUser (request):
    print(request.POST)
    groups = [x.name for x in Group.objects.all()] 
    myUSers= User.objects.all()
    for us in myUSers :
        for gr in us.groups.all():
            for key in request.POST.keys():
                key = key.split("_")
                if key[0] in groups:
                    if us.username == key[1]:
                        try:
                             us.groups.clear()
                        except Exception as e:
                            raise e
                        try:
                            us.groups.add(Group.objects.get(name=key[0]))
                        except Exception as e:
                            raise e
                        
        # us.save()
    return redirect('Admin')


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
            print(old_user_id, new_user_id)
            if old_user_id != new_user_id:
                old_user = User.objects.get(pk=old_user_id)
                new_user = User.objects.get(pk=new_user_id)
                for record in Work_data.objects.filter(id_user=old_user, status__in=['OPEN', 'BACKLOG']):
                    record.id_user = new_user
                    record.save()
            print('toto')
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
        df = df.set_index(['date', 'id_user_id'])
        # Catch most recent date
        max_date = max(df.index.get_level_values(0)).strftime("%Y-%m-%d")
        # Reduce dataframe to the most recent date
        dfextract = df.iloc[df.index.get_level_values('date') == max_date, df.columns.isin({'open_drawings',
                                                                                            'backlog_drawings',
                                                                                            'closed_drawings',
                                                                                            'checked_drawings',
                                                                                            'invalid_drawings'})]
        # Create list for comprehensive username (instead of user id
        list_user = [record.username for record in User.objects.filter(pk__in=
                                                                       dfextract.index
                                                                       .get_level_values('id_user_id').to_list())]

        # Transfer dataframe data to pygal Chart
        line_chart = pygal.StackedBar()
        line_chart.title = 'Users evolution   '
        line_chart.x_labels = list_user
        for col in dfextract.columns.to_list():
            line_chart.add(col, dfextract[col].to_list())
        # Render chart to html for template
        chart_line = line_chart.render_data_uri()

        dfextract = df.iloc[df.index.get_level_values('date') == max_date, df.columns.isin({'avg_closed_time', 'avg_backlog_time'})]
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
            .set_table_styles(styles) \
            .render()

        # print(df.groupby(level=[0]).sum())
        data = Project_history.objects.all()
        if len(history_filter.data) != 0:
            if history_filter.data['id_user']:
                data = data.filter(id_user=history_filter.data['id_user'])
            if history_filter.data['date']:
                data = data.filter(date__lte=history_filter.data['date'])
        df = pd.DataFrame.from_records(data.values())
        df = df.set_index(['date', 'id_user_id'])
        dfextract = df.groupby(level=[0]).sum()
        # print(dfextract)
        dfextract = dfextract.iloc[ : , dfextract.columns.isin({'open_drawings',
                                                                'backlog_drawings',
                                                                'closed_drawings',
                                                                'checked_drawings',
                                                                'invalid_drawings'})]
        # print(dfextract.index)
        xy_chart = pygal.DateTimeLine(x_label_rotation=35)
        xy_chart.title = 'Cumulé équipe'
        for col in dfextract.columns.to_list():
            xy_chart.add(col, [(index, row[col]) for index, row in dfextract.iterrows()])
        chart_xy = xy_chart.render_data_uri()
        return render(request, "trackdrawing/dashboradAdmin.html", locals())
    else:
        data = Project_history.objects.filter(id_user__pk=request.user.id)
        df = pd.DataFrame.from_records(data.values())
        df = df.sort_values('date', ascending=False)
        return render(request, "trackdrawing/dashboradUser.html", locals())


class ListBacklog(SingleTableView):
    pass
    model = Work_data
    context_object_name = "backlog"
    table_class = WorkTable
    template_name = "trackdrawing/Backlog_list.html"
    paginate_by = 10

    def get_table_data(self):
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
            table_data = []
            temp_user = [[record.id_SAP.pk,record.id_user.pk] for record in Work_data.objects.filter(status="CLOSED").exclude(id_user__pk=self.request.user.id)]
            table_data = ExtractSAP.objects.filter(id__in=[x[0] for x in temp_user])
            id_users = list(dict.fromkeys([x[1] for x in temp_user]))
            
            tmp_table_data=[]
            nb_plan_per_user=0
            for idUsr in id_users:
                nb_plan_per_user+=round(nb_plan_c_max/len(id_users),0)
                print(nb_plan_per_user)
                for index in range(0,len(temp_user)):
                    if(temp_user[index][1] == idUsr) : 
                        tmp_table_data.append(table_data[index])
                        nb_plan_per_user-=1
                        if nb_plan_per_user == 0:
                            break
            return tmp_table_data
        else:
            user_drawing_list = [record.id_SAP.pk for record in Work_data.objects.filter(id_user__pk=self.request.user.id, status='OPEN')]
            table_data = ExtractSAP.objects.filter(id__in=user_drawing_list)
            if table_data.count() == 0:
                # Affect new drawing automaticaly
                already_dispatched_records = [record.id_SAP.pk for record in Work_data.objects.all()]
                record_to_dispatched = ExtractSAP.objects.all().exclude(id__in=already_dispatched_records).order_by(
                    'id')[:1]
                new_drawing = Work_data.objects.create(id_SAP=record_to_dispatched[0], id_user=self.request.user, status='OPEN')
                return ExtractSAP.objects.filter(id=new_drawing.id_SAP.pk)

            return table_data


class UpdatedInfoCreate(UpdateView):
    model = ExtractSAP
    template_name = "trackdrawing/UpdatedInfo.html"
    form_class = UpdatedInfoForm
    success_url =reverse_lazy('accueil')

    def form_valid(self, form):
        form.instance.user = self.request.user
        record = Work_data.objects.get(id_SAP__pk=form.instance.pk)
        data = form.cleaned_data
        if has_group(form.instance.user, 'Check'):
            # drawing is checked
            status = 'CHECKED'
            drawing = ExtractSAP.objects.get(pk=form.instance.pk)
            for key in UpdatedInfoForm._meta.fields:
                if data[key] != getattr(drawing,key):
                    # One field has been modified by checker
                    status = 'INVALID'
                    break
            record.status = status
            record.id_checker = form.instance.user
            record.check_time_tracking = parse_duration(data["chronotime"]) - record.time_tracking
            print(parse_duration(data["chronotime"]))
            print(record.time_tracking)
            print(parse_duration(data["chronotime"]) - record.time_tracking)
        else:
            record.time_tracking = parse_duration(data["chronotime"])
        record.save()
        return super(UpdatedInfoCreate, self).form_valid(form)

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
    if fs.exists(os.path.join(fs.location, filename+'.tif')):
        file_in = filename +'.tif'
        file_in_extend = '.tif'
    elif fs.exists(os.path.join(fs.location, filename + '.tiff')):
        file_in = filename + '.tiff'
        file_in_extend = '.tiff'
    elif fs.exists(os.path.join(fs.location, filename+'.pdf')):
        file_to_open = os.path.join(fs.location, filename+'.pdf')
    filenamein = os.path.join(fs.location, file_in)
    if fs.exists(filenamein):
        if file_in_extend:
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
                f.write(img2pdf.convert(fs.path(filenameout_tmp)))
            os.remove(filenameout_tmp)
        with fs.open(file_to_open) as pdf:
           response = HttpResponse(pdf, content_type='application/pdf')
           response['Content-Disposition'] = 'inline; ' + file_to_open.basename
           return response
    else:
        return HttpResponseNotFound('The requested pdf was not found in our server.')
    # return render(request, 'trackdrawing/ExtractSAP_list.html', locals())


# def Send_To_Backlog(request, pk):
#     record = Work_data.objects.get(id_SAP__pk=pk)
#     record.status = 'BACKLOG'
#     record.save()
#     return redirect('accueil')
