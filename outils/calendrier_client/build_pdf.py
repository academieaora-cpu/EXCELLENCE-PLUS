#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_pdf.py — Génère le calendrier éditorial CLIENT (extrait août-septembre
2026), livrable jumeau de CE-EXC-001 destiné à la validation BAT.

Lit les données déjà produites par outils/calendrier_editorial/generate.py
(../calendrier_editorial/data/*.json) — une seule source de données, deux
sorties (cf. skill calendrier-editorial-aora). Ne re-génère aucun contenu :
filtre et met en forme pour un public client.

Logique volontairement opposée à l'outil interne : trié par PRIORITÉ DE
PILIER (pas chronologiquement), langage client (pas de statut SOP-001, pas
de jargon de production), format A4 PAYSAGE.

Usage :
  cd outils/calendrier_editorial && python3 generate.py   # (re)génère data/
  cd ../calendrier_client && python3 build_pdf.py
  node render_pdf.js out/calendrier_client.html ../../rapports/calendrier_client_excellence_plus_aout_septembre.pdf
"""
import base64
import codecs
import json
import mimetypes
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "calendrier_editorial", "data")
LOGOS = os.path.join(HERE, "..", "..", "_base", "logos")
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

MOIS_CIBLES = ("2026-08", "2026-09")
FR_JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]


def load(name):
    with codecs.open(os.path.join(DATA, name), "r", encoding="utf-8") as f:
        return json.load(f)


def data_uri(path):
    mime = mimetypes.guess_type(path)[0] or "image/png"
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    return "data:%s;base64,%s" % (mime, b64)


def esc(s):
    return (str(s) if s is not None else "").replace("&", "&amp;").replace("<", "&lt;") \
        .replace(">", "&gt;").replace('"', "&quot;")


def jour_semaine(date_iso):
    import datetime
    d = datetime.date.fromisoformat(date_iso)
    return FR_JOURS[d.weekday()]


def main():
    entries = load("entries.json")
    pillars = load("pillars.json")
    platforms = load("platforms.json")
    meta_ads = load("meta_ads.json")
    months = load("months.json")
    month_by_id = {m["id"]: m for m in months}
    plat_by_id = {p["id"]: p for p in platforms}

    scoped = [e for e in entries if e["mois"] in MOIS_CIBLES]
    ads_scoped = [a for a in meta_ads if a["mois"] in MOIS_CIBLES]

    logo_aora = data_uri(os.path.join(LOGOS, "aora_logo_400w.png"))
    logo_exc = data_uri(os.path.join(LOGOS, "excellence_plus_logo_500x500.png"))

    def card_html(e, pilier_couleur):
        p = plat_by_id[e["plateforme"]]
        jour = jour_semaine(e["date_iso"]).capitalize()
        return """<div class="pitch" style="border-left-color:%s">
      <div class="ptop"><h3>%s</h3><span class="pwhen">%s</span></div>
      <div class="pbadges">
        <span class="pbadge" style="background:%s">%s %s</span>
        <span class="pbadge fmt">%s</span>
      </div>
    </div>""" % (esc(pilier_couleur), esc(e["titre"]),
                  esc("%s — %s" % (jour, e["date"].split(" · ")[1] if " · " in e["date"] else e["date"])),
                  esc(p["couleur"]), esc(p["icone"]), esc(p["nom"]), esc(e["format"]))

    pillar_sections = []
    for p in pillars:
        items = sorted([e for e in scoped if e["pilier"] == p["id"]], key=lambda e: e["date_iso"])
        if not items:
            continue
        cards = [card_html(e, p["couleur"]) for e in items]
        rows = []
        for i in range(0, len(cards), 2):
            left = cards[i]
            right = cards[i + 1] if i + 1 < len(cards) else '<div class="pitch" style="visibility:hidden"></div>'
            rows.append("<tr><td>%s</td><td>%s</td></tr>" % (left, right))
        # thead repeats automatically on every printed page this table spans —
        # keeps the pillar identity visible on continuation pages.
        pillar_sections.append("""<table class="pillar-table">
  <thead><tr><th colspan="2">
    <div class="pillar-ttl" style="background:%s">
      <span>%s%s</span>
      <span class="tag">%d publication%s</span>
    </div>
  </th></tr></thead>
  <tbody>
    %s
  </tbody>
</table>""" % (esc(p["couleur"]), esc(p["nom_long"]), " ★ pilier phare" if p.get("phare") else "",
               len(items), "s" if len(items) > 1 else "", "\n".join(rows)))

    ads_html = ""
    if ads_scoped:
        rows = "\n".join(
            """<div class="ads-card">
        <div class="ads-name">🚩 %s</div>
        <div class="ads-meta">%s%s</div>
      </div>""" % (esc(a["nom"]), esc(a["periode"]), " · " + esc(a["budget"]) if a.get("budget") else "")
            for a in ads_scoped
        )
        ads_html = """<div class="ads-box">
    <h2>Campagnes Meta Ads actives sur la période</h2>
    <div class="ads-grid">%s</div>
    <p class="ads-note">Budget Meta Ads distinct du forfait de gestion AORA — géré directement par
      M. NDOMMIE sur Meta Business. Ces deux montants ne sont jamais additionnés ni présentés
      comme un total unique.</p>
  </div>""" % rows

    month_labels = " &amp; ".join(month_by_id[m]["nom"].replace(" 2026", "") for m in MOIS_CIBLES)

    html = HTML_SHELL.format(
        logo_aora=logo_aora,
        logo_exc=logo_exc,
        month_labels=month_labels,
        total=len(scoped),
        ads_html=ads_html,
        pillar_sections="\n".join(pillar_sections),
    )

    out_path = os.path.join(OUT, "calendrier_client.html")
    with codecs.open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print("HTML client écrit :", out_path, "(%d publications, %d campagnes ads)" % (len(scoped), len(ads_scoped)))


HTML_SHELL = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>Calendrier éditorial client — Excellence+ — CC-EXC-001</title>
<style>
  :root{{
    --navy:#1B2D5C; --navy2:#2A3F6E; --orange:#EC770D;
    --tint-navy:#F1F3F8; --tint-orange:#FDF1E8;
    --gray-line:#E8E8EC; --gray-mid:#9CA0A8; --white:#fff;
  }}
  *{{box-sizing:border-box;margin:0;padding:0}}
  html,body{{background:#eef0f5}}
  body{{font-family:'Inter',-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
       color:var(--navy);line-height:1.45;font-size:10pt}}
  .page{{position:relative;width:297mm;min-height:210mm;background:#fff;margin:0 auto 6mm;overflow:hidden;
        padding:14mm 16mm}}
  .page.cover{{background:var(--navy);color:#fff;padding:0}}
  @media print{{
    html,body{{background:#fff}}
    .page{{margin:0;box-shadow:none;page-break-after:always;min-height:auto;width:auto;padding:10mm 14mm}}
    .page.cover{{padding:0}}
    .page:last-child{{page-break-after:auto}}
  }}

  .kicker{{font-size:9pt;font-weight:800;color:var(--orange);letter-spacing:.6px;text-transform:uppercase;margin-bottom:6px}}
  .kicker::before{{content:"— "}}
  .tiret-accent{{width:60pt;height:5pt;background:var(--orange);margin:10px 0 16px}}
  .trait-sep{{height:2px;background:var(--orange);width:100%;margin:0 0 10mm}}
  .meta-top{{display:flex;justify-content:space-between;align-items:center;font-size:8pt;color:var(--gray-mid);
            text-transform:uppercase;letter-spacing:.4px;margin-bottom:8px}}
  h1{{font-size:24pt;font-weight:800;line-height:1.1;color:var(--navy)}}
  h2{{font-size:14pt;font-weight:800;color:var(--navy);margin-bottom:10px}}
  p{{margin-bottom:8px}}

  /* ---------- Couverture ---------- */
  .cover .inner{{padding:20mm 22mm;height:210mm;display:flex;flex-direction:column}}
  .cover .logos{{display:flex;gap:14px;align-items:center}}
  .cover .logos .chip-logo{{background:#fff;border-radius:10px;padding:8px 12px;display:flex;align-items:center;height:40px}}
  .cover .logos .chip-logo img{{height:24px;width:auto;display:block}}
  .cover .bat-badge{{display:inline-block;margin-top:22px;background:var(--orange);color:#fff;font-weight:800;
                     font-size:10pt;letter-spacing:.5px;padding:6px 16px;border-radius:999px}}
  .cover .title1{{color:#fff;font-size:34pt;font-weight:800;line-height:1.1;margin-top:14px}}
  .cover .title2{{color:var(--orange);font-size:34pt;font-weight:800;line-height:1.1}}
  .cover .tiret-c{{width:80pt;height:6pt;background:var(--orange);margin:16px 0}}
  .cover .sub{{color:#C9D2E8;font-size:11.5pt;max-width:480px;line-height:1.55}}
  .cover .refbox{{margin-top:auto;border-top:1px solid rgba(255,255,255,.25);padding-top:14px;
                 display:flex;justify-content:space-between;align-items:flex-end;font-size:9pt;color:#C9D2E8}}
  .cover .refbox b{{color:#fff;font-size:10pt}}
  .cover .signature{{font-size:10pt;color:var(--orange);font-weight:800;letter-spacing:.3px}}

  /* ---------- Intro / Meta Ads ---------- */
  .legend-row{{display:flex;gap:10px;flex-wrap:wrap;margin:12px 0 16px}}
  .legend-chip{{display:flex;align-items:center;gap:6px;font-size:10pt;font-weight:700;color:#fff;
               padding:6px 12px;border-radius:999px}}
  .legend-chip .pct{{font-weight:600;opacity:.85;font-size:9pt}}
  .ads-box{{margin-top:20px;border:1px solid var(--gray-line);border-radius:10px;padding:16px 18px;background:var(--tint-orange)}}
  .ads-box h2{{margin-bottom:10px}}
  .ads-grid{{display:flex;gap:14px;flex-wrap:wrap}}
  .ads-card{{flex:1;min-width:220px;background:#fff;border:1px solid var(--gray-line);border-left:4pt solid var(--orange);
            border-radius:8px;padding:10px 14px}}
  .ads-name{{font-weight:800;font-size:10.5pt;color:var(--navy)}}
  .ads-meta{{font-size:9.5pt;color:var(--gray-mid);margin-top:3px}}
  .ads-note{{font-size:9pt;color:var(--navy2);margin-top:10px;margin-bottom:0}}

  /* ---------- Sections piliers ---------- */
  /* thead se répète automatiquement sur chaque page imprimée que la table traverse —
     garde l'identité du pilier visible sur les pages de continuation. */
  table.pillar-table{{width:100%;border-collapse:separate;border-spacing:0 8px;margin-bottom:2px}}
  table.pillar-table td{{width:50%;vertical-align:top;padding:0}}
  .pillar-ttl{{font-size:13pt;font-weight:800;color:#fff;padding:9px 16px;border-radius:8px;margin-bottom:10px;
              display:flex;justify-content:space-between;align-items:center}}
  .pillar-ttl .tag{{font-size:9.5pt;font-weight:600;opacity:.9}}
  .pitch{{border:1px solid var(--gray-line);border-left:4pt solid var(--navy);border-radius:8px;
         margin:0 7px;padding:9px 12px;break-inside:avoid;page-break-inside:avoid}}
  .ptop{{display:flex;justify-content:space-between;align-items:baseline;gap:10px}}
  .pitch h3{{font-size:10.5pt;color:var(--navy);font-weight:700;line-height:1.3}}
  .pwhen{{font-size:8.5pt;color:var(--gray-mid);white-space:nowrap;flex-shrink:0}}
  .pbadges{{display:flex;gap:5px;margin-top:6px;flex-wrap:wrap}}
  .pbadge{{font-size:7.8pt;font-weight:700;color:#fff;padding:2px 8px;border-radius:999px}}
  .pbadge.fmt{{background:var(--gray-mid)}}

  /* ---------- Mentions ---------- */
  .mbox{{border:1px solid var(--gray-line);border-radius:10px;padding:14px 18px;margin-bottom:12px;background:#F8FAFC}}
  .mbox b{{color:var(--navy)}}
  .circuit{{display:flex;align-items:center;flex-wrap:wrap;gap:0;margin:14px 0}}
  .circuit .step{{background:var(--navy);color:#fff;font-size:9pt;font-weight:700;padding:8px 13px;border-radius:6px;
                 text-align:center;flex:1;min-width:80px}}
  .circuit .arrow{{color:var(--orange);font-size:15px;font-weight:800;padding:0 5px}}
  .warn-callout{{background:var(--tint-navy);border-left:4pt solid var(--orange);border-radius:4px;
               padding:11px 15px;margin:12px 0;font-size:9.5pt}}
  .warn-callout b{{color:var(--orange)}}
  .interdit-list{{list-style:none;margin:10px 0 0}}
  .interdit-list li{{display:flex;gap:9px;padding:5px 0;font-size:9.5pt}}
  .interdit-list .x{{color:var(--orange);font-weight:800;flex-shrink:0}}
  .contact{{font-size:10pt;line-height:1.9}}
  .foot{{margin-top:16px;border-top:1px solid var(--gray-line);padding-top:9px;font-size:9pt;color:var(--gray-mid)}}
  .foot b{{color:var(--navy)}}

  @media print{{
    .cover .inner{{height:180mm;padding:14mm 20mm}}
  }}
</style>
</head>
<body>

<!-- ============ COUVERTURE ============ -->
<div class="page cover">
  <div class="inner">
    <div class="logos">
      <div class="chip-logo"><img src="{logo_aora}" alt="AORA"></div>
      <div class="chip-logo"><img src="{logo_exc}" alt="Excellence+"></div>
    </div>
    <div class="bat-badge">SOUMIS POUR VALIDATION BAT</div>
    <div class="title1">CALENDRIER ÉDITORIAL</div>
    <div class="title2">CLIENT</div>
    <div class="tiret-c"></div>
    <div class="sub">Plan de contenu — sujets, formats, plateformes et calendrier de diffusion —
      pour {month_labels} 2026. Extrait à valider avant rédaction des textes définitifs ; chaque
      publication suivra ensuite son propre circuit BAT/BAP une fois rédigée.</div>
    <div class="refbox">
      <div>
        <div><b>Référence</b> CC-EXC-001 · Extrait de CE-EXC-001</div>
        <div>{total} publications proposées · Version 1.0 · 28 juillet 2026</div>
      </div>
      <div style="text-align:right">
        <div class="signature">L'EXCELLENCE À VOTRE PORTÉE.</div>
        <div>AORA Communication Agency</div>
      </div>
    </div>
  </div>
</div>

<!-- ============ INTRO + META ADS ============ -->
<div class="page">
  <div class="meta-top"><span>Excellence+ — Calendrier éditorial client</span><span>CC-EXC-001</span></div>
  <div class="trait-sep"></div>
  <div class="kicker">Comment lire ce document</div>
  <h1>Trois piliers,<br><span style="color:var(--orange)">un plan équilibré</span></h1>
  <div class="tiret-accent"></div>
  <p>Les publications ci-après sont classées par <strong>pilier éditorial</strong> — pas par ordre
    chronologique — pour donner une vue claire de l'équilibre stratégique du plan. La date et l'heure
    de diffusion prévues figurent sur chaque fiche.</p>
  <div class="legend-row">
    <span class="legend-chip" style="background:#C2570F">Autorité éducative <span class="pct">★ pilier phare · 40%</span></span>
    <span class="legend-chip" style="background:#1B2D5C">La méthode Excellence+ <span class="pct">35%</span></span>
    <span class="legend-chip" style="background:#1B6B3C">La preuve <span class="pct">25%</span></span>
  </div>
  {ads_html}
</div>

{pillar_sections}

<!-- ============ MENTIONS & CIRCUIT ============ -->
<div class="page">
  <div class="meta-top"><span>Excellence+ — Calendrier éditorial client</span><span>CC-EXC-001</span></div>
  <div class="trait-sep"></div>
  <div class="kicker">Mentions &amp; circuit de validation</div>
  <h1>Rien ne part<br><span style="color:var(--orange)">sans BAP écrit</span></h1>
  <div class="tiret-accent"></div>

  <div class="circuit">
    <div class="step">draft</div><div class="arrow">→</div>
    <div class="step">BAT soumis<br><span style="font-weight:400;font-size:8pt">email, 48h ouvrables</span></div><div class="arrow">→</div>
    <div class="step">BAP reçu<br><span style="font-weight:400;font-size:8pt">email uniquement</span></div><div class="arrow">→</div>
    <div class="step">publication</div><div class="arrow">→</div>
    <div class="step">archivage</div>
  </div>

  <div class="warn-callout"><b>Validation par email uniquement</b> — un retour vocal WhatsApp n'est
    jamais traité comme un BAP valide. Délai de retour souhaité : 48h ouvrables. Ce document présente
    le <strong>plan de sujets</strong> ; les textes définitifs de chaque publication suivront leur
    propre circuit BAT/BAP avant diffusion.</div>

  <ul class="interdit-list">
    <li><span class="x">✕</span><span>Jamais « Excellence++ » — nom exact : <strong>Excellence+</strong></span></li>
    <li><span class="x">✕</span><span>Jamais de mention du nombre d'enseignants</span></li>
    <li><span class="x">✕</span><span>Jamais de mélange entre budget forfait AORA et budget Meta Ads</span></li>
    <li><span class="x">✕</span><span>Taux de réussite communicables : <strong>93% (2023-2024) · 97% (2024-2025)</strong> uniquement</span></li>
  </ul>

  <div class="mbox contact" style="margin-top:16px">
    <b>Contact validation</b><br>
    Stéphane — Responsable projet · Laurence — Account Manager<br>
    M. NDOMMIE GOAP Saturnin — Excellence+
  </div>

  <div class="foot"><b>AORA Communication Agency</b> — L'EXCELLENCE À VOTRE PORTÉE.<br>
    Excellence+ · Calendrier éditorial client · CC-EXC-001 · 28 juillet 2026 · Document destiné à la validation BAT.</div>
</div>

</body>
</html>
"""

if __name__ == "__main__":
    main()
