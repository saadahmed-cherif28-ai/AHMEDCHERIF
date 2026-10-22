from django.contrib import admin

from .models import (
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


@admin.register(AppUser)
class AppUserAdmin(admin.ModelAdmin):
	list_display = ("email", "role", "is_active", "is_staff")
	list_filter = ("role", "is_active", "is_staff")
	search_fields = ("email",)


@admin.register(AlumniProfile)
class AlumniProfileAdmin(admin.ModelAdmin):
	list_display = ("first_name", "last_name", "student_number", "profile_status")
	list_filter = ("profile_status", "employment_status", "graduation_year")
	search_fields = ("first_name", "last_name", "student_number", "user__email")


admin.site.register(
	[
		AuditLog,
		Consent,
		ContactRequest,
		Location,
		Notification,
		ProfessionalExperience,
		StudyProgram,
		ValidationReview,
	]
)
