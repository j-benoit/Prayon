#! /usr/bin/env python3
# coding: utf-8
import os
from django.conf import settings
import logging
from PyPDF4 import PdfFileReader


def RenamePDFFiles():
    SAP_log = logging.getLogger('FileManagt')
    SAP_log.setLevel(logging.INFO)
    SAPHandler = logging.FileHandler('FileManagt.log')
    formatter = logging.Formatter('%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')
    SAPHandler.setFormatter(formatter)

    SAP_log.addHandler(SAPHandler)
    for file in os.listdir(settings.MEDIA_ROOT):
        if len(os.path.basename(file)) > 19:
            renamed_file = os.path.splitext(file)[0][:15] + os.path.splitext(file)[1]
            os.rename(os.path.join(settings.MEDIA_ROOT,file),os.path.join(settings.MEDIA_ROOT,renamed_file))
            SAP_log.info(
                'File ' + os.path.basename(file) + ' renamed to ' + renamed_file)
    SAP_log.removeHandler(SAPHandler)
    SAPHandler.close()


def CountPDFPages():
    for file in os.listdir(settings.MEDIA_ROOT):
        with open(os.path.join(settings.MEDIA_ROOT, file),'rb') as pdf:
            try:
                pg = PdfFileReader(pdf).getNumPages()
                print('File ' + os.path.basename(file) + ' has ' + str(pg) + ' page(s)')
            except:
                print('File ' + os.path.basename(file) + ' has raised an error')