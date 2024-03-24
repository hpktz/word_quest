## > PRÉSENTATION GÉNÉRALE :

Word Quest est une **application web** novatrice conçue pour faciliter l’apprentissage ludique et attractif du vocabulaire anglais. Elle repose sur le principe des listes de vocabulaire.

### Naissance du projet :

En mars-avril 2023, lors de conceptualisation d’un projet dans le cadre de notre spécialité NSI, nous nous sommes engagés à éviter la redondance et la simplicité souvent associées aux jeux conçus à partir de tutoriels en ligne. Nous avons réfléchi à ce qui pourrait être réellement utile, ce qui nous a conduit à identifier une problématique centrale ! Comment rendre l’apprentissage d’une liste de vocabulaire à la fois divertissant et captivant ? Notre objectif était surtout de proposer à l’utilisateur de créer ses propres listes sur notre site, il pouvait ainsi chercher ses mots et les ajouter à sa liste.

Dans cette optique, nous avons développé une première version de l’application que nous avons présentée en classe. Bien qu’étant bien structurée, cette version présentait des lacunes importantes. En effet, elle manquait d’attrait visuel et ressemblait trop à Duolingo. Nos leçons étaient trop similaires à celles proposées par l’application (leçons de compréhension, de prononciation, d’assimilation, d’écriture, etc.). De plus, l'interface était fort ressemblante.

### Changement de cap :

Face aux insuffisances de la première version, nous avons changé notre approche de l'apprentissage en abandonnant les leçons type “Duolingo” au profit de divers mini-jeux. Désormais, le système génère un parcours comprenant six jeux différents pour assimiler une liste de vocabulaire, offrant ainsi une expérience plus ludique et efficace.
# Projet Word Quest

Ce changement n'est que le début d'une *transformation majeure* de notre projet. Nous avons intégré un système complet d'XP de vie et de gemmes faisant de chaque session une aventure captivante. À la clôture de chaque leçon, les utilisateurs sont récompensés par des XP et voient leur vie diminuer en cas d'erreur majeure. De plus, des objectifs ont été incorporés à chaque liste de vocabulaire, offrant ainsi des gemmes en guise de récompense à leurs accomplissements. Une fois les vies de l'utilisateur épuisées, un court délai de 15 minutes est imposé avant de pouvoir continuer, à moins d'utiliser les gemmes pour acheter des vies supplémentaires. Parallèlement, les XP permettent de gravir les échelons d'un classement global ajoutant une dimension captivante à l'expérience. ✨🏆

Nous avons non seulement travaillé sur l'aspect psychologique de notre application pour que les utilisateurs prennent du plaisir à revenir, mais nous avons aussi mis en œuvre une interface dynamique, un design moderne et élégant, ainsi que de multiples animations pour rendre chaque interaction aussi agréable que possible. 💻🎨🎉

En ce qui concerne les listes de vocabulaire, nous avons introduit un système de partage de liste et de profil. Si un profil est rendu public ou si un utilisateur est abonné à vous, vous aurez accès à ses statistiques et à ses listes. De même les listes publiques sont désormais visibles dans l'onglet découverte, où un algorithme de recommandation vous présente les listes les plus susceptibles de vous intéresser, offrant une expérience personnalisée et enrichissante. 📚🔍🤝

## Réponse originale à un besoin :

Notre objectif était de créer un produit *unique et fort de sens*. Alors que de nombreuses applications d’apprentissage de l’anglais existent, imposant généralement les mots à l'utilisateur, peu d’entre elles offrent la possibilité de générer un parcours personnalisé et aucune ne propose l’utilisation de mini-jeux comme méthode d’apprentissage. 🌟🎮

## Organisation du travail :

### L'équipe : 

- **Abel Haller**: chargé du développement global des mini-jeux (Jeu du Pendu, Jeu du Snake, Jeu du Memory, etc.)
- **Hippolyte Pankutz** : chargé du développement global de l’application (structure de l’application flask, dashboard, système de classement, etc.)

### Répartition des tâches :

Du début jusqu’à la fin du projet, nous n’avons cessé de toujours communiquer pour garder une application uniforme. Hippolyte, ayant déjà eu des projets web par le passé à commencé à définir une charte graphique précise, et designer le style principal du dashboard. Nous avons par la suite beaucoup discuté d’éventuelles améliorations visuelles pour en arriver au résultat actuel.

Par la suite Abel, débutant en front-end et nourri par le profond désir d’apprendre, s’est chargé de la réalisation de squelette fonctionnel pour les jeux de notre application. Il a beaucoup appris sur la création artistique en css et sur les interactions js.

Hippolyte s’est, par la suite, attaqué au squelette du site et à la réalisation du dashboard, la partie sécurité a été prise au sérieux. En parallèle, Abel a continué à produire des jeux et les a connectés au site et créant une relation CLIENT-SERVEUR pour “sécuriser” les jeux afin d’éviter toute triche. 💪👨‍💻

### Technologies utilisées :

Pour la réalisation des maquettes du site nous avons utilisé Lunacy qui est gratuit et qui propose une large gamme de possibilités en termes de design et qui est, de surcroît, collaboratif avec un système de partage. 

Pour ce qui est de la communication, nous avons utilisé Discord et Notion, qui nous ont permis de nous parler lorsque nous étions chez nous, et de planifier les différentes échéances du projet.

Enfin, pour ce qui est du code, nous avons utilisé git et l’interface github pour gérer les différentes versions. Pour faire tester notre projet, nous avons utilisé GCloud pour la phase bêta. 🎨📱🔧

