from django.urls import reverse
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Avg


from datetime import timedelta
from django.utils import timezone


# Create your models here.
class Type(models.Model):
    type = models.CharField(max_length=100, verbose_name='Type de documents')
    code = models.CharField(max_length=3, verbose_name='Codification')
    desc = models.CharField(max_length=100, verbose_name='Description')
    expl = models.CharField(max_length=100, verbose_name='Signification codification')

    def __str__(self):
        return self.desc


class communData(models.Model):
    nb_plan_check = models.IntegerField(verbose_name='Nombre des plans a checker')


class ExtractSAP(models.Model):
    site = models.CharField(max_length=2, verbose_name='Site', blank=True)
    div = models.CharField(max_length=3, verbose_name='Div.', blank=True)
    ordre = models.IntegerField(verbose_name='Ordre', blank=True)
    typ = models.ForeignKey(Type, null=True, on_delete=models.PROTECT, blank=True)
    num = models.CharField(max_length=100, verbose_name='Num.', blank=True)
    folio = models.CharField(max_length=100, verbose_name='Folio', blank=True)
    status = models.CharField(max_length=3, verbose_name='Statut', blank=True)
    rev = models.CharField(max_length=2, verbose_name='Rev', blank=True)
    id_doc = models.CharField(max_length=100, verbose_name='ID Document', blank=True)
    last_ver = models.CharField(max_length=100, verbose_name='Dernière version', blank=True)
    label = models.CharField(max_length=100, verbose_name='Libellé de l ordre PM', blank=True)
    tr = models.CharField(max_length=100, verbose_name='Transfert vers ordre', blank=True)
    link = models.CharField(max_length=100, verbose_name='Lien vers le serveur', blank=True)
    title = models.CharField(max_length=100, verbose_name='Titre du document', blank=True)
    cat = models.CharField(max_length=100, verbose_name='Catégorie de document', blank=True)
    date = models.CharField(max_length=100, verbose_name='Date d émission', blank=True)
    origin = models.CharField(max_length=100, verbose_name='Provenance', blank=True)
    author = models.CharField(max_length=100, verbose_name='Auteur', blank=True)
    checker = models.CharField(max_length=100, verbose_name='Vérificateur', blank=True)
    approval = models.CharField(max_length=100, verbose_name='Approbateur', blank=True)
    validator = models.CharField(max_length=100, verbose_name='Validateur', blank=True)
    entreprise = models.CharField(max_length=100, verbose_name='Entrepreneur', blank=True)
    fournisseur = models.CharField(max_length=100, verbose_name='Fournisseur (Nom)', blank=True)
    ext_ref = models.CharField(max_length=100, verbose_name='Référence externe', blank=True)
    old_num = models.CharField(max_length=100, verbose_name='Ancien numéro de plan', blank=True)
    num_cadastre = models.CharField(max_length=100, verbose_name='Numéro Cadastre ENG', blank=True)
    rev_cadastre = models.CharField(max_length=100, verbose_name='Révision Cadastre Eng', blank=True)
    P1 = models.CharField(max_length=100, verbose_name='Poste technique #1', blank=True)
    label_P1 = models.CharField(max_length=100, verbose_name='Libellé Poste technique #1', blank=True)
    P2 = models.CharField(max_length=100, verbose_name='Poste technique #2', blank=True)
    label_P2 = models.CharField(max_length=100, verbose_name='Libellé Poste technique #2', blank=True)
    P3 = models.CharField(max_length=100, verbose_name='Poste technique #3', blank=True)
    label_P3 = models.CharField(max_length=100, verbose_name='Libellé Poste technique #3', blank=True)
    P4 = models.CharField(max_length=100, verbose_name='Poste technique #4', blank=True)
    label_P4 = models.CharField(max_length=100, verbose_name='Libellé  Poste technique #4', blank=True)
    P5 = models.CharField(max_length=100, verbose_name='Poste technique #5', blank=True)
    label_P5 = models.CharField(max_length=100, verbose_name='Libellé Poste technique #5', blank=True)
    P6 = models.CharField(max_length=100, verbose_name='Poste technique #6', blank=True)
    label_P6 = models.CharField(max_length=100, verbose_name='Libellé Poste technique #6', blank=True)
    poste = models.CharField(max_length=100, verbose_name='Poste technique', blank=True)
    label_Poste = models.CharField(max_length=100, verbose_name='Libellé Poste Technique', blank=True)
    remark = models.CharField(max_length=100, verbose_name='Remarque', blank=True)
    old_des = models.CharField(max_length=100, verbose_name='Ancienne désignation', blank=True)
    num_imp = models.CharField(max_length=100, verbose_name='N° d imputation', blank=True)
    num_trav = models.CharField(max_length=100, verbose_name='N° de bon de travail', blank=True)
    file_exists = models.CharField(max_length=100, verbose_name='Existance fichier tif/pdf/dwg', blank=True)

    def __str__(self):
        return self.num_cadastre

