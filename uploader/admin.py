from django.contrib import admin

from .models import UploadFile, FileInDb, FileOnDisk

class FileInDefDbInline(admin.TabularInline):
    model = FileInDb

# admin.site.register(UploadFile)
@admin.register(UploadFile)
class UploadFileAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'uploaded_on', 'user',)
    inlines = [FileInDefDbInline]

admin.site.register(FileInDb)
# @admin.register(FileInDefDb)
# class FileInDefDbAdmin(admin.ModelAdmin):
#     list_display = ('file', 'file_id',)



admin.site.register(FileOnDisk)


