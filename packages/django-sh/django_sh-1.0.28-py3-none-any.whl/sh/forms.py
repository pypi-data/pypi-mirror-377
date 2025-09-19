import datetime
from django import forms
from django.contrib.auth.models import User
from django.forms.widgets import ClearableFileInput
from . import functions
from .constants import (
    ELEMENTOS_PAGINA,
    MESES,
    SOLO_FECHA_ANTERIOR,
    SOLO_FECHA_POSTERIOR,
    DESDE_1900,
    ANIOS,
)

EMPTY_CHOICE = (("", "---"),)

class BootstrapForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(BootstrapForm, self).__init__(*args, **kwargs)

        for field in self.fields.keys():
            if "class" in self.fields[field].widget.attrs:
                self.fields[field].widget.attrs["class"] += " form-control"
            else:
                self.fields[field].widget.attrs["class"] = "form-control"


class BootstrapModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(BootstrapModelForm, self).__init__(*args, **kwargs)

        for field in self.fields.keys():
            if "class" in self.fields[field].widget.attrs:
                self.fields[field].widget.attrs["class"] += " form-control"
            else:
                self.fields[field].widget.attrs["class"] = "form-control"

class CalendarWidget(forms.DateInput):
    def __init__(self, fecha_validate=0, datetime=False, attrs={'autocomplete':'off'}):

        clases = ""
        if datetime:
            clases = "has_datetimepicker"
            attrs["size"] = "15"
        else:
            clases = "has_datepicker"
            attrs["size"] = "7"

        if fecha_validate == 0:
            clases = "%s fecha_posterior fecha_anterior" % clases

        if fecha_validate == 1:
            clases = "%s fecha_anterior" % clases

        if fecha_validate == 2:
            clases = "%s fecha_posterior" % clases

        attrs["class"] = clases
        super(CalendarWidget, self).__init__(attrs=attrs)


class CalendarDateTimeWidget(forms.DateTimeInput):
    def __init__(
        self, fecha_validate=SOLO_FECHA_ANTERIOR, datetime=True, attrs={}
    ):

        clases = ""
        clases = "has_datetimepicker"
        attrs["size"] = "15"

        if fecha_validate == SOLO_FECHA_ANTERIOR:
            clases = "%s solo_fecha_anterior" % clases

        if fecha_validate == SOLO_FECHA_POSTERIOR:
            clases = "%s solo_fecha_posterior" % clases

        if fecha_validate == DESDE_1900:
            clases = "%s solo_fecha_anterior bigbang" % clases

        attrs["class"] = clases
        super(CalendarDateTimeWidget, self).__init__(attrs=attrs)


class CalendarDateField(forms.DateField):
    def __init__(self, fecha_validate=0, *args, **kwargs):
        calendar_widget = CalendarWidget(
            fecha_validate=fecha_validate, datetime=False
        )

        super(CalendarDateField, self).__init__(
            input_formats=("%d/%m/%y", "%d/%m/%Y"),
            widget=calendar_widget,
            *args,
            **kwargs
        )

class CalendarDateTimeField(forms.DateTimeField):
    def __init__(self, fecha_validate=SOLO_FECHA_ANTERIOR, *args, **kwargs):
        calendar_widget = CalendarDateTimeWidget(
            fecha_validate=fecha_validate, datetime=True
        )
        if "widget" in kwargs:
            calendar_widget = kwargs["widget"]
            del kwargs["widget"]

        super(CalendarDateTimeField, self).__init__(
            input_formats=(
                "%d/%m/%Y %H:%M",
                "%d/%m/%y %H:%M",
                "%d/%m/%y %H:%M:%S",
                "%d/%m/%Y %H:%M:%S",
            ),
            widget=calendar_widget,
            *args,
            **kwargs
        )

