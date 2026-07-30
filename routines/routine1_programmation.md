# ROUTINE 1 — Programmation des publications

> **C'est la routine centrale.** C'est elle qui programme réellement chez Composio.
> Les deux autres l'alimentent.

## Paramétrage

```
Nom       : Excellence+ — Programmation quotidienne
Cadence   : Chaque jour
Heure     : 03h00 WAT  (02h00 UTC)
Dépôt     : academieaora-cpu/EXCELLENCE-PLUS · branche main
Type      : Routine distante (tourne même ordinateur éteint)
Connecteurs requis : Composio · Slack · Gmail (lecture seule)
```

**Pourquoi 03h00** — la programmation doit être faite avant le premier créneau du jour
(mardi 12h30 WAT). À 03h00 la veille est close, personne ne modifie le dépôt, et le rapport
attend l'équipe à son arrivée.

**Pourquoi quotidienne et pas au push** — une routine Claude se déclenche à l'heure, pas sur un
événement Git. Avec deux semaines d'avance de production (l'objectif du dispositif), un passage
par jour suffit largement : un visuel déposé lundi est programmé mardi 03h00, bien avant le
créneau de 12h30. Si vous constatez des validations le jour même de façon régulière, ajoutez un
second passage à 09h00 — mais traitez d'abord la cause, pas le symptôme.

---

## Le prompt

