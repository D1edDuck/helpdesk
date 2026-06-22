from django.contrib import admin

from .models import Category, Comment, Ticket


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ("author", "created_at")


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "subject",
        "status",
        "priority",
        "category",
        "created_by",
        "assigned_to",
        "deadline",
        "created_at",
    )
    list_filter = ("status", "priority", "category")
    search_fields = ("subject", "description")
    raw_id_fields = ("created_by", "assigned_to")
    readonly_fields = ("created_at", "updated_at")
    inlines = [CommentInline]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "ticket", "author", "created_at")
    readonly_fields = ("created_at",)
