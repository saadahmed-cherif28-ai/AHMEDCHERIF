from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "alumni"

urlpatterns = [
    path("", views.hello, name="hello"),
    path(
        "connexion/",
        views.RoleLoginView.as_view(template_name="alumni/login.html"),
        name="login",
    ),
    path("deconnexion/", auth_views.LogoutView.as_view(next_page="alumni:hello"), name="logout"),
    path("alumni/", views.alumni_dashboard, name="alumni-dashboard"),
    path("profil/", views.alumni_profile, name="profile"),
    path("service/", views.service_validation_queue, name="service-queue"),
    path("service/profil/<uuid:profile_id>/", views.service_review_profile, name="service-review"),
    path("service/profil/<uuid:profile_id>/verifier/", views.service_linkedin_verification, name="service-linkedin-verification"),
    path("annuaire/", views.student_directory, name="student-directory"),
    path("suggestions/", views.student_suggestions, name="student-suggestions"),
    path("annuaire/profil/<uuid:profile_id>/", views.public_profile, name="public-profile"),
    path("annuaire/<uuid:profile_id>/contacter/", views.student_contact, name="student-contact"),
    path("direction/", views.direction_dashboard, name="direction-dashboard"),
    path("direction/profils/", views.direction_profiles, name="direction-profiles"),
    path("direction/validations/", views.direction_validations, name="direction-validations"),
    path("direction/statistiques/", views.direction_statistics, name="direction-statistics"),
]
