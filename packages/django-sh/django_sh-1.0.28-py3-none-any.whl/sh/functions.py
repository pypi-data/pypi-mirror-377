# -*- coding: utf-8 -*-
from __future__ import absolute_import  
from decimal import Decimal
from django.http import HttpResponseNotFound, HttpResponseRedirect
from django.utils import timezone
from django.conf import settings
from django.shortcuts import _get_queryset
try:
    from django.urls import reverse
except:
    from django.core.urlresolvers import reverse


def date_to_str(date, to_date=False, short_year=False):
    from datetime import datetime

    if not date:
        return ""
        
    if short_year:
        date_format = "%d/%m/%y"
    else:
        date_format = "%d/%m/%Y"

    datetime_format = "%s %s" % (date_format, "%H:%M:%S")

    if isinstance(date, (datetime)):
        local_date = localtime(date)
        if to_date:
            return local_date.strftime(date_format)

        return local_date.strftime(datetime_format)
        
    return date.strftime(date_format)

def to_datetime(date, max=False):
    import datetime
    if not isinstance(date, (datetime.date, datetime.datetime)):
        return date
    dt = datetime.datetime
    current_tz = timezone.get_current_timezone()
    t = dt.min.time()
    if max:
        t = dt.max.time()
    if settings.USE_TZ:
        return dt.combine(date, t).replace(tzinfo=current_tz)
    return dt.combine(date, t)

def localtime(time=None):
    import datetime
    
    if not time:
        time = timezone.now()
    
    elif not isinstance(time, (datetime.datetime)):
        return time
    
    if not settings.USE_TZ:
        return time

    return timezone.localtime(time)

def get_fecha_cfdi(fecha):
    from datetime import datetime
    fecha_str = fecha.replace("Z", "").split('.')[0][0:19]
    return to_datetime(datetime.strptime(fecha_str, "%Y-%m-%dT%H:%M:%S"))
    
class Object:
    pass

def es_imagen(file):
    from PIL import Image
    try:
        trial_image = Image.open(file)
        trial_image.verify()
        return True
    except (IOError, AttributeError):
        return False

def clean_redirect(to, *args, **kwargs):
    """
    Regresa un HttpResponseRedirect basado en el parámetro recibido.

    Los argumentos son:

    """
    qs = kwargs.pop('qs', '')
    success = kwargs.pop('success', '')
    errmsg = kwargs.pop('errmsg', '')
    url = reverse(to, args=args, kwargs=kwargs)
    sig = "?"
    if success:
        url = u"%s?success=%s" % (url, success)
        sig = "&"
    
    elif errmsg:
        url = u"%s%serrmsg=%s" % (url, sig, errmsg)
        sig = "&"

    else:
        url = u"%s%s" % (url, qs)
        sig = "&"

    return HttpResponseRedirect(url)
    


def write_text_file(location, text):
    f = open(location, 'w')
    f.write(text)
    f.close()
    return f

def random_password(length, 
allowed_chars = 'abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789'):
    "Generates a random password with the given length and given allowed_chars"
    from random import choice
    return ''.join([choice(allowed_chars) for i in range(length)])

def escape_xml(string):
    string = unicode(string)
    string = " ".join(string.split())
    return string.replace("&", "&amp;")\
                          .replace("'", "&apos;")\
                          .replace('"', "&quot;")\
                          .replace("<", "&lt;")\
                          .replace(">", "&gt;")\
                          .replace("|", "")

def unescape_xml(string):
    return unicode(string).replace("&apos;", "'")\
                          .replace('&quot;', '"')\
                          .replace("&lt;", "<")\
                          .replace("&gt;", ">")\
                          .replace("&amp;", "&")

def random(length):
    "Generates a random text with the given length and given allowed_chars"

    allowed_chars = 'abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789'
    from random import choice
    return ''.join([choice(allowed_chars) for i in range(length)])

def clean_string(s):
    from utils.functions import localtime
    import datetime

    if s is None:
        return ""
    elif isinstance(s, (datetime.date, datetime.datetime)):
        return str(localtime(s))
    else:
        try:
            return str(s)
        except UnicodeDecodeError as e:
            return str(s.decode('utf-8'))

def xls_text_value(cell):
    cell_value = cell.value
    if cell.ctype in (2,3) and cell_value == string_to_int(cell_value):
        return unicode(string_to_int(cell_value))
    
    if isinstance(cell_value, basestring):
        return unicode(cell_value.strip())
    
    return unicode(cell_value)


def xls_int_value(val):
    return to_int(val)

def xls_decimal_value(val):
    return to_decimal(val)

def xls_value(val):
    #__PENDIENTE__ 
    #Se va a borrar esta función para usarse en favor
    #de xls_str_value, xls_int_value y xls_decimal_value
    if val == string_to_int(val):
        return unicode(string_to_int(val))
    
    if isinstance(val, basestring):
        return val.strip()
    
    return val

def import_xls(xls_file, max_rows, start_row=1):
    import xlrd

    wb = xlrd.open_workbook(file_contents=xls_file.read(),
                            formatting_info=True)
    
    hoja = wb.sheet_by_index(0)
    cols = []
    for i in xrange(start_row, hoja.nrows):
        row = []
        for a in xrange(max_rows):
            row.append(xls_value(hoja.cell(i, a).value))
        cols.append(row)
        
    return cols

def send_multipart_mail(template_name, email_context, subject, to, bcc,
                        sender=None, send_now=True, fail_silently=False, files=[], headers={}):
    from django.core.mail import EmailMultiAlternatives
    from django.template import loader, Context
    from django.conf import settings
    
    if not sender:
        sender = settings.DEFAULT_FROM_EMAIL
    context = Context(email_context)
    text_part = loader.get_template('%s.txt' % template_name).render(context)
    html_part = loader.get_template('%s.html' % template_name).render(context)
    subject_part = loader.get_template_from_string(subject).render(context)
    if type(to) != list:
        to = [to,]
    msg = EmailMultiAlternatives(subject_part, text_part, sender, to, bcc=bcc, headers=headers)
    for file in files:
        msg.attach_file(file)
    msg.attach_alternative(html_part, "text/html")
    if send_now:
        return msg.send(fail_silently)
    return msg

def save_by_name(kind, name, save=True):
    if not name:
        return None
    try:
        object = kind.objects.get(nombre=name)
    except:
        object = kind(nombre=name)
    finally:
        if save:
            object.save()
        return object

def save_ciudad(name, estado):
    #object = Ciudad.objects.get_or_create(nombre=name, estado=estado)
    #return object[0]
    """
    PENDIENTE ELIMINAR
    """
    return None

def string_to_int(s):
    return to_int(s)

def to_int(s):
    try:
        return int(s) 
    except:
        return 0

def to_decimal(s):
    try:
        s = str(s)
        s = s.replace('$','')
        d = ''.join(s.split(','))        
        return Decimal(d) 
    except:
        return Decimal("0")

def string_to_decimal(s):
    return to_decimal(s)


        
def isdecimal(value):
    try:       
        dec = Decimal(value) 
        return True
    except:
        return False

