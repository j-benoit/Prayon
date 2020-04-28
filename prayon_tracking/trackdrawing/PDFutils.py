#! /usr/bin/env python3
# coding: utf-8
import os
from django.core.files.storage import FileSystemStorage


def RenamePDFFiles():
    fs = FileSystemStorage()
    listOfFiles = [f for f in os.listdir(fs.location) if os.path.isfile(fs.location + f)]
    for file in listOfFiles:
        print(file)
        file_to_open = os.path.join(fs.location, file + '.pdf')