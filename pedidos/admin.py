from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(AnoLetivo)
admin.site.register(Curso)
admin.site.register(Semestre)
admin.site.register(Disciplina)
admin.site.register(CursoDisciplina)
admin.site.register(Edificio)
admin.site.register(Sala)
admin.site.register(Turma)
admin.site.register(Docente)
admin.site.register(Funcionario)
admin.site.register(Instituicao)
admin.site.register(EdificioInstituicao)
admin.site.register(Pedido)
admin.site.register(Salas)
admin.site.register(AuthGroup)
admin.site.register(AuthGroupPermissions)
admin.site.register(AuthPermission)
admin.site.register(AuthUser)
admin.site.register(AuthUserGroups)
admin.site.register(AuthUserUserPermissions)
admin.site.register(DjangoAdminLog)
admin.site.register(DjangoContentType)
admin.site.register(DjangoMigrations)
admin.site.register(DjangoSession)


