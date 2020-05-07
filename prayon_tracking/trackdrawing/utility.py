from django.core.files.storage import FileSystemStorage
from django.db.models import Count
from django.shortcuts import redirect
from .models import ExtractSAP, Work_data, Project_history, communData, Type
import logging, os

def log_info(message, log_file):
    PDF_log = logging.getLogger(log_file)
    PDF_log.setLevel(logging.INFO)
    PDFHandler = logging.FileHandler(log_file + '.log')
    formatter = logging.Formatter('%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')
    PDFHandler.setFormatter(formatter)

    PDF_log.addHandler(PDFHandler)
    PDF_log.info(message)
    PDF_log.removeHandler(PDFHandler)
    PDFHandler.close()

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


def Modify_drawing_status_from_csv():
    import csv
    with open('D:\\sapToRecheckLiasse2.csv', 'r') as file:
        reader = csv.reader(file, delimiter='\t')
        SAP_log = logging.getLogger('StatusModification')
        SAP_log.setLevel(logging.INFO)
        SAPHandler = logging.FileHandler('StatusModification.log')
        formatter = logging.Formatter('%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')
        SAPHandler.setFormatter(formatter)

        SAP_log.addHandler(SAPHandler)

        for row in reader:
            record = (int(row[0]))
            record_to_modify = Work_data.objects.get(id=record)
            old_status = record_to_modify.status
            record_to_modify.status = 'TO_RE-CHECK'
            record_to_modify.id_rechecker = None
            record_to_modify.comment = '[POSTRAIT TYP LIASSE]\n' + record_to_modify.comment
            recordSAP = ExtractSAP.objects.get(id=record_to_modify.id_SAP.pk)
            recordSAP.status = 'TO_RE-CHECK'
            record_to_modify.save()
            recordSAP.save()
            print('Workdata id ' + str(record_to_modify.pk) + '(' + str(recordSAP.pk) + ')' + ' status changed from '+ old_status +' to re-check')

            SAP_log.info(
                'Workdata id ' + str(record_to_modify.pk) + '(' + str(recordSAP.pk) + ')' + ' status changed from '+ old_status +' to re-check')
        SAP_log.removeHandler(SAPHandler)
        SAPHandler.close()


def Modify_drawing_status():
    record_to_modify = Work_data.objects.filter(status='CLOSED', id_SAP__typ__isnull=True)
    for record in record_to_modify:
        record.status = 'BACKLOG'
        recordSAP = ExtractSAP.objects.get(id=record.id_SAP.pk)
        recordSAP.status = 'BACKLOG'
        # record.save()
        # recordSAP.save()
        print("status of Extract SAP id %d has been modified to BACKLOG" %record.id_SAP.pk)


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


def Modify_Multipages_drawing_from_csv():
    import csv
    fs = FileSystemStorage()
    with open('D:\\RecordToDuplicate.csv', 'r') as file:
        reader = csv.reader(file, delimiter=',')
        for row in reader:
            cadastre = (row[0])
            filename = cadastre + '.pdf'
            record_to_duplicate = ExtractSAP.objects.get(num_cadastre=cadastre)
            # change Num cadastre to add Folio n°1
            record_to_duplicate.num_cadastre = cadastre + "-F001"
            log_info("Record " + cadastre + "(" + str(record_to_duplicate.pk) + "), cadastre set to " + record_to_duplicate.num_cadastre, 'CreateDuplicate')
            # os.rename(os.path.join(fs.location, filename),
            #           os.path.join(os.path.join(fs.location, 'backup'), filename))
            record_to_duplicate.save()
            for page in range(1,int(row[1])):
                record_to_duplicate.pk = None # Copy Object
                record_to_duplicate.num_cadastre = cadastre + "-F" + format((page + 1), '03d')
                record_to_duplicate.status = ''
                record_to_duplicate.save()
                log_info("Record " + cadastre + " copy to id " + str(record_to_duplicate.pk) + " , cadastre set to " + record_to_duplicate.num_cadastre, 'CreateDuplicate')
