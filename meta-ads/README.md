# META ADS — Pipeline de publication payante · Excellence+

**Référence** : MA-EXC-001 · Contrat AORA-CCC-005
**Créé le** : 05 août 2026
**Statut** : construit, **verrouillé** — les quatre portes sont fermées

---

## Ce que ce pipeline fait, et ce qu'il ne fait pas

Il prépare des campagnes Meta Ads (Facebook + Instagram) en dry-run, vérifie des
portes bloquantes, et ne passe à l'exécution réelle que si **toutes** les portes
sont ouvertes — vérifié par script, jamais par déduction humaine ni par mémoire
de conversation.

**Il ne publie et ne dépense jamais de lui-même.** Le cron du workflow ne fait que
vérifier et construire à blanc. Créer une campagne demande un déclenchement manuel
explicite, et reste soumis aux quatre portes.

Miroir de `composio-publie-aora` côté organique : chaque porte qui existe là-bas
existe ici, plus une propre au budget.

---

## Les quatre portes

Dans cet ordre. Aucune ne suffit seule. La première fermée arrête tout.

| # | Porte | Fait foi | Ouverte si |
|---|---|---|---|
| 1 | Activation temporelle | `config/meta_ads_activation.json` | le mois courant a `autorise: true` |
| 2 | Autorisation budgétaire (BAB) | `config/meta_ads_budgets.json` | scénario + plafond + trace écrite archivée |
| 3 | Créatif validé (BAP contenu) | `validation/BAP_contenu/` + `visuels/approuves/` | les deux simultanément |
| 4 | Cohérence du compte cible | `config/meta_ads_comptes.json` | identifiants visés = identifiants de référence |

`scripts/verifier_activation.py` est le **point de vérité unique**. Aucun autre
script ne réimplémente cette logique : ils importent tous
`exiger_portes_ouvertes()`. Une règle écrite à deux endroits finit par diverger,
et ici diverger veut dire dépenser de l'argent non autorisé.

**Porte 2 n'a pas d'équivalent organique.** C'est celle du budget. Le
`montant_mensuel_fcfa` est un **plafond dur** : tout `daily_budget` /
`lifetime_budget` au-delà est rejeté **avant** l'appel API, pas après le refus de
Meta. Le dépassement « temporaire pour tester » n'existe pas.

---

## Deux gestes qui restent humains

1. **`git mv` d'un dossier de campagne** de `campagnes/en_preparation/` vers
   `campagnes/autorisees/`. Aucun agent, aucune routine, aucun script ne
   l'exécute à la place d'un humain — exactement comme côté organique.
2. **Passer un mois à `autorise: true`** dans `meta_ads_activation.json`.

---

## État actuel — ce qui manque et bloque

| Valeur | Fichier | Statut |
|---|---|---|
| `ad_account_id` | `config/meta_ads_comptes.json` | ❌ null — identifiant Meta réel, à obtenir de M. NDOMMIE ou du Business Manager AORA |
| `instagram_actor_id` | `config/meta_ads_comptes.json` | ❌ null — bloque tout placement Instagram |
| `devise_compte` | `config/meta_ads_comptes.json` | ❌ null — facteur ×1 ou ×100 sur le budget réel |
| `scenario_retenu` / `montant_mensuel_fcfa` | `config/meta_ads_budgets.json` | ❌ null — attend la BAB écrite |
| `scenarios_budget_metaads.pdf` | racine du dépôt | ❌ **absent du dépôt** — voir ci-dessous |
| quartiers des 4 zones | `config/meta_ads_ciblage.json` | ❌ non tranchés — conflit Odza / Santa Barbara |
| tranche d'âge | `config/meta_ads_ciblage.json` | ❌ non tranchée — 35-70 vs 30-76 |

**Aucun de ces identifiants n'a été deviné, ni découvert par un appel d'API qui
listerait les comptes accessibles.** Un compte atteignable n'est pas un compte
autorisé — c'est précisément la confusion que la porte 4 existe pour empêcher.

### Le fichier de scénarios budgétaires est absent

`scenarios_budget_metaads.pdf` (ni un équivalent `.md` extrait) n'existe pas dans
le dépôt. C'est pourtant la seule source de vérité sur les montants. Les quatre
scénarios cités dans `meta_ads_budgets.json` (Essentiel 30k / Standard 50k /
Accéléré 75k / Objectif 50 100k FCFA/mois) proviennent de la consigne de
construction, pas d'un document versionné et vérifiable.

Conséquence **codée, pas seulement documentaire** : la porte 2 refuse de s'ouvrir
tant que ce fichier est absent du dépôt, même si `scenario_retenu` et
`montant_mensuel_fcfa` sont renseignés. Un montant sans source opposable n'est pas
un budget autorisé.

---

## Scripts

| Script | Rôle |
|---|---|
| `verifier_activation.py` | Les 4 portes. Point de vérité unique, appelé en tête de tous les autres |
| `construire_campagne.py` | Construit campaign/adset/ad. **Dry-run par défaut**, `--executer` explicite |
| `publier_ads_facebook.py` | Moteur d'exécution réelle : appels API, idempotence, échecs typés |
| `publier_ads_instagram.py` | Importe le moteur ci-dessus, `plateforme="instagram"` — ne le recopie pas |
| `publier_groupe_facebook.py` | **Expérimental**, simulation uniquement — voir ci-dessous |
| `verifier_conformite_ads.py` | Audit des 9 contrôles organiques + 10e : plafond budgétaire. Lecture seule |
| `generer_rapport_ads.py` | État des campagnes, vocabulaire strict |

