#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
booster_post_organique.py — Boost de posts organiques déjà publiés. Deux modes.

Par défaut (sans --executer) : CE SCRIPT NE BOOSTE RIEN ET N'APPELLE AUCUNE API
META. Il écrit des PROPOSITIONS — des briefs déposés dans
`meta-ads/campagnes/en_preparation/` — qu'un geste humain (`git mv` vers
`autorisees/`, puis `--executer` sur ce brief précis) rend exécutables.

Avec --executer : EXÉCUTION RÉELLE ET AUTOMATIQUE, sans geste humain
intermédiaire. Décision actée le 06/08/2026, après qu'un premier examen du
même mécanisme a été explicitement refusé puis reconfirmé sur description
complète du comportement (voir STATUT_PROJET.md). Ce mode est fait pour
tourner sur un cron (`.github/workflows/boost_metaads.yml`, toutes les 15 min)
et CRÉE PUIS ACTIVE réellement les campagnes qui passent les 4 portes — de
l'argent réel est engagé sans qu'un humain regarde cette transaction précise
avant qu'elle parte. Les 4 portes, le plafond budgétaire et l'idempotence
restent les seuls garde-fous ; ils sont revérifiés par le pipeline déjà testé
(`construire_campagne.construire()`, `publier_ads_facebook.publier()`), jamais
recopiés ici — voir executer_boost().

Éligibilité d'un post organique au boost — cinq conditions simultanées,
vérifiées par `verifier_activation.post_organique_boostable()` (définition
partagée, jamais dupliquée) :
  1. publie_le non vide — pas simplement composio_id/programme_le. Un post
     PROGRAMMÉ n'est pas encore PUBLIÉ ; confondre les deux est l'erreur que le
     contrôle 5 de superviseur-publication-aora existe pour signaler.
  2. bap_recu_le ET bap_email_ref non vides, directement sur le post.
  3. plateforme_post_id non vide. Ce champ n'est aujourd'hui renseigné nulle
     part dans le dépôt — le mécanisme qui confirmerait une mise en ligne
     réelle n'existe pas encore (composio-publie-aora/SKILL.md §2). Conséquence
     attendue et volontaire : tant qu'il manque, ce script ne boost AUCUN post,
     dans aucun des deux modes. Ce n'est pas un bug de ce script, c'est la
     porte qui tient.
  4. plateforme dans {facebook, instagram}.
  5. ne_pas_booster n'est pas true.

Budget — répartition DÉGRESSIVE du reliquat mensuel, jamais du plafond entier :
chaque boost consomme au plus la moitié de ce qui reste après les campagnes
déjà autorisées/actives ce mois-ci, avec un plancher en-dessous duquel aucun
boost supplémentaire n'est tenté (ni proposé, ni exécuté).

Silence, pas échec : mois non activé, plafond non défini, reliquat épuisé,
aucun post éligible → sortie normale (code 0), rien d'anormal à signaler, dans
les deux modes. Seul un échec technique après ouverture de toutes les portes
(--executer) est journalisé comme un échec — jamais une porte fermée.

Usage :
    python3 meta-ads/scripts/booster_post_organique.py
    python3 meta-ads/scripts/booster_post_organique.py --horizon 14 --json
    python3 meta-ads/scripts/booster_post_organique.py --executer
