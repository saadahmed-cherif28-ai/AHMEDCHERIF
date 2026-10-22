from django import forms

from .models import AlumniProfile, ContactRequest, ValidationReview


class AlumniProfileForm(forms.ModelForm):
    consent_annuaire = forms.BooleanField(
        required=True,
        label="J’autorise l’utilisation de mon profil dans l’annuaire alumni.",
        error_messages={
            "required": "Le consentement à l’annuaire est obligatoire pour soumettre le profil."
        },
    )

    class Meta:
        model = AlumniProfile
        fields = (
            "student_number",
            "first_name",
            "last_name",
            "graduation_year",
            "study_program",
            "location",
            "employment_status",
        )
        labels = {
            "student_number": "Matricule étudiant",
            "first_name": "Prénom",
            "last_name": "Nom",
            "graduation_year": "Année de diplôme",
            "study_program": "Filière",
            "location": "Localisation",
            "employment_status": "Situation professionnelle",
        }
        widgets = {
            "graduation_year": forms.NumberInput(attrs={"min": 1900, "max": 2100}),
        }


class ValidationDecisionForm(forms.ModelForm):
    class Meta:
        model = ValidationReview
        fields = ("decision", "comment")
        labels = {"decision": "Décision", "comment": "Commentaire ou motif"}
        widgets = {"comment": forms.Textarea(attrs={"rows": 4})}


class ContactRequestForm(forms.ModelForm):
    class Meta:
        model = ContactRequest
        fields = ("message",)
        labels = {"message": "Message"}
        widgets = {"message": forms.Textarea(attrs={"rows": 5})}
