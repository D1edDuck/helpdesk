import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100, verbose_name="Название")),
            ],
            options={
                "verbose_name": "Категория",
                "verbose_name_plural": "Категории",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Ticket",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("subject", models.CharField(max_length=200, verbose_name="Тема")),
                ("description", models.TextField(verbose_name="Описание")),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("new", "Новая"),
                            ("in_progress", "В работе"),
                            ("waiting", "Ожидает ответа"),
                            ("resolved", "Решена"),
                            ("closed", "Закрыта"),
                        ],
                        default="new",
                        max_length=20,
                        verbose_name="Статус",
                    ),
                ),
                (
                    "priority",
                    models.CharField(
                        choices=[
                            ("low", "Низкий"),
                            ("medium", "Средний"),
                            ("high", "Высокий"),
                            ("critical", "Критичный"),
                        ],
                        max_length=20,
                        verbose_name="Приоритет",
                    ),
                ),
                ("deadline", models.DateTimeField(verbose_name="Дедлайн")),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Создана"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Обновлена"),
                ),
                (
                    "assigned_to",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="assigned_tickets",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Исполнитель",
                    ),
                ),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="tickets.category",
                        verbose_name="Категория",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="created_tickets",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Создал",
                    ),
                ),
            ],
            options={
                "verbose_name": "Заявка",
                "verbose_name_plural": "Заявки",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="Comment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("text", models.TextField(verbose_name="Текст")),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Создан"),
                ),
                (
                    "author",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Автор",
                    ),
                ),
                (
                    "ticket",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="comments",
                        to="tickets.ticket",
                        verbose_name="Заявка",
                    ),
                ),
            ],
            options={
                "verbose_name": "Комментарий",
                "verbose_name_plural": "Комментарии",
                "ordering": ["created_at"],
            },
        ),
    ]
