# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.contrib.auth.models import User
from django.db import models
from model_utils.managers import InheritanceManager

from custom_users.models import Docente, Funcionario


class AnoLetivo(models.Model):
    ano = models.CharField(db_column='Ano', max_length=255, blank=True, null=True) 
    datainicio = models.DateField(db_column='DataInicio', blank=True, null=True)
    datafim = models.DateField(db_column='DataFim', blank=True, null=True)
    estado = models.CharField(db_column='Estado', max_length=255, blank=True, null=True) 
    class Meta:
        db_table = 'AnoLetivo'

class Curso(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    curso = models.CharField(db_column='curso', max_length=255, blank=True, null=True)
    codigo = models.IntegerField(db_column='Codigo', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'Curso'


class Semestre(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    inicio_data = models.DateField(db_column='Inicio_Data', blank=True, null=True)  # Field name made lowercase.
    fim_data = models.DateField(db_column='Fim_Data', blank=True, null=True)  # Field name made lowercase.
    nr_horas_service = models.IntegerField(db_column='Nr_Horas_service', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'Semestre'

class Disciplina(models.Model):
    id = models.AutoField(db_column='ID2', primary_key=True)  # Field name made lowercase.
    nome = models.CharField(db_column='Nome', max_length=255, blank=True, null=True)  # Field name made lowercase.
    estado = models.TextField(db_column='Estado')  # Field name made lowercase. This field type is a guess.
    codigodisciplina = models.IntegerField(db_column='codigodisciplina', blank=True, null=True)  # Field name made lowercase.
    semestreid = models.ForeignKey(Semestre, on_delete=models.CASCADE, db_column='SemestreID')  # Field name made lowercase.
    def __str__(self):
        return self.nome

    class Meta:
        db_table = 'Disciplina'

class CursoDisciplina(models.Model):
    cursoid = models.OneToOneField(Curso, on_delete=models.CASCADE, db_column='CursoID', primary_key=True)  # Field name made lowercase.
    disciplinaid2 = models.ForeignKey(Disciplina, on_delete=models.CASCADE, db_column='DisciplinaID2')  # Field name made lowercase.

    class Meta:
        db_table = 'Curso_Disciplina'
        unique_together = (('cursoid', 'disciplinaid2'),)





class Turma(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    nturma = models.CharField(db_column='NTurma', max_length=255, blank=True, null=True)  # Field name made lowercase.
    horas_semanais = models.CharField(db_column='Horas_semanais', max_length=255, blank=True, null=True)  # Field name made lowercase.
    horas_periodo = models.CharField(db_column='Horas_periodo', max_length=255, blank=True, null=True)  # Field name made lowercase.
    class Meta:
        db_table = 'Turma'



class Instituicao(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    sigla = models.CharField(db_column='Sigla', max_length=255, blank=True, null=True)
    nome = models.CharField(db_column='Nome', max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'Instituicao'


class Edificio(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    descricao = models.CharField(db_column='Descricao', max_length=255, blank=True, null=True)
    nome = models.CharField(db_column='Nome', max_length=255, blank=True, null=True)
    instituicao = models.ManyToManyField(Instituicao, through='EdificioInstituicao', related_name='edificios')
    localizacao = models.CharField(db_column='Localizacao', max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'Edificio'



class EdificioInstituicao(models.Model):
    edificio = models.ForeignKey(Edificio, on_delete=models.CASCADE)
    instituicao = models.ForeignKey(Instituicao, on_delete=models.CASCADE)

    class Meta:
        db_table = 'Edificio_Instituicao'


class TipoSala(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    tipo = models.CharField(db_column='Tipo', max_length=255, null=False)
    
    class Meta:
        db_table = 'TipoSala'

class Sala(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    nsala = models.CharField(db_column='NSala', max_length=255, blank=True, null=True)  # Field name made lowercase.
    lotacao = models.IntegerField(db_column='Lotacao', blank=True, null=True)  # Field name made lowercase.
    tipo_sala = models.ManyToManyField(TipoSala)  # Field name made lowercase.
    descricao = models.CharField(db_column='Descricao', max_length=255, blank=True, null=True)
    edificioid = models.ForeignKey(Edificio, on_delete=models.CASCADE, db_column='EdificioID', null=True)  # Field name made lowercase.
    anoletivo = models.ForeignKey(AnoLetivo, on_delete=models.CASCADE, db_column='AnoLetivo', null=True) # Field name made lowercase.
    
    class Meta:
        db_table = 'Sala'

class Docentes(models.Model):
    # Add any additional fields specific to Docente model here
    codigo = models.IntegerField(db_column='Codigo', blank=True,primary_key=True,default=0)  # Field name made lowercase.
    ativo = models.CharField(db_column='Ativo', max_length=255,blank=True, null=True)  # Field name made lowercase.
    nome = models.CharField(db_column='Nome', max_length=255, blank=True, null=True)  # Field name made lowercase.
    individuo = models.CharField(db_column='Individuo',max_length=255,blank=True, null=True)  # Field name made lowercase.
    data_de_nascimento = models.CharField(db_column='data_de_nascimento', max_length=255,blank=True, null=True)  # Field name made lowercase.
    sexo = models.CharField(db_column='sexo', max_length=255,blank=True, null=True)  # Field name made lowercase.
    tipo_de_identificacao = models.CharField(db_column='tipo_de_Identificacao', max_length=255,blank=True, null=True)  # Field name made lowercase.
    identificacao = models.CharField(db_column='identificacao', max_length=255, blank=True, null=True)  # Field name made lowercase.
    data_de_emissao_de_idenficacao = models.CharField(db_column='data_de_emissao_de_idenficacao', max_length=255,blank=True, null=True)  # Field name made lowercase.
    nacionalidade = models.CharField(db_column='nacionalidade', max_length=255,blank=True, null=True)  # Field name made lowercase.
    arquivo = models.CharField(db_column='arquivo', max_length=255,blank=True, null=True)  # Field name made lowercase.
    data_de_validade_da_identificacao = models.CharField(db_column='data_de_validade_da_identificacao', max_length=255,blank=True, null=True)  # Field name made lowercase.
    nif = models.CharField(db_column='nif', max_length=255,blank=True, null=True)  # Field name made lowercase.
    pais_fiscal = models.CharField(db_column='pais_fiscal', max_length=255,blank=True, null=True)  # Field name made lowercase.
    digito_verificacao = models.CharField(db_column='digito_verificacao',max_length=255,blank=True, null=True)  # Field name made lowercase. This field type is a guess.

    class Meta:
        db_table = 'docentes'

class Pedido(models.Model):
    objects = InheritanceManager()
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    nrpedido = models.IntegerField(db_column='NrPedido', blank=True, null=True)  # Field name made lowercase.
    titulo = models.CharField(db_column='titulo', max_length=255, blank=True, null=True)  # Field name made lowercase.
    descricao = models.CharField(db_column='Descricao', max_length=255, blank=True, null=True)  # Field name made lowercase.
    dataalvo = models.DateField(db_column='DataAlvo', blank=True, null=True)  # Field name made lowercase.
    dataanalise = models.DateField(db_column='DataAnalise', blank=True, null=True)  # Field name made lowercase.
    datavalidacao = models.DateField(db_column='DataValidacao', blank=True, null=True)  # Field name made lowercase.
    datacriacao = models.DateTimeField(db_column='DataCriacao', auto_now_add=True, blank=True, null=True)  # Field name made lowercase.
    estado = models.CharField(db_column='Estado', max_length=255, blank=True, null=True)  # Field name made lowercase.
    dataalteracao = models.DateTimeField(db_column='DataAlteracao', auto_now=True, blank=True, null=True)  # Field name made lowercase.
    anoletivo = models.ForeignKey(AnoLetivo, on_delete=models.CASCADE, db_column='AnoLetivo', null=True) 
    docente = models.ForeignKey(Docente, on_delete=models.SET_NULL, db_column='Docente', null=True)
    funcionario = models.ForeignKey(Funcionario, on_delete=models.SET_NULL, db_column='Funcionario', null=True)
    class Meta:
        db_table = 'Pedido'



class Linha(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    descricao = models.CharField(db_column='Descricao', max_length=255, blank=True, null=True)  # Field name made lowercase.
    uc = models.ForeignKey(Disciplina, on_delete=models.CASCADE, db_column='Disciplina', blank=False)#
    pedidoID = models.ForeignKey(Pedido, on_delete=models.CASCADE, db_column='PedidoID')#


class LinhaOutros(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    descricao = models.CharField(db_column='Descricao', max_length=255, blank=True, null=True)  # Field name made lowercase.
    pedidoID = models.ForeignKey(Pedido, on_delete=models.CASCADE, db_column='PedidoID')#

class LinhaHorario(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)

    tipodepedido = models.CharField(db_column='tipodepedido', max_length=255, blank=True, null=True)

    diadasemana = models.CharField(db_column='diadasemana', max_length=255, blank=True, null=True)
    horainicio = models.TimeField(db_column='HoraInicio', blank=True, null=True)
    horafim = models.TimeField(db_column='HoraFim', blank=True, null=True)
    datainicio = models.DateField(db_column='DataInicio', blank=True, null=True)
    datafim = models.DateField(db_column='DataFim', blank=True, null=True)

    novadiadasemana = models.CharField(db_column='novadiadasemana', max_length=255, blank=True, null=True)
    novahorainicio = models.TimeField(db_column='novaHoraInicio', blank=True, null=True)
    novahorafim = models.TimeField(db_column='novaHoraFim', blank=True, null=True)
    novadatainicio = models.DateField(db_column='novaDataInicio', blank=True, null=True)
    novadatafim = models.DateField(db_column='novaDataFim', blank=True, null=True)

    pedidoID = models.ForeignKey(Pedido, on_delete=models.CASCADE, db_column='PedidoID')#



class LinhaSala(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    detalhe = models.CharField(db_column='Detalhe', max_length=255, blank=True, null=True)
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE, db_column='Sala', blank=True, null=True) # Field name made lowercase.
    horainicio = models.TimeField(db_column='HoraInicio', blank=True, null=True)
    horafim = models.TimeField(db_column='HoraFim', blank=True, null=True)
    horainicioantigo = models.TimeField(db_column='HoraInicioAntigo', blank=True, null=True)
    horafimantigo = models.TimeField(db_column='HoraFimAntigo', blank=True, null=True)
    tipopedido = models.CharField(db_column='TipoPedido', max_length=255, blank=True, null=True)
    categoriatemporal = models.CharField(db_column='CategoriaTemporal', max_length=255, blank=True, null=True)
    pedidoID = models.ForeignKey(Pedido, on_delete=models.CASCADE, db_column='PedidoID')

    



class Salas(models.Model):
    t = models.IntegerField(db_column='T', blank=True, null=True)  # Field name made lowercase.
    tp = models.IntegerField(db_column='TP', blank=True, null=True)  # Field name made lowercase.
    pl = models.IntegerField(db_column='PL', blank=True, null=True)  # Field name made lowercase.
    p = models.IntegerField(db_column='P', blank=True, null=True)  # Field name made lowercase.
    l = models.IntegerField(db_column='L', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'Salas'




class DSD(models.Model):
    objects = InheritanceManager()
    periodo = models.CharField(db_column='Período', max_length=255, blank=True, null=True)  # Field name made lowercase.
    cod_disciplina = models.IntegerField(db_column='Cód. disciplina', blank=True, null=True)  # Field name made lowercase.
    disciplina = models.CharField(db_column='Disciplina', max_length=255, blank=True, null=True)  # Field name made lowercase.
    inst_discip = models.CharField(db_column='Inst. discip.', max_length=255, blank=True, null=True)  # Field name made lowercase.
    inst_disciplina = models.CharField(db_column='Inst. disciplina', max_length=255, blank=True, null=True)  # Field name made lowercase.
    depart_disciplina = models.CharField(db_column='Depart. disciplina', max_length=255, blank=True, null=True)  # Field name made lowercase.
    turma = models.CharField(db_column='Turma', max_length=255, blank=True, null=True)  # Field name made lowercase.
    codigo_curso = models.CharField(db_column='Código curso' ,max_length=255, blank=True, null=True)
    curso = models.CharField(db_column='Curso', max_length=255, blank=True, null=True)
    Cod_Docente = models.CharField(db_column='Cód. Docente', max_length=255, blank=True, null=True)
    docente = models.CharField(db_column='Docente', max_length=255, blank=True, null=True)
    func_docente = models.CharField(db_column='Função docente', max_length=255, blank=True, null=True)
    inst_docente = models.CharField(db_column='Inst. docente', max_length=255, blank=True, null=True)
    depart_docente = models.CharField(db_column='Depart. docente', max_length=255, blank=True, null=True)
    horas_semanais = models.CharField(db_column='Horas semanais', max_length=255, blank=True, null=True)
    horas_periodo = models.CharField(db_column='Horas período', max_length=255, blank=True, null=True)
    factor = models.IntegerField(db_column='Factor', blank=True, null=True)
    horas_servico = models.IntegerField(db_column='Horas serviço', blank=True, null=True)
    data_inicio = models.CharField(db_column='Data início', max_length=255, blank=True, null=True)
    data_fim = models.CharField(db_column='Data fim', max_length=255, blank=True, null=True)
    nome_docente = models.CharField(db_column='Nome Docente', max_length=255, blank=True, null=True)
    agrupamento = models.CharField(db_column='Agrupamento', max_length=255, blank=True, null=True)
    class Meta:
        db_table = 'dsd'




class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, on_delete=models.CASCADE)
    permission = models.ForeignKey('AuthPermission', on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', on_delete=models.CASCADE)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, on_delete=models.CASCADE)
    group = models.ForeignKey(AuthGroup, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, on_delete=models.CASCADE)
    permission = models.ForeignKey(AuthPermission, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', on_delete=models.CASCADE, blank=True, null=True)
    user = models.ForeignKey(AuthUser, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'