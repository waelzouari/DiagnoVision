# DiagnoVision — passation complète pour la prochaine session ChatGPT

> Dernière mise à jour : 22 novembre 2026 (Africa/Tunis)  
> Statut : MVP full-stack fonctionnel en développement, avec vertical slice principal implémenté et filtres avancés ajoutés.  
> Contrainte absolue : application Web professionnelle desktop-first uniquement. Ne pas introduire Flutter, Dart, React Native ou une application mobile/native.

## 1. But de ce document

Ce fichier est destiné à être donné tel quel à une nouvelle session ChatGPT/Codex. Il décrit :

- ce qui a réellement été développé ;
- les choix d'architecture et les contrats déjà établis ;
- les commandes de lancement et de validation ;
- les résultats de tests réellement observés ;
- les incohérences et limites connues ;
- les prochains travaux, classés par priorité ;
- les règles de sécurité et de sûreté médicale à préserver.

La nouvelle session doit commencer par lire ce document, puis les fichiers de `docs/`, avant de modifier le code.

## 2. Résumé exécutif

Le dépôt était initialement vide. Un monorepo DiagnoVision a été créé avec :

- un frontend React 18 + TypeScript strict + Vite + Tailwind CSS ;
- des composants accessibles de style shadcn/ui basés sur Radix UI ;
- React Router, TanStack Query, Axios, React Hook Form, Zod, Recharts et Lucide ;
- un backend Python/FastAPI + SQLAlchemy 2 + Pydantic ;
- authentification par JWT en cookies HttpOnly, refresh, CSRF et contrôle d'accès médecin/patient ;
- gestion des patients synthétiques ;
- consultations manuelles, audio, `MediaRecorder` et WebSocket natif ;
- providers IA déterministes de démonstration pour transcription, extraction, analyse et OCR ;
- workflow brouillon IA → correction médecin → approbation ;
- analyses longitudinales et tendances déterministes ;
- documents médicaux et extraction de démonstration ;
- PostgreSQL/pgvector, Redis, Celery, Celery Beat, MinIO, Nginx et Docker Compose ;
- migrations Alembic, CI GitHub Actions et tests backend/frontend ;
- filtres avancés frontend et backend, appliqués après contrôle d'autorisation.

Ce MVP est un prototype de recherche/hackathon. Il ne doit jamais être présenté comme un dispositif médical, un diagnostic autonome, une solution cliniquement validée ou une solution certifiée de confidentialité médicale.

## 3. Arborescence principale

```text
DiagnoVision/
├── frontend/                 # React/TypeScript/Vite
│   ├── src/app/              # Router, providers, layout, auth
│   ├── src/components/       # Composants UI partagés
│   ├── src/features/         # Auth, dashboard, patients, consultations,
│   │                         # analyse, documents, paramètres
│   ├── src/hooks/            # MediaRecorder et WebSocket
│   ├── src/lib/              # Axios, repositories, adapters API
│   ├── src/types/            # Types de domaine et API
│   ├── tests/                # Vitest/Testing Library
│   ├── e2e/                  # Playwright
│   ├── Dockerfile
│   └── package-lock.json
├── backend/
│   ├── app/main.py           # Routes FastAPI et vertical slice
│   ├── app/models.py         # Modèles SQLAlchemy
│   ├── app/schemas.py        # Schémas Pydantic
│   ├── app/security.py       # JWT, cookies, CSRF, auth
│   ├── app/providers.py      # Providers IA déterministes
│   ├── app/celery_app.py     # Configuration Celery
│   ├── app/tasks.py          # Tâches asynchrones
│   ├── alembic/              # Migration initiale
│   ├── tests/                # Tests Pytest
│   └── Dockerfile
├── ml/                       # Interface prédictive expérimentale
├── infrastructure/           # Nginx, PostgreSQL/pgvector, MinIO
├── scripts/                  # Vérification et attente HTTP
├── docs/                     # Documentation technique
├── .github/workflows/ci.yml
├── docker-compose.yml
├── .env.example
└── README.md
```

