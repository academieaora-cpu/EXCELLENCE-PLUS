---
# ─────────────────────────────────────────────────────────────────────────────
# GABARIT — ce fichier n'est PAS une campagne réelle.
#
# Il existe pour deux raisons : documenter les champs attendus par
# construire_campagne.py, et permettre de tester les portes sans inventer de
# campagne. Son id commence par GABARIT- : verifier_conformite_ads.py et
# generer_rapport_ads.py l'excluent de leurs décomptes.
#
# Pour créer une vraie campagne : copier ce fichier sous un nom réel, remplacer
# TOUS les A_REMPLIR, et le laisser dans en_preparation/. Le passage vers
# autorisees/ est un `git mv` fait par un humain — aucun script ne l'exécute.
# ─────────────────────────────────────────────────────────────────────────────

id: GABARIT-ADS-0000
nom: A_REMPLIR
creatif_ref: A_REMPLIR          # préfixe du visuel dans visuels/approuves/ et
                                # clé de rapprochement avec la fiche BAP_contenu

# Identifiants — laisser vides pour hériter de meta_ads_comptes.json.
# Les renseigner ne sert qu'à déclarer explicitement une cible : toute valeur
# différente de la config déclenche la porte 4 en criticité maximale.
ad_account_id:
page_id:
instagram_actor_id:

# Mécanisme central : Click-to-WhatsApp.
# Seuls les deux numéros de config/contacts.json → whatsapp_posts sont acceptés.
# Le numéro France +33 753 117 352 est rejeté par le script, pas seulement
# déconseillé.
whatsapp_numero: "+237 699 403 969"

# Fenêtre de diffusion — heures en WAT (UTC+1, sans heure d'été).
# La conversion en UTC est faite par heure_utc(), à un seul endroit.
date_debut: A_REMPLIR           # AAAA-MM-JJ
heure_debut: "06:00"
date_fin: A_REMPLIR             # AAAA-MM-JJ
heure_fin: "23:59"

# Budget en FCFA, entiers. Le plafond mensuel de meta_ads_budgets.json est une
# limite dure : un budget quotidien est projeté sur 30 jours avant comparaison.
budget_quotidien_fcfa: A_REMPLIR
budget_total_fcfa: A_REMPLIR

# Facebook et Instagram uniquement. tiktok, youtube et linkedin sont rejetés.
placements:
  - facebook

statut: en_preparation
---

A_REMPLIR — texte du créatif publicitaire.

Ce corps est le `message` du `link_data` envoyé à l'API. Il est soumis aux mêmes
interdits absolus que le contenu organique : le nom du client s'écrit toujours
Excellence+ et jamais avec un second signe plus (c'est un concurrent distinct) ;
jamais d'effectif d'enseignants ; jamais un chiffre non validé. Taux utilisables :
93 % (2023-2024) et 97 % (2024-2025).

La liste rouge de `config/liste_rouge.json` est appliquée au texte ci-dessous par
`construire_campagne.py` — un terme interdit bloque la construction, il n'est pas
seulement signalé.

Aucun `A_REMPLIR` ne doit subsister : `construire_campagne.py` refuse de
construire tant qu'il en reste un.
