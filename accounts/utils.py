from django.urls import reverse


def get_user_dashboard_url(user):
    if user.role == user.Role.ADMIN:
        return reverse("admin_dashboard")

    if user.role == user.Role.COURIER:
        return reverse("courier_dashboard")

    return reverse("profile")