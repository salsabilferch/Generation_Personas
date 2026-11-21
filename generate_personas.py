import argparse
import csv
import json
import random
import re
import uuid
import matplotlib.pyplot as plt
from collections import Counter

from collections import Counter
from datetime import date
from pathlib import Path

def lire_fichiers_synthea(dossier):

    patients = []

    for fichier in Path(dossier).rglob("*.json"):

        with open(fichier, "r", encoding="utf-8") as f:
            donnees = json.load(f)

        if donnees.get("resourceType") != "Bundle":
            continue

        patient = None
        conditions = []

        for entree in donnees.get("entry", []):

            ressource = entree.get("resource", {})

            if ressource.get("resourceType") == "Patient":
                patient = ressource

            elif ressource.get("resourceType") == "Condition":
                conditions.append(ressource)

        if patient is not None:

            patients.append({
                "patient": patient,
                "conditions": conditions
            })

    return patients

def calculer_age(date_naissance):

    naissance = date.fromisoformat(date_naissance)

    aujourd_hui = date.today()

    age = aujourd_hui.year - naissance.year

    if (aujourd_hui.month, aujourd_hui.day) < (naissance.month, naissance.day):
        age -= 1

    return age

def extraire_informations(patient):

    identifiant = patient.get("id")

    noms = patient.get("name", [])

    if noms:
        prenom = noms[0].get("given", [""])[0]
        nom = noms[0].get("family", "")
    else:
        prenom = ""
        nom = ""

    sexe = patient.get("gender")

    date_naissance = patient.get("birthDate")

    age = calculer_age(date_naissance) if date_naissance else None

    persona = {
        "id": identifiant,
        "prenom": prenom,
        "nom": nom,
        "sexe": sexe,
        "date_naissance": date_naissance,
        "age": age
    }

    return persona

def extraire_conditions(conditions):

    antecedents = []
    pathologies_actives = []
    statut_inconnu = []

    for condition in conditions:

        # 1. Récupérer le nom de la condition
        code = condition.get("code", {})
        nom = code.get("text")

        if not nom:
            codages = code.get("coding", [])
            if codages:
                nom = codages[0].get("display")

        if not nom:
            continue

        # 2. Conserver uniquement les maladies
        if "(disorder)" not in nom.lower():
            continue

        # Supprimer le suffixe pour un affichage plus lisible
        nom = nom.replace(" (disorder)", "")

        # 3. Récupérer le statut clinique
        statut = condition.get("clinicalStatus", {})
        codages_statut = statut.get("coding", [])

        codes = [
            c.get("code", "").lower()
            for c in codages_statut
        ]

        # 4. Vérifier si la maladie est terminée
        date_fin = (
            condition.get("abatementDateTime")
            or condition.get("abatementPeriod")
            or condition.get("abatementAge")
            or condition.get("abatementBoolean") is True
        )

        # 5. Classer la maladie
        if "resolved" in codes or "inactive" in codes or date_fin:
            antecedents.append(nom)

        elif "active" in codes or "recurrence" in codes:
            pathologies_actives.append(nom)

        else:
            statut_inconnu.append(nom)

    # 6. Supprimer les doublons
    antecedents = list(dict.fromkeys(antecedents))
    pathologies_actives = list(dict.fromkeys(pathologies_actives))
    statut_inconnu = list(dict.fromkeys(statut_inconnu))

    return antecedents, pathologies_actives, statut_inconnu

def analyser_population(personas):

    nombre = len(personas)

    if nombre == 0:
        print("Aucun persona à analyser.")
        return

    # 1. Calculer l'âge moyen
    ages = [
        p["age"]
        for p in personas
        if p["age"] is not None
    ]

    age_moyen = sum(ages) / len(ages) if ages else None

    # 2. Répartition par sexe enregistré
    sexes = Counter(
        p["sexe"] for p in personas
    )

    # 3. Patients avec des pathologies actives
    avec_pathologies = sum(
        1 for p in personas
        if len(p["pathologies_actives"]) > 0
    )

    # 4. Patients sans pathologie active identifiée
    sans_pathologies = nombre - avec_pathologies

    # 5. Compter les maladies actives
    maladies = Counter()

    for persona in personas:
        maladies.update(persona["pathologies_actives"])

    # 6. Afficher les statistiques
    print("\n===== STATISTIQUES DE LA POPULATION =====")

    print("Nombre de patients :", nombre)

    if age_moyen is not None:
        print("Âge moyen :", round(age_moyen, 1))

    print("\nRépartition par sexe enregistré :")
    for sexe, effectif in sexes.items():
        print(sexe, ":", effectif)

    print("\nPatients avec pathologies actives :", avec_pathologies)
    print("Patients sans pathologie active identifiée :", sans_pathologies)

    print("\nLes 10 pathologies actives les plus fréquentes :")

    for maladie, effectif in maladies.most_common(10):
        print(maladie, ":", effectif)

        # Répartition des professions
    professions = Counter(
        p["profession"] for p in personas
    )

    print("\nRépartition des professions :")

    for profession, effectif in professions.items():
        print(profession, ":", effectif)

    # Répartition des activités sportives
    activites = Counter(
        p["activite_sportive"] for p in personas
    )

    print("\nRépartition des activités sportives :")

    for activite, effectif in activites.items():
        print(activite, ":", effectif)

