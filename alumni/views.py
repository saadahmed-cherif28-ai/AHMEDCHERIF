from datetime import timedelta
from statistics import median

from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Count, F, Min, Q
from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import AlumniProfileForm, ContactRequestForm, ValidationDecisionForm
from .models import (
	AlumniProfile,
	AppUser,
	AuditLog,
	Consent,
	ContactRequest,
	Notification,
	ProfileView,
	ValidationReview,
)


class RoleLoginView(LoginView):
	def get_success_url(self):
		if self.request.user.role == AppUser.Role.ALUMNI:
			return reverse("alumni:alumni-dashboard")
		if self.request.user.role == AppUser.Role.DIRECTION:
			return reverse("alumni:direction-dashboard")
		if self.request.user.role == AppUser.Role.SERVICE_ALUMNI:
			return reverse("alumni:service-queue")
		if self.request.user.role == AppUser.Role.STUDENT:
			return reverse("alumni:student-suggestions")
		return reverse("alumni:hello")


def hello(request):
	return render(request, "alumni/hello.html")


@login_required
def alumni_dashboard(request):
	if request.user.role not in (AppUser.Role.ALUMNI, AppUser.Role.DIRECTION):
		raise PermissionDenied
	profile = AlumniProfile.objects.filter(user=request.user).first()
	profile_views = profile.profile_views.select_related("viewer_user") if profile else ProfileView.objects.none()
	contact_requests = profile.contact_requests.select_related("student_user") if profile else ContactRequest.objects.none()
	return render(
		request,
		"alumni/alumni_dashboard.html",
		{
			"profile": profile,
			"profile_views": profile_views[:20],
			"view_count": profile_views.count(),
			"contact_requests": contact_requests[:10],
		},
	)


def public_profile(request, profile_id):
	profile = get_object_or_404(
		AlumniProfile.objects.select_related("study_program", "location").prefetch_related("experiences"),
		pk=profile_id,
		profile_status=AlumniProfile.ProfileStatus.VALIDATED,
		published_at__isnull=False,
		consents__purpose="annuaire_alumni",
		consents__revoked_at__isnull=True,
	)
	if not request.user.is_authenticated or request.user != profile.user:
		ProfileView.objects.create(
			alumni_profile=profile,
			viewer_user=request.user if request.user.is_authenticated else None,
		)
	return render(request, "alumni/public_profile.html", {"profile": profile})


@login_required
def student_suggestions(request):
	if request.user.role not in (AppUser.Role.STUDENT, AppUser.Role.DIRECTION):
		raise PermissionDenied
	profiles = AlumniProfile.objects.filter(
		profile_status=AlumniProfile.ProfileStatus.VALIDATED,
		published_at__isnull=False,
		consents__purpose="annuaire_alumni",
		consents__revoked_at__isnull=True,
	).select_related("study_program", "location").order_by("-last_confirmed_at", "last_name").distinct()
	query = request.GET.get("q", "").strip()
	if query:
		profiles = profiles.filter(
			Q(first_name__icontains=query)
			| Q(last_name__icontains=query)
			| Q(study_program__name__icontains=query)
		)
	return render(
		request,
		"alumni/student_suggestions.html",
		{"profiles": profiles, "query": query},
	)


@login_required
def alumni_profile(request):
	if request.user.role != AppUser.Role.ALUMNI:
		raise PermissionDenied

	profile = AlumniProfile.objects.filter(user=request.user).first()
	active_consent = (
		Consent.objects.filter(
			alumni_profile=profile,
			purpose="annuaire_alumni",
			revoked_at__isnull=True,
		).exists()
		if profile
		else False
	)
	if request.method == "POST":
		form = AlumniProfileForm(request.POST, instance=profile)
		if form.is_valid():
			with transaction.atomic():
				profile = form.save(commit=False)
				profile.user = request.user
				profile.profile_status = AlumniProfile.ProfileStatus.PENDING
				profile.submitted_at = timezone.now()
				profile.save()
				consent = Consent.objects.filter(
					alumni_profile=profile,
					purpose="annuaire_alumni",
					revoked_at__isnull=True,
				).first()
				if consent is None:
					consent = Consent.objects.create(
						alumni_profile=profile,
						purpose="annuaire_alumni",
						policy_version="2026-01",
						accepted_at=timezone.now(),
					)
				AuditLog.objects.create(
					actor_user=request.user,
					alumni_profile=profile,
					action="profile_submitted",
					details="Profil soumis avec consentement actif pour l’annuaire.",
				)
			return redirect("alumni:profile")
	else:
		form = AlumniProfileForm(
			instance=profile,
			initial={"consent_annuaire": active_consent},
		)

	return render(
		request,
		"alumni/profile_form.html",
		{"form": form, "profile": profile},
	)


