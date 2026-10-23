# KPI, retour d'expérience et assistant carrière (IA)

Projet : SI Alumni EIGSICA — version Django, branche `version-django`.
Document rédigé le 23 octobre 2026.

Les valeurs de l'application actuelle sont celles des **données de démonstration**. Elles ne représentent pas les diplômés réels.

---

## 1. Tableau de KPI

| Indicateur | Définition | Cible | Valeur actuelle | Source |
|---|---|---|---|---|
| Taux d'alumni recensés | Profils validés / diplômés ciblés | ≥ 70 % | Non mesurable : référentiel absent (valeur provisoire de 10 diplômés) | Tableau de bord |
| Taux de profils complets | Profils validés avec filière, ville et pays / profils validés | ≥ 85 % | Non mesuré en réel (100 % sur 2 profils de démo) | Tableau de bord |
| Taux de profils à jour | Profils confirmés depuis moins de 12 mois / profils validés | ≥ 75 % | Non mesuré en réel | Tableau de bord |
| Délai médian de validation | Jours entre la soumission et la validation | ≤ 3 jours | Non mesuré en réel | Historique des statuts |
| Demandes de contact | Nombre de demandes envoyées par les étudiants | À fixer après un mois de test | 1 (démo) | Base de données |
| Consultations de l'annuaire | Recherches effectuées par semaine | À fixer après un mois de test | Non mesuré | À ajouter |
| Questions à l'assistant | Nombre de questions posées par semaine | À fixer après le pilote | Pas encore d'assistant | Journal anonymisé |
| Réponses jugées utiles | Pouce vers le haut / total des évaluations | ≥ 70 % | Pas encore d'assistant | Évaluation sous chaque réponse |
| Réponses sourcées | Réponses fondées sur des données agrégées / total | 100 % | Pas encore d'assistant | Contrôle manuel d'un échantillon |
| Signalements non traités | Réponses signalées sans suite | 0 | Pas encore d'assistant | Journal de signalement |

---

## 2. Retour d'expérience

### Ce qui a bien fonctionné
- Le parcours complet du MVP a été mis en place : connexion par rôle, profil avec consentement, validation, annuaire, fiche, tableau de bord.
- Les 28 tests automatisés passent sur la version Django.
- La vérification LinkedIn est réservée au service Alumni, et le texte collé n'est jamais enregistré.
- La démonstration vidéo couvre toutes les interfaces, par rôle, en mode clair et en mode sombre.

### Difficultés rencontrées
1. **Deux versions du projet** : une version Flask et une version Django ont coexisté. Les instructions du guide de démonstration ne correspondaient pas au projet Django, et il a fallu les réécrire.
2. **Identifiants incohérents** : les comptes de test utilisaient `@example.com` au lieu de `@example.test`, et les mots de passe avaient été modifiés à la main. La connexion échouait pour cette raison.
3. **Un commit local vidait le fichier de tests** (212 lignes supprimées). Il a été écarté avant toute publication.
4. **Encodage de `requirements.txt`** : le fichier est en UTF-16, ce qui peut empêcher l'installation des dépendances sur certains postes.
5. **Mode clair de la connexion** : titres et boutons illisibles sur fond blanc. Corrigé.
6. **Rendu hors connexion** : la page de connexion charge son style depuis un CDN. La vidéo a été enregistrée avec une copie locale du même moteur de style.
7. **Fichiers mal nommés** : une double extension (`.mp4.mp4`) a été créée à cause de l'extension masquée par Windows.

### Leçons à retenir
- Garder une seule version du projet, et une seule source de vérité pour la documentation.
- Documenter les identifiants à partir de la base réelle, et les vérifier avant de les publier.
- Ne jamais pousser un commit sans avoir regardé les fichiers supprimés (`git show --stat`).
- Afficher les extensions de fichiers dans l'explorateur Windows avant de renommer ou copier.
- Tester chaque étape dans le navigateur, en plus des tests automatisés.

---

## 3. Retours des utilisateurs et des personnes concernées

**Statut : à compléter.** Les retours n'ont pas encore été recueillis.

### Qui sera interrogé
- Service Alumni : 1 à 2 personnes
- Alumni : 2 à 3 personnes
- Étudiants : 2 à 3 personnes
- Direction : 1 personne

### Méthode proposée
Un entretien de 15 minutes, avec les 5 questions ci-dessous, et une démonstration de l'application.

### Questions
1. Avez-vous compris, sans aide, à quoi sert l'application ?
2. Quelle étape vous a semblé la plus simple, et laquelle la plus difficile ?
3. Vous sentez-vous à l'aise avec le consentement et la publication de vos données ?
4. Quelle fonctionnalité vous manque le plus ?
5. Feriez-vous confiance à un assistant qui répond à vos questions de carrière ? Pourquoi ?

### Tableau de synthèse

| Profil interrogé | Date | Point positif | Point à améliorer | Décision ou suite |
|---|---|---|---|---|
| Service Alumni | à compléter | à compléter | à compléter | à compléter |
| Alumni | à compléter | à compléter | à compléter | à compléter |
| Étudiant | à compléter | à compléter | à compléter | à compléter |
| Direction | à compléter | à compléter | à compléter | à compléter |

---

## 4. Intégration de l'IA : l'assistant carrière

### Principe
Un assistant de discussion, disponible pour les étudiants et les alumni connectés, qui répond aux questions sur les choix de carrière : filières, secteurs, premiers postes, évolutions, compétences demandées.

### Fonctionnement
1. L'utilisateur pose sa question dans une page **Assistant** (réservée aux rôles connectés).
2. Le serveur Django prépare un contexte : statistiques **agrégées et anonymisées** des profils validés (filières, secteurs et postes les plus fréquents, villes). Aucun nom ni identifiant n'entre dans ce contexte.
3. Le serveur envoie la question et ce contexte à un modèle d'IA par API. La clé est stockée dans une variable d'environnement, jamais dans le code.
4. La réponse s'affiche avec deux boutons : utile / pas utile, et signaler.
5. Chaque échange est enregistré sans identité, pour mesurer les KPI.

### Garde-fous
- Aucun nom, aucune photo, aucune donnée personnelle dans les réponses.
- Une statistique n'est affichée que si elle porte sur au moins 5 profils.
- Mention visible : « Conseil indicatif, il ne remplace pas un conseiller d'orientation. »
- L'assistant refuse les sujets hors carrière et renvoie vers le service Alumni.
- Une limite de questions par utilisateur et par jour.
- Toute réponse signalée est examinée par le service Alumni.

### Étapes de réalisation
1. **Page statique** : questions fréquentes proposées en boutons, réponses écrites à la main. Aucune IA.
2. **Premier appel API** : une seule question libre, réponse générique, sans données de la base.
3. **Contexte agrégé** : ajout des statistiques anonymisées de l'annuaire.
4. **Évaluation** : boutons utile / pas utile, journal anonymisé, mesure des KPI du tableau.

### Décisions à prendre
- Modèle d'IA : service externe payant par question, ou modèle installé sur l'école (plus de travail, mais aucune donnée envoyée à l'extérieur).
- Qui répond aux signalements, et dans quel délai.
- Accord des alumni : doivent-ils accepter que leurs parcours nourrissent les statistiques de l'assistant ?
