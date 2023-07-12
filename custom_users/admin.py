from django.contrib import admin
from .models import *

# Register your models here.
filter_horizontal = ('groups', 'user_permissions')
admin.site.register(CustomUser)
