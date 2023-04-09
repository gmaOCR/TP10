# TP10 - Créez une API sécurisée RESTful en utilisant Django REST
TP10 d'openClassRoom - Publier une application permettant de remonter et suivre des problèmes techniques 
(issue tracking system).
---
## Installation

Utiliser [pip](https://pip.pypa.io/en/stable/) pour installer les dépendances.

Clonez le projet:
```bash
git clone https://github.com/gmaOCR/TP10.git
```
Créez et activez l'environnement virtuel:
```bash
pipenv shell
```
Installez les packages:
```bash
cd TP9
pip install -r requirements.txt
```
Appliquez les migrations si besoin:
```bash
python manage.py makemigrations
python manage.py migrate
```
Lancez le serveur:
```bash 
python manage.py runserver
```
---
## Web

Ouvrez votre navigateur favori et connectez vous sur: http://127.0.0.1:8000/

---
## Fonctionnalités

#### Un utilisateur peut :
*	se connecter et s’inscrire – le site ne doit pas être accessible à un utilisateur non connecté 
*	consulter un flux contenant les derniers tickets et les commentaires des utilisateurs qu'il suit, classés par ordre chronologique, les plus récents en premier ;
*	créer de nouveaux tickets pour demander une critique sur un livre/article ;
*	créer des critiques en réponse à des tickets ;
*	créer des critiques qui ne sont pas en réponse à un ticket. Dans le cadre d'un processus en une étape, l'utilisateur créera un ticket puis un commentaire en réponse à son propre ticket ;
*	voir, modifier et supprimer ses propres tickets et commentaires ;
*	suivre les autres utilisateurs en entrant leur nom d'utilisateur ;
*	voir qui il suit et suivre qui il veut ;
*	cesser de suivre un utilisateur.

#### Un développeur peut :
*	créer un environnement local en utilisant venv, et gérer le site en se basant sur la documentation détaillée présentée dans le fichier README.md.

#### Le site a :
*	une interface utilisateur correspondant à celle des wireframes ;
*	une interface utilisateur propre et minimale ;

---
## License
[GNU](https://choosealicense.com/licenses/gpl-2.0/)