from django.contrib import admin

# Register your models here.
from . models import *

class BooksInventoryAdmin(admin.ModelAdmin):
	list_display = ('book_name', 'author_name', 'books_count')

admin.site.register(BooksLibrary, BooksInventoryAdmin)
admin.site.register(UserProfile)