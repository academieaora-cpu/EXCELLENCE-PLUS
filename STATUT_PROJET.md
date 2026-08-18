# STATUT DU PROJET — Excellence+ × AORA

> Document de continuité de session. À lire en complément des 4 fichiers de la
> LECTURE OBLIGATOIRE (`CLAUDE.md`). Mis à jour à chaque livraison majeure —
> si tu reprends ce projet dans une nouvelle session, lis ce fichier en premier
> pour connaître l'état réel du repo sans avoir à tout re-déduire du git log.

Dernière mise à jour : 18 août 2026.

## Branches

- **Branche de travail courante** : `claude/validation-formula-root-uwvxvh`
  (élargissement de la formule de validation à la racine « valid » + alignement de
  l'ID de Page, 18/08/2026 — voir points de vigilance 16 et 17)
- **Branche de travail précédente** : `claude/appliquer-changeset-excellence-plus-ylnsd4`
  (recalage CE-EXC-001/LE-EXC-001/PE-EXC-001 du 18/08/2026, voir point de vigilance 15)
- **Branches de travail précédentes** : `claude/meta-ads-publie-aora-ik6u82` (pipeline Meta
  Ads, fusionnée dans `main` le 05/08/2026), `claude/excellence-plus-repo-setup-rs7efy`
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
| **CE-EXC-001** | `rapports/calendrier_editorial_excellence_plus.html` | **Refondu le 18/08/2026** — nouvelle architecture HTML (fiches `<details class="fiche-card">` groupées par mois, statuts cliquables À produire/Bloqué/etc., glossaire intégré) ; **n'est plus produit par `outils/calendrier_editorial/`** (voir README de ce dossier, superséde). **août 2026 → janvier 2027 (6 mois pleins)**, 78 publications Facebook/WhatsApp/Instagram (13/mois) + TikTok hors grille. Première publication : lundi 03/08/2026 06h00 (remplace le 10/08 retenu le 03/08). 4 canaux ouverts SIMULTANÉMENT (remplace l'ouverture progressive). **Version courante.** |
| — | `rapports/calendrier_client_excellence_plus_aout_septembre.html` + `.pdf` (CC-EXC-001) | **Supprimé le 18/08/2026** (commits `da57bfd`/`4b6837f`, hors session). Aucun livrable client de rechange déposé à ce jour — si un extrait client est de nouveau nécessaire, `outils/calendrier_client/` existe encore mais lit une structure de données (`window.ENTRIES`) que CE-EXC-001 n'a plus depuis sa refonte : il faudra l'adapter à la nouvelle structure, pas simplement le relancer. |
| **LE-EXC-001** | `rapports/ligne_editoriale_excellence_plus.html` + `.pdf` | **Version 1.1 (18/08/2026)** — Section 5 (stratégie plateformes) et Section 6 (cadence) réécrites : 4 canaux simultanés, lundi/mercredi/samedi 06h00/12h00/06h00, statut réel du volet Meta Ads (verrouillé, pas de campagne en cours). Résout la vigilance historique §5 (recalage sur le calendrier actif). |
| **PE-EXC-001** | `rapports/planification_editoriale_excellence_plus.html` + `.pdf` | **Version 2.1 (18/08/2026)** — Sections 1, 2, 3, 4 recalées sur la même base que LE-EXC-001 (03/08 au lieu du 11/08, 4 canaux simultanés au lieu d'une hiérarchie 1-4 progressive). Thèmes mensuels (Section 3) et budget (Section 6) déjà corrects, non retouchés. |
| **MA-EXC-001** | `meta-ads/` + `.github/workflows/publish_scheduled_metaads.yml` + `routines/routine4_metaads.md` | **Pipeline Meta Ads (05/08/2026)** — miroir payant de `composio-publie-aora`. 4 portes bloquantes (activation temporelle · BAB budgétaire · BAP contenu + visuel · cohérence du compte), plafond budgétaire dur vérifié avant appel API, idempotence triple clé, conversion WAT→UTC, échecs typés. Groupes Facebook en simulation forcée. **État : verrouillé** — les 4 portes sont fermées, aucune campagne créable. Devenu **Routine 4**, à 03h00 WAT (même heure que R1) + lundi 08h00 WAT. Détail : `meta-ads/README.md`. |

## Outillage préservé dans le repo

- `outils/calendrier_editorial/` — ⚠️ **superséde depuis le 18/08/2026** (CE-EXC-001
  a une structure HTML entièrement différente désormais — voir point de
  vigilance 15 et le README du dossier). Pipeline conservé à titre historique
  (`generate.py` → `build_data.py` → `inject_template.py` → HTML autonome,
  **100 % déterministe**) — ne pas le relancer en pensant régénérer le fichier
  courant, il produirait l'ancienne architecture (`window.ENTRIES`/`WEEKS`) et
  l'écraserait.
- `outils/calendrier_client/` — génère CC-EXC-001 (supprimé le 18/08/2026, voir
  tableau des livrables) à partir des données produites par
  `calendrier_editorial/generate.py`. Doublement obsolète pour l'instant : sa
  source de données ne correspond plus à CE-EXC-001, et le livrable qu'il
  produit n'existe plus. `MOIS_CIBLES` dans `build_pdf.py` contrôlait la période
  extraite ; technique clé conservée pour référence : sections piliers en
  `<table><thead>` (pas de simples `<div>`) pour que l'en-tête coloré du pilier
  se répète automatiquement sur les pages de continuation en impression.
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
5. **Résolu le 18/08/2026** — LE-EXC-001 est recalé (v1.1, Sections 5-6 : 4
   canaux simultanés, cadence lundi/mercredi/samedi). Voir point 15 pour le
   détail de la correction et de son origine.
6. **CC-EXC-001 supprimé le 18/08/2026** (hors session — voir tableau des
   livrables) : plus de pendant client du tout, pas seulement une couverture
   incomplète. Si un extrait client redevient nécessaire, `outils/calendrier_client/`
   devra d'abord être adapté à la nouvelle structure de CE-EXC-001 (plus de
   `window.ENTRIES`) avant de pouvoir être relancé.
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

