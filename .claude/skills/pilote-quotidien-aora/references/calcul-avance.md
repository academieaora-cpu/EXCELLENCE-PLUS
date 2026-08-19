# AVANCE, QUOTA, GOULOT — comment on calcule

## L'avance

**Définition** : le nombre de jours entre aujourd'hui et le dernier créneau **consécutivement**
couvert.

Un créneau est couvert s'il est `PUBLIE`, `PROGRAMME` ou `PRET`. Un créneau `TEXTE_SEUL` ou `VIDE`
casse la chaîne, et l'avance s'arrête là.

**Pourquoi la consécutivité compte**

```
Lun 03  🟢 prêt
Mer 05  🟢 prêt
Ven 07  🟡 texte seul     ← la chaîne casse ici
Dim 09  🟢 prêt
Lun 10  🟢 prêt

Avance = 4 jours (jusqu'au 05), pas 11.
```

Compter jusqu'au 10 donnerait une avance de 11 jours et un sentiment de sécurité faux : le vendredi
07 serait une page vide, visible par tous les abonnés. On ne compte que ce qui protège vraiment.

**Un `TEXTE_SEUL` ne compte pas comme couvert.** Le texte est écrit, mais sans visuel il ne partira
pas. Il représente du travail fait, pas un créneau sécurisé. Il apparaît dans le goulot, pas dans
l'avance.

---

## Le quota du jour

| Avance | Phase | Quota | Logique |
|---|---|---|---|
| < 7 jours | **RATTRAPAGE** | 3 posts | On produit plus qu'on ne consomme |
| 7 à 11 jours | **CONSOLIDATION** | 2 posts | On gagne encore du terrain |
| 12 à 13 jours | **CONSOLIDATION** | 1 post | On approche, on ralentit |
| ≥ 14 jours | **MAINTIEN** | 1 post | On remplace ce qui part |

**La mécanique de la montée en charge**

Consommation en août : 5 créneaux Facebook par semaine.
Production en rattrapage : 3 posts × 5 jours ouvrés = 15 par semaine.
Gain net : **10 créneaux par semaine**, soit environ deux semaines d'avance gagnées par semaine.

Partant de zéro fin juillet, l'objectif de 14 jours est atteignable **avant la mi-août** — sans
journée héroïque, juste par régularité. C'est exactement ce que veut dire « progressif ».

**Pourquoi un plafond à 3**

Au-delà, deux choses cassent. La qualité d'abord : un post écrit en série perd l'ancrage sur un
élève réel, un progrès réel — et c'est précisément ce qui distingue Excellence+. Le stock ensuite :
du contenu produit trop en avance devient du remplissage qu'on republiera sans conviction, ou qu'on
jettera.

Un stock n'a de valeur que s'il est publiable tel quel le jour venu.

---

## Le goulot

**Goulot = nombre de créneaux `TEXTE_SEUL`.**

C'est le nombre de visuels qu'un humain doit monter et déposer dans `approuves/`.

C'est presque toujours le vrai point de blocage du dispositif. Le texte, la machine le produit vite.
Le visuel demande Canva, une photo terrain adaptée, un œil. Un pilote qui optimise la production de
texte sans regarder le goulot fabrique un stock de textes qui ne partiront jamais.

**Règle de lecture du rapport**

```
Goulot 0-2   →  fluide
Goulot 3-5   →  à traiter dans la journée
Goulot 6+    →  le texte prend de l'avance sur le visuel
                 réduire le quota de rédaction et concentrer l'effort sur les visuels
```

Si le goulot dépasse 6 deux jours de suite, signale-le explicitement : produire davantage de texte
n'aide plus, il faut du temps humain sur Canva ou une session de production visuelle groupée.

---

## Cas limites

**Aucun créneau couvert** → avance 0, phase RATTRAPAGE. Normal au démarrage, pas une alerte.

**Un créneau passé resté vide** → c'est un vrai écart de conformité. Il entre au journal mensuel et
apparaît dans le rapport. À distinguer d'un créneau futur non couvert, qui n'est rien du tout
pendant la montée en charge.

**Deux posts sur le même créneau** → doublon. Ne tranche pas : signale et laisse l'équipe décider
lequel garde le créneau.

**Créneau hors grille** (un post à une heure qui n'existe pas dans `config/creneaux.json`) →
signale. Soit le planning a dérivé, soit la config n'a pas été mise à jour après un accord client.

**Changement de mois pendant l'horizon** → les créneaux saisonniers changent (août a un cinquième
créneau Facebook). Le script gère le basculement automatiquement, mois par mois.
