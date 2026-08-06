---
name: verifier-validations-gmail-aora
description: >-
  Détection de validations client par email pour le volet Meta Ads — BAB (budget) et BAP créatif
  publicitaire — avec correspondance de formule stricte, jamais déduite d'une simple impression
  d'accord. Déclenche ce skill sur « le client a répondu pour le budget », « vérifie si M. NDOMMIE
  a validé la BAB », « le client a validé le créatif pub », « cherche les validations Gmail »,
  « est-ce que cette réponse compte comme une BAP/BAT/BAB ». Ne remplace pas l'étape 2 de
  routine1_programmation.md (BAT/BAP du contenu ORGANIQUE, déjà câblée et testée) — couvre ce qui
  est spécifique au payant : le BAB (budget) et le BAP d'un créatif publicitaire DÉDIÉ (campagne
  autonome avec visuel/texte propre à la pub, distinct d'un boost qui réutilise le BAP organique
  déjà existant). Écrit une preuve dans meta-ads/validation/BAB_budget/ ou
  meta-ads/validation/BAP_contenu/ selon le cas, et déplace un visuel vers visuels/approuves/
  UNIQUEMENT sur correspondance exacte de hash SHA-256 — jamais sur jugement esthétique. Ne
  renseigne jamais scenario_retenu, montant_mensuel_fcfa ou autorisation_ecrite_ref — un humain
  lit l'email et transcrit le montant, toujours.
---

# VÉRIFICATION DES VALIDATIONS GMAIL — AORA × Excellence+

## 1 · Rôle, et pourquoi son périmètre est celui-ci et pas un autre

Un circuit de validation par email existe déjà dans ce dépôt pour l'organique : BAT/BAP,
détectés et traités à l'étape 2 de `routine1_programmation.md` → `scripts/traiter_bap.py`. Ce
circuit fonctionne, est testé, et **tu ne le remplaces pas** — le dupliquer ici créerait deux
détecteurs de la même chose, et l'un finirait par diverger de l'autre.

Ce skill couvre ce qui est spécifique au payant, en deux circuits distincts qui ne se confondent
jamais :

**BAB** (Bon À Budgétiser) — l'autorisation écrite du scénario et du montant Meta Ads
(`meta-ads/config/meta_ads_budgets.json`), gardée par la porte 2 de `verifier_activation.py`.
N'existait pas avant le 05/08/2026.