9. **(05/08/2026) `scenarios_budget_metaads.pdf` est absent du dépôt.** C'est pourtant
   la seule source de vérité sur les montants des 4 scénarios (Essentiel 30k /
   Standard 50k / Accéléré 75k / Objectif 50 100k FCFA). Les montants ne vivent
   aujourd'hui que dans un commentaire de `meta-ads/config/meta_ads_budgets.json`,
   sans document opposable derrière. **Traité comme une porte, pas comme une note** :
   `verifier_activation.py` refuse d'ouvrir la porte 2 tant que le fichier manque,
   même `scenario_retenu` et `montant_mensuel_fcfa` renseignés. Déposer le PDF (ou
   son extraction .md) à la racine du dépôt lève ce point.
10. **(05/08/2026) Ciblage Meta Ads — les 4 zones pondérées n'ont pas de quartiers.**
   Le modèle retenu est 4 zones pondérées sur tout Yaoundé (A 25 % / B 35 % / C 30 % /
   D 10 %), mais la répartition des quartiers entre ces zones n'existe nulle part dans
   le dépôt : `brand_guidelines.md` §3 documente 3 zones RECO-001, avec le conflit Odza
   (premium vs Extension) et Santa Barbara (absent de RECO-001) explicitement non
   tranché — voir point 7. Passer de 3 zones à 4 n'est pas un renommage, aucune
   correspondance n'est documentée. `meta_ads_ciblage.json` porte donc
   `ciblage_utilisable: false` et des `quartiers: []` ; `construire_campagne.py` refuse
   de construire un ad set. Même statut pour la tranche d'âge (35-70 vs 30-76, point 2).
   **Rien n'a été inventé** — remplir ces listes est une décision d'équipe.
11. **(05/08/2026) Trois identifiants Meta manquent** dans
   `meta-ads/config/meta_ads_comptes.json` : `ad_account_id`, `instagram_actor_id`,
   `devise_compte`. Ce sont des valeurs réelles à obtenir de M. NDOMMIE ou du Business
   Manager AORA. Elles n'ont été ni devinées, ni découvertes par un listing d'API
   (`ads_get_ad_accounts` était disponible en session et n'a délibérément pas été
   appelé) : un compte atteignable n'est pas un compte autorisé, et c'est exactement la
   confusion que la porte 4 existe pour empêcher. `devise_compte` n'est pas cosmétique —
   l'API attend les budgets en unité mineure de la devise du compte, soit un facteur 100
   entre XAF et EUR/USD. **`ad_account_id` est l'action humaine la plus bloquante du
   dispositif Meta Ads.**