## 4. Frontend développé

### 4.1 Stack effectivement utilisée

- React `18.3.1` ;
- TypeScript `5.7.2`, mode strict ;
- Vite `6.0.5` ;
- Tailwind CSS `3.4.17` ;
- Radix UI Tabs/Dialog avec composants réutilisables style shadcn ;
- React Router `7.1.1` ;
- TanStack Query `5.62.7` ;
- Axios `1.7.9` ;
- React Hook Form + Zod ;
- Recharts `2.15.0` ;
- Lucide React ;
- Vitest, Testing Library, ESLint et Playwright.

Le lockfile `frontend/package-lock.json` a été généré. Le Node local utilisé pour la vérification était Node 24, alors que le projet cible Node LTS 20/22 (`.nvmrc` et `engines >=20 <23`). L'installation a donc émis un avertissement `EBADENGINE`, sans empêcher les tests ou le build.

### 4.2 Routes Web implémentées

- `/login`
- `/dashboard`
- `/patients`
- `/patients/new`
- `/patients/:patientId`
- `/patients/:patientId/consultations/new`
- `/consultations/:consultationId`
- `/consultations/:consultationId/review`
- `/patients/:patientId/analytics`
- `/patients/:patientId/documents`
- `/settings`

Les routes protégées sont enveloppées par un guard d'authentification et un `DashboardLayout` commun.

### 4.3 Shell et design

Le frontend fournit :

- sidebar persistante desktop, repliable sur petit écran ;
- topbar, breadcrumbs et indication permanente « Research prototype » ;
- palette médicale demandée (`#0F766E`, `#14B8A6`, fond `#F8FAFC`) ;
- cartes, badges de statut, tableaux responsifs, états vides et erreurs ;
- focus visibles, labels, navigation clavier et attributs ARIA de base ;
- pages optimisées pour 1280/1440 px et adaptables aux viewports plus petits ;
- séparation visuelle entre faits approuvés et contenu IA/simulé.

### 4.4 Authentification frontend

- Axios utilise les cookies (`withCredentials`) ;
- aucun JWT n'est stocké dans `localStorage` ou `IndexedDB` ;
- le token CSRF est obtenu via `/auth/csrf` et envoyé dans `X-CSRF-Token` ;
- un flux de refresh centralisé évite les refresh concurrents ;
- le cache TanStack Query est vidé au logout ;
- aucune persistance du cache clinique n'est activée.

### 4.5 Fonctionnalités patients

- liste des patients avec pagination ;
- création d'un patient synthétique validée par Zod ;
- page patient avec onglets : overview, medical history, consultations, observations, documents et AI analysis ;
- timeline clinique ;
- observations approuvées ;
- liens directs vers consultation, documents et analyses.

### 4.6 Filtration des données — frontend

La filtration a fait l'objet d'un second passage spécifique.

Liste patients :

- recherche par nom avec debounce ;
- le texte recherché reste uniquement en mémoire et n'est jamais ajouté à l'URL ;
- filtre de tendance : improving, stable, worsening, insufficient_data ;
- filtre local de complétude du dossier médical ;
- tri par nom, date de naissance, date de création ou mise à jour ;
- ordre ascendant/descendant ;
- pagination et taille de page ;
- résumé des filtres actifs, bouton reset et état vide filtré ;
- filtres non sensibles encodés dans l'URL pour conserver la navigation ;
- aucun nom de patient ni résultat clinique dans les query strings.

Timeline patient :

- filtre par type d'événement ;
- filtre par statut ;
- bornes de date ;
- ordre chronologique ;
- validation `date_from <= date_to` ;
- états loading/error/retry/empty.

Observations :