### Vocabulaire — les quatre mots ne s'échangent pas

- **programmée** : créée dans Meta, diffusion future. Rien n'est dépensé.
- **active** : en diffusion réelle, de l'argent part en ce moment.
- **terminée** : date de fin atteinte ou budget épuisé.
- **en ligne** : employé **uniquement** après confirmation par l'API que le statut
  Meta est `ACTIVE`. Jamais déduit d'un appel de création réussi.

Un appel de création qui réussit prouve que Meta a accepté l'objet, rien de plus.
Les campagnes sont créées en `PAUSED`.

### Idempotence

Triple clé : `(ad_account_id, empreinte du créatif, date-heure de lancement UTC)`,
vérifiée avant tout appel API et enregistrée après succès dans
`campagnes/registre_idempotence.json`. Sans elle, un retry GitHub Actions créerait
une seconde campagne identique — avec un second budget.

### Fuseau

WAT = UTC+1 **toute l'année**, sans heure d'été. La conversion se fait à un seul
endroit : `heure_utc()` dans `construire_campagne.py`. Les runners GitHub Actions
tournent en UTC.

---

## Groupes Facebook — expérimental, désactivé, à ne pas promettre

⚠️ **Ne jamais présenter cette fonctionnalité à M. NDOMMIE comme acquise.**

Depuis 2018, Meta restreint très fortement la publication automatisée dans un
Groupe. La permission `publish_to_groups` n'est quasiment plus accordée à une app
tierce : en pratique, seule une app détenue par un administrateur du groupe,
installée dans ce groupe, et passée en revue Meta peut l'obtenir.

`publier_groupe_facebook.py` **simule** et n'appelle rien. Le drapeau
`EXPERIMENTAL` est en dur dans le script **et** dans `meta_ads_groupes.json` : le
lever suppose d'éditer les deux, volontairement, preuve technique à l'appui (cinq
éléments listés dans le fichier de config). Fallback en attendant : un humain
publie à la main.

Ce circuit est **organique** : il ne dépense rien. Il vit ici parce qu'il partage
la surface d'API Meta, pas parce qu'il consomme du budget.

---

## Workflow et horaires

Le workflow est à **`.github/workflows/publish_scheduled_metaads.yml`**, à la
racine du dépôt — et non dans `meta-ads/.github/workflows/`. GitHub Actions ne lit
les workflows qu'à la racine du dépôt : un fichier placé sous `meta-ads/` ne se
serait jamais déclenché.

C'est la **Routine 4** du dispositif ([`routines/routine4_metaads.md`](../routines/routine4_metaads.md)),
alignée sur les horaires des routines existantes :

| Cron | Heure WAT | Aligné sur |
|---|---|---|
| `0 2 * * *` | 03h00, tous les jours | Routine 1 — `programmation_quotidienne.yml` |
| `0 7 * * 1` | 08h00, lundi | `rapport_hebdo.yml` |

Le périmètre payant se vérifie au moment où le périmètre organique se programme :
une seule lecture du dispositif le matin, pas deux à des heures différentes qu'on
finit par ne plus rapprocher.

**Même horaire que R1, jamais le même fichier.** R1 engage du contenu, R4 engage de
l'argent ; les fondre ferait qu'une erreur de configuration sur l'un exposerait
l'autre. Secrets également distincts (`META_MARKETING_TOKEN`,
`SLACK_WEBHOOK_URL_METAADS`).

Les deux passages programmés **ne créent rien** : ils vérifient, auditent et
construisent à blanc. L'exécution réelle n'existe que par `workflow_dispatch`
manuel avec `executer: true`, et reste soumise aux quatre portes.

---

## Séparation budgétaire — absolue

Le budget média Meta Ads et le forfait de gestion AORA
(facturation **AORA-EXCPLUS-2026-001**) sont deux systèmes de suivi distincts,
non fongibles, dans deux fichiers distincts. **Jamais un seul tableau.**

---

## Interdictions

1. Lancer une campagne sans les quatre portes ouvertes.
2. Faire figurer « Excellence++ » dans un créatif.
3. Mentionner un effectif d'enseignants non confirmé par écrit.
4. Publier un visage d'enfant identifiable sans autorisation parentale tracée.
5. Mélanger le suivi Meta Ads et la référence de facturation du forfait AORA.
6. Dépasser le `montant_mensuel_fcfa` autorisé, même temporairement pour tester —
   toute modification de plafond repasse par une nouvelle BAB écrite.
7. Présenter la publication automatique en Groupe comme fonctionnelle avant preuve
   technique documentée.

Le numéro France **+33 753 117 352** ne doit jamais apparaître dans un créatif
publicitaire. Seuls **+237 699 403 969** et **+237 679 941 300** sont autorisés
(`config/contacts.json`). Le script rejette, il ne se contente pas de déconseiller.

---

*ACADÉMIE AORA · MA-EXC-001 · v1.0 — 05/08/2026 · Contrat AORA-CCC-005*
