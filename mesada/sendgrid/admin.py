# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import SendEmailSendgridEvent, SendgridTemplates


@admin.register(SendgridTemplates)
class SendgridTemplatesAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "template_id")
    search_fields = ("name",)


@admin.register(SendEmailSendgridEvent)
class SendEmailSendgridEventAdmin(admin.ModelAdmin):
    list_display = ("id", "success", "causes", "created", "template_id")
    list_filter = ("success", "created")
