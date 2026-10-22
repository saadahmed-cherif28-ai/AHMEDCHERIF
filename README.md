# Projet Alumni EIGSICA

Application Django locale de suivi des alumni de l’EIGSICA. Le projet utilise
Django, des templates HTML intégrés et SQLite pour le prototype. Les données
chargées sont fictives.

## Prérequis

- Windows et PowerShell ;
- Python 3.14 ;
- ouvrir PowerShell dans le dossier du projet.

## Installation depuis zéro

Dans le dossier du projet, créer l’environnement virtuel :

```powershell
python -m venv .venv
```

Si `python` n’est pas reconnu, utiliser le chemin Python installé localement :

```powershell
& "$env:LOCALAPPDATA\Programs\Python\Python314\python.exe" -m venv .venv
```

Installer les dépendances :

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Créer les tables SQLite :

```powershell
.\.venv\Scripts\python.exe manage.py migrate
```

Charger les données fictives :

```powershell
.\.venv\Scripts\python.exe manage.py seed_demo
```

La commande `seed_demo` configure le mot de passe local `demo1234` pour les
comptes fictifs. Pour choisir un autre mot de passe, utiliser ensuite :

```powershell
.\.venv\Scripts\python.exe manage.py changepassword direction@example.test
```

## Lancer l’application

```powershell
.\.venv\Scripts\python.exe manage.py runserver
```

Ouvrir ensuite : <http://127.0.0.1:8000/>

Pour arrêter le serveur, revenir dans PowerShell et appuyer sur `Ctrl+C`.

## Routes disponibles

- Accueil : <http://127.0.0.1:8000/> ;
- Connexion : <http://127.0.0.1:8000/connexion/> ;
- Déconnexion : formulaire **Se déconnecter** dans les espaces connectés ;
- Espace Alumni : <http://127.0.0.1:8000/alumni/> ;
- Profil alumni : <http://127.0.0.1:8000/profil/> ;
- File Service Alumni : <http://127.0.0.1:8000/service/> ;
- Annuaire Étudiant : <http://127.0.0.1:8000/annuaire/> ;
- Suggestions Étudiant : <http://127.0.0.1:8000/suggestions/> ;
- Profil public : accessible avec le bouton **Voir le profil** depuis les suggestions ;
- Tableau de bord Direction : <http://127.0.0.1:8000/direction/>.

Les comptes de démonstration sont fictifs. Après avoir défini les mots de passe
avec `changepassword`, utiliser :

| Rôle | Email |
| --- | --- |
| Alumni | `aissata.fall@example.test` |
| Étudiant | `aminata.ba@example.test` |
| Service Alumni | `service.alumni@example.test` |
| Direction | `direction@example.test` |

Mot de passe de démonstration pour ces quatre comptes : `demo1234`.

## État du MVP

### Fonctionnalités terminées

- initialisation Django et connexion SQLite locale ;
- modèles, relations, contraintes et migrations de la base Alumni ;
- données fictives répétables avec `seed_demo` ;
- connexion par email et redirection selon le rôle ;
- formulaire Alumni avec profil, filière, localisation et situation professionnelle ;
- consentement obligatoire pour l’annuaire, avec date et version enregistrées ;
- soumission du profil vers l’état « En attente » et journal d’audit ;
- tableau de bord Direction avec profils récents et indicateurs ;
- file de validation Service Alumni avec décision, motif et publication protégée par le consentement ;
- annuaire Étudiant avec recherche par nom, filière ou ville ;
- demandes de contact sans affichage direct de l’adresse personnelle ;
- déconnexion accessible depuis les espaces principaux ;
- pages Direction Profils, Validations et Statistiques accessibles depuis la navigation ;
- espace Alumni avec compteur de consultations et visiteurs identifiés ;
- page publique de profil et suggestions Étudiant ;
- 21 tests automatisés couvrant les parcours actuellement développés.

### Fonctionnalités restantes

- gestion complète des notifications dans l’interface ;
- texte légal définitif du consentement et configuration de production.

### Limites et décisions à prendre

- le texte juridique réel du consentement doit remplacer le texte de démonstration ;
- la version `2026-01` du consentement est provisoire ;
- les données, comptes et mots de passe sont uniquement destinés au développement local ;
- le taux de recensement réel nécessite le nombre total d’anciens étudiants attendus ;
- la connexion ENT/SSO et les règles de visibilité des étudiants restent à définir.

## Scénario de démonstration en 3 minutes

1. Ouvrir <http://127.0.0.1:8000/> et cliquer sur **Se connecter**.
2. Se connecter avec le compte Alumni `aissata.fall@example.test` et le mot de passe `demo1234`.
3. Montrer le formulaire **Mon profil alumni** et les champs préremplis.
4. Montrer la case de consentement obligatoire.
5. Cliquer sur **Enregistrer et soumettre** et montrer le message indiquant que le profil est en attente de vérification.
6. Se déconnecter, puis se connecter avec `service.alumni@example.test` et montrer la file de validation.
7. Ouvrir Cheikh Ndiaye, choisir « Correction demandée », écrire un motif et enregistrer.
8. Se déconnecter, puis se connecter avec `aminata.ba@example.test` et montrer l’annuaire avec Aïssata publiée.
9. Ouvrir Aïssata, écrire un message et envoyer la demande de contact.
10. Se déconnecter, puis se connecter avec `direction@example.test` et montrer le tableau de bord : profils, complétude, fraîcheur, délai médian et statuts.
11. Depuis la navigation Direction, ouvrir **Profils**, **Validations**, **Statistiques**, **File Service**, **Suggestions** et **Annuaire** pour montrer l’accès transversal.

## Vérifier le projet

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py test
```

Les bases `db.sqlite3`, `db_alumni.sqlite3` et l’environnement `.venv` restent
locaux et ne doivent pas être ajoutés au dépôt.