@login_required
def service_validation_queue(request):
	if request.user.role not in (AppUser.Role.SERVICE_ALUMNI, AppUser.Role.DIRECTION):
		raise PermissionDenied
	profiles = AlumniProfile.objects.filter(
		profile_status__in=(
			AlumniProfile.ProfileStatus.PENDING,
			AlumniProfile.ProfileStatus.CORRECTION_REQUESTED,
		)
	).select_related("user", "study_program", "location")
	return render(request, "alumni/service_queue.html", {"profiles": profiles})


@login_required
def service_review_profile(request, profile_id):
	if request.user.role not in (AppUser.Role.SERVICE_ALUMNI, AppUser.Role.DIRECTION):
		raise PermissionDenied
	profile = AlumniProfile.objects.select_related("user", "study_program", "location").get(
		pk=profile_id
	)
	consent_active = profile.consents.filter(
		purpose="annuaire_alumni", revoked_at__isnull=True
	).exists()
	if request.method == "POST":
		form = ValidationDecisionForm(request.POST)
		if form.is_valid():
			decision = form.cleaned_data["decision"]
			if decision == ValidationReview.Decision.APPROVED and not consent_active:
				form.add_error(
					"decision",
					"Un profil ne peut être publié qu’avec un consentement actif.",
				)
				return render(
					request,
					"alumni/service_review.html",
					{"profile": profile, "form": form, "consent_active": consent_active},
				)
			review = form.save(commit=False)
			review.alumni_profile = profile
			review.reviewer_user = request.user
			review.save()
			if decision == ValidationReview.Decision.APPROVED:
				profile.profile_status = AlumniProfile.ProfileStatus.VALIDATED
				profile.published_at = timezone.now()
				notification_type = Notification.Type.PROFILE_VALIDATED
			else:
				profile.profile_status = (
					AlumniProfile.ProfileStatus.CORRECTION_REQUESTED
					if decision == ValidationReview.Decision.CORRECTION_REQUESTED
					else AlumniProfile.ProfileStatus.REJECTED
				)
				profile.published_at = None
				notification_type = Notification.Type.CORRECTION_REQUESTED
			profile.save(update_fields=("profile_status", "published_at"))
			Notification.objects.create(
				recipient_user=profile.user,
				alumni_profile=profile,
				type=notification_type,
			)
			AuditLog.objects.create(
				actor_user=request.user,
				alumni_profile=profile,
				validation_review=review,
				action="profile_reviewed",
				details=review.comment,
			)
			return redirect("alumni:service-queue")
	else:
		form = ValidationDecisionForm()
	return render(
		request,
		"alumni/service_review.html",
		{"profile": profile, "form": form, "consent_active": consent_active},
	)


@login_required
def student_directory(request):
	if request.user.role not in (AppUser.Role.STUDENT, AppUser.Role.DIRECTION):
		raise PermissionDenied
	profiles = AlumniProfile.objects.filter(
		profile_status=AlumniProfile.ProfileStatus.VALIDATED,
		published_at__isnull=False,
		consents__purpose="annuaire_alumni",
		consents__revoked_at__isnull=True,
	).select_related("study_program", "location").distinct()
	query = request.GET.get("q", "").strip()
	program = request.GET.get("program", "").strip()
	city = request.GET.get("city", "").strip()
	if query:
		profiles = profiles.filter(
			Q(first_name__icontains=query)
			| Q(last_name__icontains=query)
			| Q(study_program__name__icontains=query)
		)
	if program:
		profiles = profiles.filter(study_program_id=program)
	if city:
		profiles = profiles.filter(location__city__icontains=city)
	return render(
		request,
		"alumni/student_directory.html",
		{
			"profiles": profiles,
			"query": query,
			"programs": AlumniProfile.objects.values_list(
				"study_program_id", "study_program__name"
			).distinct(),
			"selected_program": program,
			"city": city,
		},
	)


