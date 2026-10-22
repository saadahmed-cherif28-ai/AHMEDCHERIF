# Schéma de base de données corrigé

Ce document propose une base de données alignée sur le backlog et les maquettes. Il complète le schéma existant sans modifier les fichiers de conception d’origine.

**Repères :** `PK` est la clé primaire, l’identifiant unique d’une ligne. `FK` est une clé étrangère, le lien vers une ligne d’une autre table. `UNIQUE` interdit les doublons.

## 1. Tables du MVP

### `APP_USER` — comptes et rôles

- `id` : PK, UUID.
- `email` : obligatoire et unique.
- `role` : `ALUMNI`, `STUDENT`, `SERVICE_ALUMNI`, `DIRECTION` ou `ADMIN`.
- `created_at` : date de création.
- Informations de connexion : à définir après le choix entre ENT/SSO et mot de passe. Si les deux modes sont acceptés, prévoir un fournisseur d’identité et un identifiant externe ; le mot de passe doit rester facultatif pour les comptes SSO.

### `ALUMNI_PROFILE` — profil alumni

- `id` : PK, UUID.
- `user_id` : FK vers `APP_USER.id`, obligatoire et unique. Un compte ne peut avoir qu’un seul profil alumni.
- `student_number` : obligatoire et unique.
- `first_name`, `last_name` : nom affiché dans le profil et les résultats.
- `graduation_year` : année de diplôme, utilisée comme promotion si c’est bien la règle retenue.
- `study_program_id` : FK vers `STUDY_PROGRAM.id`.
- `location_id` : FK vers `LOCATION.id`, facultative si l’alumni ne souhaite pas partager sa localisation.
- `employment_status` : situation professionnelle.
- `profile_status` : `DRAFT`, `PENDING`, `CORRECTION_REQUESTED`, `VALIDATED` ou `REJECTED`.
- `last_confirmed_at` : date de dernière confirmation du profil.
- `published_at` : date de publication, vide tant que le profil n’est pas publié.

### `STUDY_PROGRAM` — filières

- `id` : PK, UUID.
- `name` : nom de la filière, obligatoire et unique.

### `LOCATION` — localisations

- `id` : PK, UUID.
- `country_code`, `region`, `city` : stockés dans des champs séparés pour les filtres et les statistiques géographiques.

### `PROFESSIONAL_EXPERIENCE` — expériences professionnelles

- `id` : PK, UUID.
- `alumni_profile_id` : FK vers `ALUMNI_PROFILE.id`.
- `company`, `job_title`, `sector` : entreprise, poste et secteur.
- `start_date`, `end_date` : dates de l’expérience ; `end_date` peut être vide si l’expérience est en cours.
- Règle : la date de fin ne peut pas précéder la date de début. L’état « en cours » est déduit de l’absence de date de fin ; il n’y a donc pas de champ séparé `is_current`.

### `CONSENT` — consentements

- `id` : PK, UUID.
- `alumni_profile_id` : FK vers `ALUMNI_PROFILE.id`.
- `purpose` : finalité du consentement.
- `policy_version` : version du texte accepté.
- `accepted_at` : date d’acceptation.
- `revoked_at` : date de retrait, vide tant que le consentement est actif.
- Règles : conserver les anciens consentements pour l’historique ; n’autoriser qu’un consentement actif par profil et par finalité. L’état actif est déduit de `revoked_at` vide, sans champ booléen supplémentaire.
- Avant publication ou mise en relation, vérifier que le profil est validé et que le consentement nécessaire est toujours actif.

### `VALIDATION_REVIEW` — décisions du service Alumni

- `id` : PK, UUID.
- `alumni_profile_id` : FK vers `ALUMNI_PROFILE.id`.
- `reviewer_user_id` : FK vers `APP_USER.id`.
- `decision` : décision du contrôle, par exemple validation, correction demandée ou rejet.
- `comment` : motif ou commentaire, facultatif.
- `created_at` : date de la décision.
- Conserver chaque décision afin de garder l’historique des validations et corrections.

### `CONTACT_REQUEST` — demandes de mise en relation

- `id` : PK, UUID.
- `student_user_id` : FK vers `APP_USER.id` pour le compte Étudiant.
- `alumni_profile_id` : FK vers `ALUMNI_PROFILE.id`.
- `status`, `message`, `created_at` : état, message facultatif et date de la demande.
- Enregistrer la demande sans afficher directement l’adresse personnelle de l’alumni.

### `NOTIFICATION` — notifications

- `id` : PK, UUID.
- `recipient_user_id` : FK vers `APP_USER.id`.
- `alumni_profile_id` : FK facultative vers `ALUMNI_PROFILE.id`.
- `type`, `status`, `created_at`, `sent_at` : type, état et dates de la notification.
- Sert notamment à signaler une correction demandée ou la publication d’un profil.

### `AUDIT_LOG` — journal des actions

- `id` : PK, UUID, comme les autres identifiants.
- `actor_user_id` : FK vers `APP_USER.id`, facultative pour les actions automatiques du système.
- `alumni_profile_id`, `consent_id`, `experience_id`, `validation_review_id`, `contact_request_id` : FKs facultatives vers les objets concernés.
- `action`, `details`, `created_at` : action effectuée, détails utiles et date.
- Règle : chaque entrée doit référencer l’objet concerné avec une vraie FK, et non un identifiant libre dont l’existence ne pourrait pas être vérifiée.

## 2. Relations principales

- Un compte (`APP_USER`) peut avoir zéro ou un profil alumni (`ALUMNI_PROFILE`).
- Un programme ou un lieu peut être associé à plusieurs profils ; chaque profil a au plus un programme et un lieu.
- Un profil alumni peut avoir plusieurs expériences, consentements historiques, décisions de validation et demandes de contact.
- Un étudiant peut créer plusieurs demandes de contact. Chaque demande vise un profil alumni.
- Un agent du service Alumni peut enregistrer plusieurs décisions de validation.

## 3. Fonctions du backlog à ajouter si elles sont retenues

Ces tables ne sont pas toutes nécessaires pour le premier MVP ; elles servent à couvrir les fonctions prévues après la première version.

- `REMINDER_CAMPAIGN` et `REMINDER_RECIPIENT` : campagnes de relance et suivi des alumni contactés ou ayant répondu.
- `IMPORT_BATCH` et `IMPORT_ERROR` : suivi des imports CSV et détail des lignes refusées. Un export simple peut être produit directement depuis les profils.
- Mentorat, offres et événements : ajouter des tables dédiées uniquement si ces fonctions « Could » sont validées pour une version ultérieure.
- Recommandations par IA : hors MVP selon le backlog actuel ; ne pas ajouter de table avant que cette fonction soit confirmée.

## 4. Règles à confirmer avant l’implémentation

- Le mode de connexion retenu pour chaque rôle : ENT/SSO, mot de passe, ou les deux.
- Le texte et les finalités exactes du consentement, ainsi que la durée de conservation des données.
- La correspondance entre promotion, année de diplôme et filière.
- Les informations qu’un étudiant peut consulter et la façon dont une demande de contact est transmise.
- Les valeurs autorisées pour les situations professionnelles et les états d’une demande de contact.
