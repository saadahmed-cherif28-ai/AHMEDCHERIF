import os
import statistics
from datetime import timedelta
from functools import wraps

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from sqlalchemy import func, select
from werkzeug.security import check_password_hash

from database import SessionLocal
from models import (
    AlumniProfile,
    Consent,
    ConsentVersion,
    StatusHistory,
    User,
    utcnow,
)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-only-a-changer")

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "Connectez-vous pour accéder à cette page."

# Page d'accueil de chaque rôle après connexion
ROLE_HOMES = {
    "ALUMNI": "espace_alumni",
    "SERVICE": "espace_service",
    "DIRECTION": "espace_direction",
    "ADMIN": "espace_admin",
    "STUDENT": "espace_etudiant",
}

# Filières proposées dans le formulaire et dans le filtre de l'annuaire
PROGRAMMES = ["Informatique", "Industrie", "Cybersécurité"]

CONSENT_PURPOSE = "suivi_alumni"

# Nombre de diplômés ciblés : valeur provisoire, à remplacer par le référentiel de l'école
DIPLOMES_CIBLES = 10

STATUT_LIBELLES = {
    "DRAFT": "Brouillon (non soumis)",
    "PENDING": "En attente de validation",
    "NEEDS_CORRECTION": "À compléter",
    "VALIDATED": "Validé",
    "REJECTED": "Refusé",
}


@login_manager.user_loader
def load_user(user_id):
    with SessionLocal() as session:
        return session.get(User, user_id)


def role_required(*roles):
    """Autorise l'accès seulement aux rôles indiqués."""

    def decorator(view):
        @wraps(view)
        @login_required
        def wrapper(*args, **kwargs):
            if current_user.role not in roles:
                return "Accès refusé : cette page n'est pas pour votre rôle.", 403
            return view(*args, **kwargs)

        return wrapper

    return decorator


# ---------- Fonctions utilitaires ----------


def get_profile(session, user_id):
    return session.scalar(select(AlumniProfile).where(AlumniProfile.user_id == user_id))


def consentement_actif(session, profile):
    return session.scalar(
        select(Consent).where(
            Consent.alumni_id == profile.id, Consent.revoked_at.is_(None)
        )
    )


def version_consentement(session):
    return session.scalar(
        select(ConsentVersion)
        .where(ConsentVersion.purpose_code == CONSENT_PURPOSE)
        .order_by(ConsentVersion.published_at.desc())
    )


def historise(session, profile, to_status, actor_id, comment=None):
    """Change le statut et garde une trace de l'ancien statut."""
    session.add(
        StatusHistory(
            alumni_id=profile.id,
            from_status=profile.status,
            to_status=to_status,
            actor_user_id=actor_id,
            comment=comment,
        )
    )
    profile.status = to_status


def dernier_motif(session, profile):
    historique = session.scalar(
        select(StatusHistory)
        .where(
            StatusHistory.alumni_id == profile.id,
            StatusHistory.to_status == "NEEDS_CORRECTION",
        )
        .order_by(StatusHistory.created_at.desc())
    )
    return historique.comment if historique else None


def doublons_de(session, profile):
    """Autres profils ayant le même nom, prénom et promotion."""
    return session.scalars(
        select(AlumniProfile).where(
            AlumniProfile.first_name == profile.first_name,
            AlumniProfile.last_name == profile.last_name,
            AlumniProfile.graduation_year == profile.graduation_year,
            AlumniProfile.id != profile.id,
        )
    ).all()


def valeurs_du_profil(profile, email):
    return {
        "first_name": profile.first_name,
        "last_name": profile.last_name,
        "graduation_year": profile.graduation_year,
        "program": profile.program or "",
        "city": profile.city or "",
        "country": profile.country or "",
        "email": email,
    }


def valider_profil(values):
    """Renvoie un dictionnaire d'erreurs, vide si tout est correct."""
    errors = {}
    if not values["first_name"]:
        errors["first_name"] = "Le prénom est obligatoire."
    if not values["last_name"]:
        errors["last_name"] = "Le nom est obligatoire."
    try:
        annee = int(values["graduation_year"])
        if not 1980 <= annee <= 2100:
            errors["graduation_year"] = "L'année doit être entre 1980 et 2100."
    except ValueError:
        errors["graduation_year"] = "Saisissez une année valide, par exemple 2022."
    if values["program"] not in PROGRAMMES:
        errors["program"] = "Choisissez une filière dans la liste."
    if not values["city"]:
        errors["city"] = "La ville est obligatoire."
    if not values["country"]:
        errors["country"] = "Le pays est obligatoire."
    if "@" not in values["email"] or "." not in values["email"].split("@")[-1]:
        errors["email"] = "Saisissez une adresse e-mail valide."
    return errors


