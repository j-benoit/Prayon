from django.core.files.storage import FileSystemStorage
from django.db.models import Count
from django.shortcuts import redirect
from django.contrib.auth.models import User
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


def Modify_drawing_from_csv():
    import csv
    # fs = FileSystemStorage()
    with open('D:\\Maj1805suite.csv', 'r') as file:
        reader = csv.reader(file, delimiter=',')
        for row in reader:
            id, old_num, ordre, num_imp, num_trav = row
            id_SAP = getattr(Work_data.objects.get(id=id),'id_SAP')
            print(id,old_num,ordre,num_imp,num_trav)
            record = ExtractSAP.objects.get(id=id_SAP.pk)
            ordre = int(ordre) if ordre else None

            # if old_num and old_num != record.old_num:
            if old_num != record.old_num:
                # change Num Ancien plan
                log_info("Record " + record.num_cadastre + "(" + str(record.pk) + "), ancien plan changed to " + old_num + "("+record.old_num+")", 'BatchModification')
                record.old_num = old_num
                record.remark = "Ancien plan: " + old_num
            if ordre != record.ordre:
                # change Num ordre
                log_info("Record " + record.num_cadastre + "(" + str(record.pk) + "), ordre changed to " + str(ordre) + "("+str(record.ordre)+")", 'BatchModification')
                record.ordre = ordre
            if num_imp != record.num_imp:
                # change Num imputation
                log_info("Record " + record.num_cadastre + "(" + str(record.pk) + "), imputation changed to " + num_imp + "("+record.num_imp+")", 'BatchModification')
                record.num_imp = num_imp
            if num_trav != record.num_trav:
                # change Num travaux
                log_info("Record " + record.num_cadastre + "(" + str(record.pk) + "), Num Trav changed to " + num_trav + "(" + record.num_trav + ")", 'BatchModification')
                record.num_trav = num_trav
            # os.rename(os.path.join(fs.location, filename),
            #           os.path.join(os.path.join(fs.location, 'backup'), filename))
            record.save()


def Modify_division_from_csv():
    import csv
    # fs = FileSystemStorage()
    with open('D:\\MajDiv_Client.csv', 'r') as file:
        reader = csv.reader(file, delimiter='|')
        for row in reader:
            pk, div_client = row
            record = ExtractSAP.objects.get(id=pk)
            record.division_client = div_client
            log_info("Record " + record.num_cadastre + "(" + str(
                record.pk) + "), division client changed to " + div_client, 'DivClientModification')
            record.save()

def create_new_drawing_id():
    records = ExtractSAP.objects.all().exclude(status='BACKLOG') # Tous les enregistrements sauf ceux qui sont au Backlog
    records = records.exclude(site='') # Supprime les enregistrements avec site = blank
    records = records.exclude(div='') # Supprime les enregistrements avec div = blank
    records = records.exclude(ordre=None) # Supprime les enregistrements avec numero ordre = blank
    records_multi = records.exclude(typ__isnull=True) # Supprime les enregistrements avec Type = blank
    records = records_multi.exclude(num_cadastre__regex=r'(F\d{3})$')  # Supprime les enregistrements multipage

    list_test = list(records.values_list('site','div','ordre','typ__code').distinct())

    # Process single page drawings
    for site, div, ordre, type in list_test:
        recs = records.filter(site=site, div=div, ordre=ordre, typ__code=type)

        for num, rec in enumerate(recs):
            # folio = rec.folio if rec.folio is not '' else 0
            folio = 0 # Initilisation du folio, pas de multipage dans cette boucle

            rev = rec.rev if rec.rev is not '' else 0
            # rev = 0 # Initialisation de la révision

            new_id = rec.site + "_" + format(int(rec.div), '03d') + "_" + str(rec.ordre) + "_" \
                     + rec.typ.code + "_" + format(int(num), '06d') + "_" + format(int(folio), '03d') \
                     + "_ASB_" + format(int(rev), '03d')

            log_info(str(rec.id) + " new id: " + new_id + ', ' + rec.num_cadastre, 'NumberingDraws')

            # Backup Record
            rec.div = format(int(rec.div), '03d')
            rec.num = format(int(num), '06d')
            rec.folio = format(int(folio), '03d')
            rec.rev = format(int(rev), '03d')
            rec.id_doc = new_id
            rec.save()

    # Process multipage records
    records = records_multi.filter(num_cadastre__regex=r'(F\d{3})$')  # Conserve uniquement les enregistrements multipage
    list_test = list(records.values_list('site','div','ordre','typ__code').distinct())

    for site, div, ordre, type in list_test:
        num = records_multi.filter(site=site, div=format(int(div), '03d'), ordre=ordre, typ__code=type).count()
        recs = records.filter(site=site, div=div, ordre=ordre, typ__code=type)
        list_drw = list(recs.filter(num_cadastre__regex=r'F001$').values_list('num_cadastre', flat=True).distinct())
        for drw in list_drw:
            drawing = drw[:len(drw)-5]
            rec_draw = recs.filter(num_cadastre__startswith=drawing)

            for rec in rec_draw:
                folio = int(rec.num_cadastre[-3:])-1
                rev = rec.rev if rec.rev is not '' else 0 # Initialisation de la révision

                new_id = rec.site + "_" + format(int(rec.div), '03d') + "_" + str(rec.ordre) + "_" \
                         + rec.typ.code + "_" + format(int(num), '06d') + "_" + format(int(folio), '03d') \
                         + "_ASB_" + format(int(rev), '03d')

                log_info(str(rec.id) + " new id: " + new_id + ', ' + rec.num_cadastre, 'NumberingDraws')

                # Backup Record
                rec.div = format(int(rec.div), '03d')
                rec.num = format(int(num), '06d')
                rec.folio = format(int(folio), '03d')
                rec.rev = format(int(rev), '03d')
                rec.id_doc = new_id
                rec.save()
            num +=1