def get_previous_next_by_fecha(instance):
    anterior = siguiente = None
    try:
        anterior = instance.get_previous_by_fecha()
    except:
        pass
    try:
        siguiente = instance.get_next_by_fecha()
    except:
        pass
    return [anterior, siguiente]
    
def get_last_attr(obj, attrs):
    for attr in attrs:
        obj = getattr(obj, attr)
    return obj

def add_month(year, month):
    month = int(month)
    year = int(year)
    month += 1
    if month == 13:
        month = 1
        year += 1
    return [year, month]

def restar_mes(year, month, n=1):
    month = int(month)
    year = int(year)

    for i in range(0,n):
        month -= 1
        if month == 0:
            month = 12
            year -= 1

    return [year, month]

def cur(value):
    from django.contrib.humanize.templatetags.humanize import intcomma
    from django.template.defaultfilters import floatformat
    return ("$%s" % intcomma(floatformat(value, 2)))

def add_day(d):
    from datetime import timedelta
    import time
    from datetime import date
    ts = time.strptime(unicode(d), "%Y-%m-%d")
    d = date(ts[0], ts[1], ts[2])
    new_date = d + timedelta(days=1)
    return new_date
    

def substract_month(year, month):
    month = int(month)
    year = int(year)
    month -= 1
    if month == 0:
        month = 12
        year -= 1
    return [year, month]

def difference_between_dates(d1, d2, format="%Y-%m-%d"):
    import time
    from datetime import date
    ts1 = time.strptime(unicode(d1), format)
    ts2 = time.strptime(unicode(d2), format)
    
    d1 = date(ts1[0], ts1[1], ts1[2])
    d2 = date(ts2[0], ts2[1], ts2[2])
    
    delta = d1 - d2
    return delta

def year_month_to_desde_hasta(year, month):
    from datetime import date
    import calendar
    if not year and not month:
        desde = date(year=1950, month=1, day=1)
        hasta = date(year=2030, month=12, day=31)

    elif not year:
        desde = date(year=1950, month=1, day=1)
        hasta = date(year=2030, month=12, day=31)

    elif not month:
        year = int(year)
        desde = date(year=year, month=1, day=1)
        hasta = date(year=year, month=12, day=31)

    else:
        year = int(year)
        month = int(month)
        if not month:
            month = 1
        if not year:
            year = 2008
        desde = date(year=year, month=month, day=1)
        hasta = date(year=year, month=month, day=calendar.monthrange(year,month)[1])
    
    return [to_datetime(desde), to_datetime(hasta, max=True)]


def get_month_year(request):
    from datetime import datetime
    month = request.GET.get('month')
    year = request.GET.get('year')
    if month is None or month == "undefined":
        month = timezone.now().month
    if year is None or year == "undefined": 
        year = timezone.now().year
    return [month, year]


def get_first_or_error(klass, msg, last=False):
    all = klass.objects.all()
    if all:
        if last:
            return all.latest()
        return all[0]
    else:
        raise HttpResponseNotFound(msg)

def get_desde_hasta(request):
    import datetime
    desde = request.GET.get('desde')
    hasta = request.GET.get('hasta')
    if desde is None or hasta == "undefined":
        desde = str(datetime.date.today())
    if hasta is None or hasta == "undefined": 
        hasta = str(datetime.date.today())
    
    try:
        if '/' in desde:
            desde = datetime.datetime.strptime(desde, '%d/%m/%y').strftime('%Y-%m-%d')
        if '/' in hasta:
            hasta = datetime.datetime.strptime(hasta, '%d/%m/%y').strftime('%Y-%m-%d')
    except:
        pass
        
    return [desde, hasta]

def get_first_or_None(klass, msg, last=False):
    all = klass.objects.all()
    if all:
        if last:
            return all.latest()
        return all[0]
    else:
        return None

def chain_order(order, reverse, *iterables):
    from itertools import chain
    import operator
    objects = list(chain(*iterables))
    if hasattr(order, '__iter__'):
        objects.sort(key=operator.attrgetter(*order), reverse=reverse)
    else:
        objects.sort(key=operator.attrgetter(order), reverse=reverse)
    return objects
    
def custom_redirect(url_name, *args, **kwargs):
    import urllib
    url = reverse(url_name, args = args)
    params = urllib.urlencode(**kwargs)
    return HttpResponseRedirect(url + "?%s" % params)


class XmlNewObject:
    def __init__(self, *args, **kwargs):
        self.texto = kwargs.get("texto", "")
        self.lista_etiqueta = []
        self.num_elementos = 0

    def set_lista_etiqueta(self, nombre_elemento):
        import re
        self.lista_etiqueta = re.split("<%s" % nombre_elemento, self.texto, flags=re.IGNORECASE)
        self.lista_etiqueta.pop(0)
        self.num_elementos = len(self.lista_etiqueta)

    def find(self, nombre_elemento):
        self.set_lista_etiqueta(nombre_elemento)
        return self.get_elemento(nombre_elemento)

    def find_list(self, nombre_elemento):
        self.set_lista_etiqueta(nombre_elemento)
        lista = []
        ind = 0
        for le in self.lista_etiqueta:
            lista.append(self.get_elemento(nombre_elemento, index=ind))
            ind += 1
        return lista

    def get_elemento(self, nombre, index=0):
        import re
        if self.num_elementos <= 0:
            return self.__class__(texto="")

        if "</%s>" % nombre.lower() in self.texto.lower():
            texto = re.split('</%s>' % nombre, self.lista_etiqueta[index], flags=re.IGNORECASE)[0]
        else:
            texto = self.lista_etiqueta[index].split("/>")[0]
        
        obj = self.__class__()
        obj.texto = texto
        return obj

    def get(self, nombre_attr, default=None):
        import re
        lista_valor = re.split('%s="' % nombre_attr, self.texto, flags=re.IGNORECASE)
        if len(lista_valor) <= 1:
            return default
        valor = lista_valor[1].split('"')[0].strip()
        if not valor:
            return default
        return self.unescape(valor)

    def unescape(self, string):
        return string.replace("&apos;", "'")\
                              .replace('&quot;', '"')\
                              .replace("&lt;", "<")\
                              .replace("&gt;", ">")\
                              .replace("&amp;", "&")

def decode_text_file(txtfile, es_cfdi=True):
    """
    Compatiblidad para no tener que poner .read() a todas partes donde 
    se usaba antes que existiera decode_text
    """
    return decode_text(txtfile.read(), es_cfdi=es_cfdi)

def decode_text(txt, es_cfdi=True):
    """
    Recibe un string lo intenta codificar en utf8 y otros posibles
    encodings, y regresa el texto como unicode.
    """

    if es_cfdi:
        """ 
            SI EL TEXTO ES UN CFDI XML Y EMPIEZA CON UN '?' 
            SE QUITA EL SIGNO PARA QUE SEA UN XML VÁLIDO
        """

        if isinstance(txt, bytes):
            signo = b"?"
        else:
            signo = "?"

        if txt.startswith(signo):
            txt = txt[1:]

    if not isinstance(txt, bytes):
        return txt

    e = None
    for encoding in ["utf-8", "cp1252", "latin-1"]:
        try:
            return txt.decode(encoding)
        except UnicodeDecodeError as exception:
            e = exception
            continue
        else:
            break
    else:
        raise e

