# Journal du projet

## 2026-10-09

- **Fait :** Vérifié Python 3.14.7 et pip 26.2.1. Ajouté les dossiers Python et `Scripts` au `PATH` utilisateur ; les commandes `python` et `pip` fonctionnent.
- **Fait :** Créé l’environnement virtuel `.venv` et vérifié qu’il exécute Python 3.14.7.
- **Fait :** Installé Django 5.2.18 dans `.venv` et vérifié sa version.
- **Fait :** Généré l’application Django `alumni/` avec ses fichiers standards.
- **Fait :** Créé la configuration Django, la route `/` et le template « Hello » ; `manage.py check` passe et le test de la page réussit.
- **Fait :** Rédigé `README.md` avec les commandes Windows de préparation, migration, lancement et test.
- **Fait :** Initialisé la base locale `db.sqlite3` avec les migrations Django.
- **Fait :** Relancé `manage.py check` et `manage.py test alumni` avec succès ; vérifié la route `/` en HTTP (200, texte « Hello ») et démarré le serveur local.
- **Fait :** Créé les modèles, relations et contraintes du schéma Alumni ; `manage.py check` passe.
- **Fait :** Généré `alumni/migrations/0001_initial.py` pour créer les tables dans une base distincte, sans toucher à `db.sqlite3`.
- **Fait :** Ajouté la commande réexécutable `seed_demo` avec des exemples fictifs, et un test des relations et de l’absence de doublons ; `manage.py check` passe.
- **Fait :** `makemigrations --check --dry-run` ne détecte aucun changement manquant ; toutes les migrations ont été appliquées à `db_alumni.sqlite3`.
- **Fait :** Chargé les données fictives : 2 profils, 2 expériences, 2 consentements et 1 demande de contact. Le test `alumni` passe (2 tests, dont la répétition sans doublons de `seed_demo`).
- **Reste à faire :** Aucune étape restante pour la création initiale du schéma. Le développement peut continuer avec les fonctionnalités du MVP.

## 2026-10-09 — Tableau de bord Direction

- **Fait :** Ajouté une date de soumission au profil pour calculer le délai de validation et généré une migration.
- **Fait :** Ajouté une page de connexion et un tableau de bord réservé au rôle Direction, avec indicateurs, répartition des états et profils récents.
- **Fait :** Étendu les données fictives avec un compte Direction et des profils de démonstration qui montrent des cas complets, à corriger et anciens.
- **Fait :** Ajouté quatre tests sur la connexion, les droits d’accès et les valeurs des indicateurs. Les six tests de l’application passent.
- **Fait :** Mis à jour le README avec les commandes pour migrer, charger les exemples, définir le mot de passe local et ouvrir le tableau de bord.
- **Fait :** Appliqué la migration locale, chargé les exemples, vérifié la page de connexion et le tableau de bord dans le navigateur, et confirmé que la feuille CSS est servie en HTTP 200.
- **Fait :** Vérifié `manage.py check`, l’absence de migration manquante et les six tests, y compris le calcul d’une seule première validation par profil.
- **Reste à faire :** Le taux réel de recensement ne peut pas être calculé sans connaître le nombre total d’anciens étudiants attendus ; le tableau de bord affiche donc le nombre de profils enregistrés.

## 2026-10-22 — Profil alumni et consentement

- **Fait :** Ajouté le formulaire protégé `/profil/` pour saisir ou corriger un profil alumni.
- **Fait :** Ajouté le consentement obligatoire pour l’annuaire, avec version et date d’acceptation enregistrées.
- **Fait :** Ajouté la soumission vers l’état « En attente », l’audit de l’action et les tests des droits, du consentement et de la soumission.
- **Fait :** Corrigé l’affichage du message d’erreur du consentement et la redirection de connexion selon le rôle, qui envoyait auparavant un alumni vers une page Direction interdite.
- **Fait :** Vérifié dans le navigateur le parcours connexion alumni → formulaire → soumission, puis restauré les données de démonstration.
- **Fait :** Ajouté la file de validation du Service Alumni, l’annuaire filtrable Étudiant, les demandes de contact, les comptes de démonstration communs et la déconnexion.
- **Fait :** Vérifié les parcours Service Alumni et Étudiant dans le navigateur ; la suite comporte maintenant 16 tests réussis.
- **Fait :** Corrigé `seed_demo` pour qu’il reste réexécutable après l’envoi de plusieurs demandes de contact depuis l’annuaire.
- **Fait :** Rendu aussi les notifications de démonstration idempotentes après plusieurs demandes de contact.
- **Fait :** Relié les trois sections Direction à des pages fonctionnelles : profils, historique des validations et statistiques.
- **Fait :** Ajouté les tests des trois pages Direction.
- **Fait :** Ajouté la page d’accueil publique, l’espace Alumni avec compteur et historique des consultations, la page de profil public et les suggestions Étudiant.
- **Fait :** Ajouté la table `ProfileView`, sa migration et les droits permettant à la Direction de consulter tous les espaces.
- **Fait :** La suite de tests comporte maintenant 20 tests réussis.

## 2026-10-22 — Accès complet de démonstration

- **Fait :** Vérifié la page d’accueil publique et l’espace Alumni dans le navigateur.
- **Fait :** Vérifié les accès Direction aux espaces Alumni, Service et Étudiant.
- **Fait :** Ajouté un test d’accès transversal Direction ; la suite comporte maintenant 21 tests réussis.
- **Limite connue :** le clic automatique sur une page de connexion masquée du navigateur n’a pas pu être rejoué ; les parcours sont couverts par les tests Django et le serveur répond sur `http://127.0.0.1:8000/`.
- **Reste à faire :** Les décisions métier de production restent à confirmer : texte légal du consentement, SSO et règles de conservation.
