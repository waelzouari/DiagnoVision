# Prompt pour générer la présentation PowerPoint DiagnoVision

## Rôle

Tu es un expert en pitch de startups HealthTech, storytelling produit, design de présentations et communication scientifique responsable. Génère une présentation PowerPoint `.pptx` professionnelle pour présenter le prototype **DiagnoVision** devant un jury.

La présentation doit être rédigée principalement en **français**, avec quelques libellés produit anglais conservés lorsqu’ils apparaissent dans l’interface, par exemple `Voice Agent`, `Document Agent` et `Priority Agent`.

## Objectif

Présenter DiagnoVision comme un prototype Web d’aide à la documentation et à la revue médicale qui :

1. enregistre une conversation médecin–patient après consentement explicite ;
2. transforme la conversation en transcription structurée ;
3. nettoie les données vocales et préserve les négations médicales ;
4. extrait des informations utiles de documents médicaux synthétiques ;
5. fusionne les informations vocales, documentaires et longitudinales par patient ;
6. présente des hypothèses de risque explicables, jamais comme des diagnostics ;
7. génère un score transparent de **priorité de revue du dossier** ;
8. laisse systématiquement la décision et la validation finales au médecin.

## Contrainte de durée

La présentation orale complète doit durer **exactement 5 minutes maximum**, questions non comprises.

- Prévoir environ **4 minutes 40 secondes de contenu**.
- Garder **20 secondes de marge** pour les transitions ou un ralentissement pendant la vidéo.
- Une vidéo de démonstration de **1 minute** sera intégrée dans une slide.
- Générer des notes orateur brèves pour chaque slide.
- Les notes doivent indiquer le temps cible et un texte oral naturel.

## Format attendu

- Créer **7 slides maximum**.
- Format panoramique **16:9**.
- Style médical moderne, sobre, desktop-first et crédible.
- Palette principale :
  - vert médical foncé `#0F766E` ;
  - turquoise `#14B8A6` ;
  - bleu nuit `#0F172A` ;
  - fond clair `#F8FAFC` ;
  - ambre pour les avertissements ;
  - rouge uniquement pour les priorités élevées ou les risques.
- Typographie sans-serif moderne, très lisible.
- Utiliser de grandes valeurs numériques, des icônes simples et peu de texte.
- Éviter les paragraphes longs.
- Ne jamais utiliser d’image de vrai patient.
- Utiliser uniquement des illustrations abstraites, des pictogrammes médicaux ou des captures du prototype avec données synthétiques.
- Ajouter un petit footer sur chaque slide : `Prototype de recherche · Données synthétiques · Validation médicale obligatoire`.

## Message central

Le message principal doit être :

> DiagnoVision transforme des conversations et documents médicaux synthétiques en un dossier structuré, traçable et priorisé, afin d’aider le médecin à revoir les cas importants sans remplacer son jugement clinique.

## Structure obligatoire des slides

### Slide 1 — Titre et proposition de valeur

**Temps oral : 20 secondes**

Titre :

> DiagnoVision

Sous-titre :

> De la conversation clinique à une revue patient structurée et priorisée

Afficher visuellement le flux simplifié :

```text
Conversation + Documents → Données structurées → Revue priorisée
```

Ajouter les mentions :

- prototype Web HealthTech ;
- données exclusivement synthétiques ;
- médecin toujours dans la boucle.

Notes orateur suggérées :

> DiagnoVision est un espace clinique Web qui aide à transformer les conversations et documents médicaux en informations structurées, puis à présenter au médecin les dossiers qui méritent une revue prioritaire.

### Slide 2 — Le problème et les statistiques

**Temps oral : 40 secondes**

Titre :

> Le médecin soigne, mais il doit aussi documenter

Présenter trois statistiques avec de grands chiffres :

1. **49,2 %** du temps de travail ambulatoire observé était consacré au dossier électronique et au travail de bureau, contre **27 %** au contact clinique direct avec les patients.
2. Les erreurs diagnostiques représentent environ **16 %** du préjudice évitable dans les soins.
3. Les erreurs médicamenteuses représentent un coût mondial estimé à **42 milliards USD par an**.

Relier les statistiques au problème sans prétendre que DiagnoVision les résout directement :

- données fragmentées entre conversation, documents et historique ;
- charge de documentation ;
- information importante difficile à prioriser ;
- risque de manquer une contradiction ou une donnée absente.

