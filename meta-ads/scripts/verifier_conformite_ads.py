#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verifier_conformite_ads.py — Audit de conformité du pipeline Meta Ads.

Miroir de `.claude/skills/superviseur-publication-aora/scripts/verifier_conformite.py`,
adapté au payant, avec un 10e contrôle qui n'a pas d'équivalent côté organique :
le plafond budgétaire.

  1  Compte et Page cibles     ad_account_id / page_id conformes à meta_ads_comptes.json
  2  Fenêtre d'activation      aucun mois de diffusion non autorisé
  3  Double porte              BAP contenu écrit ET visuel dans visuels/approuves/
  4  Idempotence               une clé, une campagne ; un id, un fichier
  5  Vocabulaire               « active » jamais affirmé sans confirmation d'API
  6  Automatismes concurrents  aucun second moteur qui toucherait Meta Ads
  7  Expéditeur autorisé       BAB et BAP reçus de config/comptes.json
  8  Formule de validation     racine « valid » détectée, sans mot disqualifiant
  9  Numéros WhatsApp          numéros Cameroun uniquement, jamais le +33
 10  Plafond budgétaire        aucune campagne active ou programmée au-delà du plafond

LECTURE SEULE. Ne modifie rien, ne publie rien, ne corrige rien. Il dit ce qui ne
tient pas ; la décision reste humaine.

Usage :
    python3 meta-ads/scripts/verifier_conformite_ads.py
    python3 meta-ads/scripts/verifier_conformite_ads.py --repo . --json
