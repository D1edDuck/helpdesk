from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand

from tickets.models import Category


class Command(BaseCommand):
    help = "Инициализация тестовых данных"

    def handle(self, *args, **options) -> None:
        group, created = Group.objects.get_or_create(name="support_agents")
        if created:
            self.stdout.write(self.style.SUCCESS("✓ Группа support_agents создана"))
        else:
            self.stdout.write("  Группа support_agents уже существует")

        categories = ["Сеть", "Принтеры", "ПО", "Оборудование", "Прочее"]
        for name in categories:
            _obj, created = Category.objects.get_or_create(name=name)
            if created:
                self.stdout.write(self.style.SUCCESS(f"✓ Категория «{name}» создана"))

        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@example.com", "admin")
            self.stdout.write(
                self.style.SUCCESS("✓ Суперпользователь admin/admin создан")
            )

        if not User.objects.filter(username="agent").exists():
            agent = User.objects.create_user("agent", "agent@example.com", "agent123")
            agent.groups.add(group)
            self.stdout.write(self.style.SUCCESS("✓ Агент agent/agent123 создан"))

        if not User.objects.filter(username="user1").exists():
            User.objects.create_user("user1", "user1@example.com", "user123")
            self.stdout.write(self.style.SUCCESS("✓ Заявитель user1/user123 создан"))

        self.stdout.write(
            self.style.SUCCESS("\nГотово! Сервер: python manage.py runserver")
        )