class Updated_info(models.Model):
    site = models.CharField(max_length=2, verbose_name='Site')
    div = models.CharField(max_length=3, verbose_name='Div.')
    ordre = models.CharField(max_length=8, verbose_name='Ordre')
    typ = models.ForeignKey(Type, null= True, on_delete=models.PROTECT)
    num = models.CharField(max_length=100, verbose_name='Num.')
    folio = models.CharField(max_length=100, verbose_name='Folio')
    status = models.CharField(max_length=3, verbose_name='Statut')
    rev = models.CharField(max_length=2, verbose_name='Rev')
    id_doc = models.CharField(max_length=100, verbose_name='ID Document')
    last_ver = models.CharField(max_length=100, verbose_name='Dernière version')
    label = models.CharField(max_length=100, verbose_name='Libellé de l ordre PM')
    tr = models.CharField(max_length=100, verbose_name='Transfert vers ordre')
    link = models.CharField(max_length=100, verbose_name='Lien vers le serveur')
    title = models.CharField(max_length=100, verbose_name='Titre du document')
    cat = models.CharField(max_length=100, verbose_name='Catégorie de document')
    date = models.CharField(max_length=100, verbose_name='Date d émission')
    origin = models.CharField(max_length=100, verbose_name='Provenance')
    author = models.CharField(max_length=100, verbose_name='Auteur')
    checker = models.CharField(max_length=100, verbose_name='Vérificateur')
    approval = models.CharField(max_length=100, verbose_name='Approbateur')
    validator = models.CharField(max_length=100, verbose_name='Validateur')
    entreprise = models.CharField(max_length=100, verbose_name='Entrepreneur')
    fournisseur = models.CharField(max_length=100, verbose_name='Fournisseur (Nom)')
    ext_ref = models.CharField(max_length=100, verbose_name='Référence externe')
    old_num = models.CharField(max_length=100, verbose_name='Ancien numéro de plan', validators=[])
    num_cadastre = models.CharField(max_length=100, verbose_name='Numéro Cadastre ENG')
    rev_cadastre = models.CharField(max_length=100, verbose_name='Révision Cadastre Eng')
    P1 = models.CharField(max_length=100, verbose_name='Poste technique #1')
    label_P1 = models.CharField(max_length=100, verbose_name='Libellé Poste technique #1')
    P2 = models.CharField(max_length=100, verbose_name='Poste technique #2')
    label_P2 = models.CharField(max_length=100, verbose_name='Libellé Poste technique #2')
    P3 = models.CharField(max_length=100, verbose_name='Poste technique #3')
    label_P3 = models.CharField(max_length=100, verbose_name='Libellé Poste technique #3')
    P4 = models.CharField(max_length=100, verbose_name='Poste technique #4')
    label_P4 = models.CharField(max_length=100, verbose_name='Libellé  Poste technique #4')
    P5 = models.CharField(max_length=100, verbose_name='Poste technique #5')
    label_P5 = models.CharField(max_length=100, verbose_name='Libellé Poste technique #5')
    P6 = models.CharField(max_length=100, verbose_name='Poste technique #6')
    label_P6 = models.CharField(max_length=100, verbose_name='Libellé Poste technique #6')
    poste = models.CharField(max_length=100, verbose_name='Poste technique')
    label_Poste = models.CharField(max_length=100, verbose_name='Libellé Poste Technique')
    remark = models.CharField(max_length=100, verbose_name='Remarque')
    old_des = models.CharField(max_length=100, verbose_name='Ancienne désignation')
    num_imp = models.CharField(max_length=100, verbose_name='N° d imputation')
    num_trav = models.CharField(max_length=100, verbose_name='N° de bon de travail')
    file_exists = models.CharField(max_length=100, verbose_name='Existance fichier tif/pdf/dwg')