def pourcentage(part, total):
    return round(part / total * 100) if total else 0


# ---------- Connexion ----------


@app.route("/")
def accueil():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        with SessionLocal() as session:
            user = session.scalar(select(User).where(User.email == email))

        if (
            user is not None
            and user.is_active
            and user.password_hash is not None
            and check_password_hash(user.password_hash, password)
        ):
            login_user(user)
            return redirect(url_for(ROLE_HOMES[user.role]))

        return (
            render_template(
                "login.html", error="E-mail ou mot de passe incorrect.", email=email
            ),
            401,
        )

    return render_template("login.html", error=None, email="")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Vous êtes déconnecté.")
    return redirect(url_for("login"))


# ---------- Espace alumni : profil, consentement, soumission ----------


@app.route("/espace/alumni")
@role_required("ALUMNI")
def espace_alumni():
    return render_template(
        "espace.html",
        titre="Espace alumni",
        message="Complétez votre profil, puis soumettez-le au service Alumni.",
    )


@app.route("/profil", methods=["GET", "POST"])
@role_required("ALUMNI")
def profil():
    with SessionLocal() as session:
        user = session.get(User, current_user.id)
        profile = get_profile(session, user.id)
        consent = consentement_actif(session, profile) if profile else None

        if request.method == "POST":
            values = {
                "first_name": request.form.get("first_name", "").strip(),
                "last_name": request.form.get("last_name", "").strip(),
                "graduation_year": request.form.get("graduation_year", "").strip(),
                "program": request.form.get("program", "").strip(),
                "city": request.form.get("city", "").strip(),
                "country": request.form.get("country", "").strip(),
                "email": request.form.get("email", "").strip().lower(),
            }
            consent_coche = request.form.get("consent") == "on"

            errors = valider_profil(values)
            # Sans case cochée, rien n'est enregistré
            if not consent_coche:
                errors["consent"] = "Cochez la case pour enregistrer vos données."

            # L'e-mail doit rester unique : refus s'il appartient à un autre compte
            if not errors and values["email"] != user.email:
                autre = session.scalar(
                    select(User).where(User.email == values["email"])
                )
                if autre is not None:
                    errors["email"] = "Cet e-mail est déjà utilisé par un autre compte."

            if errors:
                motif = (
                    dernier_motif(session, profile)
                    if profile and profile.status == "NEEDS_CORRECTION"
                    else None
                )
                return render_template(
                    "profil.html",
                    values=values,
                    errors=errors,
                    statut_label=STATUT_LIBELLES[profile.status if profile else "DRAFT"],
                    consent_actif=consent_coche,
                    peut_soumettre=False,
                    motif=motif,
                )

            user.email = values["email"]
            if profile is None:
                profile = AlumniProfile(user_id=user.id)
                session.add(profile)

            profile.first_name = values["first_name"]
            profile.last_name = values["last_name"]
            profile.graduation_year = int(values["graduation_year"])
            profile.program = values["program"]
            profile.city = values["city"]
            profile.country = values["country"]

            session.flush()  # donne un identifiant au profil avant de le lier au consentement

            if consent is None:
                version = version_consentement(session)
                session.add(
                    Consent(
                        alumni_id=profile.id,
                        consent_version_id=version.id,
                        granted_at=utcnow(),
                    )
                )

            # Un profil déjà validé qui change doit être revalidé
            if profile.status == "VALIDATED":
                profile.is_published = False
                historise(
                    session, profile, "PENDING", user.id, "Modification du profil"
                )

            session.commit()
            flash("Profil enregistré.")
            return redirect(url_for("profil"))

        # Affichage du formulaire
        if profile is None:
            values = {
                "first_name": "",
                "last_name": "",
                "graduation_year": "",
                "program": "",
                "city": "",
                "country": "",
                "email": user.email,
            }
            statut = "DRAFT"
            motif = None
        else:
            values = valeurs_du_profil(profile, user.email)
            statut = profile.status
            motif = dernier_motif(session, profile) if statut == "NEEDS_CORRECTION" else None

        return render_template(
            "profil.html",
            values=values,
            errors={},
            statut_label=STATUT_LIBELLES[statut],
            consent_actif=consent is not None,
            peut_soumettre=statut in ("DRAFT", "NEEDS_CORRECTION") and consent is not None,
            motif=motif,
        )


