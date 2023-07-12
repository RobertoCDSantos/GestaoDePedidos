
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    codigo = models.IntegerField(db_column='Codigo', blank=True,primary_key=True,default=0)  # Field name made lowercase.
    is_docente = models.BooleanField(default=False)
    is_funcionario = models.BooleanField(default=False)
    pass


class Docente(CustomUser):
    # Add any additional fields specific to Docente model here

    class Meta:
        db_table = 'docente'

class Funcionario(CustomUser):
    # Add any additional fields specific to Funcionario model here
    class Meta:
        db_table = 'funcionario'


class RightsSupport(models.Model):
            
    class Meta:
        
        managed = False  # No database table creation or deletion  \
                         # operations will be performed for this model. 
                
        default_permissions = () # disable "add", "change", "delete"
                                 # and "view" default permissions

        permissions = ( 
            ('docente_rights', 'Global docente rights'),  
            ('funcionario_rights', 'Global funcionario rights'),
            ('any_rights', 'Global any rights'),  
        )
