# Résumé du projet

## 1. Résumé de l’application

L’application doit aider l’EIGSICA à recenser et suivre ses anciens étudiants (alumni).
Les alumni sont invités à saisir leur profil, leur parcours et leur consentement à l’utilisation de leurs données.
Le service Alumni contrôle les profils, demande des corrections si nécessaire et publie ceux qui sont validés.
Les étudiants peuvent rechercher des profils selon leur domaine et contacter un alumni.
La direction suit des indicateurs sur le nombre de profils, leur complétude, leur fraîcheur et les délais de validation.
Le projet cherche à remplacer un suivi dispersé par un processus unique, contrôlé et régulièrement actualisé.
La maquette prévoit aussi l’authentification, une file de validation et un tableau de bord.
La sécurité, le consentement et la limitation de l’accès aux données sont des exigences importantes.

## 2. Inventaire et éléments manquants

| Fichier trouvé | Contenu repéré |
| --- | --- |
| `S1_Rapport_.PROGAMME.DE.SUIVI.DES.ALUMNIS.EIGSICA.pdf.pdf` | Diagnostic et objectifs, processus actuel et processus cible, règles métier, exigences fonctionnelles, KPI et cible à six mois. |
| `S2_Rapport_Suivi_Alumni (2).pdf` | Backlog MVP de dix récits utilisateur, maquettes d’écrans, architecture technique et schéma relationnel avec dictionnaire de données. |
| `Capture d'écran 2026-09-28 173700.png` | Diagramme du processus cible : contribution et validation des profils, recherche par les étudiants. |
| `Capture d'écran 2026-09-28 181600.png` | Diagramme d’invitation d’un alumni et de son consentement. |

**Présents dans les rapports, mais pas comme fichiers séparés :** le backlog, les maquettes d’écrans et le schéma de base de données. Les deux captures seules sont des diagrammes de processus, pas des maquettes d’écran.

**Non trouvés dans le dossier :** fichiers de backlog séparés, fichiers de maquettes modifiables, schéma de base de données séparé, code de l’application, plan de tests et règles de conservation des données précises. Leur absence du dossier ne permet pas de savoir s’ils existent ailleurs.

## 3. Incohérences et points à harmoniser

- **Accès des étudiants :** le processus cible prévoit que les étudiants recherchent un alumni et le contactent. Pourtant, les rôles de la table `USER` listent Alumni, Service, Direction et Admin, sans rôle Étudiant. Il faut décider comment les étudiants se connectent et quelles données ils peuvent voir.
- **Moyens de connexion :** les exigences évoquent un lien d’invitation ou les identifiants de l’école, et une autre ligne précise une connexion via ENT/SSO. Le schéma prévoit un mot de passe stocké sous forme de hash. Ces options ne décrivent pas clairement le même mode de connexion.
- **Périmètre du MVP :** les rapports n’emploient pas exactement les mêmes priorités. Le backlog classe la gestion des données par CSV et les relances en « Should », la carte en « Could » et les recommandations par IA hors MVP. L’autre rapport inclut aussi mentorat et événements comme fonctions « Could ». Le périmètre à livrer en premier doit être fixé dans une seule liste de référence.
- **Vitesse de recherche :** une exigence vise moins de 2 secondes pour 95 % des recherches ; le backlog accepte une réponse en moins de 3 secondes. Il faut choisir une seule cible.
- **Filtres et données géographiques :** la recherche et la carte utilisent le pays et la ville, mais le schéma regroupe ces informations dans `city_country`. Des champs séparés seraient plus clairs pour filtrer et faire des statistiques par zone.
- **Preuve du consentement :** le backlog demande un consentement daté, révocable et associé à une finalité. La base prévoit les dates d’accord et de révocation, mais ne montre pas clairement la version du texte accepté ni son historique. La durée de conservation est aussi à définir avec l’établissement.

## 4. Questions pour avancer

1. Quelles fonctions doivent absolument être dans la première version : seulement les fonctions « Must », ou aussi les imports/exports CSV et les relances ? La carte, le mentorat, les événements et l’IA restent-ils hors MVP ?
2. Les étudiants auront-ils un compte ? Quelle méthode de connexion faut-il retenir pour chaque rôle : ENT/SSO, lien d’invitation ou mot de passe ?
3. Quels champs doit contenir un profil, et lesquels doivent servir à la recherche ? En particulier, faut-il stocker la ville et le pays séparément ?
4. Quelles informations de consentement doit-on conserver (texte ou version acceptée, date, finalité, révocation) et combien de temps garder les données ?
5. Quelle cible de rapidité retenir pour une recherche : moins de 2 secondes pour 95 % des recherches, ou moins de 3 secondes ?