"""
import argparse
import json
import shutil
import sys
import tempfile
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verifier_activation import (  # noqa: E402
    cle_mois,
    est_vide,
    fcfa,
    lire_front_matter,
    lire_json,
    porte_1_activation,
    porte_2_budget,
    post_organique_boostable,
)
from verifier_conformite_ads import campagnes, mois_couverts  # noqa: E402
from publier_ads_facebook import publier  # noqa: E402

# En-dessous de ce montant, une proposition de boost n'a plus de sens
# opérationnel — mieux vaut ne rien proposer que proposer un montant symbolique
# qu'un humain devra de toute façon ajuster à la main.
PLANCHER_BOOST_FCFA = 1000

DOSSIER_PROPOSITIONS = ["en_preparation", "autorisees", "actives", "terminees"]


def deja_propose(repo: Path, post_ref: str) -> Path | None:
    """Un post déjà couvert par un brief de boost, quel que soit son dossier."""
    for dossier in DOSSIER_PROPOSITIONS:
        base = repo / "meta-ads" / "campagnes" / dossier
        if not base.is_dir():
            continue
        for chemin in base.glob("BOOST-*.md"):
            meta, _ = lire_front_matter(chemin)
            if meta and str(meta.get("post_ref", "")).strip() == str(post_ref).strip():
                return chemin
    return None


def reliquat_mensuel(repo: Path, plafond: int, aujourdhui: date) -> int:
    """Plafond moins ce que les campagnes autorisées/actives engagent déjà ce mois-ci.

    Même calcul que le contrôle 10 de verifier_conformite_ads.py — importé de
    là, pas réécrit : deux calculs du même reliquat finiraient par diverger.

    ⚠️ Prend `aujourdhui` (date), PAS une clé « aout_2026 » façon cle_mois() :
    mois_couverts() rend ses clés au format AAAA-MM ("2026-08"), format
    différent et incompatible avec celui de cle_mois(). Les comparer sans
    conversion ne matche jamais — bug réel détecté par test le 06/08/2026 (le
    reliquat renvoyait toujours le plafond entier, jamais le montant réellement
    disponible). Cette fonction construit sa propre clé AAAA-MM en interne,
    justement pour ne plus dépendre d'un appelant qui pourrait se tromper de
    format une seconde fois.
    """
    mois_aaaa_mm = f"{aujourdhui.year:04d}-{aujourdhui.month:02d}"
    engage = 0
    for dossier, _, meta, _ in campagnes(repo):
        if dossier not in ("autorisees", "actives"):
            continue
        if mois_aaaa_mm not in mois_couverts(meta):
            continue
        q = meta.get("budget_quotidien_fcfa")
        t = meta.get("budget_total_fcfa")
        if isinstance(q, int) and not isinstance(q, bool):
            engage += q * 30
        if isinstance(t, int) and not isinstance(t, bool):
            engage += t
    return max(0, plafond - engage)


def numero_whatsapp_par_defaut(repo: Path):
    contacts, err = lire_json(repo / "config" / "contacts.json")
    if err:
        return None
    numeros = contacts.get("whatsapp_posts") or []
    return numeros[0] if numeros else None


def candidats_eligibles(repo: Path, horizon_jours: int, aujourdhui: date):
    """Posts organiques boostables, non déjà proposés, triés du plus récent au plus ancien."""
    candidats = []
    for chemin in sorted((repo / "contenu").rglob("*.md")):
        meta, _ = lire_front_matter(chemin)
        if not meta:
            continue
        ref = str(chemin.relative_to(repo))
        ok, motif, post_meta = post_organique_boostable(repo, ref)
        if not ok:
            continue
        publie_le = str(post_meta.get("publie_le", "")).strip()[:10]
        try:
            jour_publie = date.fromisoformat(publie_le)
        except ValueError:
            continue
        if jour_publie < aujourdhui - timedelta(days=horizon_jours):
            continue
        if deja_propose(repo, ref):
            continue
        candidats.append((jour_publie, ref, post_meta))
    candidats.sort(key=lambda c: c[0], reverse=True)
    return candidats


def contenu_brief_boost(post_ref: str, post_meta: dict, budget_fcfa: int, numero_defaut,
                        aujourdhui: date, mode_propose: bool = True) -> tuple:
    """Construit le contenu YAML d'un brief de boost. Une seule définition,
    réutilisée en mode proposition (§ ecrire_proposition) et en mode exécution
    automatique (§ executer_boost) — le format du brief ne doit jamais diverger
    entre les deux, seule sa DESTINATION (en_preparation/ vs. temporaire) diffère.

    Retourne (post_id, contenu).
    """
    post_id = str(post_meta.get("id", Path(post_ref).stem)).strip()
    debut = aujourdhui.isoformat()
    fin = (aujourdhui + timedelta(days=7)).isoformat()
    plateforme = str(post_meta.get("plateforme", "")).strip().lower()

    entete = (
        "# PROPOSITION GÉNÉRÉE AUTOMATIQUEMENT — booster_post_organique.py, "
        f"{aujourdhui.isoformat()}\n#\n"
        "# Ceci n'est PAS une autorisation. C'est une suggestion chiffrée, déposée dans\n"
        "# en_preparation/ comme tout autre brief. Rien ne part sans le geste humain\n"
        "# habituel : relecture, ajustement éventuel du budget/de la fenêtre, puis\n"
        "# git mv vers autorisees/, puis --executer avec les 4 portes ouvertes."
        if mode_propose else
        "# BOOST AUTOMATIQUE — brief de travail temporaire, booster_post_organique.py --executer\n#\n"
        "# Ce fichier n'est PAS un brief humain : il sert uniquement à faire transiter ce\n"
        "# boost par construire_campagne.py/publier_ads_facebook.py, exactement comme un\n"
        "# brief autorisé à la main. Supprimé après l'exécution, réussie ou non — voir\n"
        "# meta-ads/campagnes/actives/ pour la trace du résultat, jamais ce fichier."
    )

    contenu = f"""---
