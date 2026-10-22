# Démonstration — SI Alumni EIGSICA (version Django)

Vidéo : [demo/demo-alumni-eigsica.mp4](demo/demo-alumni-eigsica.mp4) (environ 2 min 30, en mode sombre puis en mode clair)

## Lancer l'application

```
python -m venv .venv
.venv\Scripts\activate          (Windows)
source .venv/bin/activate       (macOS / Linux)
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Ouvrez ensuite http://127.0.0.1:8000 dans le navigateur.

`seed_demo` crée les données de démonstration. Sur une base neuve, le mot de passe de tous les comptes de test est **demo1234**.

## Comptes de test

| Rôle | Adresse e-mail | Mot de passe |
|---|---|---|
| Alumni (profil validé) | aissata.fall@example.test | demo1234 |
| Alumni (correction demandée) | cheikh.ndiaye@example.test | demo1234 |
| Service Alumni | service.alumni@example.test | demo1234 |
| Étudiant | aminata.ba@example.test | demo1234 |
| Direction | direction@example.test | demo1234 |

## Déroulé de la démonstration

1. **Accueil et connexion** : présentation de la page, saisie des identifiants, en mode sombre.
2. **Espace alumni** (Cheikh Ndiaye) : complétion du profil, case de consentement, soumission. Le statut passe à « En attente de validation ».
3. **Service Alumni** : examen du profil, décision avec commentaire.
4. **Espace étudiant** (Aminata Ba) : suggestions, annuaire, fiche, demande de contact.
5. **Direction** : profils alumni, validations, statistiques, tableau de bord.
6. **Mode clair** : connexion et tableau de bord en mode clair.

## Tests

```
python manage.py test alumni
```

Six tests doivent passer.
