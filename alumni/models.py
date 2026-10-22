import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import F, Q


class AppUser(AbstractUser):
	class Role(models.TextChoices):
		ALUMNI = "ALUMNI", "Alumni"
		STUDENT = "STUDENT", "Étudiant"
		SERVICE_ALUMNI = "SERVICE_ALUMNI", "Service Alumni"
		DIRECTION = "DIRECTION", "Direction"
		ADMIN = "ADMIN", "Administration"

	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	username = None
	first_name = None
	last_name = None
	email = models.EmailField(unique=True)
	role = models.CharField(max_length=24, choices=Role.choices)
	created_at = models.DateTimeField(auto_now_add=True)

	USERNAME_FIELD = "email"
	REQUIRED_FIELDS = []

	def __str__(self):
		return self.email


class StudyProgram(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	name = models.CharField(max_length=150, unique=True)

	def __str__(self):
		return self.name


class Location(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	country_code = models.CharField(max_length=2)
	region = models.CharField(max_length=100, blank=True)
	city = models.CharField(max_length=100)

	class Meta:
		constraints = [
			models.UniqueConstraint(
				fields=("country_code", "region", "city"),
				name="uniq_location_country_region_city",
			)
		]

	def __str__(self):
		return f"{self.city}, {self.country_code}"


class AlumniProfile(models.Model):
	class EmploymentStatus(models.TextChoices):
		EMPLOYED = "employed", "En poste"
		SEEKING = "seeking", "En recherche"
		STUDYING = "studying", "En études"
		OTHER = "other", "Autre"

	class ProfileStatus(models.TextChoices):
		DRAFT = "draft", "Brouillon"
		PENDING = "pending", "En attente"
		CORRECTION_REQUESTED = "correction_requested", "Correction demandée"
		VALIDATED = "validated", "Validé"
		REJECTED = "rejected", "Refusé"

	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	user = models.OneToOneField(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="alumni_profile",
	)
	student_number = models.CharField(max_length=40, unique=True)
	first_name = models.CharField(max_length=100)
	last_name = models.CharField(max_length=100)
	graduation_year = models.PositiveSmallIntegerField()
	study_program = models.ForeignKey(
		StudyProgram,
		on_delete=models.PROTECT,
		related_name="alumni_profiles",
	)
	location = models.ForeignKey(
		Location,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name="alumni_profiles",
	)
	employment_status = models.CharField(
		max_length=12,
		choices=EmploymentStatus.choices,
	)
	profile_status = models.CharField(
		max_length=24,
		choices=ProfileStatus.choices,
		default=ProfileStatus.DRAFT,
	)
	submitted_at = models.DateTimeField(null=True, blank=True)
	last_confirmed_at = models.DateTimeField(null=True, blank=True)
	published_at = models.DateTimeField(null=True, blank=True)

	def __str__(self):
		return f"{self.first_name} {self.last_name} ({self.student_number})"


class ProfessionalExperience(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	alumni_profile = models.ForeignKey(
		AlumniProfile,
		on_delete=models.CASCADE,
		related_name="experiences",
	)
	company = models.CharField(max_length=150)
	job_title = models.CharField(max_length=150)
	sector = models.CharField(max_length=100, blank=True)
	start_date = models.DateField()
	end_date = models.DateField(null=True, blank=True)

	class Meta:
		constraints = [
			models.CheckConstraint(
				condition=Q(end_date__isnull=True) | Q(end_date__gte=F("start_date")),
				name="experience_end_after_start",
			)
		]

	def __str__(self):
		return f"{self.job_title} - {self.company}"


class Consent(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	alumni_profile = models.ForeignKey(
		AlumniProfile,
		on_delete=models.CASCADE,
		related_name="consents",
	)
	purpose = models.CharField(max_length=60)
	policy_version = models.CharField(max_length=40)
	accepted_at = models.DateTimeField()
	revoked_at = models.DateTimeField(null=True, blank=True)

	class Meta:
		constraints = [
			models.UniqueConstraint(
				fields=("alumni_profile", "purpose"),
				condition=Q(revoked_at__isnull=True),
				name="uniq_active_consent_purpose",
			),
			models.CheckConstraint(
				condition=Q(revoked_at__isnull=True) | Q(revoked_at__gte=F("accepted_at")),
				name="consent_revoked_after_acceptance",
			),
		]

	def __str__(self):
		return f"{self.purpose} - {self.alumni_profile}"


class ValidationReview(models.Model):
	class Decision(models.TextChoices):
		APPROVED = "approved", "Validé"
		CORRECTION_REQUESTED = "correction_requested", "Correction demandée"
		REJECTED = "rejected", "Refusé"

	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	alumni_profile = models.ForeignKey(
		AlumniProfile,
		on_delete=models.CASCADE,
		related_name="reviews",
	)
	reviewer_user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.PROTECT,
		related_name="validation_reviews",
	)
	decision = models.CharField(max_length=24, choices=Decision.choices)
	comment = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.get_decision_display()} - {self.alumni_profile}"


class ContactRequest(models.Model):
	class Status(models.TextChoices):
		PENDING = "pending", "En attente"
		ACCEPTED = "accepted", "Acceptée"
		DECLINED = "declined", "Refusée"

	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	student_user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.PROTECT,
		related_name="contact_requests_sent",
	)
	alumni_profile = models.ForeignKey(
		AlumniProfile,
		on_delete=models.CASCADE,
		related_name="contact_requests",
	)
	status = models.CharField(
		max_length=12,
		choices=Status.choices,
		default=Status.PENDING,
	)
	message = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"Demande de {self.student_user} vers {self.alumni_profile}"


class Notification(models.Model):
	class Type(models.TextChoices):
		PROFILE_VALIDATED = "profile_validated", "Profil validé"
		CORRECTION_REQUESTED = "correction_requested", "Correction demandée"
		CONTACT_REQUEST = "contact_request", "Demande de contact"

	class Status(models.TextChoices):
		QUEUED = "queued", "En attente"
		SENT = "sent", "Envoyée"
		FAILED = "failed", "Échec"

	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	recipient_user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="notifications",
	)
	alumni_profile = models.ForeignKey(
		AlumniProfile,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name="notifications",
	)
	type = models.CharField(max_length=24, choices=Type.choices)
	status = models.CharField(
		max_length=12,
		choices=Status.choices,
		default=Status.QUEUED,
	)
	created_at = models.DateTimeField(auto_now_add=True)
	sent_at = models.DateTimeField(null=True, blank=True)

	def __str__(self):
		return f"{self.get_type_display()} pour {self.recipient_user}"


