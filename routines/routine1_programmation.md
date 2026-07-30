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
Skill : composio-publie-aora — suis-le intégralement.

ÉTAPE 0 — ARRÊT ÉVENTUEL
Si le fichier PAUSE existe à la racine : affiche son motif, ne fais rien d'autre,
termine. Un planning en pause l'est par décision de l'équipe.

ÉTAPE 1 — ÉTAT DES PUBLICATIONS
Lance : python3 scripts/programmer_publications.py --horizon 7
Ce script applique les huit portes. Ne réimplémente aucune de ses règles :
une règle écrite à deux endroits finit par diverger.

ÉTAPE 2 — BAP ARRIVÉS MAIS NON ENREGISTRÉS
Cherche dans Gmail les emails reçus de M. NDOMMIE contenant une validation
("je valide", "bon à publier", "BAP") depuis 7 jours.
Pour chacun, vérifie si le fichier de contenu correspondant porte déjà
bap_recu_le renseigné.
Si un email de validation existe SANS que le dépôt soit à jour : signale-le
comme action humaine prioritaire.
⚠️ Tu ne renseignes JAMAIS bap_recu_le ni bap_email_ref toi-même, même en ayant
l'email sous les yeux. Ce geste appartient à Laurence ou Stéphane. Le faire,
c'est supprimer le contrôle sans que personne l'ait décidé.

ÉTAPE 3 — PROGRAMMATION CHEZ COMPOSIO
Pour chaque publication déclarée PRÊTE à l'étape 1, et uniquement celles-là :
  a. Cherche l'action Composio de programmation sur Page Facebook
     (COMPOSIO_SEARCH_TOOLS). Ne devine jamais un slug d'action.
  b. Vérifie que la connexion au compte Facebook Excellence+ est active.
  c. Applique la mise en forme selon config/mise_en_forme.json :
     2 segments Unicode maximum (accroche + chiffre-clé), jamais sur le numéro
     WhatsApp, les hashtags ni les liens.
  d. Récapitule dans Slack ce qui va partir, puis programme.
  e. Récupère l'identifiant retourné par Composio.

ÉTAPE 4 — ÉCRITURE EN RETOUR
Écris dans le front-matter de chaque fichier programmé :
  composio_id   : l'identifiant retourné
  programme_le  : la date-heure de programmation
  etat          : PROGRAMME
Un seul commit, message : "programmation: N publication(s) — AAAA-MM-JJ"
Sans cette écriture, la porte d'idempotence ne joue plus et la même publication
repartirait demain.

ÉTAPE 5 — RAPPORT SLACK
Canal #excellence-plus. Format court :
  · ce qui a été programmé (identifiant, date, heure WAT)
  · ce qui est bloqué et pourquoi
  · UNE seule action humaine, la plus bloquante, avec sa conséquence chiffrée

CE QUE TU NE FAIS JAMAIS
· Renseigner bap_recu_le ou bap_email_ref
· Déplacer un fichier dans visuels/approuves/ — ce geste EST la validation
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