def get_xml_object(xml_text):

    """
    El tipo de cambio de la moneda USD lo toma de la bsae de datos central,
    de acuerdo al tipo de cambio del DOF.
    """
    from .classes import XmlNewObject
    from datetime import datetime
    from cfdi.classes import unescape
    from cfdi.functions import remover_addenda
    import sys
    import re

    TIPOS_REGIMEN = (
        #(1, 'Asimilados a salarios (DESCONTINUADO)'),
        (2, 'Sueldos y salarios'),
        (3, 'Jubilados'),
        (4, 'Pensionados'),
        (5, ('Asimilados a salarios, Miembros de las Sociedades ' 
             'Cooperativas de Producción.')),
        (6, ('Asimilados a salarios, Integrantes de Sociedades '
            'y Asociaciones Civiles')),
        (7, ('Asimilados a salarios, Miembros de consejos directivos, '
            'de vigilancia, consultivos, honorarios a administradores, '
            'comisarios y gerentes generales.')),
        (8, 'Asimilados a salarios, Actividad empresarial (comisionistas)'),
        (9, 'Asimilados a salarios, Honorarios asimilados a salarios'),
        (10, 'Asimilados a salarios, Ingresos acciones o títulos valor'),
    )

    RIESGO_PUESTOS = (
        (0, "------"),
        (1, "Clase I"),
        (2, "Clase II"),
        (3, "Clase III"),
        (4, "Clase IV"),
        (5, "Clase V"),
    )
    
    xml_text = xml_text.strip()

    if not xml_text:
        return None

    #if sys.version_info[0] >= 3:
        

    xml_text = decode_text(xml_text)
    
    import codecs
    cond1 = xml_text.encode('utf-8').startswith(codecs.BOM_UTF8 + b'<')
    cond2 = xml_text.encode('utf-8').startswith(b'<')
    
    if not cond1 and not cond2:
        return None


    xml_text = remover_addenda(xml_text)

    soup = XmlNewObject(texto=xml_text)
    xml = Object()
    xml.complemento = None
    version = 3
    reg_entero = re.compile(r'[^\d]+')
    o = soup.find("comprobante")

    #xml.es_v33 = True
    if o.get('version', '') == "3.3":
        xml.es_v33 = True
        xml.formadepago = o.get('metodopago', '')
        xml.metododepago = o.get('formapago', '')        
    else:
        xml.formadepago = o.get('formadepago', '')
        xml.metododepago = o.get('metododepago', '')
        xml.es_v33 = False
        if o.find("regimenfiscal"):
            xml.regimen = o.find("regimenfiscal").get("regimen")

    xml.forma_pago_at =  1 if xml.formadepago == "PPD" else 0
    xml.version = version
    xml.total = o.get('total', '')
    xml.sello = o.get('sello', '')
    xml.noaprobacion = o.get('noaprobacion', '')
    xml.anoaprobacion = o.get('anoaprobacion', '')
    xml.nocertificado = o.get('nocertificado', '')
    xml.folio = reg_entero.sub('', o.get('folio', '')[-9:])
    xml.serie = o.get('serie', '')
    xml.fecha_str = o.get('fecha', '')
    xml.fecha_dt = get_fecha_cfdi(xml.fecha_str)

    #__PENDIENTE__ eliminar para evitar confusiones 
    #con la fecha en formato texto o datetime
    xml.fecha = xml.fecha_str

    xml.subtotal = o.get('subtotal', '')
    xml.descuento = o.get('descuento', '')
    
    xml.numctapago = o.get('numctapago', '')
    xml.condicionesdepago = o.get('condicionesdepago', '')
    xml.moneda = o.get('moneda', '')
    xml.tipocambio = o.get('tipocambio', '1')

    xml.tipodecomprobante = o.get('tipodecomprobante', '')
    xml.lugarexpedicion = o.get('lugarexpedicion', '')


    ######## EMISOR ########
    xml.emisor = Object()
    xml.emisor.rfc = o.find("emisor").get("rfc").strip()
    xml.emisor.nombre = unescape(o.find("emisor").get("nombre"))
    if o.get('version', '') == "3.3":
        xml.regimen = o.find("emisor").get("regimenfiscal", '')
    
    xml.emisor.domiciliofiscal = Object()
    xml.emisor.domiciliofiscal.calle = o.find("emisor").find("domiciliofiscal").get("calle", '')[:500]
    xml.emisor.domiciliofiscal.noexterior = o.find("emisor").find("domiciliofiscal").get("noexterior", '')[:100]
    xml.emisor.domiciliofiscal.nointerior = o.find("emisor").find("domiciliofiscal").get("nointerior", '')[:100]
    xml.emisor.domiciliofiscal.colonia = o.find("emisor").find("domiciliofiscal").get("colonia", '')[:100]
    xml.emisor.domiciliofiscal.municipio = o.find("emisor").find("domiciliofiscal").get("municipio", '')[:255]
    xml.emisor.domiciliofiscal.localidad = o.find("emisor").find("domiciliofiscal").get("localidad", '')[:255]
    xml.emisor.domiciliofiscal.estado = o.find("emisor").find("domiciliofiscal").get("estado", '')[:255]
    xml.emisor.domiciliofiscal.pais = o.find("emisor").find("domiciliofiscal").get("pais", '')[:100]
    xml.emisor.domiciliofiscal.codigopostal = o.find("emisor").find("domiciliofiscal").get("codigopostal", '')[:6]
    ########

    ######## RECEPTOR ########
    xml.receptor = Object()
    xml.receptor.rfc = o.find("receptor").get("rfc").strip()
    xml.receptor.nombre = unescape(o.find("receptor").get("nombre"))
    xml.receptor.regimen = o.find("receptor").get("regimen") or o.find("receptor").get("regimenfiscal")
    xml.receptor.registro_patronal = o.find("receptor").get("registropatronal")
    xml.receptor.usocfdi = o.find("receptor").get("usocfdi")

    xml.receptor.domicilio = Object()
    xml.receptor.domicilio.calle = o.find("receptor").find("domicilio").get("calle", '')
    xml.receptor.domicilio.noexterior = o.find("receptor").find("domicilio").get("noexterior", '')
    xml.receptor.domicilio.nointerior = o.find("receptor").find("domicilio").get("nointerior", '')
    xml.receptor.domicilio.colonia = o.find("receptor").find("domicilio").get("colonia", '')
    xml.receptor.domicilio.municipio = o.find("receptor").find("domicilio").get("municipio", '')
    xml.receptor.domicilio.localidad = o.find("receptor").find("domicilio").get("localidad", '')
    xml.receptor.domicilio.estado = o.find("receptor").find("domicilio").get("estado", '')
    xml.receptor.domicilio.pais = o.find("receptor").find("domicilio").get("pais", '')
    xml.receptor.domicilio.codigopostal = o.find("receptor").find("domicilio").get("codigopostal", '')[0:5]
    direccion_completa = xml.receptor.domicilio.calle

    if xml.receptor.domicilio.noexterior:
        direccion_completa = "%s #%s" % (direccion_completa, xml.receptor.domicilio.noexterior)

    if  xml.receptor.domicilio.colonia:
        direccion_completa = "%s Col: %s" % (direccion_completa, xml.receptor.domicilio.colonia)

    if xml.receptor.domicilio.codigopostal:
        direccion_completa = "%s CP: %s" % (direccion_completa, xml.receptor.domicilio.codigopostal)            

    direccion_completa = "%s %s %s" % (direccion_completa, xml.receptor.domicilio.municipio, xml.receptor.domicilio.estado)            

    xml.receptor.domicilio.completa = direccion_completa
    ########
    xml.iva = 0
    xml.importe_tasa_cero = 0
    xml.importe_tasa_general = 0
    xml.importe_tasa_frontera = 0
    xml.importe_exento = 0
    xml.total_tasa_cero = 0
    xml.total_tasa_general = 0
    xml.total_tasa_frontera = 0
    xml.total_exento = 0
    xml.tasa_cero = False
    xml.ieps = 0
    xml.retencion_isr = 0
    xml.retencion_iva = 0
    total_traslados = 0 
    total_retenciones = 0

    conceptos = o.find("conceptos").find_list("concepto")
    xml.conceptos = []

    importe_tasa_frontera = 0
    total_impuestos_tasa_fronetra = 0
    importe_tasa_general = 0
    total_impuestos_tasa_general = 0

    for c in conceptos:
        tasa_iva_concepto = ""
        tasa_ieps_concepto = ""
        total_iva = 0
        total_ieps = 0
        base_iva = ""
        total_base_iva_concepto = 0
        base_ieps = ""
        tipo_factor_ieps = "tasa"
        descuento = to_decimal(c.get("descuento"))
        total_traslado_concepto = 0
        importe_tasa_frontera_concepto = 0
        importe_tasa_general_concepto = 0
        if xml.es_v33:
            importe_concepto = to_decimal(c.get("importe"))
            for tras in c.find_list("traslado"):
                tasa_iva = ""
                tasa_ieps = ""
                importe_ieps = 0
                importe_traspaso = to_decimal(tras.get("importe"))
                base_traslado = to_decimal(tras.get("base"))
                if to_decimal(tras.get("base")):
                    if tras.get("impuesto").upper() == "002":
                        tasa_iva = tras.get("tasaocuota")
                        tasa_iva_concepto = tasa_iva
                        total_iva += importe_traspaso
                        if tras.get("tipofactor") == "exento":
                            tasa_iva = "exento"
                        
                    elif tras.get("impuesto").upper() == "003":
                        tasa_ieps = tras.get("tasaocuota")
                        tasa_ieps_concepto = tasa_ieps
                        total_ieps += to_decimal(tras.get("importe"))
                        importe_ieps = to_decimal(tras.get("importe"))
                        tipo_factor_ieps = tras.get("tipofactor").lower()
                    
                    total_traslado_concepto += importe_traspaso

            es_frontera = to_decimal(tasa_iva_concepto) == to_decimal("0.08")
            es_combustible = (
                c.get("claveprodserv", "") == "15101506" and 
                not to_decimal(total_ieps)
            )
            es_tasa_cero = (
                tasa_iva_concepto and
                not to_decimal(tasa_iva_concepto) 
                and tasa_iva_concepto != "exento"
            )
            if tasa_iva_concepto:
                #SI ES COMBUSTIBLE, TOMA TODO EL IMPORTE DEL 
                #CONCEPTO PARA EL TOTAL DE TASA GENERAL/FRONTERA
                if es_combustible:
                    importe_tasa = importe_concepto
                else:
                    importe_tasa = (
                        importe_concepto -
                        descuento
                    )

                if to_decimal(tasa_iva_concepto):
                    if es_frontera:
                        importe_tasa_frontera += importe_tasa
                        total_impuestos_tasa_fronetra += total_traslado_concepto
                        if not es_combustible:
                            xml.importe_tasa_frontera += importe_tasa
                    else:

                        importe_tasa_general += importe_tasa
                        total_impuestos_tasa_general += total_traslado_concepto
                        if not es_combustible:
                            xml.importe_tasa_general += importe_tasa

                elif es_tasa_cero:
                    xml.importe_tasa_cero += importe_tasa
                    xml.total_tasa_cero += (
                        importe_tasa + 
                        total_traslado_concepto 
                    )

            for t in c.find_list("retencion"):
                if t.get("impuesto").upper() == "002":
                    xml.retencion_iva += to_decimal(t.get("importe"))
                elif t.get("impuesto").upper() == "001":
                    xml.retencion_isr += to_decimal(t.get("importe"))

            xml.iva += total_iva
            xml.ieps += total_ieps


        else:
            base_iva = to_decimal(c.get("importe"))
            tasa_iva = to_decimal("0.16")

        xml.conceptos.append({
            "cantidad":c.get("cantidad"),
            "claveprodserv":c.get("claveprodserv"),
            "claveunidad":c.get("claveunidad"),
            "descripcion":unescape(c.get("descripcion")),
            "importe":c.get("importe"),
            "noidentificacion":unescape(c.get("noidentificacion", "").strip())[:100],
            "unidad":(c.get("unidad") or c.get("claveunidad")),#version 3.3,
            "valorunitario":c.get("valorunitario"),
            "tasa_iva":tasa_iva_concepto,
            "total_iva":total_iva,
            "tasa_ieps":tasa_ieps_concepto,
            "total_ieps":total_ieps,
            "base_iva":base_iva,
            "base_ieps":base_ieps,
            "tipo_factor_ieps":tipo_factor_ieps,
            "descuento":descuento,
        })

    xml.total_tasa_frontera += (
        to_precision_decimales(importe_tasa_frontera, 2) + 
        to_precision_decimales(total_impuestos_tasa_fronetra, 2)
    )

    xml.total_tasa_general += (
        to_precision_decimales(importe_tasa_general, 2) + 
        to_precision_decimales(total_impuestos_tasa_general, 2)
    )


    if not xml.es_v33:
        for t in o.find("impuestos").find("traslados").find_list("traslado"):
            importe_traslado = to_decimal(t.get("importe"))
            if t.get("impuesto") == "IVA":
                xml.iva += importe_traslado
            elif t.get("impuesto") == "IEPS":
                xml.ieps += importe_traslado
    
    pago = o.find("pagos", "pago10")
    xml.es_comprobante_pago = False
    if pago.exists:
        xml.es_comprobante_pago = True
        xml.abono_fecha_pago = pago.get("fechapago")
        xml.abono_forma_pago = pago.get("formadepagop")
        xml.abono_moneda = pago.get("monedap")
        xml.abono_monto = pago.get("monto")
        xml.abono_num_operacion = pago.get("numoperacion")

        xml.banco_ordenante = pago.get("nombancoordext")
        xml.cuenta_ordenante = pago.get("ctaordenante")
        xml.rfc_cuenta_ordenante = pago.get("rfcemisorctaord")
        xml.rfc_cuenta_beneficiario = pago.get("rfcemisorctaben")
        xml.cuenta_beneficiario = pago.get("ctabeneficiario")
                
        xml.pagos = []
        for p in pago.find_list("doctorelacionado", "pago10"):  
            xml.pagos.append({
                "imp_pagado":p.get("imppagado"),
                "imp_saldo_ant":p.get("impsaldoant"),
                "imp_saldo_insoluto":p.get("impsaldoinsoluto"),
                "metodo_pago":p.get("metododepagodr"),
                "moneda":p.get("monedadr"),
                "num_parcialidad":p.get("numparcialidad"),
                "folio":p.get("folio"),
                "serie":p.get("serie"),
                "iddocumento":p.get("iddocumento"),
            })

    xml.impuestos = Object()
    xml.impuestos.totalimpuestostrasladados = o.find("impuestos").get_num("totalimpuestostrasladados")
    
    xml.impuestos.totalImpuestosRetenidos = o.find("impuestos").get_num("totalimpuestosretenidos")
    impuestoslocales = o.find_list("impuestoslocales", "implocal")
    xml.impuestos_locales = []
    xml.total_impestos_locales = 0
    if impuestoslocales:
        for il in impuestoslocales:
            xml.impuestos_locales.append({
                "nombre":il.get("implocretenido"),
                "importe":il.get("importe"),
                "tasa":il.get("tasaderetencion"),
            })

            xml.total_impestos_locales += to_decimal(il.get("importe"))


    if not xml.iva:
        xml.tasa_cero = True

    xml.importe_tasa_general = to_precision_decimales(xml.importe_tasa_general)
    xml.importe_tasa_cero = to_precision_decimales(xml.importe_tasa_cero)
    xml.total_tasa_general = to_precision_decimales(xml.total_tasa_general)
    xml.total_tasa_cero = (
        to_precision_decimales(xml.total_tasa_cero) + 
        xml.total_impestos_locales
    )
    xml.total_tasa_frontera = to_precision_decimales(xml.total_tasa_frontera)

    xml.importe_exento = (
        to_decimal(xml.subtotal) - 
        to_decimal(xml.descuento) - 
        xml.importe_tasa_general - 
        xml.importe_tasa_frontera - 
        xml.importe_tasa_cero
    )
    
    xml.total_exento = (
        to_decimal(xml.total) -
        xml.total_tasa_general - 
        xml.total_tasa_frontera - 
        xml.total_tasa_cero
    )

    if xml.total_tasa_general or xml.total_tasa_frontera:
        """
            SI HAY IMPUESTOS RETENIDOS, SE SUMA AL EXENTO POR QUE 
            SE LE RESTA ARRIBA (TOTAL_TASA_GENERAL O TOTAL_TASA_FRONTERA)
        """
        xml.total_exento += xml.impuestos.totalImpuestosRetenidos

    if version == 3:
        xml.complemento = Object() 
        xml.complemento.timbrefiscaldigital = Object()
        complemento = o.find("complemento")

        for version_ecc in ["ecc11", "ecc12"]:

            estado_cuenta_combustible = XmlNewObject(texto=xml_text).find("EstadoDeCuentaCombustible", version_ecc)
            conceptos_combustible = []
            for concepto in estado_cuenta_combustible.find_list("ConceptoEstadoDeCuentaCombustible", version_ecc):
                iva = concepto.find("Traslados", version_ecc).find_list("Traslado", version_ecc)[0].get("Importe")
                conceptos_combustible.append({
                    "fecha":concepto.get("Fecha"),
                    "rfc":concepto.get("Rfc"),
                    "importe":to_decimal(concepto.get("Importe")),
                    "iva":to_decimal(iva),
                })
        

        xml.complemento.conceptos_combustible = conceptos_combustible
        xml.complemento.timbrefiscaldigital.uuid = ""
        if complemento.exists:
            tfd = complemento.find("timbrefiscaldigital", "tfd")
            xml.complemento.timbrefiscaldigital.version = tfd.get("version")
            xml.complemento.timbrefiscaldigital.uuid = tfd.get("uuid")
            xml.complemento.timbrefiscaldigital.fechatimbrado_str = tfd.get("fechatimbrado")
            xml.complemento.timbrefiscaldigital.fechatimbrado_dt = get_fecha_cfdi(xml.complemento.timbrefiscaldigital.fechatimbrado_str)
            xml.complemento.timbrefiscaldigital.sellocfd = tfd.get("sellocfd")
            xml.complemento.timbrefiscaldigital.nocertificadosat = tfd.get("nocertificadosat")
            xml.complemento.timbrefiscaldigital.sellosat = tfd.get("sellosat")
            xml.complemento.timbrefiscaldigital.rfcprovcertif = tfd.get('rfcprovcertif', '')

            if xml.complemento.timbrefiscaldigital.uuid:
                xml.complemento.timbrefiscaldigital.cadenaoriginal = "||1.0|%s|%s|%s|%s||" % (
                   xml.complemento.timbrefiscaldigital.uuid,
                   xml.complemento.timbrefiscaldigital.fechatimbrado_str,
                   xml.complemento.timbrefiscaldigital.sellocfd,
                   xml.complemento.timbrefiscaldigital.nocertificadosat,
                )
            else:
                xml.complemento.timbrefiscaldigital.cadenaoriginal = ""

            nomina_xml = complemento.find("nomina", "nomina12")
            if not nomina_xml.exists:
                nomina_xml = complemento.find("nomina", "nomina")
                
            if nomina_xml.exists:
                xml.complemento.nomina = Object()
                nomina_version =  nomina_xml.get("version")
                
                receptor_nomina = nomina_xml.find("receptor")
                xml.complemento.nomina.numero_empleado = receptor_nomina.get("numempleado", "")
                xml.complemento.nomina.curp = receptor_nomina.get("curp", "")
                xml.complemento.nomina.nss = receptor_nomina.get("numseguridadsocial", "")
                xml.complemento.nomina.tipo_regimen = to_int(receptor_nomina.get("tiporegimen", ""))
                xml.complemento.nomina.get_tipo_regimen_display = dict(TIPOS_REGIMEN).get(string_to_int(xml.complemento.nomina.tipo_regimen), "")
                xml.complemento.nomina.fecha_inicio = nomina_xml.get("fechainicialpago", "")
                xml.complemento.nomina.fecha_fin = nomina_xml.get("fechafinalpago", "")
                xml.complemento.nomina.fecha_pago = nomina_xml.get("fechapago", "")
                xml.complemento.nomina.dias = nomina_xml.get("numdiaspagados", "")
                xml.complemento.nomina.departamento = receptor_nomina.get("departamento", "")
                xml.complemento.nomina.puesto = receptor_nomina.get("puesto", "")
                xml.complemento.nomina.tipo_contrato = receptor_nomina.get("tipocontrato", "")
                xml.complemento.nomina.tipo_jornada = receptor_nomina.get("tipojornada", "")
                xml.complemento.nomina.riesgo_puesto = receptor_nomina.get("riesgopuesto", "")
                xml.complemento.nomina.get_riesgo_puesto_display = RIESGO_PUESTOS[string_to_int(xml.complemento.nomina.riesgo_puesto)][1] if to_int(xml.complemento.nomina.riesgo_puesto) else None
                xml.complemento.nomina.sdi = receptor_nomina.get("salariodiariointegrado", "")
                xml.complemento.nomina.sbc = receptor_nomina.get("salariobasecotapor", "")
                xml.complemento.nomina.fecha_iniciorel_laboral = receptor_nomina.get("fechainiciorellaboral", "")
                xml.complemento.nomina.antiguedad = receptor_nomina.get("Antig\xfcedad", "")
                xml.complemento.nomina.clabe = receptor_nomina.get("clabe", "")
                xml.complemento.nomina.periodicidadpago = receptor_nomina.get("periodicidadpago", "")
                xml.complemento.nomina.claveentfed = receptor_nomina.get("claveentfed", "")
                xml.complemento.nomina.registro_patronal = nomina_xml.find("emisor").get("registropatronal", "")
                esncf = nomina_xml.find("emisor").get("entidadsncf", {})
                xml.complemento.nomina.origen_recurso = esncf.get("origenrecurso", "")
                xml.complemento.nomina.monto_recurso_propio = esncf.get("montorecursopropio", "")
                xml.complemento.nomina.tipo_nomina = nomina_xml.get("tiponomina", "")

                percepciones = nomina_xml.find("percepciones").find_list("percepcion")
                xml.complemento.nomina.percepciones = []
                xml.complemento.nomina.total_percepciones = 0
                if percepciones:
                    for p in percepciones:
                        xml.complemento.nomina.percepciones.append({
                            "clave":p.get("clave"),
                            "concepto":p.get("concepto"),
                            "importegravado":p.get("importegravado"),
                            "importeexento":p.get("importeexento"),
                            "tipo":p.get("tipopercepcion"),
                        })
                        xml.complemento.nomina.total_percepciones += (string_to_decimal(p.get("importegravado"))+ string_to_decimal(p.get("importeexento")))

                
                otrospagos = nomina_xml.find("otrospagos").find_list("otropago")
                xml.complemento.nomina.otrospagos = []
                xml.complemento.nomina.total_otrospagos = 0
                if otrospagos:
                    for p in otrospagos:

                        xml.complemento.nomina.subsidio = 0
                        subsidio = p.find("subsidioalempleo")
                        if subsidio.exists:
                            xml.complemento.nomina.subsidio = to_decimal(subsidio.get("subsidiocausado"))

                        xml.complemento.nomina.otrospagos.append({
                            "clave":p.get("clave"),
                            "concepto":p.get("concepto"),
                            "importe":p.get("importe"),
                            "tipo":p.get("tipootropago")
                        })
                        xml.complemento.nomina.total_otrospagos += string_to_decimal(p.get("importe"))

                deducciones = nomina_xml.find("deducciones").find_list("deduccion")
                xml.complemento.nomina.deducciones = []
                xml.complemento.nomina.total_deducciones = 0
                if deducciones:
                    for d in deducciones:
                        xml.complemento.nomina.deducciones.append({
                            "clave":d.get("clave"),
                            "concepto":d.get("concepto"),
                            "importe":d.get("importe"),
                            "tipo":d.get("tipodeduccion")
                        })
                        xml.complemento.nomina.total_deducciones += string_to_decimal(d.get("importe"))
                       
                horasextra = nomina_xml.find("horasextra").find_list("horaextra")
                xml.complemento.nomina.horasextra = []
                
                if horasextra:
                    for he in horasextra:
                        xml.complemento.nomina.horasextra.append(he)

                incapacidades = nomina_xml.find("incapacidades").find_list("incapacidad")
                xml.complemento.nomina.incapacidades = []
                if incapacidades:
                    for i in incapacidades:
                        xml.complemento.nomina.incapacidades.append(i)

                xml.complemento.nomina.total_percibido = to_decimal(xml.total)
                
            else:
                xml.complemento.nomina = None

            ine = complemento.find("ine", "ine")
            if ine.exists:
                xml.complemento.ine = Object()
                xml.complemento.ine.tipoproceso = ine.get("tipoproceso", "")
                xml.complemento.ine.tipocomite = ine.get("tipocomite", "")
                if ine.find("entidad"):
                    xml.complemento.ine.claveentidad = ine.find("entidad").get("claveentidad", "")
                    if ine.find("entidad").find("contabilidad"):
                        xml.complemento.ine.idcontabilidad = ine.find("entidad").find("contabilidad").get("idcontabilidad", "")

            iedu = complemento.find("insteducativas", "iedu")
            if iedu.exists:
                xml.complemento.iedu = Object()
                xml.complemento.version =  iedu.get("version")
                xml.complemento.autrvoe = iedu.get("autrvoe")
                xml.complemento.nombre_alumno = iedu.get("nombrealumno")
                xml.complemento.curp = iedu.get("curp")
                xml.complemento.nivel_educativo = iedu.get("niveleducativo")
                xml.complemento.rfc_pago = iedu.get("rfcpago")


    xml.es_dolares = False
    xml.es_euros = False
    xml.importe = to_decimal(xml.total) - to_decimal(xml.iva) - to_decimal(xml.ieps) + xml.impuestos.totalImpuestosRetenidos
    if not xml.moneda.upper() in ["MXN", "MN", "PESOS", "MX"]:
        if "USD" in xml.moneda.upper() or xml.moneda.upper().startswith("D"):
            xml.es_dolares = True
        elif "EUR" in xml.moneda.upper() or xml.moneda.upper().startswith("E"):
            xml.es_euros = True
        else:
            if string_to_decimal(xml.tipocambio) > 1:
                xml.es_dolares = True

    return xml

