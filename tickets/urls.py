from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("tickets/", views.ticket_list, name="ticket_list"),
    path("tickets/create/", views.ticket_create, name="ticket_create"),
    path("tickets/<int:pk>/", views.ticket_detail, name="ticket_detail"),
    path("tickets/<int:pk>/comment/", views.add_comment, name="add_comment"),
    path(
        "tickets/<int:pk>/change-status/<str:new_status>/",
        views.change_status,
        name="change_status",
    ),
    path("tickets/<int:pk>/assign/", views.assign_ticket, name="assign_ticket"),
    path("tickets/<int:pk>/update/", views.update_ticket, name="update_ticket"),
]