class FiltroForm(BootstrapForm):

    SI_NO_OP = (("", "------------"), (1, u"Sí"), (0, u"No"))
    STATUS_OP = (
        ("activos", "Activos"), 
        ("inactivos", "Inactivos"),
        ("todos", "Todos"),
    )
    STATUS_PROVEEDOR = (
        ("","----------------"),
        (1,"En proceso de alta"),
        (2,"Vigente"),
    )
    STATUS_CONTRATO = (
        ("","----------------"),
        (1,"Activo"),
        (2,"Inactivo"),
    )

    page_size = forms.ChoiceField(choices=ELEMENTOS_PAGINA, required=False)

    # req_year = forms.ChoiceField(required=False)
    year = forms.ChoiceField(choices=ANIOS, required=False)

    # req_month = forms.ChoiceField(choices=MESES, required=False)
    month = forms.ChoiceField(choices=MESES, required=False)

    q = forms.CharField(max_length=100, required=False)

    # cuenta_bancaria = forms.ModelChoiceField(CuentaBancaria.objects.none())
    proveedor = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"autocomplete": "off"})
    )
    desde = CalendarDateField(required=False)
    hasta = CalendarDateField(required=False)
    fechahora = CalendarDateTimeField(required=False)
    categoria = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"size": 7})
    )
    subcategoria = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"size": 7})
    )
    subsubcategoria = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"size": 7})
    )
    
    #usuario = forms.ModelChoiceField(
    #    queryset=User.objects.none(), required=False
    #)
    fecha = CalendarDateField(required=False)

    desde_month = forms.ChoiceField(choices=MESES, required=False)
    desde_year = forms.ChoiceField(required=False)
    hasta_month = forms.ChoiceField(choices=MESES, required=False)
    hasta_year = forms.ChoiceField(required=False)

    si_no = forms.ChoiceField(choices=SI_NO_OP, required=False)
    status = forms.ChoiceField(choices=STATUS_OP, required=False)

    booleano = forms.BooleanField(required=False)

    choices = forms.ChoiceField(choices=[], required=False)
    choices2 = forms.ChoiceField(choices=[], required=False)
    choices3 = forms.ChoiceField(choices=[], required=False)
    choices4 = forms.ChoiceField(choices=[], required=False)

    #Reportes
    fecha_vigencia = CalendarDateField(required=False)
    status_contrato = forms.ChoiceField(choices=STATUS_CONTRATO, required=False)
    status_proveedor = forms.ChoiceField(choices=STATUS_PROVEEDOR, required=False)
    fecha_ultima_compra_menor =CalendarDateField(required=False)
    monto_menor_a = forms.CharField(required=False)
    desde_fecha_batch = CalendarDateField(required=False)
    hasta_fecha_batch  = CalendarDateField(required=False)
    
    def clean_q(self):
        """
        Se limpian los espacios extra.
        """
        return " ".join(self.cleaned_data["q"].split())


    def clean(self):
        cleaned_data = self.cleaned_data
        desde = functions.to_datetime(cleaned_data.get("desde"))
        hasta = functions.to_datetime(cleaned_data.get("hasta"), max=True)
        year = cleaned_data.get("year")
        month = cleaned_data.get("month")

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super(FiltroForm, self).__init__(*args, **kwargs)

        """
        #self.fields["cedis"].queryset = get_cedis() 
        self.fields["usuario"].queryset = User.objects.filter(is_active=True)
        
        today = datetime.date.today()
        self.initial["desde"] = today
        self.initial["hasta"] = today
        self.initial["year"] = today.year
        self.initial["month"] = today.month
        self.initial["desde_year"] = today.year
        self.initial["hasta_year"] = today.year
        self.initial["desde_month"] = today.month
        self.initial["hasta_month"] = today.month
        
        if hasattr(self.data, '_mutable') and not self.data._mutable:
            self.data = self.data.copy()

        if self.data.get('month') is None:
            self.data['month'] = today.month
        if self.data.get('year') is None:
            self.data['year'] = today.year  
        if self.data.get('desde') is None:
            self.data['desde'] = today
        if self.data.get('hasta') is None:
            self.data['hasta'] = today
        if self.data.get('activa') is None:
            self.data['activa'] = 1
        """
