# BAT, BAP, Publication & Reporting — Référence M7

> ⚠️ **Formule de validation — à vérifier par client.** Les gabarits ci-dessous utilisent
> « BAT VALIDÉ » / « BAP VALIDÉ » comme formule par défaut. Pour un client équipé d'un dispositif
> de publication automatisé (ex. Excellence+), la formule exacte attendue peut être différente et
> vit dans la configuration de ce dispositif (`config/validation_formules.json` pour Excellence+),
> pas dans ce document. Vérifier cette source avant d'envoyer un email de validation.

## Distinction fondamentale : BAT ≠ BAP

**BAT** (Bon À Tirer) = validation du **contenu** : texte + visuel brut.
Le client approuve ce qu'on dit et comment on le montre.

**BAP** (Bon À Publier) = validation **finale avant diffusion** : contenu formaté pour la
plateforme, hashtags définitifs, heure exacte, tags, mentions, lien en bio si nécessaire.
Le client approuve la forme opérationnelle de diffusion.

Les deux étapes sont distinctes et séquentielles. On ne passe pas au BAP sans BAT validé.

---

## Séquence complète M7

```
┌──────────────┐
│ PRÉPARATION  │ — Assembler le dossier BAT complet
└──────┬───────┘
       ↓
┌──────────────┐
│  SOUMISSION  │ — Envoyer au client par EMAIL uniquement (jamais oral / WhatsApp vocal)
│     BAT      │
└──────┬───────┘
       ↓
┌────────────────────┐
│ ATTENTE RÉPONSE    │ — Délai max : 48h ouvrables (SOP-001)
└──────┬─────────────┘
       ↓
  [BAT VALIDÉ ?]
  ├── NON → Corrections → Nouveau BAT soumis (max 2 rounds inclus)
  └── OUI
       ↓
┌──────────────┐
│ PRÉPARATION  │ — Finaliser format plateforme, hashtags, heure, liens, tags
│     BAP      │
└──────┬───────┘
       ↓
┌──────────────┐
│  SOUMISSION  │ — Envoyer dossier BAP par email
│     BAP      │
└──────┬───────┘
       ↓
  [BAP VALIDÉ ?]
  ├── NON → Correction format (pas du fond — si fond = nouveau BAT)
  └── OUI
       ↓
┌─────────────┐
│ PUBLICATION │ — Publier ou programmer
└──────┬──────┘
       ↓
┌─────────────┐
│ CONFIRMATION│ — Email de confirmation au client avec lien du post
└─────────────┘
```

---

## Dossier BAT — Contenu

```
BAT #[n] — [Marque] — [Date]

CONTENU
  Plateforme                  : ___
  Format                      : ___
  Date de publication prévue  : ___

TEXTE / CAPTION
  [Texte complet exactement tel que publié — aucune abréviation]

VISUEL
  Lien Canva (preview après commit) : ___
  ou fichier joint                  : ___

HASHTAGS PROPOSÉS
  [Liste complète]

NOTES POUR LE CLIENT
  [Points d'attention, questions en suspens, options proposées]

DEMANDE
  Merci de valider par retour d'email avec la mention « BAT VALIDÉ »
  ou de transmettre vos corrections avant le [date limite 48h].
```

## Dossier BAP — Contenu

```
BAP #[n] — [Marque] — [Date]
(suite du BAT #[n] validé le ___)

FORMAT PLATEFORME
  Dimensions visuelles        : ___ × ___ px (conforme [plateforme])
  Ratio / format Canva        : ___

PARAMÈTRES DE PUBLICATION
  Compte à utiliser           : ___
  Date exacte                 : ___
  Heure exacte                : ___ (fuseau horaire : ___)
  Hashtags définitifs         : [liste finale]
  Comptes à taguer/mentionner : ___
  Lien en bio requis          : Oui → [URL] / Non
  Épingler ce post            : Oui / Non

DEMANDE
  Merci de valider par retour d'email avec la mention « BAP VALIDÉ ».
```

---

## Grille de contrôle qualité avant BAT

