# Word Quest - Guide d'installation

Bienvenue dans le guide d'installation de Word Quest. Ce guide vous aidera à configurer votre environnement de développement et à lancer notre site avec succès. Si vous avez des questions ou rencontrez des problèmes, n'hésitez pas à nous contacter pour obtenir de l'aide supplémentaire.

## Table des Matières 📋
1. [Étapes Préliminaires](#étapes-préliminaires-)
2. [Installation de Wamp64](#installation-de-wamp64-)
3. [Clonage du Site](#clonage-du-site-)
4. [Installation des Modules Python](#installation-des-modules-python-)
5. [Ajout de la Base de Données](#ajout-de-la-base-de-données-)
6. [Ajout des Variables d'Environnement](#ajout-des-variables-d'environnement-)
7. [Lancement du Serveur](#lancement-du-serveur-)
8. [Auteurs](#auteurs-)
 
## Étapes Préliminaires 🛠️

Avant de commencer, assurez-vous d'avoir les élements suivants :
- Un ordinateur sous Windows
- Une connexion internet stable
- Python 3.8 ou supérieur

## Installation de Wamp64 📦

Pour installer Wamp64, suivez les étapes suivantes :
1. Rendez-vous sur le site officiel de Wamp64 : [Wamp64](https://www.wampserver.com/)
2. Lancez le programme d'installation et installez les composants nécessaires
> **Note :** Voici une page github qui vous aideras à installer les composants nécessaires :
> [Microsoft Visual C++ Redistributable Packages](https://gist.github.com/ChuckMichael/7366c38f27e524add3c54f710678c98b)
3. Une fois l'installation terminée, lancez WAMP64 depuis votre menu de démarrage.

## Clonage du Site 🌐

1. Ouvrez votre terminal
2. Naviguez jusqu'à votre dossier www de Wamp64
```bash
cd C:\wamp64\www\word_quest
```
3. Clonez le site depuis le repository
```bash 
git clone https://github.com/hpktz/word_quest
```

## Installation des Modules Python 🐍

1. Assurez vous d'avoir Python 3.8 ou supérieur installé sur votre machine
2. Ouvrez votre terminal
3. Naviguez jusqu'au dossier du site
```bash
cd C:\wamp64\www\word_quest\sources
```
4. Installez les modules nécessaires
```bash
pip install -r requirements.txt
```

## Ajout de la Base de Données 📊

1. Ouvrez votre navigateur et rendez-vous sur [phpMyAdmin](http://localhost/phpmyadmin/)
2. Connectez-vous avec les identifiants par défaut (login : root, mot de passe : vide)
3. Créez une nouvelle base de données nommée `word_quest`
4. Importez le fichier `sources/word_quest.sql` dans la base de données
> **Note :** La base contient des données de base pour le site (utilisateurs, scores, etc.). Cela permet de tester l'environnement complet du site.

## Ajout des Variables d'Environnement ⚙️

1. Créez un fichier `.env` dans le dossier `word_quest/sources`
2. Modifiez les variables d'environnement pour correspondre à votre configuration
```env
FLASK_SECRET_KEY=<VOTRE_CLE_SECRETE> - Clé secrète Flask (valeurs aléatoires recommandées)
COLLINS_API_KEY=<VOTRE_CLE_API_COLLINS> - Clé API Collins Dictionary
GOOGLE_SEARCH_API_KEY=<VOTRE_CLE_API_GOOGLE> - Clé API Google Custom Search Engine
GOOGLE_SEARCH_ENGINE_ID=<VOTRE_ID_MOTEUR_RECHERCHE_GOOGLE> - ID du moteur de recherche Google
EMAILING_SERVICE_PASSWORD=<VOTRE_MOT_DE_PASSE_EMAILING_SERVICE> - Mot de passe du compte de messagerie
EMAILING_SERVICE_TOKEN=<VOTRE_TOKEN_EMAILING_SERVICE> - Token Google Cloud pour taches Cron
DIRECTORY_PATH=sources/
DB_HOST=localhost
DB_NAME=word_quest
DB_USERNAME=root
DB_PASSWORD=
```

## Lancement du Serveur 🚀

1. Lancez WAMP64 depuis votre menu de démarrage
2. Ouvrez votre terminal
3. Naviguez jusqu'au dossier du site
```bash
cd C:\wamp64\www\word_quest\sources
```
4. Lancez le serveur
```bash
python main.py
```

Félicitations ! Vous avez maintenant configuré votre environnement de développement et lancé notre site avec succès. 🎉

Si vous rencontrez des problèmes ou avez des questions, n'hésitez pas à nous contacter pour obtenir de l'aide supplémentaire.

## Auteurs 📝

- **Hippolyte Pankutz** - *Développeur* - [hpktz](https://github.com/hpktz)
- **Abel Haller** - *Développeur* - [Abelouuu](https://github.com/Abelouuu)