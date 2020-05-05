#! /usr/bin/env python3
# coding: utf-8
import os
from django.conf import settings
import logging
from PyPDF4 import PdfFileReader, PdfFileWriter
import win32com.client


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


def CountPDFPages_in_dir(path):
    log_file = 'PDF_page_count_log'
    for file in os.listdir(path):
        log_info("File " + file + " has " + CountPDFPages(path, file) + " page(s)", log_file)


def CountPDFPages(path, file):
    QP = win32com.client.Dispatch("DebenuPDFLibrary64Lite1114.PDFLibrary")
    QP.LoadFromFile(os.path.join(path, file), "")
    return QP.PageCount()


def tiff2pdf(path, file, Out_Path):
    QP = win32com.client.Dispatch("DebenuPDFLibrary64Lite1114.PDFLibrary")
    Out_filename = os.path.splitext(file)[0] + ".pdf"
    QP.AddImageFromFile(os.path.join(path, file), 0)
    lWidth = QP.ImageWidth()
    lHeight = QP.ImageHeight()

    if lWidth != 0 and lHeight != 0:
        QP.SetPageDimensions(lWidth, lHeight)
        QP.DrawImage(0, lHeight, lWidth, lHeight)
        if QP.SaveToFile(os.path.join(Out_Path, Out_filename)) == 1:
            return "File " + file + " successfully convert to pdf"
        else:
            return "File " + file + " could not be convert to pdf"
    else:
        return "File " + file + " has one null dimension"


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


def convert_dir_to_pdf(input_dir, output_dir):
    log_file = 'PDF_utils_log'
    for file in os.listdir(input_dir):
        ext = os.path.splitext(file)[1]
        if ext.casefold() in ['.tif', '.tiff']:
            log_info(tiff2pdf(input_dir, file, output_dir), log_file)
        elif ext.casefold() in ['.pdf']:
            QP = win32com.client.Dispatch("DebenuPDFLibrary64Lite1114.PDFLibrary")
            QP.LoadFromFile(os.path.join(input_dir, file), "")
            QP.RotatePage(-90)
            pages = QP.PageCount()
            if QP.SaveToFile(os.path.join(output_dir, file)) == 1:
                if pages > 1:
                    log_info("File " + file + " has Multi Pages", log_file)
                log_info("File " + file + " copied to output directory (rotated -90°)", log_file)
            else:
                log_info("File " + file + " could not be written", log_file)


def add_textbox_to_pdf(path):
    sc = 72/25.4
    for file in os.listdir(path):
        QP = win32com.client.Dispatch("DebenuPDFLibrary64Lite1114.PDFLibrary")
        QP.LoadFromFile(os.path.join(path, file), "")
        QP.SetTextSize(int(51*sc))
        print(QP.GetPageBox(1,2), QP.GetPageBox(1,3))
        print(QP.PageWidth(), QP.PageHeight())
        QP.SetOrigin(1)
        QP.DrawTextBox(QP.PageWidth()-500,QP.PageHeight()-200,500,200,"test ajout text",0)
        QP.SaveToFile(os.path.join(path, 'new2.pdf'))

def pdf_add_metadata(path, file, key, value):
    with open(os.path.join(path, file),'rb') as pdf:
        try:
            pdf_reader = PdfFileReader(pdf)
            metadata = pdf_reader.getDocumentInfo()
            print(metadata)
            pdf_writer = PdfFileWriter()
            pdf_writer.appendPagesFromReader(pdf_reader)
            pdf_writer.addMetadata({
                '/' + key: value,
            #     # '/Title': 'PDF in Python'
            })
            file_out = open(os.path.join(path, 'new.pdf'), 'wb')
            pdf_writer.write(file_out)
            #
            pdf.close()
            file_out.close()
            # print('File ' + os.path.basename(file) + ' has ' + str(pg) + ' page(s)')
        except ValueError:
            print(ValueError, 'rrrt')


if __name__ == '__main__':
    # Require Foxit ActiveX component DebenuPDFLibrary64Lite1114.dll
    # cmd: regsvr32 'path_to_dll\DebenuPDFLibrary64Lite1114.dll'

    # in_path = "D:\\AUSY\\Prayon\\not_convert"
    # out_path = "D:\\AUSY\\Prayon\\plan a traiter2_PDF"
    # convert_dir_to_pdf(in_path, out_path)

    in_path = "D:\\AUSY\\Prayon\\20200505"
    filename = '8-9S1-BD-7230-081-305-306 AB.pdf'
    pdf_add_metadata(in_path, filename, 'NumeroCadastre', '00000-110-444')
