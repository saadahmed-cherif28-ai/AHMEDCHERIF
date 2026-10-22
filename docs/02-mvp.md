# Périmètre du MVP

## Hypothèse

Cette première version est conçue pour être testée avec des données fictives. On évite d’utiliser de vraies données d’alumni avant d’avoir préparé les accès, les sauvegardes et les règles de confidentialité.

## 1. Fonctionnalités indispensables

Le MVP contient au maximum cinq fonctionnalités, organisées pour réaliser un parcours complet.

1. **Connexion et accès selon le rôle.** Alumni, Étudiant, Service Alumni et Direction voient les pages qui leur sont destinées. Pour commencer, le service crée les comptes manuellement ; l’envoi automatique d’invitations par e-mail attendra.
2. **Profil alumni et consentement.** L’alumni saisit ou corrige son profil, donne son accord pour l’usage de ses données et soumet le profil. Les champs obligatoires et les doublons d’e-mail ou de matricule sont vérifiés.
3. **Contrôle et publication.** Le Service Alumni consulte les profils en attente, demande une correction avec un motif ou valide le profil. L’alumni peut corriger puis soumettre à nouveau. Seuls les profils validés et dont le consentement est actif sont publiés.
4. **Recherche et demande de contact.** L’étudiant recherche parmi les profils publiés avec quelques filtres prioritaires, puis envoie une demande de contact. L’adresse personnelle de l’alumni n’est pas affichée directement.
5. **Tableau de bord Direction.** Il calcule le nombre de profils recensés, leur complétude et leur fraîcheur, ainsi que le délai médian de validation. Les premières cibles proposées dans le rapport sont 70 % de profils recensés, 85 % de profils complets, 75 % de profils à jour et un délai médian inférieur à 3 jours.

## 2. Fonctionnalités utiles, mais reportées après le premier essai

- Invitations et notifications automatiques par e-mail.
- Import et export de fichiers CSV.
- Campagnes automatiques de relance des profils non actualisés.

L’invitation par e-mail est indiquée comme prioritaire dans un des documents. Elle est reportée ici pour simplifier le premier prototype : les comptes seront créés manuellement au début. La connexion et la protection des pages par rôle restent indispensables.

## 3. Fonctionnalités à faire plus tard

- Carte géographique des alumni.
- Mentorat, offres et événements.
- Recommandations par intelligence artificielle, déjà placées hors MVP dans le backlog.

## 4. Étapes de réalisation, de la plus simple à la plus complexe

1. Créer le projet avec une base de données locale et des données fictives.
2. Ajouter les comptes, les rôles et la connexion ; vérifier que chaque rôle ne voit que les pages autorisées.
3. Ajouter le formulaire du profil et l’enregistrement du consentement.
4. Vérifier les champs obligatoires et les doublons, puis faire passer un profil soumis à l’état « en attente ».
5. Créer la file de validation du Service Alumni, les motifs de correction et le renvoi d’un profil corrigé.
6. Publier uniquement les profils validés avec un consentement actif, puis créer la recherche avec les filtres prioritaires.
7. Enregistrer une demande de contact et permettre au service de la consulter.
8. Ajouter le tableau de bord et vérifier ses calculs avec des exemples connus.

## 5. Stack technique

La stack des documents (React, Vite, TypeScript et Tailwind pour l’interface ; FastAPI et Python pour le serveur ; PostgreSQL pour la base de données) est adaptée à une application qui doit grandir. Pour une personne débutante, elle demande toutefois de coordonner plusieurs outils et deux langages.

Pour démarrer plus simplement, il est proposé d’utiliser **Django avec ses pages HTML intégrées et SQLite en local**. Django fournit déjà la connexion, les rôles, l’administration et les formulaires ; les maquettes actuelles (formulaires, validation et tableau de bord) ne nécessitent pas une interface React séparée. PostgreSQL pourra remplacer SQLite avant une mise en production.

Pendant l’apprentissage, utiliser uniquement des données fictives. Avant de traiter de vraies données, préparer l’hébergement, les accès, les sauvegardes et les règles de confidentialité.