def get_xml_value(xml_content, field):
    try:
        return xml_content.split('%s="' % field)[1].split('"')[0].upper().strip()
    except:
        return ''


    
def ultimo_dia_mes(year, month):
    from datetime import date, timedelta
    next_year, next_month = add_month(year, month)
    fecha = date(year=next_year, month=next_month, day=1) - timedelta(days=1)
    return fecha
    
def get_pagina(request, objects,  page_size=25):
    from django.core.paginator import Paginator, InvalidPage, EmptyPage
    
    paginator = Paginator(objects, page_size)
    try:
        num_pagina = int(request.GET.get('pag', '1'))
    except ValueError:
        num_pagina = 1
    try:
        pagina = paginator.page(num_pagina)
    except (EmptyPage, InvalidPage):
        pagina = paginator.page(paginator.num_pages)
    
    return pagina
    

def to_precision_decimales(valor_decimal, precision=2):
    from decimal import Decimal, ROUND_HALF_UP

    if not valor_decimal:
        return Decimal("0.00")

    return Decimal("%s" % valor_decimal).quantize(
        Decimal("0.%0*d" % (precision, 1)), 
        ROUND_HALF_UP
    )

def delete_objects(klass):
    for o in klass.objects.all():
        o.delete()
    
def seconds_to_human(secs):
    hours = 0
    minutes = 0
    while(secs > 3600):
        hours += 1
        secs -= 3600
    
    while(secs > 60):
        minutes += 1
        secs -= 60
        
    return [hours, minutes, int(secs)]
    