Ajouter les sources en petit, mais lisibles :

- Sinsky et al., *Annals of Internal Medicine*, 2016, PMID 27595430 : <https://pubmed.ncbi.nlm.nih.gov/27595430/>
- OMS, *World Patient Safety Day 2024* : <https://www.who.int/campaigns/world-patient-safety-day/world-patient-safety-day-2024>
- OMS, *Medication Without Harm* : <https://www.who.int/initiatives/medication-without-harm/>

Notes orateur suggérées :

> La difficulté n’est pas seulement d’obtenir des données, mais de les rassembler et de les rendre exploitables. Les médecins consacrent une part importante de leur temps à l’EHR, tandis que les erreurs diagnostiques et médicamenteuses restent une composante majeure de la sécurité des soins. Notre prototype explore une meilleure organisation de l’information, sans revendiquer une réduction clinique déjà démontrée.

### Slide 3 — La solution et le parcours utilisateur

**Temps oral : 35 secondes**

Titre :

> Un parcours unique autour du patient

Créer un diagramme horizontal en cinq étapes :

```text
1. Consentement et enregistrement
2. Transcription et data cleaning
3. Lecture des documents
4. Fusion des données patient
5. Hypothèses et priorité de revue
```

Sous chaque étape, afficher une courte phrase :

- enregistrement local dans la démo ;
- suppression des hésitations et normalisation des unités ;
- OCR/extraction simulée des rapports ;
- provenance et contradictions conservées ;
- résultats soumis au médecin.

Ne pas utiliser le mot « diagnostic automatique ».

### Slide 4 — Architecture multi-agents simulée

**Temps oral : 40 secondes**

Titre :

> Cinq agents spécialisés, une validation humaine

Présenter les cinq composants sous forme de cartes reliées :

1. **Voice Agent**
   - symptômes ;
   - durée ;
   - médicaments ;
   - négations.
2. **Document Agent**
   - analyses biologiques ;
   - valeurs et unités ;
   - conclusions de rapports de scanner.
3. **Fusion Agent**
   - rapproche les sources ;
   - détecte les contradictions ;
   - conserve la provenance.
4. **Risk Agent**
   - produit des hypothèses explicables ;
   - signale les informations manquantes ;
   - s’abstient lorsque les données sont insuffisantes.
5. **Priority Agent**
   - calcule un score transparent de priorité de revue ;
   - explique chaque point attribué.

Afficher clairement un encadré :

> Dans le prototype actuel, ces agents et résultats sont simulés par des scénarios frontend statiques. Aucun modèle médical réel n’est déployé.

### Slide 5 — Démonstration vidéo

**Temps total : 1 minute 10 secondes**

- Introduction orale avant lecture : **10 secondes**.
- Vidéo : **1 minute maximum**.

Titre :

> Démonstration : du patient au dossier priorisé

Créer une grande zone vidéo occupant environ 75 % de la slide.

Ajouter un emplacement média explicitement nommé :

```text
[INSÉRER ICI LA VIDÉO DE DÉMONSTRATION — DURÉE 1:00]
Fichier attendu : demo-diagnovision-60s.mp4
```

Ajouter sous la vidéo une mini-frise :

```text
Patient → Enregistrement → Data cleaning → Documents → Risques → Score
```

Si l’outil de génération peut intégrer une vidéo dans PowerPoint :

- intégrer `demo-diagnovision-60s.mp4` ;
- ne pas lancer automatiquement la vidéo ;
- afficher une miniature avec un bouton de lecture visible ;
- conserver un fallback sous forme d’image si le codec vidéo n’est pas supporté.

Si le fichier vidéo n’est pas fourni, créer uniquement le placeholder sans inventer de contenu vidéo.

Notes orateur suggérées avant la vidéo :

> Cette démonstration montre le parcours complet avec des données synthétiques : sélection du patient, enregistrement, nettoyage de la transcription, fusion des documents, hypothèses explicables et score de priorité.

### Slide 6 — Résultat de la démo et métriques du prototype

**Temps oral : 35 secondes**

Titre :

> Une revue explicable, pas une boîte noire

Présenter un exemple patient synthétique :

```text
Sami Gharbi — Score de priorité de revue : 82/100
```

Montrer les raisons :

