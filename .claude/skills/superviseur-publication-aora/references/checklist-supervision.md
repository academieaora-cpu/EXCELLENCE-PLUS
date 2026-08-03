# Checklist de supervision — version courte

À relire en 30 secondes avant ou après toute exécution de routine touchant la publication.

| # | Contrôle | Fichier de vérité | Écart type |
|---|---|---|---|
| 1 | Page Facebook cible | `config/page_cible.json` | Composio pointe vers une autre Page/ID |
| 2 | Créneaux | `config/creneaux.json` | Post programmé à un jour/heure absent du fichier |
| 3 | Double porte | état réel du dépôt (front-matter + `visuels/approuves/`) | `composio_id` présent sans BAP écrit et/ou sans visuel approuvé |
| 4 | Idempotence | front-matter de tous les posts | même `composio_id` sur deux fichiers |
| 5 | Vocabulaire | front-matter (`statut`, `publie_le`) | rapport dit « publié » sans `publie_le` renseigné |
| 6 | Automatismes concurrents | `.github/workflows/publish_scheduled.yml` | encore actif → jamais une preuve, rappel une fois par audit |
| 7 | Expéditeur autorisé | `config/comptes.json` → `client.emails_autorises` | BAP transcrit d'une adresse absente de la liste |
| 8 | Formule de validation | `config/validation_formules.json` | email demandé/reçu avec « BAP VALIDÉ » au lieu de la formule exacte |
| 9 | Numéros WhatsApp | `config/contacts.json` | numéro France (+33) utilisé comme contact dans un post |

## Dernier état constaté (03/08/2026 — à mettre à jour, pas à recopier tel quel indéfiniment)

- `config/page_cible.json`, `config/comptes.json`, `config/validation_formules.json`,
  `config/contacts.json` : **absents du dépôt au 03/08/2026**, changeset préparé (comptes.json,
  creneaux.json mis à jour, mise_en_forme.json mis à jour, validation_formules.json, page_cible.json,
  contacts.json) mais pas encore poussé sur `main` — aucun accès en écriture au dépôt au moment de
  la préparation. Vérifier à chaque audit si le push a eu lieu.
- `config/creneaux.json` : contenait encore Mardi 12h30/Jeudi 19h00/Samedi 10h00 (version du
  30/07) au 03/08, alors même que le calendrier annoncé au client est déjà Lundi 06h00/Mercredi
  12h00/Samedi 06h00. Le patch corrige ceci, sous réserve du push.
- `publish_scheduled.yml` : actif (cron `*/15 5-21 * * *`), appelle `check_and_publish.py` dont
  l'appel Composio n'est pas implémenté et qui ne vérifie pas la porte visuel. Désactivation
  recommandée par `composio-publie-aora/SKILL.md` §1, pas encore faite au moment de l'écriture.
- `contenu/facebook/EXC-FB-2026-001.md` : `statut: draft`, `date_publication: 2026-08-11` (mardi —
  cohérent avec l'ANCIEN calendrier, pas avec le nouveau) ; `visuel_ref` pointe vers un fichier qui
  n'existe pas dans `visuels/approuves/` (seulement un `.gitkeep`). Ces deux écarts ne sont pas
  encore corrigés.
- `.claude/skills/composio-publie-aora/SKILL.md` : porte 9 (Page cible) et référence à
  `config/page_cible.json` ajoutées le 03/08 — édité localement, pas encore poussé.

Cette section se périme vite — si elle ne correspond plus à ce que `verifier_conformite.py`
rapporte, fais confiance au script, pas à ce tableau.
