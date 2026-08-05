---
name: verifier-validations-gmail-aora
description: >-
  Détection de validations client par email (BAB Meta Ads en priorité) avec correspondance de
  formule stricte, jamais déduite d'une simple impression d'accord. Déclenche ce skill sur « le
  client a répondu pour le budget », « vérifie si M. NDOMMIE a validé la BAB », « cherche les
  validations Gmail », « est-ce que cette réponse compte comme une BAP/BAT/BAB ». Ne remplace pas
  l'étape 2 de routine1_programmation.md (BAT/BAP organiques, déjà câblée et testée) — se
  concentre sur le BAB Meta Ads, nouveau et non couvert ailleurs. Écrit une preuve dans
  meta-ads/validation/BAB_budget/ si la correspondance est claire et sans ambiguïté ; ne renseigne
  jamais lui-même scenario_retenu, montant_mensuel_fcfa ou autorisation_ecrite_ref — un humain lit
  l'email et transcrit le montant, toujours.
---

# VÉRIFICATION DES VALIDATIONS GMAIL — AORA × Excellence+

## 1 · Rôle, et pourquoi son périmètre est étroit

Deux circuits de validation par email existent déjà dans ce dépôt : BAT/BAP organiques, détectés
et traités à l'étape 2 de `routine1_programmation.md` → `scripts/traiter_bap.py`. Ce circuit
fonctionne, est testé, et **tu ne le remplaces pas** — le dupliquer ici créerait deux détecteurs
de la même chose, et l'un finirait par diverger de l'autre.

Ce skill couvre ce qui manque : la **BAB** (Bon À Budgétiser), l'autorisation écrite du scénario
et du montant Meta Ads (`meta-ads/config/meta_ads_budgets.json`), distincte du BAP contenu et
gardée par la porte 2 de `verifier_activation.py`. Elle n'existait pas avant le 05/08/2026 et
n'a donc aucun circuit de détection.

---

## 2 · La leçon qui justifie la prudence de ce skill

Une session antérieure (05/08/2026) a consulté la vraie boîte Gmail (`academieaora@gmail.com`,
lecture seule) et trouvé un échange réel du jour : un email « Visuel Excellence+ » auquel
M. NDOMMIE a répondu **« Bien reçu »**.

Ce n'est **pas** une validation valide, malgré l'apparence évidente d'accord. « Bien reçu »
confirme une réception, pas une décision. Ce cas réel est la meilleure justification qui existe
dans ce dépôt pour la règle de correspondance stricte — ne l'assouplis jamais sur la base d'un
« c'est clairement ce qu'il voulait dire ». La formule exacte existe précisément pour ne pas avoir
à interpréter une intention.

---

## 3 · Ce que tu cherches

Formule attendue : `config/validation_formules.json → bab.formules_recevables`
(« Je valide ce budget pour activation. » au 05/08/2026).

⚠️ **Avant de chercher quoi que ce soit** : vérifie que le gabarit d'email envoyé à M. NDOMMIE
pour lui demander une BAB demande bien CETTE formule exacte. Au 05/08/2026, aucun gabarit du
dépôt ne l'envoie encore — le modèle d'email BAB vit dans le skill `community-manager-aora`, qui
n'est pas un fichier de ce dépôt (skill de compte, hors périmètre git), donc invérifiable d'ici.
Si tu ne peux pas confirmer que la bonne formule a été demandée, dis-le explicitement dans ton
rapport plutôt que de traiter une réponse plausible comme une validation.

Recherche Gmail (`Gmail:search_threads`, `Gmail:get_thread`) :
1. Fils dont l'objet évoque un budget/scénario Meta Ads envoyé par `academieaora@gmail.com`
   (voir `config/comptes.json → aora.email_envoi_bat` pour l'adresse d'envoi).
2. Parmi les réponses, ne retiens que celles dont l'expéditeur est **exactement** une adresse de
   `config/comptes.json → client.emails_autorises` — aucune ressemblance, aucun alias.
