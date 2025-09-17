import sys #Con esta libreria recibimos los argumentos
import os

def main():
    # Tu código actual aquí, pero adaptado
    if len(sys.argv) < 2:
        print("Error: Debes especificar el nombre de la aplicación")
        print("Uso: crear-app-django <nombre_app>")
        sys.exit(1)
    
    
    print(sys.argv)
    print(sys.argv[1])


    # Variables
    app_nombre = f"{sys.argv[1]}".lower()
    app_nombre_con_aplicacion = "aplicaciones."+app_nombre

    # Contenido para apps.py
    contenido = """from django.apps import AppConfig


    class {}Config(AppConfig):
        default_auto_field = 'django.db.models.BigAutoField'
        name = '{}'
    """.format(app_nombre.capitalize(), app_nombre_con_aplicacion)


    #print(contenido)


    #1.Creamos la carpeta principal con el nombre de la aplicacion
    #os.mkdir(app_nombre.lower())
    #os.makedirs("APP/migrations")
    #os.makedirs(f"{app_nombre}/migrations")


    # Paso 1: Crea la carpeta 'migrations' dentro de la carpeta de la app
    # La función makedirs() creará tanto 'mi_blog' como 'mi_blog/migrations'
    # si no existen.
    ruta_migrations = os.path.join(app_nombre, "migrations")
    os.makedirs(ruta_migrations, exist_ok=True)

    # Paso 2: Crea el archivo __init__.py dentro de la carpeta migrations
    ruta_init = os.path.join(ruta_migrations, "__init__.py")
    # Abre el archivo en modo de escritura ('w').
    # No es necesario escribir nada, ya que la existencia del archivo es suficiente.
    with open(ruta_init, "w") as archivo:
        pass

    # Paso 3: Crea los otros archivos al mismo nivel que app_nombre

    print(f"La carpeta '{ruta_migrations}' y el archivo '{ruta_init}' han sido creados.")

    # Ruta para el archivo __init__.py
    ruta___init__ = os.path.join(app_nombre, "__init__.py")
    with open(ruta___init__, "w") as f:
        pass


    # Contenido del código comentado para admin.py
    contenido_comentado = """# from django.contrib import admin
    # from aplicaciones.historial.models import *

    # @admin.register(HistorialActividadesUsuarios)
    # class HistorialActividadesUsuariosAdmin(admin.ModelAdmin):
    #     # Campos que se mostraran en la vista de lista del admin
    #     list_display = ('fecha', 'usuario', 'tipo_actividad', 'descripcion', 'usuario_modificado', 'objeto_id')
        
    #     # Campos para la busqueda en el admin
    #     search_fields = ('usuario__email', 'descripcion', 'objeto_id')
        
    #     # Campos que se pueden filtrar
    #     list_filter = ('tipo_actividad', 'fecha')

    #     # Campos que seran de solo lectura en el formulario
    #     readonly_fields = ('fecha', 'usuario', 'usuario_modificado', 'tipo_actividad', 'descripcion', 'objeto_id', 'objeto_tipo')
    # """

    # Ruta para el archivo admin.py
    ruta_admin = os.path.join(app_nombre, "admin.py")
    with open(ruta_admin, "w") as f:
        f.write(contenido_comentado)

    # Ruta para el archivo form.py
    ruta_form = os.path.join(app_nombre, "form.py")
    with open(ruta_form, "w") as f:
        pass

    # Ruta para el archivo views.py
    ruta_views = os.path.join(app_nombre, "views.py")
    with open(ruta_views, "w") as f:
        pass

    # Ruta para el archivo urls.py
    ruta_urls = os.path.join(app_nombre, "urls.py")
    with open(ruta_urls, "w") as f:
        f.write("from django.urls import path\n")
        f.write("from . import views\n\n")
        f.write(f"app_name = '{app_nombre}'\n\n") # ⬅️ Corrección aquí
        f.write("urlpatterns = [\n")
        f.write("    # path('mi-ruta/', views.mi_vista, name='mi_vista'),\n")
        f.write("]\n")

    # Ruta para el archivo apps.py
    ruta_apps = os.path.join(app_nombre, "apps.py")
    with open(ruta_apps, "w") as f:
        f.write(contenido)

    # Ruta para el archivo models.py
    ruta_models = os.path.join(app_nombre, "models.py")
    with open(ruta_models, "w") as f:
        pass

    # Ruta para el archivo tests.py
    ruta_tests = os.path.join(app_nombre, "tests.py")
    with open(ruta_tests, "w") as f:
        pass

    # Ruta para el archivo tests.py
    ruta_tests = os.path.join(app_nombre, "tests.py")
    with open(ruta_tests, "w") as f:
        pass

    # Ruta para el archivo signals.py
    ruta_signals = os.path.join(app_nombre, "signals.py")
    with open(ruta_signals, "w") as f:
        pass






# Este bloque permite ejecutar el script directamente
if __name__ == "__main__":
    main()




