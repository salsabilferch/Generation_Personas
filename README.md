# Génération de personas de patients — Projet IAFA

## Objectif

Générer une population synthétique de 100 patients âgés de 18 à 30 ans à l'aide de Synthea, puis extraire et enrichir leurs caractéristiques pour une simulation en environnement universitaire.

## 1. Installation

Ouvrir un terminal dans le dossier du projet.

**Créer un environnement virtuel :**

```bash
python3 -m venv .venv
```

**Activer l'environnement :**

```bash
source .venv/bin/activate
```

**Installer Synthea (paquet Python tietai-synthea) :**

```bash
python3 -m pip install tietai-synthea
```

**Installer Matplotlib pour les graphiques :**

```bash
python3 -m pip install matplotlib
```

Ou installer toutes les dépendances en une seule commande :

```bash
python3 -m pip install -r requirements.txt
```

**Vérifier l'installation de Synthea :**

```bash
synthea --help
```

## 2. Générer les 100 patients

Exécuter la commande :

```bash
synthea -p 100 -a 18-30 -s 12345 -o ./resultats
```

- `-p 100` : générer 100 patients.
- `-a 18-30` : définir la tranche d'âge de 18 à 30 ans.
- `-s 12345` : utiliser une graine fixe pour la reproductibilité.
- `-o ./resultats` : définir le dossier de sortie.

Les fichiers FHIR JSON seront générés dans `resultats/fhir/`.

## 3. Générer et analyser les personas

Exécuter :

```bash
python3 generate_personas.py
```

Ce script permet d'extraire les informations démographiques et médicales, d'ajouter une profession et une activité sportive, de calculer des statistiques et de créer des graphiques.

## 4. Résultats

```text
resultats/
├── fhir/        # Données médicales Synthea
├── personas/    # Personas enrichis
└── graphiques/  # Graphiques statistiques
```

## 5. Vérifier le nombre de personas

```bash
find resultats/personas -name "*.json" | wc -l
```

Résultat attendu : **100 personas**, si la génération et l'extraction se sont déroulées correctement.

## 6. Limites

Les professions et les activités sportives sont actuellement générées selon des règles probabilistes provisoires. Une validation de la cohérence de la population reste nécessaire.