3. Compare le corps, en minuscules et sans accents, à la formule exacte de
   `validation_formules.json → bab.formules_recevables`. Vérifie aussi qu'aucun mot de
   `mots_disqualifiants` n'apparaît (« mais », « sous réserve », « à condition », etc.).

⚠️ **Écart de convention documenté, non résolu** : les objets email BAT/BAP/BAB ne portent
aujourd'hui aucune référence exacte de campagne ou de scénario (pas d'identifiant du type
`EXC-FB-2026-XXX`), ce qui complique le rattachement automatique d'une réponse à UNE proposition
précise. Tant que ce n'est pas corrigé dans les gabarits (`community-manager-aora`, hors dépôt),
traite tout rattachement non évident comme ambigu — voir §4.

---

## 4 · Ce que tu écris, et ce que tu n'écris jamais

**Si la correspondance est claire et sans ambiguïté** (un scénario cité dans le fil = une réponse
qui valide, formule exacte, expéditeur autorisé, aucune réserve) :

Écris un fichier dans `meta-ads/validation/BAB_budget/`, nommé
`BAB-<AAAA-MM-JJ>-<scenario-en-minuscules>.md` (ex. `BAB-2026-09-standard.md`), contenant :

```yaml
---
creatif_ref:              # si le fil le précise, sinon vide — ne jamais deviner
scenario_cite: standard    # tel que compris du fil, en minuscules
email_expediteur: excellencecontact91@gmail.com
email_id_gmail: <id du message>
recu_le: 2026-09-DD
---

<corps exact de la réponse, copié tel quel — c'est la preuve, elle ne se paraphrase pas>
```

**Tu t'arrêtes là.** Tu n'écris JAMAIS `scenario_retenu`, `montant_mensuel_fcfa`, ni
`autorisation_ecrite_ref` dans `meta-ads/config/meta_ads_budgets.json` — même après avoir lu
l'email de tes propres yeux. Ce sont les trois champs qui ouvrent la porte 2, et cette porte
gouverne un plafond de dépense réelle. Un humain (Stéphane ou Laurence) lit le fichier de preuve
que tu as écrit, confirme le montant exact, et transcrit lui-même ces trois champs. C'est plus
strict que le circuit BAP organique (où `traiter_bap.py` peut écrire `bap_recu_le` sur la base
d'un fichier de preuve) — volontairement : une BAP mal transcrite se corrige avant la prochaine
programmation, un plafond budgétaire mal transcrit autorise une dépense réelle immédiatement.

**Si ce n'est PAS clair** (aucune formule exacte, montant absent du fil, plusieurs scénarios
évoqués sans qu'on sache lequel est retenu, réserve exprimée) : n'écris **aucun** fichier.
Signale l'email comme action humaine, avec la raison précise de l'ambiguïté.

---

## 5 · Ce que tu ne fais jamais

1. Traiter « Bien reçu », « Ok merci », « C'est noté » ou toute formule d'accueil comme une
   validation — voir §2.
2. Écrire un champ de `meta_ads_budgets.json` — voir §4, aucune exception.
3. Assouplir la formule de `validation_formules.json` parce qu'une réponse « veut clairement
   dire » qu'elle valide.
4. Traiter une réponse BAT/BAP organique comme si c'était une BAB, ou l'inverse — trois
   circuits, trois formules, jamais interchangeables.
5. Envoyer un email au client, ou en rédiger un brouillon à sa place sans qu'on te le demande.

---

## 6 · Fichiers de référence

| Fichier | Contenu |
|---|---|
| `config/validation_formules.json` | Formules BAT/BAP/BAB exactes — fait foi |
| `config/comptes.json` | Adresse client autorisée, adresse d'envoi AORA |
| `meta-ads/config/meta_ads_budgets.json` | Où la BAB confirmée doit être transcrite — par un humain |
| `routines/routine1_programmation.md` | Circuit BAT/BAP organique existant, ne pas dupliquer |

---

*ACADÉMIE AORA · MA-EXC-001 · v1.0 — 05/08/2026 · Contrat AORA-CCC-005*
