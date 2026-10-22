from io import StringIO

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .models import (
	AlumniProfile,
	AppUser,
	Consent,
	ContactRequest,
	ValidationReview,
	ProfileView,
)


class HelloPageTests(TestCase):
	def test_homepage_displays_alumni_landing_page(self):
		response = self.client.get("/")

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Alumni EIGSICA")
		self.assertContains(response, "Faire vivre le réseau alumni")


class DemoDataTests(TestCase):
	def test_seed_demo_creates_related_records_and_is_repeatable(self):
		output = StringIO()

		call_command("seed_demo", stdout=output)

		self.assertEqual(AlumniProfile.objects.count(), 2)
		self.assertEqual(AppUser.objects.count(), 5)
		self.assertEqual(Consent.objects.count(), 2)
		self.assertEqual(ContactRequest.objects.count(), 1)
		self.assertIn("Aïssata Fall", output.getvalue())

		call_command("seed_demo", stdout=StringIO())

		self.assertEqual(AlumniProfile.objects.count(), 2)
		self.assertEqual(AppUser.objects.count(), 5)


class DirectionDashboardTests(TestCase):
	@classmethod
	def setUpTestData(cls):
		call_command("seed_demo")
		cls.direction_user = AppUser.objects.get(email="direction@example.test")
		cls.direction_user.set_password("temporary-test-password")
		cls.direction_user.save()
		cls.service_user = AppUser.objects.get(
			email="service.alumni@example.test"
		)

	def test_anonymous_user_is_redirected_to_login(self):
		response = self.client.get("/direction/")

		self.assertRedirects(response, "/connexion/?next=/direction/")

	def test_direction_sees_dashboard_metrics(self):
		self.client.force_login(self.direction_user)
		profile = AlumniProfile.objects.get(student_number="EIG-2019-014")
		ValidationReview.objects.create(
			alumni_profile=profile,
			reviewer_user=self.service_user,
			decision=ValidationReview.Decision.APPROVED,
			comment="Deuxième vérification de démonstration.",
		)

		response = self.client.get("/direction/")

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Tableau de bord")
		self.assertEqual(response.context["total_profiles"], 2)
		self.assertEqual(response.context["complete_profiles"], 1)
		self.assertEqual(response.context["completeness_percent"], 50)
		self.assertEqual(response.context["fresh_profiles"], 1)
		self.assertEqual(response.context["freshness_percent"], 50)
		self.assertEqual(response.context["median_validation_days"], 1.0)

	def test_non_direction_user_is_forbidden(self):
		self.client.force_login(self.service_user)

		response = self.client.get("/direction/")

		self.assertEqual(response.status_code, 403)

	def test_direction_can_sign_in_with_email_and_password(self):
		response = self.client.post(
			"/connexion/",
			{
				"username": "direction@example.test",
				"password": "temporary-test-password",
			},
		)

		self.assertRedirects(response, "/direction/")

	def test_direction_navigation_pages_are_available(self):
		self.client.force_login(self.direction_user)

		for route, text in (
			("alumni:direction-profiles", "Profils alumni"),
			("alumni:direction-validations", "Validations"),
			("alumni:direction-statistics", "Statistiques"),
		):
			response = self.client.get(reverse(route))
			self.assertEqual(response.status_code, 200)
			self.assertContains(response, text)


class AlumniProfileTests(TestCase):
	@classmethod
	def setUpTestData(cls):
		call_command("seed_demo")
		cls.alumni_user = AppUser.objects.get(email="aissata.fall@example.test")
		cls.program = cls.alumni_user.alumni_profile.study_program

	def test_alumni_can_view_existing_profile(self):
		self.client.force_login(self.alumni_user)
		response = self.client.get(reverse("alumni:profile"))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Mon profil alumni")
		self.assertContains(response, "Aïssata")

	def test_profile_requires_consent_to_be_submitted(self):
		self.client.force_login(self.alumni_user)
		profile = self.alumni_user.alumni_profile
		response = self.client.post(
			reverse("alumni:profile"),
			{
				"student_number": profile.student_number,
				"first_name": profile.first_name,
				"last_name": profile.last_name,
				"graduation_year": profile.graduation_year,
				"study_program": str(self.program.pk),
				"employment_status": profile.employment_status,
			},
		)

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "consentement à l’annuaire est obligatoire")

	def test_profile_submission_sets_pending_status_and_records_consent(self):
		self.client.force_login(self.alumni_user)
		profile = self.alumni_user.alumni_profile
		response = self.client.post(
			reverse("alumni:profile"),
			{
				"student_number": profile.student_number,
				"first_name": profile.first_name,
				"last_name": profile.last_name,
				"graduation_year": profile.graduation_year,
				"study_program": str(self.program.pk),
				"employment_status": profile.employment_status,
				"consent_annuaire": "on",
			},
		)

		profile.refresh_from_db()
		self.assertRedirects(response, reverse("alumni:profile"))
		self.assertEqual(profile.profile_status, AlumniProfile.ProfileStatus.PENDING)
		self.assertTrue(profile.consents.filter(purpose="annuaire_alumni", revoked_at__isnull=True).exists())

	def test_direction_cannot_access_alumni_profile_form(self):
		direction = AppUser.objects.get(email="direction@example.test")
		self.client.force_login(direction)

		response = self.client.get(reverse("alumni:profile"))

		self.assertEqual(response.status_code, 403)

	def test_alumni_can_sign_in_and_is_sent_to_profile(self):
		self.alumni_user.set_password("temporary-alumni-password")
		self.alumni_user.save()

		response = self.client.post(
			"/connexion/",
			{
				"username": self.alumni_user.email,
				"password": "temporary-alumni-password",
			},
		)

		self.assertRedirects(response, reverse("alumni:alumni-dashboard"))