class Work_data(models.Model):
    DRAWING_STATUS = [
        ('OPEN', 'OPEN'),
        ('BACKLOG', 'BACKLOG'),
        ('CLOSED', 'CLOSED'),
        ('CHECKED', 'CHECKED'),
        ('INVALID', 'INVALID'),
    ]
    id_SAP = models.OneToOneField(ExtractSAP, on_delete=models.PROTECT)
    id_user = models.ForeignKey(User, on_delete=models.PROTECT)
    status = models.CharField(max_length=7, choices=DRAWING_STATUS, default='OPEN')
    created_date = models.DateField(auto_now_add=True)
    modified_date = models.DateField(auto_now=True)
    comment = models.TextField(blank=True)
    time_tracking = models.DurationField(default=timedelta(), blank=True)


class Project_history(models.Model):

    id_user = models.ForeignKey(User, on_delete=models.PROTECT)
    date = models.DateField(auto_now=False)
    open_drawings = models.IntegerField(verbose_name='Plans Ouverts', blank=True, null=True)
    backlog_drawings = models.IntegerField(verbose_name='Plans au Backlog', blank=True, null=True)
    closed_drawings = models.IntegerField(verbose_name='Plans Fermés', blank=True, null=True)
    checked_drawings = models.IntegerField(verbose_name='Plans Vérifiés', blank=True, null=True)
    avg_closed_time = models.DurationField(blank=True, null=True)
    avg_backlog_time = models.DurationField(blank=True, null=True)

    # @receiver(post_save, sender=Work_data)
    # def create_history(sender, instance, created, **kwargs):
    #     if created:
    #         print(instance.id_user, timezone.now())
            # Project_history.objects.create(id_user=instance.id_user, date=timezone.now())

    @receiver(post_save, sender=Work_data)
    def save_history(sender, instance, **kwargs):
        record, created = Project_history.objects.get_or_create(id_user=instance.id_user, date=timezone.now().date())
        record.open_drawings = Work_data.objects.filter(id_user=instance.id_user, modified_date__lte=timezone.now().date(),
                                                        status='OPEN').count()
        record.backlog_drawings = Work_data.objects.filter(id_user=instance.id_user, modified_date__lte=timezone.now().date(),
                                                        status='BACKLOG').count()
        record.closed_drawings = Work_data.objects.filter(id_user=instance.id_user, modified_date__lte=timezone.now().date(),
                                                        status='CLOSED').count()
        record.checked_drawings = Work_data.objects.filter(id_user=instance.id_user, modified_date__lte=timezone.now().date(),
                                                        status='CHECKED').count()
        record.avg_closed_time = Work_data.objects.filter(id_user=instance.id_user, modified_date__lte=timezone.now().date(),
                                                          status='CLOSED').aggregate(Avg('time_tracking'))['time_tracking__avg']
        record.avg_backlog_time = \
        Work_data.objects.filter(id_user=instance.id_user, modified_date__lte=timezone.now().date(),
                                 status='BACKLOG').aggregate(Avg('time_tracking'))['time_tracking__avg']
        record.save()

