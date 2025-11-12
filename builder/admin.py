from django.contrib import admin
from .models import variable,formula
# Register your models here.
class variableadmin(admin.ModelAdmin):
    list_display=['id','name','type','value']
    search_fields=['name','type','value']   
    list_filter=['type']
admin.site.register(variable,variableadmin)

class formulaadmin(admin.ModelAdmin):
    list_display=['id','name','expression']
    search_fields=['name','expression']
admin.site.register(formula,formulaadmin)