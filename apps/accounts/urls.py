from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "accounts"

urlpatterns = [
    path("utilisateurs/", views.user_list, name="user_list"),
    path("utilisateurs/ajouter/", views.user_create, name="user_create"),
    path("utilisateurs/<int:pk>/modifier/", views.user_edit, name="user_edit"),
    path("utilisateurs/<int:pk>/mot-de-passe/", views.user_password, name="user_password"),
    path("utilisateurs/<int:pk>/supprimer/", views.user_delete, name="user_delete"),
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("password-change/", auth_views.PasswordChangeView.as_view(
        template_name="registration/password_change.html",
        success_url="/accounts/password-change-done/"
    ), name="password_change"),
    path("password-change-done/", auth_views.PasswordChangeDoneView.as_view(
        template_name="registration/password_change_done.html"
    ), name="password_change_done"),
]
