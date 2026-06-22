from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseForbidden,
    HttpResponseRedirect,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import (
    AgentUpdateForm,
    AssignForm,
    CommentForm,
    RegisterForm,
    TicketCreateForm,
    TicketFilterForm,
)
from .models import Ticket


def is_agent(user) -> bool:
    return user.groups.filter(name="support_agents").exists() or user.is_staff


def require_agent(view_func):
    """Decorator: allow only agents / staff."""

    def wrapper(request, *args, **kwargs):
        if not is_agent(request.user):
            return HttpResponseForbidden("Доступ запрещён.")
        return view_func(request, *args, **kwargs)

    wrapper.__name__ = view_func.__name__
    return login_required(wrapper)


def register(request: HttpRequest) -> HttpResponseRedirect | HttpResponse:
    if request.user.is_authenticated:
        return redirect("ticket_list")
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Регистрация прошла успешно!")
            return redirect("ticket_list")
    else:
        form = RegisterForm()
    return render(request, "tickets/register.html", {"form": form})


@login_required
def home(request: HttpRequest) -> HttpResponseRedirect:
    return redirect("ticket_list")


@login_required
def ticket_list(request: HttpRequest) -> HttpResponse:
    agent = is_agent(request.user)

    if agent:
        qs = Ticket.objects.select_related("category", "created_by", "assigned_to")
    else:
        qs = Ticket.objects.filter(created_by=request.user).select_related(
            "category", "created_by", "assigned_to"
        )

    filter_form = TicketFilterForm(request.GET) if agent else None

    if agent and filter_form and filter_form.is_valid():
        cd = filter_form.cleaned_data
        if cd.get("status"):
            qs = qs.filter(status=cd["status"])
        if cd.get("priority"):
            qs = qs.filter(priority=cd["priority"])
        if cd.get("assigned_to"):
            qs = qs.filter(assigned_to=cd["assigned_to"])
        sort = cd.get("sort") or "-created_at"
        qs = qs.order_by(sort)
    else:
        qs = qs.order_by("-created_at")

    now = timezone.now()
    return render(
        request,
        "tickets/ticket_list.html",
        {
            "tickets": qs,
            "filter_form": filter_form,
            "is_agent": agent,
            "now": now,
        },
    )


@login_required
def ticket_create(request: HttpRequest) -> HttpResponseRedirect | HttpResponse:
    if request.method == "POST":
        form = TicketCreateForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.created_by = request.user
            ticket.save()
            messages.success(request, f"Заявка #{ticket.pk} создана.")
            return redirect("ticket_detail", pk=ticket.pk)
    else:
        form = TicketCreateForm()
    return render(request, "tickets/ticket_create.html", {"form": form})


@login_required
def ticket_detail(
    request: HttpRequest, pk: int
) -> HttpResponseForbidden | HttpResponse:
    ticket = get_object_or_404(Ticket, pk=pk)
    agent = is_agent(request.user)

    if not agent and ticket.created_by != request.user:
        return HttpResponseForbidden("Нет доступа к этой заявке.")

    comment_form = CommentForm()
    assign_form = AssignForm(instance=ticket) if agent else None
    update_form = AgentUpdateForm(instance=ticket) if agent else None

    return render(
        request,
        "tickets/ticket_detail.html",
        {
            "ticket": ticket,
            "comments": ticket.comments.select_related("author").all(),
            "comment_form": comment_form,
            "assign_form": assign_form,
            "update_form": update_form,
            "is_agent": agent,
        },
    )


@login_required
def add_comment(
    request: HttpRequest, pk: int
) -> HttpResponseForbidden | HttpResponseRedirect:
    ticket = get_object_or_404(Ticket, pk=pk)
    agent = is_agent(request.user)

    if not agent and ticket.created_by != request.user:
        return HttpResponseForbidden()

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.ticket = ticket
            comment.author = request.user
            comment.save()
            messages.success(request, "Комментарий добавлен.")
    return redirect("ticket_detail", pk=pk)


@require_agent
def change_status(
    request: HttpRequest, pk: int, new_status: str
) -> HttpResponseRedirect:
    if request.method != "POST":
        return redirect("ticket_detail", pk=pk)

    ticket = get_object_or_404(Ticket, pk=pk)
    allowed = [s for s, _ in ticket.allowed_next_statuses]

    if new_status not in allowed:
        messages.error(request, "Недопустимый переход статуса.")
        return redirect("ticket_detail", pk=pk)

    ticket.status = new_status
    ticket.save(update_fields=["status", "updated_at"])
    messages.success(request, f"Статус изменён на «{ticket.status_label}».")
    return redirect("ticket_detail", pk=pk)


@require_agent
def assign_ticket(request: HttpRequest, pk: int) -> HttpResponseRedirect:
    if request.method != "POST":
        return redirect("ticket_detail", pk=pk)

    ticket = get_object_or_404(Ticket, pk=pk)
    form = AssignForm(request.POST, instance=ticket)
    if form.is_valid():
        form.save()
        messages.success(request, "Исполнитель назначен.")
    else:
        messages.error(request, "Ошибка назначения исполнителя.")
    return redirect("ticket_detail", pk=pk)


@require_agent
def update_ticket(request: HttpRequest, pk: int) -> HttpResponseRedirect:
    if request.method != "POST":
        return redirect("ticket_detail", pk=pk)

    ticket = get_object_or_404(Ticket, pk=pk)
    form = AgentUpdateForm(request.POST, instance=ticket)
    if form.is_valid():
        form.save()
        messages.success(request, "Заявка обновлена.")
    else:
        messages.error(request, "Ошибка обновления заявки.")
    return redirect("ticket_detail", pk=pk)