class AuditLog(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	actor_user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name="audit_entries",
	)
	alumni_profile = models.ForeignKey(
		AlumniProfile,
		on_delete=models.PROTECT,
		null=True,
		blank=True,
		related_name="audit_entries",
	)
	consent = models.ForeignKey(
		Consent,
		on_delete=models.PROTECT,
		null=True,
		blank=True,
		related_name="audit_entries",
	)
	experience = models.ForeignKey(
		ProfessionalExperience,
		on_delete=models.PROTECT,
		null=True,
		blank=True,
		related_name="audit_entries",
	)
	validation_review = models.ForeignKey(
		ValidationReview,
		on_delete=models.PROTECT,
		null=True,
		blank=True,
		related_name="audit_entries",
	)
	contact_request = models.ForeignKey(
		ContactRequest,
		on_delete=models.PROTECT,
		null=True,
		blank=True,
		related_name="audit_entries",
	)
	action = models.CharField(max_length=80)
	details = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		constraints = [
			models.CheckConstraint(
				condition=(
					Q(alumni_profile__isnull=False)
					| Q(consent__isnull=False)
					| Q(experience__isnull=False)
					| Q(validation_review__isnull=False)
					| Q(contact_request__isnull=False)
				),
				name="audit_log_has_target",
			)
		]

	def __str__(self):
		return f"{self.action} ({self.created_at:%Y-%m-%d})"


class ProfileView(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	alumni_profile = models.ForeignKey(
		AlumniProfile,
		on_delete=models.CASCADE,
		related_name="profile_views",
	)
	viewer_user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name="profile_views",
	)
	viewed_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ("-viewed_at",)

	def __str__(self):
		viewer = self.viewer_user.email if self.viewer_user else "Visiteur non connecté"
		return f"{self.alumni_profile} consulté par {viewer}"
