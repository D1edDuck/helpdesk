from datetime import timedelta

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Category(models.Model):
    name = models.CharField("Название", max_length=100)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Ticket(models.Model):
    STATUS_NEW = "new"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_WAITING = "waiting"
    STATUS_RESOLVED = "resolved"
    STATUS_CLOSED = "closed"

    STATUS_CHOICES = [
        (STATUS_NEW, "Новая"),
        (STATUS_IN_PROGRESS, "В работе"),
        (STATUS_WAITING, "Ожидает ответа"),
        (STATUS_RESOLVED, "Решена"),
        (STATUS_CLOSED, "Закрыта"),
    ]

    PRIORITY_LOW = "low"
    PRIORITY_MEDIUM = "medium"
    PRIORITY_HIGH = "high"
    PRIORITY_CRITICAL = "critical"

    PRIORITY_CHOICES = [
        (PRIORITY_LOW, "Низкий"),
        (PRIORITY_MEDIUM, "Средний"),
        (PRIORITY_HIGH, "Высокий"),
        (PRIORITY_CRITICAL, "Критичный"),
    ]

    PRIORITY_HOURS = {
        PRIORITY_CRITICAL: 4,
        PRIORITY_HIGH: 8,
        PRIORITY_MEDIUM: 24,
        PRIORITY_LOW: 72,
    }

    STATUS_TRANSITIONS = {
        STATUS_NEW: [STATUS_IN_PROGRESS, STATUS_CLOSED],
        STATUS_IN_PROGRESS: [STATUS_WAITING, STATUS_RESOLVED, STATUS_CLOSED],
        STATUS_WAITING: [STATUS_IN_PROGRESS, STATUS_RESOLVED, STATUS_CLOSED],
        STATUS_RESOLVED: [STATUS_CLOSED, STATUS_IN_PROGRESS],
        STATUS_CLOSED: [],
    }

    subject = models.CharField("Тема", max_length=200)
    description = models.TextField("Описание")
    status = models.CharField(
        "Статус", max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW
    )
    priority = models.CharField("Приоритет", max_length=20, choices=PRIORITY_CHOICES)
    deadline = models.DateTimeField("Дедлайн")
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, verbose_name="Категория"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="created_tickets",
        verbose_name="Создал",
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="assigned_tickets",
        null=True,
        blank=True,
        verbose_name="Исполнитель",
    )
    created_at = models.DateTimeField("Создана", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлена", auto_now=True)

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"#{self.pk} {self.subject}"

    def save(self, *args, **kwargs) -> None:
        if not self.pk and not self.deadline:
            hours = self.PRIORITY_HOURS.get(self.priority, 24)
            self.deadline = timezone.now() + timedelta(hours=hours)
        super().save(*args, **kwargs)

    @property
    def is_overdue(self) -> bool:
        if self.status in (self.STATUS_RESOLVED, self.STATUS_CLOSED):
            return False
        return self.deadline < timezone.now()

    @property
    def priority_color(self) -> str:
        return {
            self.PRIORITY_LOW: "success",
            self.PRIORITY_MEDIUM: "warning",
            self.PRIORITY_HIGH: "orange",
            self.PRIORITY_CRITICAL: "danger",
        }.get(self.priority, "secondary")

    @property
    def allowed_next_statuses(self):
        """Returns list of (status_code, label) that are valid transitions."""
        allowed = self.STATUS_TRANSITIONS.get(self.status, [])
        return [(s, dict(self.STATUS_CHOICES)[s]) for s in allowed]

    @property
    def status_label(self) -> str | None:
        return dict(self.STATUS_CHOICES).get(self.status, self.status)

    @property
    def priority_label(self) -> str | None:
        return dict(self.PRIORITY_CHOICES).get(self.priority, self.priority)


class Comment(models.Model):
    ticket = models.ForeignKey(
        Ticket, on_delete=models.CASCADE, related_name="comments", verbose_name="Заявка"
    )
    author = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Автор")
    text = models.TextField("Текст")
    created_at = models.DateTimeField("Создан", auto_now_add=True)

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"Комментарий от {self.author} к {self.ticket}"
