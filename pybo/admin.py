from django.contrib import admin
from .models import Question, Answer

# Register your models here.
admin.site.register(Answer)


class QuestionAdmin(admin.ModelAdmin):
    search_fields = ['subject']
    
admin.site.register(Question, QuestionAdmin)
