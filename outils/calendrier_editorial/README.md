# Pipeline de génération — calendrier éditorial CE-EXC-001

Génère `rapports/calendrier_editorial_excellence_plus.html` (calendrier interactif
juillet → décembre 2026, navigation 4 niveaux : vue 6 mois → mois → semaine → fiche).

## Pipeline

```
generate.py          -> data/*.json (9 fichiers : entries, weeks, months, pillars,
                         platforms, platforms_hors_scope, statuts, meta_ads, kpi)
build_data.py         -> data.js (fusion ASCII-safe des 9 JSON en window.X globaux)
inject_template.py    -> HTML autonome (injecte data.js + logos en base64 dans template.html)
```

## Régénérer le calendrier

Depuis ce dossier (`outils/calendrier_editorial/`) :

```bash
python3 generate.py
python3 build_data.py
python3 inject_template.py \
  --template template.html \
  --data data.js \
  --logo-aora ../../_base/logos/aora_logo_400w.png \
  --logo-excellence ../../_base/logos/excellence_plus_logo_500x500.png \
  --out ../../rapports/calendrier_editorial_excellence_plus.html
```

`generate.py` est **100% déterministe** (vérifié par diff sur deux runs successifs) —
aucun aléa, donc `data/` et `data.js` sont des artefacts reproductibles et ne sont
**pas commités** (à régénérer localement si besoin d'inspection).

## Où modifier quoi

- **Contenu juillet/août/septembre** : `EXPLICIT_FB` (titres Facebook transcrits
  fidèlement depuis le brief client), `WA_THEMES`, `IG_RUBRIQUES_JAS`,
  `TT_RUBRIQUES_JAS` dans `generate.py`.
- **Contenu octobre/novembre/décembre** : `AXES_OND` (axes donnés par le client,
  génération systématique avec rotation + suffixes `LAP_SUFFIX` pour éviter les
  répétitions de titres sur les rubriques à haute fréquence).
- **Piliers, plateformes, statuts, mois, campagnes Meta Ads** : constantes en tête de
  `generate.py` (`PILLARS`, `PLATFORMS`, `PLATFORMS_HORS_SCOPE`, `STATUTS`, `MONTHS`,
  `META_ADS`).
- **UI / interactions** (recherche, filtres, favoris, statuts, modale, breadcrumb,
  export PDF) : `template.html`, section `<script>`.
- **Design AORA** (couleurs, kicker, badges) : `template.html`, section `<style>`.

## Points de vigilance déjà résolus (ne pas réintroduire)

- `weekIdOf()` (JS, calcul ISO week côté client) a été **vérifié identique** à
  `isocalendar()` (Python) sur les 288 entrées — cf. `WEEKS[].id` = `"S<numéro ISO>"`.
  Toutes les dates du projet (juil.–déc. 2026) tombent dans une seule année ISO
  (2026), donc pas de collision possible entre semaines de même numéro.
- Le vrai lundi de la semaine 32 est le **3 août 2026** (le 4 août est un mardi).
  `calendrier/calendrier_editorial.json` (fichier source d'origine, jamais corrigé)
  traite encore le 4 août comme un lundi — ce calendrier-ci utilise les vraies
  semaines ISO.
- `hash()` Python n'est **pas** reproductible d'un run à l'autre (randomisé par
  défaut) — ne pas l'utiliser pour la pseudo-randomisation ; utiliser un compteur
  stable à la place (voir `wk_i` dans `generate.py`).
- Les campagnes Meta Ads doivent apparaître comme **fiches distinctes info-only**
  dans la vue semaine (`metaAdsCardHTML()` appelée depuis `renderWeek()` via
  `adsOverlappingWeek()`, qui compare `debut_iso`/`fin_iso` de la semaine et de la
  campagne) — ne jamais les fusionner avec le budget forfait AORA.

## QA avant toute publication

```bash
# Depuis outils/calendrier_editorial/, après build :
node -e "
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  await page.goto('file://' + process.cwd() + '/../../rapports/calendrier_editorial_excellence_plus.html', { waitUntil: 'networkidle' });
  console.log('entries:', await page.evaluate(() => window.ENTRIES.length));
  console.log('js errors (hors Google Fonts, bloqué en sandbox):', errors.filter(e => !e.toLowerCase().includes('font')));
  await browser.close();
})();
"
python3 ../../scripts/validate_repo.py
```
