from django.contrib import admin
from .models import Employee, Detected ,clients , allocation,hpadmin

# Register your models here.

admin.site.register(Employee)
admin.site.register(Detected)
admin.site.register(clients)
admin.site.register(allocation)
admin.site.register(hpadmin)