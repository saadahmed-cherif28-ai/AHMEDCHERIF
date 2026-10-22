from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from alumni.models import (
    AlumniProfile,
    AppUser,
    AuditLog,
    Consent,
    ContactRequest,
    Location,
    Notification,
    ProfessionalExperience,
    StudyProgram,
    ValidationReview,
)


class Command(BaseCommand):
    help = "Crée un petit jeu de données fictives pour tester l'application."
    demo_password = "demo1234"

    def handle(self, *args, **options):
        alumni_role = AppUser.Role.ALUMNI
        student_role = AppUser.Role.STUDENT
        service_role = AppUser.Role.SERVICE_ALUMNI

        aissata_user = self.get_demo_user("aissata.fall@example.test", alumni_role)
        cheikh_user = self.get_demo_user("cheikh.ndiaye@example.test", alumni_role)
        student_user = self.get_demo_user("aminata.ba@example.test", student_role)
        service_user = self.get_demo_user("service.alumni@example.test", service_role)
        direction_user = self.get_demo_user(
        	"direction@example.test", AppUser.Role.DIRECTION
        )

        program, _ = StudyProgram.objects.update_or_create(
            name="Systèmes d'information"
        )
        dakar, _ = Location.objects.update_or_create(
            country_code="SN",
            region="Dakar",
            city="Dakar",
        )
        thies, _ = Location.objects.update_or_create(
            country_code="SN",
            region="Thiès",
            city="Thiès",
        )

        now = timezone.now()
        aissata, _ = AlumniProfile.objects.update_or_create(
            user=aissata_user,
            defaults={
                "student_number": "EIG-2019-014",
                "first_name": "Aïssata",
                "last_name": "Fall",
                "graduation_year": 2019,
                "study_program": program,
                "location": dakar,
                "employment_status": AlumniProfile.EmploymentStatus.EMPLOYED,
                "profile_status": AlumniProfile.ProfileStatus.VALIDATED,
                "submitted_at": now - timedelta(days=2),
                "last_confirmed_at": now - timedelta(days=12),
                "published_at": now - timedelta(days=12),
            },
        )
        cheikh, _ = AlumniProfile.objects.update_or_create(
            user=cheikh_user,
            defaults={
                "student_number": "EIG-2021-027",
                "first_name": "Cheikh",
                "last_name": "Ndiaye",
                "graduation_year": 2021,
                "study_program": program,
                "location": thies,
                "employment_status": AlumniProfile.EmploymentStatus.SEEKING,
                "profile_status": AlumniProfile.ProfileStatus.CORRECTION_REQUESTED,
                "submitted_at": now - timedelta(days=405),
                "last_confirmed_at": now - timedelta(days=400),
                "published_at": None,
            },
        )

        current_experience, _ = ProfessionalExperience.objects.update_or_create(
            alumni_profile=aissata,
            company="Atelier Numérique Démo",
            job_title="Analyste de données",
            start_date=date(2023, 6, 1),
            defaults={"sector": "Numérique", "end_date": None},
        )
        past_experience, _ = ProfessionalExperience.objects.update_or_create(
            alumni_profile=cheikh,
            company="Cabinet Conseil Démo",
            job_title="Assistant systèmes",
            start_date=date(2022, 1, 10),
            defaults={"sector": "Conseil", "end_date": date(2024, 8, 31)},
        )

        aissata_consent, _ = Consent.objects.update_or_create(
            alumni_profile=aissata,
            purpose="annuaire_alumni",
            policy_version="2026-01",
            defaults={
                "accepted_at": now - timedelta(days=90),
                "revoked_at": None,
            },
        )
        cheikh_consent, _ = Consent.objects.update_or_create(
            alumni_profile=cheikh,
            purpose="annuaire_alumni",
            policy_version="2026-01",
            defaults={
                "accepted_at": now - timedelta(days=45),
                "revoked_at": now - timedelta(days=20),
            },
        )

        aissata_review, _ = ValidationReview.objects.update_or_create(
            alumni_profile=aissata,
            reviewer_user=service_user,
            decision=ValidationReview.Decision.APPROVED,
            defaults={"comment": "Profil vérifié et publié."},
        )
        ValidationReview.objects.filter(pk=aissata_review.pk).update(
            created_at=now - timedelta(days=1)
        )
        cheikh_review, _ = ValidationReview.objects.update_or_create(
            alumni_profile=cheikh,
            reviewer_user=service_user,
            decision=ValidationReview.Decision.CORRECTION_REQUESTED,
            defaults={"comment": "Merci de préciser le secteur de votre poste."},
        )
        ValidationReview.objects.filter(pk=cheikh_review.pk).update(
            created_at=now - timedelta(days=400)
        )

        contact_request = ContactRequest.objects.filter(
            student_user=student_user,
            alumni_profile=aissata,
        ).order_by("created_at").first()
        if contact_request is None:
            contact_request = ContactRequest.objects.create(
                student_user=student_user,
                alumni_profile=aissata,
                status=ContactRequest.Status.PENDING,
                message="Bonjour, pourriez-vous me parler de votre parcours en analyse de données ?",
            )
        notification = Notification.objects.filter(
            recipient_user=aissata_user,
            alumni_profile=aissata,
            type=Notification.Type.CONTACT_REQUEST,
        ).first()
        if notification is None:
            Notification.objects.create(
                recipient_user=aissata_user,
                alumni_profile=aissata,
                type=Notification.Type.CONTACT_REQUEST,
                status=Notification.Status.QUEUED,
            )
        AuditLog.objects.get_or_create(
            contact_request=contact_request,
            action="contact_request_created",
            defaults={
                "actor_user": student_user,
                "alumni_profile": aissata,
                "details": "Demande de démonstration créée.",
            },
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Données de démonstration prêtes : "
                f"{AlumniProfile.objects.count()} profils, "
                f"{ProfessionalExperience.objects.count()} expériences, "
                f"{Consent.objects.count()} consentements et "
                f"{ContactRequest.objects.count()} demande de contact."
            )
        )
        for profile in AlumniProfile.objects.select_related("user").order_by("student_number"):
            self.stdout.write(
                f"- {profile.first_name} {profile.last_name} "
                f"({profile.student_number}) : "
                f"{profile.get_profile_status_display()} - {profile.user.email}"
            )

    @staticmethod
    def get_demo_user(email, role):
        user, created = AppUser.objects.get_or_create(
            email=email,
            defaults={"role": role, "is_active": True},
        )
        user.role = role
        user.is_active = True
        if created or not user.has_usable_password():
            user.set_password(Command.demo_password)
        user.save()
        return user