@login_required
def student_contact(request, profile_id):
	if request.user.role not in (AppUser.Role.STUDENT, AppUser.Role.DIRECTION):
		raise PermissionDenied
	profile = AlumniProfile.objects.filter(
		pk=profile_id,
		profile_status=AlumniProfile.ProfileStatus.VALIDATED,
		published_at__isnull=False,
		consents__purpose="annuaire_alumni",
		consents__revoked_at__isnull=True,
	).select_related("study_program", "location").first()
	if profile is None:
		raise PermissionDenied
	if request.method == "POST":
		form = ContactRequestForm(request.POST)
		if form.is_valid():
			contact = form.save(commit=False)
			contact.student_user = request.user
			contact.alumni_profile = profile
			contact.save()
			Notification.objects.create(
				recipient_user=profile.user,
				alumni_profile=profile,
				type=Notification.Type.CONTACT_REQUEST,
			)
			return redirect("alumni:student-directory")
	else:
		form = ContactRequestForm()
	return render(
		request,
		"alumni/student_contact.html",
		{"profile": profile, "form": form},
	)


def _direction_only(request):
	if request.user.role != AppUser.Role.DIRECTION:
		raise PermissionDenied


@login_required
def direction_profiles(request):
	_direction_only(request)
	profiles = AlumniProfile.objects.select_related("study_program", "location").order_by(
		"last_name", "first_name"
	)
	return render(request, "alumni/direction_profiles.html", {"profiles": profiles})


@login_required
def direction_validations(request):
	_direction_only(request)
	reviews = ValidationReview.objects.select_related(
		"alumni_profile", "reviewer_user"
	).order_by("-created_at")
	return render(request, "alumni/direction_validations.html", {"reviews": reviews})


@login_required
def direction_statistics(request):
	_direction_only(request)
	profiles = AlumniProfile.objects.all()
	total_profiles = profiles.count()
	complete_profiles = profiles.filter(
		experiences__isnull=False,
		consents__purpose="annuaire_alumni",
		consents__revoked_at__isnull=True,
	).distinct().count()
	status_counts = dict(
		profiles.values("profile_status")
		.annotate(total=Count("id"))
		.values_list("profile_status", "total")
	)
	return render(
		request,
		"alumni/direction_statistics.html",
		{
			"total_profiles": total_profiles,
			"complete_profiles": complete_profiles,
			"completeness_percent": round(complete_profiles * 100 / total_profiles)
			if total_profiles
			else 0,
			"status_counts": status_counts,
			"reviews_count": ValidationReview.objects.count(),
			"contacts_count": ContactRequest.objects.count(),
		},
	)


@login_required
def direction_dashboard(request):
	if request.user.role != AppUser.Role.DIRECTION:
		raise PermissionDenied

	now = timezone.now()
	profiles = AlumniProfile.objects.all()
	total_profiles = profiles.count()
	complete_profiles = profiles.filter(
		experiences__isnull=False,
		consents__purpose="annuaire_alumni",
		consents__revoked_at__isnull=True,
	).distinct().count()
	fresh_profiles = profiles.filter(
		last_confirmed_at__gte=now - timedelta(days=365)
	).count()

	validation_durations = [
		(created_at - submitted_at).total_seconds() / 86400
		for submitted_at, created_at in ValidationReview.objects.filter(
			decision=ValidationReview.Decision.APPROVED,
			alumni_profile__submitted_at__isnull=False,
			created_at__gte=F("alumni_profile__submitted_at"),
		)
		.values("alumni_profile_id", "alumni_profile__submitted_at")
		.annotate(first_approval=Min("created_at"))
		.values_list("alumni_profile__submitted_at", "first_approval")
	]
	median_validation_days = (
		round(median(validation_durations), 1) if validation_durations else None
	)
	status_counts = dict(
		profiles.values_list("profile_status")
		.annotate(total=Count("id"))
		.values_list("profile_status", "total")
	)
	status_breakdown = [
		{
			"label": label,
			"count": status_counts.get(value, 0),
			"width_percent": (
				round(status_counts.get(value, 0) * 100 / total_profiles)
				if total_profiles
				else 0
			),
		}
		for value, label in AlumniProfile.ProfileStatus.choices
	]
	recent_profiles = profiles.select_related("study_program").order_by(
		F("submitted_at").desc(nulls_last=True), "-id"
	)[:5]

	return render(
		request,
		"alumni/direction_dashboard.html",
		{
			"total_profiles": total_profiles,
			"complete_profiles": complete_profiles,
			"completeness_percent": (
				round(complete_profiles * 100 / total_profiles)
				if total_profiles
				else 0
			),
			"fresh_profiles": fresh_profiles,
			"freshness_percent": (
				round(fresh_profiles * 100 / total_profiles) if total_profiles else 0
			),
			"median_validation_days": median_validation_days,
			"pending_profiles": profiles.filter(
				profile_status=AlumniProfile.ProfileStatus.PENDING
			).count(),
			"status_breakdown": status_breakdown,
			"recent_profiles": recent_profiles,
		},
	)
