# Maps 2.0

A partir des coordonnées GPS d’une personne et de l’adresse à laquelle elle veut se rendre et de certains critères, indiquer à l’utilisateur s’il vaut mieux prendre un Vélib’, une autolib’ ou le métro.
On se limitera à la ville de Paris et on se concentrera sur des critères tels que : la météo, les stations de métro/vélib/autolib à proximité du lieu de départ et d’arrivée, la charge à porter, etc…
Une interface graphique n’est pas obligatoire pour ce projet.

## 1. Présentation et fonctionnalités
TO DO

## 2. POOA
![GitHub Logo](/static/images/uml.png)
Format: ![Alt Text](png)


## 3. Utilisation

### Installation

Les librairies nécéssaires sont indiquées dans le fichier ```requirements.txt```
Pour les installer, il suffit de se placer dans le dossier maps_2.0, et d'éxécuter la commande suivante:

#### Pour Linux
```
pip install -r requirements.txt
```
**Solution alternative :** utiliser l'environnement virtuel présent dans l'archive zip via la commande 
```
source (maps_2.0 folder)/venv/bin/activate
```

#### Windows
```
python -m pip install -r requirements.txt 
```

### Lancement du serveur
Dans le dossier du projet, executer le fichier 
```__main__.py```
via la commande :
```python __main__.py```
**Remarque :** le paramètre ```--debugger``` ou ```-d``` à l'exécution permet de lancer le programme en mode débugger, avec des logs plus détaillés

Le serveur Flask démarre alors, et les logs sont visibles en console.
L'application est accessible depuis un navigateur web via l'url donnée en console (par défault: http://127.0.0.1:5000/).