## Les étapes du projet :

- **Avril - Mai 2023 :** Emergence de l’idée et du besoin de l’application, création de la première version.
- **Août - Sept 2023 :** Départ à zéro. On définit le fil directeur de l’application, et on commence à la designer sur Lunacy. La charte graphique et les jeux à créer sont définis. Les objectifs sont fixés. 
- **Oct - Déc 2023 : (PRE-ALPHA)** Réalisation de multiples “templates” en html et css pour voir ce dont on est capable et réajustement des objectifs. Apprentissage du système flask pour python.
- **Jan - Mars 2024 : (ALPHA)** Développement complet de l’application sur les bases établies aux étapes précédentes.
- **Mars 2024 : (BETA - v1.0)** Mise en ligne de la version bêta de l’application, et prise en compte des retours pour l’amélioration de l’application. En parallèle, documentations du projet en vue du concours.
- **Fin Mars 2024 : (PRODUCTION - v1.1)** Finalisation complète de l’application, tous les problèmes apparents sont réglés. 📆🚀

## Fonctionnement et opérationnalité :

Le projet est opérationnel à 100% au moment du dépôt du dossier. Tout a été testé par la communauté et par nous-même. Nous sommes arrivés au niveau de nos objectifs fixés plus tôt dans l’année.

Pour vérifier l’absence de bug apparent, nous avons du différencier deux types d’erreurs. Les bugs simples, comme un problème d’affichage ou un jeu qui crachait, et les failles de sécurité. Pour ce qui est des bugs simples, nous avons nous même imaginé et testé une grande partie des possibilité, puis notre communauté s’en est chargé et leur retour nous ont permis d’améliorer notre système.

Pour ce qui est des failles critiques, nous avons réaliser des tests de sécurité : 
- Cloud Web Security Scanner (Google) : pas de faille détectée
- ImmuniWeb : Grade A obtenu

De plus, notre page d'accueil sur PageSpeed Insights (Google), obtient un score moyen de 95% pour sa version mobile et de 99% pour sa version bureau, révélateur alors de notre souci de bien faire en ce qui concerne la mise en page et la sécurité de notre site. Ces scores lui permettront de remonter dans les recherches Google pour une meilleure visibilité. 🔒🔍🚀

Les seules difficultés rencontrées furent lors de la phase PRE-ALPHA lorsque nous devions tester nos capacités, elles ont été vite résolues et rien ne nous a vraiment bloqué par l’avenir.

## Ouverture :

### Critiques et améliorations

Nous avons achevé la version grand public fonctionnelle de notre projet, mais cela ne signifie pas que notre application est exempte de défaut. Tout d'abord bien que nous offrons plusieurs mini-jeux, leur nombre reste limité pour assurer une diversité significative.

Notre objectif est clair, ajouter de nouveaux mini-jeux à l'avenir afin de maintenir l'intérêt des utilisateurs et d'éviter la redondance. En ce qui concerne les profils publics bien qu'ils aient été intégrés, leurs fonctionnalités restent limitées ne permettant pas une interaction significative entre les utilisateurs. Nous envisageons d'implémenter un système de messagerie ou d'envoi d'encouragement pour favoriser l'engagement des utilisateurs.

Par ailleurs, nos listes et parcours manquent de personnalisation. Bien que nous adaptions les parcours au niveau de l'utilisateur, leur similitude nuit à l'expérience. Nous envisageons d'améliorer cela en ajoutant des illustrations thématiques à chaque liste et en intégrant artistiquement le parcours. De plus, notre API actuel pour la création de liste de vocabulaire ne nous fournit pas toujours des exemples associés aux mots, limitant ainsi les possibilités de jeux. Nous envisageons d'intégrer prochainement l'intelligence artificielle dans notre site en utilisant les modèles de langage Gemini Pro de Google Vertex AI, pour fournir des exemples diversifiés et détecter les thèmes dans les mots choisis, permettant ainsi d'ajouter des illustrations pertinentes.

Cependant, cette amélioration entraînerait des coûts supplémentaires ce qui nous obligerait à ne plus proposer notre application gratuitement. Bien que les tarifs de Gemini Pro soient abordables, un grand volume de requête peut entraîner des frais considérables. Nous devons également reconnaître que facturer notre application irait à l'encontre de notre engagement éducatif. Limiter les fonctionnalités des comptes gratuits pourrait être une alternative. 💡💰

### Compétences acquises et leçons à retenir

Nous sommes satisfaits des résultats obtenus et considérons notre approche comme étant la bonne. Cependant, nous reconnaissons qu’une planification plus précoce aurait permis de maximiser les fonctionnalités, et une meilleure coordination sur certaines structures telles que les données, les relations CLIENT-SERVEUR, et l’utilisation de Flask en général, aurait réduit les pertes de temps.

Initialement peu familiers avec Flask, nous n'étions pas conscients de la possibilité de créer des sites avec Python. Par conséquent, nous avons exploité nos connaissances existantes (telles que la programmation orientée objet, les recherches dichotomiques, les listes et dictionnaires) et nous les avons enrichies avec des nouveaux éléments (Flask et ses sous-jacents). Ce projet nous a permis de développer des compétences et des réflexes essentiels pour notre avenir professionnel. 

Enfin, notre projet favorise l'inclusion en permettant le partage de liste de vocabulaire entre utilisateurs, cela crée une communauté d'apprentissage collaboratif où chacun peut contribuer et bénéficier des connaissances des autres, favorisant ainsi le développement inclusif et collaboratif. 🌍🤝📚