@app.route("/profil/soumettre", methods=["POST"])
@role_required("ALUMNI")
def soumettre():
    with SessionLocal() as session:
        user = session.get(User, current_user.id)
        profile = get_profile(session, user.id)

        if profile is None:
            flash("Enregistrez d'abord votre profil.")
            return redirect(url_for("profil"))
        if consentement_actif(session, profile) is None:
            flash("Le consentement est requis avant la soumission.")
            return redirect(url_for("profil"))
        if profile.status not in ("DRAFT", "NEEDS_CORRECTION"):
            flash("Ce profil ne peut pas être soumis dans son état actuel.")
            return redirect(url_for("profil"))

        erreurs = valider_profil(valeurs_du_profil(profile, user.email))
        if erreurs:
            flash("Profil incomplet : " + " ".join(erreurs.values()))
            return redirect(url_for("profil"))

        historise(session, profile, "PENDING", user.id, "Profil soumis")
        profile.last_confirmed_at = utcnow()
        session.commit()
        flash("Profil soumis. Il est en attente de validation.")
    return redirect(url_for("profil"))


@app.route("/profil/retirer-consentement", methods=["POST"])
@role_required("ALUMNI")
def retirer_consentement():
    with SessionLocal() as session:
        profile = get_profile(session, current_user.id)
        consent = consentement_actif(session, profile) if profile else None
        if consent is not None:
            consent.revoked_at = utcnow()
            profile.is_published = False
            session.commit()
            flash("Consentement retiré : votre profil n'est plus visible dans l'annuaire.")
    return redirect(url_for("profil"))


# ---------- Espace service Alumni : validation ----------


@app.route("/espace/service")
@role_required("SERVICE")
def espace_service():
    return render_template(
        "espace.html",
        titre="Espace service Alumni",
        message="Validez, corrigez ou publiez les profils.",
    )


@app.route("/validation")
@role_required("SERVICE")
def validation():
    with SessionLocal() as session:
        en_attente = session.scalars(
            select(AlumniProfile)
            .where(AlumniProfile.status == "PENDING")
            .order_by(AlumniProfile.last_name)
        ).all()
        valides_non_publies = session.scalars(
            select(AlumniProfile).where(
                AlumniProfile.status == "VALIDATED",
                AlumniProfile.is_published.is_(False),
            )
        ).all()
        doublons = {p.id: len(doublons_de(session, p)) > 0 for p in en_attente}
        return render_template(
            "validation.html",
            en_attente=en_attente,
            valides=valides_non_publies,
            doublons=doublons,
        )


@app.route("/validation/<profile_id>/valider", methods=["POST"])
@role_required("SERVICE")
def valider(profile_id):
    with SessionLocal() as session:
        profile = session.get(AlumniProfile, profile_id)
        if profile is None or profile.status != "PENDING":
            flash("Profil introuvable ou non en attente.")
        else:
            historise(session, profile, "VALIDATED", current_user.id, "Validé")
            session.commit()
            flash("Profil validé.")
    return redirect(url_for("validation"))


@app.route("/validation/<profile_id>/corriger", methods=["POST"])
@role_required("SERVICE")
def corriger(profile_id):
    motif = request.form.get("motif", "").strip()
    with SessionLocal() as session:
        profile = session.get(AlumniProfile, profile_id)
        if profile is None or profile.status != "PENDING":
            flash("Profil introuvable ou non en attente.")
        elif not motif:
            flash("Le motif est obligatoire pour renvoyer un profil.")
        else:
            historise(session, profile, "NEEDS_CORRECTION", current_user.id, motif)
            session.commit()
            flash("Profil renvoyé à l'alumni avec le motif indiqué.")
    return redirect(url_for("validation"))