```
Exécute la programmation quotidienne Excellence+.

Dépôt : academieaora-cpu/EXCELLENCE-PLUS, branche main.
Skill : composio-publie-aora — suis-le intégralement à partir de l'étape 4.

ÉTAPE 0 — ARRÊT ÉVENTUEL
Si le fichier PAUSE existe à la racine : affiche son motif, ne fais rien d'autre,
termine. Un planning en pause l'est par décision de l'équipe.

ÉTAPE 1 — ÉTAT INITIAL
Lance : python3 scripts/programmer_publications.py --horizon 7
Ce script applique les huit portes. Ne réimplémente aucune de ses règles :
une règle écrite à deux endroits finit par diverger. Ce résultat sert de
référence "avant" pour le rapport final — l'étape 3 le refera "après".

ÉTAPE 2 — TRAITEMENT DES BAP
C'est ici, et seulement ici, que le dépôt enregistre une validation client.
scripts/traiter_bap.py est le point d'entrée UNIQUE, quel que soit le chemin
d'origine : un fichier déposé à la main par Laurence dans validation/BAP/, ou
un fichier que TU écris toi-même après lecture de Gmail (sous-étape a). Dans
les deux cas c'est le script — jamais toi directement — qui contrôle et
enregistre.

  a. LECTURE GMAIL (compte academieaora@gmail.com)
     Cherche les réponses de M. NDOMMIE à un email BAT (objet commençant par
     "BAT — publications Excellence+") contenant la formule exacte attendue :
     « Je valide ce contenu pour publication. »
     Pour chaque email de validation trouvé :
       1. Identifie, dans le corps du BAT auquel il répond, la ou les dates de
          publication couvertes par le lot.
       2. Pour chaque date, vérifie dans le dépôt s'il existe une publication
          BAT_soumis dont bap_recu_le est encore vide pour cette date.
       3. Si la correspondance est CLAIRE et SANS AMBIGUÏTÉ (une date de
          l'email = une publication en attente, pas plus) : écris un fichier
          dans validation/BAP/, nommé
          gmail-<8 premiers caractères de l'ID du message>_JJ_MM_AAAA_HHhMM
          (JJ_MM_AAAA = la date de publication validée, HHhMM = heure de
          réception de l'email). N'écris RIEN d'autre — pas de front-matter,
          pas de bap_recu_le : ça, c'est le travail du script, à la sous-étape b.
       4. Si ce n'est PAS clair (email qui ne cite aucune date reconnaissable,
          lot déjà entièrement traité, publication introuvable) : n'écris
          AUCUN fichier. Signale l'email comme action humaine à l'étape 5.
          Deviner ici reviendrait à publier sur la foi d'une supposition.
     ⚠️ Tu n'écris JAMAIS toi-même bap_recu_le ou bap_email_ref, et tu ne
     déplaces JAMAIS toi-même un visuel vers approuves/ — même après avoir lu
     l'email de validation de tes propres yeux. Seul le fichier que tu déposes
     dans validation/BAP/ vaut preuve ; seul scripts/traiter_bap.py a le droit
     d'agir sur cette preuve.

  b. TRAITEMENT
     Lance : python3 scripts/traiter_bap.py
     Ce script reprend tous les fichiers présents dans validation/BAP/ — ceux
     que tu viens d'écrire ET tout dépôt manuel de Laurence depuis le dernier
     passage — recontrôle liste rouge et A_REMPLIR, enregistre bap_recu_le /
     bap_email_ref / statut, déplace le visuel correspondant vers approuves/
     s'il le trouve dans visuels/en_production/, et archive le fichier BAP
     traité. S'il signale un fichier non traité (nom hors convention, aucune
     ou plusieurs publications correspondantes, terme interdit) : reporte-le
     tel quel à l'étape 5, ne tranche pas à sa place.

  c. ALERTE SLACK DÉDIÉE
     Pour CHAQUE publication où traiter_bap.py rapporte un visuel déplacé vers
     approuves/, envoie immédiatement un message Slack séparé du rapport de
     fin de routine :
       « 🔓 Visuel déplacé automatiquement vers approuves/ — <id> — BAP :
       <nom du fichier archivé> — source : <Gmail | dépôt manuel> »
     Ce geste change d'état un visuel sans qu'un humain l'ait fait à la main :
     il mérite sa propre ligne, pas une mention noyée dans le rapport global.

ÉTAPE 3 — ÉTAT APRÈS TRAITEMENT
Relance : python3 scripts/programmer_publications.py --horizon 7
De nouvelles publications peuvent être passées PRÊTES depuis l'étape 1 —
c'est cette liste, pas celle de l'étape 1, qui gouverne l'étape 4.

ÉTAPE 4 — PROGRAMMATION CHEZ COMPOSIO
Pour chaque publication déclarée PRÊTE à l'étape 3, et uniquement celles-là :
  a. Cherche l'action Composio de programmation sur Page Facebook
     (COMPOSIO_SEARCH_TOOLS). Ne devine jamais un slug d'action.
  b. Vérifie que la connexion au compte Facebook Excellence+ est active.
  c. Applique la mise en forme selon config/mise_en_forme.json :
     2 segments Unicode maximum (accroche + chiffre-clé), jamais sur le numéro
     WhatsApp, les hashtags ni les liens.
  d. Récapitule dans Slack ce qui va partir, puis programme.
  e. Récupère l'identifiant retourné par Composio.

ÉTAPE 5 — ÉCRITURE EN RETOUR
Écris dans le front-matter de chaque fichier programmé à l'étape 4 :
  composio_id   : l'identifiant retourné
  programme_le  : la date-heure de programmation
Ne touche pas au champ statut : il reste BAP_recu jusqu'à la publication
réelle — SOP-001 ne connaît pas d'état intermédiaire "programmé". C'est la
présence de composio_id/programme_le qui fait foi pour la porte
d'idempotence (cf. scripts/programmer_publications.py, fonction qui renvoie
DEJA_PROGRAMME).
Un seul commit pour l'étape 2 ("bap: N validation(s) enregistrée(s) —
AAAA-MM-JJ") et un seul commit pour l'étape 5 ("programmation: N
publication(s) — AAAA-MM-JJ"). Sans cette écriture, la porte d'idempotence ne
joue plus et la même publication repartirait demain.

ÉTAPE 6 — RAPPORT SLACK
Canal #excellence-plus. Format court :
  · BAP enregistrés à l'étape 2 (source Gmail ou dépôt manuel) et visuels
    déplacés — même s'ils ont déjà été annoncés à l'étape 2c, un rappel groupé
    ici aide la relecture du matin
  · fichiers de validation/BAP/ non traités, et pourquoi
  · ce qui a été programmé (identifiant, date, heure WAT)
  · ce qui est bloqué et pourquoi
  · UNE seule action humaine, la plus bloquante, avec sa conséquence chiffrée

CE QUE TU NE FAIS JAMAIS
· Écrire bap_recu_le ou bap_email_ref toi-même, en dehors d'un appel à
  scripts/traiter_bap.py — jamais à la main, jamais par une autre voie
· Déplacer un fichier dans visuels/approuves/ toi-même — seul
  scripts/traiter_bap.py en a le droit, et seulement sur la base d'un fichier
  BAP vérifié dans validation/BAP/
· Écrire un fichier dans validation/BAP/ sur une correspondance douteuse —
  aucune date reconnaissable, lot déjà soldé, publication introuvable
· Modifier le texte d'un post validé : le texte du BAP est celui qui part
· Inventer un identifiant de Page, de compte ou d'action Composio
· Publier immédiatement : ce sont des publications PROGRAMMÉES
· Republier un contenu portant déjà un composio_id
· Envoyer un email au client

Si une valeur manque (identifiant de Page, numéro WhatsApp), arrête-toi et
dis-le dans le rapport. Une publication partie sur la mauvaise Page ne se
rattrape pas.
```

---

## Avant la première exécution

Faites-la tourner **une fois à la main** avant de la planifier. Une routine programmée sans
l'avoir vue tourner produit sa première surprise à 3h du matin, un jour où personne ne regarde.

Au premier passage, demandez-lui de s'arrêter après l'étape 1 et de vous montrer ce qu'elle
*aurait* programmé. Vous verrez le nom exact de l'action Composio retenue — communiquez-le moi,
je le figerai dans le skill pour que les passages suivants soient plus rapides et plus sûrs.

**Spécifiquement pour l'étape 2 (Gmail → validation/BAP/ → traiter_bap.py)** : la première fois
qu'un email de validation produit un déplacement réel vers `approuves/`, vérifiez le résultat à
la main avant de faire confiance aux passages suivants sans surveillance — lisez le fichier BAP
archivé dans `validation/BAP/traites/`, le front-matter mis à jour, et le visuel effectivement
présent dans `approuves/`. C'est le seul geste de cette routine qui change un état considéré
jusqu'ici comme exclusivement humain ; il mérite d'être vu tourner une fois, en clair, avant
d'être laissé sans supervision.
