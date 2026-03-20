from django.contrib import admin
from .models import Category, Article, Source

class SourceInline(admin.TabularInline):
    model = Source
    extra = 1


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'created_at') 
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'summary') # Barre de recherche
    inlines = [SourceInline]

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',) 
    search_fields = ('name',) # Barre de recherche