class ServiceAndStudentTests(TestCase):
	@classmethod
	def setUpTestData(cls):
		call_command("seed_demo")
		cls.service_user = AppUser.objects.get(email="service.alumni@example.test")
		cls.student_user = AppUser.objects.get(email="aminata.ba@example.test")
		cls.cheikh = AlumniProfile.objects.get(student_number="EIG-2021-027")
		cls.aissata = AlumniProfile.objects.get(student_number="EIG-2019-014")

	def test_service_login_redirects_to_validation_queue(self):
		response = self.client.post(
			"/connexion/",
			{"username": self.service_user.email, "password": "demo1234"},
		)

		self.assertRedirects(response, reverse("alumni:service-queue"))

	def test_service_can_request_correction(self):
		self.client.force_login(self.service_user)
		response = self.client.post(
			reverse("alumni:service-review", args=[self.cheikh.pk]),
			{
				"decision": ValidationReview.Decision.CORRECTION_REQUESTED,
				"comment": "Merci de préciser le secteur.",
			},
		)

		self.assertRedirects(response, reverse("alumni:service-queue"))
		self.cheikh.refresh_from_db()
		self.assertEqual(
			self.cheikh.profile_status,
			AlumniProfile.ProfileStatus.CORRECTION_REQUESTED,
		)

	def test_service_cannot_publish_without_active_consent(self):
		self.client.force_login(self.service_user)
		response = self.client.post(
			reverse("alumni:service-review", args=[self.cheikh.pk]),
			{"decision": ValidationReview.Decision.APPROVED, "comment": "OK"},
		)

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "consentement actif")

	def test_student_can_search_published_profiles(self):
		self.client.force_login(self.student_user)
		response = self.client.get(reverse("alumni:student-directory"), {"q": "Aïssata"})

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Aïssata Fall")
		self.assertNotContains(response, "Cheikh Ndiaye")

	def test_student_login_redirects_to_suggestions(self):
		response = self.client.post(
			"/connexion/",
			{"username": self.student_user.email, "password": "demo1234"},
		)

		self.assertRedirects(response, reverse("alumni:student-suggestions"))

	def test_student_can_send_contact_request(self):
		self.client.force_login(self.student_user)
		response = self.client.post(
			reverse("alumni:student-contact", args=[self.aissata.pk]),
			{"message": "Bonjour, pouvez-vous partager votre parcours ?"},
		)

		self.assertRedirects(response, reverse("alumni:student-directory"))
		self.assertTrue(
			ContactRequest.objects.filter(
				student_user=self.student_user,
				alumni_profile=self.aissata,
			).exists()
		)

	def test_public_profile_records_authenticated_viewer(self):
		self.client.force_login(self.student_user)
		response = self.client.get(reverse("alumni:public-profile", args=[self.aissata.pk]))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Aïssata Fall")
		self.assertTrue(
			ProfileView.objects.filter(
				alumni_profile=self.aissata,
				viewer_user=self.student_user,
			).exists()
		)

class AlumniDashboardTests(TestCase):
	@classmethod
	def setUpTestData(cls):
		call_command("seed_demo")
		cls.alumni_user = AppUser.objects.get(email="aissata.fall@example.test")
		cls.student_user = AppUser.objects.get(email="aminata.ba@example.test")

	def test_alumni_dashboard_shows_profile_viewers(self):
		profile = self.alumni_user.alumni_profile
		ProfileView.objects.create(alumni_profile=profile, viewer_user=self.student_user)
		self.client.force_login(self.alumni_user)

		response = self.client.get(reverse("alumni:alumni-dashboard"))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Consultations du profil")
		self.assertContains(response, self.student_user.email)

	def test_direction_can_access_all_role_spaces(self):
		direction = AppUser.objects.get(email="direction@example.test")
		self.client.force_login(direction)

		for route_name in (
			"alumni:alumni-dashboard",
			"alumni:service-queue",
			"alumni:student-suggestions",
			"alumni:student-directory",
		):
			with self.subTest(route=route_name):
				response = self.client.get(reverse(route_name))
				self.assertEqual(response.status_code, 200)
