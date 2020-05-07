#! /usr/bin/env python3
# coding: utf-8
import os
from django.conf import settings
import logging
from PyPDF4 import PdfFileReader, PdfFileWriter
import win32com.client
from PIL import Image


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
        log_info("File " + file + " has " + str(CountPDFPages(path, file)) + " page(s)", log_file)


def CountTIFFPages_in_dir(path):
    log_file = 'TIFF_page_count_log'
    for file in os.listdir(path):
        ext = os.path.splitext(file)[1]
        if ext.casefold() in ['.tif', '.tiff']:
            try:
                img = Image.open(os.path.join(path, file))
                log_info("File " + file + " has " + str(img.n_frames) + " page(s)", log_file)
                img.close()
            except:
                log_info("File " + file + " can not be readed", log_file)


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


def multitiff2pdf(path, file, Out_Path):
    log_file = 'PDF_utils_log'
    img = Image.open(os.path.join(path, file))
    nb_frame = img.n_frames
    img.close()
    for frame in range(0, nb_frame):
        QP = win32com.client.Dispatch("DebenuPDFLibrary64Lite1114.PDFLibrary")
        Out_filename = os.path.splitext(file)[0] +"-F"+ format((frame + 1), '03d') +".pdf"
        QP.AddImageFromFile(os.path.join(path, file), frame)
        lWidth = QP.ImageWidth()
        lHeight = QP.ImageHeight()

        if lWidth != 0 and lHeight != 0:
            QP.SetPageDimensions(lWidth, lHeight)
            QP.DrawImage(0, lHeight, lWidth, lHeight)
            if QP.SaveToFile(os.path.join(Out_Path, Out_filename)) == 1:
                log_info("File " + file + " frame " + format((frame + 1), '03d') + " successfully convert to pdf", log_file)
            else:
                log_info("File " + file + " frame " + format((frame + 1), '03d') + " could not be convert to pdf", log_file)
        else:
            log_info("File " + file + " frame " + format((frame + 1), '03d') + " has one null dimension", log_file)


def Split_pdf(path, file, Out_Path):
    log_file = 'PDF_utils_log'
    pdf = PdfFileReader(os.path.join(path, file))
    for frame in range(pdf.getNumPages()):
        pdf = PdfFileReader(os.path.join(path, file))
        pdf_writer = PdfFileWriter()
        pdf_writer.addPage(pdf.getPage(frame))
        Out_filename = os.path.splitext(file)[0] +"-F"+ format((frame + 1), '03d') +".pdf"
        with open(os.path.join(Out_Path, Out_filename), 'wb') as out:
            pdf_writer.write(out)
            log_info("File " + file + " frame " + format((frame + 1), '03d') + " successfully splitted", log_file)
        out.close()

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
            # QP.RotatePage(-90)
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

def pdf_add_metadata(path, file, key, value, out_file, out_path=''):
    if out_path == '' :
        out_path = path
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
            file_out = open(os.path.join(out_path, out_file), 'wb')
            pdf_writer.write(file_out)
            #
            pdf.close()
            file_out.close()
            # print('File ' + os.path.basename(file) + ' has ' + str(pg) + ' page(s)')
        except ValueError:
            print(ValueError, 'rrrt')


def get_metadata(file, key):
    with open(file, 'rb') as pdf:
        pdf_reader = PdfFileReader(pdf)
        metadata = pdf_reader.getDocumentInfo()
        print(metadata)
        property = metadata.get('/'+key,'Key Error')
    return property



def pdf_add_Stamp(path, file, stamp):
    with open(os.path.join(path, file),'rb') as pdf:
        pdf_reader = PdfFileReader(pdf)
        with open(os.path.join(path, stamp),'rb') as file_stamp:
            watermark = PdfFileReader(file_stamp)
            first_page = pdf_reader.getPage(0)
            first_page_watermark = watermark.getPage(0)

            first_page.mergePage(first_page_watermark)

            pdf_writer = PdfFileWriter()
            pdf_writer.addPage(first_page)
            pdf_writer.addMetadata({
                '/NumeroCadastre': 'LaTeteAToto',
            #     # '/Title': 'PDF in Python'
            })
            file_out = open(os.path.join(path, 'new_w_stamp.pdf'), 'wb')
            pdf_writer.write(file_out)
            #
            pdf_reader.close()
            file_out.close()
            watermark.close()


if __name__ == '__main__':
    # Require Foxit ActiveX component DebenuPDFLibrary64Lite1114.dll
    # cmd: regsvr32 'path_to_dll\DebenuPDFLibrary64Lite1114.dll'

    # Conversion de plans
    # in_path = "D:\\AUSY\\Prayon\\not_convert"
    # out_path = "D:\\AUSY\\Prayon\\plan a traiter2_PDF"
    # convert_dir_to_pdf(in_path, out_path)

    # Ajout de metadata
    in_path = "D:\\AUSY\\Prayon\\20200506\\Multipage_doc"
    out_path = "D:\\AUSY\\Prayon\\20200506\\PDF"
    filename = '0067032-002-001.pdf'
    filestamp = 'Prayon_Stamp.pdf'
    # pdf_add_metadata(in_path, filename, 'NumeroCadastre', '00000-110-444')
    # pdf_add_Stamp(in_path, filename, filestamp)
    # Split_pdf(in_path, filename, out_path)
    for file in os.listdir(in_path):
        ext = os.path.splitext(file)[1]
        if ext.casefold() in ['.tif', '.tiff']:
            multitiff2pdf(in_path, file, out_path)
        elif ext.casefold() in ['.pdf']:
            Split_pdf(in_path, file, out_path)
