# `.claude/skills/` — miroir partiel du Projet Claude.ai « Excellence Plus »

**Ce dossier n'est pas synchronisé automatiquement.** Chaque skill ici est une copie ponctuelle
d'un skill qui vit, en original, dans le Projet Claude.ai « Excellence Plus »
(`/mnt/skills/user/<nom>/` côté claude.ai). Si l'un des deux évolue sans que l'autre soit reporté
à la main, ils divergent silencieusement — sans erreur, sans avertissement.

**Ce n'est pas théorique : c'est déjà arrivé.** En vérifiant avant d'ajouter les 4 skills
ci-dessous (18/08/2026), la copie repo de `superviseur-publication-aora/SKILL.md` s'est révélée
**plus à jour** que la copie claude.ai sur deux points — vérifiés directement contre l'état réel
du dépôt, pas juste comparés entre eux :

| Point | Copie claude.ai (avant correction) | Copie repo (vérifiée exacte) |
|---|---|---|
| `publish_scheduled.yml` | Traité comme actif, à re-signaler à chaque audit | Résolu le 03/08/2026 — fichier absent, scripts dans `scripts/archive/` (confirmé) |
| Formules BAP | Traité comme désaligné avec `validation_formules.json` | Résolu le 12/08/2026 — les deux formulations sont recevables (confirmé dans le fichier) |

Sens inverse aussi observé : la copie claude.ai portait une précision absente de la copie repo
(origine du numéro 679 941 300 sur le flyer validé par M. NDOMMIE) — donc la dérive ne va pas
system­atiquement dans un seul sens. Les deux corrections ci-dessus ont été reportées dans la
copie claude.ai le 18/08/2026 ; la précision manquante n'a pas été ajoutée ici, pour ne pas
mélanger cette correction avec l'ajout des 4 skills qui est l'objet de ce commit.

**Conséquence pratique** : avant de faire confiance à une affirmation d'un skill de ce dossier sur
un point sensible (formule de validation, page cible, statut d'un workflow), vérifier l'état réel
du dépôt plutôt que le texte du skill seul — exactement la règle « le dépôt est la seule source de
vérité » que ces skills appliquent eux-mêmes au reste du projet.

---

## Skills présents ici

| Skill | Origine | Rôle |
|---|---|---|
| `composio-publie-aora` | déjà présent, non touché ce jour | Seul point qui publie effectivement (Composio) |
| `superviseur-publication-aora` | déjà présent, non touché ce jour | Audit a posteriori des publications |
| `community-manager-aora` | ajouté 18/08/2026 | M1→M7, cœur éditorial — M4 = rédaction |
| `redaction-hebdo-excellence-plus` | ajouté 18/08/2026 | Rédaction hebdomadaire (mercredi), délègue à M4 |
| `contenu-visuel-excellence-plus` | ajouté 18/08/2026 | Texte + statut visuel d'un post, à la demande |
| `pilote-quotidien-aora` | ajouté 18/08/2026 | Pilote quotidien — publie, rédige le manquant, briefs visuels |

Les 4 skills ajoutés le 18/08/2026 incluent la convention de mise en forme Unicode (YayText)
adoptée le même jour pour les légendes Facebook — voir
`redaction-hebdo-excellence-plus/references/mise-en-forme-yaytext.md`.

## Skills qui existent côté claude.ai mais PAS ici

`direction-artistique-excellence-plus`, `meta-ads-publie-aora`, `pilote-metaads-aora`,
`calendrier-editorial-aora`, `expert-brief-aora`, `gestion-client-aora`, `identite-aora`,
`redaction-brief-aora`, `canva`, `expert-prompt-canva`, `brief-formation-aora`, et
`synchro-depot-aora` (mentionné dans les notes de session mais absent du Projet claude.ai
au 18/08/2026 — à vérifier si son contenu existe ailleurs avant de le considérer perdu).

Ne pas supposer qu'un de ces skills existe ici sous un autre nom : s'il faut sa logique dans une
session Claude Code, le porter explicitement plutôt que de la reconstruire de mémoire.

---

*ACADÉMIE AORA · miroir `.claude/skills/` · 18/08/2026 · Contrat AORA-CCC-005*