def replace_unicode(string):
    if type(string) == type(u""): #En caso de ser unicode
        string = string.replace(u"á", "a")
        string = string.replace(u"é", "e")
        string = string.replace(u"í", "i")
        string = string.replace(u"ó", "o")
        string = string.replace(u"ú", "u")
        string = string.replace(u"ñ", "n")
        string = string.replace(u"ü", "u")
        string = string.replace(u"Á", "A")
        string = string.replace(u"É", "E")
        string = string.replace(u"Í", "I")
        string = string.replace(u"Ó", "O")
        string = string.replace(u"Ú", "U")
        string = string.replace(u"Ñ", "N")
        string = string.replace(u"Ü", "U")
        string = string.replace(u"Ü", "U")
        string = string.replace(u"´", "'")
        string = string.replace(u"°", "o")
        
    
    elif type(string) == type(""): #En caso de ser str
        string = string.replace("á", "a")
        string = string.replace("é", "e")
        string = string.replace("í", "i")
        string = string.replace("ó", "o")
        string = string.replace("ú", "u")
        string = string.replace("ñ", "n")
        string = string.replace("ü", "u")
        string = string.replace("Á", "A")
        string = string.replace("É", "E")
        string = string.replace("Í", "I")
        string = string.replace("Ó", "O")
        string = string.replace("Ú", "U")
        string = string.replace("Ñ", "N")
        string = string.replace("Ü", "U")
        string = string.replace("´", "'")
        string = string.replace("°", "o")
        
    return string

