# visuels/formats/ — Gabarits par plateforme

Ce dossier contient les gabarits vides (canevas Canva/PSD exportés en PNG) utilisés comme point de départ pour chaque nouveau visuel. Un gabarit porte déjà la bande orange 6px, la zone logo et la grille — il ne reste qu'à intégrer texte et photo.

## Gabarits attendus

| Fichier | Plateforme | Format | Dimensions | Poids max |
|---------|-----------|--------|-----------|-----------|
| `facebook_1080x1080.png` | Facebook post image | Carré | 1080 × 1080 px | 4 MB |
| `facebook_1200x630.png` | Facebook lien | Paysage | 1200 × 630 px | 4 MB |
| `facebook_1640x624.png` | Facebook cover | Bannière | 1640 × 624 px | 4 MB |
| `instagram_1080x1080.png` | Instagram post | Carré | 1080 × 1080 px | 8 MB |
| `instagram_1080x1350.png` | Instagram portrait | Portrait | 1080 × 1350 px | 8 MB |
| `instagram_stories_1080x1920.png` | Stories / Reels | Vertical | 1080 × 1920 px | 4 GB (vidéo) |
| `tiktok_1080x1920.png` | TikTok image/vidéo | Vertical | 1080 × 1920 px | 20 MB |
| `whatsapp_800x800.png` | WhatsApp Channel | Carré | 800 × 800 px | 5 MB |

## Règles de texte communes

- Texte minimum 28pt sur mobile
- Logo Excellence+ toujours présent, coin bas droit, minimum 80px de hauteur
- Bande orange 6px en haut de chaque visuel (signature AORA)
- Safe area Reels/Stories : 100px en haut et en bas (zones masquées par l'UI de l'app)

## Nommage

Un gabarit rempli et exporté quitte ce dossier — il devient un visuel de production et suit le circuit `visuels/en_production/ → bat_soumis/ → approuves/ → publies/`, jamais l'inverse. Ce dossier ne contient que des canevas vides, réutilisables.
