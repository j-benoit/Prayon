#! /usr/bin/env python3
# coding: utf-8
import re
from crispy_forms.bootstrap import FieldWithButtons, StrictButton
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Column, Field, Layout, Row, Submit
from django import forms
from django.core.validators import EmailValidator, RegexValidator
from django.utils.dateparse import parse_duration

from .models import ExtractSAP, Work_data


class UpdatedInfoForm(forms.ModelForm):
    check_entreprise = forms.BooleanField(required=False, initial=True)
    check_fournisseur = forms.BooleanField(required=False, initial=True)
    check_ext_ref = forms.BooleanField(required=False, initial=True)
    check_old_num = forms.BooleanField(required=False, initial=True)
    check_num_imp = forms.BooleanField(required=False, initial=True)
    backlog_comment = forms.CharField(widget=forms.Textarea, required=False,)
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
            "entreprise",
            "fournisseur",
            "ext_ref",
            "old_num",
            "num_cadastre",
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
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.attrs = {"name": "chronoForm"}
        for field_name, field in self.fields.items():
            self.fields[field_name].widget.attrs["placeholder"] = field_name

        # self.helper.form_show_labels = False
        self.fields["typ"].label = False

        self.helper.layout = Layout(
            Row(
                Column(
                    "check_entreprise",
                    "check_fournisseur",
                    "check_ext_ref",
                    "check_old_num",
                    "check_num_imp",
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
                            css_class="form-label-group col-md-4 mb-0",
                        ),
                        Column(
                            Field(
                                "div",
                                template="trackdrawing/custom_inputs.html",
                                readonly=True,
                            ),
                            css_class="form-group col-md-4 mb-0",
                        ),
                        Column(
                            Field(
                                "num_cadastre",
                                template="trackdrawing/custom_inputs.html",
                                readonly=True,
                            ),
                            css_class="form-group col-md-4 mb-0",
                        ),
                        css_class="form-label-group",
                    ),
                    Row(
                        # Column(Field('typ', template="trackdrawing/custom_select.html"), css_class='col-md-4 mb-0'),
                        Column("typ", required=True, css_class="col-md-4 mb-0"),
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
                            Field(
                                "title",
                                template="trackdrawing/custom_inputs.html",
                                required=True,
                            ),
                            css_class="col-md-10 mb-0",
                        ),
                        Column(
                            Field(
                                "date",
                                template="trackdrawing/custom_inputs.html",
                                required=True,
                            ),
                            css_class="form-group col-md-1 mb-0",
                        ),
                        Column(
                            Field(
                                "author",
                                template="trackdrawing/custom_inputs.html",
                                required=True,
                            ),
                            css_class="form-group col-md-1 mb-0",
                        ),
                        css_class="form-label-group",
                    ),
                    Row(
                        Column(
                            FieldWithButtons(
                                "entreprise",
                                StrictButton(
                                    "?",
                                    css_class="btn-success",
                                    onclick='handleDoubtField(this, "entreprise")',
                                ),
                                template="trackdrawing/custom_input_btn.html",
                                required=True,
                            ),
                            css_class="form-group col-md-3 mb-0",
                        ),
                        Column(
                            FieldWithButtons(
                                "fournisseur",
                                StrictButton(
                                    "?",
                                    css_class="btn-success",
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
                                    css_class="btn-success",
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
                                    css_class="btn-success",
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
                                    css_class="btn-success",
                                    onclick='handleDoubtField(this, "num_ip")',
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
                                    css_class="btn-success",
                                    onclick='handleDoubtField(this, "num_trav")',
                                ),
                                template="trackdrawing/custom_input_btn.html",
                                required=True,
                            ),
                            css_class="form-group col-md-4 mb-0",
                        ),
                        Column(
                            Field(
                                "file_exists",
                                template="trackdrawing/custom_inputs.html",
                            ),
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
                            "backlog_comment", css_class="form-group col-md-12 mb-0"
                        ),
                        css_class="form-row",
                    ),
                    Submit("submit", "Submit"),
                    HTML(
                        '<a class="btn btn-success" href={% url "show_image" num_cadastre=form.instance.pk%} target="pdfview" onClick="chronoStart()" id="id_view">View Drawing</a>'
                    ),
                    # StrictButton('View Drawing', css_class="btn btn-success",  onClick="chronoStart()", name="startstop"),
                    StrictButton(
                        "Pause timer",
                        css_class="btn btn-success",
                        onClick="chronoStart()",
                        name="startstop",
                    ),
                    # HTML('<a class="btn btn-secondary" href={% url "backlog"  pk=form.instance.pk  %} id="id_view"><i class="fas fa-arrow-alt-circle-right"></i>Backlog</a>'),
                    HTML(
                        '<button type="submit" class="btn btn-secondary" name="backlog">'
                        '<i class="fas fa-arrow-alt-circle-right"></i>Backlog'
                        "</button>"
                    ),
                    # Submit('backlog', 'Backlog'),
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

    def clean(self):
        if "submit" in self.data:
            # do submit
            pass
        elif "backlog" in self.data:
            record = Work_data.objects.get(id_SAP__pk=self.instance.pk)
            record.comment = self.data["backlog_comment"]
            record.time_tracking = parse_duration(self.data["chronotime"])
            record.status = "BACKLOG"
            record.save()

    def clean_entreprise(self):
        """
        Validate that the supplied fournisseur field is not empty if associated checkbox is True
       """

        print("TCL: self.cleaned_data", self.cleaned_data)

        field_name = "entreprise"
        value_field = self.cleaned_data[field_name]
        is_fournisseur = self.data.get("check_{}".format(field_name), "off")

        if not self.cleaned_data[field_name] and is_fournisseur == "on":
            alert_no_value = (
                "Merci de remplir le champ demandé ou de cocher la case en question"
            )
            raise forms.ValidationError(alert_no_value)

        return value_field

    def clean_fournisseur(self):
        """
       Validate that the supplied fournisseur field is not empty if associated checkbox is True
       """
        field_name = "fournisseur"
        value_field = self.cleaned_data[field_name]
        is_fournisseur = self.data.get("check_{}".format(field_name), "off")

        if not self.cleaned_data[field_name] and is_fournisseur == "on":
            alert_no_value = (
                "Merci de remplir le champ demandé ou de cocher la case en question"
            )
            raise forms.ValidationError(alert_no_value)

        return value_field

    def clean_ext_ref(self):
        """
       Validate that the supplied fournisseur field is not empty if associated checkbox is True
       """
        field_name = "ext_ref"
        value_field = self.cleaned_data[field_name]
        is_fournisseur = self.data.get("check_{}".format(field_name), "off")

        if not self.cleaned_data[field_name] and is_fournisseur == "on":
            alert_no_value = (
                "Merci de remplir le champ demandé ou de cocher la case en question"
            )
            raise forms.ValidationError(alert_no_value)

        return value_field

    def clean_old_num(self):
        """
       Validate that the supplied fournisseur field is not empty if associated checkbox is True
       """
        field_name = "old_num"
        value_field = self.cleaned_data[field_name]
        is_fournisseur = self.data.get("check_{}".format(field_name), "off")

        if not self.find_punctuation(value_field):
            raise forms.ValidationError("Merci de supprimer les ponctuations")

        if not self.cleaned_data[field_name] and is_fournisseur == "on":
            alert_no_value = (
                "Merci de remplir le champ demandé ou de cocher la case en question"
            )
            raise forms.ValidationError(alert_no_value)

        return value_field

    def clean_num_imp(self):
        """
       Validate that the supplied fournisseur field is not empty if associated checkbox is True
       """
        field_name = "num_imp"
        value_field = self.cleaned_data[field_name]
        is_fournisseur = self.data.get("check_{}".format(field_name), "off")

        if self.find_punctuation(value_field):
            raise forms.ValidationError("Merci de supprimer les ponctuations")

        if not self.cleaned_data[field_name] and is_fournisseur == "on":
            alert_no_value = (
                "Merci de remplir le champ demandé ou de cocher la case en question"
            )
            raise forms.ValidationError(alert_no_value)

        return value_field

    def clean_num_trav(self):
        """
       Validate that the supplied fournisseur field is not empty if associated checkbox is True
       """
        field_name = "num_trav"
        value_field = self.cleaned_data[field_name]
        is_fournisseur = self.data.get("check_{}".format(field_name), "off")

        if not self.num_trav_format(value_field):
            raise forms.ValidationError(
                "Merci de renseigner le champ comme ceci : NNNN/NN"
            )

        return value_field

    def no_value(self, field_name, text):
        checked_field = self.data.get("check_{}".format(field_name), "off")

        if not self.cleaned_data[field_name] and checked_field == "on":
            alert_no_value = (
                "Merci de remplir le champ demandé ou de cocher la case en question"
            )

    def find_punctuation(self, text):
        pattern = "[:,!.?;]"
        result = re.search(pattern, text)
        return not result

    def num_trav_format(self, text):
        pattern = "(\d{1,4})?/(\d{2})?$"
        result = re.match(pattern, text)

        return result