def html_escape(string):
    string = string.replace(u"á", "&aacute;")
    string = string.replace(u"é", "&eacute;")
    string = string.replace(u"í", "&iacute;")
    string = string.replace(u"ó", "&oacute;")
    string = string.replace(u"ú", "&uacute;")
    string = string.replace(u"ñ", "&ntilde;")
    string = string.replace(u"ü", "&uuml;")
    string = string.replace(u"Á", "&Aacute;")
    string = string.replace(u"É", "&Eacute;")
    string = string.replace(u"Í", "&Iacute;")
    string = string.replace(u"Ó", "&Oacute;")
    string = string.replace(u"Ú", "&Uacute;")
    string = string.replace(u"Ñ", "&Ntilde;")
    string = string.replace(u"Ü", "&Uuml;")
    string = string.replace(u"°", "&deg;")
    string = string.replace(u"\n", "<br />")
    return string

def render_to_pdf(template_src, context_dict, to_file=False, landscape=False, debug=False):
    from django.template.loader import get_template
    from django.template import Context
    from subprocess import Popen, call, PIPE
    from datetime import datetime
    template = get_template(template_src)
    context = Context(context_dict)
    html  = template.render(context)
    
    from django.conf import settings
    
    
    if debug:
        return HttpResponse(html, mimetype="text/html")
        

    input_html = '%s/afc_input_%s.html' % (settings.TMP_DIR, timezone.now().microsecond)
    write_text_file(input_html, html.encode("utf8"))


    #args = ["/usr/bin/wkhtmltopdf.sh"]
    args = [settings.WKHTMLTOPDF, "-q"]

    args.append(input_html)
    
    
    
    if to_file:
        args.append(to_file)
    else:
        args.append("-")
        
    popen = Popen(args, stdout=PIPE, stderr=PIPE)
    
    try:
        body_contents = popen.stdout.read()
        mimetype='application/pdf'
        
    except Exception as e:
        body_contents = "Hubo un error al generar el documento: %s" % e
        mimetype='plain/html'
        
    finally:
        popen.terminate()
        popen.wait()
    
    return HttpResponse(body_contents, mimetype=mimetype)

