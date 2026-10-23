"""Vérification d'un profil alumni à partir d'un texte copié depuis LinkedIn.

Le texte est analysé en mémoire et n'est jamais enregistré.
Le résultat est une recommandation : la décision reste au service Alumni.
"""

import re
import unicodedata

VERIFIED = "VERIFIED"
DISCREPANCY_FOUND = "DISCREPANCY_FOUND"
UNMATCHED = "UNMATCHED"

STATUS_LABELS = {
    VERIFIED: "Vérifié",
    DISCREPANCY_FOUND: "Incohérence détectée",
    UNMATCHED: "Non concordant",
}

# Poids des critères dans le score de confiance (total 100)
WEIGHTS = {"identite": 40, "diplome": 30, "poste": 30}


def normaliser(texte):
    """Minuscules, sans accents, sans ponctuation : pour comparer les mots."""
    texte = unicodedata.normalize("NFD", texte.lower())
    texte = "".join(c for c in texte if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", " ", texte).strip()


def mots(texte):
    return set(normaliser(texte).split())


def comparer_identite(profil, texte):
    texte_n = normaliser(texte)
    mots_texte = set(texte_n.split())
    prenom_ok = normaliser(profil.first_name) in texte_n
    # Le nom peut être composé ou avoir une variante : on compare chaque partie
    parties_nom = [p for p in normaliser(profil.last_name).split() if p]
    nom_ok = bool(parties_nom) and all(p in mots_texte for p in parties_nom)
    if prenom_ok and nom_ok:
        return VERIFIED, "Prénom et nom présents dans le profil LinkedIn."
    if prenom_ok or nom_ok:
        manque = "le nom" if prenom_ok else "le prénom"
        return DISCREPANCY_FOUND, f"Un seul des deux correspond : {manque} n'apparaît pas."
    return UNMATCHED, "Ni le prénom ni le nom n'apparaissent dans le texte."


def comparer_diplome(profil, texte):
    texte_n = normaliser(texte)
    annee_ok = str(profil.graduation_year) in texte_n
    filiere = normaliser(profil.study_program.name) if profil.study_program else ""
    filiere_ok = bool(filiere) and filiere in texte_n
    # Si le texte ne mentionne ni la filière ni l'année, on ne peut pas conclure
    if annee_ok and filiere_ok:
        return VERIFIED, "Filière et promotion correspondent."
    if annee_ok or filiere_ok:
        manque = "la filière" if annee_ok else "la promotion"
        return DISCREPANCY_FOUND, f"Une information correspond, {manque} n'est pas retrouvée."
    return UNMATCHED, "Ni la filière ni la promotion ne sont mentionnées."


def comparer_poste(profil, texte):
    actuelle = profil.experiences.filter(end_date__isnull=True).order_by("-start_date").first()
    if actuelle is None:
        return UNMATCHED, "Aucun poste actuel dans la base : rien à comparer."
    texte_n = normaliser(texte)
    entreprise = normaliser(actuelle.company)
    entreprise_ok = bool(entreprise) and entreprise in texte_n
    mots_poste = {m for m in mots(actuelle.job_title) if len(m) > 2}
    mots_texte = mots(texte)
    recouvrement = len(mots_poste & mots_texte) / len(mots_poste) if mots_poste else 0
    poste_ok = recouvrement >= 0.5
    if entreprise_ok and poste_ok:
        return VERIFIED, "Entreprise et poste correspondent."
    if entreprise_ok or poste_ok:
        manque = "le poste" if entreprise_ok else "l'entreprise"
        return DISCREPANCY_FOUND, (
            f"Une information correspond, {manque} diffère : "
            "changement récent possible, à vérifier."
        )
    return UNMATCHED, "Entreprise et poste différents de la base."


def verifier(profil, texte):
    """Renvoie le statut global, le score (0 à 100), le détail et la recommandation."""
    criteres = {
        "identite": comparer_identite(profil, texte),
        "diplome": comparer_diplome(profil, texte),
        "poste": comparer_poste(profil, texte),
    }

    score = 0
    for cle, (statut, _) in criteres.items():
        if statut == VERIFIED:
            score += WEIGHTS[cle]
        elif statut == DISCREPANCY_FOUND:
            score += WEIGHTS[cle] // 2

    if criteres["identite"][0] == UNMATCHED:
        statut_global = UNMATCHED
        recommandation = "Profil non concordant : ne pas valider, vérifier l'identité de la personne."
    elif all(statut == VERIFIED for statut, _ in criteres.values()):
        statut_global = VERIFIED
        recommandation = "Concordance complète : validation possible, la décision reste au service."
    else:
        statut_global = DISCREPANCY_FOUND
        recommandation = "Vérification manuelle requise : au moins un critère ne concorde pas."

    return {
        "statut": statut_global,
        "libelle": STATUS_LABELS[statut_global],
        "score": score,
        "criteres": [
            {"nom": nom, "statut": statut, "libelle": STATUS_LABELS[statut], "detail": detail}
            for nom, (statut, detail) in criteres.items()
        ],
        "recommandation": recommandation,
    }
