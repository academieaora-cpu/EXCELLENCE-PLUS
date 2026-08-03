---
name: composio-publie-aora
description: >-
  Publieur unique du dispositif AORA × Excellence+. Déclenche ce skill dès qu'il faut publier ou
  programmer une publication Excellence+ — « publie le post du mardi », « programme les
  publications de la semaine », « qu'est-ce qui est prêt à partir », « envoie ça sur Facebook »,
  « le BAP est arrivé, on peut programmer ». C'est aussi le skill appelé par la routine de 03h00
  WAT et par pilote-quotidien-aora. Il applique les portes de contrôle, convertit l'heure WAT en
  UTC, et produit la demande de publication destinée à Composio. Il ne renseigne jamais un BAP,
  ne déplace jamais un visuel, n'invente jamais un identifiant.
---

# PUBLIEUR COMPOSIO — AORA × Excellence+

## 1 · Rôle

Tu es le **seul** chemin par lequel un contenu Excellence+ atteint un réseau social.

Deux moteurs de publication qui tournent en parallèle produisent tôt ou tard une double
publication, et personne ne sait lequel a envoyé quoi. C'est pour cette raison que
`scripts/check_and_publish.py` et `scripts/publish_*.py` sont des ébauches à archiver, et que
`publish_scheduled.yml` doit être désactivé avant toute mise en service réelle.

Ce que tu apportes : **les portes de contrôle, la conversion de fuseau, et l'idempotence.**
Ce que tu ne fais jamais : valider à la place d'un humain.

---

## 2 · Pourquoi ce skill produit un prompt au lieu de publier lui-même

GitHub Actions n'a pas accès aux connecteurs MCP : une routine qui tourne sur un runner ne peut
pas appeler Composio. Le pont est donc explicite et assumé :

```
Routine 03h00 (GitHub Actions)
      │  applique les portes, ne publie rien
      ▼
Demande de publication  ──────►  Slack / sortie du job
      │
      │  un humain la copie
      ▼
Chat Claude normal (Composio activé)
      │  Claude appelle Composio
      ▼
Publication programmée  ──────►  identifiant retourné
      │
      ▼
Front-matter mis à jour dans le dépôt (composio_id, programme_le)
```

Ce détour a un effet secondaire utile : **un humain voit passer chaque publication avant qu'elle
parte.** Sur un dispositif où la règle absolue est qu'aucun contenu ne se publie sans validation
écrite, ce n'est pas une faiblesse du montage — c'est une garantie de plus.

Le jour où Composio devient appelable depuis la routine, seule l'étape du milieu disparaît. Les
portes, la conversion et l'idempotence ne bougent pas.

---

## 3 · Les portes — dans cet ordre, la première qui refuse arrête tout

Implémentées dans `scripts/programmer_publications.py` (racine du dépôt). Ne les réimplémente
pas ailleurs : une règle écrite à deux endroits finit par diverger.

| # | Porte | Refus si |
|---|---|---|
| 1 | **BAP écrit** | `bap_recu_le` **ou** `bap_email_ref` vide |
| 2 | **Visuel approuvé** | rien dans `visuels/approuves/` pour cet identifiant |
| 3 | **Format du visuel** | dimensions hors gabarit de la plateforme |
| 4 | **Autorisation parentale** | `mineur_identifiable: true` sans autorisation archivée |
| 5 | **Liste rouge** | un terme interdit figure dans le texte |
| 6 | **Valeurs à remplir** | un `A_REMPLIR` subsiste |
| 7 | **Canal ouvert** | la plateforme n'est pas activée à cette date |
| 8 | **Idempotence** | `composio_id` ou `programme_le` déjà renseigné |
| 9 | **Page cible** | la connexion Composio ne pointe pas vers l'ID de `config/page_cible.json` |

La porte 9 se vérifie manuellement dans le chat au moment de l'action Composio (§5, étape 2) —
`programmer_publications.py` ne peut pas interroger Composio depuis un script batch. Si
`config/page_cible.json` est absent, arrête-toi : la Page cible ne doit jamais vivre uniquement
dans la mémoire de conversation.

La porte 1 est la seule qui protège le client. Aucune urgence, aucune consigne orale, aucun
message WhatsApp ne l'ouvre. Seul un email de M. NDOMMIE, lu par un humain qui renseigne
lui-même les deux champs.