def Modify_Num_Cadastre_from_csv():
    import csv
    # fs = FileSystemStorage()
    with open('D:\\9_Unsplit.csv', 'r') as file:
        reader = csv.reader(file, delimiter='|')
        for row in reader:
            pk, num_cadastre = row
            record = ExtractSAP.objects.get(id=Work_data.objects.get(id=pk).id_SAP.pk)
            record.num_cadastre = num_cadastre
            log_info("Record " + record.num_cadastre + "(" + str(
                record.pk) + "), numero cadastre changed to " + num_cadastre, 'ModifBase200602')
            record.save()

    file.close()
    with open('D:\\8_deleterecord.csv', 'r') as file:
        reader = csv.reader(file, delimiter='|')
        for row in reader:
            pk = int(row[0])
            owork = Work_data.objects.get(id=pk)
            record = ExtractSAP.objects.get(id=owork.id_SAP.pk)
            log_info("Record " + record.num_cadastre + "(" + str(
                record.pk) + "), suppressed", 'ModifBase200602')
            owork.delete()
            record.delete()

    file.close()

    with open('D:\\6_NoFile.csv', 'r') as file:
        reader = csv.reader(file, delimiter='|')
        for row in reader:
            pk = int(row[0])
            owork = Work_data.objects.get(id=pk)
            record = ExtractSAP.objects.get(id=owork.id_SAP.pk)
            owork.status = 'BACKLOG'
            record.status = 'BACKLOG'
            record.file_exists ='N/A'

            log_info("Record " + record.num_cadastre + "(" + str(
                record.pk) + "), status changed to BACKLOG (no associated file)", 'ModifBase200602')
            owork.save()
            record.save()

    file.close()

    with open('D:\\5_CancelFile.csv', 'r') as file:
        reader = csv.reader(file, delimiter='|')
        for row in reader:
            pk = int(row[0])
            owork = Work_data.objects.get(id=pk)
            record = ExtractSAP.objects.get(id=owork.id_SAP.pk)
            if record.remark:
                record.remark = record.remark + '\nPLAN ANNULE'
            else:
                record.remark = 'PLAN ANNULE'

            log_info("Record " + record.num_cadastre + "(" + str(
                record.pk) + "), 'PLAN ANNULE' added to remark", 'ModifBase200602')
            record.save()

    file.close()

    # 3 & 4_à gérer en folio déjà splitté
    with open('D:\\3_4_duplicate.csv', 'r') as file:
        reader = csv.reader(file, delimiter='|')
        for row in reader:
            pk = int(row[0])
            owork = Work_data.objects.get(id=pk)
            record_to_duplicate = ExtractSAP.objects.get(id=owork.id_SAP.pk)
            cadastre = record_to_duplicate.num_cadastre
            filename = cadastre + '.pdf'
            # change Num cadastre to add Folio n°1
            record_to_duplicate.num_cadastre = cadastre + "-F001"
            record_to_duplicate.status = ''
            record_to_duplicate.file_exists = ''
            record_to_duplicate.remark = ''
            log_info("Record " + cadastre + "(" + str(record_to_duplicate.pk) + "), cadastre set to " + record_to_duplicate.num_cadastre, 'ModifBase200602')
            # os.rename(os.path.join(fs.location, filename),
            #           os.path.join(os.path.join(fs.location, 'backup'), filename))
            record_to_duplicate.save()
            for page in range(1,int(row[1])):
                record_to_duplicate.pk = None # Copy Object
                record_to_duplicate.num_cadastre = cadastre + "-F" + format((page + 1), '03d')
                record_to_duplicate.status = ''
                record_to_duplicate.save()
                log_info("Record " + cadastre + " copy to id " + str(record_to_duplicate.pk) + " , cadastre set to " + record_to_duplicate.num_cadastre, 'ModifBase200602')
            owork.delete()
    # 1 & 2_à gérer en folio déjà splitté
    with open('D:\\1_2_duplicate.csv', 'r') as file:
        reader = csv.reader(file, delimiter='|')
        for row in reader:
            new_cadastre, record_to_update, record_to_duplicate = row
            if record_to_update:
                owork = Work_data.objects.get(id_SAP__pk=record_to_update)
                record = ExtractSAP.objects.get(id=record_to_update)
                cadastre = record.num_cadastre
                filename = cadastre + '.pdf'
                # change Num cadastre to add Folio n°1
                record.num_cadastre = new_cadastre
                record.status = ''
                record.file_exists = ''
                record.remark = ''
                log_info("Record " + cadastre + "(" + str(record.pk) + "), cadastre set to " + new_cadastre, 'ModifBase200602')
                record.save()
                owork.delete()
            if record_to_duplicate:
                record = ExtractSAP.objects.get(id=record_to_duplicate)
                cadastre = record.num_cadastre
                record.pk = None # Copy Object
                record.num_cadastre = new_cadastre
                record.status = ''
                record.save()
                log_info("Record " + cadastre + " copy to id " + str(record.pk) + " , cadastre set to " + new_cadastre, 'ModifBase200602')