**Texte / Caption**
- [ ] Orthographe et grammaire vérifiées
- [ ] Ton conforme au Contexte Client
- [ ] Accroche efficace (ligne 1 retient l'attention)
- [ ] CTA présent, unique, clair
- [ ] Hashtags dans la liste validée, quantité correcte par plateforme
- [ ] Mentions obligatoires présentes (si applicable)
- [ ] Aucun interdit éditorial violé

**Visuel**
- [ ] Charte graphique respectée (palette, typographie, logo)
- [ ] Aucune image générée par IA
- [ ] Sources : Unsplash / Pexels / Pixabay / bibliothèque Canva
- [ ] Logo présent, bonne version
- [ ] Textes lisibles (contraste ≥ 4,5:1 WCAG AA)
- [ ] Format Canva correct pour la plateforme
- [ ] Commit Canva effectué (pas de brouillon)

**Général**
- [ ] Date et heure cohérentes avec le calendrier
- [ ] Post aligné avec le pilier de contenu prévu
- [ ] Aucun placeholder non remplacé

---

## Emails types

### Soumission BAT

```
Objet : BAT #[n] — [Marque] — [Plateforme] — Publication [date]

Bonjour [Prénom],

Veuillez trouver ci-dessous le BAT #[n] pour validation avant publication.

[Insérer dossier BAT]

Pour valider : répondez à cet email avec la mention « BAT VALIDÉ ».
Pour corriger : transmettez vos retours avant le [date + 48h].

Date de publication prévue : [date] à [heure].

Cordialement,
[Signature AORA]
```

### Soumission BAP

```
Objet : BAP #[n] — [Marque] — À publier le [date] à [heure]

Bonjour [Prénom],

Suite à votre validation du BAT #[n], voici le dossier BAP pour validation finale.

[Insérer dossier BAP]

Pour valider : répondez avec la mention « BAP VALIDÉ ».

Cordialement,
[Signature AORA]
```

### Confirmation publication

```
Objet : Publication confirmée — [Marque] — [Plateforme] — [Date]

Bonjour [Prénom],

Le contenu a bien été publié / programmé.

Plateforme  : ___
Date/Heure  : ___
Lien        : [URL du post]

N'hésitez pas à nous signaler tout point d'attention.

Cordialement,
[Signature AORA]
```

### Avenant corrections supplémentaires (round 3+)

```
Objet : Corrections supplémentaires — [Marque] — Avenant

Bonjour [Prénom],

Les 2 rounds de corrections inclus dans notre contrat sont épuisés.
Toute correction supplémentaire est facturée [montant] conformément à l'article [n] de votre
contrat (SOP-001 AORA).

Merci de confirmer votre accord par retour d'email avant que nous procédions.

Cordialement,
[Signature AORA]
```

---

## Gestion des rounds de correction

- **Round 1** : client transmet corrections → on corrige → nouveau BAT soumis
- **Round 2** : si nouvelles corrections → on corrige → BAT final soumis
- **Round 3+** : envoyer l'email d'avenant AVANT de corriger. Ne jamais corriger sans accord écrit.

---

## Reporting

### Rapport hebdomadaire (format léger)

```
RAPPORT HEBDO — [Marque] — Semaine [n] — [Dates]

PUBLICATIONS
  Posts publiés   : ___ / ___ prévus
  Formats         : ___
  Piliers couverts: ___

PERFORMANCES CLÉS
  Portée totale   : ___  /  Impressions    : ___
  Engagements     : ___  /  Taux engagement: ___
  Abonnés gagnés  : ___
  Meilleur post   : [thème] — [métriques]

À VENIR CETTE SEMAINE
  Posts programmés     : ___
  BAT à envoyer        : ___
  Visuels à produire   : ___
```

### Rapport mensuel (format complet)

```
RAPPORT MENSUEL — [Marque] — [Mois]

A. RÉSUMÉ EXÉCUTIF
   [3 lignes max : ce qui s'est passé / ce qui a marché / ce qui suit]

B. PUBLICATIONS
   Total : ___ posts · Prévus : ___ · Taux de réalisation : ___%
   Répartition par plateforme : [tableau]
   Répartition par pilier     : [tableau]

C. PERFORMANCES GLOBALES
   [Tableau KPIs vs objectifs — toutes plateformes]

D. TOP CONTENUS (3 meilleurs posts)
   Post 1 : [visuel / thème / métriques / leçon à retenir]
   Post 2 : [idem]
   Post 3 : [idem]

E. CONTENUS À FAIBLE PERFORMANCE (2–3)
   [Analyse causes + recommandations concrètes]

F. OBSERVATIONS COMMUNAUTÉ & ALGORITHME
   [Ce qu'on apprend des comportements de la communauté]

G. RECOMMANDATIONS MOIS SUIVANT
   [3–5 actions, justifiées par les données, avec responsable et date]

H. APERÇU PLANNING M+1
   [Grandes lignes du calendrier du mois suivant]
```
