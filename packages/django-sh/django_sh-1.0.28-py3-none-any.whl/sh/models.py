from django.db import models
from django.contrib.auth import get_user_model
import pathlib
from .functions import (
    to_datetime
)
# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger("sh")

with open(pathlib.Path(__file__).parent.resolve() / "auth_function_default.py", "r") as file_auth:
    DEFAULT_AUTH_FUNCTION_STR = file_auth.read()

class ShellSettings(models.Model):
    code_before = models.TextField(null=True)
    code_after = models.TextField(null=True)
    auth_function = models.TextField(null=True, default=DEFAULT_AUTH_FUNCTION_STR)

    def _evaluate_auth_function(self, request):
        if not self.auth_function:
            return request.user.is_superuser
        
        try:
            compiled_code = compile(self.auth_function, "<string>", "exec")
            _local_vars = {}
            exec(compiled_code, {}, _local_vars)

            if "is_valid_user" in _local_vars:
                return _local_vars["is_valid_user"](request)
            else:
                logger.error(f"No se encontró la función is_valid_user en locals()")
            
            return request.user.is_superuser

        except Exception as e:
            logger.error(str(e))
            return request.user.is_superuser
    
    def is_valid_request(self, request):
        error = self._evaluate_auth_function(request)
        if error:
            return error

class Command(models.Model):
    text = models.TextField(null=True)
    output = models.TextField(null=True)
    error = models.TextField(null=True)
    start = models.DateTimeField(null=True)
    end = models.DateTimeField(null=True)
    created_at = models.DateTimeField(null=True, auto_now_add=True)
    user = models.ForeignKey(get_user_model()(), related_name="sh_commands", on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ("-id",)
    
    def to_dict(self):
        return {
            "id": self.pk,
            "output": self.output,
        }
    

    def get_duracion(self):
        if not self.start or not self.end:
            return "No disponible"

        delta = self.end - self.start  # timedelta
        total_seconds = delta.total_seconds()

        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        parts = []
        if hours >= 1:
            parts.append(f"{int(hours)}h")
        if minutes >= 1:
            parts.append(f"{int(minutes)}m")
        if seconds > 0 or not parts:
            # segundos con hasta 3 decimales si hace falta
            parts.append(f"{seconds:.3f}s".rstrip("0").rstrip("."))

        return " ".join(parts)
        

    @classmethod
    def get_objects(cls, vars):
        q = vars.get("q","")
        desde = vars.get("desde")
        hasta = vars.get("hasta")
        objects = cls.objects.all()
       
        if q:
            objects = objects.filter(
                models.Q(text__icontains=q)
            )
        if desde:
            desde = to_datetime(desde, min=True)
            objects = objects.filter(start__gte=desde)
    
        if hasta:
            hasta = to_datetime(hasta, max=True)
            objects = objects.filter(start__lte=hasta)

        return objects

class SavedCommand(models.Model):
    user = models.ForeignKey(get_user_model()(), related_name="sh_saved_commands", on_delete=models.CASCADE)
    command = models.ForeignKey(Command, related_name="users", on_delete=models.PROTECT)
    description = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