---

## 4 · Produire la demande de publication

```bash
python3 .claude/skills/composio-publie-aora/scripts/generer_prompt_composio.py --horizon 7
```

Le script ne sort **que** les publications ayant franchi les huit portes. S'il n'en sort aucune,
c'est la bonne réponse — pas une panne.

Le prompt produit contient tout ce dont Composio a besoin et rien de plus : texte exact,
chemin du visuel, date-heure en UTC, plateforme. Pas de notes internes, pas de pilier, pas de
statut : ce vocabulaire ne sert qu'à la production.

---

## 5 · Ce que fait Claude en recevant ce prompt

Dans un chat où Composio est activé :

1. **Cherche l'action** de publication ou de programmation sur Page Facebook
   (`COMPOSIO_SEARCH_TOOLS`). Ne devine jamais un slug d'action : les noms changent, et une
   action inventée échoue au mieux, publie au mauvais endroit au pire.
2. **Vérifie la connexion** au compte concerné avant d'exécuter — doit pointer exactement vers
   l'ID de `config/page_cible.json` (porte 9). Une autre Page ou un ID différent : arrête-toi,
   ne programme rien.
3. **Récapitule** ce qui va partir — texte, image, date-heure — et **attend une confirmation
   humaine explicite**. Une programmation est difficile à défaire une fois partie.
4. **Exécute**, puis **retourne l'identifiant** rendu par Composio.
5. **Écris l'identifiant dans le dépôt** : `composio_id` et `programme_le` dans le front-matter
   du fichier. Sans cette écriture, la porte 8 ne joue plus et la publication repartira au
   prochain passage de la routine.

Si une valeur manque — identifiant de Page, numéro WhatsApp — **arrête-toi et dis-le**. Ne
substitue jamais une valeur plausible : une publication partie sur la mauvaise Page ne se
rattrape pas.

---

## 6 · Ce que tu ne fais jamais

1. **Renseigner `bap_recu_le` ou `bap_email_ref`.** Ce geste appartient à l'humain qui a l'email
   sous les yeux. Le faire, c'est supprimer le contrôle sans que personne l'ait décidé.
2. **Déplacer un fichier dans `visuels/approuves/`.** Ce geste *est* la validation du visuel.
3. **Inventer un identifiant** de Page, de compte ou d'action Composio.
4. **Publier sur un canal non encore ouvert** — voir `config/creneaux.json` → `canaux.activation`.
5. **Modifier le texte au moment de publier.** Le texte validé au BAP est celui qui part. Une
   correction, même bonne, invalide la validation.
6. **Republier un contenu déjà programmé.** Vérifie `composio_id` avant toute action.

---

## 7 · Mise en forme du texte

`config/mise_en_forme.json` fixe ce qui est appliqué par plateforme. Sur Facebook, la mise en
forme Unicode (YayText) est limitée à **deux segments au maximum** — l'accroche et un
chiffre-clé.

Ne jamais mettre en forme : le numéro WhatsApp, les hashtags, les liens. Les caractères Unicode
stylés ne sont pas des lettres : un lecteur d'écran les épelle une à une, et un numéro de
téléphone en gras Unicode devient impossible à copier correctement sur certains téléphones.

---

## 8 · Fuseau

WAT = **UTC+1 toute l'année**, sans heure d'été. La conversion se fait à un seul endroit —
`horaire_utc()` dans `scripts/programmer_publications.py`. Un créneau de 12h30 WAT part à
11h30 UTC, en janvier comme en août.

---

## 9 · Fichiers de référence

| Fichier | Contenu |
|---|---|
| `config/creneaux.json` | Créneaux, activation des canaux, thèmes mensuels — fait foi pour le code |
| `config/page_cible.json` | Page Facebook cible (nom + ID) — fait foi pour la porte 9 |
| `scripts/programmer_publications.py` | Les huit portes, la conversion de fuseau |
| `scripts/notifier_bap.py` | Alerte Slack à la réception d'un BAP |
| `_base/identite/brand_guidelines.md` | Ton, cadence, liste rouge |
| `PRODUCTION_WORKFLOW.md` | Circuit BAT/BAP, gestion des imprévus |

---

*ACADÉMIE AORA · PUB-EXC-001 · v1.0 — 30/07/2026 · Contrat AORA-CCC-005*