def xls_to_response(xls, fname):
    from django.http import HttpResponseRedirect, HttpResponse
    response = HttpResponse(content_type="application/ms-excel")
    response['Content-Disposition'] = 'attachment; filename=%s' % fname
    xls.save(response)
    return response
    

def first_object_or_None(klass, *args, **kwargs):

    queryset = klass.objects.filter(*args, **kwargs)
    if not queryset.exists():
        return None
    return queryset[0]


def getTagXml(xml, name):
    try:
        return xml.split("<%s>" % name)[1].split("</%s>" % name)[0]
    except IndexError:
        return ""

def json_response(something, allow_origin=False, status=200):
    import json
    from django.http import HttpResponse
    response = HttpResponse(
        json.dumps(something),
        content_type = 'application/json; charset=utf8',
        status = status
    )
    response['Cache-Control'] = 'no-cache'
    if allow_origin:
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS, FETCH"
        response["Access-Control-Max-Age"] = "1000"
        response["Access-Control-Allow-Headers"] = "*"

    return response


def xlsx_to_response(wb, fname):
    from django.http import HttpResponse
    wb.wb.close()
    wb.output_xlsx.seek(0)

    if fname.endswith(".xls"):
        fname = fname[:-4]
    response = HttpResponse(wb.output_xlsx.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response['Content-Disposition'] = "attachment; filename=%s.xlsx" % (fname)
    return response

def get_ip_address(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def parse_date(text, *formats):
    from datetime import datetime
    for fmt in formats:
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            pass
    raise ValueError('No valid date format found')

def es_imagen(archivo):
    from PIL import Image
    if archivo:
        try:
            trial_image = Image.open(archivo)
            return True
        except IOError:
            pass
    return False

def get_instance_or_func(k):
    if callable(k):
        return k()
    else:
        return k

def validar_clabe():
    pass

def reemplazar_acentos(texto):
    return texto.replace(u"Á", u"A")\
                .replace(u"É", u"E")\
                .replace(u"Í", u"I")\
                .replace(u"Ó", u"O")\
                .replace(u"Ú", u"U")\
                .replace(u"á", u"a")\
                .replace(u"é", u"e")\
                .replace(u"í", u"i")\
                .replace(u"ó", u"o")\
                .replace(u"ú", u"u")\

def get_entidades_choices(i):
    from .models import ENTIDADES
    entidades = []
    for e in ENTIDADES:
        entidades.append((e[0], e[i-1]))

    return entidades

def get_estado(id, short=False, full_result=False):
    from .models import ENTIDADES
    result = None
    for e in ENTIDADES:
        if id == e[0]:
            if not full_result:
                result = e[1] if short else e[2]
            else:
                result = e
            break
            
    return result

def get_object_or_None(klass, *args, **kwargs):
    """
    Uses get() to return an object or None if the object does not exist.

    klass may be a Model, Manager, or QuerySet object. All other passed
    arguments and keyword arguments are used in the get() query.

    Note: Like with get(), a MultipleObjectsReturned will be raised if more than one
    object is found.
    """
    queryset = _get_queryset(klass)
    try:
        return queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist:
        return None



def get_config(key, default):
    """
    Get settings from django.conf if exists,
    return default value otherwise

    example:

    ADMIN_EMAIL = get_config('ADMIN_EMAIL', 'default@email.com')
    """
    return getattr(settings, key, default)

def merge_dicts(x, y):
    z = x.copy()   # start with x's keys and values
    z.update(y)    # modifies z with y's keys and values & returns None
    return z


def add_months(fecha, n=1, less=False, day=None):
    from datetime import datetime
    month = fecha.month
    year = fecha.year
    
    if not day:
        day = fecha.day

    for i in range(n):
        if less:
            month -= 1
            if month == 0:
                month = 12
                year -= 1 
        else:
            month += 1
            if month == 13:
                month = 1
                year += 1

    try:
        fecha = datetime(year, month, day)
    except ValueError:
        fecha = datetime.combine(ultimo_dia_mes(year, month), datetime.min.time())
    return to_datetime(fecha)

def send_to_sentry(e, data={}, tags={}):
    try:
        return client.captureMessage(e, extra=data, tags=tags)
    except Exception as e:
        pass


def add_months(fecha, n=1, less=False, day=None):

    from datetime import datetime
    month = fecha.month
    year = fecha.year
    from utils.functions import ultimo_dia_mes
    
    if not day:
        day = fecha.day

    for i in range(n):
        if less:
            month -= 1
            if month == 0:
                month = 12
                year -= 1 
        else:
            month += 1
            if month == 13:
                month = 1
                year += 1

    try:
        fecha = datetime(year, month, day)
    except ValueError:
        fecha = datetime.combine(ultimo_dia_mes(year, month), datetime.min.time())
    return to_datetime(fecha)

def get_wb_xlsx(output=None):
    """

    """
    import xlsxwriter
    from io import BytesIO
    output_xlsx = BytesIO() if not output else output
    class WbXlsx:
        pass
    wb = WbXlsx()
    wb.wb = xlsxwriter.Workbook(output_xlsx, { 'constant_memory': True })
    wb.XLWT_TITULO = wb.wb.add_format({'bold': True})
    wb.XLWT_TITULO_CENTER = wb.wb.add_format({'bold': True, "align":"center", })
    wb.XLWT_NUM = wb.wb.add_format({'num_format': '#,##0.00'})
    wb.XLWT_PORCIENTO = wb.wb.add_format({'num_format': '0.00%'})
    wb.DATE_FX = wb.wb.add_format({'num_format': 'DD/MM/YY'})
    wb.XLWT_NUM_TITLE = wb.wb.add_format({"bold":True, 'num_format': '#,##0.00',})
    wb.XLWT_NUM_TITLE_RED = wb.wb.add_format({"bold":True, 'num_format': '#,##0.00', 'font_color':'red'})
    wb.XLWT_NUM_RED = wb.wb.add_format({'num_format': '#,##0.00', 'font_color':'red'})


    wb.output_xlsx = output_xlsx
    return wb

def admintotal_key_valida(cadena, cadena_encriptada):
    import hashlib
    if cadena_encriptada == hashlib.sha1(cadena.encode("utf-8")).hexdigest():
        return True
    return False


def aggregate_sum(qs, field, td=True):
    if not td:
        return to_int(qs.aggregate(Sum(field))["%s__sum" % field])
    return to_decimal(qs.aggregate(Sum(field))["%s__sum" % field])

def get_url_solicitar_firma_pdf(pdf_url):
    from firmamex import SignmageServices
    s =  SignmageServices(settings.FIRMAMEX_WEBID, settings.FIRMAMEX_APIKEY)
    
    if pdf_url.startswith("/"):
        pdf_url = settings.ROOT_URL + pdf_url 

    return s.request({"url_doc":pdf_url})


def hash_post(dic):
    """
    Función para validar requests entre servicios de admintotal
    """
    import collections, hashlib
    from django.conf import settings
    text = ""
    for item, value in collections.OrderedDict(sorted(dic.items())).items():
        if not value is None: 
            text += "%s" % value

    text += settings.ADMINTOTAL_KEY
    dic["cadenaEncriptada"] = hashlib.sha1(text.encode("utf-8")).hexdigest()
    return dic

def hash_valido(post):
    """
    Función para validar requests entre servicios de admintotal
    """
    import collections, hashlib
    from django.conf import settings
    post = dict(post)
    try:
        cadena_encriptada = post.pop("cadenaEncriptada")[0]
    except:
        return False
    post_text = ""

    for item, lista_valores in collections.OrderedDict(sorted(post.items())).items():
        for value in lista_valores:
            post_text += value
    post_text += settings.ADMINTOTAL_KEY
    return cadena_encriptada == hashlib.sha1(post_text.encode("utf-8")).hexdigest()

def paginar(objects, limit=20, page=None):
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    
    paginator = Paginator(objects, limit)
    try:
        objects = paginator.page(page)
    except PageNotAnInteger:
        objects = paginator.page(1)
    except EmptyPage:
        objects = paginator.page(paginator.num_pages)

    result_objs = objects.object_list
    previous_page_number = None
    next_page_number = None

    if objects.has_previous():
        previous_page_number = objects.previous_page_number()

    if objects.has_next():
        next_page_number = objects.next_page_number()

    meta = {
        'number': objects.number,
        'has_previous':objects.has_previous(),
        'has_next':objects.has_next(),
        'page_range':objects.paginator.page_range,
        'previous_page_number': previous_page_number,
        'next_page_number': next_page_number,
        'paginator': {
            'num_pages': objects.paginator.num_pages,
            'count': objects.paginator.count
        }
    }
    return meta, result_objs

def get_files_from_zip(archivo, ext=None):
    if not archivo:
        return []

    from zipfile import ZipFile
    archivoZip = ZipFile(archivo.file, "r")
    archivos = []
    for file_name in archivoZip.namelist():
        if ext and not file_name.lower().endswith(".%s" % ext.lower()):
            continue
        archivos.append({
            "content":archivoZip.open(file_name).read(),
            "name":file_name,
        })

    return archivos

def sustituir_instance(instance_e, instance_s, excepciones=[]):

    for r in instance_e.__class__._meta.get_fields(include_hidden=True):
        if r.many_to_many and r.auto_created:
            if not r.related_model.__name__ in excepciones:
                for obj in getattr(instance_e, r.get_accessor_name()).all():
                    getattr(obj, r.field.name).remove(instance_e)
                    if not getattr(obj, r.field.name).filter(id=instance_s.id).exists():
                        getattr(obj, r.field.name).add(instance_s)

    for r in instance_e.__class__._meta.get_fields():
        if (r.one_to_many or r.one_to_one) and r.auto_created and not r.concrete:

            if not r.related_model.__name__ in excepciones:
                objects = []
                if r.one_to_one:
                    try:
                        getattr(instance_s, r.get_accessor_name())
                        continue
                    except ObjectDoesNotExist:
                        pass
                    try:
                        obj = getattr(instance_e, r.get_accessor_name())
                        objects.append(obj)
                    except ObjectDoesNotExist:
                        pass
                else:
                    objects = getattr(instance_e, r.get_accessor_name()).all()
                for obj in objects:
                    if not r.many_to_many:
                        try:
                            setattr(obj, r.field.name, instance_s)
                            obj.save()
                        except IntegrityError:
                            pass