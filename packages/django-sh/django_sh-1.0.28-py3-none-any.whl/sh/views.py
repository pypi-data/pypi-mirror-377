from operator import length_hint
from django.contrib.auth.decorators import login_required, permission_required
from django.db import models
from django.shortcuts import get_object_or_404, render, HttpResponse, redirect
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from .models import SavedCommand, ShellSettings, Command
from django.contrib.auth.decorators import user_passes_test
from django.utils import timezone
from django.urls import reverse
from . import utils_views
from .forms import FiltroForm, EMPTY_CHOICE


#@user_passes_test(lambda u: u.is_superuser)
def command(request, pk=None): 
    shell_settings = ShellSettings.objects.get_or_create()[0]
    error = shell_settings.is_valid_request(request)
    if error:
        return HttpResponse(error)
    
    error = ''
    command_obj = None
    objects = []
    matrix = []
    
    if request.method == 'POST':
        command_obj, error = ejecutar(request)  
        return redirect(reverse("sh:command", args=[command_obj.pk]))
    
    default_command_text = ""
    if pk:
        command_obj = get_object_or_404(Command, pk=pk)
        default_command_text = command_obj.text

    command = request.POST.get("query", default_command_text)
    return render(request, 'sh/command.html', { 
        'objects':objects, 
        'query': command, 
        'command_obj': command_obj, 
        'error':error,
        "pk":pk
    }) 


#@user_passes_test(lambda u: u.is_superuser)
def ejecutar(request):
    from builtins import str

    try:
        shell_settings = ShellSettings.objects.get()
    except ObjectDoesNotExist:
        shell_settings = ShellSettings.objects.get_or_create()[0]
       
    command = Command(user=request.user)
    objects = []
    matrix = []
    query = request.POST.get('query', '').strip()
    q = query.replace("\r","")
    q += "\n"
    error = ""

    command.start = timezone.now()
    command_string = ""

    # helpers
    _ = objects.append
    
    command.text = f"{q}"
    command_string += f"{command.text}\n"

    if shell_settings.code_after:
        command_string += f"\n\n{shell_settings.code_after}"

    command.save()

    if request.POST.get("enable_try"):
        try:
            _local_vars = {"_": _}
            compiled_code = compile(shell_settings.code_before, "<string>", "exec")
            exec(compiled_code, {}, _local_vars)

            compiled_code = compile(command_string, "<string>", "exec")
            exec(command_string, {}, _local_vars)

        except Exception as e:
            error = u"%s %s" % (str(e.__class__), str(e))
    else:
        _local_vars = {"_": _}
        compiled_code = compile(shell_settings.code_before, "<string>", "exec")
        exec(compiled_code, {}, _local_vars)

        compiled_code = compile(command_string, "<string>", "exec")
        exec(command_string, {}, _local_vars)
    
    command.end = timezone.now()
    out = "\n".join([str(x) for x in objects])
    command.output = f"No. de elementos: {len(objects)} \n {out}"
   

    if error:
        command.error = error

    command.save()

    return command, error

#@user_passes_test(lambda u: u.is_superuser)
def editar_configuracion(request):
    shell_settings = ShellSettings.objects.get_or_create()[0]
    error = shell_settings.is_valid_request(request)
    if error:
        return HttpResponse(error)

    if request.method == "POST":
        shell_settings.code_before = request.POST.get("code_before")
        shell_settings.auth_function = request.POST.get("auth_function")
        shell_settings.save()
        return redirect("sh:command")
    
    return render(
        request,
        'sh/settings.html',
        {"shell_settings":shell_settings},
    )

def reports(request):
    return redirect("/")


#@user_passes_test(lambda u: u.is_superuser)
def save_command(request, pk):
    shell_settings = ShellSettings.objects.get_or_create()[0]
    error = shell_settings.is_valid_request(request)
    if error:
        return HttpResponse(error)

    instance = get_object_or_404(Command, pk=pk)
    saved_command = SavedCommand.objects.create(
        command=instance, 
        user=request.user,
    )
    return redirect("sh:command_history")

@user_passes_test(lambda u: u.is_superuser)
def view_report(request, pk):
    """
    No hace validación de firewall
    """

    if request.user.is_anonymous:
        return redirect("/")

    instance = get_object_or_404(Command, pk=pk)
    
    prohibited_strings = [
        "delete",
        "save",
        "update",
        "create",
    ]
    for ps in prohibited_strings:
        assert not ps in instance.text

    objects = []
    matrix = []
    _ = objects.append
    try:
        exec(shell_settings.code_before)    
        exec(instance.text)
    except Exception as e:
        return HttpResponse(e)
        
    return format_response(matrix)

def format_response(matrix, is_table=True):

    if is_table:
        outtxt = "<table>\n"
        for line in matrix:
            outtxt += "<tr>\n"    
            for col in line:
                outtxt += f"    <td>{col}</td>\n"
            outtxt +="</tr>\n"
        outtxt += "</table>"
    else:
        outtxt = "<br />".join(matrix)

    return HttpResponse(outtxt)  

#@user_passes_test(lambda u: u.is_superuser)
def delete_saved_command(request, pk):
    shell_settings = ShellSettings.objects.get_or_create()[0]
    shell_settings.is_valid_request(request)
    obj = request.user.sh_saved_commands.get(pk=pk)
    obj.delete()
    return redirect("sh:saved_commands")

#@user_passes_test(lambda u: u.is_superuser)
def saved_commands(request):
    rget = request.GET.copy()
    shell_settings = ShellSettings.objects.get_or_create()[0]
    shell_settings.is_valid_request(request)

    rget = request.GET.copy()
    rget["usuario"] = request.user

    filtro_form = FiltroForm(request.GET)

    if filtro_form.is_valid():
        q = filtro_form.cleaned_data["q"]
        desde = filtro_form.cleaned_data["desde"]
        hasta = filtro_form.cleaned_data["hasta"]
        objects = request.user.sh_saved_commands.all()

        if q:
             objects = objects.filter(
                models.Q(command__text__icontains=q)
            )

        if desde:
            objects = objects.filter(
                models.Q(command__start__gte=desde)
            )
        
        if hasta:
            objects = objects.filter(
                models.Q(command__start__lte=hasta)
            )

        return utils_views.list_view(
            request,
            objects,
            template='sh/saved_commands.html',
            variables = {
                'filtro_form':filtro_form,
            }
        
        )


#@user_passes_test(lambda u: u.is_superuser)
def command_history(request):
    shell_settings = ShellSettings.objects.get_or_create()[0]
    shell_settings.is_valid_request(request)

    filtro_form = FiltroForm(request.GET)

    if filtro_form.is_valid():

        objects = Command.get_objects(filtro_form.cleaned_data)

        return utils_views.list_view(
            request,
            objects,
            template='sh/command_history.html',
            variables = {
                'filtro_form':filtro_form,
            }
        
        )
