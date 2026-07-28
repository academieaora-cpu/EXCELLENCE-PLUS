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
| — | `calendrier/calendrier_editorial_aout_2026.html` | Calendrier HTML — août 2026 seul (semaine 32), première itération |
| **CE-EXC-001** | `rapports/calendrier_editorial_excellence_plus.html` | Calendrier interactif **juillet → décembre 2026**, 288 créneaux, navigation 4 niveaux (vue 6 mois → mois → semaine → fiche). **Version courante, remplace toutes les itérations précédentes.** Voir `outils/calendrier_editorial/README.md` pour régénérer. |
| **LE-EXC-001** | `rapports/ligne_editoriale_excellence_plus.html` + `.pdf` | Ligne éditoriale (7 sections), sourcée depuis `brand_guidelines.md` + `plateforme_marque.md` |
| **PE-EXC-001** | `rapports/planification_editoriale_excellence_plus.html` + `.pdf` | Planification éditoriale (7 sections : synthèse stratégique, hiérarchie plateformes, thèmes mensuels, grille hebdo, circuit de validation, budget, taux validés) |

## Outillage préservé dans le repo

- `outils/calendrier_editorial/` — pipeline complet de génération de CE-EXC-001
  (`generate.py` → `build_data.py` → `inject_template.py` → HTML autonome).
  **100 % déterministe** (vérifié par diff sur runs successifs). Voir le
  `README.md` du dossier pour la commande de régénération et la liste des
  endroits où modifier le contenu.
- Les pipelines de LE-EXC-001 et PE-EXC-001 (rendu HTML→PDF via Playwright,
  scripts d'injection de logos) **n'ont pas été préservés dans le repo** — ils
  n'existaient que dans le scratchpad éphémère d'une session précédente et ont
  été perdus à la fin de cette session. Seuls les fichiers finaux (HTML+PDF
  dans `rapports/`) subsistent. À reconstruire si une régénération est
  nécessaire un jour (le contenu source reste `brand_guidelines.md` +
  `plateforme_marque.md` + `calendrier_editorial.json`).

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
3. **`calendrier/calendrier_editorial.json`** (fichier source d'origine, semaine
   32) traite le **4 août 2026 comme un lundi — c'est en réalité un mardi**
   (le vrai lundi est le 3 août). Toutes les versions ultérieures du calendrier
   (y compris CE-EXC-001) utilisent les vraies semaines ISO et ignorent cette
   erreur, mais le fichier JSON source lui-même n'a jamais été corrigé.
4. Aucun post n'a encore de `bap_recu_le` renseigné nulle part dans le repo —
   normal à ce stade (rien n'est encore validé/publié), mais rappel que la
   règle absolue « jamais publier sans BAP » s'applique dès le premier post
   réel.

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

## Pour démarrer une nouvelle session

Colle ceci en premier message :

> Lis `STATUT_PROJET.md` et `CLAUDE.md` avant toute action. Le calendrier
> CE-EXC-001 est à jour dans `rapports/`, pipeline de régénération dans
> `outils/calendrier_editorial/`.

Rien d'autre n'est en attente à ce stade — tous les livrables demandés ont été
poussés. Les 4 points de vigilance ci-dessus sont les seuls sujets ouverts.