def attribuer_profession(persona, rng):

    age = persona["age"]

    if age is None:
        return "Non renseignée"

    if age <= 22:
        professions = [
            "Étudiant",
            "Étudiant",
            "Étudiant",
            "Personnel universitaire"
        ]

    elif age <= 26:
        professions = [
            "Étudiant",
            "Étudiant",
            "Doctorant",
            "Personnel universitaire"
        ]

    else:
        professions = [
            "Étudiant",
            "Doctorant",
            "Enseignant",
            "Personnel universitaire"
        ]

    return rng.choice(professions)

def attribuer_activite_sportive(persona, rng):

    age = persona["age"]

    if age is None:
        return "Non renseignée"

    if age <= 24:
        activites = [
            "Régulière",
            "Régulière",
            "Occasionnelle",
            "Occasionnelle",
            "Faible"
        ]

    else:
        activites = [
            "Régulière",
            "Occasionnelle",
            "Occasionnelle",
            "Faible",
            "Faible"
        ]

    return rng.choice(activites)

def enregistrer_personas(personas, dossier_sortie):

    dossier = Path(dossier_sortie)

    # Créer le dossier s'il n'existe pas
    dossier.mkdir(parents=True, exist_ok=True)

    # Parcourir les personas
    for persona in personas:

        identifiant = persona["id"]

        # Construire le nom du fichier
        nom_fichier = f"{identifiant}.json"

        chemin = dossier / nom_fichier

        # Enregistrer le persona
        with open(chemin, "w", encoding="utf-8") as f:

            json.dump(
                persona,
                f,
                indent=4,
                ensure_ascii=False
            )

    print(f"\n{len(personas)} personas enregistrés dans {dossier}")

def visualiser_population(personas):

    dossier = Path("resultats/graphiques")
    dossier.mkdir(parents=True, exist_ok=True)

    # 1. Distribution des âges
    ages = [p["age"] for p in personas if p["age"] is not None]

    plt.figure(figsize=(8, 5))
    plt.hist(ages, bins=range(18, 33), edgecolor="black")
    plt.title("Distribution des âges")
    plt.xlabel("Âge")
    plt.ylabel("Nombre de patients")
    plt.tight_layout()
    plt.savefig(dossier / "ages.png")
    plt.close()

    # 2. Répartition par sexe enregistré
    sexes = Counter(p["sexe"] for p in personas)

    plt.figure(figsize=(6, 6))
    plt.pie(
        sexes.values(),
        labels=sexes.keys(),
        autopct="%1.1f%%"
    )
    plt.title("Répartition par sexe enregistré")
    plt.tight_layout()
    plt.savefig(dossier / "sexes.png")
    plt.close()

    # 3. Répartition des professions
    professions = Counter(p["profession"] for p in personas)

    plt.figure(figsize=(9, 5))
    plt.bar(professions.keys(), professions.values())
    plt.title("Répartition des professions")
    plt.xlabel("Profession")
    plt.ylabel("Nombre de patients")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    plt.savefig(dossier / "professions.png")
    plt.close()

    # 4. Activité sportive
    activites = Counter(p["activite_sportive"] for p in personas)

    plt.figure(figsize=(8, 5))
    plt.bar(activites.keys(), activites.values())
    plt.title("Répartition des activités sportives")
    plt.xlabel("Niveau d'activité")
    plt.ylabel("Nombre de patients")
    plt.tight_layout()
    plt.savefig(dossier / "sport.png")
    plt.close()

    # 5. Pathologies actives les plus fréquentes
    maladies = Counter()

    for persona in personas:
        maladies.update(persona["pathologies_actives"])

    top_maladies = maladies.most_common(10)

    if top_maladies:
        noms, effectifs = zip(*top_maladies)

        plt.figure(figsize=(11, 6))
        plt.barh(noms[::-1], effectifs[::-1])
        plt.title("Les 10 pathologies actives les plus fréquentes")
        plt.xlabel("Nombre de patients")
        plt.tight_layout()
        plt.savefig(dossier / "pathologies.png")
        plt.close()

    print("\nGraphiques enregistrés dans :", dossier)

dossier = "resultats/fhir"

patients = lire_fichiers_synthea(dossier)

print("Nombre de patients trouvés :", len(patients))

personas = []
rng = random.Random(12345)
for donnees_patient in patients:

    patient = donnees_patient["patient"]

    conditions = donnees_patient["conditions"]

    persona = extraire_informations(patient)

    antecedents, pathologies_actives, statut_inconnu = extraire_conditions(conditions)

    persona["antecedents"] = antecedents
    persona["pathologies_actives"] = pathologies_actives
    persona["profession"] = attribuer_profession(persona, rng)
    persona["activite_sportive"] = attribuer_activite_sportive(persona, rng)

    personas.append(persona)

print("\nPremier persona extrait :")

if personas:
    print(json.dumps(personas[0], indent=2, ensure_ascii=False))

# Analyser les 100 patients
analyser_population(personas)

enregistrer_personas(personas, "resultats/personas")

visualiser_population(personas)