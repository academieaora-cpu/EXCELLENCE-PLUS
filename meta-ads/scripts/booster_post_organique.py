#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
booster_post_organique.py — Propose des boosts pour des posts organiques déjà publiés.

CE SCRIPT NE BOOSTE RIEN LUI-MÊME ET N'APPELLE AUCUNE API META. Il écrit des
PROPOSITIONS : des briefs au même format que ceux que `construire_campagne.py`
sait déjà lire, déposés dans `meta-ads/campagnes/en_preparation/`. Rien de
nouveau n'exécute — ce script ajoute un générateur de propositions en tête d'un
pipeline déjà construit et déjà testé (4 portes, dry-run par défaut, `--executer`
explicite). Le geste qui rend une proposition exécutable reste un geste humain :
`git mv` vers `autorisees/`, exactement comme pour une campagne écrite à la main.

Éligibilité d'un post organique au boost — quatre conditions simultanées,
vérifiées par `verifier_activation.post_organique_boostable()` (définition
partagée, jamais dupliquée) :
  1. publie_le non vide — pas simplement composio_id/programme_le. Un post
     PROGRAMMÉ n'est pas encore PUBLIÉ ; confondre les deux est l'erreur que le
     contrôle 5 de superviseur-publication-aora existe pour signaler.
  2. plateforme_post_id non vide. Ce champ n'est aujourd'hui renseigné nulle
     part dans le dépôt — le mécanisme qui confirmerait une mise en ligne
     réelle n'existe pas encore (composio-publie-aora/SKILL.md §2). Conséquence
     attendue et volontaire : tant qu'il manque, ce script ne propose AUCUN
     boost. Ce n'est pas un bug de ce script, c'est la porte qui tient.
  3. plateforme dans {facebook, instagram}.
  4. ne_pas_booster n'est pas true.

Budget — répartition DÉGRESSIVE du reliquat mensuel, jamais du plafond entier :
chaque proposition consomme au plus la moitié de ce qui reste après les
campagnes déjà autorisées/actives ce mois-ci, avec un plancher en-dessous
duquel aucune proposition supplémentaire n'est écrite. Un humain peut modifier
le montant dans le brief avant de l'autoriser — ce script propose un point de
départ chiffré, jamais une décision arrêtée.

Silence, pas échec : mois non activé, plafond non défini, reliquat épuisé,
aucun post éligible → sortie normale (code 0), rien d'anormal à signaler.
Seule une écriture de fichier impossible est une erreur de CE script.

Usage :
    python3 meta-ads/scripts/booster_post_organique.py
    python3 meta-ads/scripts/booster_post_organique.py --horizon 14 --json
"""
import argparse
import json
import sys
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


def reliquat_mensuel(repo: Path, plafond: int, mois: str) -> int:
    """Plafond moins ce que les campagnes autorisées/actives engagent déjà ce mois-ci.

    Même calcul que le contrôle 10 de verifier_conformite_ads.py — importé de
    là, pas réécrit : deux calculs du même reliquat finiraient par diverger.
    """
    engage = 0
    for dossier, _, meta, _ in campagnes(repo):
        if dossier not in ("autorisees", "actives"):
            continue
        if mois not in mois_couverts(meta):
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


def ecrire_proposition(repo: Path, post_ref: str, post_meta: dict, budget_fcfa: int,
                       numero_defaut, aujourdhui: date) -> Path:
    post_id = str(post_meta.get("id", Path(post_ref).stem)).strip()
    dest = repo / "meta-ads" / "campagnes" / "en_preparation" / f"BOOST-{post_id}.md"
    debut = aujourdhui.isoformat()
    fin = (aujourdhui + timedelta(days=7)).isoformat()
    plateforme = str(post_meta.get("plateforme", "")).strip().lower()

    contenu = f"""---
# ─────────────────────────────────────────────────────────────────────────────
# PROPOSITION GÉNÉRÉE AUTOMATIQUEMENT — booster_post_organique.py, {aujourdhui.isoformat()}
#
# Ceci n'est PAS une autorisation. C'est une suggestion chiffrée, déposée dans
# en_preparation/ comme tout autre brief. Rien ne part sans le geste humain
# habituel : relecture, ajustement éventuel du budget/de la fenêtre, puis
# git mv vers autorisees/, puis --executer avec les 4 portes ouvertes.
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

# Proposé par répartition dégressive du reliquat mensuel — un humain peut
# ajuster ce montant avant d'autoriser. Ce n'est pas un montant validé.
budget_total_fcfa: {budget_fcfa}

placements:
  - {plateforme}

statut: en_preparation
genere_par: booster_post_organique.py
genere_le: {datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')}
---

(Pas de corps propre à ce brief — le texte qui part est celui du post organique
référencé ci-dessus, jamais réécrit. Voir {post_ref}.)
"""
    dest.write_text(contenu, encoding="utf-8")
    return dest


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Propose des boosts pour des posts organiques publiés — écrit, n'exécute rien.")
    ap.add_argument("--repo", type=Path, default=Path("."))
    ap.add_argument("--horizon", type=int, default=14,
                    help="N'examine que les posts publiés dans les N derniers jours")
    ap.add_argument("--mois", type=str, default=None, help="Mois évalué AAAA-MM (test)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    repo = args.repo.resolve()
    if not (repo / "meta-ads").is_dir():
        print(f"❌ {repo / 'meta-ads'} introuvable.", file=sys.stderr)
        return 2

    from verifier_activation import mois_depuis_argument
    aujourdhui = mois_depuis_argument(args.mois) if args.mois else date.today()

    resultat = {"propositions": [], "raison_silence": None}

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
            mois = cle_mois(aujourdhui)
            reliquat = reliquat_mensuel(repo, plafond, mois)
            numero_defaut = numero_whatsapp_par_defaut(repo)
            candidats = candidats_eligibles(repo, args.horizon, aujourdhui)

            if reliquat < PLANCHER_BOOST_FCFA:
                resultat["raison_silence"] = (
                    f"reliquat mensuel {fcfa(reliquat)} sous le plancher {fcfa(PLANCHER_BOOST_FCFA)} "
                    f"— déjà engagé par les campagnes autorisées/actives de {mois}")
            elif not candidats:
                resultat["raison_silence"] = (
                    f"aucun post organique éligible dans les {args.horizon} derniers jours "
                    f"(publie_le + plateforme_post_id + plateforme FB/IG requis)")
            else:
                restant = reliquat
                for jour_publie, post_ref, post_meta in candidats:
                    if restant < PLANCHER_BOOST_FCFA:
                        break
                    proposition_fcfa = max(PLANCHER_BOOST_FCFA, restant // 2)
                    proposition_fcfa = min(proposition_fcfa, restant)
                    dest = ecrire_proposition(repo, post_ref, post_meta, proposition_fcfa,
                                              numero_defaut, aujourdhui)
                    restant -= proposition_fcfa
                    resultat["propositions"].append({
                        "post_ref": post_ref,
                        "post_id": post_meta.get("id"),
                        "publie_le": jour_publie.isoformat(),
                        "budget_propose_fcfa": proposition_fcfa,
                        "fichier": str(dest.relative_to(repo)),
                    })

    if args.json:
        print(json.dumps(resultat, ensure_ascii=False, indent=2))
        return 0

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
