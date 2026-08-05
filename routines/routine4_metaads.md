# ROUTINE 4 — Vérification Meta Ads

> **Cette routine ne dépense rien et ne crée aucune campagne.** Elle vérifie les quatre portes,
> audite la conformité, et rapporte. La création d'une campagne reste un geste manuel explicite.

## Paramétrage

```
Nom       : Excellence+ — Vérification Meta Ads
Cadence   : Chaque jour
Heure     : 03h00 WAT  (02h00 UTC)  ← même heure que la Routine 1
Passage supplémentaire : lundi 08h00 WAT (07h00 UTC) ← même heure que rapport_hebdo.yml
Dépôt     : academieaora-cpu/EXCELLENCE-PLUS · branche main
Type      : GitHub Actions — .github/workflows/publish_scheduled_metaads.yml
Connecteurs requis : Slack (fil Meta Ads dédié) · Meta Marketing API en lecture seule
```

**Pourquoi la même heure que R1** — le périmètre payant se vérifie au moment où le périmètre
organique se programme. Une seule lecture du dispositif le matin, pas deux à des heures
différentes qu'on finit par ne plus rapprocher. Le rapport de R4 attend l'équipe à côté de celui
de R1.

**Pourquoi un passage lundi 08h00** — le rapport de 03h00 s'écrit quand personne n'est réveillé.
Celui du lundi arrive avec l'équipe, en même temps que le rapport hebdomadaire organique.

**Pourquoi pas toutes les 15 minutes** — c'était la cadence du `publish_scheduled.yml` supprimé le
03/08/2026. Un pipeline qui ne dépense que sur déclenchement manuel n'a aucune raison de se
réveiller 68 fois par jour : la réactivité n'est pas l'enjeu, la traçabilité l'est.

---

## Pourquoi une quatrième routine et pas une étape de la Routine 1

Même raison que pour les trois premières : **trois métiers distincts, trois routines distinctes**
(voir [README.md](README.md)). R4 échoue pour ses propres raisons — un token Marketing expiré, un
plafond dépassé, un compte publicitaire absent — et se répare séparément.

S'ajoute ici une raison propre au payant : R1 engage du contenu, R4 engage de l'argent. Les fondre
ferait qu'une erreur de configuration sur l'une exposerait l'autre. C'est la même logique qui
interdit de fusionner `publish_scheduled_metaads.yml` et `programmation_quotidienne.yml`, alors
même qu'ils tournent à la même heure : **même horaire, jamais même fichier.**

---

## Ce que fait le passage automatique

```
1. Halte si PAUSE existe à la racine.

2. python3 meta-ads/scripts/verifier_activation.py --tout
   Les quatre portes, évaluées toutes les quatre (--tout) pour que le rapport
   dise POURQUOI c'est fermé, pas seulement QUE c'est fermé.
   Une porte fermée n'est pas une panne du job : c'est l'information attendue.

3. python3 meta-ads/scripts/verifier_conformite_ads.py
   Les 9 contrôles du superviseur organique + le 10e, propre au payant :
   plafond budgétaire jamais dépassé, y compris par le CUMUL de plusieurs
   campagnes sous le plafond chacune.

4. python3 meta-ads/scripts/generer_rapport_ads.py
   Vocabulaire strict. « en ligne » n'est employé qu'après confirmation API.

5. Artefacts conservés 14 jours : portes.txt, rapport_metaads.txt
```

Aucune de ces quatre étapes n'appelle l'API en écriture. Aucune ne peut dépenser.

---

## Ce qui n'est PAS automatique — et ne le sera pas

| Geste | Qui |
|---|---|
| `git mv` d'une campagne de `en_preparation/` vers `autorisees/` | un humain, jamais un script |
| Passer un mois à `autorise: true` dans `meta_ads_activation.json` | un humain |
| Renseigner `scenario_retenu` / `montant_mensuel_fcfa` après BAB écrite | un humain |
| Créer réellement la campagne chez Meta | `workflow_dispatch` manuel, `executer: true`, **et** les 4 portes ouvertes |

Le déclenchement programmé **ne peut pas** créer de campagne : l'étape d'exécution réelle est
conditionnée à `github.event_name == 'workflow_dispatch'`. Et même là, le script revérifie les
quatre portes lui-même — la garantie est dans le code, pas dans une expression YAML.

---

## Les interdits communs — version R4

Les trois interdits des routines 1 à 3 s'appliquent (jamais de `bap_recu_le` à la main, jamais de
visuel déplacé, jamais d'email au client). S'y ajoutent ceux du périmètre payant :

1. **Jamais lancer une campagne sans les quatre portes ouvertes.**
2. **Jamais dépasser `montant_mensuel_fcfa`**, même temporairement « pour tester » — toute
   modification de plafond repasse par une nouvelle BAB écrite.
3. **Jamais mélanger le suivi Meta Ads et la facturation du forfait AORA**
   (AORA-EXCPLUS-2026-001) — deux systèmes de suivi, deux fichiers, jamais un seul tableau.
4. **Jamais présenter la publication automatique en Groupe comme fonctionnelle** avant preuve
   technique documentée.
5. **Jamais deviner un identifiant Meta**, ni le découvrir par un listing d'API : un compte
   atteignable n'est pas un compte autorisé.

---

## Avant la première exécution

R4 est la moins risquée des quatre routines — elle ne peut rien dépenser en l'état. Mais elle est
aussi **verrouillée** : les quatre portes sont fermées au 05/08/2026, et le rapport le dira tous
les matins tant que les valeurs humaines manqueront.

Ce n'est pas une panne à corriger. C'est l'état attendu tant que :

- `ad_account_id`, `instagram_actor_id`, `devise_compte` sont null ;
- aucune BAB écrite n'est archivée dans `meta-ads/validation/BAB_budget/` ;
- `scenarios_budget_metaads.pdf` est absent du dépôt ;
- août 2026 reste verrouillé par contrat (mois 1, Meta Ads non activé).

Secrets à créer dans les settings du dépôt avant que l'exécution manuelle serve à quelque chose —
**distincts de ceux de Composio** :

```
META_MARKETING_TOKEN
SLACK_WEBHOOK_URL_METAADS   (ou SLACK_BOT_TOKEN_METAADS + SLACK_CHANNEL_METAADS)
```

---

*ACADÉMIE AORA · MA-EXC-001 · Contrat AORA-CCC-005*
