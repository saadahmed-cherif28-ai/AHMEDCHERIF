from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from .models import AlumniProfile, AppUser, AuditLog
from .verification import DISCREPANCY_FOUND, UNMATCHED, VERIFIED, verifier


class VerificationLogicTests(TestCase):
	@classmethod
	def setUpTestData(cls):
		call_command("seed_demo", stdout=StringIO())
		cls.profil = AlumniProfile.objects.get(student_number="EIG-2019-014")

	def test_concordance_complete(self):
		texte = (
			"Aïssata Fall. Systèmes d'information, promotion 2019. "
			"Analyste de données chez Atelier Numérique Démo."
		)
		resultat = verifier(self.profil, texte)
		self.assertEqual(resultat["statut"], VERIFIED)
		self.assertEqual(resultat["score"], 100)

	def test_entreprise_differente_demande_verification(self):
		texte = (
			"Aïssata Fall. Systèmes d'information, promotion 2019. "
			"Analyste de données chez une autre entreprise."
		)
		resultat = verifier(self.profil, texte)
		self.assertEqual(resultat["statut"], DISCREPANCY_FOUND)
		self.assertNotEqual(resultat["recommandation"], "Concordance complète")

	def test_personne_differente_non_concordant(self):
		texte = "Jean Dupont. Ingénieur en génie civil, promotion 2008."
		resultat = verifier(self.profil, texte)
		self.assertEqual(resultat["statut"], UNMATCHED)


class VerificationViewTests(TestCase):
	@classmethod
	def setUpTestData(cls):
		call_command("seed_demo", stdout=StringIO())
		cls.profil = AlumniProfile.objects.get(student_number="EIG-2019-014")
		cls.service = AppUser.objects.get(email="service.alumni@example.test")
		cls.alumni = AppUser.objects.get(email="aissata.fall@example.test")
		cls.url = f"/service/profil/{cls.profil.id}/verifier/"

	def test_alumni_ne_peut_pas_ouvrir_la_page(self):
		self.client.force_login(self.alumni)
		self.assertEqual(self.client.get(self.url).status_code, 403)

	def test_service_ouvre_la_page(self):
		self.client.force_login(self.service)
		self.assertEqual(self.client.get(self.url).status_code, 200)

	def test_resultat_trace_sans_enregistrer_le_texte(self):
		self.client.force_login(self.service)
		texte_secret = "Texte LinkedIn unique XYZ-123"
		response = self.client.post(self.url, {"linkedin_text": texte_secret})
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Résultat")

		log = AuditLog.objects.filter(action="linkedin_verification").latest("created_at")
		self.assertIn("%", log.details)
		self.assertNotIn("XYZ-123", log.details)

	def test_texte_vide_refuse(self):
		self.client.force_login(self.service)
		response = self.client.post(self.url, {"linkedin_text": "   "})
		self.assertContains(response, "Collez le texte du profil LinkedIn")