# ─────────────────────────────────────────────────────────────────────────────
{entete}
# ─────────────────────────────────────────────────────────────────────────────

id: BOOST-{post_id}
nom: "Boost — {post_id}"
type_campagne: boost
post_ref: {post_ref}

ad_account_id:
page_id: "61584305458367"
instagram_actor_id:

whatsapp_numero: "{numero_defaut or 'A_REMPLIR'}"

date_debut: {debut}
heure_debut: "08:00"
date_fin: {fin}
heure_fin: "23:59"

# {"Proposé" if mode_propose else "Calculé"} par répartition dégressive du reliquat mensuel.
budget_total_fcfa: {budget_fcfa}

placements:
  - {plateforme}

statut: {"en_preparation" if mode_propose else "en_execution_automatique"}
genere_par: booster_post_organique.py
genere_le: {datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')}
---

(Pas de corps propre à ce brief — le texte qui part est celui du post organique
référencé ci-dessus, jamais réécrit. Voir {post_ref}.)
"""
    return post_id, contenu


def ecrire_proposition(repo: Path, post_ref: str, post_meta: dict, budget_fcfa: int,
                       numero_defaut, aujourdhui: date) -> Path:
    post_id, contenu = contenu_brief_boost(post_ref, post_meta, budget_fcfa, numero_defaut,
                                           aujourdhui, mode_propose=True)
    dest = repo / "meta-ads" / "campagnes" / "en_preparation" / f"BOOST-{post_id}.md"
    dest.write_text(contenu, encoding="utf-8")
    return dest


def executer_boost(repo: Path, post_ref: str, post_meta: dict, budget_fcfa: int,
                   numero_defaut, aujourdhui: date) -> dict:
    """Exécute réellement un boost. Retourne un dict de résultat pour le rapport
    de ce passage — n'imprime rien elle-même, main() s'en charge.

    N'implémente AUCUNE logique d'appel API propre : construit un brief
    temporaire (jamais dans en_preparation/ — ce dossier reste un espace humain,
    jamais traversé par ce mode) et délègue entièrement à publier_ads_facebook.
    publier(), qui revérifie lui-même les 4 portes, l'idempotence, le plafond
    budgétaire, et applique les politiques d'échec typées déjà testées. Ce
    script n'a donc AUCUNE des ces règles à réimplémenter — et donc aucune
    façon de diverger de ce que le chemin humain (§4bis de
    meta-ads-publie-aora/SKILL.md) applique par ailleurs.

    activer_immediatement=True : seule différence avec le chemin humain. C'est
    la ligne qui fait la politique de ce mode — la campagne part en ACTIVE dans
    la même exécution que sa création, sans qu'un humain ne regarde cette
    transaction précise. Ne JAMAIS passer ce paramètre à True ailleurs que dans
    cette fonction.
    """
    post_id, contenu = contenu_brief_boost(post_ref, post_meta, budget_fcfa, numero_defaut,
                                           aujourdhui, mode_propose=False)
    plateforme = str(post_meta.get("plateforme", "")).strip().lower()

    tmp_dir = Path(tempfile.mkdtemp(prefix="boost-auto-"))
    tmp_brief = tmp_dir / f"BOOST-{post_id}.md"
    tmp_brief.write_text(contenu, encoding="utf-8")

    try:
        code_sortie = publier(repo, tmp_brief, plateforme, executer=True,
                              jour=aujourdhui, activer_immediatement=True)
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    if code_sortie != 0:
        return {"post_id": post_id, "post_ref": post_ref, "succes": False,
               "budget_fcfa": budget_fcfa}

    # Succès : la trace vit dans actives/, jamais le brief temporaire (supprimé
    # ci-dessus) ni en_preparation/ (jamais touché par ce mode). L'identifiant
    # Meta réel est déjà dans registre_idempotence.json (écrit par publier()) —
    # ce fichier est une vue lisible pour les humains, pas une seconde source
    # de vérité : generer_rapport_ads.py lit les deux et ne devrait jamais les
    # voir diverger.
    dest = repo / "meta-ads" / "campagnes" / "actives" / f"BOOST-{post_id}.md"
    contenu_trace = contenu.replace("statut: en_execution_automatique",
                                    "statut: programmee")
    dest.write_text(contenu_trace, encoding="utf-8")

    return {"post_id": post_id, "post_ref": post_ref, "succes": True,
           "budget_fcfa": budget_fcfa, "fichier": str(dest.relative_to(repo))}


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Boost des posts organiques publiés — propose par défaut, exécute avec --executer.")
    ap.add_argument("--repo", type=Path, default=Path("."))
    ap.add_argument("--horizon", type=int, default=14,
                    help="N'examine que les posts publiés dans les N derniers jours")
    ap.add_argument("--mois", type=str, default=None, help="Mois évalué AAAA-MM (test)")
    ap.add_argument("--executer", action="store_true",
                    help="EXÉCUTION RÉELLE ET AUTOMATIQUE — crée ET active les campagnes qui "
                         "passent les 4 portes, sans confirmation humaine par transaction. "
                         "Sans ce flag : dry-run, écrit des propositions, n'appelle aucune API.")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    repo = args.repo.resolve()
    if not (repo / "meta-ads").is_dir():
        print(f"❌ {repo / 'meta-ads'} introuvable.", file=sys.stderr)
        return 2

    from verifier_activation import mois_depuis_argument
    aujourdhui = mois_depuis_argument(args.mois) if args.mois else date.today()

    resultat = {"propositions": [], "executions": [], "raison_silence": None}

    porte1 = porte_1_activation(repo, aujourdhui)
    if not porte1.ouverte:
        resultat["raison_silence"] = f"porte 1 fermée — {porte1.motif}"
    else:
        porte2 = porte_2_budget(repo)
        if not porte2.ouverte:
            resultat["raison_silence"] = f"porte 2 fermée — {porte2.motif}"
        else:
            budgets, _ = lire_json(repo / "meta-ads" / "config" / "meta_ads_budgets.json")
            plafond = budgets["montant_mensuel_fcfa"]
            mois = cle_mois(aujourdhui)  # forme "aout_2026" — affichage humain uniquement
            reliquat = reliquat_mensuel(repo, plafond, aujourdhui)
            numero_defaut = numero_whatsapp_par_defaut(repo)
            candidats = candidats_eligibles(repo, args.horizon, aujourdhui)

            if reliquat < PLANCHER_BOOST_FCFA:
                resultat["raison_silence"] = (
                    f"reliquat mensuel {fcfa(reliquat)} sous le plancher {fcfa(PLANCHER_BOOST_FCFA)} "
                    f"— déjà engagé par les campagnes autorisées/actives de {mois}")
            elif not candidats:
                resultat["raison_silence"] = (
                    f"aucun post organique éligible dans les {args.horizon} derniers jours "
                    f"(publie_le + BAP direct + plateforme_post_id + plateforme FB/IG requis)")
            else:
                restant = reliquat
                for jour_publie, post_ref, post_meta in candidats:
                    if restant < PLANCHER_BOOST_FCFA:
                        break
                    budget_calcule = max(PLANCHER_BOOST_FCFA, restant // 2)
                    budget_calcule = min(budget_calcule, restant)

                    if args.executer:
                        r = executer_boost(repo, post_ref, post_meta, budget_calcule,
                                          numero_defaut, aujourdhui)
                        resultat["executions"].append(r)
                        if r["succes"]:
                            restant -= budget_calcule
                    else:
                        dest = ecrire_proposition(repo, post_ref, post_meta, budget_calcule,
                                                  numero_defaut, aujourdhui)
                        restant -= budget_calcule
                        resultat["propositions"].append({
                            "post_ref": post_ref,
                            "post_id": post_meta.get("id"),
                            "publie_le": jour_publie.isoformat(),
                            "budget_propose_fcfa": budget_calcule,
                            "fichier": str(dest.relative_to(repo)),
                        })

    echecs = [e for e in resultat["executions"] if not e["succes"]]

    if args.json:
        print(json.dumps(resultat, ensure_ascii=False, indent=2))
        return 1 if echecs else 0

    if args.executer:
        print(f"\n🚀 BOOST AUTOMATIQUE — EXÉCUTION RÉELLE — {aujourdhui.strftime('%d/%m/%Y')}\n")
        if resultat["executions"]:
            reussies = [e for e in resultat["executions"] if e["succes"]]
            if reussies:
                print(f"   {len(reussies)} boost(s) créé(s) et activé(s) :")
                for e in reussies:
                    print(f"      ✅ {e['post_id']} — {fcfa(e['budget_fcfa'])} → {e['fichier']}")
            if echecs:
                print(f"   {len(echecs)} échec(s) technique(s) — détail dans l'alerte Slack "
                      f"de chaque tentative :")
                for e in echecs:
                    print(f"      ❌ {e['post_id']} — {fcfa(e['budget_fcfa'])} tentés, "
                          f"post organique non affecté")
            print()
        else:
            print(f"   Rien à exécuter — {resultat['raison_silence']}.")
            print("   Ce n'est pas un échec : une porte fermée ou l'absence de candidat est "
                  "le comportement attendu.\n")
        return 1 if echecs else 0

    print(f"\n💡 PROPOSITIONS DE BOOST — {aujourdhui.strftime('%d/%m/%Y')}\n")
    if resultat["propositions"]:
        print(f"   {len(resultat['propositions'])} proposition(s) écrite(s) dans "
              f"meta-ads/campagnes/en_preparation/ :")
        for p in resultat["propositions"]:
            print(f"      · {p['post_id']} (publié {p['publie_le']}) — "
                  f"{fcfa(p['budget_propose_fcfa'])} proposés → {p['fichier']}")
        print("\n   Ce sont des PROPOSITIONS. Rien ne part sans le geste humain habituel : "
              "relecture,")
        print("   ajustement éventuel, git mv vers autorisees/, puis --executer.\n")
    else:
        print(f"   Rien à proposer — {resultat['raison_silence']}.")
        print("   Ce n'est pas un échec : une porte fermée ou l'absence de candidat est "
              "le comportement attendu.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