**BAP créatif publicitaire** — l'approbation d'un créatif conçu spécifiquement pour la publicité
(campagne autonome, chemin b : carrousel dédié, vidéo tournée pour la pub, copy différente de
l'organique), gardée par la porte 3 de `verifier_activation.py` pour ce chemin précis. **Ne
couvre PAS le boost** d'un post déjà publié organiquement — un boost réutilise le BAP organique
déjà présent sur le post (`post_organique_boostable()` le vérifie directement sur le post,
`bap_recu_le`/`bap_email_ref` inclus), et ne déclenche donc aucun aller-retour email
supplémentaire pour le simple fait de mettre un budget derrière un contenu déjà approuvé.

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

## 3a · Ce que tu cherches — BAB (budget)

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

## 3b · Ce que tu cherches — BAP créatif publicitaire (campagne autonome uniquement)

Formule attendue : **la même que le BAP organique**, `config/validation_formules.json →
bap.formules_recevables` (« Je valide ce contenu pour publication. »). Il n'existe pas de formule
distincte pour un créatif publicitaire — même exigence, même fichier, même comparaison en
minuscules et sans accents.

Recherche Gmail : fils dont l'objet ou le corps identifie un `creatif_ref` de campagne autonome
(présent dans un brief sous `meta-ads/campagnes/en_preparation/`, jamais un boost — voir §1).
Les quatre conditions cumulatives, identiques à celles du BAP organique :

1. **Expéditeur** — adresse exactement dans `config/comptes.json → client.emails_autorises`.
2. **Formule** — le corps contient la formule exacte ci-dessus.
3. **Créatif identifié** — un ou plusieurs `creatif_ref` cités dans l'objet ou le corps, ou le
   fil rattaché sans ambiguïté à un seul brief de `en_preparation/`.
4. **Aucune réserve** — mêmes mots disqualifiants que partout ailleurs dans le dispositif.

Les quatre réunies → approbation recevable, passe à l'archivage (§4). Une seule manquante →
n'archive rien, signale l'email comme ambigu avec la condition précise qui manque.

### Promotion du visuel — uniquement sur correspondance de hash, jamais sur jugement

Pour chaque `creatif_ref` dont l'approbation vient d'être archivée : calcule le SHA-256 du visuel
candidat (`visuels/bat_soumis/` ou `visuels/en_production/`, ou le `visuel_ref` cité dans le
brief) et compare-le au hash enregistré au moment du BAT, ou référencé dans le brief.

```bash
sha256sum <chemin_du_visuel_candidat>
```

**Correspondance exacte** → déplace vers `visuels/approuves/` (le geste qui *est* la validation
du visuel côté organique s'applique identiquement ici — `meta-ads/README.md` : « le dossier de
référence reste `visuels/approuves/`, en créer un second dupliquerait la source de vérité »).
**Pas de correspondance, ou visuel introuvable** : ne déplace rien, signale-le — un hash qui ne
correspond pas veut dire qu'un fichier a changé depuis le BAT, jamais une décision à trancher à
l'œil.

Si un visuel correspondant est déjà dans `approuves/` (parce que le pipeline organique l'a promu
en premier — un même visuel peut servir à l'organique et à une déclinaison publicitaire) : dis-le,
ne fais rien de plus, ne déplace rien une seconde fois.

---

## 4a · Ce que tu écris pour une BAB, et ce que tu n'écris jamais

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

## 4b · Ce que tu écris pour un BAP créatif publicitaire

**Approbation recevable** (§3b) → écris un fichier dans `meta-ads/validation/BAP_contenu/`, nommé
`<creatif_ref>_BAP.md`, au format que `construire_campagne.py` (porte 3, chemin campagne autonome)
sait déjà lire :

```yaml
---
creatif_ref: <creatif_ref>
bap_recu_le: AAAA-MM-JJ
bap_email_ref: <id du message Gmail>
objet: "<objet exact du fil>"
formule_relevee: "Je valide ce contenu pour publication."
transcrit_par: verifier-validations-gmail-aora
transcrit_le: AAAA-MM-JJTHH:MM:SSZ
---

<corps exact de la réponse, copié tel quel>
```

Puis la promotion du visuel par hash (§3b) — les deux gestes vont ensemble, comme côté organique
où `traiter_bap.py` archive la preuve ET déplace le visuel dans le même passage.

**Tu n'écris JAMAIS directement dans un brief de campagne** (`meta-ads/campagnes/en_preparation/*.md`)
— ni `bap_recu_le`, ni `bap_email_ref`, ni aucun champ. La fiche que tu écris dans
`BAP_contenu/` est la preuve ; c'est `verifier_activation.py` (porte 3) qui la rapproche du brief
au moment de la vérification, jamais toi en modifiant le brief à la main.

**Ambiguïté** → même règle que partout dans ce skill : n'écris rien, signale la raison précise.

---

## 5 · Ce que tu ne fais jamais

1. Traiter « Bien reçu », « Ok merci », « C'est noté » ou toute formule d'accueil comme une
   validation — voir §2.
2. Écrire un champ de `meta_ads_budgets.json` — voir §4a, aucune exception.
3. Déplacer un visuel vers `visuels/approuves/` sans correspondance exacte de hash SHA-256 —
   voir §3b, jamais sur jugement esthétique, jamais « ça ressemble à ce qui était prévu ».
4. Écrire un champ directement dans un brief de campagne (`en_preparation/*.md`) — voir §4b,
   la fiche `BAP_contenu/` est la preuve, jamais le brief lui-même.
5. Assouplir une formule de `validation_formules.json` parce qu'une réponse « veut clairement
   dire » qu'elle valide.
6. Traiter une réponse BAT/BAP organique comme si c'était une BAB ou un BAP créatif publicitaire,
   ou l'inverse — trois circuits, trois usages, jamais interchangeables même quand deux d'entre
   eux partagent la même formule (BAP organique et BAP créatif publicitaire, voir §3b).
7. Envoyer un email au client, ou en rédiger un brouillon à sa place sans qu'on te le demande.
8. Confondre un boost avec une campagne autonome — un boost ne passe jamais par ce skill pour
   son créatif, voir §1.

---

## 6 · Fichiers de référence

| Fichier | Contenu |
|---|---|
| `config/validation_formules.json` | Formules BAT/BAP/BAB exactes — fait foi |
| `config/comptes.json` | Adresse client autorisée, adresse d'envoi AORA |
| `meta-ads/config/meta_ads_budgets.json` | Où la BAB confirmée doit être transcrite — par un humain |
| `meta-ads/validation/BAP_contenu/` | Où la preuve BAP créatif publicitaire est archivée — §4b |
| `meta-ads/scripts/verifier_activation.py` | `post_organique_boostable()` — pourquoi un boost ne repasse jamais par ce skill |
| `routines/routine1_programmation.md` | Circuit BAT/BAP organique existant, ne pas dupliquer |

---

*ACADÉMIE AORA · MA-EXC-001 · v1.1 — 06/08/2026 — BAP créatif publicitaire ajouté · Contrat AORA-CCC-005*
