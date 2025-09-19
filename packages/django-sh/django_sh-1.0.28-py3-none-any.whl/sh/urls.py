from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = "sh"

urlpatterns = [
    path('', views.command, name="command"),
    path('command/', views.command, name="command"),
    path('command/<int:pk>/', views.command, name="command"),
    path('settings/', views.editar_configuracion, name="settings"),
    path('reports/', views.reports, name="reports"),
    path('view_report/<int:pk>/', views.view_report, name="view_report"),
    path('command_history/', views.command_history, name="command_history"),
    path('saved_commands/', views.saved_commands, name="saved_commands"),
    path('save_command/<int:pk>/', views.save_command, name="save_command"),
    path('delete_saved_command/<int:pk>/', views.delete_saved_command, name="delete_saved_command"),
]

urlpatterns = urlpatterns + static(
    settings.STATIC_URL, document_root=settings.STATIC_ROOT
)

