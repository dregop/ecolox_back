# Projet Backend avec Flask

Ce projet est une application backend développée avec Flask

## Prérequis

Avant de commencer, assurez-vous d'avoir installé les éléments suivants :

- Python 3.x
- pip (pour installer les dépendances)

## Installation

1. **Clonez le dépôt :**
   Clonez ce projet sur votre machine locale via Git :
   ```bash
   git clone <URL_du_dépôt>
   cd <nom_du_dépôt>

2. Créez un environnement virtuel
   ```bash
   python3 -m venv venv

3. Installez les dépendances
   ```bash
   pip install -r requirement.txt

4. Définissez la variable FLASK_APP
   ```bash
   export FLASK_APP=./src/main.py

5. Lancer l'application (debug en environnement de développement)
   ```bash
   flask run --debug
