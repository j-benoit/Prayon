#! /usr/bin/env python3
# coding: utf-8
import re
from crispy_forms.bootstrap import FieldWithButtons, StrictButton
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Column, Field, Layout, Row, Submit
from django import forms
from django.core.validators import EmailValidator, RegexValidator, ProhibitNullCharactersValidator
from django.utils.dateparse import parse_duration
from django.forms.widgets import HiddenInput
from django.core.exceptions import ValidationError

from .models import ExtractSAP, Work_data
from .utils import has_group


class ShowDistinct(forms.ModelForm):
    FIELD_CHOICE = [
        ('author', 'Author'),
        ('fournisseur', 'Entreprise'),
        ('title', 'titre')
    ]
    field_choice = forms.ChoiceField(choices = FIELD_CHOICE)
    contains = forms.CharField(required=False)

    class Meta:
        model=ExtractSAP
        fields = (
            "field_choice",
            "contains",
        )

    def __init__(self, *args, **kwargs):
        super(ShowDistinct, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.form_show_labels = True
        self.helper.layout = Layout(
            Row(
                Column(
                    Field(
                        "field_choice",
                    ),
                    css_class="form-label col-md-3 mb-0",
                ),
                Column(
                    Field(
                        "contains",
                        # template="trackdrawing/custom_inputs.html",
                    ),
                    css_class="form-group col-md-9 mb-0",
                ),
                css_class="form-label",
            ),
            Submit("submit", "Submit"),
        )


class UpdatedInfoForm(forms.ModelForm):
    backlog_comment = forms.CharField(widget=forms.Textarea(attrs={'rows':5,}), required=False)
    chronotime = forms.CharField()

    class Meta:
        model = ExtractSAP
        fields = (
            "site",
            "div",
            "typ",
            "num",
            "folio",
            "title",
            "date",
            "author",
            "tag",
            "fournisseur",
            "ext_ref",
            "old_num",
            "ordre_nv",
            "num_cadastre",
            "rev_cadastre",
            "poste",
            "label_Poste",
            "P1",
            "label_P1",
            "P2",
            "label_P2",
            "P3",
            "label_P3",
            "P4",
            "label_P4",
            "P5",
            "label_P5",
            "P6",
            "label_P6",
            "num_imp",
            "num_trav",
            "file_exists",
        )

    def __init__(self, *args, **kwargs):
        super(UpdatedInfoForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.attrs = {"name": "chronoForm"}
        for field_name, field in self.fields.items():
            self.fields[field_name].widget.attrs["placeholder"] = field_name

        # self.helper.form_show_labels = False
        self.fields["typ"].label = False

        self.fields["old_num"].validators = [
            RegexValidator('[:,!.?;]', message="Merci de supprimer les ponctuations", inverse_match=True)]
        self.fields["num_imp"].validators = [
            RegexValidator('[:,!.?;]', message="Merci de supprimer les ponctuations", inverse_match=True)]
        # self.fields["num_trav"].validators = [
        #     RegexValidator('(\d{1,4})?/(\d{2})?$', message="Merci de renseigner le champ comme ceci : NNNN/NN")]

        # Get comment from Work_data
        record = Work_data.objects.get(id_SAP__pk=self.instance.pk)
        comment = record.comment
        self.fields["backlog_comment"].initial = comment
        self.fields["chronotime"].initial = record.time_tracking

        # Set visibibilty depending of content
        test_fields = ["poste",
                       "P1",
                       "P2",
                       "P3",
                       "P4",
                       "P5",
                       "P6"]
        for test_field in test_fields:
            if not getattr(record.id_SAP, test_field):
                if test_field == "poste":
                    self.fields["label_Poste"].widget = HiddenInput()
                    self.fields["label_Poste"].label = ""
                else:
                    self.fields["label_" + test_field].widget = HiddenInput()
                    self.fields["label_" + test_field].label = ""
                self.fields[test_field].widget = HiddenInput()
                self.fields[test_field].label = ""

        self.helper.layout = Layout(
            Row(
                Column(
                    css_class="col col-md-1 mb-0",
                ),
                Column(
                    Row(
                        Column(
                            Field(
                                "site",
                                template="trackdrawing/custom_inputs.html",
                                readonly=True,
                            ),
                            css_class="form-label-group col-md-3 mb-0",
                        ),
                        Column(
                            Field(
                                "div",
                                template="trackdrawing/custom_inputs.html",
                                readonly=True,
                            ),
                            css_class="form-group col-md-3 mb-0",
                        ),
                        Column(
                            Field(
                                "num_cadastre",
                                template="trackdrawing/custom_inputs.html",
                                readonly=True,
                            ),
                            css_class="form-group col-md-3 mb-0",
                        ),
                        Column(
                            FieldWithButtons(
                                "rev_cadastre",
                                StrictButton(
                                    "?",
                                    css_class=self.choose_btn_class("rev_cadastre", comment),
                                    onclick='handleDoubtField(this, "rev_cadastre")',
                                ),
                                template="trackdrawing/custom_input_btn.html",
                            ),
                            css_class="form-group col-md-3 mb-0",
                        ),
                        css_class="form-label-group",
                    ),
                    Row(
                        Column(
                            Row(
                                Column("typ", required=True, css_class="col-md-11 mb-0"),
                                Column(
                                    StrictButton(
                                        "?",
                                        # css_class="btn-success" ,
                                        css_class=self.choose_btn_class("typ", comment),
                                        name="btn_typ",
                                        onclick='handleDoubtField(this, "typ")',
                                    ),
                                    css_class="col-md-1 mb-0",
                                ),
                            ),
                            css_class="col-md-4 mb-0"
                        ),
                        Column(
                            Field("num", template="trackdrawing/custom_inputs.html"),
                            css_class="form-group col-md-4 mb-0",
                        ),
                        Column(
                            Field("folio", template="trackdrawing/custom_inputs.html",),
                            css_class="form-group col-md-4 mb-0",
                        ),
                        css_class="form-label-group",
                    ),
                    Row(
                        Column(
                            FieldWithButtons(
                                "title",
                                StrictButton(
                                    "?",
                                    css_class=self.choose_btn_class("title", comment),
                                    onclick='handleDoubtField(this, "title")',
                                ),
                                template="trackdrawing/custom_input_btn.html",
                            ),
                            css_class="col-md-8 mb-0",
                        ),
                        Column(
                            FieldWithButtons(
                                "date",
                                StrictButton(
                                    "?",
                                    css_class=self.choose_btn_class("date", comment),
                                    onclick='handleDoubtField(this, "date")',
                                ),
                                template="trackdrawing/custom_input_btn.html",
                            ),
                            css_class="form-group col-md-2 mb-0",
                        ),
                        Column(
                            FieldWithButtons(
                                "author",
                                StrictButton(
                                    "?",
                                    css_class=self.choose_btn_class("author", comment),
                                    onclick='handleDoubtField(this, "author")',
                                ),
                                template="trackdrawing/custom_input_btn.html",
                            ),
                            css_class="form-group col-md-2 mb-0",
                        ),
                        css_class="form-label-group",
                    ),
                    Row(
                        Column(
                            FieldWithButtons(
                                "tag",
                                StrictButton(
                                    "?",
                                    css_class=self.choose_btn_class("tag", comment),
                                    onclick='handleDoubtField(this, "tag")',
                                ),
                                template="trackdrawing/custom_input_btn.html",
                            ),
                            css_class="form-group col-md-3 mb-0",
                        ),
                        Column(
                            FieldWithButtons(
                                "fournisseur",
                                StrictButton(
                                    "?",
                                    css_class=self.choose_btn_class("fournisseur", comment),
                                    onclick='handleDoubtField(this, "fournisseur")',
                                ),
                                template="trackdrawing/custom_input_btn.html",
                                required=True,
                            ),
                            css_class="form-group col-md-3 mb-0",
                        ),
                        Column(
                            FieldWithButtons(
                                "ext_ref",
                                StrictButton(
                                    "?",
                                    css_class=self.choose_btn_class("ext_ref", comment),
                                    onclick='handleDoubtField(this, "ext_ref")',
                                ),
                                template="trackdrawing/custom_input_btn.html",
                                required=True,
                            ),
                            css_class="form-group col-md-3 mb-0",
                        ),
                        Column(
                            FieldWithButtons(
                                "old_num",
                                StrictButton(
                                    "?",
                                    css_class=self.choose_btn_class("old_num", comment),
                                    onclick='handleDoubtField(this, "old_num")',
                                ),
                                template="trackdrawing/custom_input_btn.html",
                                required=True,
                            ),
                            css_class="form-group col-md-3 mb-0",
                        ),
                        css_class="form-row",
                    ),
                    Row(
                        Column(
                            FieldWithButtons(
                                "num_imp",
                                StrictButton(
                                    "?",
                                    css_class=self.choose_btn_class("num_imp", comment),
                                    onclick='handleDoubtField(this, "num_imp")',
                                ),
                                template="trackdrawing/custom_input_btn.html",
                                required=True,
                            ),
                            css_class="form-group col-md-4 mb-0",
                        ),
                        Column(
                            FieldWithButtons(
                                "num_trav",
                                StrictButton(
                                    "?",
                                    css_class=self.choose_btn_class("num_trav", comment),
                                    onclick='handleDoubtField(this, "num_trav")',
                                ),
                                template="trackdrawing/custom_input_btn.html",
                                required=True,
                            ),
                            css_class="form-group col-md-4 mb-0",
                        ),
                        Column(
                            FieldWithButtons(
                                "ordre_nv",
                                StrictButton(
                                    "?",
                                    css_class=self.choose_btn_class("ordre_nv", comment),
                                    onclick='handleDoubtField(this, "ordre_nv")',
                                ),
                                template="trackdrawing/custom_input_btn.html",
                                required=True,
                            ),
                            # Field(
                            #     "file_exists",
                            #     template="trackdrawing/custom_inputs.html",
                            # ),
                            css_class="form-group col-md-4 mb-0",
                        ),
                        css_class="form-row",
                    ),
                    Row(
                        Column(
                            Field(
                                "poste",
                                template="trackdrawing/custom_inputs.html",
                                readonly=True,
                            ),
                            css_class="form-group col-md-2 mb-0",
                        ),
                        Column(
                            Field(
                                "label_Poste",
                                template="trackdrawing/custom_inputs.html",
                                readonly=True,
                            ),
                            css_class="form-group col-md-10 mb-0",
                        ),
                        css_class="form-row",
                    ),
                    Row(
                        Column(
                            Field(
                                "P1",
                                template="trackdrawing/custom_inputs.html",
                                readonly=True,
                            ),
                            css_class="form-group col-md-2 mb-0",
                        ),
                        Column(
                            Field(
                                "label_P1",
                                template="trackdrawing/custom_inputs.html",
                                readonly=True,
                            ),
                            css_class="form-group col-md-10 mb-0",
                        ),
                        css_class="form-row",
                    ),
                    Row(
                        Column(
                            Field(
                                "P2",
                                template="trackdrawing/custom_inputs.html",
                                readonly=True,
                            ),
                            css_class="form-group col-md-2 mb-0",
                        ),
                        Column(
                            Field(
                                "label_P2",
                                template="trackdrawing/custom_inputs.html",
                                readonly=True,
                            ),
                            css_class="form-group col-md-10 mb-0",
                        ),
                        css_class="form-row",
                    ),
                    Row(
                        Column(
                            Field(
                                "P3",
                                template="trackdrawing/custom_inputs.html",
                                readonly=True,
                            ),
                            css_class="form-group col-md-2 mb-0",
                        ),
                        Column(
                            Field(
                                "label_P3",
                                template="trackdrawing/custom_inputs.html",
                                readonly=True,
                            ),
                            css_class="form-group col-md-10 mb-0",
                        ),
                        css_class="form-row",
                    ),
                    Row(
                        Column(
                            Field(
                                "P4",
                                template="trackdrawing/custom_inputs.html",
                                readonly=True,
                            ),
                            css_class="form-group col-md-2 mb-0",
                        ),
                        Column(
                            Field(
                                "label_P4",
                                template="trackdrawing/custom_inputs.html",
                                readonly=True,
                            ),
                            css_class="form-group col-md-10 mb-0",
                        ),
                        css_class="form-row",
                    ),
                    Row(
                        Column(
                            Field(
                                "P5",
                                template="trackdrawing/custom_inputs.html",
                                readonly=True,
                            ),
                            css_class="form-group col-md-2 mb-0",
                        ),
                        Column(
                            Field(
                                "label_P5",
                                template="trackdrawing/custom_inputs.html",
                                readonly=True,
                            ),
                            css_class="form-group col-md-10 mb-0",
                        ),
                        css_class="form-row",
                    ),
                    Row(
                        Column(
                            Field(
                                "P6",
                                template="trackdrawing/custom_inputs.html",
                                readonly=True,
                            ),
                            css_class="form-group col-md-2 mb-0",
                        ),
                        Column(
                            Field(
                                "label_P6",
                                template="trackdrawing/custom_inputs.html",
                                readonly=True,
                            ),
                            css_class="form-group col-md-10 mb-0",
                        ),
                        css_class="form-row",
                    ),
                    Row(
                        Column(
                                StrictButton(
                                "Fichier Illisible",
                                css_class="btn btn-success",
                                onClick="illisible(this)",
                                name="btn_illisible",
                            ),
                            css_class="form-group col-md-3 mb-0"
                        ),
                        Column(
                            StrictButton(
                                "Schéma électrique",
                                css_class="btn btn-success",
                                onClick="electrique(this)",
                                name="btn_elec",
                            ),
                            css_class="form-group col-md-3 mb-0"
                        ),
                        Column(
                            StrictButton(
                                "Fichier mauvaise qualité",
                                css_class="btn btn-success",
                                onClick="qualite(this)",
                                name="btn_qualite",
                            ),
                            css_class="form-group col-md-3 mb-0"
                        ),
                        Column(
                            StrictButton(
                                "Numéro de cadastre",
                                css_class="btn btn-success",
                                onClick="cadastre(this)",
                                name="btn_num_cadatsre",
                            ),
                            css_class="form-group col-md-3 mb-0"
                        ),
                        css_class="form-row",
                    ),
                    Row(
                        Column(
                            "backlog_comment", css_class="form-group col-md-12 mb-0"
                        ),
                        css_class="form-row",
                    ),

                    css_class="col-md-10 mb-0",
                ),
                Column(
                    Field(
                        "chronotime",
                        template="trackdrawing/custom_inputs.html",
                        readonly=True,
                        value="00:00:00",
                    ),
                    css_class="col-md-1 mb-0 display_chrono",
                ),
            ),
        )

        if self.instance.status in ['OPEN', 'CLOSED', 'BACKLOG']:
            self.helper.layout.append(
                Row(
                    Column(css_class="col col-md-1 mb-0", ),
                    Column(
                        Row(
                            Submit("submit", "Submit"),
                            HTML(
                                '<a class="btn btn-success" href={% url "show_image" num_cadastre=form.instance.pk%} target="pdfview" onClick="chronoStart()" id="id_view">View Drawing</a>'
                            ),
                            # StrictButton(
                            #     "Pause timer",
                            #     css_class="btn btn-success",
                            #     onClick="chronoStart()",
                            #     name="startstop",
                            # ),
                            HTML(
                                '<button type="submit" class="btn btn-secondary" name="backlog">'
                                '<i class="fas fa-arrow-alt-circle-right"></i>Backlog'
                                "</button>"
                            ),
                            css_class="form-row",
                        )
                        , css_class="col col-md-10 mb-0",
                    ),
                    Column(css_class="col col-md-1 mb-0", ),
                ),
            )

        if self.instance.status in ['CHECKED', 'INVALID']:
            self.helper.layout.append(
                Row(
                    Column(css_class="col col-md-1 mb-0", ),
                    Column(
                        Row(
                            HTML(
                                '<a class="btn btn-success" href={% url "show_image" num_cadastre=form.instance.pk%} target="pdfview" id="id_view">View Drawing</a>'
                            ),
                            css_class="form-row",
                        )
                        , css_class="col col-md-10 mb-0",
                    ),
                    Column(css_class="col col-md-1 mb-0", ),
                ),
            )


    def choose_btn_class(self, field, comment):
        if "[" + field.upper() + "]" in comment:
            return "btn-warning"
        else:
            return "btn-success"

    def clean_typ(self):
        typ = self.cleaned_data['typ']

        if not typ:
            raise ValidationError('Le type est obligatoire')

        return typ