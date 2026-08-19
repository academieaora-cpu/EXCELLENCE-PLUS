# Format des messages Slack — `#excellence-plus`

Un message par post rédigé. Jamais de récapitulatif unique qui empile plusieurs posts : sur
mobile, un pavé de trois posts est illisible et personne ne réagit dessus.

## Gabarit

```
📋 *[ID]* — [Plateforme] · [jour] [date] · [heure] WAT · Pilier [n] [nom du pilier] · format [format]

[si angle recentré ou dérivé sans entrée calendrier préexistante : une ligne l'expliquant,
 avant le texte]

[si carrousel/multi-slides : la légende d'abord, puis le détail slide par slide]

⚠️ *Statut draft* — BAT non envoyé. [tout point ouvert : visuel absent ou hors circuit,
chiffre écarté faute de source, angle recentré, etc. — sinon omettre la ligne]
```

Le texte du post va toujours dans un bloc de code (```), jamais en citation (`>`) : ça préserve
les sauts de ligne exacts et permet à l'équipe de le copier tel quel.

## Exemple réel — EXC-FB-2026-002, envoyé le 08/08/2026 pour le créneau du 12/08/2026

```
📋 *EXC-FB-2026-002* — Facebook · mercredi 12/08 · 12h00 WAT · Pilier 2 Méthode Excellence+ · format carrousel (nouvellement rédigé — le calendrier marquait `a_rediger`)

*Légende :*
```
Envoyer un enseignant, ce n'est pas assez. On le sait — c'est pour ça qu'on
ne s'arrête pas là.
[...]
#Yaoundé #SoutienScolaire #SuiviTerrain
```

*Slides (brief textuel pour direction-artistique-excellence-plus, Archétype B — 3 temps) :*
1. Accroche — « Envoyer un enseignant ne suffit pas. Voici ce qu'on fait après → »
2. ① Suivi — encadreurs sur le terrain, pas juste un appel
3. ② Vérification — observé vs. prévu pour l'élève
4. ③ Correction — on ajuste méthode/rythme/enseignant, on recommence
5. Clôture — 93 % → 97 % + CTA WhatsApp + logo

⚠️ *Statut draft* — aucun visuel (`visuel_ref: null`), doit d'abord passer par
`direction-artistique-excellence-plus`. Le thème calendrier disait « sélection et suivi des
enseignants » — recentré sur la gestion/suivi documentés dans `brand_guidelines.md` : rien sur
les critères de sélection n'est sourcé par écrit.
```

## Pourquoi un message par post

Un pavé unique de trois posts est illisible sur mobile et personne ne réagit dessus. Un message
par post permet à l'équipe de réagir, de commenter ou de signaler un problème sur UN post précis
sans faire défiler les deux autres. C'est aussi plus facile à retrouver pour
`superviseur-publication-aora`, qui s'active sur les messages Slack de ce canal.

## En cas de blocage

Si une porte se ferme (voir `portes-bloquantes.md`), poste quand même — le message de blocage
tient lieu de post pour ce créneau, l'équipe doit savoir qu'il reste vide :

```
🚩 BLOCAGE — [ID ou date du créneau]
Porte  : [numéro et intitulé, ou « aucune source documentée »]
Motif  : [une phrase, factuelle]
Action : [une seule action humaine, nommément attribuée]
```