- filtre texte/catégorie avec debounce ;
- filtre par code/type ;
- bornes de date ;
- ordre de tri ;
- validation des dates et feedback accessible.

Les types et adapters correspondants sont dans `frontend/src/lib/repositories.ts` et `frontend/src/types/api.ts`.

### 4.7 Consultations, audio et temps réel

- création de consultation manuelle ou audio ;
- consentement obligatoire avant l'activation audio ;
- hook `useRecorder` utilisant `navigator.mediaDevices.getUserMedia` et `MediaRecorder` ;
- détection de MIME supporté au runtime ;
- start, pause/reprise, stop, cancel, durée et preview ;
- libération des tracks microphone au stop/unmount ;
- upload par `Blob`, `File` et `FormData` ;
- hook WebSocket natif avec enveloppes `event`, séquences et finalisation `stop` ;
- transcript éditable ;
- lancement transcription/extraction et polling de job ;
- page de revue avant approbation médecin.

### 4.8 Analyse et documents

- demande d'analyse patient et polling du job ;
- présentation des tendances improving/stable/worsening ;
- résumé, références, conflits, limitations et version du modèle ;
- upload document/image ;
- traitement OCR de démonstration ;
- revue et approbation des extractions.

### 4.9 Adapters API corrigés

Des adapters frontend convertissent les différences entre le format wire backend et le domaine React, notamment :

- `name` ↔ `full_name` ;
- consultation enveloppée ;
- `manual_notes` ;
- consentement `{granted: true}` ;
- format brut des drafts ;
- résultat d'analyse imbriqué ;
- formes dashboard/settings ;
- observations et timeline.

Ne pas supprimer ces adapters sans aligner d'abord les schémas OpenAPI/backend.

## 5. Backend développé

### 5.1 Architecture

Backend FastAPI modulaire compact, avec :

- configuration par environnement ;
- SQLAlchemy 2 ;
- schémas Pydantic ;
- SQLite comme fallback local rapide ;
- PostgreSQL configuré pour Docker ;
- migration Alembic initiale ;
- Celery/Beat et Redis ;
- providers IA injectables/déterministes ;
- stockage privé local de développement et MinIO prévu dans Compose.

Le code MVP est actuellement assez compact dans `backend/app/main.py`. Une prochaine session peut le refactorer en routers/services/repositories sans changer les contrats externes.

### 5.2 Authentification et sécurité implémentées

- JWT access court et refresh ;
- cookies HttpOnly, SameSite strict, Secure configurable ;
- rotation du refresh ;
- CSRF cookie/header pour mutations ;
- contrôle Origin/CORS configurable ;
- contrôle d'accès médecin → patient avant lecture ou filtrage ;
- auth WebSocket et validation d'origine ;
- `Cache-Control: no-store`/headers de sécurité applicatifs ;
- audit logs ;
- validation taille/type d'upload ;
- consentement d'enregistrement ;
- noms de fichiers non utilisés comme chemins publics ;
- aucun secret dans les URL.

### 5.3 Endpoints implémentés

Santé :

- `GET /health`

Authentification :

- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- `GET /api/v1/auth/csrf`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`

Patients :

- `GET /api/v1/patients`
- `POST /api/v1/patients`
- `GET /api/v1/patients/{patient_id}`
- `PATCH /api/v1/patients/{patient_id}`
- `GET /api/v1/patients/{patient_id}/observations`
- `GET /api/v1/patients/{patient_id}/timeline`
- `GET /api/v1/patients/{patient_id}/consultations`

Consultations :

- `POST /api/v1/patients/{patient_id}/consultations`
- `GET /api/v1/consultations/{consultation_id}`
- `POST /api/v1/consultations/{consultation_id}/consent`
- `POST /api/v1/consultations/{consultation_id}/audio`
- `POST /api/v1/consultations/{consultation_id}/transcribe`
- `POST /api/v1/consultations/{consultation_id}/extract`
- `PATCH /api/v1/consultations/{consultation_id}/draft`
- `POST /api/v1/consultations/{consultation_id}/approve`
- `WS /api/v1/consultations/{consultation_id}/stream`

Analyses :

- `POST /api/v1/patients/{patient_id}/analyze`
- `GET /api/v1/patients/{patient_id}/analyses`
- `GET /api/v1/analyses/{analysis_id}`
- `POST /api/v1/analyses/{analysis_id}/review`

Documents :

- `POST /api/v1/patients/{patient_id}/documents`
- `GET /api/v1/patients/{patient_id}/documents`
- `POST /api/v1/documents/{document_id}/process`
- `POST /api/v1/documents/{document_id}/approve`

Autres :

- `GET /api/v1/jobs/{job_id}`
- `GET /api/v1/dashboard/overview`
- `GET /api/v1/settings`
- `PATCH /api/v1/settings`

Les traitements longs renvoient HTTP 202 et un `job_id`.

### 5.4 Filtration des données — backend

Les filtres sont appliqués après l'autorisation du médecin, jamais avant.

Patients :

- recherche littérale échappée (`%` et `_` ne deviennent pas des wildcards SQL) ;
- filtre de tendance calculé à partir des observations approuvées ;
- tri stable avec UUID comme tie-breaker ;
- tri par nom, date de naissance, création ou mise à jour ;
- ordre asc/desc ;
- bornes strictes sur `page` et `page_size`.

Observations :

- code ;
- catégorie ;
- date de début/fin ;
- ordre ;
- offset/limit bornés.

Timeline :

- type d'événement ;
- statut ;
- dates ;
- ordre ;
- pagination.

Consultations, documents et analyses :

- endpoints de collection filtrés ;
- recherche/état/date selon la ressource ;
- validation des enums et plages ;
- isolation cross-doctor testée.

### 5.5 Données et modèles

Les modèles requis ont été établis autour de concepts FHIR-inspired, sans revendiquer une conformité FHIR complète :

- doctors ;
- patients ;
- patient_access ;
- consultations ;
- recording_consents ;
- audio_recordings ;
- transcripts et transcript_segments ;
- clinical_drafts ;
- symptoms, conditions, medications, allergies ;
- observations ;
- documents et document_extractions ;
- analysis_runs et ai_findings ;
- alerts ;
- processing_jobs ;
- embeddings ;
- audit_logs ;
- doctor_settings.

### 5.6 IA de démonstration

Le mode par défaut est explicitement `mock`/déterministe :

- transcription synthétique horodatée ;
- extraction structurée avec symptômes, négations, observations et sources ;
- conservation des champs manquants sans invention ;
- analyse de tendance déterministe ;
- OCR/extraction document de démonstration ;
- sorties clairement simulées.

Aucun provider réel Faster-Whisper, Ollama, Sentence Transformers, pgvector ou PaddleOCR n'est encore entièrement branché en production. Les interfaces, variables et limites sont documentées pour la prochaine phase. Ne jamais basculer silencieusement vers un mock lorsqu'un provider réel configuré échoue.

## 6. Infrastructure développée

`docker-compose.yml` définit :

- `gateway` : build frontend + Nginx ;
- `backend` : FastAPI/Uvicorn ;
- `worker` : Celery ;
- `beat` : Celery Beat ;
- `postgres` : PostgreSQL 16 + pgvector ;
- `redis` ;
- `minio` et initialisation du bucket privé ;
- `ollama` optionnel via profile.

En mode production-like, seul le gateway publie un port hôte (`8080`). Les autres services sont sur un réseau privé interne.

Nginx fournit :

- frontend statique Vite ;
- fallback SPA pour React Router ;
- proxy `/api/v1` ;
- upgrade WebSocket ;
- limites d'upload ;
- CSP et headers de sécurité ;
- absence d'interception des routes API par le fallback SPA.

La configuration Compose a été validée pendant l'implémentation, mais la commande exige un vrai fichier `.env` car les services déclarent `env_file: .env`.

## 7. Données synthétiques et credentials

Le seed backend crée cinq profils fictifs couvrant :

- indicateurs en amélioration ;
- indicateurs en dégradation ;
- état stable ;
- informations incomplètes ;
- observations contradictoires.

### Incohérence importante à corriger en priorité

Le code backend actuel crée réellement :

```text
Email: demo@diagnovision.local
Password: Demo123!
```

Mais `README.md` et `docs/DEMO_GUIDE.md` indiquent actuellement :

```text
Email: doctor@diagnovision.local
Password: DemoPass123!
```

La prochaine session doit choisir une seule paire, idéalement celle documentée (`doctor@diagnovision.local` / `DemoPass123!`), puis aligner :

- le seed backend ;
- les tests ;
- le README ;
- le guide de démo ;
- les éventuels fixtures Playwright.

Tant que ce point n'est pas corrigé, utiliser les credentials du code backend pour un lancement local.

## 8. Tests et validations réellement exécutés

### Backend

Commande :

```bash
.venv/bin/pytest -q backend/tests
```

Résultat réel :

```text
8 passed, 51 warnings in 1.32s
```

Les warnings concernent principalement des dépréciations FastAPI/Starlette/python-jose, pas des échecs fonctionnels.

Ruff correctness profile :

```bash
.venv/bin/ruff check backend/app backend/tests ml
```

Résultat :

```text
All checks passed!
```

Le profil Ruff a volontairement été limité aux règles de correction (`E9`, `F63`, `F7`, `F82`) car le MVP backend est compact et générait des centaines de violations purement stylistiques. Un refactoring/formatage complet reste à faire.

Couverture fonctionnelle backend incluse dans les tests :

- login et CSRF ;
- patient vertical slice ;
- consentement audio ;
- filtres et pagination ;
- enums et bornes invalides ;
- échappement des wildcards ;
- tendances ;
- filtres observations/timeline/consultations/documents/analyses ;
- isolation entre deux médecins.

### Frontend

Commandes et résultats réels :

```text
npm run lint       -> succès
npm run typecheck  -> succès
npm run test       -> 1 test passé
npm run build      -> succès
```

Build Vite réel :

```text
dist/index.html                   0.47 kB
dist/assets/index-*.css          25.56 kB (5.31 kB gzip)
dist/assets/index-*.js          902.45 kB (264.93 kB gzip)
```

Warning restant : bundle JavaScript supérieur à 500 kB. Ce n'est pas un échec, mais le code splitting est une tâche recommandée.

Vitest a exécuté `frontend/tests/ui.test.tsx`. Le dossier Playwright est explicitement exclu de Vitest et doit être lancé séparément.

### Non encore validé de bout en bout

- `npm run test:e2e` n'a pas été exécuté jusqu'au succès avec les navigateurs Playwright ;
- le stack Docker complet n'a pas été lancé jusqu'à une démo complète ;
- le test browser réel login → patient → consultation → approbation n'a pas été terminé ;
- microphone Chrome/Firefox/Safari non testé manuellement ;
- codecs MediaRecorder et reconnexion WebSocket non vérifiés multi-browser ;
- build Docker complet et healthchecks non observés jusqu'au vert.

Ne pas annoncer ces validations comme réussies avant de les exécuter.

## 9. Commandes de démarrage

### 9.1 Stack Docker recommandée

```bash
cd /Users/waelzouari/tech4health/DiagnoVision
cp .env.example .env
docker compose up --build
```

Puis ouvrir :

```text
http://localhost:8080
```

Migration si nécessaire :

```bash
docker compose run --rm backend alembic upgrade head
```

### 9.2 Développement local

Backend :

```bash
cd /Users/waelzouari/tech4health/DiagnoVision
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
DATABASE_URL=sqlite:///./diagnovision.db \
DEMO_MODE=true \
SECURE_COOKIES=false \
uvicorn app.main:app --app-dir backend --reload --port 8000
```

Frontend :

```bash
cd /Users/waelzouari/tech4health/DiagnoVision/frontend
npm ci
npm run dev
```

Ouvrir `http://localhost:5173`.