12. **(08/08/2026) Périmètre scolaire cible élargi sur décision d'équipe, non confirmé par
   écrit côté client.** `brand_guidelines.md` §3 limitait jusqu'ici la cible à Collège
   (4e/3e/BEPC) + Lycéens en préparation Bac, francophone uniquement. Élargi à SIL–Terminale,
   francophone et anglophone, à la demande du compte academieaora@gmail.com en session — sans
   trace écrite de M. NDOMMIE. Répercuté sur `contenu/facebook/EXC-FB-2026-001.md` et
   `meta-ads/config/meta_ads_ciblage.json` (`langues`, `demographie.cible`) pour cohérence
   interne ; le ciblage Meta Ads reste `ciblage_utilisable: false` par ailleurs, donc sans effet
   réel. **À confirmer par écrit auprès du client dès que possible** — traiter comme une
   hypothèse de travail tant que ce n'est pas fait, ne jamais la présenter comme un fait validé
   dans un livrable client.
13. **(10/08/2026) Créneaux Lundi/Mercredi/Samedi (modifiés le 02/08/2026) retenus sans trace
   écrite client.** `config/creneaux.json` notait « NON CONFIRMÉ » depuis le 02/08 — aucun email
   de M. NDOMMIE archivé dans `validation/BAP/` sur ce changement précis de jours/heures. Le
   compte academieaora@gmail.com a affirmé en session que la validation avait eu lieu
   physiquement à la signature du contrat ; aucun document contractuel n'est présent dans le
   dépôt pour le vérifier, et la chronologie pose question (la signature précède en principe
   l'ajustement du 02/08, qui remplaçait un créneau déjà en place). Retenu comme décision
   d'équipe, pas comme fait client vérifié — voir la note datée dans `config/creneaux.json`. Si
   M. NDOMMIE réagit un jour à ce créneau précis, traiter comme un point ouvert à reprendre avec
   lui, pas comme un changement pré-validé à défendre.

14. **(17/08/2026) Stéphane désigné « autorité suprême du projet » dans `CLAUDE.md`**,
   avec son email de contact, sur instruction directe donnée en session par le compte
   academieaora@gmail.com (confirmée explicitement via question de clarification —
   portée voulue : décision finale sur le dépôt, les choix éditoriaux et les
   instructions ; validation ou refus de tout livrable). Aucun accès GitHub n'a été
   accordé : le repo n'a qu'un seul collaborateur (`academieaora-cpu`), aucun outil
   d'invitation de collaborateur n'est disponible en session, et une invitation
   GitHub réelle nécessiterait de toute façon un nom d'utilisateur GitHub, pas
   seulement un email. Si un accès technique (GitHub, Slack, etc.) est requis plus
   tard, il devra être accordé manuellement par un administrateur du compte
   academieaora-cpu, avec l'identifiant exact du compte cible.
   **(17/08/2026, suite)** Compte GitHub de Stéphane communiqué en session :
   `github.com/olouou` (existence vérifiée via `search_users`, id 109242639).
   Toujours pas de collaborateur ajouté — reste une action manuelle à faire par
   un administrateur de `academieaora-cpu` sur
   `github.com/academieaora-cpu/EXCELLENCE-PLUS/settings/access` (Add people →
   `olouou` → rôle Write ou Admin → l'invitation doit ensuite être acceptée par
   `olouou` avant que l'accès soit effectif).

15. **(18/08/2026) CE-EXC-001 refondu hors session, deux contradictions avec
   la vérité machine tranchées en session par le compte academieaora@gmail.com :**
   - CE-EXC-001 fait désormais démarrer les publications au **lundi 03/08/2026**
     (semaine ISO 32), alors que `config/creneaux.json` et
     `calendrier/semaine_active.json` disaient depuis le 03/08 que la bonne date
     était le 10/08 (semaine 33). **Tranché : le 03/08 est la nouvelle réalité**
     — `config/creneaux.json` (`premiere_publication`, `_historique_creneaux`)
     et `calendrier/semaine_active.json`/`calendrier_editorial.json` corrigés en
     conséquence.
   - CE-EXC-001 montre Facebook + WhatsApp + Instagram simultanés dès août, alors
     que `config/creneaux.json` prévoyait une ouverture progressive (Instagram
     09/2026, TikTok 10/2026). **Tranché : l'ouverture simultanée est la nouvelle
     réalité** — `canaux.activation` et `creneaux.{whatsapp,instagram}` ajoutés
     dans `config/creneaux.json` (miroir exact de `facebook`) ; TikTok reste hors
     grille fixe (~1×/mois, vidéo source requise), aucun triplet jour/heure/pilier
     ne lui est inventé.
   Répercuté dans LE-EXC-001 (v1.1), PE-EXC-001 (v2.1), `routines/routine1_*.md`,
   `routines/routine2_*.md`, `superviseur-publication-aora/SKILL.md` (Contrôle 2),
   et une note de dépréciation ajoutée à `outils/calendrier_editorial/` (dont la
   sortie ne correspond plus à la structure HTML actuelle de CE-EXC-001 — ne pas
   le relancer en pensant régénérer le fichier courant).
   **Point ouvert découvert au passage, non résolu** : `contenu/facebook/EXC-FB-2026-001.md`
   (le seul post réellement rédigé du dépôt, `date_publication: 2026-08-10`,
   titre « Préparer la rentrée — trois gestes à commencer maintenant ») ne
   correspond à aucune fiche de CE-EXC-001 pour cette date ni pour aucune autre —
   ni le sujet, ni l'angle. Il est orphelin par rapport au plan actuel. Noté dans
   `calendrier/semaine_active.json` ; à trancher avec Stéphane/Laurence (le
   retirer, le recaler sur une fiche existante, ou le garder hors-plan) avant
   tout BAT/BAP sur ce fichier.
   **Autre point ouvert** : seul un post est rédigé dans tout le dépôt
   (`contenu/facebook/EXC-FB-2026-001.md`) alors que le plan recalé attend 7
   publications Facebook entre le 03/08 et le 18/08 (aujourd'hui) — retard de
   production réel, pas seulement un décalage de date de lancement. `posts_a_produire`
   dans `calendrier/semaine_active.json` est volontairement laissé vide (voir sa
   `_lisez_moi`) plutôt que de contenir des identifiants inventés.
   **Résolu le 18/08/2026 (même jour, décision de posture)** : le compte
   academieaora@gmail.com a tranché en session que ce retard **n'est pas à
   rattraper** — pas de production en rafale pour combler les créneaux du 03
   au 17/08. La routine de production regarde uniquement vers l'avant (le
   prochain créneau à venir), et **le sujet précis d'un créneau donné n'est
   plus figé** : CE-EXC-001 propose un angle par créneau, mais l'équipe peut
   le changer jour au jour (actualité, occasion) sans que ce soit un écart —
   seule la structure (jour/heure/canal/pilier dominant) reste fixe. Répercuté
   dans `config/creneaux.json` (`_lisez_moi`), `calendrier/semaine_active.json`
   et `routines/routine2_production.md`.

16. **Résolu le 18/08/2026 — l'ID de la Page Facebook avait divergé entre trois
   fichiers.** `config/page_cible.json` a été corrigé le 15/08/2026 (commit
   `149aef4`) : l'identifiant réel de la Page « Excellence+ Éducation » est
   **885480714646404**, l'ancien **61584305458367** était erroné. Deux copies de
   l'ancienne valeur avaient survécu à cette correction et n'ont été trouvées que
   le 18/08 : `superviseur-publication-aora/SKILL.md` (Contrôle 1 et §6, qui
   auraient fait signaler comme **⚠️ CRITIQUE** une publication pourtant partie
   sur la bonne Page) et `meta-ads/config/meta_ads_comptes.json` → `page_id`
   (que `verifier_conformite_ads.py` signalait effectivement en CRITIQUE : deux
   fichiers se contredisant sur la Page cible). Les deux sont alignés sur
   `config/page_cible.json`, qui reste la seule source de vérité ; §6 du skill,
   qui décrivait encore la procédure « créer le fichier s'il est absent », est
   requalifié en historique — le fichier existe depuis le 03/08.
   **Leçon à retenir, pas seulement un correctif** : corriger un identifiant dans
   son fichier de vérité ne suffit pas — il faut `grep` l'ancienne valeur dans
   tout le dépôt le jour même. Le contrôle automatique n'a rattrapé qu'une des
   deux copies (celle de `meta_ads_comptes.json`) ; l'autre vivait dans un
   document de skill, hors de portée de tout script.

17. **(18/08/2026) La reconnaissance d'une validation client passe de la formule
   exacte à la racine « valid ».** `config/validation_formules.json` exigeait
   jusqu'ici une correspondance avec une liste figée de phrases (élargie une
   première fois le 12/08 pour y ajouter « BAP VALIDÉ »). M. NDOMMIE n'a
   historiquement jamais repris une de ces formules mot pour mot : exiger
   l'exactitude a raté des validations réelles plus souvent qu'elle n'en a
   protégé. Le fichier porte désormais `tige_reconnue` (« valid ») et toute forme
   du verbe compte comme signal positif — valide, validé, validée, validons,
   validation. `\bvalid\w*` ne matche pas dans « invalide »/« invalider »
   (aucune limite de mot entre le préfixe et la racine) — vérifié par test.
   `mots_disqualifiants` passe de 14 à 28 entrées : élargir la détection positive
   rend cette liste **plus** critique, pas moins, puisqu'une correspondance sur la
   seule racine attrape aussi « je NE valide PAS » — ce qu'une correspondance sur
   la phrase entière évitait par accident. Répercuté dans
   `meta-ads/scripts/verifier_conformite_ads.py` (Contrôle 8) et
   `superviseur-publication-aora` (Contrôle 8 + checklist, v1.2).
   **Ce que ce changement ne fait pas** : `scripts/traiter_bap.py` ne lit toujours
   pas `validation_formules.json` — le rapprochement entre l'email reçu et le
   fichier déposé dans `validation/BAP/` reste une décision humaine, ce fichier
   n'en est que le critère documenté. Aucun mot-clé ne remplace la lecture
   complète de l'email, et les 3 autres conditions (expéditeur exact, objet
   identifié, aucune réserve) s'appliquent toujours en plus.
   **Reste à faire, hors dépôt** : le skill `community-manager-aora` (§Cas
   Excellence+) porte encore un « ⚠️ Point de vigilance ouvert » sur le
   désalignement gabarit email / `validation_formules.json`. Ce désalignement est
   résolu depuis le 12/08 et sans objet depuis le 18/08. Ce skill ne vit pas dans
   ce dépôt (il est synchronisé depuis le Projet claude.ai) : la requalification en
   « historique résolu » doit être faite là-bas, elle ne peut pas l'être ici.

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
> août 2026 → janvier 2027, 6 mois) est à jour dans `rapports/` — refondu le
> 18/08/2026, plus produit par `outils/calendrier_editorial/` (superséde, voir
> son README). CC-EXC-001 (client) a été supprimé le 18/08/2026, pas de
> remplaçant à ce jour.

Rien d'autre n'est en attente à ce stade — tous les livrables demandés ont été
poussés sur `main` et la branche de travail.

Sur les 15 points de vigilance ci-dessus, **aucun ne bloque la production
éditoriale au sens strict**, mais le point 15 signale un vrai retard de
production (1 seul post rédigé sur 7 attendus depuis le 03/08) et un post
orphelin par rapport au plan actuel. Trois autres bloquent le pipeline Meta Ads
(points 9, 10, 11) — c'est voulu : le dispositif est conçu pour rester verrouillé
tant qu'une valeur humaine manque, plutôt que de tourner sur une supposition. Le
plus bloquant est `ad_account_id`, parce que c'est le seul qu'aucun arbitrage
interne ne peut lever.

**Meta Ads reste par ailleurs non activé au mois 1 (août 2026) par contrat
AORA-CCC-005** : même si les trois points ci-dessus étaient résolus demain, la
porte 1 resterait fermée jusqu'à une activation écrite pour septembre.
