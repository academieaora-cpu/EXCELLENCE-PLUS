# ROUTINE 3 — BAT quotidien

> Elle prépare l'envoi du lot au client. C'est le seul point du dispositif qui touche à la
> relation client — et c'est pour cette raison qu'elle **ne peut pas envoyer d'email
> elle-même**.

## Paramétrage

```
Nom       : Excellence+ — BAT quotidien
Cadence   : Chaque jour
Heure     : 07h00 WAT  (06h00 UTC)
Dépôt     : academieaora-cpu/EXCELLENCE-PLUS · branche main
Type      : Routine distante
Connecteurs requis : Gmail (brouillons) · Slack
```

**Pourquoi 07h00** — après R1 (03h00, programmation) et R2 (05h00, production), qui ont pu
compléter le lot du jour avant ce passage.

**Pourquoi quotidienne et pas seulement le mercredi** — passage quotidien décidé pour rester
aligné avec R1 et R2. Le risque de doublon (rédiger un brouillon pour un lot déjà soumis la
veille) est traité à l'étape 1 par l'exclusion des publications dont `statut` est déjà
`BAT_soumis` — sans ce filtre, un passage quotidien redemanderait chaque jour la validation d'un
lot déjà envoyé à Laurence. Si le rythme quotidien s'avère trop dense pour la relecture de
Laurence, revenir à un passage hebdomadaire plutôt que désactiver le filtre.

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
Prépare le BAT quotidien Excellence+.

Dépôt : academieaora-cpu/EXCELLENCE-PLUS, branche main.

ÉTAPE 0 — Si PAUSE existe à la racine : affiche le motif et arrête-toi.

ÉTAPE 1 — CONSTITUER LE LOT
Identifie les publications dont la date de publication tombe dans 7 à 14 jours,
qui ont un texte rédigé, dont bap_recu_le est encore vide, ET dont statut est
encore draft (PAS déjà BAT_soumis — cette exclusion évite de reconstituer
chaque jour un lot déjà soumis à Laurence la veille ou l'avant-veille : c'est
elle, la porte d'idempotence de cette routine, comme composio_id/programme_le
le sont pour R1).
Pour chacune, vérifie :
  · le contrôle liste rouge passe
  · aucune valeur A_REMPLIR ne subsiste
  · un visuel existe (dans approuves/ ou en_production/)
Si une publication échoue à l'un de ces contrôles, ne la mets PAS dans le lot :
signale-la à part. On ne soumet jamais une ébauche au client.
Si aucune publication n'est éligible : dis-le simplement dans le rapport Slack
et arrête-toi là — un jour sans nouveau lot n'est pas une anomalie.

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
passe statut à BAT_soumis (c'est le champ front-matter réel — cf.
contenu/facebook/*.md — pas "etat").
Un seul commit : "bat: lot du [date] — N publication(s)"
Ne touche à AUCUN autre champ. En particulier : jamais bap_recu_le ni
bap_email_ref, qui n'appartiennent qu'à l'humain qui a l'email de validation
sous les yeux.

ÉTAPE 4 — RAPPORT SLACK
Canal #excellence-plus :
  · le brouillon est prêt, N publications, période couverte — ou "aucun
    nouveau lot aujourd'hui" si l'étape 1 n'a rien trouvé
  · les publications écartées du lot et pourquoi
  · les BAT des jours précédents toujours sans réponse, avec leur âge
    (au-delà de 48 h ouvrables, le calendrier se décale d'autant — clause du
    contrat, sans pénalité pour AORA)
  · UNE action humaine : « Laurence — relire et envoyer le brouillon » (si un
    brouillon a été créé aujourd'hui)

CE QUE TU NE FAIS JAMAIS
· Envoyer un email au client. Brouillon uniquement.
· Renseigner bap_recu_le ou bap_email_ref.
· Mettre dans le lot une publication qui échoue à un contrôle.
· Remettre dans un lot une publication déjà à statut BAT_soumis.
· Relancer le client toi-même — la relance est un geste de Laurence.
```

---

## Relances

La routine **signale** les BAT sans réponse ; elle ne relance pas. Le protocole de relance
(24 h puis 48 h, par email) appartient à Laurence — voir `PRODUCTION_WORKFLOW.md` §6.

Une relance automatique envoyée au dirigeant d'une entreprise cliente, sans qu'un humain l'ait
décidée, se retourne contre l'agence bien plus vite qu'elle ne fait gagner du temps.