"""
import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verifier_activation import (  # noqa: E402
    MOIS_FR,
    est_vide,
    lire_front_matter,
    lire_json,
)

DOSSIERS_CAMPAGNES = ["en_preparation", "autorisees", "actives", "terminees"]

# Détection des numéros dans le corps d'un créatif. Volontairement étroite : une
# regex trop large lit « 97 % en 2024-2025 » comme un numéro de téléphone, et un
# audit qui crie au loup à chaque chiffre est un audit que l'équipe arrête de
# lire — c'est le travers que le contrôle 4 de superviseur-publication-aora
# signale explicitement.
MOTIFS_TELEPHONE = [
    r"\+\d[\d\s().-]{6,}\d",              # format international explicite : +237 …
    r"\b237[\s.-]?\d{3}[\s.-]?\d{3}[\s.-]?\d{3}\b",   # indicatif Cameroun sans +
    r"\b6\d{2}[\s.-]\d{3}[\s.-]\d{3}\b",  # mobile camerounais local, avec séparateurs
]

# Les briefs dont l'id commence par ce préfixe documentent le format sans décrire
# une campagne réelle — ils n'ont rien à respecter.
PREFIXE_GABARIT = "GABARIT-"


def sans_accent(t: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", t)
                   if unicodedata.category(c) != "Mn").lower()


def campagnes(repo: Path):
    """Retourne [(dossier, chemin, meta, corps)] pour tous les briefs réels."""
    trouvees = []
    for dossier in DOSSIERS_CAMPAGNES:
        base = repo / "meta-ads" / "campagnes" / dossier
        if not base.is_dir():
            continue
        for chemin in sorted(base.glob("*.md")):
            meta, corps = lire_front_matter(chemin)
            if meta is None:
                continue
            if str(meta.get("id", "")).strip().startswith(PREFIXE_GABARIT):
                continue
            trouvees.append((dossier, chemin, meta, corps))
    return trouvees


def mois_couverts(meta: dict):
    """Mois AAAA-MM touchés par la fenêtre de diffusion déclarée."""
    debut = str(meta.get("date_debut", "")).strip()
    fin = str(meta.get("date_fin", "")).strip() or debut
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", debut):
        return []
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", fin):
        fin = debut
    a1, m1 = int(debut[:4]), int(debut[5:7])
    a2, m2 = int(fin[:4]), int(fin[5:7])
    mois, a, m = [], a1, m1
    while (a, m) <= (a2, m2) and len(mois) < 36:
        mois.append(f"{a:04d}-{m:02d}")
        m += 1
        if m > 12:
            m, a = 1, a + 1
    return mois


def main() -> int:
    ap = argparse.ArgumentParser(description="Audit de conformité Meta Ads — lecture seule.")
    ap.add_argument("--repo", type=Path, default=Path("."))
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    repo = args.repo.resolve()
    if not (repo / "meta-ads").is_dir():
        print(f"❌ {repo / 'meta-ads'} introuvable — ce n'est pas le dépôt attendu.",
              file=sys.stderr)
        return 2

    critiques, avertissements, infos = [], [], []

    comptes, err_comptes = lire_json(repo / "meta-ads" / "config" / "meta_ads_comptes.json")
    budgets, err_budgets = lire_json(repo / "meta-ads" / "config" / "meta_ads_budgets.json")
    activation, err_activation = lire_json(
        repo / "meta-ads" / "config" / "meta_ads_activation.json")
    contacts, err_contacts = lire_json(repo / "config" / "contacts.json")
    formules, err_formules = lire_json(repo / "config" / "validation_formules.json")
    emails_cfg, err_emails = lire_json(repo / "config" / "comptes.json")
    page_organique, _ = lire_json(repo / "config" / "page_cible.json")

    liste = campagnes(repo)

    # ── Contrôle 1 — compte et Page cibles ───────────────────────────────────
    if err_comptes:
        critiques.append(f"meta_ads_comptes.json : {err_comptes} — aucune référence de compte")
    else:
        ad_account = comptes.get("ad_account_id")
        page_id = comptes.get("page_id")
        if est_vide(ad_account):
            infos.append("ad_account_id null — valeur humaine attendue (porte 4 fermée)")
        if est_vide(comptes.get("instagram_actor_id")):
            infos.append("instagram_actor_id null — valeur humaine attendue "
                         "(bloque tout placement Instagram)")
        if est_vide(comptes.get("devise_compte")):
            infos.append("devise_compte null — le facteur de conversion des budgets "
                         "(×1 ou ×100) est indéterminé, aucun budget constructible")
        attendu = (page_organique or {}).get("facebook", {}).get("id")
        if attendu and str(attendu) != str(page_id):
            critiques.append(
                f"page_id « {page_id} » ≠ config/page_cible.json « {attendu} » — deux "
                f"fichiers se contredisent sur la Page cible")
        for dossier, chemin, meta, _ in liste:
            for champ in ("ad_account_id", "page_id", "instagram_actor_id"):
                vise = meta.get(champ)
                if est_vide(vise):
                    continue
                if str(vise).strip() != str(comptes.get(champ) or "").strip():
                    critiques.append(
                        f"{meta.get('id')} ({dossier}) vise {champ} « {vise} », référence "
                        f"« {comptes.get(champ)} » — un budget parti sur le mauvais compte "
                        f"ne se rattrape pas")

    # ── Contrôle 2 — fenêtre d'activation ────────────────────────────────────
    if err_activation:
        critiques.append(f"meta_ads_activation.json : {err_activation}")
    else:
        for dossier, chemin, meta, _ in liste:
            if dossier == "en_preparation":
                continue  # Une préparation n'engage rien tant qu'elle n'est pas autorisée.
            for ym in mois_couverts(meta):
                cle = f"{MOIS_FR[int(ym[5:7]) - 1]}_{ym[:4]}"
                entree = activation.get(cle)
                if not (isinstance(entree, dict) and entree.get("autorise") is True):
                    critiques.append(
                        f"{meta.get('id')} ({dossier}) diffuse sur {ym} — « {cle} » n'est "
                        f"pas autorisé dans meta_ads_activation.json")

    # ── Contrôle 3 — double porte (BAP contenu + visuel) ─────────────────────
    dossier_bap = repo / "meta-ads" / "validation" / "BAP_contenu"
    fiches = {}
    if dossier_bap.is_dir():
        for f in sorted(dossier_bap.glob("*.md")):
            m, _ = lire_front_matter(f)
            if m and not est_vide(m.get("creatif_ref")):
                fiches[str(m["creatif_ref"]).strip()] = (f, m)

    approuves = repo / "visuels" / "approuves"
    for dossier, chemin, meta, _ in liste:
        if dossier == "en_preparation":
            continue
        ref = str(meta.get("creatif_ref", "")).strip()
        manque = []
        fiche = fiches.get(ref)
        if fiche is None:
            manque.append(f"aucune fiche BAP pour « {ref} »")
        else:
            _, m = fiche
            if est_vide(m.get("bap_recu_le")):
                manque.append("bap_recu_le vide")
            if est_vide(m.get("bap_email_ref")):
                manque.append("bap_email_ref vide — validation non opposable")
        visuel = None
        if not est_vide(meta.get("visuel_ref")):
            cand = repo / str(meta["visuel_ref"]).strip()
            visuel = cand if cand.is_file() else None
        if visuel is None and ref and approuves.is_dir():
            visuel = next((f for f in sorted(approuves.iterdir())
                           if f.is_file() and f.name.startswith(ref)), None)
        if visuel is None:
            manque.append("aucun visuel dans visuels/approuves/")
        if manque:
            critiques.append(f"{meta.get('id')} ({dossier}) — {' ; '.join(manque)}")

    # ── Contrôle 4 — idempotence ─────────────────────────────────────────────
    par_id = {}
    for dossier, chemin, meta, _ in liste:
        par_id.setdefault(str(meta.get("id", chemin.stem)).strip(), []).append(
            str(chemin.relative_to(repo)))
    for cid, fichiers in par_id.items():
        if len(fichiers) > 1:
            critiques.append(f"id de campagne « {cid} » porté par {len(fichiers)} fichiers : "
                             f"{', '.join(fichiers)}")

    registre, err_registre = lire_json(
        repo / "meta-ads" / "campagnes" / "registre_idempotence.json")
    if not err_registre and isinstance(registre, dict):
        cles = registre.get("cles", {})
        vues = {}
        for cle, info in cles.items():
            signature = (info.get("ad_account_id"), info.get("creatif_ref"),
                         info.get("lancement_utc"))
            if signature in vues:
                critiques.append(
                    f"registre d'idempotence : deux clés pour la même campagne "
                    f"{signature} — {vues[signature]} et {cle}")
            vues[signature] = cle
        infos.append(f"registre d'idempotence : {len(cles)} campagne(s) enregistrée(s)")
    else:
        infos.append("registre d'idempotence absent — normal tant qu'aucune campagne "
                     "n'a été créée")

    # ── Contrôle 5 — vocabulaire ─────────────────────────────────────────────
    for dossier, chemin, meta, _ in liste:
        statut = sans_accent(str(meta.get("statut", "")))
        confirme = meta.get("statut_meta_confirme_le")
        if dossier == "actives" and est_vide(confirme):
            avertissements.append(
                f"{meta.get('id')} est dans campagnes/actives/ mais "
                f"statut_meta_confirme_le est vide — « active » suppose une lecture "
                f"d'API confirmant le statut ACTIVE, pas une création réussie")
        if ("active" in statut or "en ligne" in statut) and est_vide(confirme):
            avertissements.append(
                f"{meta.get('id')} — statut « {meta.get('statut')} » affirmé sans "
                f"statut_meta_confirme_le : à corriger en « programmée »")

    # ── Contrôle 6 — automatismes concurrents ────────────────────────────────
    workflows = repo / ".github" / "workflows"
    moteurs = []
    if workflows.is_dir():
        for wf in sorted(workflows.glob("*.yml")):
            texte = wf.read_text(encoding="utf-8", errors="replace")
            touche_ads = any(m in texte for m in ("meta-ads/", "META_MARKETING_TOKEN",
                                                  "graph.facebook.com"))
            if touche_ads:
                moteurs.append(wf.name)
    if len(moteurs) > 1:
        critiques.append(
            f"{len(moteurs)} workflows touchent Meta Ads ({', '.join(moteurs)}) — deux "
            f"moteurs en parallèle produisent tôt ou tard une double campagne")
    elif moteurs:
        infos.append(f"un seul workflow Meta Ads : {moteurs[0]}")
    if (repo / ".github" / "workflows" / "publish_scheduled.yml").is_file():
        critiques.append(
            "publish_scheduled.yml est de retour dans .github/workflows/ — ce moteur "
            "de publication concurrent avait été supprimé le 03/08/2026. Régression.")

    # ── Contrôle 7 — expéditeur autorisé ─────────────────────────────────────
    autorises = []
    if err_emails:
        critiques.append(f"config/comptes.json : {err_emails} — aucune adresse client de "
                         f"référence, aucun BAB ni BAP n'est validable")
    else:
        autorises = ((emails_cfg.get("client") or {}).get("emails_autorises")) or []
        if not autorises:
            critiques.append("config/comptes.json → client.emails_autorises vide")

    dossier_bab = repo / "meta-ads" / "validation" / "BAB_budget"
    preuves = []
    for base, etiquette in ((dossier_bab, "BAB"), (dossier_bap, "BAP")):
        if base.is_dir():
            for f in sorted(base.glob("*.md")):
                m, corps = lire_front_matter(f)
                preuves.append((etiquette, f, m or {}, corps or ""))

    for etiquette, f, m, corps in preuves:
        exp = str(m.get("email_expediteur", "")).strip().lower()
        if not exp:
            avertissements.append(
                f"{etiquette} {f.name} — email_expediteur absent du front-matter : "
                f"l'origine de la validation n'est pas vérifiable")
        elif autorises and exp not in [a.lower() for a in autorises]:
            critiques.append(
                f"{etiquette} {f.name} — expéditeur « {exp} » hors "
                f"config/comptes.json → emails_autorises ({', '.join(autorises)})")

    # ── Contrôle 8 — formule de validation ───────────────────────────────────
    # Élargi le 18/08/2026 : toute forme de la racine `tige_reconnue` compte comme
    # signal positif (regex \btige\w*), plus une liste figée de formules exactes —
    # voir config/validation_formules.json → _lisez_moi pour le raisonnement.
    if err_formules:
        critiques.append(f"config/validation_formules.json : {err_formules}")
    else:
        tige = sans_accent(str(formules.get("tige_reconnue") or "valid"))
        motif_tige = re.compile(r"\b" + re.escape(tige) + r"\w*")
        # dict.fromkeys : sans accents, « pas validé » et « pas validée » deviennent la
        # même clé — sans dédoublonnage le rapport citerait deux fois le même mot.
        disqualifiants = list(dict.fromkeys(
            sans_accent(x) for x in (formules.get("mots_disqualifiants") or [])))
        for etiquette, f, m, corps in preuves:
            texte = sans_accent(corps)
            signal = bool(motif_tige.search(texte))
            if not signal:
                critiques.append(
                    f"{etiquette} {f.name} — aucune forme de « {tige} » trouvée dans la "
                    f"trace (ex. valide, validé, validation).")
            trouves = [d for d in disqualifiants if d and d in texte]
            if trouves:
                # « malgré » n'a de sens que si la racine a bien été détectée : une
                # trace qui ne dit qu'« invalide » déclenche un disqualifiant sans
                # jamais avoir produit de signal positif.
                nuance = ("validation possiblement sous réserve, malgré une forme de "
                          f"« {tige} » détectée") if signal else (
                          "aucun signal positif par ailleurs : ce n'est pas une "
                          "validation sous réserve, c'est une non-validation")
                avertissements.append(
                    f"{etiquette} {f.name} — mot(s) disqualifiant(s) présent(s) : "
                    f"{', '.join(trouves)} — {nuance}")

    # ── Contrôle 9 — numéros WhatsApp ────────────────────────────────────────
    chiffres = lambda n: "".join(c for c in str(n) if c.isdigit())  # noqa: E731
    if err_contacts:
        critiques.append(f"config/contacts.json : {err_contacts} — risque qu'un créatif "
                         f"parte avec un numéro halluciné")
    else:
        permis = [chiffres(n) for n in (contacts.get("whatsapp_posts") or [])]
        exclus = {chiffres(n): motif for n, motif in (contacts.get("whatsapp_exclus") or {}).items()}
        for dossier, chemin, meta, corps in liste:
            candidats = {chiffres(meta.get("whatsapp_numero", ""))}
            for motif in MOTIFS_TELEPHONE:
                candidats |= {chiffres(n) for n in re.findall(motif, corps or "")}
            for num in {c for c in candidats if c}:
                if num in exclus:
                    critiques.append(
                        f"{meta.get('id')} ({dossier}) — numéro exclu « +{num} » : "
                        f"{exclus[num]}")
                elif num.startswith("33"):
                    critiques.append(
                        f"{meta.get('id')} ({dossier}) — numéro France « +{num} » dans un "
                        f"créatif publicitaire Excellence+")
                elif permis and num not in permis:
                    avertissements.append(
                        f"{meta.get('id')} ({dossier}) — numéro « +{num} » absent de "
                        f"config/contacts.json → whatsapp_posts")

    # ── Contrôle 10 — plafond budgétaire (propre au payant) ──────────────────
    plafond = None
    if err_budgets:
        critiques.append(f"meta_ads_budgets.json : {err_budgets} — aucun plafond opposable")
    else:
        plafond = budgets.get("montant_mensuel_fcfa")
        if est_vide(plafond):
            infos.append("montant_mensuel_fcfa null — plafond non fixé, porte 2 fermée "
                         "(aucune campagne ne peut être construite)")
        elif not isinstance(plafond, int) or isinstance(plafond, bool) or plafond <= 0:
            critiques.append(f"montant_mensuel_fcfa invalide : {plafond!r}")

    if isinstance(plafond, int) and not isinstance(plafond, bool) and plafond > 0:
        cumul = {}
        for dossier, chemin, meta, _ in liste:
            if dossier in ("en_preparation", "terminees"):
                continue
            quotidien = meta.get("budget_quotidien_fcfa")
            total = meta.get("budget_total_fcfa")
            if isinstance(quotidien, int) and not isinstance(quotidien, bool):
                projete = quotidien * 30
                if projete > plafond:
                    critiques.append(
                        f"{meta.get('id')} ({dossier}) — budget quotidien {quotidien} FCFA "
                        f"× 30 j = {projete} FCFA, au-dessus du plafond {plafond} FCFA")
                for ym in mois_couverts(meta):
                    cumul[ym] = cumul.get(ym, 0) + projete
            if isinstance(total, int) and not isinstance(total, bool):
                if total > plafond:
                    critiques.append(
                        f"{meta.get('id')} ({dossier}) — budget total {total} FCFA "
                        f"au-dessus du plafond mensuel {plafond} FCFA")
                for ym in mois_couverts(meta):
                    cumul[ym] = cumul.get(ym, 0) + total
        # Le plafond est mensuel, pas par campagne : deux campagnes sous le
        # plafond chacune peuvent le dépasser ensemble.
        for ym, montant in sorted(cumul.items()):
            if montant > plafond:
                critiques.append(
                    f"cumul des campagnes actives/autorisées sur {ym} = {montant} FCFA, "
                    f"au-dessus du plafond mensuel {plafond} FCFA")

    # ── Sortie ───────────────────────────────────────────────────────────────
    if args.json:
        print(json.dumps({"critiques": critiques, "avertissements": avertissements,
                          "infos": infos, "campagnes_examinees": len(liste)},
                         ensure_ascii=False, indent=2))
        return 1 if critiques else 0

    print("\n🔍 AUDIT DE CONFORMITÉ META ADS — lecture seule\n")
    print(f"   Campagnes réelles examinées : {len(liste)} "
          f"(gabarits exclus)")
    for i in infos:
        print(f"   · {i}")
    if critiques:
        print(f"\n   ⚠️ CRITIQUE ({len(critiques)})")
        for c in critiques:
            print(f"      {c}")
    if avertissements:
        print(f"\n   ⚠️ À corriger ({len(avertissements)})")
        for a in avertissements:
            print(f"      {a}")
    if not critiques and not avertissements:
        print("\n   ✅ Aucun écart détecté.")
    if critiques:
        print("\n   → Recommandation : ne rien créer ni activer avant d'avoir tranché "
              "le premier point.")
    print()
    return 1 if critiques else 0


if __name__ == "__main__":
    sys.exit(main())
