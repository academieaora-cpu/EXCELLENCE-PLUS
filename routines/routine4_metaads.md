# ROUTINE 4 — Vérification et propositions Meta Ads

> **Cette routine ne dépense rien et ne crée aucune campagne.** Elle vérifie les quatre portes,
> audite la conformité, **propose** des boosts (sans les autoriser), et rapporte. La création
> d'une campagne — neuve ou boost — reste un geste manuel explicite, du premier au dernier pas.

## Paramétrage

```
Nom       : Excellence+ — Vérification Meta Ads
Dépôt     : academieaora-cpu/EXCELLENCE-PLUS · branche main
Type      : GitHub Actions — .github/workflows/publish_scheduled_metaads.yml (PAS une Routine
            Claude Code Remote — aucun appel LLM dans cette routine, uniquement des scripts
            Python déterministes)
Connecteurs requis : aucun (Slack via webhook/token en secret, pas via connecteur de chat)

Deux passages quotidiens, deux rôles distincts :

  03h00 WAT (02h00 UTC) ← même heure que la Routine 1
    verifier_activation.py --tout · verifier_conformite_ads.py ·
    booster_post_organique.py (écrit des propositions dans en_preparation/, commit
    encadré à ce seul dossier) · rapport local (artefact, pas de Slack)

  07h15 WAT (06h15 UTC) ← 15 min après R2 (production organique, 07h00 WAT)
    generer_rapport_ads.py --slack — lecture seule, rien n'est écrit dans le dépôt.
    C'est le rapport du skill pilote-metaads-aora, posté dans le fil Meta Ads dédié.
```

**Pourquoi la même heure que R1 pour le passage de 03h00** — le périmètre payant se vérifie au
moment où le périmètre organique se programme. C'est aussi le seul moment où ce dispositif écrit
quoi que ce soit dans le dépôt (les propositions de boost) — comme R1, qui committe à 03h00 avant
que quiconque soit devant son écran.

**Pourquoi 07h15 et pas le lundi 08h00** — une version antérieure alignait un second passage sur
`rapport_hebdo.yml` (lundi 08h00, hebdomadaire). Remplacé le 05/08/2026 par un rapport **quotidien**
à 07h15, juste après R2 : l'équipe voit la production du jour et l'état Meta Ads dans la même
fenêtre, tous les jours, pas seulement le lundi. Garder les deux aurait doublé le même message à
moins d'une heure d'écart un lundi sur deux — le genre de bruit qui fait qu'on arrête de lire un
rapport.

**Pourquoi pas toutes les 15 minutes** — c'était la cadence du `publish_scheduled.yml` supprimé le
03/08/2026. Un pipeline qui ne dépense que sur déclenchement manuel n'a aucune raison de se
réveiller 68 fois par jour : la réactivité n'est pas l'enjeu, la traçabilité l'est.

## Ce que le passage de 03h00 committe, et le garde-fou qui l'encadre

`booster_post_organique.py` n'écrit que des fichiers `BOOST-*.md` dans
`meta-ads/campagnes/en_preparation/` — jamais `autorisees/`, jamais un config, jamais un post
organique. Le job GitHub Actions applique un second contrôle, indépendant du script : après
exécution, il relit `git status --porcelain` en entier et refuse de committer quoi que ce soit
si un seul fichier hors de ce dossier a bougé. Ce n'est pas une méfiance envers le script — c'est
la même discipline que le plafond budgétaire : vérifier avant d'agir, jamais faire confiance
après coup.

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

## Ce que fait chaque passage automatique

```
TOUJOURS, d'abord :
  0. Halte si PAUSE existe à la racine — si présent, aucune étape suivante ne
     s'exécute (le job sort proprement, aucun fichier n'est produit).

À 03h00 WAT ET à 07h15 WAT :
  1. python3 meta-ads/scripts/verifier_activation.py --tout
     Les quatre portes, évaluées toutes les quatre (--tout) pour que le rapport
     dise POURQUOI c'est fermé, pas seulement QUE c'est fermé.
     Une porte fermée n'est pas une panne du job : c'est l'information attendue.

  2. python3 meta-ads/scripts/verifier_conformite_ads.py
     Les 10 contrôles internes du script + la détection des trous silencieux
     (campagne autorisée jamais lancée, active jamais confirmée, BAB non
     reliée, proposition de boost oubliée).

UNIQUEMENT à 03h00 WAT (github.event.schedule == '0 2 * * *') :
  3. python3 meta-ads/scripts/booster_post_organique.py --horizon 14
     Propose des boosts pour les posts organiques publiés éligibles. Silence
     si rien à proposer — ce n'est jamais un échec.

  4. Commit encadré : seuls des fichiers sous meta-ads/campagnes/en_preparation/
     peuvent partir dans ce commit. Tout le reste fait échouer le job avant
     tout git add — voir « le garde-fou qui l'encadre » ci-dessus.

TOUJOURS, ensuite :
  5. python3 meta-ads/scripts/generer_rapport_ads.py [--slack si 07h15]
     Vocabulaire strict. « en ligne » n'est employé qu'après confirmation API.
     --slack uniquement à 07h15 : le passage de 03h00 reste local (artefact),
     personne n'a besoin d'un ping Slack à 3h du matin.

  6. Artefacts conservés 14 jours : portes.txt, rapport_metaads.txt,
     propositions_boost.txt (si le passage de 03h00 en a produit).
```

Aucune de ces étapes n'appelle l'API Meta en écriture. Aucune ne peut dépenser — la seule écriture
qui existe dans tout ce parcours est le commit encadré de l'étape 4, et il ne peut toucher qu'un
brief en attente d'autorisation, jamais une campagne active ni un centime.

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

**Nuance sur ce tableau, depuis l'ajout du boost (05/08/2026)** : *écrire une proposition* de
boost dans `en_preparation/` EST automatique, à 03h00. Ce n'est pas une exception à ce tableau —
c'est exactement ce que fait déjà un humain qui rédige un brief à la main : ça atterrit dans
`en_preparation/`, un dossier qui, par construction, ne signifie rien d'autorisé. Ce que ce
tableau protège reste intact : rien ne quitte `en_preparation/` sans le `git mv` d'un humain.

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