- fatigue et vertiges rapportés ;
- hémoglobine synthétique à 9,2 g/dL, signalée basse ;
- tension synthétique en hausse : 124 → 139 → 154 mmHg ;
- ferritine et historique des saignements manquants ;
- hypothèse affichée : « possible pattern compatible avec une anémie — à évaluer ».

Présenter séparément les **métriques internes du prototype**, sans les appeler performances cliniques :

- **5** profils patients synthétiques ;
- **5** agents simulés dans l’interface ;
- **5** types de scénarios : amélioration, dégradation, stabilité, contradiction et données insuffisantes ;
- **8/8** tests frontend réussis au dernier passage de validation ;
- **0** donnée patient réelle utilisée.

Ajouter une mention visible :

> Ces chiffres décrivent la couverture fonctionnelle de la démo, pas la précision médicale d’un modèle.

### Slide 7 — Valeur, limites et prochaine étape

**Temps oral : 40 secondes**

Titre :

> Aujourd’hui : une preuve de parcours. Demain : une validation scientifique.

Créer trois colonnes :

#### Valeur démontrée

- interface centrée patient ;
- information multi-source structurée ;
- provenance visible ;
- score explicable ;
- médecin dans la boucle.

#### Limites assumées

- données synthétiques ;
- agents simulés ;
- aucune performance clinique revendiquée ;
- aucune certification de dispositif médical.

#### Roadmap

- intégrer speech-to-text et OCR réels ;
- constituer un dataset légal et documenté ;
- définir les outcomes et protocoles de validation ;
- mesurer sensibilité, spécificité, calibration et biais ;
- réaliser une étude prospective avec supervision médicale et réglementaire.

Terminer avec la phrase :

> Notre ambition n’est pas de remplacer le médecin, mais de lui rendre le contexte clinique plus clair, plus traçable et plus rapide à revoir.

## Répartition temporelle obligatoire

| Slide | Durée cible |
|---|---:|
| 1. Titre | 0:20 |
| 2. Problème et statistiques | 0:40 |
| 3. Solution | 0:35 |
| 4. Architecture agents | 0:40 |
| 5. Vidéo | 1:10 |
| 6. Résultats de la démo | 0:35 |
| 7. Limites et roadmap | 0:40 |
| **Total planifié** | **4:40** |
| **Marge** | **0:20** |

La marge de 20 secondes doit être préservée sans raccourcir la vidéo.

## Exigences relatives aux statistiques

- Ne présenter que les trois statistiques externes indiquées dans ce prompt.
- Afficher l’année, le contexte et la source.
- Ne jamais transformer une association en causalité.
- Ne jamais affirmer que DiagnoVision réduit déjà les erreurs, le temps administratif, les hospitalisations ou les coûts.
- Distinguer visuellement :
  - **statistiques externes du problème** ;
  - **métriques techniques internes du prototype** ;
  - **aucune métrique de performance clinique disponible**.

## Exigences de sécurité médicale

Ne jamais écrire que DiagnoVision :

- diagnostique une maladie ;
- prédit avec certitude les maladies futures ;
- remplace le médecin ;
- est cliniquement validé ;
- est certifié comme dispositif médical ;
- garantit la confidentialité de vraies données médicales ;
- possède un score d’urgence médicale validé.

Utiliser les formulations suivantes :

- « hypothèse de risque à examiner » ;
- « priorité de revue du dossier » ;
- « résultat synthétique simulé » ;
- « données insuffisantes — abstention » ;
- « validation médicale obligatoire ».

## Livrables demandés à l’agent

Produire :

1. un fichier `.pptx` éditable ;
2. une version PDF de secours ;
3. les notes orateur dans chaque slide ;
4. un tableau récapitulatif des temps par slide ;
5. une liste des sources dans les notes de la slide 2 ;
6. un placeholder vidéo clairement identifiable si le MP4 n’est pas disponible ;
7. aucune donnée médicale réelle ni image identifiable de patient.

Avant de livrer, vérifier :

- absence de débordement ou texte coupé ;
- lisibilité depuis une salle de jury ;
- cohérence des couleurs et icônes ;
- total oral inférieur ou égal à 5 minutes ;
- présence de la slide vidéo de 1 minute ;
- présence des sources des statistiques ;
- distinction claire entre prototype fonctionnel et système médical validé.
