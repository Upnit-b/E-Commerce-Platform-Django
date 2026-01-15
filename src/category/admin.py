from django.contrib import admin

from .models import Category

# Register your models here.
# configuring the category admin view and functionality
class CategoryAdmin(admin.ModelAdmin):
    # prepopulated_fields = {"slug": ("category_name",)}
    list_display = ("category_name", "slug")
    readonly_fields = ("slug",)


admin.site.register(Category, CategoryAdmin)
