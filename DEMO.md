# Scénario de démonstration — SI Alumni EIGSI (MVP)

## Lancer l'application

```
cd /home/claude/si-alumni
source ~/mvp-env/bin/activate
python seed.py      # crée les tables et les comptes de test (à faire une seule fois)
python app.py
```

Ouvrez ensuite `http://127.0.0.1:5000` dans le navigateur.

Comptes de test (mot de passe : `test1234`) :
- alumni@example.com
- service@example.com
- direction@example.com
- etudiant@example.com

## Déroulé pour la vidéo (environ 3 minutes)

1. **Connexion alumni** : se connecter avec alumni@example.com. Montrer la redirection vers l'espace alumni.
2. **Profil** : ouvrir « Mon profil ». Remplir prénom, nom, promotion, filière, ville, pays. Ne pas cocher la case : cliquer sur « Enregistrer » et montrer que le message d'erreur empêche l'enregistrement.
3. **Consentement** : cocher la case, enregistrer. Puis cliquer sur « Soumettre mon profil » : le statut passe à « En attente de validation ».
4. **Service Alumni** : se déconnecter, se connecter avec service@example.com, ouvrir « Validation des profils ».
   - Renvoyer le profil avec un motif (« Photo manquante », par exemple).
   - Se reconnecter comme alumni : le motif est affiché. Corriger, soumettre à nouveau.
   - Revenir comme service : valider, puis publier dans l'annuaire.
5. **Étudiant** : se connecter avec etudiant@example.com, ouvrir « Annuaire des alumni ». Filtrer par promotion, puis par filière et ville. Ouvrir une fiche.
6. **Direction** : se connecter avec direction@example.com, ouvrir « Tableau de bord ». Montrer les 4 indicateurs.
7. **Conclusion** : revenir sur l'alumni, retirer le consentement. Le profil disparaît de l'annuaire.

## Ce que la démonstration ne couvre pas encore

- Connexion par ENT/SSO et invitation par mail (reportées)
- Relances automatiques et notifications (reportées)
- Import et export CSV (reportés)
- Taux d'alumni recensés calculé sur le vrai référentiel : valeur provisoire de 10 diplômés ciblés
