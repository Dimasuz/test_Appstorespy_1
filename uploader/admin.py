from django.contrib import admin

from .models import UploadFile

admin.site.register(UploadFile)


# @admin.register(UploadFile)
# class UploadFileAdmin(admin.ModelAdmin):
#     list_display = ('file', 'file_path', 'user',)
