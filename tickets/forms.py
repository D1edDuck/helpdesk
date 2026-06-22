from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group, User

from .models import Comment, Ticket


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=False, label="Email")

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"


class TicketCreateForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ("subject", "description", "category", "priority")
        widgets = {
            "subject": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "priority": forms.Select(attrs={"class": "form-select"}),
        }
        labels = {
            "subject": "Тема",
            "description": "Описание",
            "category": "Категория",
            "priority": "Приоритет",
        }


class AgentUpdateForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ("priority", "deadline")
        widgets = {
            "priority": forms.Select(attrs={"class": "form-select"}),
            "deadline": forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            ),
        }
        labels = {
            "priority": "Приоритет",
            "deadline": "Дедлайн",
        }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.deadline:
            self.initial["deadline"] = self.instance.deadline.strftime("%Y-%m-%dT%H:%M")


class AssignForm(forms.ModelForm):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        try:
            support_group = Group.objects.get(name="support_agents")
            agents = User.objects.filter(groups=support_group, is_active=True)
        except Group.DoesNotExist:
            agents = User.objects.none()
        self.fields["assigned_to"].queryset = agents
        self.fields["assigned_to"].widget.attrs["class"] = "form-select"
        self.fields["assigned_to"].required = False

    class Meta:
        model = Ticket
        fields = ("assigned_to",)
        labels = {"assigned_to": "Исполнитель"}


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("text",)
        widgets = {
            "text": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Введите комментарий...",
                }
            ),
        }
        labels = {"text": "Комментарий"}


class TicketFilterForm(forms.Form):
    status = forms.ChoiceField(
        choices=[("", "Все статусы")] + Ticket.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-select form-select-sm"}),
        label="Статус",
    )
    priority = forms.ChoiceField(
        choices=[("", "Все приоритеты")] + Ticket.PRIORITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-select form-select-sm"}),
        label="Приоритет",
    )
    assigned_to = forms.ModelChoiceField(
        queryset=User.objects.none(),
        required=False,
        empty_label="Все исполнители",
        widget=forms.Select(attrs={"class": "form-select form-select-sm"}),
        label="Исполнитель",
    )
    sort = forms.ChoiceField(
        choices=[
            ("-created_at", "Сначала новые"),
            ("created_at", "Сначала старые"),
            ("deadline", "Дедлайн ↑"),
            ("-deadline", "Дедлайн ↓"),
        ],
        required=False,
        widget=forms.Select(attrs={"class": "form-select form-select-sm"}),
        label="Сортировка",
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        try:
            support_group = Group.objects.get(name="support_agents")
            self.fields["assigned_to"].queryset = User.objects.filter(
                groups=support_group, is_active=True
            )
        except Group.DoesNotExist:
            pass