## 10. Artefacts locaux à nettoyer

Les validations ont généré des artefacts locaux qui ne sont pas du code source :

- `backend/diagnovision.db` ;
- `test_diagnovision.db` ;
- caches `.pytest_cache/` et `.ruff_cache/` ;
- fichiers générés `frontend/*.js`, `frontend/*.d.ts`, `frontend/*.tsbuildinfo` provenant de la première configuration TypeScript ;
- `frontend/node_modules/` et `frontend/dist/`.

La prochaine session doit vérifier `.gitignore`, puis supprimer uniquement les artefacts générés avec prudence. Ne pas supprimer les fichiers source `.ts`, `.tsx`, le lockfile, les migrations ou les documents.

## 11. Dette technique et problèmes connus

### P0 — à corriger avant démo complète

1. Aligner les credentials seed/tests/docs.
2. Lancer `docker compose up --build` et corriger tout problème runtime.
3. Exécuter un workflow navigateur complet avec Playwright ou browser automation.
4. Vérifier que le login utilise correctement les cookies/CSRF derrière Nginx.
5. Vérifier le workflow consultation complet : consentement, upload/record, transcription, extraction, édition, approbation, timeline mise à jour.
6. Vérifier upload document → process → review → approve.
7. Ajouter des tests frontend spécifiques aux filtres nouvellement créés.

