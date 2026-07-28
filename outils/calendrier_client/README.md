# Pipeline de génération — calendrier éditorial CLIENT (CC-EXC-001)

Génère `rapports/calendrier_client_excellence_plus_aout_septembre.html` et `.pdf` —
extrait client du calendrier CE-EXC-001, limité à août + septembre 2026, format A4
**paysage**, prêt pour soumission BAT. Livrable jumeau de l'outil interne
(`outils/calendrier_editorial/`) : même source de données, mise en forme opposée —
trié par **priorité de pilier** (pas chronologiquement), langage client (pas de
statut SOP-001, pas de jargon de production).

## Pipeline

```
1. outils/calendrier_editorial/generate.py   -> data/*.json (source unique)
2. build_pdf.py                               -> out/calendrier_client.html (autonome, logos inlinés)
3. render_pdf.js                              -> out/calendrier_client.pdf (A4 paysage, pagination réelle)
```

## Régénérer

```bash
cd ../calendrier_editorial && python3 generate.py   # (re)génère data/ si absent
cd ../calendrier_client
python3 build_pdf.py
node render_pdf.js out/calendrier_client.html out/calendrier_client.pdf
cp out/calendrier_client.html ../../rapports/calendrier_client_excellence_plus_aout_septembre.html
cp out/calendrier_client.pdf  ../../rapports/calendrier_client_excellence_plus_aout_septembre.pdf
```

`out/` n'est pas commité (voir `.gitignore`) — artefact reproductible à la demande.
Penser à nettoyer `outils/calendrier_editorial/data/` après usage (non commité non
plus) : `scripts/validate_repo.py` scanne le disque, pas seulement git, et signalera
le terme interdit (présent intentionnellement dans le champ `notes` de chaque entrée,
comme rappel du nom exact du client) si ces fichiers traînent au moment du commit.

## Portée

`MOIS_CIBLES = ("2026-08", "2026-09")` dans `build_pdf.py` — à modifier pour étendre
la période. Le circuit `<thead>` par table de pilier se répète automatiquement sur
chaque page imprimée (technique standard CSS print) : ne pas revenir à une simple
`<div>` pour la grille de fiches, l'identité du pilier redeviendrait invisible sur
les pages de continuation.

## Ce qui n'est PAS dans ce document (volontairement)

- Aucun texte de post final : tout est encore au statut `a_rediger` côté outil
  interne — ce PDF valide un **plan de sujets**, pas des textes rédigés.
- Aucun statut SOP-001 (`draft`/`BAT_soumis`/…) : vocabulaire interne, pas client.
- Aucune mention de Prepdia, du nombre d'enseignants, ni de la Fondation Zacharias
  Tanee Fomum — cf. `_base/identite/brand_guidelines.md` §Liste Rouge.
