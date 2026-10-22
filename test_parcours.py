"""Vérifie le parcours complet du MVP, de la saisie du profil jusqu'au tableau de bord.

Lancer avec : python test_parcours.py
Chaque exécution crée des comptes de test avec un suffixe unique.
"""

import uuid

from sqlalchemy import select
from werkzeug.security import generate_password_hash

from app import app
from database import SessionLocal
from models import AlumniProfile, Consent, User

suffixe = uuid.uuid4().hex[:6]
resultats = []


def check(label, ok):
    resultats.append(bool(ok))
    print(("OK    " if ok else "ECHEC ") + label)


def creer_compte(email, role):
    with SessionLocal() as s:
        s.add(
            User(
                email=email,
                role=role,
                password_hash=generate_password_hash("test1234"),
            )
        )
        s.commit()


def connexion(email):
    client = app.test_client()
    client.post("/login", data={"email": email, "password": "test1234"})
    return client


def etat(email):
    """Renvoie le statut et la publication du profil, ou None s'il n'existe pas."""
    with SessionLocal() as s:
        user = s.scalar(select(User).where(User.email == email))
        profil = s.scalar(
            select(AlumniProfile).where(AlumniProfile.user_id == user.id)
        )
        if profil is None:
            return None
        return {
            "id": profil.id,
            "status": profil.status,
            "is_published": profil.is_published,
        }


def consentement_actif(email):
    profil = etat(email)
    if profil is None:
        return False
    with SessionLocal() as s:
        return (
            s.scalar(
                select(Consent).where(
                    Consent.alumni_id == profil["id"], Consent.revoked_at.is_(None)
                )
            )
            is not None
        )


email_a = f"alumni.a.{suffixe}@example.com"
email_b = f"alumni.b.{suffixe}@example.com"
nom = f"Nom{suffixe}"

donnees_a = {
    "first_name": "Test",
    "last_name": nom,
    "graduation_year": "2022",
    "program": "Informatique",
    "city": "Casablanca",
    "country": "Maroc",
    "email": email_a,
}
donnees_b = {**donnees_a, "city": "Rabat", "email": email_b}

creer_compte(email_a, "ALUMNI")
creer_compte(email_b, "ALUMNI")

print("--- Étape 5 : consentement ---")
ca = connexion(email_a)
ca.post("/profil", data=donnees_a)
check("sans case cochée, rien n'est enregistré", etat(email_a) is None)

print("--- Étape 4 et 5 : saisie avec consentement ---")
r = ca.post("/profil", data={**donnees_a, "consent": "on"})
check("saisie avec consentement enregistrée", r.status_code == 302)
check("statut Brouillon au départ", etat(email_a)["status"] == "DRAFT")
check("consentement enregistré en base", consentement_actif(email_a))

print("--- Étape 6 : soumission ---")
ca.post("/profil/soumettre")
check("après soumission : En attente", etat(email_a)["status"] == "PENDING")
id_a = etat(email_a)["id"]

print("--- Étape 7 : validation par le service Alumni ---")
cs = connexion("service@example.com")
check("le service voit le profil en attente", nom in cs.get("/validation").get_data(as_text=True))
cs.post(f"/validation/{id_a}/corriger", data={"motif": ""})
check("correction sans motif refusée", etat(email_a)["status"] == "PENDING")
cs.post(f"/validation/{id_a}/corriger", data={"motif": "Photo manquante"})
check("correction avec motif : À compléter", etat(email_a)["status"] == "NEEDS_CORRECTION")
check("l'alumni voit le motif", "Photo manquante" in ca.get("/profil").get_data(as_text=True))
ca.post("/profil", data={**donnees_a, "consent": "on"})
ca.post("/profil/soumettre")
check("resoumission après correction : En attente", etat(email_a)["status"] == "PENDING")
cs.post(f"/validation/{id_a}/valider")
check("validation : Validé, pas encore publié", etat(email_a)["status"] == "VALIDATED" and not etat(email_a)["is_published"])
cs.post(f"/validation/{id_a}/publier")
check("publication : profil publié", etat(email_a)["is_published"])

print("--- Étape 8 : doublon ---")
cb = connexion(email_b)
cb.post("/profil", data={**donnees_b, "consent": "on"})
cb.post("/profil/soumettre")
check("le service voit un doublon probable", "Doublon probable" in cs.get("/validation").get_data(as_text=True))
id_b = etat(email_b)["id"]
check("le doublon n'est pas fusionné automatiquement", etat(email_a) is not None and etat(email_b) is not None)

print("--- Étapes 9 et 10 : recherche et fiche ---")
et = connexion("etudiant@example.com")
check("filtre promotion : l'alumni publié apparaît", nom in et.get("/annuaire?promotion=2022").get_data(as_text=True))
check("le profil non validé n'apparaît pas", email_b not in et.get("/annuaire?promotion=2022").get_data(as_text=True))
check("filtres combinés filière + ville + pays", nom in et.get("/annuaire?filiere=Informatique&ville=casablanca&pays=Maroc").get_data(as_text=True))
check("aucun résultat : message affiché", "Aucun alumni" in et.get("/annuaire?ville=Paris").get_data(as_text=True))
fiche = et.get(f"/annuaire/{id_a}")
check("fiche accessible avec coordonnées", fiche.status_code == 200 and email_a in fiche.get_data(as_text=True))
check("fiche d'un profil non publié : 404", et.get(f"/annuaire/{id_b}").status_code == 404)

print("--- Étape 11 : tableau de bord ---")
dt = connexion("direction@example.com")
r = dt.get("/tableau-de-bord")
check("la direction voit le tableau de bord", r.status_code == 200 and "Taux d'alumni recensés" in r.get_data(as_text=True))
check("le service ne voit pas le tableau de bord", cs.get("/tableau-de-bord").status_code == 403)

print("--- Étape 12 : retrait du consentement ---")
ca.post("/profil/retirer-consentement")
check("retrait : profil dépublié", etat(email_a)["is_published"] is False)
check("retrait : profil absent de l'annuaire", nom not in et.get("/annuaire?promotion=2022").get_data(as_text=True))

print()
print(f"Bilan : {sum(resultats)} réussi(s) sur {len(resultats)}")
