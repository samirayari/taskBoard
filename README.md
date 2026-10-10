# TaskBoard

TaskBoard est une petite API de gestion de tâches écrite en Python avec FastAPI.

C'est le **projet fil rouge** de la semaine de formation DevOps (M1 informatique). Cette version 1.0.0 est le point de départ : l'API fonctionne, elle est testée et documentée. Pendant les ateliers, vous la ferez évoluer avec Git, les tests automatisés, Docker et un pipeline d'intégration continue.

Le projet est volontairement simple :

- pas de base de données : les tâches sont gardées **en mémoire** ;
- pas d'interface graphique : on utilise la documentation interactive de l'API et `curl` ;
- peu de fichiers, faciles à lire.

## Sommaire

1. [Prérequis](#1-prérequis)
2. [Créer et activer un environnement virtuel](#2-créer-et-activer-un-environnement-virtuel)
3. [Installer les dépendances](#3-installer-les-dépendances)
4. [Lancer l'application](#4-lancer-lapplication)
5. [Documentation interactive](#5-documentation-interactive)
6. [Exemples de requêtes](#6-exemples-de-requêtes)
7. [Lancer les tests](#7-lancer-les-tests)
8. [Variables d'environnement](#8-variables-denvironnement)
9. [Structure du projet](#9-structure-du-projet)
10. [Problèmes fréquents](#10-problèmes-fréquents)

## 1. Prérequis

- **Python 3.12** ; vérifiez avec `python3.12 --version` (macOS/Linux) ou `py -3.12 --version` (Windows) ;
- **pip** (fourni avec Python) ;
- **curl** (déjà présent sous macOS, Linux et Windows 10/11) ;
- **Git**, pour récupérer le projet et pour les ateliers.

Toutes les commandes ci-dessous se lancent **depuis le dossier `taskboard`**, celui qui contient ce README.

## 2. Créer et activer un environnement virtuel

Un environnement virtuel (`.venv`) isole les dépendances du projet de celles du système.

### macOS / Linux

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

### Windows PowerShell

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
```

Une fois l'environnement activé, l'invite de commande commence par `(.venv)`. Pour en sortir, tapez `deactivate`.

> L'environnement doit être activé **dans chaque nouveau terminal** avant de lancer l'application ou les tests.

## 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

Le fichier `requirements.txt` contient des versions fixées :

| Paquet    | Rôle                                                 |
|-----------|------------------------------------------------------|
| `fastapi` | Framework de l'API (installe aussi Pydantic)         |
| `uvicorn` | Serveur qui exécute l'application                    |
| `httpx2`  | Client HTTP utilisé par le `TestClient` des tests    |
| `pytest`  | Lanceur de tests                                     |

## 4. Lancer l'application

### En développement (port 8000)

```bash
uvicorn app.main:app --reload --port 8000
```

- `app.main:app` désigne l'objet `app` du fichier `app/main.py` ;
- `--reload` redémarre le serveur automatiquement à chaque modification du code.

L'API répond sur <http://localhost:8000>. Arrêtez le serveur avec `Ctrl+C`.

### En écoutant sur toutes les interfaces (préparation de l'atelier Docker)

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Par défaut, Uvicorn n'écoute que sur `127.0.0.1` : seule la machine locale peut le joindre. Avec `--host 0.0.0.0`, il accepte aussi les connexions venant d'autres machines ou d'un conteneur. C'est nécessaire dans un conteneur Docker. Sans cette option, l'API resterait inaccessible depuis l'extérieur du conteneur.

### Deux limites importantes de cette version

- **Les données disparaissent au redémarrage.** Les tâches sont stockées en mémoire. Elles sont donc perdues à chaque arrêt du serveur, et aussi à chaque redémarrage automatique provoqué par `--reload`.
- **Un seul processus serveur.** Chaque processus a sa propre mémoire. N'utilisez pas l'option `--workers` : avec plusieurs processus, chacun aurait sa propre liste de tâches et les réponses deviendraient incohérentes. Une base de données, ajoutée lors d'un prochain atelier, lèvera ces deux limites.

## 5. Documentation interactive

Avec le serveur lancé, ouvrez dans un navigateur :

- **Swagger UI** : <http://localhost:8000/docs>. Cliquez sur une route, puis sur **Try it out** et **Execute** pour envoyer une vraie requête ;
- **ReDoc** : <http://localhost:8000/redoc>, une documentation en lecture seule ;
- **Schéma OpenAPI brut** : <http://localhost:8000/openapi.json>.

## 6. Exemples de requêtes

### Les routes

| Méthode  | Route           | Rôle                                   | Succès |
|----------|-----------------|----------------------------------------|--------|
| `GET`    | `/health`       | Vérifier que l'API fonctionne          | 200    |
| `GET`    | `/version`      | Nom et version de l'application        | 200    |
| `GET`    | `/tasks`        | Lister les tâches                      | 200    |
| `GET`    | `/tasks/{id}`   | Lire une tâche                         | 200    |
| `POST`   | `/tasks`        | Créer une tâche                        | 201    |
| `PATCH`  | `/tasks/{id}`   | Modifier le titre et/ou l'état         | 200    |
| `DELETE` | `/tasks/{id}`   | Supprimer une tâche (réponse sans corps) | 204  |

Une tâche a la forme suivante :

```json
{"id": 1, "title": "Apprendre Git", "completed": false}
```

- `id` est attribué automatiquement (1, 2, 3…) ;
- `title` est débarrassé des espaces de début et de fin, puis doit contenir entre 1 et 100 caractères ;
- `completed` vaut `false` à la création.

### Avec curl (macOS / Linux)

```bash
# État de l'API
curl http://localhost:8000/health
# {"status":"ok"}

# Version
curl http://localhost:8000/version
# {"name":"TaskBoard","version":"1.0.0"}

# Créer une tâche
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Apprendre Git"}'
# {"id":1,"title":"Apprendre Git","completed":false}

# Lister les tâches
curl http://localhost:8000/tasks
# [{"id":1,"title":"Apprendre Git","completed":false}]

# Lire une tâche
curl http://localhost:8000/tasks/1

# Marquer une tâche comme terminée
curl -X PATCH http://localhost:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'
# {"id":1,"title":"Apprendre Git","completed":true}

# Changer le titre
curl -X PATCH http://localhost:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"title": "Maîtriser Git"}'

# Supprimer une tâche (-i affiche le code HTTP : 204 No Content, sans corps)
curl -i -X DELETE http://localhost:8000/tasks/1
```

### Exemples d'erreurs

```bash
# Tâche inexistante → 404
curl -i http://localhost:8000/tasks/999
# {"detail":"Task 999 not found"}

# Titre composé uniquement d'espaces → 422
curl -i -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "   "}'
# {"detail":[{"type":"string_too_short","loc":["body","title"],
#             "msg":"String should have at least 1 character", ...}]}

# PATCH sans aucun champ → 422
curl -i -X PATCH http://localhost:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{}'
# ... "msg":"Value error, Provide at least one field: title or completed" ...
```

Codes HTTP utilisés :

| Code  | Signification                                                          |
|-------|------------------------------------------------------------------------|
| `200` | Succès                                                                 |
| `201` | Tâche créée                                                            |
| `204` | Tâche supprimée (pas de corps de réponse)                              |
| `404` | La tâche demandée n'existe pas                                         |
| `422` | Données invalides : titre vide ou trop long, identifiant non entier, JSON incorrect… |

### Sous Windows PowerShell

Dans PowerShell, `curl` peut être un alias vers `Invoke-WebRequest`, qui n'accepte pas les mêmes options. Utilisez **`curl.exe`** :

```powershell
curl.exe http://localhost:8000/health
```

Pour envoyer du JSON, le plus simple est d'utiliser `Invoke-RestMethod` :

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:8000/tasks `
  -ContentType "application/json" -Body '{"title": "Apprendre Git"}'

Invoke-RestMethod -Method Patch -Uri http://localhost:8000/tasks/1 `
  -ContentType "application/json" -Body '{"completed": true}'

Invoke-RestMethod -Method Delete -Uri http://localhost:8000/tasks/1
```

Vous pouvez aussi passer par la documentation interactive (<http://localhost:8000/docs>), qui fonctionne de la même façon sur tous les systèmes.

## 7. Lancer les tests

Avec l'environnement virtuel activé, depuis le dossier `taskboard` :

```bash
pytest          # résumé
pytest -v       # détail de chaque test
```

Résultat attendu : `19 passed`.

Les tests (`tests/test_api.py`) utilisent le `TestClient` de FastAPI : ils appellent l'API **sans lancer de serveur**. Avant chaque test, une fixture vide le stockage. Chaque test part donc d'une liste vide, quel que soit l'ordre d'exécution.

Pour lancer un seul test :

```bash
pytest tests/test_api.py::test_create_and_get_task
```

## 8. Variables d'environnement

L'application fonctionne **sans aucune configuration** et sans fichier `.env`. Deux variables permettent de changer les valeurs par défaut :

| Variable      | Valeur par défaut | Utilisation                                                |
|---------------|-------------------|------------------------------------------------------------|
| `APP_NAME`    | `TaskBoard`       | Nom renvoyé par `/version` et affiché dans `/docs`         |
| `APP_VERSION` | `1.0.0`           | Version renvoyée par `/version` et affichée dans `/docs`   |

Elles sont lues **au démarrage** du serveur. Après une modification, redémarrez-le.

macOS / Linux, pour une seule commande :

```bash
APP_NAME="TaskBoard Demo" APP_VERSION=1.0.1 uvicorn app.main:app --port 8000
```

Windows PowerShell, pour le terminal en cours :

```powershell
$env:APP_NAME = "TaskBoard Demo"
$env:APP_VERSION = "1.0.1"
uvicorn app.main:app --port 8000
```

Vérification :

```bash
curl http://localhost:8000/version
# {"name":"TaskBoard Demo","version":"1.0.1"}
```

## 9. Structure du projet

```
taskboard/
├── app/
│   ├── __init__.py      fait de app/ un paquet Python
│   ├── main.py          application FastAPI, configuration et routes
│   ├── models.py        modèles de requête et de réponse (validation)
│   └── store.py         stockage des tâches en mémoire
├── tests/
│   ├── __init__.py
│   └── test_api.py      tests de l'API
├── pytest.ini           configuration de pytest
├── requirements.txt     dépendances aux versions fixées
├── .gitignore           fichiers à ne pas versionner (.venv, caches…)
└── README.md
```

Les routes (`main.py`) ne savent pas comment les tâches sont stockées : elles passent uniquement par les méthodes de `store.py`. Pour utiliser une base de données plus tard, seul `store.py` devra être remplacé.

## 10. Problèmes fréquents

**`ModuleNotFoundError: No module named 'fastapi'`, ou `uvicorn` / `pytest` introuvable**
L'environnement virtuel n'est pas activé, ou les dépendances ne sont pas installées. Activez-le (section 2), vérifiez la présence de `(.venv)` dans l'invite, puis relancez `pip install -r requirements.txt`.

**`ModuleNotFoundError: No module named 'app'`, ou `Could not import module "app.main"`**
La commande est lancée depuis le mauvais dossier. Placez-vous dans le dossier `taskboard`, celui qui contient `app/` et ce README, puis relancez-la.

**`python3.12: command not found`, ou `py -3.12` ne trouve pas Python**
Python 3.12 n'est pas installé, ou pas sous ce nom. Installez-le depuis <https://www.python.org/downloads/> (ou avec le gestionnaire de paquets de votre système). Vérifiez ensuite avec `python3.12 --version`. Si l'environnement virtuel a été créé avec une autre version, supprimez le dossier `.venv` et recréez-le.

**Windows : « l'exécution de scripts est désactivée sur ce système » lors de l'activation**
PowerShell bloque le script d'activation. Autorisez les scripts locaux pour votre utilisateur, puis relancez l'activation :

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

**`[Errno 48] Address already in use` (macOS) ou `[Errno 98]` (Linux) : le port 8000 est occupé**
Un autre serveur, souvent un TaskBoard lancé dans un autre terminal, utilise déjà le port. Arrêtez-le avec `Ctrl+C` dans son terminal. Vous pouvez aussi lancer celui-ci sur un autre port avec `--port 8001`. Pour savoir quel processus occupe le port : `lsof -i :8000` (macOS/Linux) ou `netstat -ano | findstr :8000` (Windows).

**Mes tâches ont disparu**
C'est normal : le stockage est en mémoire. Les tâches sont perdues à chaque redémarrage, y compris lors d'un rechargement automatique avec `--reload` après une modification du code.

**Les réponses sont incohérentes : une tâche créée est parfois introuvable**
Le serveur tourne probablement avec plusieurs processus (`--workers 2` ou plus). Chaque processus a sa propre mémoire. Relancez le serveur sans `--workers`.

**Réponse `422 Unprocessable Entity`**
Les données envoyées sont invalides. Le champ `detail` de la réponse indique où se trouve l'erreur (`loc`) et pourquoi (`msg`). Causes fréquentes :
- titre vide, composé uniquement d'espaces, ou de plus de 100 caractères ;
- `PATCH` sans `title` ni `completed` ;
- identifiant non entier (`/tasks/abc`) ;
- JSON mal formé, ou en-tête `Content-Type: application/json` oublié.

Tous les messages d'erreur de l'API sont en anglais, comme le code.

**`test_version` échoue alors que le reste passe**
La variable `APP_VERSION` ou `APP_NAME` est sans doute définie dans votre terminal. Le test attend les valeurs par défaut (`TaskBoard`, `1.0.0`). Supprimez-la avec `unset APP_VERSION APP_NAME` (macOS/Linux) ou `Remove-Item Env:APP_VERSION, Env:APP_NAME` (PowerShell), puis relancez `pytest`.

**`curl` sous PowerShell renvoie une erreur sur `-X` ou `-H`**
Utilisez `curl.exe` au lieu de `curl`, ou `Invoke-RestMethod` (voir section 6).
