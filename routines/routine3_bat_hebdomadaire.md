# ROUTINE 3 — BAT hebdomadaire

> Elle prépare l'envoi du lot au client. C'est le seul point du dispositif qui touche à la
> relation client — et c'est pour cette raison qu'elle **ne peut pas envoyer d'email
> elle-même**.

## Paramétrage

```
Nom       : Excellence+ — BAT hebdomadaire
Cadence   : Chaque mercredi
Heure     : 09h00 WAT  (08h00 UTC)
Dépôt     : academieaora-cpu/EXCELLENCE-PLUS · branche main
Type      : Routine distante
Connecteurs requis : Gmail (brouillons) · Slack
```

**Pourquoi mercredi** — c'est le jour de la validation interne dans la mécanique hebdomadaire
du dispositif. Le BAT part à J-7 du créneau, ce qui laisse les 48 h ouvrables de retour prévues
au contrat, plus une marge si le client tarde.

**Pourquoi 09h00** — après le pilote de 07h00, qui a pu compléter le lot le matin même.

---

## La règle qui gouverne cette routine

`brand_guidelines.md` §14 : *« Claude ne soumet jamais directement au client, et n'envoie jamais
d'email au client — il rédige au plus un brouillon. »*

Cette routine **crée un brouillon Gmail**. Elle ne l'envoie pas. C'est Laurence qui relit et
envoie — elle est la seule interlocutrice du client.

Ce n'est pas une précaution de façade : un email parti automatiquement au client, avec un
contenu que personne n'a relu, engage l'agence sur un livrable. Le brouillon coûte deux minutes
à Laurence et supprime ce risque entièrement.

---

## Le prompt

```
Prépare le BAT hebdomadaire Excellence+.

Dépôt : academieaora-cpu/EXCELLENCE-PLUS, branche main.

ÉTAPE 0 — Si PAUSE existe à la racine : affiche le motif et arrête-toi.

ÉTAPE 1 — CONSTITUER LE LOT
Identifie les publications dont la date de publication tombe dans 7 à 14 jours,
qui ont un texte rédigé, et dont bap_recu_le est encore vide.
Pour chacune, vérifie :
  · le contrôle liste rouge passe
  · aucune valeur A_REMPLIR ne subsiste
  · un visuel existe (dans approuves/ ou en_production/)
Si une publication échoue à l'un de ces contrôles, ne la mets PAS dans le lot :
signale-la à part. On ne soumet jamais une ébauche au client.

ÉTAPE 2 — RÉDIGER LE BROUILLON GMAIL
Destinataire : M. NDOMMIE GOAP Saturnin (Excellence+)
Objet : "BAT — publications Excellence+ du [date début] au [date fin]"

Corps :
  · une phrase de contexte, ton AORA : direct, exigeant, proche, ambitieux
  · pour chaque publication : date et heure WAT, canal, texte intégral,
    description du visuel
  · le délai de retour attendu : 48 h ouvrables
  · la formulation exacte attendue en retour :
    « Je valide ce contenu pour publication. »
  · le rappel que la validation se fait par email uniquement — un vocal ou un
    message WhatsApp ne vaut pas BAP

⚠️ CRÉE UN BROUILLON. N'ENVOIE RIEN.
Laurence relit et envoie. Elle est la seule interlocutrice du client.

ÉTAPE 3 — TRACER DANS LE DÉPÔT
Pour chaque publication du lot, renseigne bat_soumis_le à la date du jour et
passe etat à BAT_soumis.
Un seul commit : "bat: lot du [date] — N publication(s)"
Ne touche à AUCUN autre champ. En particulier : jamais bap_recu_le ni
bap_email_ref, qui n'appartiennent qu'à l'humain qui a l'email de validation
sous les yeux.

ÉTAPE 4 — RAPPORT SLACK
Canal #excellence-plus :
  · le brouillon est prêt, N publications, période couverte
  · les publications écartées du lot et pourquoi
  · les BAT des semaines précédentes toujours sans réponse, avec leur âge
    (au-delà de 48 h ouvrables, le calendrier se décale d'autant — clause du
    contrat, sans pénalité pour AORA)
  · UNE action humaine : « Laurence — relire et envoyer le brouillon »

CE QUE TU NE FAIS JAMAIS
· Envoyer un email au client. Brouillon uniquement.
· Renseigner bap_recu_le ou bap_email_ref.
· Mettre dans le lot une publication qui échoue à un contrôle.
· Relancer le client toi-même — la relance est un geste de Laurence.
```

---

## Relances

La routine **signale** les BAT sans réponse ; elle ne relance pas. Le protocole de relance
(24 h puis 48 h, par email) appartient à Laurence — voir `PRODUCTION_WORKFLOW.md` §6.

Une relance automatique envoyée au dirigeant d'une entreprise cliente, sans qu'un humain l'ait
décidée, se retourne contre l'agence bien plus vite qu'elle ne fait gagner du temps.
