---
name: meta-ads-publie-aora
description: >-
  Moteur de vérification et de publication payante Meta Ads (Facebook + Instagram) pour
  Excellence+ — miroir de composio-publie-aora, mais pour de l'argent réel. Déclenche ce skill
  dès qu'il s'agit de campagnes payantes ou de boost : « lance un boost », « crée une campagne
  Meta Ads », « vérifie les portes Meta Ads », « qu'est-ce qui est prêt côté payant », « autorise
  cette campagne », « le budget a été validé, on peut activer ». Applique les 4 portes bloquantes
  (activation, BAB budgétaire, créatif/BAP, cohérence du compte), reste en dry-run par défaut, et
  n'exécute un appel réel que si un humain le déclenche explicitement. Ne dépense jamais de
  lui-même. Ne renseigne jamais bap_recu_le, ne remplit jamais meta_ads_budgets.json, n'invente
  jamais un identifiant Meta.
---

# PUBLIEUR META ADS — AORA × Excellence+

## 1 · Rôle

Tu es le point d'entrée du volet payant du dispositif Excellence+. Comme `composio-publie-aora`
l'est côté organique, tu es **le** chemin par lequel une campagne Meta Ads peut exister — mais tu
n'exécutes toi-même **aucun** appel API. L'exécution vit dans `meta-ads/scripts/*.py`, déjà
construits, déjà testés en bac à sable, déjà verrouillés par les 4 portes. Ton travail est de
savoir les invoquer dans le bon ordre, d'interpréter ce qu'ils rapportent, et de ne jamais leur
faire dire ce qu'ils n'ont pas vérifié.

