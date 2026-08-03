# STATUT DU PROJET — Excellence+ × AORA

> Document de continuité de session. À lire en complément des 4 fichiers de la
> LECTURE OBLIGATOIRE (`CLAUDE.md`). Mis à jour à chaque livraison majeure —
> si tu reprends ce projet dans une nouvelle session, lis ce fichier en premier
> pour connaître l'état réel du repo sans avoir à tout re-déduire du git log.

Dernière mise à jour : 28 juillet 2026.

## Branches

- **Branche de travail désignée** : `claude/excellence-plus-repo-setup-rs7efy`
- **`main`** : synchronisée avec la branche de travail (merge `--no-ff` après
  chaque livraison confirmée par l'utilisateur). Les deux branches sont à jour
  l'une par rapport à l'autre au moment de la rédaction de ce document.
- Convention établie : développer sur la branche désignée, pousser, puis
  merger proprement vers `main` (jamais de force-push) quand une livraison est
  actée.

## Livrables produits (tous poussés sur `main` et la branche de travail)

| Réf. | Fichier | Contenu |
|---|---|---|
| — | Structure repo initiale | `CLAUDE.md`, `_base/identite/*`, `_base/couleurs/*`, `_base/logos/*`, `_base/templates/*`, `calendrier/*.json`, `scripts/*.py`, `.github/workflows/*.yml` |
| — | `calendrier/calendrier_editorial_aout_2026.html` | Calendrier HTML — août 2026 seul (semaine 32), première itération, jamais retouché depuis |
| **CE-EXC-001** | `rapports/calendrier_editorial_excellence_plus.html` | Calendrier interactif **août → décembre 2026 (5 mois actifs — juillet achevé, retiré du plan)**, 239 créneaux, navigation 4 niveaux (vue d'ensemble → mois → semaine → fiche). Mois numérotés Mois 1 (août) à Mois 5 (décembre) ; décembre = bilan mi-annuel. **Version courante.** Voir `outils/calendrier_editorial/README.md` pour régénérer. |
| **CC-EXC-001** | `rapports/calendrier_client_excellence_plus_aout_septembre.html` + `.pdf` | **Livrable client** — extrait août+septembre du calendrier ci-dessus, A4 **paysage**, trié par priorité de pilier (pas chronologique), langage client (pas de statut SOP-001), 89 publications, 9 pages, prêt pour soumission BAT. Twin livrable de CE-EXC-001 (même source de données). Voir `outils/calendrier_client/README.md`. |
| **LE-EXC-001** | `rapports/ligne_editoriale_excellence_plus.html` + `.pdf` | Ligne éditoriale (7 sections), sourcée depuis `brand_guidelines.md` + `plateforme_marque.md`. Pas encore recalée sur 5 mois (voir vigilance §5). |
| **PE-EXC-001** | `rapports/planification_editoriale_excellence_plus.html` + `.pdf` | Planification éditoriale (7 sections). **Version 1.1** — recalée sur 5 mois actifs (août-décembre), décembre repositionné bilan mi-annuel, forfait AORA (6 mois / 315 000 FCFA) laissé intact avec note distinguant durée contractuelle et fenêtre de production active. |

## Outillage préservé dans le repo

- `outils/calendrier_editorial/` — pipeline complet de génération de CE-EXC-001
  (`generate.py` → `build_data.py` → `inject_template.py` → HTML autonome).
  **100 % déterministe** (vérifié par diff sur runs successifs). Voir le
  `README.md` du dossier pour la commande de régénération et la liste des
  endroits où modifier le contenu (piliers, plateformes, mois, axes de contenu).
- `outils/calendrier_client/` — génère CC-EXC-001 à partir des données produites
  par `calendrier_editorial/generate.py` (même source, pas de duplication de
  contenu). `MOIS_CIBLES` dans `build_pdf.py` contrôle la période extraite.
  Technique clé : sections piliers en `<table><thead>` (pas de simples `<div>`)
  pour que l'en-tête coloré du pilier se répète automatiquement sur les pages de
  continuation en impression — cf. README du dossier.
- **Piège récurrent** : `generate.py` écrit `data/` + `data.js` dans le dossier
  courant. Ces artefacts sont gitignorés mais `scripts/validate_repo.py` scanne
  le **disque**, pas seulement git — il faut les supprimer (`rm -rf data
  data.js`) avant `git status`/commit, sinon le scan « termes interdits »
  remonte un faux positif sur le champ `notes` (avertissement intentionnel).
- Les pipelines de LE-EXC-001 (rendu HTML→PDF via Playwright, scripts
  d'injection de logos) **n'ont pas été préservés dans le repo** — seul le
  fichier final (HTML+PDF dans `rapports/`) subsiste. À reconstruire si une
  régénération est nécessaire un jour (contenu source : `brand_guidelines.md` +
  `plateforme_marque.md`).

## Points de vigilance non résolus

1. **Nom de la page Facebook/WhatsApp incohérent entre documents** :
   « Excellence Plus Éducation » (LE-EXC-001, orthographe corrigée) vs
   « Excellence au plus éducation » (PE-EXC-001, dicté littéralement 3 fois par
   l'utilisateur malgré une clarification proposée deux fois). **À trancher
   avec Stéphane/Laurence avant publication externe.**
2. **Tranche d'âge cible incohérente entre documents** : « 35 à 70 ans »
   (chiffre sourcé dans `brand_guidelines.md`, utilisé dans LE-EXC-001) vs
   « 30-76 ans » (dicté littéralement par l'utilisateur dans PE-EXC-001).
   Même statut : à trancher, pas corrigé silencieusement.
3. **Résolu le 03/08/2026** — tous les calendriers ont été recalés sur le
   dispositif du 30/07-02/08/2026 (3 publications/semaine, Facebook seul au
   lancement, config/creneaux.json fait foi) et sur la vraie première semaine
   ISO (semaine 33, lundi 10 → dimanche 16 août 2026 — pas la semaine 32,
   04 → 10 août, encore moins le 4 août traité comme un lundi) :
   `calendrier/semaine_active.json`, `calendrier/calendrier_editorial.json`,
   `calendrier/calendrier_editorial_aout_2026.html` corrigés à la main ;
   CE-EXC-001 et CC-EXC-001 régénérés via leurs pipelines respectifs
   (`outils/calendrier_editorial/generate.py` lit déjà `config/creneaux.json`
   depuis la v3 du 30/07 — il suffisait de relancer le pipeline après la mise
   à jour du fichier de créneaux, pas de le réécrire).
   **Point ouvert découvert au passage** : `calendrier/calendrier_editorial_aout_2026.html`
   a un bug préexistant, antérieur à cette correction — `window.ENTRIES` n'est
   jamais assigné depuis la constante `ENTRIES` (seul `window.ENTRIES = window.ENTRIES || []`
   existe), donc la page n'a jamais affiché aucune donnée depuis sa création.
   Le contenu est maintenant correct mais reste invisible à l'affichage. Ce
   fichier est une première itération non maintenue, supersedée par CE-EXC-001 —
   à archiver ou corriger si quelqu'un doit un jour s'en servir réellement.
4. Aucun post n'a encore de `bap_recu_le` renseigné nulle part dans le repo —
   normal à ce stade (rien n'est encore validé/publié), mais rappel que la
   règle absolue « jamais publier sans BAP » s'applique dès le premier post
   réel.
5. **LE-EXC-001 n'a pas été recalé sur 5 mois actifs** (contrairement à
   CE-EXC-001 et PE-EXC-001, v1.1) — il documente encore un cadre implicite
   juillet-décembre. Impact limité (LE-EXC-001 est une charte éditoriale, pas
   un planning daté), mais à harmoniser si le document est retouché.
6. **Les 3 mois non couverts par CC-EXC-001** (octobre, novembre, décembre)
   n'ont pas encore de pendant client — seuls août+septembre ont un extrait
   BAT-ready. `outils/calendrier_client/build_pdf.py` peut être relancé avec
   `MOIS_CIBLES` étendu quand ces mois devront être soumis à validation.
7. **(28 juillet 2026)** Trois documents de référence poussés dans le repo
   (`_base/identite/Plan_AORA_EXCELLENCE_PLUS_Rentree_2026.md` = RECO-001,
   `_base/aora/AORA_Charte_Graphique_2026.md`, `_base/aora/AORA_SOP001_v1_Gestion_Client.md`)
   ont déclenché une passe de réconciliation (`brand_guidelines.md`, `CLAUDE.md`,
   nouveau `PRODUCTION_WORKFLOW.md`). Deux points **volontairement non tranchés**,
   détaillés avec leur raisonnement dans `brand_guidelines.md` §6 et §14 :
   - RECO-001 utilise « 25 enseignants » deux fois (dont un titre de post suggéré) —
     le blocage headcount de `brand_guidelines.md` reste néanmoins en vigueur (ce
     fichier est postérieur à RECO-001 et formalise ce blocage explicitement).
   - Le SOP-001 officiel définit BAT et BAP comme deux approbations à usages
     distincts (print vs digital), pas nécessairement séquentielles — le circuit
     à 4 étapes utilisé partout dans ce repo n'a pas été réécrit sur cette seule
     base (impact trop large pour une décision unilatérale).
   Autres points ouverts : ciblage Meta Ads par zone RECO-001 vs zones premium
   `brand_guidelines.md` (Odza classé différemment, Santa Barbara absent de
   RECO-001) ; horizon RECO-001 commence en juin 2026, avant la date de démarrage
   contractuel juillet 2026 indiquée dans `brand_guidelines.md`.
8. **Résolu le 03/08/2026** — `.github/workflows/publish_scheduled.yml` (cron
   `*/15 5-21 * * *`, moteur de publication concurrent qui appelait directement
   les API sociales sans passer par Composio ni vérifier la porte visuel) a été
   supprimé. `scripts/check_and_publish.py` et les `scripts/publish_facebook.py`
   / `publish_instagram.py` / `publish_tiktok.py` / `publish_whatsapp.py`
   associés sont déplacés vers `scripts/archive/`. Il n'existe désormais qu'un
   seul chemin de publication : routine `programmation_quotidienne.yml` (03h00
   WAT) → `demande_composio.txt` → skill `composio-publie-aora` en chat Claude.
   Aucune Routine CCR (`list_triggers`) n'est encore programmée pour ce compte —
   le déclenchement à 03h00/07h00 WAT reste porté par GitHub Actions, pas par
   une Routine Claude Code Remote.

## Conventions établies (à respecter dans une nouvelle session)

- **Format des livrables** : HTML autonome (aucune dépendance externe hormis
  Google Fonts, qui échoue silencieusement en sandbox sans réseau — normal,
  pas un bug produit), PDF rendu via Playwright/Chromium avec
  `headerTemplate`/`footerTemplate` pour la pagination réelle.
- **QA systématique avant toute publication** : Playwright headless (0 erreur
  JS hors échec Google Fonts), scan anti-dérive de marque (termes interdits,
  chiffres fabriqués), `python3 scripts/validate_repo.py` avant chaque commit.
- **CSS pour PDF** : toujours placer les surcharges `@media print` **à la fin**
  de la feuille de style (sinon elles perdent la cascade face aux règles de
  base de même spécificité, même si elles apparaissent "après" dans une
  media query imbriquée plus tôt) ; `break-inside:avoid` sur tableaux/cartes.
- **Génération de contenu à grande échelle** : pour toute rubrique récurrente
  à haute fréquence, prévoir un pool de variantes large (6-10+) ou une
  génération combinatoire (accroche × sujet) — sinon répétition de titres
  quasi-identiques sur plusieurs mois. Ne jamais utiliser `hash()` Python pour
  la pseudo-randomisation (non reproductible d'un run à l'autre) — préférer un
  compteur stable.
- **Design system AORA** (cf. skill `identite-aora`) : marges 42pt latérales /
  92pt haut / 60pt bas, kicker orange 9pt gras « — LABEL », titre bicolore
  navy/orange, Navy #1B2D5C / Orange #F37021 / Blanc — jamais de 4ᵉ couleur
  sans validation DA sur un document de marque. Exception assumée : les
  couleurs natives de plateforme (Facebook bleu, WhatsApp vert, etc.) et le
  code couleur des piliers dans les outils internes (calendrier) sont un usage
  fonctionnel, pas un visuel de marque — jugé acceptable, à confirmer si
  contesté.
- **SOP-001** : `draft → BAT_soumis → BAP_recu → publié → archivé`. Le
  vocabulaire à 5 états utilisé dans l'UI de CE-EXC-001 (« À rédiger / BAT
  envoyé / BAT validé / BAP reçu / Publié ») est une extension propre à cet
  outil, pas un remplacement du circuit SOP-001 officiel.
- **Ne jamais coder en dur un compte qui peut dériver** (ex. libellé « Vue 6
  mois » dans un breadcrumb) — la portée du calendrier a déjà changé une fois
  (6 → 5 mois) et un libellé figé devient silencieusement faux. Préférer un
  texte générique (« Vue d'ensemble ») ou une valeur calculée.
- **Répétition d'en-tête de section à travers les sauts de page PDF** : une
  simple `<div>` de titre ne réapparaît jamais sur une page de continuation.
  Utiliser une vraie balise `<table><thead>` (le `<thead>` se répète
  automatiquement à l'impression) dès qu'une section peut dépasser une page —
  technique utilisée dans `outils/calendrier_client/build_pdf.py`.
- **Séparer durée contractuelle et fenêtre de production active** : le forfait
  AORA-CCC-005 reste 6 mois / 315 000 FCFA quoi qu'il arrive au contenu
  éditorial (ex. juillet retiré du plan actif) — ne jamais recalculer une
  figure contractuelle à partir d'un changement de portée éditoriale.

## Pour démarrer une nouvelle session

Colle ceci en premier message :

> Lis `STATUT_PROJET.md` et `CLAUDE.md` avant toute action. CE-EXC-001 (interne,
> août-décembre) et CC-EXC-001 (client, août-septembre) sont à jour dans
> `rapports/`, pipelines de régénération dans `outils/calendrier_editorial/` et
> `outils/calendrier_client/`.

Rien d'autre n'est en attente à ce stade — tous les livrables demandés ont été
poussés sur `main` et la branche de travail. Les 6 points de vigilance
ci-dessus sont les seuls sujets ouverts (aucun n'est bloquant).
