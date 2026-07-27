# AORA × Excellence+ — Pipeline Éditorial Automatisé

Pipeline de publication sociale automatisée pour Excellence+ (Yaoundé, Cameroun).
Géré par ACADÉMIE AORA — Contrat AORA-CCC-005.

## Plateformes

Facebook · Instagram · TikTok · WhatsApp Channel

## Stack

Claude Code · Composio · GitHub Actions

## Structure

- `_base/` → Fichiers de référence (brand, logos, couleurs, templates)
- `contenu/` → Posts rédigés (.md) par plateforme
- `visuels/` → Assets visuels (en production → bat → approuvés → publiés)
- `validation/` → Logs BAT et BAP
- `calendrier/` → Planning éditorial JSON
- `scripts/` → Automatisation Python
- `.github/` → GitHub Actions (publication, rappels, rapports)

## Circuit de validation

`draft → BAT_soumis → BAP_recu → publié → archivé`

## Secrets GitHub requis

`COMPOSIO_API_KEY` · `FB_PAGE_ID` · `FB_ACCESS_TOKEN`
`INSTAGRAM_ACCOUNT_ID` · `TIKTOK_ACCESS_TOKEN`
`WHATSAPP_CHANNEL_ID` · `WHATSAPP_ACCESS_TOKEN` · `SLACK_WEBHOOK_URL`

## Contact

Stéphane (Chef de projet) · Laurence (Account Manager)