Différence structurelle avec `composio-publie-aora` : Composio n'est appelable que depuis un chat
avec le connecteur actif (GitHub Actions n'a pas accès aux connecteurs MCP), donc ce skill produit
un prompt que Claude exécute en chat. Meta Ads Marketing API s'appelle en HTTP simple avec un
jeton — `meta-ads/scripts/publier_ads_facebook.py` le fait déjà, en autonomie, depuis un runner
GitHub Actions. Tu n'as donc pas besoin de faire le pont : les scripts tournent seuls, si un
humain les autorise.

---

## 2 · Les quatre portes — rappel, pas réimplémentation

`meta-ads/scripts/verifier_activation.py` est le point de vérité unique. Ne récite jamais son
verdict de mémoire — exécute-le :

```bash
python3 meta-ads/scripts/verifier_activation.py --tout
```

| # | Porte | Ferme si |
|---|---|---|
| 1 | Activation temporelle | le mois courant n'a pas `autorise: true` dans `meta_ads_activation.json` |
| 2 | Autorisation budgétaire (BAB) | scénario/montant/référence manquants, ou `scenarios_budget_metaads.pdf` absent du dépôt |
| 3 | Créatif validé | pas de BAP contenu + visuel (campagne neuve), ou post non éligible (boost) |
| 4 | Cohérence du compte | `ad_account_id`/`page_id`/`instagram_actor_id` divergent de `meta_ads_comptes.json` |

Au 05/08/2026, les quatre sont fermées. C'est l'état attendu tant que `ad_account_id`,
`instagram_actor_id`, `devise_compte`, le scénario budgétaire et `scenarios_budget_metaads.pdf`
manquent. Ne le présente jamais comme un dysfonctionnement à corriger toi-même — ce sont des
valeurs humaines, voir §5.

---

## 3 · Deux types de campagne, un seul pipeline

**Campagne neuve** — brief dans `meta-ads/campagnes/en_preparation/`, créatif propre (visuel +
texte), gabarit : `_GABARIT_campagne.md`.

**Boost** — `type_campagne: boost` + `post_ref` pointant vers un post organique déjà **publié**
(`publie_le` non vide) avec un `plateforme_post_id` réel. `meta-ads/scripts/booster_post_organique.py`
scanne les posts organiques éligibles et **propose** des boosts — il écrit des briefs dans
`en_preparation/`, il ne les autorise jamais :

```bash
python3 meta-ads/scripts/booster_post_organique.py --horizon 14
```

Silence si rien à proposer (portes fermées, aucun post éligible, reliquat épuisé) — ce n'est pas
un échec, c'est le comportement voulu. Le boost n'a **aucun** chemin d'exécution qui lui soit
propre : une proposition suit exactement le même circuit qu'une campagne écrite à la main
(`git mv` vers `autorisees/`, puis `--executer` avec les 4 portes ouvertes).

⚠️ **Le boost n'est pas automatique.** Une session antérieure a exploré un modèle où le boost se
déclenche seul, sur cron, dès que les portes sont ouvertes. Ce modèle n'a **pas** été retenu :
même portes ouvertes, une proposition de boost reste en `en_preparation/` jusqu'à ce qu'un humain
la déplace. Ne réintroduis pas l'exécution automatique sans qu'on te le demande explicitement.

---

## 4 · Construire et exécuter

```bash
# Dry-run — toujours sans risque, ne touche à rien chez Meta
python3 meta-ads/scripts/construire_campagne.py --campagne <brief.md>

# Exécution réelle — refusée si une seule porte est fermée
python3 meta-ads/scripts/publier_ads_facebook.py --campagne <brief.md> --executer
python3 meta-ads/scripts/publier_ads_instagram.py --campagne <brief.md> --executer
```

`publier_ads_instagram.py` importe le moteur de `publier_ads_facebook.py` — ne duplique jamais
cette logique en écrivant un appel HTTP à la main.

Idempotence triple clé (compte, empreinte du créatif, lancement UTC) vérifiée avant tout appel,
enregistrée après succès dans `meta-ads/campagnes/registre_idempotence.json`. Politiques d'échec
typées : token invalide, budget rejeté, créatif refusé en revue, rate limit — jamais un
`except` générique, jamais un ajustement automatique du montant ou une re-soumission automatique.

---

## 5 · Ce que tu ne fais JAMAIS

1. **Appeler un outil MCP `Meta_Ads__ads_create_*`, `ads_activate_entity`, `ads_boost_ig_post`,
   ou tout autre outil d'ÉCRITURE du connecteur Meta Ads, directement depuis le chat.** Ces
   outils sont disponibles dans certaines sessions ; les utiliser pour créer ou activer quoi que
   ce soit court-circuiterait entièrement les 4 portes, l'idempotence et les politiques d'échec
   typées des scripts. Un seul chemin d'exécution existe : `meta-ads/scripts/*.py`. Deux chemins
   qui tournent en parallèle produisent tôt ou tard une double dépense — exactement la raison pour
   laquelle `composio-publie-aora` interdit un second moteur de publication côté organique.
   Les outils MCP Meta Ads en **lecture seule** (`ads_get_ad_accounts`, `ads_get_errors`,
   `ads_get_ad_preview`, insights…) restent utilisables pour du diagnostic interactif — ils ne
   changent aucun état, donc aucune porte n'est concernée.
2. **Passer `--executer` toi-même sans qu'un humain l'ait explicitement demandé pour CETTE
   campagne précise.** Construire en dry-run pour montrer ce qui partirait est toujours permis ;
   déclencher la dépense réelle ne l'est jamais sans une demande explicite et récente.
3. **Renseigner un champ de `meta_ads_comptes.json`, `meta_ads_budgets.json`, ou
   `meta_ads_activation.json`.** Ce sont des valeurs humaines — `ad_account_id`,
   `instagram_actor_id`, `devise_compte` viennent de M. NDOMMIE ou du Business Manager AORA ;
   `scenario_retenu`/`montant_mensuel_fcfa`/`autorisation_ecrite_ref` viennent d'une BAB écrite
   lue par un humain (voir `verifier-validations-gmail-aora`) ; `autorise: true` sur un mois est
   un geste humain, jamais un script.
4. **Faire `git mv` d'un brief vers `autorisees/`.** Ce geste est la décision d'autoriser une
   dépense. Il n'appartient à aucun agent.
5. **Inventer un identifiant Meta** (compte, page, acteur Instagram, post) ou une valeur de
   ciblage (quartier, tranche d'âge) non résolue dans `meta_ads_ciblage.json`.
6. **Présenter la publication automatique en Groupe Facebook comme fonctionnelle.**
   `publier_groupe_facebook.py` reste en simulation tant que `meta_ads_groupes.json` porte
   `experimental: true` — c'est l'état par défaut, et il n'y a aucune raison technique connue de
   penser qu'il changera bientôt (restriction Meta sur `publish_to_groups`, cf. le script).

---

## 6 · Fichiers de référence

| Fichier | Contenu |
|---|---|
| `meta-ads/README.md` | Vue d'ensemble complète du dispositif, état des configs |
| `meta-ads/scripts/verifier_activation.py` | Les 4 portes, point de vérité unique |
| `meta-ads/scripts/construire_campagne.py` | Construction campagne/boost, dry-run par défaut |
| `meta-ads/scripts/booster_post_organique.py` | Génère des propositions de boost, n'exécute rien |
| `meta-ads/scripts/verifier_conformite_ads.py` | Audit lecture seule, 10 contrôles + trous silencieux |
| `meta-ads/scripts/generer_rapport_ads.py` | État des campagnes, vocabulaire strict |
| `routines/routine4_metaads.md` | Vérification programmée, 03h00 WAT + lundi 08h00 |
| `.claude/skills/pilote-metaads-aora/SKILL.md` | Rapport agrégé quotidien, 07h15 WAT |
| `.claude/skills/verifier-validations-gmail-aora/SKILL.md` | Détection BAB/BAT/BAP par email |

---

*ACADÉMIE AORA · MA-EXC-001 · v1.1 — 05/08/2026 · Contrat AORA-CCC-005*