@app.route("/validation/<profile_id>/publier", methods=["POST"])
@role_required("SERVICE")
def publier(profile_id):
    with SessionLocal() as session:
        profile = session.get(AlumniProfile, profile_id)
        if profile is None or profile.status != "VALIDATED":
            flash("Seul un profil validé peut être publié.")
        else:
            profile.is_published = True
            profile.published_at = utcnow()
            session.commit()
            flash("Profil publié dans l'annuaire.")
    return redirect(url_for("validation"))


# ---------- Espace étudiant : annuaire ----------


@app.route("/espace/etudiant")
@role_required("STUDENT")
def espace_etudiant():
    return render_template(
        "espace.html",
        titre="Espace étudiant",
        message="Recherchez des alumni par promotion, filière, ville ou pays.",
    )


@app.route("/annuaire")
@role_required("STUDENT")
def annuaire():
    promotion = request.args.get("promotion", "").strip()
    filiere = request.args.get("filiere", "").strip()
    ville = request.args.get("ville", "").strip()
    pays = request.args.get("pays", "").strip()

    with SessionLocal() as session:
        requete = select(AlumniProfile).where(
            AlumniProfile.status == "VALIDATED",
            AlumniProfile.is_published.is_(True),
        )
        if promotion.isdigit():
            requete = requete.where(AlumniProfile.graduation_year == int(promotion))
        if filiere:
            requete = requete.where(AlumniProfile.program == filiere)
        if ville:
            requete = requete.where(func.lower(AlumniProfile.city) == ville.lower())
        if pays:
            requete = requete.where(func.lower(AlumniProfile.country) == pays.lower())

        resultats = session.scalars(requete.order_by(AlumniProfile.last_name)).all()
        return render_template(
            "annuaire.html",
            resultats=resultats,
            filieres=PROGRAMMES,
            filtres={
                "promotion": promotion,
                "filiere": filiere,
                "ville": ville,
                "pays": pays,
            },
        )


@app.route("/annuaire/<profile_id>")
@role_required("STUDENT")
def fiche(profile_id):
    with SessionLocal() as session:
        profile = session.get(AlumniProfile, profile_id)
        if (
            profile is None
            or profile.status != "VALIDATED"
            or not profile.is_published
        ):
            return "Profil introuvable.", 404
        user = session.get(User, profile.user_id)
        return render_template("fiche.html", profil=profile, email=user.email)


# ---------- Espace direction : tableau de bord ----------


@app.route("/espace/direction")
@role_required("DIRECTION")
def espace_direction():
    return render_template(
        "espace.html",
        titre="Espace direction",
        message="Consultez le tableau de bord de pilotage.",
    )


@app.route("/espace/admin")
@role_required("ADMIN")
def espace_admin():
    return render_template(
        "espace.html",
        titre="Espace administrateur",
        message="Espace administrateur (à définir plus tard).",
    )


@app.route("/tableau-de-bord")
@role_required("DIRECTION", "ADMIN")
def tableau_de_bord():
    with SessionLocal() as session:
        valides = session.scalars(
            select(AlumniProfile).where(AlumniProfile.status == "VALIDATED")
        ).all()
        total = len(valides)

        completes = sum(1 for p in valides if p.program and p.city and p.country)

        limite = utcnow() - timedelta(days=365)
        a_jour = sum(
            1 for p in valides if p.last_confirmed_at and p.last_confirmed_at >= limite
        )

        # Délai entre la première soumission et la première validation, en jours
        delais = []
        for p in valides:
            historique = session.scalars(
                select(StatusHistory).where(StatusHistory.alumni_id == p.id)
            ).all()
            soumis = [h.created_at for h in historique if h.to_status == "PENDING"]
            valide = [h.created_at for h in historique if h.to_status == "VALIDATED"]
            if soumis and valide:
                delais.append((min(valide) - min(soumis)).total_seconds() / 86400)

        kpi = {
            "recenses": pourcentage(total, DIPLOMES_CIBLES),
            "completes": pourcentage(completes, total),
            "a_jour": pourcentage(a_jour, total),
            "delai": round(statistics.median(delais), 1) if delais else None,
        }
        return render_template(
            "tableau_bord.html",
            kpi=kpi,
            total=total,
            diplomes_cibles=DIPLOMES_CIBLES,
        )


# ---------- Lancement ----------


if __name__ == "__main__":
    app.run(debug=True)