### P1 — qualité et architecture

1. Refactorer `backend/app/main.py` en routers/services/repositories.
2. Générer les types TypeScript depuis OpenAPI et réduire les adapters manuels.
3. Ajouter React lazy routes/code splitting pour réduire le bundle.
4. Ajouter davantage de tests Vitest/RTL : protected routes, session expiry, permission microphone refusée, erreurs API, filtres.
5. Stabiliser les tests Playwright et installer les browsers CI.
6. Remplacer les événements FastAPI `on_event` par lifespan.
7. Utiliser des datetimes timezone-aware partout.
8. Appliquer Ruff format/Black-like formatting après refactoring.
9. Supprimer les fichiers TypeScript générés parasites et empêcher leur régénération.

### P2 — providers réels et data engineering

1. Implémenter réellement Faster-Whisper en worker non bloquant.
2. Implémenter Ollama/provider LLM avec validation Pydantic stricte.
3. Ajouter Sentence Transformers + pgvector avec isolation médecin/patient avant retrieval.
4. Implémenter PaddleOCR/OpenCV/PyMuPDF réel avec limites de ressources.
5. Brancher MinIO pour les fichiers privés avec accès autorisé/signed.
6. Matérialiser réellement Bronze/Silver/Gold et ETL idempotent.
7. Implémenter locking Redis et déduplication durable des jobs.
8. Ajouter un modèle prédictif uniquement si un dataset légal et documenté existe ; sinon garder l'abstention.

## 12. Règles à préserver absolument

- React/TypeScript/Vite uniquement pour le frontend.
- FastAPI/Python pour le backend.
- Aucun Flutter, Dart, React Native, Android, iOS ou desktop natif.
- Application entièrement utilisable depuis un navigateur desktop moderne.
- `MediaRecorder` et WebSocket natifs pour l'audio/temps réel.
- Données exclusivement synthétiques pour développement/démo.
- Aucun JWT ou donnée clinique persistée dans `localStorage`/IndexedDB.
- Contrôle d'accès serveur obligatoire ; les route guards frontend ne suffisent pas.
- Autorisation médecin/patient avant retrieval, filtrage ou accès fichier.
- Consentement explicite avant microphone/enregistrement.
- Aucune invention de donnée clinique manquante.
- Tous les faits IA restent en draft jusqu'à approbation explicite du médecin.
- Conserver provenance, timestamps, pages et valeurs originales.
- Ne jamais présenter les suggestions IA comme diagnostics définitifs.
- Ne jamais inventer une performance de modèle ou une validation clinique.
- Ne jamais envoyer de vraies données médicales à un provider externe dans ce projet.
- Ne jamais committer de secrets ou credentials réels.

## 13. Plan conseillé pour la prochaine session

### Étape 1 — audit et nettoyage contrôlé

1. Lire ce fichier et tous les documents `docs/*.md`.
2. Exécuter `git status` si le dépôt Git est initialisé ; préserver les changements utilisateur.
3. Nettoyer seulement les artefacts générés listés en section 10.
4. Corriger les credentials incohérents.

### Étape 2 — validation full stack

1. Copier `.env.example` vers `.env` et remplacer les secrets locaux si nécessaire.
2. Lancer `docker compose up --build`.
3. Attendre tous les healthchecks.
4. Tester `/health`, `/api/v1/auth/login` et la page `/login` via le gateway.
5. Tester le refresh direct de `/patients/...` pour vérifier le fallback SPA.

### Étape 3 — E2E P0

Créer/compléter un test Playwright qui :

1. se connecte ;
2. filtre la liste patients ;
3. crée ou sélectionne un patient synthétique ;
4. crée une consultation ;
5. donne le consentement ;
6. upload un audio fixture ;
7. attend transcription/extraction ;
8. édite et approuve le draft ;
9. vérifie timeline/observations ;
10. lance une analyse ;
11. upload et traite un rapport laboratoire synthétique ;
12. se déconnecte et vérifie la protection de route.

### Étape 4 — couverture des filtres frontend

Ajouter des tests RTL couvrant :

- debounce de recherche ;
- absence du nom recherché dans l'URL ;
- query params non sensibles ;
- reset filters ;
- pagination ;
- date range invalide ;
- états vides ;
- erreurs backend 422/403/404 ;
- conservation de l'isolation patient.

### Étape 5 — providers et entrepôt

Une fois le P0 stable, implémenter les providers réels un par un derrière les interfaces existantes. Chaque provider doit avoir :

- timeout ;
- validation stricte ;
- gestion d'échec explicite ;
- pas de fallback silencieux ;
- version du modèle ;
- provenance ;
- tests de contrat offline.

## 14. Prompt court à donner à la prochaine session

Copier ce texte avec ce fichier :

```text
Lis complètement docs/HANDOFF_NEXT_SESSION.md et les documents docs/*.md.
Continue le projet DiagnoVision sans changer sa plateforme : React + TypeScript +
Vite côté frontend, FastAPI/Python côté backend, navigateur desktop uniquement.
Préserve les fonctionnalités existantes et les contrôles de sécurité. Commence par
corriger les credentials incohérents, nettoyer les artefacts générés, lancer le
stack Docker complet et faire passer le workflow Playwright end-to-end. Ensuite,
renforce les tests frontend de filtration, puis poursuis les tâches P1/P2 listées
dans la passation. Ne revendique aucun test non exécuté ni validation clinique.
```

## 15. Documents complémentaires

- `README.md`
- `docs/ARCHITECTURE.md`
- `docs/API_CONTRACT.md`
- `docs/DATABASE_SCHEMA.md`
- `docs/AI_PIPELINE.md`
- `docs/DATA_WAREHOUSE.md`
- `docs/SECURITY.md`
- `docs/MODEL_LIMITATIONS.md`
- `docs/DEMO_GUIDE.md`
- `docs/TEAM_TASKS.md`

Ce document de passation doit rester factuel : toute future session doit mettre à jour les sections « tests réellement exécutés », « problèmes connus » et « prochaines priorités » après chaque phase importante.
