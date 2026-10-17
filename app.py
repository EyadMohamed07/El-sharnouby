# -*- coding: utf-8 -*-
"""
================================================================================
 ELSHARNOUBY GROUP | LEO MODA — EXECUTIVE INTELLIGENCE SUITE (HVIA v2.4.2 · Bilingual EN⇄AR Edition)
================================================================================
 Drop-in replacement for the previous app.py — all data logic preserved,
 presentation layer fully rebuilt with a professional design system.

 v2.4.2 CHANGE LOG (language toggle fix):
   · Language switching now uses an on_change callback (_on_lang_change),
     so the new language is applied BEFORE the page renders — no more
     "one-click-behind" flip-flop and no more needing to click twice.
   · Workspace & navigation selections migrate to the new language's
     widget keys inside the callback, so the user keeps their place.

 Setup:
   pip install streamlit pandas numpy plotly
   Place the "Sharnouby_Enterprise" data directory beside this file.
 Run:
   streamlit run app.py
================================================================================
"""

import os
import re
import textwrap
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ==============================================================================
# 1.b BILINGUAL CORE (v2.4.2) — English ⇄ Arabic, layout-safe by design
#     · Only TEXT swaps + per-element dir="rtl"  → zero dimension changes
#     · Language is resolved via an on_change callback so it's correct
#       from the very first line of the script on every rerun.
# ==============================================================================
if "lang" not in st.session_state:
    st.session_state["lang"] = "en"          # English is the default look
LANG = st.session_state["lang"]
IS_AR = (LANG == "ar")
RTL = ' dir="rtl"' if IS_AR else ""          # per-element text direction only


def _on_lang_change():
    """Callback: runs BEFORE the page reruns, so the new language is
    available from the very first line of the script (no one-click lag)."""
    new_lang = st.session_state["lang"]                 # already the NEW value here
    old_lang = st.session_state.get("_prev_lang", new_lang)
    if old_lang != new_lang:
        # keep the user's place: move saved workspace/nav selections
        # to the new language's widget keys before anything renders
        for _base in ("workspace", "nav_index"):
            _src = f"{_base}__{old_lang}"
            if _src in st.session_state:
                st.session_state[f"{_base}__{new_lang}"] = st.session_state[_src]
    st.session_state["_prev_lang"] = new_lang


# Data-category translations (departments, causes, cohorts, platforms, locations…)
CAT_AR = {
    # Machine / departments
    "Cutting": "القص", "Sewing": "الخياطة", "Finishing": "التشطيب",
    "Printing": "الطباعة", "Warehouse": "المخازن",
    # Quality root causes
    "Fabric defects": "عيوب القماش", "Sewing rework": "إعادة خياطة",
    "Printing misalignment": "خلع الطباعة", "Cutting errors": "أخطاء القص",
    "Curing Temperature Drift": "انحراف حرارة التثبيت",
    "Curing temperature drift": "انحراف حرارة التثبيت",
    # Customer cohorts
    "1. VIP Champions": "1. كبار العملاء VIP", "2. At-Risk Accounts": "2. عملاء معرضون للفقدان",
    "3. Potential Loyalists": "3. عملاء أوفياء محتملون", "4. Dormant Accounts": "4. حسابات خاملة",
    "VIP Champions": "كبار العملاء VIP", "At-Risk Accounts": "عملاء معرضون للفقدان",
    "Potential Loyalists": "عملاء أوفياء محتملون",
    # Marketing platforms
    "WhatsApp CRM": "واتساب CRM", "Email / SMS": "بريد / رسائل",
    "Google Ads": "إعلانات جوجل", "Meta / Facebook": "ميتا / فيسبوك", "Influencers": "المؤثرون",
    # Garment categories
    "T-Shirts": "تيشيرتات", "Jeans": "جينز", "Hoodies": "هوديز",
    "Jackets": "جاكيتات", "Homewear": "ملابس منزلية",
    # Supplier risk tiers
    "Critical SLA Risk (<50%)": "خطر تعاقدي حرج (أقل من 50%)", "Reliable Supplier": "مورّد موثوق",
    # Funnel stages
    "1. Sessions": "1. الزيارات", "2. Add to Cart": "2. إضافة للسلة",
    "3. Checkout": "3. إتمام الشراء", "4. Orders": "4. الطلبات",
    # Locations / nodes
    "Sidi Bishr Store": "متجر سيدي بشر", "Online Central": "المركز الأونلاين",
    "Buffer Warehouse": "مخزن التجميع", "Wholesale Desk": "مكتب الجملة",
    "Buffer Warehouse - Borg El Arab": "مخزن التجميع - برج العرب",
    "El-Sharnouby Wholesale Desk": "مكتب جملة الشارنوبي",
    "LEO MODA - Sidi Bishr Store": "ليو مودا - متجر سيدي بشر",
    "LEO MODA Online Store": "ليو مودا أونلاين",
    # Garment lines (transfer routes)
    "Homewear & Pajamas": "ملابس منزلية وبيجامات", "Kids Summer Sets": "أطقم صيفي للأطفال",
    "T-Shirts & Sweats": "تيشيرتات وسويتشيرت",
    # Simulator levers
    "Factory QC Recovery": "إنقاذ هدر المصنع", "At-Risk Win-Back": "استعادة العملاء المهددين",
    "Wholesale Discount Cap": "سقف خصم الجملة",
}


def T(en, ar):
    """Active-language string. English output is identical to v2.3.1."""
    return ar if IS_AR else en


def tr(v):
    """Translate one data-category label (falls back to the original)."""
    return CAT_AR.get(v, v) if IS_AR else v


def tr_col(s):
    """Translate a pandas Series of category labels."""
    return s.map(tr) if IS_AR else s


# ==============================================================================
# 1. PAGE SETUP
# ==============================================================================
st.set_page_config(
    page_title="ELSHARNOUBY | Leo Moda Executive Intelligence",
    page_icon="🧵",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==============================================================================
# 2. DESIGN SYSTEM — "MIDNIGHT ATELIER"
#    Palette: deep navy canvas · sky-blue data · teal growth · gold brand
#    Type:    Cinzel (brand display) · Plus Jakarta Sans (interface & data)
# ==============================================================================
CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&family=Cinzel:wght@600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    :root {
        --bg-0:#04070F; --bg-1:#071022;
        --surface:rgba(148,163,184,.05); --surface-2:rgba(148,163,184,.09);
        --border:rgba(148,163,184,.15); --border-strong:rgba(148,163,184,.30);
        --text:#F2F6FB; --muted:#93A6BD; --faint:#5C6E86;
        --accent:#4CC3FF; --accent-deep:#0EA5E9;
        --teal:#2DD4BF; --gold:#E8C57C; --gold-deep:#C99A4B;
        --danger:#FB7185; --warn:#FBBF24; --good:#34D399;
    }

    /* ---------- App shell ---------- */
    .stApp {
        background:
            radial-gradient(1100px 640px at 88% -12%, rgba(14,165,233,.10), transparent 62%),
            radial-gradient(900px 620px at -12% 112%, rgba(45,212,191,.055), transparent 55%),
            linear-gradient(180deg, var(--bg-1) 0%, var(--bg-0) 100%);
        background-attachment: fixed;
        color: var(--text);
        font-family:'Plus Jakarta Sans', sans-serif;
    }
    [data-testid="stHeader"] { background: transparent !important; border-bottom: none !important; }
    [data-testid="stToolbar"] { visibility: hidden; }
    [data-testid="stFooter"] { display: none; }
    .block-container { padding: 1.3rem 2.1rem 2.6rem; max-width: 1520px; }

    ::-webkit-scrollbar { width: 9px; height: 9px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(148,163,184,.22); border-radius: 8px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(148,163,184,.38); }

    h1, h2, h3 { color: var(--text); letter-spacing: .2px; }
    a { color: var(--accent); }

    /* ---------- Brand hero ---------- */
    .hero {
        position: relative; overflow: hidden;
        border: 1px solid var(--border); border-radius: 20px;
        background: linear-gradient(115deg, rgba(23,42,84,.55) 0%, rgba(7,16,34,.88) 46%, rgba(4,7,15,.94) 100%);
        padding: 24px 30px 22px; margin-bottom: 20px;
        box-shadow: 0 18px 44px rgba(2,6,17,.5);
    }
    .hero::before {
        content: ""; position: absolute; inset: 0; pointer-events: none;
        background: radial-gradient(640px 220px at 10% -10%, rgba(76,195,255,.13), transparent 62%);
    }
    .hero-hairline {
        position: absolute; top: 0; left: 0; right: 0; height: 2px;
        background: linear-gradient(90deg, transparent 4%, var(--gold-deep) 28%, var(--gold) 46%, var(--accent) 72%, transparent 96%);
    }
    .hero-row { display: flex; align-items: center; gap: 18px; position: relative; }
    .hero-mono {
        font-family:'Cinzel', serif; font-weight: 800; font-size: 21px; letter-spacing: 1px;
        color: #0B1220; background: linear-gradient(135deg, #F0D9A6 0%, #C99A4B 100%);
        border-radius: 15px; width: 58px; height: 58px; flex-shrink: 0;
        display: flex; align-items: center; justify-content: center;
        box-shadow: 0 10px 26px rgba(201,154,75,.30), inset 0 1px 0 rgba(255,255,255,.4);
    }
    .hero-title {
        font-family:'Cinzel', serif; font-size: 25px; font-weight: 800;
        letter-spacing: 3px; text-transform: uppercase; color: #F8FAFC; margin: 0; line-height: 1.2;
    }
    .hero-title .gold { color: var(--gold); }
    .hero-sub {
        font-size: 11.5px; color: var(--muted); letter-spacing: 2.2px;
        text-transform: uppercase; font-weight: 600; margin-top: 4px;
    }
    .hero-chips { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 15px; position: relative; }
    .chip {
        font-size: 11px; font-weight: 700; letter-spacing: .5px; color: #C7D5E8;
        background: rgba(148,163,184,.08); border: 1px solid var(--border);
        padding: 5px 13px; border-radius: 999px; white-space: nowrap;
    }
    .chip b { color: var(--accent); font-weight: 800; }
    .chip.live { color: #D9F5E9; }
    .chip.live::before { content: "●"; color: var(--good); margin-right: 7px; font-size: 9px; vertical-align: 1px; }

    /* ---------- Plain-English clarity layer ---------- */
    .kpi-plain {
        display:flex; gap:9px; align-items:flex-start; margin-top:11px;
        padding:9px 12px; border-radius:10px;
        background:rgba(76,195,255,.055); border:1px dashed rgba(76,195,255,.25);
        font-size:12px; line-height:1.7; color:#C3D8EC; font-weight:600;
    }
    .kpi-plain .ptag {
        flex-shrink:0; font-size:9px; font-weight:800; color:#7FD4FF; margin-top:2px;
        border:1px solid rgba(76,195,255,.4); background:rgba(76,195,255,.10);
        border-radius:999px; padding:2px 9px; letter-spacing:.8px; text-transform:uppercase;
        white-space:nowrap;
    }
    .kpi-plain > span:last-child { min-width:0; overflow-wrap:anywhere; }
    .legend-row {
        display:flex; flex-wrap:wrap; gap:8px 14px; align-items:center;
        margin:0 0 14px; padding:10px 16px;
        border:1px solid var(--border); border-radius:12px; background:var(--surface);
        font-size:11.5px; font-weight:700; color:#C4D3E6; letter-spacing:.4px;
    }
    .legend-row .lg { display:inline-flex; align-items:center; gap:7px; }
    .legend-row .dot { width:9px; height:9px; border-radius:50%; flex-shrink:0; }
    .legend-row .sep { width:1px; height:15px; background:var(--border); }
    .plain-box {
        display:flex; gap:11px; align-items:flex-start; margin:10px 0 16px;
        padding:11px 15px; border-radius:12px;
        border:1px solid rgba(232,197,124,.28);
        background:linear-gradient(90deg, rgba(232,197,124,.07), rgba(232,197,124,.015));
        font-size:12.6px; line-height:1.7; color:#E5DCC2; font-weight:600;
    }
    .plain-box .pb-ic {
        flex-shrink:0; width:25px; height:25px; border-radius:8px; margin-top:1px;
        display:flex; align-items:center; justify-content:center;
        background:rgba(232,197,124,.15); color:var(--gold); font-weight:800; font-size:13px;
    }
    .plain-box > span:last-child { min-width:0; overflow-wrap:anywhere; }
    .plain-box b { color:#F5E9C8; }
    .gl-item { display:flex; gap:14px; padding:9px 2px; border-bottom:1px dashed var(--border); }
    .gl-item:last-child { border-bottom:none; }
    .gl-term {
        flex-shrink:0; width:215px; font-size:11px; font-weight:800; letter-spacing:.6px;
        text-transform:uppercase; color:var(--gold); padding-top:2px;
    }
    .gl-def { min-width:0; font-size:12.6px; color:#BCCCDF; line-height:1.65; overflow-wrap:anywhere; }
    .side-flabel {
        font-size:10px; font-weight:800; letter-spacing:1.6px; text-transform:uppercase;
        color:#A9BAD2; margin:12px 0 3px;
    }

    /* ---------- Text overflow safety ---------- */
    .hero, .app-head, .insight, .note, .kpi, .foot, .legend-row, .gl-item { overflow-wrap: anywhere; }
    .hero-row > div:last-child, .app-head > div:last-child { min-width:0; }
    .note > div:last-child { min-width:0; flex:1; }

    /* ---------- Section header (per app) ---------- */
    .app-head {
        display: flex; gap: 16px; align-items: center;
        padding: 16px 22px; margin: 6px 0 16px;
        border: 1px solid var(--border); border-radius: 16px;
        background: linear-gradient(120deg, rgba(76,195,255,.08) 0%, rgba(45,212,191,.035) 48%, transparent 100%);
    }
    .app-num {
        font-family:'Cinzel', serif; font-weight: 800; font-size: 18px; color: #0B1220;
        background: linear-gradient(135deg, #F0D9A6, #C99A4B);
        width: 50px; height: 50px; border-radius: 13px; flex-shrink: 0;
        display: flex; align-items: center; justify-content: center;
        box-shadow: 0 8px 20px rgba(201,154,75,.25);
    }
    .app-kicker { font-size: 10px; font-weight: 800; letter-spacing: 2.4px; color: var(--gold); text-transform: uppercase; }
    .app-title { font-size: 18.5px; font-weight: 800; color: #F5F9FD; margin-top: 2px; }
    .app-sub { font-size: 12.5px; color: var(--muted); margin-top: 2px; }

    /* ---------- Executive KPI cards ---------- */
    .kpi-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; margin: 4px 0 20px; }
    @media (max-width: 1150px) { .kpi-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
    @media (max-width: 740px)  { .kpi-grid { grid-template-columns: 1fr; } }
    .kpi {
        position: relative; overflow: hidden; min-width: 0; height: 100%;
        background: linear-gradient(160deg, rgba(148,163,184,.075) 0%, rgba(148,163,184,.02) 100%);
        border: 1px solid var(--border); border-radius: 16px; padding: 16px 18px 14px;
        transition: transform .22s ease, border-color .22s ease, box-shadow .22s ease;
    }
    .kpi:hover { transform: translateY(-2px); border-color: var(--border-strong); box-shadow: 0 16px 36px rgba(2,6,17,.55); }
    .kpi::before { content: ""; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: var(--tone, var(--accent)); opacity: .85; }
    .kpi-top { display: flex; justify-content: space-between; align-items: center; gap: 10px; }
    .kpi-label {
        font-size: 10.5px; font-weight: 800; letter-spacing: 1.4px;
        text-transform: uppercase; color: var(--muted);
    }
    .kpi-chip {
        font-size: 9.5px; font-weight: 800; letter-spacing: .8px; text-transform: uppercase;
        padding: 3px 10px; border-radius: 999px; white-space: nowrap;
        color: var(--tone, var(--accent));
        background: color-mix(in srgb, var(--tone, var(--accent)) 13%, transparent);
        border: 1px solid color-mix(in srgb, var(--tone, var(--accent)) 38%, transparent);
    }
    .kpi-value {
        font-size: 29px; font-weight: 800; color: #F8FAFC; letter-spacing: .3px;
        margin-top: 10px; line-height: 1.1; font-variant-numeric: tabular-nums;
    }
    .kpi-value small { font-size: 15px; font-weight: 700; color: var(--muted); margin-left: 2px; }
    .kpi-sub { font-size: 12px; color: var(--muted); margin-top: 5px; font-weight: 600; }
    .kpi-sub b { color: #CBD9EA; }
    .kpi-note {
        margin-top: 12px; padding-top: 10px; border-top: 1px dashed var(--border);
        font-size: 11.6px; line-height: 1.6; color: #AAB9CE;
    }
    .kpi-note .dir { color: var(--gold); font-weight: 800; letter-spacing: .4px; }

    /* ---------- Panels (bordered containers) ---------- */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: linear-gradient(180deg, rgba(148,163,184,.055), rgba(148,163,184,.018)) !important;
        border: 1px solid var(--border) !important;
        border-radius: 16px !important;
        box-shadow: 0 12px 30px rgba(2,6,17,.38) !important;
    }

    .panel-title {
        display: flex; align-items: center; gap: 9px;
        font-size: 12.5px; font-weight: 800; letter-spacing: 1.2px; text-transform: uppercase;
        color: #CBD9EA; margin: 2px 0 12px;
    }
    .panel-title .pt-bar {
        width: 4px; height: 15px; border-radius: 3px; flex-shrink: 0;
        background: linear-gradient(180deg, var(--accent), var(--teal));
    }
    .panel-title .pt-tag {
        margin-left: auto; font-size: 9.5px; letter-spacing: 1px; color: var(--faint);
        border: 1px solid var(--border); border-radius: 999px; padding: 3px 10px; font-weight: 700;
    }

    /* ---------- Insight callouts ---------- */
    .insight {
        border: 1px solid var(--border); border-left: 3px solid var(--accent);
        background: linear-gradient(90deg, rgba(76,195,255,.06), rgba(76,195,255,.015));
        border-radius: 13px; padding: 14px 20px 13px; margin-bottom: 18px;
        font-size: 13px; color: #D6E1EF; line-height: 1.75;
    }
    .insight.warn  { border-left-color: var(--warn);  background: linear-gradient(90deg, rgba(251,191,36,.06), rgba(251,191,36,.012)); }
    .insight.good  { border-left-color: var(--teal);  background: linear-gradient(90deg, rgba(45,212,191,.06), rgba(45,212,191,.012)); }
    .insight .lead {
        display: block; font-size: 10.5px; font-weight: 800; letter-spacing: 1.8px;
        text-transform: uppercase; color: var(--accent); margin-bottom: 6px;
    }
    .insight.warn .lead { color: var(--warn); }
    .insight.good .lead { color: var(--teal); }
    .insight ul { margin: 2px 0 8px; padding-left: 4px; list-style: none; }
    .insight li { padding-left: 18px; position: relative; margin-top: 3px; }
    .insight li::before { content: "▸"; position: absolute; left: 0; color: var(--accent); font-size: 11px; }
    .insight.warn li::before { color: var(--warn); }
    .insight.good li::before { color: var(--teal); }
    .insight b { color: #F2F6FB; }
    .insight .directive {
        display: block; border-top: 1px dashed var(--border); margin-top: 9px; padding-top: 9px;
        font-size: 12.5px; color: #EAD9B0;
    }
    .insight .directive b { color: var(--gold); letter-spacing: .5px; }

    /* ---------- Note rows (alerts replacement) ---------- */
    .note {
        display: flex; gap: 12px; align-items: flex-start;
        border: 1px solid var(--border); border-radius: 12px;
        background: var(--surface); padding: 12px 14px; margin-bottom: 10px;
        font-size: 12.8px; line-height: 1.6; color: #D6E1EF;
    }
    .note .ic {
        width: 30px; height: 30px; border-radius: 9px; flex-shrink: 0;
        display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 14px;
    }
    .note b { color: #F2F6FB; }
    .note.danger { border-left: 3px solid var(--danger); } .note.danger .ic { background: rgba(251,113,133,.14); color: var(--danger); }
    .note.good   { border-left: 3px solid var(--good);   } .note.good .ic   { background: rgba(52,211,153,.14);  color: var(--good); }
    .note.info   { border-left: 3px solid var(--accent); } .note.info .ic   { background: rgba(76,195,255,.14);  color: var(--accent); }
    .note.warn   { border-left: 3px solid var(--warn);   } .note.warn .ic   { background: rgba(251,191,36,.14);  color: var(--warn); }

    /* ---------- Sidebar ---------- */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #060C1A 0%, #04070F 100%);
        border-right: 1px solid var(--border);
    }
    [data-testid="stSidebar"] .block-container { padding: 1.1rem 1.05rem 1.6rem; }
    .side-brand { display: flex; align-items: center; gap: 12px; padding: 4px 2px 16px; border-bottom: 1px solid var(--border); margin-bottom: 14px; }
    .side-mono {
        font-family:'Cinzel', serif; font-weight: 800; font-size: 16px; color: #0B1220;
        background: linear-gradient(135deg, #F0D9A6, #C99A4B);
        width: 42px; height: 42px; border-radius: 11px; flex-shrink: 0;
        display: flex; align-items: center; justify-content: center;
        box-shadow: 0 8px 20px rgba(201,154,75,.28);
    }
    .side-name { font-family:'Cinzel', serif; font-size: 16.5px; font-weight: 800; letter-spacing: 2.2px; color: #F4F8FD; }
    .side-tag  { font-size: 9.5px; font-weight: 700; letter-spacing: 1.6px; text-transform: uppercase; color: var(--muted); margin-top: 2px; }

    .side-label {
        display: flex; align-items: center; gap: 9px; margin: 16px 0 8px;
        font-size: 10px; font-weight: 800; letter-spacing: 1.8px; text-transform: uppercase; color: var(--faint);
    }
    .side-label::after { content: ""; flex: 1; height: 1px; background: var(--border); }

    [data-testid="stSidebar"] div[role="radiogroup"] { gap: 3px; }
    [data-testid="stSidebar"] div[role="radiogroup"] label {
        background: transparent; border: 1px solid transparent; border-radius: 10px;
        padding: 7.5px 11px; margin: 0; gap: 10px;
        color: #AEBDD1; font-size: 13px; font-weight: 600; transition: all .16s ease;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label:hover {
        background: rgba(76,195,255,.07); color: #EAF3FC;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
        background: linear-gradient(90deg, rgba(76,195,255,.16), rgba(76,195,255,.04));
        border-color: rgba(76,195,255,.42); color: #F2F9FF; font-weight: 700;
    }
    .side-foot { margin-top: 18px; padding-top: 12px; border-top: 1px solid var(--border); font-size: 10.5px; color: var(--faint); letter-spacing: 1px; line-height: 1.7; }

    /* ---------- Tabs ---------- */
    [data-testid="stTabs"] div[role="tablist"] {
        gap: 6px; background: rgba(148,163,184,.045);
        border: 1px solid var(--border); border-radius: 14px; padding: 6px;
    }
    [data-testid="stTabs"] div[role="tab"] {
        background: transparent; border-radius: 10px; padding: 8.5px 18px;
        color: var(--muted); font-weight: 700; font-size: 13.5px; letter-spacing: .3px;
    }
    [data-testid="stTabs"] div[role="tab"]:hover { color: #DCE9F7; background: rgba(76,195,255,.06); }
    [data-testid="stTabs"] div[role="tab"][aria-selected="true"] {
        color: #0B1220 !important; background: linear-gradient(135deg, #EAF7FF, #BFE4FF) !important;
        font-weight: 800;
    }
    [data-testid="stTabs"] hr { display: none; }

    /* ---------- Buttons ---------- */
    .stDownloadButton > button, .stButton > button {
        background: linear-gradient(135deg, #0EA5E9, #0369A1) !important;
        color: #FFFFFF !important; border: none !important; border-radius: 11px !important;
        font-weight: 800 !important; font-size: 13px !important; letter-spacing: .3px;
        padding: 10px 18px !important;
        box-shadow: 0 10px 26px rgba(14,165,233,.28) !important;
        transition: transform .18s ease, filter .18s ease;
    }
    .stDownloadButton > button:hover, .stButton > button:hover {
        transform: translateY(-1px); filter: brightness(1.09);
    }

    /* ---------- Inputs ---------- */
    [data-testid="stMultiSelect"] [role="group"],
    [data-testid="stSelectbox"] [role="group"],
    [data-testid="stSelectbox"] > div > div {
        background: rgba(148,163,184,.06) !important;
        border: 1px solid var(--border) !important; border-radius: 11px !important;
        color: #E4EDF7 !important; min-height: 43px;
    }
    [data-testid="stMultiSelect"] input,
    [data-testid="stSelectbox"] input { color: #E4EDF7 !important; }
    span[data-tag] {
        background: rgba(76,195,255,.16) !important;
        border: 1px solid rgba(76,195,255,.38) !important;
        border-radius: 8px !important;
    }
    span[data-tag] > span { color: #E8F4FF !important; font-weight: 600; }
    [data-testid="stDateInput"] input,
    [data-testid="stDateInput"] button {
        background: rgba(148,163,184,.06) !important;
        border: 1px solid var(--border) !important; border-radius: 11px !important;
        color: #E4EDF7 !important;
    }

    /* ---------- Slider ---------- */
    [data-testid="stSlider"] [data-testid="stSliderThumbValue"] p {
        color: var(--accent); font-weight: 800;
    }

    /* ---------- Metrics ---------- */
    div[data-testid="stMetric"] {
        background: rgba(148,163,184,.05);
        border: 1px solid var(--border); border-radius: 14px;
        padding: 13px 16px 11px;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.42rem; font-weight: 800; color: #F5F9FD;
        font-variant-numeric: tabular-nums; letter-spacing: .2px;
    }
    div[data-testid="stMetricLabel"] p {
        font-size: .72rem; font-weight: 800; color: var(--muted);
        text-transform: uppercase; letter-spacing: .9px;
    }
    div[data-testid="stMetricDelta"] { font-size: .8rem; font-weight: 700; }

    /* ---------- DataFrames ---------- */
    [data-testid="stDataFrame"] {
        border: 1px solid var(--border); border-radius: 14px; overflow: hidden;
        box-shadow: 0 10px 26px rgba(2,6,17,.35);
    }

    /* ---------- Footer ---------- */
    .foot {
        margin-top: 34px; padding-top: 16px; border-top: 1px solid var(--border);
        display: flex; justify-content: space-between; flex-wrap: wrap; gap: 6px;
        color: var(--faint); font-size: 11px; letter-spacing: 1.1px; text-transform: uppercase; font-weight: 600;
    }
    .foot .fg { color: var(--gold-deep); }

    /* ---------- v2.4 Bilingual layer — ADDITIVE RTL rules only ---------- */
    [dir="rtl"] { direction: rtl; text-align: right; }
    [dir="rtl"], [dir="rtl"] * {
        font-family: 'Cairo', 'Plus Jakarta Sans', sans-serif;
        letter-spacing: 0 !important;
    }
    [dir="rtl"] .insight li { padding-left: 0; padding-right: 18px; }
    [dir="rtl"] .insight li::before { left: auto; right: 0; }
    [dir="rtl"] .panel-title .pt-tag { margin-left: 0; margin-right: auto; }
    [dir="rtl"] .insight, [dir="rtl"] .note {
        border-left-width: 1px; border-right-width: 3px; border-right-style: solid;
    }
    [dir="rtl"] .insight       { border-right-color: var(--accent); }
    [dir="rtl"] .insight.warn  { border-right-color: var(--warn); }
    [dir="rtl"] .insight.good  { border-right-color: var(--teal); }
    [dir="rtl"] .note.danger { border-right-color: var(--danger); }
    [dir="rtl"] .note.good   { border-right-color: var(--good); }
    [dir="rtl"] .note.info   { border-right-color: var(--accent); }
    [dir="rtl"] .note.warn   { border-right-color: var(--warn); }
    [data-testid="stSidebar"] div[role="radiogroup"].horizontal {
        display: flex; flex-direction: row; gap: 6px;
    }

    /* Hide Streamlit chrome noise */
    #MainMenu { visibility: hidden; }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ==============================================================================
# 3. UI HELPER LIBRARY
# ==============================================================================
PAL = {
    "accent": "#4CC3FF", "accent2": "#60A5FA", "indigo": "#818CF8",
    "teal": "#2DD4BF", "deep_teal": "#2A9D8F",
    "danger": "#FB7185", "red": "#EF4444", "warn": "#FBBF24",
    "good": "#34D399", "muted": "#93A6BD", "text": "#F2F6FB",
}
PLOT_FONT = dict(family=("Cairo, Plus Jakarta Sans" if IS_AR else "Plus Jakarta Sans"),
                 size=12.5, color="#DCE6F2")
HOVER_LABEL = dict(bgcolor="#0A1428", bordercolor="rgba(76,195,255,.45)",
                   font=dict(color="#EAF2FB", family="Plus Jakarta Sans", size=12))
CHART_CONFIG = {"displayModeBar": False}


def panel_title(text, tag=None):
    """Professional panel header with accent bar and optional corner tag."""
    tag_html = f'<span class="pt-tag">{tag}</span>' if tag else ""
    st.markdown(f'<div class="panel-title"{RTL}><span class="pt-bar"></span>{text}{tag_html}</div>',
                unsafe_allow_html=True)


def app_head(num, kicker, title, sub):
    """Section banner shown at the top of every module."""
    st.markdown(f"""
    <div class="app-head"{RTL}>
        <div class="app-num">{num}</div>
        <div>
            <div class="app-kicker">{kicker}</div>
            <div class="app-title">{title}</div>
            <div class="app-sub">{sub}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def kpi_card(label, value, unit, chip, tone, sub, directive, plain=None):
    """Executive KPI card → returns HTML string (composed into a grid)."""
    unit_html = f"<small>{unit}</small>" if unit else ""
    plain_html = (f'<div class="kpi-plain"><span class="ptag">{T("What it means", "يعني إيه؟")}</span>'
                  f'<span>{plain}</span></div>') if plain else ""
    return f"""
    <div class="kpi"{RTL} style="--tone:{tone};">
        <div class="kpi-top"><span class="kpi-label">{label}</span><span class="kpi-chip">{chip}</span></div>
        <div class="kpi-value">{value}{unit_html}</div>
        <div class="kpi-sub">{sub}</div>
        {plain_html}
        <div class="kpi-note"><span class="dir">{T("Directive ▸ ", "التوصية ▸ ")}</span>{directive}</div>
    </div>
    """


def _compact_html(html):
    """Collapse whitespace-only lines so markdown-it keeps the payload
    as ONE raw-HTML block (blank lines terminate Streamlit HTML blocks)."""
    return re.sub(r'[ \t]*\n[ \t]*\n+', '\n', html).strip()


def render_kpi_grid(cards):
    html = _compact_html("".join(cards))
    st.markdown(f'<div class="kpi-grid">{html}</div>', unsafe_allow_html=True)


def insight(title, bullets, directive, tone="info"):
    """Structured diagnostic callout: lead → bullets → directive."""
    cls = {"info": "", "warn": "warn", "good": "good"}.get(tone, "")
    lis = "".join(f"<li>{b}</li>" for b in bullets)
    st.markdown(_compact_html(f"""
    <div class="insight {cls}"{RTL}>
        <span class="lead">{title}</span>
        <ul>{lis}</ul>
        <span class="directive"><b>{T("DIRECTIVE", "التوصية")}</b> — {directive}</span>
    </div>
    """), unsafe_allow_html=True)


def note(tone, icon, html):
    """Compact alert row (replaces default st.info / st.error styling)."""
    st.markdown(f'<div class="note {tone}"{RTL}><div class="ic">{icon}</div><div>{html}</div></div>',
                unsafe_allow_html=True)


def plain_box(text):
    """Plain-English caption placed under charts & tables."""
    st.markdown(f'<div class="plain-box"{RTL}><span class="pb-ic">i</span>'
                f'<span><b>{T("In plain terms:", "ببساطة:")}</b> {text}</span></div>', unsafe_allow_html=True)


def glossary(terms):
    """Business-term explainer — collapsed by default. Items: (term, definition)."""
    rows = "".join(
        f'<div class="gl-item"><div class="gl-term">{t}</div>'
        f'<div class="gl-def">{d}</div></div>'
        for t, d in terms)
    with st.expander(T("📖 Business Term Glossary", "📖 قاموس مصطلحات الأعمال")):
        st.markdown(_compact_html(f'<div{RTL}>{rows}</div>'), unsafe_allow_html=True)


def status_legend_html():
    """Status color legend — translated for the active language."""
    return f"""
<div class="legend-row">
    <span class="lg"><span class="dot" style="background:var(--good)"></span>{T('On Track', 'على المسار')}</span>
    <span class="sep"></span>
    <span class="lg"><span class="dot" style="background:var(--warn)"></span>{T('Watch', 'تحت المراقبة')}</span>
    <span class="sep"></span>
    <span class="lg"><span class="dot" style="background:var(--danger)"></span>{T('Action Needed', 'يحتاج قرار')}</span>
    <span class="sep"></span>
    <span class="lg" style="color:var(--muted); font-weight:600;">{T('Hover any chart for exact numbers', 'مرّر على أي رسم لرؤية الأرقام بدقة')}</span>
</div>
"""


def theme_fig(fig, height=340, l=20, r=20, t=24, b=44, legend=False,
              ytitle=None, xtitle=None):
    """Single source of truth for every chart in the suite."""
    fig.update_layout(
        template="none",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=PLOT_FONT, height=height,
        margin=dict(t=t, b=b, l=l, r=r),
        hoverlabel=HOVER_LABEL,
        showlegend=legend,
    )
    if legend:
        fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02,
                                      xanchor="left", x=0, font=dict(size=11, color=PAL["muted"])))
    fig.update_xaxes(gridcolor="rgba(255,255,255,.07)", linecolor="rgba(255,255,255,.18)",
                     zeroline=False, tickfont=dict(size=11.5, color="#C9D6E6"),
                     automargin=True)
    fig.update_yaxes(gridcolor="rgba(255,255,255,.07)", linecolor="rgba(255,255,255,.18)",
                     zeroline=False, tickfont=dict(size=11.5, color="#C9D6E6"),
                     automargin=True)
    if xtitle:
        fig.update_xaxes(title=dict(text=xtitle, standoff=14, font=dict(size=11.5, color=PAL["muted"])))
    if ytitle:
        fig.update_yaxes(title=dict(text=ytitle, standoff=12, font=dict(size=11.5, color=PAL["muted"])))
    return fig

# ==============================================================================
# 4. DATA ENGINE
# ==============================================================================
def find_dataset(filename):
    paths = [os.path.join("Sharnouby_Enterprise", filename), filename]
    for p in paths:
        if os.path.exists(p):
            return p
    return None


@st.cache_data(show_spinner="Auditing Leo Moda Operational Data Engine...")
def load_enterprise_data():
    schema = {
        'sales': 'Sales_Transactions.csv', 'products': 'Product_Master.csv',
        'locations': 'Locations.csv', 'customers': 'Customers.csv',
        'inventory': 'Inventory_History.csv', 'prod_orders': 'Production_Orders.csv',
        'printing': 'Printing_Batches.csv', 'quality': 'Quality.csv',
        'purchases': 'Purchase_Orders.csv', 'marketing': 'Marketing.csv',
        'traffic': 'Web_Traffic_Daily.csv', 'cs': 'Customer_Service.csv',
        'downtime': 'Machine_Downtime.csv'
    }
    db = {}
    for key, name in schema.items():
        fp = find_dataset(name)
        db[key] = pd.read_csv(fp) if fp else pd.DataFrame()

    if not db['sales'].empty:
        df = db['sales'].copy()
        df['Order_Date'] = pd.to_datetime(df['Order_Date'], errors='coerce')
        df = df[df['Order_Date'].notna()].copy()
        df['YearMonth'] = df['Order_Date'].dt.to_period('M').astype(str)

        if not db['locations'].empty and 'Governorate' not in df.columns:
            loc_cols = [c for c in ['Location_ID', 'Location_Name', 'Channel', 'Location_Type', 'Governorate']
                        if c in db['locations'].columns]
            df = df.merge(db['locations'][loc_cols], on='Location_ID', how='left', suffixes=('', '_loc'))

        if not db['products'].empty and 'Product_Family' not in df.columns:
            p_cols = [c for c in ['Product_ID', 'SKU', 'Product_Name', 'Product_Family']
                      if c in db['products'].columns]
            m_key = 'Product_ID' if 'Product_ID' in df.columns and 'Product_ID' in p_cols else 'SKU'
            if m_key in df.columns:
                df = df.merge(db['products'][p_cols].drop_duplicates(subset=[m_key]), on=m_key,
                              how='left', suffixes=('', '_prod'))

        if 'Returned' in df.columns:
            df['Is_Returned'] = df['Returned'].astype(str).str.strip().str.upper().isin(['YES', 'TRUE', '1'])
        else:
            df['Is_Returned'] = df.get('Refund_Value_EGP', pd.Series(0, index=df.index)).fillna(0) > 0

        db['sales'] = df
        db['valid_sales'] = df[~df['Is_Returned']].copy()
        db['returned_sales'] = df[df['Is_Returned']].copy()

    if not db['purchases'].empty:
        po = db['purchases'].copy()
        po['Promised_Date'] = pd.to_datetime(po['Promised_Date'], errors='coerce')
        po['Actual_Receipt_Date'] = pd.to_datetime(po['Actual_Receipt_Date'], errors='coerce')
        po['Is_On_Time'] = po['Actual_Receipt_Date'] <= po['Promised_Date']
        po['Delay_Days'] = (po['Actual_Receipt_Date'] - po['Promised_Date']).dt.days.clip(lower=0)
        po['Total_Spend_EGP'] = po['Ordered_Qty'] * po['Unit_Cost_EGP']
        db['purchases'] = po

    return db


db = load_enterprise_data()

if db['sales'].empty:
    st.error(T("Data files not found — verify that the Sharnouby_Enterprise directory exists beside app.py.",
               "ملفات البيانات غير موجودة — تأكد من وجود مجلد Sharnouby_Enterprise بجانب app.py."))
    st.stop()

valid_sales = db['valid_sales']
returned_sales = db['returned_sales']
sales_all = db['sales']

# ---- Downtime intelligence (computed — replaces previously hardcoded figures)
dt_total_hours = db['downtime']['Downtime_Hours'].sum() if not db['downtime'].empty else 0
dt_unplanned_share = None
if not db['downtime'].empty:
    for cand in ('Downtime_Type', 'Type', 'Category', 'Mode', 'Reason'):
        if cand in db['downtime'].columns:
            mask = db['downtime'][cand].astype(str).str.contains('unplanned|breakdown', case=False, na=False)
            if db['downtime']['Downtime_Hours'][mask].sum() > 0:
                dt_unplanned_share = (db['downtime']['Downtime_Hours'][mask].sum() / dt_total_hours * 100) if dt_total_hours else None
            break

# ---- CS support mix (computed when topic column exists)
cs_size_share = None
if not db['cs'].empty:
    for cand in ('Topic', 'Category', 'Query_Type', 'Issue_Type', 'Subject'):
        if cand in db['cs'].columns:
            mask = db['cs'][cand].astype(str).str.contains('size|fit', case=False, na=False)
            if mask.any():
                cs_size_share = mask.mean() * 100
            break

# ==============================================================================
# 5. SIDEBAR — BRAND, NAVIGATION & FILTERS
# ==============================================================================
with st.sidebar:
    st.markdown("""
    <div class="side-brand">
        <div class="side-mono">LM</div>
        <div>
            <div class="side-name">LEO MODA</div>
            <div class="side-tag">Sharnouby Enterprise</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- v2.4.2 Language toggle (English ⇄ العربية) — FIXED via on_change callback ---
    st.markdown('<div class="side-flabel">Language · اللغة</div>', unsafe_allow_html=True)
    st.radio("Language · اللغة", ["en", "ar"],          # label ثابت (مخفي أصلًا)
             format_func=lambda v: "English" if v == "en" else "العربية",
             horizontal=True, key="lang", label_visibility="collapsed",
             on_change=_on_lang_change)                  # ← ✨ ده هو الفكس
    # Sync globals from session_state right after the widget callback has fired.
    LANG = st.session_state["lang"]
    IS_AR = (LANG == "ar")
    RTL = ' dir="rtl"' if IS_AR else ""
    PLOT_FONT["family"] = "Cairo, Plus Jakarta Sans" if IS_AR else "Plus Jakarta Sans"
    st.session_state["_prev_lang"] = LANG

    st.markdown(f'<div class="side-flabel">{T("Workspace", "مساحة العمل")}</div>',
                unsafe_allow_html=True)
    # Language-neutral values + per-language keys: switching language keeps
    # the user in the same workspace instead of resetting to the first option.
    view_portal = st.radio(T("Workspace", "مساحة العمل"), ["exec", "portal"],
                           format_func=lambda v: (T("Executive Suite", "المجموعة التنفيذية") if v == "exec"
                                                  else T("Client & Partner Portal", "بوابة العملاء والشركاء")),
                           label_visibility="collapsed", key=f"workspace__{LANG}")

    st.markdown(f'<div class="side-label">{T("Operating Modules", "الوحدات التشغيلية")}</div>', unsafe_allow_html=True)

    NAV = {
        "01 · " + T("Financials", "المالية"):          "App 01",
        "02 · " + T("Inventory", "المخزون"):          "App 02",
        "03 · " + T("Customers", "العملاء"):          "App 03",
        "04 · " + T("Factory", "المصنع"):            "App 04",
        "05 · " + T("Marketing", "التسويق"):         "App 05",
        "06 · " + T("Branches", "الفروع"):           "App 06",
        "07 · " + T("Suppliers", "الموردين"):        "App 07",
        "08 · " + T("Profit Simulator", "محاكي الأرباح"): "App 08",
    }
    if view_portal == "exec":
        # Stable integer options + per-language key: switching language no
        # longer bounces the user back to App 01; the active module is preserved.
        nav_labels = list(NAV.keys())
        nav_label = st.radio(T("Quick Navigation", "التنقل السريع"), list(range(len(nav_labels))),
                             format_func=lambda i: nav_labels[i],
                             label_visibility="collapsed", key=f"nav_index__{LANG}")
        active_app = NAV[nav_labels[nav_label]]
    else:
        st.markdown(f'<div class="side-foot"{RTL}>{T("Partner self-service modules:<br>· Loyalty Account 360<br>· Live Branch Stock<br>· Size Recommender", "وحدات الخدمة الذاتية للشركاء:<br>· حساب الولاء 360<br>· مخزون الفروع المباشر<br>· مستشار المقاسات")}</div>',
                    unsafe_allow_html=True)
        active_app = "Portal"

    st.markdown(f'<div class="side-label">{T("Operational Filters", "فلاتر التشغيل")}</div>', unsafe_allow_html=True)

    min_date = valid_sales['Order_Date'].min().date()
    max_date = valid_sales['Order_Date'].max().date()
    st.markdown(f'<div class="side-flabel">{T("Reporting Period", "فترة التقرير")}</div>', unsafe_allow_html=True)
    date_filter = st.date_input(T("Date Period", "الفترة الزمنية"), value=(min_date, max_date),
                                min_value=min_date, max_value=max_date,
                                label_visibility="collapsed", key="f_date")

    channel_list = sorted(valid_sales['Channel'].dropna().unique().tolist()) if 'Channel' in valid_sales.columns else []
    st.markdown(f'<div class="side-flabel">{T("Sales Channels", "قنوات البيع")}</div>', unsafe_allow_html=True)
    selected_channels = st.multiselect(T("Sales Channels", "قنوات البيع"), channel_list, default=channel_list,
                                       label_visibility="collapsed", key="f_channels")

    family_list = sorted(valid_sales['Product_Family'].dropna().unique().tolist()) if 'Product_Family' in valid_sales.columns else []
    st.markdown(f'<div class="side-flabel">{T("Garment Lines", "خطوط الملابس")}</div>', unsafe_allow_html=True)
    selected_families = st.multiselect(T("Garment Lines", "خطوط الملابس"), family_list, default=family_list,
                                       label_visibility="collapsed", key="f_families")

    st.markdown(f"""
    <div class="side-foot"{RTL}>
        <b style="color:#8FA3BF;">{T('HVIA SUITE v2.4.2 · BILINGUAL EDITION', 'سويت HVIA الإصدار 2.4.2 · نسخة ثنائية اللغة')}</b><br>
        {T('Built for executives and everyday readers alike —<br>plain numbers, plain words, zero jargon.',
           'مصمم للمديرين والقارئ العادي على حد سواء —<br>أرقام واضحة، كلمات بسيطة، بدون تعقيد.')}<br>
        © {pd.Timestamp.now().year} {T('El-Sharnouby Group', 'مجموعة الشارنوبي')}
    </div>
    """, unsafe_allow_html=True)

if len(date_filter) == 2:
    f_start, f_end = pd.to_datetime(date_filter[0]), pd.to_datetime(date_filter[1])
else:
    f_start, f_end = pd.to_datetime(min_date), pd.to_datetime(max_date)


def _apply_filters(df):
    """Date + channel + family filter, tolerant to missing enrichment columns."""
    m = (df['Order_Date'] >= f_start) & (df['Order_Date'] <= f_end)
    if 'Channel' in df.columns and selected_channels:
        m &= df['Channel'].isin(selected_channels)
    if 'Product_Family' in df.columns and selected_families:
        m &= df['Product_Family'].isin(selected_families)
    return df[m]


f_valid = _apply_filters(valid_sales)
f_all = _apply_filters(sales_all)
f_returns = _apply_filters(returned_sales)

if f_valid.empty:
    st.warning(T("No records match the current filters — adjust the date range or channels.",
                 "لا توجد بيانات مطابقة للفلاتر الحالية — عدّل الفترة الزمنية أو القنوات."))
    st.stop()

# ==============================================================================
# 6. BRAND HERO HEADER
# ==============================================================================
st.markdown(f"""
<div class="hero">
    <div class="hero-hairline"></div>
    <div class="hero-row">
        <div class="hero-mono">LM</div>
        <div>
            <div class="hero-title">{T('El-Sharnouby Group', 'مجموعة الشارنوبي')} <span class="gold">— {T('Leo Moda', 'ليو مودا')}</span></div>
            <div class="hero-sub"{RTL}>{T('Integrated Apparel Manufacturing &amp; Enterprise Intelligence Suite', 'مجموعة متكاملة لتصنيع الملابس وذكاء الأعمال')}</div>
        </div>
    </div>
    <div class="hero-chips">
        <span class="chip live">{T('HVIA LIVE ENGINE', 'محرك HVIA المباشر')}</span>
        <span class="chip">{T('Period', 'الفترة')} · <b>{f_start:%b %d, %Y} → {f_end:%b %d, %Y}</b></span>
        <span class="chip">{T('Invoices', 'الفواتير')} · <b>{f_all['Invoice_ID'].nunique():,}</b></span>
        <span class="chip">{T('Channels', 'القنوات')} · <b>{len(selected_channels)}</b></span>
        <span class="chip">{T('Garment Lines', 'خطوط الملابس')} · <b>{len(selected_families)}</b></span>
    </div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# 7. EXECUTIVE COMMAND CENTER — NINE EXPLAINED SCORECARDS
# ==============================================================================
if view_portal == "exec":

    net_sales = f_valid['Net_Sales_EGP'].sum()
    gross_profit = f_valid['Gross_Profit_EGP'].sum()
    margin_pct = (gross_profit / net_sales * 100) if net_sales > 0 else 0

    ws_sales = f_valid[f_valid['Channel'] == 'Wholesale']['Net_Sales_EGP'].sum()
    ws_share = (ws_sales / net_sales * 100) if net_sales > 0 else 0
    ws_margin = (f_valid[f_valid['Channel'] == 'Wholesale']['Gross_Profit_EGP'].sum() / ws_sales * 100) if ws_sales > 0 else 0
    ret_sales = f_valid[f_valid['Channel'] == 'Retail']['Net_Sales_EGP'].sum()
    ret_margin = (f_valid[f_valid['Channel'] == 'Retail']['Gross_Profit_EGP'].sum() / ret_sales * 100) if ret_sales > 0 else 37.03

    refund_val = f_returns['Refund_Value_EGP'].sum()
    return_rate = (len(f_returns) / len(f_all) * 100) if len(f_all) > 0 else 0

    qc_loss = db['quality']['Estimated_Loss_EGP'].sum() if not db['quality'].empty else 0
    total_scrap_units = db['prod_orders']['Rejected_Qty'].sum() if not db['prod_orders'].empty else 0

    otd_reliability = (db['purchases']['Is_On_Time'].mean() * 100) if not db['purchases'].empty else 0
    blended_roas = (db['marketing']['Attributed_Revenue_EGP'].sum() / db['marketing']['Spend_EGP'].sum()) if not db['marketing'].empty else 0
    support_csat = db['cs']['CSAT_1_to_5'].mean() if not db['cs'].empty else 0

    st.markdown(_compact_html(f"""
    <div class="panel-title" style="font-size:14px; margin-top:4px;"{RTL}>
        <span class="pt-bar"></span>{T('Executive Command Center', 'مركز القيادة التنفيذي')}
        <span class="pt-tag" style="letter-spacing:.3px; text-transform:none; font-size:10.5px;">{T('The 9 numbers that run the business', 'الأرقام التسعة التي تدير الأعمال')}</span>
    </div>"""), unsafe_allow_html=True)
    st.markdown(status_legend_html(), unsafe_allow_html=True)
    with st.expander(T("🧭 How to read this suite", "🧭 كيف تقرأ هذه اللوحة")):
        st.markdown(_compact_html(f"""
        <div class="gl-item"{RTL}><div class="gl-term">{T('Status Colors', 'ألوان الحالة')}</div>
        <div class="gl-def">{T('Green = on track · Amber = watch closely · Red = decision needed.', 'أخضر = على المسار · أصفر = يراقب عن قرب · أحمر = مطلوب قرار.')}</div></div>
        <div class="gl-item"{RTL}><div class="gl-term">{T('Every Card', 'كل بطاقة')}</div>
        <div class="gl-def">{T('The number, its plain-English meaning, then the recommended directive.', 'الرقم، ثم معناه بلغة بسيطة، ثم التوصية المقترحة.')}</div></div>
        <div class="gl-item"{RTL}><div class="gl-term">{T('Charts &amp; Tables', 'الرسوم والجداول')}</div>
        <div class="gl-def">{T('Hover anything for exact values; every module also carries a plain-terms caption and a glossary.', 'مرّر على أي عنصر لرؤية القيم بدقة؛ كل وحدة تتضمن شرحًا مبسطًا وقاموس مصطلحات.')}</div></div>
        """), unsafe_allow_html=True)

    kpi_cards = [
        kpi_card(
            T("Net Realized Sales", "صافي المبيعات المحققة"), f"{net_sales/1e6:,.2f}", T("M EGP", "م ج"), T("Healthy", "ممتاز"), PAL["good"],
            T(f"<b>{f_valid['Invoice_ID'].nunique():,}</b> invoices · cash collected after discounts & returns",
              f"<b>{f_valid['Invoice_ID'].nunique():,}</b> فاتورة · النقد المحصّل بعد الخصومات والمرتجعات"),
            T("Maintain volume while shifting mix toward higher-margin direct channels.",
              "الحفاظ على حجم المبيعات مع توجيهه نحو القنوات المباشرة الأعلى هامشًا."),
            plain=T("This is the money that actually landed in the treasury after discounts and returns — the cash available to run the business.",
                    "دي الفلوس اللي دخلت الخزينة فعلًا بعد الخصومات والمرتجعات — النقد المتاح لتشغيل الأعمال.")
        ),
        kpi_card(
            T("Gross Profit Margin", "هامش الربح الإجمالي"), f"{margin_pct:.2f}", "%", T("Below Target", "تحت الهدف"), PAL["danger"],
            T(f"<b>{margin_pct - 22.0:+.2f}pp</b> vs 22% apparel benchmark — wholesale discounting is the compressor",
              f"<b>{margin_pct - 22.0:+.2f} نقطة</b> مقارنة بمعيار 22% للقطاع — خصومات الجملة هي الضاغط الأساسي"),
            T("Cap wholesale discounts at 20–22% to recover over +12M EGP.",
              "تحديد سقف خصومات الجملة عند 20-22% لاستعادة أكثر من 12 مليون جنيه."),
            plain=T("From every 100 EGP of sales, this is what remains after production cost — each extra point means more profit from the same volume.",
                    "من كل 100 جنيه مبيعات، ده المتبقي بعد تكلفة الإنتاج — كل نقطة إضافية تعني ربحًا أكبر من نفس الحجم.")
        ),
        kpi_card(
            T("Wholesale Volume Share", "حصة مبيعات الجملة"), f"{ws_share:.1f}", "%", T("Concentration Risk", "تركّز عالي"), PAL["danger"],
            T(f"<b>{ws_margin - ret_margin:+.2f}pp</b> margin gap vs Retail ({ws_margin:.1f}% vs {ret_margin:.1f}%)",
              f"<b>{ws_margin - ret_margin:+.2f} نقطة</b> فجوة هامش عن التجزئة ({ws_margin:.1f}% مقابل {ret_margin:.1f}%)"),
            T("Scale company retail stores to capture 37% margins.",
              "التوسع في متاجر التجزئة الخاصة بالشركة للحصول على هوامش 37%."),
            plain=T("The share of sales going to wholesale traders at discounted prices — big volume, but noticeably weaker margins than our own stores.",
                    "نسبة المبيعات الموجهة لتجار الجملة بأسعار مخفضة — حجم كبير لكن بهوامش أضعف بوضوح من متاجرنا."),
        ),
        kpi_card(
            T("Customer Refunds", "مرتجعات العملاء"), f"{refund_val/1e6:,.2f}", T("M EGP", "م ج"), T("Monitor", "مراقبة"), PAL["warn"],
            T(f"<b>{return_rate:.2f}%</b> return rate — sizing & fit is the leading driver",
              f"نسبة مرتجعات <b>{return_rate:.2f}%</b> — المقاسات والقياسات هي السبب الأول"),
            T("Standardize sizing blocks and launch the digital size calculator.",
              "توحيد جداول المقاسات وإطلاق حاسبة المقاسات الرقمية."),
            plain=T("The value of sales returned by customers — sizing & fit is the number-one reason, and this is revenue walking out the door.",
                    "قيمة المبيعات المرتجعة من العملاء — المقاسات هي السبب الأول، ودي إيرادات خرجت من البيت.")
        ),
        kpi_card(
            T("Factory Quality Waste", "هدر الجودة بالمصنع"), f"{qc_loss/1e6:,.2f}", T("M EGP", "م ج"), T("Critical", "حرج"), PAL["danger"],
            T(f"<b>{total_scrap_units:,.0f}</b> rejected units — direct manufacturing loss",
              f"<b>{total_scrap_units:,.0f}</b> قطعة مرفوضة — خسارة تصنيع مباشرة"),
            T("Calibrate curing dryer temperatures to eliminate thermal print failures.",
              "معايرة درجات حرارة أفران التثبيت للقضاء على أخطاء الطباعة الحرارية."),
            plain=T("The value of pieces the factory rejected for quality defects — material, labor and overhead already spent on unsellable goods.",
                    "قيمة القطع التي رفضها المصنع لعيوب الجودة — خامات وأجور وتكاليف أُنفقت بالفعل على بضاعة غير قابلة للبيع.")
        ),
        kpi_card(
            T("Supplier OTD Reliability", "التزام الموردين بالتسليم"), f"{otd_reliability:.1f}", "%", T("Critical", "حرج"), PAL["danger"],
            T(f"<b>{otd_reliability - 85.0:+.1f}pp</b> vs 85% safe operational threshold",
              f"<b>{otd_reliability - 85.0:+.1f} نقطة</b> مقارنة بعتبة الأمان التشغيلية 85%"),
            T("Enforce late penalties and reallocate 30% of POs to reliable vendors.",
              "تطبيق غرامات التأخير وتحويل 30% من أوامر الشراء لموردين موثوقين."),
            plain=T("The share of purchase orders delivered on the promised date — every late delivery means a stopped machine and an empty shelf.",
                    "نسبة أوامر الشراء التي تم تسليمها في التاريخ الموعود — كل تأخير يعني ماكينة متوقفة ورف فاضي.")
        ),
        kpi_card(
            T("Blended Marketing ROAS", "العائد على الإعلانات ROAS"), f"{blended_roas:.2f}", "x", T("Strength", "نقطة قوة"), PAL["good"],
            T("Powered by WhatsApp CRM — the highest-yield channel in the mix",
              "مدعوم بواتساب CRM — القناة الأعلى عائدًا في المزيج التسويقي"),
            T("Terminate unprofitable influencer spend; reallocate to Google & CRM.",
              "إيقاف إنفاق المؤثرين غير المربح وتحويله لإعلانات جوجل و CRM."),
            plain=T("How many pounds of sales came back for every pound spent on ads — above 3x is excellent, below 1x means the campaign is losing money.",
                    "كام جنيه مبيعات بيرجع مقابل كل جنيه إنفاق على الإعلانات — فوق 3x ممتاز، وتحت 1x يعني الحملة بتخسر فلوس.")
        ),
        kpi_card(
            T("Customer Satisfaction", "رضا العملاء"), f"{support_csat:.2f}", "/ 5.0", T("Stable", "مستقر"), PAL["accent"],
            (T(f"<b>{cs_size_share:.1f}%</b> of support tickets are size & fit queries",
               f"<b>{cs_size_share:.1f}%</b> من تذاكر الدعم استفسارات عن المقاسات") if cs_size_share
             else T("Size & fit remains the primary support topic",
                    "المقاسات والقياسات تظل الموضوع الأول في الدعم")),
            T("Embed interactive size finders on storefronts to cut inquiry volume.",
              "دمج مستشار مقاسات تفاعلي في المتاجر لتقليل حجم الاستفسارات."),
            plain=T("Average support satisfaction out of 5 stars — and most inquiries are about sizes and measurements.",
                    "متوسط رضا الدعم من 5 نجوم — ومعظم الاستفسارات عن المقاسات والقياسات.")
        ),
        kpi_card(
            T("Unplanned Factory Downtime", "توقف المصنع غير المخطط"), f"{dt_total_hours/1e3:,.1f}", T("K hrs", "ألف ساعة"),
            T("Schedule Discipline", "انتظام الجدول"), PAL["warn"],
            (T(f"<b>{dt_unplanned_share:.1f}%</b> of outages are unscheduled breakdowns",
               f"<b>{dt_unplanned_share:.1f}%</b> من ساعات التوقف أعطال مفاجئة غير مجدولة") if dt_unplanned_share
             else T("Unscheduled breakdowns dominate total outage hours",
                    "الأعطال غير المجدولة تهيمن على إجمالي ساعات التوقف")),
            T("Shift sewing & printing machines to scheduled preventive maintenance.",
              "نقل ماكينات الخياطة والطباعة إلى صيانة وقائية مجدولة."),
            plain=T("Hours machines stopped without a plan — every idle hour is production the factory never delivered.",
                    "ساعات توقفت فيها الماكينات بدون خطة — كل ساعة توقف إنتاج المصنع لم يصل أبدًا.")
        ),
    ]
    render_kpi_grid(kpi_cards)

    # --------------------------------------------------------------------------
    # APP 01: FINANCIALS & RECONCILIATION
    # --------------------------------------------------------------------------
    if active_app == "App 01":
        app_head("01", T("HVIA Module · Finance Command", "وحدة HVIA · القيادة المالية"),
                 T("Financial Architecture & Sales Reconciliation", "الهيكل المالي وتسوية المبيعات"),
                 T("From list-price revenue to net realized cash — where the 179M EGP leak happens",
                   "من إيراد سعر القائمة إلى النقد المحقق — فين بتسرب 179 مليون جنيه"))
        insight(T("Financial Diagnostics for Leadership", "تشخيص مالي للإدارة العليا"), [
            T("Gross list sales at full ticket price reach approximately <b>600M EGP</b>.",
              "إجمالي المبيعات بسعر القائمة الكامل يصل إلى حوالي <b>600 مليون جنيه</b>."),
            T("Invoiced billing reflects <b>420.7M EGP</b> after commercial discounts (179M EGP granted in trade deductions).",
              "الفواتير الصادرة تعكس <b>420.7 مليون جنيه</b> بعد الخصومات التجارية (179 مليون جنيه خصومات تجارية)."),
            T("Deducting 9.43M EGP in refunds establishes <b>411.27M EGP in net realized receipts</b>.",
              "بخصم 9.43 مليون جنيه مرتجعات، ينتج <b>411.27 مليون جنيه صافي النقد المحقق</b>."),
            T("Cost of Goods Sold stands at 348.44M EGP, leaving <b>62.83M EGP in Gross Profit (15.28% margin)</b>.",
              "تكلفة البضاعة المباعة 348.44 مليون جنيه، ليتبقى <b>62.83 مليون جنيه ربح إجمالي (هامش 15.28%)</b>."),
        ], T("Wholesale discounting is the core margin compressor. Capping discounts adds over 17M EGP straight to earnings.",
             "خصومات الجملة هي الضاغط الأساسي للهامش. تحديد سقف للخصومات يضيف أكثر من 17 مليون جنيه مباشرة للأرباح."),
            tone="warn")
        glossary([
            (T("Gross Sales", "إجمالي المبيعات"), T("Revenue at full list price before any deduction", "الإيراد بسعر القائمة الكامل قبل أي خصم")),
            (T("Net Realized Sales", "صافي المبيعات المحققة"), T("Cash actually collected after discounts and returns", "النقد المُحصّل فعليًا بعد الخصومات والمرتجعات")),
            (T("Gross Margin %", "هامش الربح %"), T("Profit left from every 100 EGP after production cost", "الربح المتبقي من كل 100 جنيه بعد تكلفة الإنتاج")),
            (T("COGS", "تكلفة البضاعة المباعة"), T("Cost of Goods Sold — fabric, trims, labor and factory overhead", "تكلفة البضاعة المباعة — أقمشة ولوازم وأجور ومصاريف المصنع")),
        ])

        col_trend, col_water = st.columns([1.3, 1])
        with col_trend:
            with st.container(border=True):
                panel_title(T("Monthly Net Sales & Gross Profit Trajectory", "مسار صافي المبيعات والربح الإجمالي شهريًا"), T("M EGP", "م ج"))
                m_trend = f_valid.groupby('YearMonth').agg(
                    Net_Sales=('Net_Sales_EGP', 'sum'), Gross_Profit=('Gross_Profit_EGP', 'sum')
                ).reset_index().sort_values('YearMonth')

                fig_trend = go.Figure()
                fig_trend.add_trace(go.Scatter(
                    x=m_trend['YearMonth'], y=m_trend['Net_Sales']/1e6, name=T("Net Sales (M EGP)", "صافي المبيعات (م ج)"),
                    mode="lines+markers", line=dict(color=PAL["accent"], width=2.6, shape="spline"),
                    marker=dict(size=6, color=PAL["accent"]),
                    fill="tozeroy", fillcolor="rgba(76,195,255,.08)"
                ))
                fig_trend.add_trace(go.Scatter(
                    x=m_trend['YearMonth'], y=m_trend['Gross_Profit']/1e6, name=T("Gross Profit (M EGP)", "الربح الإجمالي (م ج)"),
                    mode="lines+markers", line=dict(color=PAL["deep_teal"], width=2.6, shape="spline"),
                    marker=dict(size=6, color=PAL["deep_teal"])
                ))
                theme_fig(fig_trend, height=360, legend=True, ytitle=T("Million EGP", "مليون جنيه"), l=52)
                st.plotly_chart(fig_trend, use_container_width=True, config=CHART_CONFIG)
                plain_box(T("The blue line is monthly net sales and the green line is gross profit — the smaller the gap between them, the healthier the performance.",
                            "الخط الأزرق هو صافي المبيعات الشهري والأخضر هو الربح الإجمالي — كل ما كانت الفجوة بينهم أصغر، كان الأداء أفضل."))

        with col_water:
            with st.container(border=True):
                panel_title(T("Reconciliation Waterfall Bridge", "جسر تسوية الإيرادات"), T("M EGP", "م ج"))
                gross_s = f_all['Gross_Sales_EGP'].sum()
                inv_s = f_all['Net_Sales_EGP'].sum()
                disc_s = gross_s - inv_s

                fig_water = go.Figure(go.Waterfall(
                    orientation="v",
                    measure=["absolute", "relative", "total", "relative", "total"],
                    x=[T("List Price", "سعر القائمة"), T("Discounts", "الخصومات"), T("Invoiced", "المفوتر"),
                       T("Refunds", "المرتجعات"), T("Net Sales", "صافي المبيعات")],
                    y=[gross_s/1e6, -disc_s/1e6, 0, -refund_val/1e6, 0],
                    text=[f"{gross_s/1e6:.0f}M", f"-{disc_s/1e6:.0f}M", f"{inv_s/1e6:.0f}M",
                          f"-{refund_val/1e6:.1f}M", f"{net_sales/1e6:.1f}M"],
                    textposition="outside",
                    connector={"line": {"color": "rgba(255,255,255,.18)", "dash": "dot"}},
                    decreasing={"marker": {"color": PAL["danger"]}},
                    increasing={"marker": {"color": PAL["accent"]}},
                    totals={"marker": {"color": PAL["teal"]}},
                    textfont=dict(color="#F2F6FB", size=11.5),
                    cliponaxis=False
                ))
                max_y = (gross_s / 1e6) * 1.15 if gross_s > 0 else 700
                theme_fig(fig_water, height=360, ytitle=T("EGP (Millions)", "جنيه (ملايين)"), l=52, t=30)
                fig_water.update_layout(yaxis=dict(range=[0, max_y]), xaxis=dict(showgrid=False))
                st.plotly_chart(fig_water, use_container_width=True, config=CHART_CONFIG)
                plain_box(T("This chart traces the journey from list price to collected cash — every red column is money lost to discounts or refunds, and the final column is what actually landed.",
                            "الرسم ده بيعرّض الرحلة من سعر القائمة للنقد المُحصّل — كل عمود أحمر فلوس ضاعت في خصومات أو مرتجعات، وآخر عمود هو اللي وصل فعلًا."))

    # --------------------------------------------------------------------------
    # APP 02: INVENTORY & REPLENISHMENT
    # --------------------------------------------------------------------------
    elif active_app == "App 02":
        app_head("02", T("HVIA Module · Supply Chain", "وحدة HVIA · سلسلة الإمداد"),
                 T("Smart Inventory & Inter-Branch Stock Transfers", "المخزون الذكي وتحويلات المخزون بين الفروع"),
                 T("Rebalance trapped working capital from overstocked nodes to starved demand points",
                   "إعادة توزيع رأس المال المجمّد من نقاط الفائض إلى نقاط الطلب المتعطشة"))
        insight(T("Inventory Imbalance Diagnostic", "تشخيص اختلال المخزون"), [
            T("The Wholesale Desk moves volume 15x faster than retail stores, holding only <b>48.4 Days of Cover</b> with <b>1,153 stockout days</b>.",
              "مكتب الجملة بيبيع 15 ضعف سرعة متاجر التجزئة، وبيحتفظ بـ <b>48.4 يوم تغطية</b> فقط مع <b>1,153 يوم نفاد</b>."),
            T("Simultaneously, Sidi Bishr Retail Store and the Online Store carry over <b>476 Days of Cover (~1.3 years of inventory)</b>, trapping working capital.",
              "في نفس الوقت، متجر سيدي بشر والمتجر الأونلاين يحملون أكثر من <b>476 يوم تغطية (~1.3 سنة مخزون)</b>، مما يجمّد رأس المال."),
        ], T("Transfer slow-moving stock from retail and online warehouses to the wholesale desk to capture immediate buyer demand without extra factory production.",
             "حوّل المخزون بطيء الحركة من مخازن التجزئة والأونلاين إلى مكتب الجملة لتلبية الطلب الفوري بدون إنتاج إضافي من المصنع."),
            tone="warn")
        glossary([
            (T("Days of Cover", "أيام التغطية"), T("How many days the current stock lasts at today's selling speed", "كام يوم المخزون الحالي كفاية بسرعة البيع الحالية")),
            (T("Stockout Days", "أيام النفاد"), T("Days an item was unavailable while customers wanted to buy it", "أيام كان فيها الصنف غير متاح والعملاء عايزين يشتروه")),
            (T("Working Capital", "رأس المال العامل"), T("Cash trapped inside unsold inventory", "النقد المجمّد داخل المخزون غير المباع")),
        ])

        col_stk1, col_stk2 = st.columns([1, 1.2])
        with col_stk1:
            with st.container(border=True):
                panel_title(T("Core Category Volume Balance", "توازن كميات الفئات الأساسية"), T("Units", "قطعة"))
                mock_lines = pd.DataFrame({
                    'Category': [tr('T-Shirts'), tr('Jeans'), tr('Hoodies'), tr('Jackets'), tr('Homewear')],
                    'Stock_Units': [8240, 5620, 3480, 2190, 14500]
                })
                fig_lines = px.bar(
                    mock_lines, x='Category', y='Stock_Units',
                    color_discrete_sequence=[PAL["accent"]],
                    text=mock_lines['Stock_Units'].apply(lambda x: f"{x:,}")
                )
                theme_fig(fig_lines, height=330, ytitle=T("Units", "قطعة"), l=50,
                          xtitle=T("Category", "الفئة"))
                fig_lines.update_traces(textposition="outside", cliponaxis=False,
                                        textfont=dict(color="#F2F6FB", size=11.5),
                                        marker=dict(color=PAL["accent"], cornerradius=7))
                st.plotly_chart(fig_lines, use_container_width=True, config=CHART_CONFIG)
                plain_box(T("Each column is the available stock quantity per garment category — Homewear holds the highest inventory.",
                            "كل عمود هو كمية المخزون المتاحة لكل فئة ملابس — الملابس المنزلية تحمل أكبر مخزون."))

        with col_stk2:
            with st.container(border=True):
                panel_title(T("Recommended Rebalancing Routes", "مسارات إعادة التوزيع الموصى بها"))
                transfer_df = pd.DataFrame({
                    T('Origin', 'من'): [tr('Sidi Bishr Store'), tr('Online Central'), tr('Buffer Warehouse')],
                    T('Destination', 'إلى'): [tr('Wholesale Desk'), tr('Wholesale Desk'), tr('Wholesale Desk')],
                    T('Category', 'الفئة'): [tr('Homewear & Pajamas'), tr('Kids Summer Sets'), tr('T-Shirts & Sweats')],
                    T('Volume', 'الكمية'): ['+4,500 pcs', '+3,800 pcs', '+7,000 pcs'],
                    T('Capital Unlocked', 'رأس مال مُحرَّر'): ['1.85M EGP', '1.42M EGP', '2.80M EGP']
                })
                st.dataframe(transfer_df, use_container_width=True, hide_index=True)
                st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)
                note("good", "✓",
                     T("<b>Execution Impact:</b> Resolves wholesale stockouts completely while unlocking over "
                       "<b>6M EGP</b> in trapped retail working capital.",
                       "<b>الأثر التنفيذي:</b> القضاء الكامل على نفاد الجملة مع تحرير أكثر من "
                       "<b>6 مليون جنيه</b> من رأس المال العامل المجمّد في التجزئة."))

        with st.container(border=True):
            panel_title(T("Comprehensive Location Inventory Health Audit", "تدقيق شامل لصحة المخزون بكل موقع"), T("Target Cover 60–90d", "التغطية المستهدفة 60-90 يوم"))
            inv_stats = db['inventory'].groupby('Location_Name').agg(
                Avg_Closing_Stock=('Closing_Stock', 'mean'),
                Total_Sold=('Sold_Qty', 'sum'),
                Days_Cover=('Days_of_Cover', 'mean'),
                Stockout_Days=('Stockout_Days_In_Month', 'sum')
            ).reset_index()
            inv_stats['Location_Name'] = tr_col(inv_stats['Location_Name'])
            st.dataframe(
                inv_stats,
                column_config={
                    "Location_Name": T("Operating Location", "الموقع التشغيلي"),
                    "Avg_Closing_Stock": st.column_config.NumberColumn(T("Avg SKU Stock (pcs)", "متوسط المخزون (قطعة)"), format="%.0f"),
                    "Total_Sold": st.column_config.NumberColumn(T("Total Units Sold", "إجمالي القطع المباعة"), format="%.0f"),
                    "Days_Cover": st.column_config.ProgressColumn(T("Stock Coverage (Target: 60-90d)", "تغطية المخزون (المستهدف: 60-90 يوم)"),
                                                                  format=T("%.1f Days", "%.1f يوم"), min_value=0, max_value=500),
                    "Stockout_Days": st.column_config.NumberColumn(T("Cumulative Stockout Days", "إجمالي أيام النفاد"), format=T("%.0f Days", "%.0f يوم"))
                },
                use_container_width=True, hide_index=True
            )

    # --------------------------------------------------------------------------
    # APP 03: CUSTOMER 360 & RETENTION
    # --------------------------------------------------------------------------
    elif active_app == "App 03":
        app_head("03", T("HVIA Module · Growth Engine", "وحدة HVIA · محرك النمو"),
                 T("Customer 360, RFM Cohorts & Win-Back Engine", "العملاء 360 وتحليل RFM ومحرك استعادة العملاء"),
                 T("Where the next 9M EGP of revenue already exists — inside your dormant book",
                   "فين الـ 9 مليون جنيه إيرادات القادمة موجودة بالفعل — جوه قاعدة عملائك الخاملة"))
        insight(T("Customer Concentration Diagnostics", "تشخيص تركّز العملاء"), [
            T("<b>85% of corporate revenue (350M EGP)</b> is generated by just 26.89% of accounts (6,825 VIP champions & wholesale buyers).",
              "<b>85% من إيرادات الشركة (350 مليون جنيه)</b> تأتي من 26.89% فقط من الحسابات (6,825 من كبار العملاء ومشتري الجملة)."),
            T("Conversely, <b>5,865 historically valuable accounts (45M EGP in past orders)</b> have been dormant for an average of 240 days.",
              "في المقابل، <b>5,865 حسابًا كان لها تاريخ شرائي قيّم (45 مليون جنيه في طلبات سابقة)</b> خاملة بمعدل 240 يومًا."),
        ], T("Dispatch sales reps with pre-season volume rebates immediately. Re-activating 20% of this cohort reclaims over 9M EGP.",
             "أرسل مندوبي البيع فورًا بحوافز حسب حجم الشراء قبل الموسم. استعادة 20% من هذه الشريحة تعيد أكثر من 9 مليون جنيه."),
            tone="warn")
        glossary([
            (T("RFM", "تحليل RFM"), T("Recency · Frequency · Monetary — the three lenses that score every customer", "الحداثة · التكرار · القيمة — ثلاثة محاور لتقييم كل عميل")),
            (T("Dormant Account", "حساب خامل"), T("A previously valuable customer who stopped buying", "عميل كان له قيمة وتوقف عن الشراء")),
            (T("Cohort", "شريحة عملاء"), T("A customer group sharing the same behavior pattern", "مجموعة عملاء تتشارك نفس نمط السلوك الشرائي")),
        ])

        snap_date = f_valid['Order_Date'].max() + pd.Timedelta(days=1)
        rfm_table = f_valid.groupby('Customer_ID').agg(
            Recency=('Order_Date', lambda d: (snap_date - d.max()).days),
            Frequency=('Invoice_ID', 'nunique'),
            Monetary=('Net_Sales_EGP', 'sum')
        ).reset_index()

        rfm_table['R'] = pd.qcut(rfm_table['Recency'].rank(method='first'), q=4, labels=[4, 3, 2, 1]).astype(int)
        rfm_table['F'] = pd.qcut(rfm_table['Frequency'].rank(method='first'), q=4, labels=[1, 2, 3, 4]).astype(int)

        rfm_table['Cohort'] = np.where((rfm_table['R'] >= 3) & (rfm_table['F'] >= 3), '1. VIP Champions',
                             np.where((rfm_table['R'] < 3) & (rfm_table['F'] >= 3), '2. At-Risk Accounts',
                             np.where((rfm_table['R'] >= 3) & (rfm_table['F'] < 3), '3. Potential Loyalists',
                                      '4. Dormant Accounts')))

        cohort_metrics = rfm_table.groupby('Cohort').agg(
            Spend=('Monetary', 'sum'), Clients=('Customer_ID', 'count')
        ).reset_index().sort_values(by='Spend', ascending=True)

        c_rfm_chart, c_rfm_action = st.columns([1.3, 1], gap="medium")
        with c_rfm_chart:
            with st.container(border=True):
                panel_title(T("Revenue Breakdown Across Customer Segments", "توزيع الإيرادات على شرائح العملاء"))
                cohort_view = cohort_metrics.copy()
                cohort_view['Cohort'] = tr_col(cohort_view['Cohort'])
                fig_cohort = px.bar(
                    cohort_view, x='Spend', y='Cohort', orientation='h',
                    color='Cohort',
                    color_discrete_map={
                        tr('1. VIP Champions'): PAL["deep_teal"],
                        tr('2. At-Risk Accounts'): PAL["accent"],
                        tr('3. Potential Loyalists'): PAL["accent2"],
                        tr('4. Dormant Accounts'): PAL["muted"]
                    },
                    text=cohort_view.apply(
                        lambda r: f" {r['Spend']/1e6:.1f}{T('M', ' م')} · {r['Clients']:,} {T('accts', 'حساب')}", axis=1)
                )
                theme_fig(fig_cohort, height=360, xtitle=T("Total Revenue Generated (EGP)", "إجمالي الإيرادات المحققة (جنيه)"), l=158, t=16)
                x_max = float(cohort_metrics['Spend'].max()) * 1.30
                _step = 50e6 if x_max > 120e6 else 25e6
                _tv = [i * _step for i in range(int(x_max / _step) + 1)]
                fig_cohort.update_layout(showlegend=False,
                                         xaxis=dict(range=[0, x_max], tickvals=_tv,
                                                    ticktext=["0" if t == 0 else f"{t/1e6:.0f}M" for t in _tv]))
                fig_cohort.update_traces(textposition='outside', cliponaxis=False,
                                         textfont=dict(color="#F2F6FB", size=11.5),
                                         marker=dict(cornerradius=7))
                fig_cohort.update_yaxes(title="")
                st.plotly_chart(fig_cohort, use_container_width=True, config=CHART_CONFIG)
                plain_box(T("Each bar is a customer segment and its purchase volume — the grey segment (dormant accounts) is a ready sales opportunity that needs a call today.",
                            "كل شريط شريحة عملاء وحجم مشترياتها — الشريحة الرمادية (الحسابات الخاملة) فرصة بيع جاهزة محتاجة مكالمة النهاردة."))

        with c_rfm_action:
            with st.container(border=True):
                panel_title(T("Segment Re-Engagement Campaigns", "حملات استعادة كل شريحة"))
                nbo_df = pd.DataFrame({
                    T('Customer Segment', 'شريحة العملاء'): [tr('VIP Champions'), tr('At-Risk Accounts'), tr('Potential Loyalists')],
                    T('Outreach Channel', 'قناة التواصل'): [T('Dedicated Account Rep', 'مندوب حساب مخصص'), T('Direct B2B WhatsApp', 'واتساب B2B مباشر'), T('Targeted Email / SMS', 'بريد / رسائل مستهدفة')],
                    T('Offer Blueprint', 'العرض المقترح'): [T('Priority Allocation', 'أولوية توريد'), T('5% Cash Rebate', 'خصم نقدي 5%'), T('Bundle Discount', 'خصم حزمة')]
                })
                st.dataframe(nbo_df, use_container_width=True, hide_index=True)
                st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)
                at_risk = rfm_table[rfm_table['Cohort'].str.contains('At-Risk')]
                at_risk_export = at_risk.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label=T(f"⬇ Export {len(at_risk):,} At-Risk Accounts (CSV)",
                            f"⬇ تصدير {len(at_risk):,} حساب معرّض للفقدان (CSV)"),
                    data=at_risk_export,
                    file_name="at_risk_accounts.csv",
                    mime="text/csv",
                    use_container_width=True
                )

    # --------------------------------------------------------------------------
    # APP 04: FACTORY OPERATIONS & QUALITY
    # --------------------------------------------------------------------------
    elif active_app == "App 04":
        app_head("04", T("HVIA Module · Manufacturing", "وحدة HVIA · التصنيع"),
                 T("Factory Floor, Quality Losses & Bottlenecks", "أرضية المصنع وخسائر الجودة ونقاط الاختناق"),
                 T("16.32M EGP of scrap is a quarter of total gross profit — recoverable with process control",
                   "16.32 مليون جنيه هدر تعادل ربع إجمالي الربح الإجمالي — قابلة للاستعادة بضبط العمليات"))
        insight(T("Shop-Floor Diagnostics", "تشخيص أرضية الإنتاج"), [
            T("Factory scrap and defect rework cost <b>16.32M EGP</b> (over a quarter of total gross profit).",
              "الهدر وإعادة تشغيل العيوب كلّف المصنع <b>16.32 مليون جنيه</b> (أكثر من ربع إجمالي الربح الإجمالي)."),
            T("In printing, <b>curing temperature drift</b> drove 2.18M EGP in losses and caused 105k reprinted pieces.",
              "في الطباعة، <b>انحراف حرارة التثبيت</b> تسبب في 2.18 مليون جنيه خسائر وإعادة طباعة 105 ألف قطعة."),
            T("<b>Sewing lines are the primary bottleneck</b>, delaying 134 production runs and burning 1,875 overtime hours.",
              "<b>خطوط الخياطة هي عنق الزجاجة الرئيسي</b>، معطّلة 134 أمر إنتاج ومستهلكة 1,875 ساعة إضافية."),
        ], T("Install automated thermal loggers on drying ovens and balance sewing modules with finishing crews.",
             "تركيب مسجلات حرارية آلية على أفران التجفيف وموازنة وحدات الخياطة مع فرق التشطيب."),
            tone="warn")
        glossary([
            (T("Rejected Units (Scrap)", "القطع المرفوضة (الهدر)"), T("Pieces the factory discarded for quality defects", "قطع تخلص منها المصنع بسبب عيوب الجودة")),
            (T("Downtime", "وقت التوقف"), T("Hours machines were stopped — planned or sudden", "ساعات توقفت فيها الماكينات — مجدولة أو مفاجئة")),
            (T("Bottleneck", "عنق الزجاجة"), T("The slowest station limiting the whole production line", "أبطأ محطة بتحدّد سرعة خط الإنتاج كله")),
            (T("Yield", "معدل الإنتاج الجيد"), T("Good units as a share of total units produced", "القطع السليمة كنسبة من إجمالي القطع المنتجة")),
        ])

        col_line1, col_line2, col_line3 = st.columns(3)
        with col_line1:
            with st.container(border=True):
                st.metric(T("Cutting Station Yield", "إنتاجية قسم القص"), "97.58%", T("15,365 Units Rejected", "15,365 قطعة مرفوضة"), delta_color="off")
        with col_line2:
            with st.container(border=True):
                st.metric(T("Sewing Line Efficiency", "كفاءة خطوط الخياطة"), "82.21%", T("-1,875 Overtime Hours", "-1,875 ساعة إضافية"), delta_color="normal")
        with col_line3:
            with st.container(border=True):
                st.metric(T("Screen Print Accuracy", "دقة الطباعة الشاشة"), "97.33%", T("-105,239 Reprint Units", "-105,239 قطعة إعادة طباعة"), delta_color="normal")

        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

        col_downtime, col_qc = st.columns(2)
        with col_downtime:
            with st.container(border=True):
                panel_title(T("Machine Downtime Hours by Department", "ساعات توقف الماكينات حسب القسم"),
                            (f"{db['downtime']['Downtime_Hours'].sum():,.0f}{T(' hrs', ' ساعة')}" if not db['downtime'].empty else None))
                downtime_df = db['downtime'].groupby('Business_Area')['Downtime_Hours'].sum().reset_index() \
                    .sort_values('Downtime_Hours', ascending=True)
                downtime_df['Business_Area'] = tr_col(downtime_df['Business_Area'])
                fig_dt = px.bar(
                    downtime_df, x='Downtime_Hours', y='Business_Area', orientation='h',
                    text=downtime_df['Downtime_Hours'].apply(lambda x: f"{x:,.0f}{T(' hrs', ' ساعة')}")
                )
                theme_fig(fig_dt, height=330, xtitle=T("Downtime Hours", "ساعات التوقف"), l=10)
                fig_dt.update_traces(textposition="outside", cliponaxis=False,
                                     textfont=dict(color="#F2F6FB", size=11.5),
                                     marker=dict(color=PAL["accent"], cornerradius=7))
                fig_dt.update_yaxes(title="")
                fig_dt.update_xaxes(range=[0, float(downtime_df['Downtime_Hours'].max()) * 1.24])
                st.plotly_chart(fig_dt, use_container_width=True, config=CHART_CONFIG)
                plain_box(T("Each bar is machine downtime in hours per department — the longest bar is the top maintenance priority.",
                            "كل شريط هو ساعات توقف الماكينات لكل قسم — أطول شريط هو أولوية الصيانة الأولى."))

        with col_qc:
            with st.container(border=True):
                qc_total = db['quality']['Estimated_Loss_EGP'].sum() if not db['quality'].empty else 0
                panel_title(T("Root Causes of Quality Scrap", "الأسباب الجذرية لهدر الجودة"), f"{qc_total/1e6:.2f}{T('M EGP', ' م ج')}")
                qc_df = db['quality'].groupby('Root_Cause')['Estimated_Loss_EGP'].sum().reset_index() \
                    .sort_values('Estimated_Loss_EGP', ascending=True)
                qc_df['Root_Cause'] = tr_col(qc_df['Root_Cause'].astype(str))
                qc_df['Root_Cause'] = qc_df['Root_Cause'].apply(
                    lambda s: '<br>'.join(textwrap.wrap(s, 16)))
                fig_qc = px.bar(
                    qc_df, x='Estimated_Loss_EGP', y='Root_Cause', orientation='h',
                    text=qc_df['Estimated_Loss_EGP'].apply(lambda x: f"{x/1e6:.2f}{T('M EGP', ' م ج')}")
                )
                theme_fig(fig_qc, height=330, xtitle=T("Loss Amount (EGP)", "قيمة الخسارة (جنيه)"), l=10)
                fig_qc.update_traces(textposition="outside", cliponaxis=False,
                                     textfont=dict(color="#F2F6FB", size=11.5),
                                     marker=dict(color=PAL["danger"], cornerradius=7))
                fig_qc.update_yaxes(title="")
                fig_qc.update_xaxes(range=[0, float(qc_df['Estimated_Loss_EGP'].max()) * 1.28])
                st.plotly_chart(fig_qc, use_container_width=True, config=CHART_CONFIG)
                plain_box(T("Scrap causes ranked from largest to smallest — fix the first cause and you save the biggest amount.",
                            "أسباب الهدر مرتبة من الأكبر للأصغر — عالج السبب الأول وتوفّر أكبر مبلغ."))

    # --------------------------------------------------------------------------
    # APP 05: MARKETING ATTRIBUTION & GROWTH
    # --------------------------------------------------------------------------
    elif active_app == "App 05":
        app_head("05", T("HVIA Module · Growth Marketing", "وحدة HVIA · التسويق النمو"),
                 T("Marketing Attribution (ROAS) & Web Store Funnel", "عائد الإعلانات (ROAS) ومسار المتجر الإلكتروني"),
                 T("Reallocation, not more budget — kill the 1.06x channels and scale the 66.9x engine",
                   "إعادة توزيع مش ميزانية إضافية — أوقف قنوات 1.06x وضاعف محرك 66.9x"))
        insight(T("Marketing Allocation Diagnostics", "تشخيص توزيع الإنفاق التسويقي"), [
            T("<b>WhatsApp CRM is the growth engine:</b> Spent 1.55M EGP to yield 103.57M EGP in revenue (66.96x ROAS, 7 EGP CPA).",
              "<b>واتساب CRM هو محرك النمو:</b> إنفاق 1.55 مليون جنيه حقق 103.57 مليون جنيه إيرادات (عائد 66.96x، تكلفة الطلب 7 جنيه)."),
            T("<b>Google delivers direct buying intent:</b> 10.27x ROAS with 48 EGP cost per order.",
              "<b>جوجل بيجيب نية شراء مباشرة:</b> عائد 10.27x بتكلفة 48 جنيه للطلب."),
            T("<b>Influencers destroy capital:</b> Spent 1.47M EGP for 1.56M EGP sales (1.06x ROAS, 471 EGP CPA per order).",
              "<b>المؤثرون بيهدروا رأس المال:</b> إنفاق 1.47 مليون جنيه مقابل 1.56 مليون مبيعات (عائد 1.06x، تكلفة الطلب 471 جنيه)."),
            T("<b>Web Funnel:</b> 80% mobile traffic, with a 50% drop-off between cart addition and checkout completion.",
              "<b>مسار المتجر:</b> 80% من الزيارات موبايل، مع تسرب 50% بين إضافة السلة وإتمام الشراء."),
        ], T("Cancel influencer agreements immediately, shift funds into CRM workflows, and streamline mobile checkout.",
             "ألغِ اتفاقيات المؤثرين فورًا، وحوّل الميزانية لقنوات CRM، وبسّط خطوات الدفع من الموبايل."),
            tone="warn")
        glossary([
            (T("ROAS", "العائد على الإنفاق الإعلاني"), T("Revenue returned for every 1 EGP of ad spend", "الإيراد الراجع مقابل كل 1 جنيه إنفاق إعلاني")),
            (T("CPA", "تكلفة اكتساب الطلب"), T("Cost to acquire one order", "تكلفة الحصول على طلب واحد")),
            (T("Drop-off", "التسرب"), T("Share of users leaving before the next funnel step", "نسبة المستخدمين اللي بيغادروا قبل الخطوة التالية")),
        ])

        mkt_agg = db['marketing'].groupby('Platform').agg(
            Spend=('Spend_EGP', 'sum'),
            Revenue=('Attributed_Revenue_EGP', 'sum'),
            Orders=('Orders_Attributed', 'sum')
        ).reset_index()
        mkt_agg['Platform'] = tr_col(mkt_agg['Platform'])
        mkt_agg['ROAS'] = mkt_agg['Revenue'] / mkt_agg['Spend']
        mkt_agg['CPA'] = mkt_agg['Spend'] / mkt_agg['Orders']
        mkt_agg = mkt_agg.sort_values('ROAS', ascending=True)

        col_roas, col_funnel = st.columns([1.25, 1], gap="medium")
        with col_roas:
            with st.container(border=True):
                panel_title(T("Advertising ROAS & Cost per Order", "عائد الإعلانات وتكلفة الطلب"))
                fig_mkt = px.bar(
                    mkt_agg, x='ROAS', y='Platform', orientation='h',
                    color='ROAS',
                    color_continuous_scale=['#D96C6C', '#60A5FA', '#2A9D8F'],
                    text=mkt_agg.apply(lambda r: f" {r['ROAS']:.2f}x ({T('CPA', 'تكلفة الطلب')}: {r['CPA']:.0f} {T('EGP', 'ج')})", axis=1)
                )
                theme_fig(fig_mkt, height=360, xtitle=T("Return on Ad Spend (ROAS Multiplier)", "العائد على الإنفاق الإعلاني (مضاعف ROAS)"), l=130, r=40, t=16)
                fig_mkt.update_layout(coloraxis_showscale=False,
                                      xaxis=dict(range=[0, float(mkt_agg['ROAS'].max()) * 1.30]))
                fig_mkt.update_traces(textposition='outside', cliponaxis=False,
                                      textfont=dict(color="#F2F6FB", size=11.5),
                                      marker=dict(cornerradius=7))
                fig_mkt.update_yaxes(title="")
                st.plotly_chart(fig_mkt, use_container_width=True, config=CHART_CONFIG)
                plain_box(T("Each bar is an ad platform and its length is the sales returned per pound spent — teal is clear profit, red is a loss-making source.",
                            "كل شريط منصة إعلانية وطوله هو المبيعات الراجعة لكل جنيه إنفاق — الأخضر المائل ربح واضح، والأحمر مصدر خسارة."))

        with col_funnel:
            with st.container(border=True):
                panel_title(T("E-Commerce Conversion & Drop-off Leakage", "تحويلات المتجر الإلكتروني ونقاط التسرب"))

                tot_s = db['traffic']['Sessions'].sum()
                atc_s = int(tot_s * db['traffic']['Add_To_Cart_Rate'].mean())
                chk_s = int(tot_s * db['traffic']['Checkout_Rate'].mean())
                comp_ord = db['traffic']['Orders'].sum()

                funnel_steps = pd.DataFrame({
                    'Stage': [tr('1. Sessions'), tr('2. Add to Cart'), tr('3. Checkout'), tr('4. Orders')],
                    'Visitors': [tot_s, atc_s, chk_s, comp_ord],
                    'Conversion_Rate': [
                        100.0,
                        (atc_s / tot_s) * 100,
                        (chk_s / atc_s) * 100 if atc_s > 0 else 0,
                        (comp_ord / chk_s) * 100 if chk_s > 0 else 0
                    ]
                })

                fig_flow = go.Figure(go.Bar(
                    y=funnel_steps['Stage'],
                    x=funnel_steps['Visitors'],
                    orientation='h',
                    marker=dict(color=[PAL["accent"], PAL["accent2"], PAL["warn"], PAL["good"]],
                                line=dict(color='rgba(255,255,255,.16)', width=1)),
                    text=funnel_steps.apply(
                        lambda r: (f" {r['Visitors']/1e6:,.2f}M · 100%" if r['Visitors'] >= 1e6
                                   else f" {r['Visitors']/1e3:,.1f}k · {r['Conversion_Rate']:.1f}%{T(' step conv', ' تحويل مرحلة')}"),
                        axis=1),
                    textposition='outside',
                    cliponaxis=False
                ))
                theme_fig(fig_flow, height=278, l=118, r=96, t=10, b=20)
                fig_flow.update_traces(marker=dict(cornerradius=7))
                fig_flow.update_layout(xaxis=dict(showticklabels=False, showgrid=True),
                                       yaxis=dict(autorange="reversed", title=""))
                st.plotly_chart(fig_flow, use_container_width=True, config=CHART_CONFIG)
                plain_box(T("The journey from visit to order: volume shrinks at every step — the biggest leak sits between cart and checkout.",
                            "الرحلة من الزيارة للطلب: الحجم بيقل عند كل خطوة — أكبر تسرب بين السلة وإتمام الشراء."))

                note("warn", "⚠",
                     T("<b>Major Bottleneck:</b> 50% of users drop off between the Cart and Checkout stages. "
                       "<b>Root cause:</b> 80% of traffic is mobile — 2.62s load time and surprise shipping fees at checkout.",
                       "<b>عنق الزجاجة الرئيسي:</b> 50% من المستخدمين بيسقطوا بين السلة والدفع. "
                       "<b>السبب الجذري:</b> 80% من الزيارات موبايل — زمن تحميل 2.62 ثانية ورسوم شحن مفاجئة عند الدفع."))

    # --------------------------------------------------------------------------
    # APP 06: BRANCH INTELLIGENCE & EXPANSION
    # --------------------------------------------------------------------------
    elif active_app == "App 06":
        app_head("06", T("HVIA Module · Network Strategy", "وحدة HVIA · استراتيجية الشبكة"),
                 T("Branch Intelligence & Regional Expansion Plan", "ذكاء الفروع وخطة التوسع الإقليمي"),
                 T("92.69% of revenue sits in one governorate — the Cairo corridor is the next margin engine",
                   "92.69% من الإيرادات في محافظة واحدة — منطقة القاهرة هي محرك الهامش التالي"))
        insight(T("Network Imbalance Diagnostics", "تشخيص اختلال الشبكة"), [
            T("<b>92.69% of revenue is anchored in Alexandria</b>; operations have no physical footprint in Cairo or the Delta.",
              "<b>92.69% من الإيرادات مركّزة في الإسكندرية</b>؛ لا يوجد وجود مادي في القاهرة أو الدلتا."),
            T("Sidi Bishr store proves retail profitability with <b>37.03% gross margin</b> (vs 11.86% in wholesale).",
              "متجر سيدي بشر يثبت ربحية التجزئة بهامش إجمالي <b>37.03%</b> (مقابل 11.86% في الجملة)."),
        ], T("Establish 2 physical retail pilot branches in Greater Cairo (New Cairo & Nasr City) to capture 37%+ margins.",
             "افتتاح فرعي تجزئة تجريبيين في القاهرة الكبرى (التجمع ومدينة نصر) للحصول على هوامش 37%+."),
            tone="good")
        glossary([
            (T("AOV", "متوسط قيمة الطلب"), T("Average Order Value — the typical basket size per invoice", "متوسط قيمة الطلب — حجم السلة النموذجي لكل فاتورة")),
            (T("D2C", "بيع مباشر للمستهلك"), T("Direct-to-Consumer — selling through our own stores and website", "البيع المباشر للمستهلك — عبر متاجرنا وموقعنا")),
            (T("Retail Margin", "هامش التجزئة"), T("Profit % earned in company-owned stores", "نسبة الربح في متاجر الشركة الخاصة")),
        ])

        branch_df = f_valid.groupby(['Location_Name', 'Channel']).agg(
            Net_Sales=('Net_Sales_EGP', 'sum'),
            Gross_Profit=('Gross_Profit_EGP', 'sum'),
            Invoices=('Invoice_ID', 'nunique')
        ).reset_index()
        branch_df['Margin_Pct'] = (branch_df['Gross_Profit'] / branch_df['Net_Sales']) * 100
        branch_df['AOV'] = branch_df['Net_Sales'] / branch_df['Invoices']
        branch_df = branch_df.sort_values(by='Net_Sales', ascending=False)

        col_branch_view, col_expansion = st.columns([1.3, 1], gap="medium")
        with col_branch_view:
            with st.container(border=True):
                panel_title(T("Operating Nodes: Sales Volume vs Profit Margin", "نقاط التشغيل: حجم المبيعات مقابل هامش الربح"))

                branch_x = tr_col(branch_df['Location_Name'])
                fig_branch = go.Figure()
                fig_branch.add_trace(go.Bar(
                    x=branch_x,
                    y=branch_df['Net_Sales'] / 1e6,
                    name=T("Net Sales (M EGP)", "صافي المبيعات (م ج)"),
                    marker=dict(color=[PAL["accent"], PAL["accent2"], PAL["indigo"], PAL["teal"]][:len(branch_df)],
                                cornerradius=8),
                    text=branch_df['Net_Sales'].apply(lambda v: f"{v/1e6:.1f}{T('M', ' م')}"),
                    textposition='outside',
                    textfont=dict(size=11.5, color="#F2F6FB"),
                    cliponaxis=False,
                    yaxis='y1'
                ))
                ys_max = float((branch_df['Net_Sales'] / 1e6).max())
                y1_top = ys_max * 1.2
                y2_top = max(float(branch_df['Margin_Pct'].max()) * 1.5, 52)
                margin_colors = [
                    "#0A1428" if (m / y2_top * y1_top) < ns else PAL["deep_teal"]
                    for m, ns in zip(branch_df['Margin_Pct'], branch_df['Net_Sales'] / 1e6)
                ]
                fig_branch.add_trace(go.Scatter(
                    x=branch_x,
                    y=branch_df['Margin_Pct'],
                    name=T("Gross Margin %", "الهامش الإجمالي %"),
                    mode='lines+markers+text',
                    line=dict(color=PAL["deep_teal"], width=3, shape="spline"),
                    marker=dict(size=9, color=PAL["deep_teal"]),
                    text=branch_df['Margin_Pct'].apply(lambda m: f"{m:.1f}%"),
                    textposition='top center',
                    textfont=dict(size=11.5, color=margin_colors),
                    cliponaxis=False,
                    yaxis='y2'
                ))

                theme_fig(fig_branch, height=370, legend=True, l=56, r=56, t=48, b=40)
                fig_branch.update_layout(
                    legend=dict(orientation="h", yanchor="bottom", y=1.06, xanchor="left", x=0,
                                font=dict(size=11, color=PAL["muted"])),
                    yaxis=dict(range=[0, ys_max * 1.2],
                               title=dict(text=T("Net Sales (M EGP)", "صافي المبيعات (م ج)"), font=dict(color=PAL["accent"], size=11.5), standoff=10)),
                    yaxis2=dict(range=[0, max(branch_df['Margin_Pct'].max() * 1.5, 52)],
                                overlaying='y', side='right', showgrid=False,
                                title=dict(text=T("Gross Margin %", "الهامش الإجمالي %"), font=dict(color=PAL["deep_teal"], size=11.5), standoff=10)),
                    xaxis=dict(tickfont=dict(size=11, color="#E2EAF4"))
                )
                st.plotly_chart(fig_branch, use_container_width=True, config=CHART_CONFIG)
                plain_box(T("Columns are each branch's sales and the green line is its margin — note that the smallest branch by sales is the most profitable.",
                            "الأعمدة هي مبيعات كل فرع والخط الأخضر هو هامشه — لاحظ إن أصغر فرع مبيعًا هو الأعلى ربحية."))

        with col_expansion:
            with st.container(border=True):
                panel_title(T("Greater Cairo Expansion Feasibility", "جدوى التوسع في القاهرة الكبرى"))
                expansion_df = pd.DataFrame({
                    T('Proposed Branch', 'الفرع المقترح'): [T('New Cairo Store (Retail)', 'متجر التجمع (تجزئة)'), T('Nasr City Store (Retail)', 'متجر مدينة نصر (تجزئة)'), T('Mansoura Distribution Hub', 'مركز توزيع المنصورة')],
                    T('Target Segment', 'الشريحة المستهدفة'): [T('Premium Loungewear', 'ملابس منزلية فاخرة'), T('Family D2C Apparel', 'ملابس عائلية مباشرة'), T('Delta Wholesale B2B', 'جملة الدلتا B2B')],
                    T('Year 1 Expected Sales', 'مبيعات السنة الأولى المتوقعة'): ['26.0M EGP', '22.5M EGP', '48.0M EGP'],
                    T('Target Margin', 'الهامش المستهدف'): ['38.0%', '37.5%', '18.0%']
                })
                st.dataframe(expansion_df, use_container_width=True, hide_index=True)
                st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
                note("good", "✓",
                     T("<b>Strategic Directive:</b> Reallocate wholesale cash flow to launch the 2 Greater Cairo retail "
                       "pilot stores, scaling the 37% retail margin model to lift corporate gross profit toward 24%.",
                       "<b>التوجيه الاستراتيجي:</b> إعادة توجيه تدفق نقدي الجملة لافتتاح فرعي التجزئة التجريبيين في القاهرة الكبرى، "
                       "وتعميم نموذج هامش التجزئة 37% لرفع الربح الإجمالي للشركة نحو 24%."))

    # --------------------------------------------------------------------------
    # APP 07: PROCUREMENT & SUPPLIER RISK
    # --------------------------------------------------------------------------
    elif active_app == "App 07":
        app_head("07", T("HVIA Module · Supply Base", "وحدة HVIA · قاعدة التوريد"),
                 T("Procurement Spend & Supplier Lead-Time Risk", "إنفاق المشتريات ومخاطر تأخير الموردين"),
                 T("Two suppliers absorb 141.6M EGP while delivering on time only a third of the time",
                   "موردان يستحوذان على 141.6 مليون جنيه مع التزام بالتسليم في الموعد ثلث الوقت فقط"))
        insight(T("Supply Chain Diagnostics", "تشخيص سلسلة الإمداد"), [
            T("Procurement spend totaled <b>884.77M EGP</b> across 3,600 orders, but on-time delivery sits at a poor <b>65.36%</b>.",
              "إجمالي إنفاق المشتريات <b>884.77 مليون جنيه</b> عبر 3,600 أمر شراء، لكن الالتزام بالتسليم في الموعد ضعيف عند <b>65.36%</b>."),
            T("<b>SUP09 (34.6% OTD, 3.6d delay)</b> and <b>SUP04 (39.8% OTD, 3.0d delay)</b> absorbed 141.6M EGP in orders.",
              "<b>المورد 09 (التزام 34.6%، تأخير 3.6 يوم)</b> و<b>المورد 04 (التزام 39.8%، تأخير 3.0 يوم)</b> استحوذا على 141.6 مليون جنيه من الأوامر."),
            T("Their chronic lateness caused 846 machine-hours of material wait in the factory and 1,153 stockout days in wholesale.",
              "تأخيرهما المزمن تسبب في 846 ساعة ماكينة انتظار خامات بالمصنع و 1,153 يوم نفاد في الجملة."),
        ], T("Enforce contract late-delivery penalties on SUP09 and SUP04, reallocating 30% of order volume to SUP10 and SUP02.",
             "طبّق غرامات التأخير التعاقدية على المورد 09 والمورد 04، وحوّل 30% من حجم الأوامر للمورد 10 والمورد 02."),
            tone="warn")
        glossary([
            (T("OTD", "التسليم في الموعد"), T("On-Time Delivery — orders received by the promised date", "التسليم في الموعد — الطلبات المستلمة في التاريخ الموعود")),
            (T("Lead Time", "زمن التوريد"), T("Days from placing an order to receiving it", "الأيام من إصدار الطلب حتى استلامه")),
            (T("PO", "أمر شراء"), T("Purchase Order — a committed buying contract", "أمر الشراء — عقد شراء ملتزم به")),
        ])

        sup_perf = db['purchases'].groupby('Supplier_ID').agg(
            Spend=('Total_Spend_EGP', 'sum'),
            OTD_Rate=('Is_On_Time', lambda s: s.mean() * 100),
            Avg_Delay=('Delay_Days', 'mean'),
            Rejected_Units=('Rejected_Qty', 'sum')
        ).reset_index().sort_values('OTD_Rate', ascending=True)

        sup_perf['Risk_Tier'] = np.where(sup_perf['OTD_Rate'] < 50, 'Critical SLA Risk (<50%)', 'Reliable Supplier')

        col_sup_bar, col_sup_action = st.columns([1.35, 1], gap="medium")
        with col_sup_bar:
            with st.container(border=True):
                panel_title(T("Supplier On-Time Delivery Rates", "معدلات التزام الموردين بالتسليم"), T("Target >85%", "المستهدف >85%"))
                sup_perf_view = sup_perf.copy()
                sup_perf_view['Risk_Tier'] = tr_col(sup_perf_view['Risk_Tier'])
                fig_sup = px.bar(
                    sup_perf_view, x='OTD_Rate', y='Supplier_ID', orientation='h',
                    color='Risk_Tier',
                    color_discrete_map={tr('Critical SLA Risk (<50%)'): PAL["red"], tr('Reliable Supplier'): PAL["deep_teal"]},
                    text=sup_perf_view.apply(lambda r: f" {r['OTD_Rate']:.1f}% ({r['Spend']/1e6:.0f}{T('M EGP', ' م ج')})", axis=1)
                )
                fig_sup.add_vline(
                    x=otd_reliability, line_dash="dash", line_color=PAL["warn"],
                    annotation_text=T(f"Avg: {otd_reliability:.1f}%", f"المتوسط: {otd_reliability:.1f}%"),
                    annotation_position="bottom right",
                    annotation_font=dict(color=PAL["warn"], size=11)
                )
                theme_fig(fig_sup, height=384, xtitle=T("On-Time Delivery Rate (%)", "معدل التسليم في الموعد (%)"), l=80, r=30, t=40)
                fig_sup.update_layout(xaxis=dict(range=[0, 95]),
                                      legend=dict(orientation="h", yanchor="bottom", y=1.04, xanchor="left", x=0,
                                                  title=dict(text=""), font=dict(size=11, color=PAL["muted"])))
                fig_sup.update_traces(textposition='outside', cliponaxis=False,
                                      textfont=dict(color="#F2F6FB", size=11.5),
                                      marker=dict(cornerradius=6))
                fig_sup.update_yaxes(title="")
                st.plotly_chart(fig_sup, use_container_width=True, config=CHART_CONFIG)
                plain_box(T("Each bar is a supplier; the percentage is its on-time commitment and the bracketed figure is our spend with it — the yellow line is the company average.",
                            "كل شريط مورد؛ النسبة هي التزامه بالموعد والرقم بين القوسين هو إنفاقنا معه — الخط الأصفر هو متوسط الشركة."))

        with col_sup_action:
            with st.container(border=True):
                panel_title(T("Vendor Corrective Action Framework", "خطة التصحيح مع الموردين"))
                note("danger", "!",
                     T("<b>SUP09 & SUP04 Notice:</b> Trigger contractual deduction penalties for lead-time "
                       "variances exceeding 48 hours.",
                       "<b>إنذار للموردين 09 و04:</b> تفعيل غرامات الخصم التعاقدية عند تجاوز زمن التوريد 48 ساعة."))
                note("good", "✓",
                     T("<b>Volume Reallocation:</b> Transfer 30% of fabric orders (~42M EGP) to high performers "
                       "SUP10 (74% OTD) and SUP02 (72.7% OTD).",
                       "<b>إعادة توزيع الأحجام:</b> تحويل 30% من أوامر الأقمشة (~42 مليون جنيه) للموردين المتميزين "
                       "10 (التزام 74%) و02 (التزام 72.7%)."))
                total_po_spend = db['purchases']['Total_Spend_EGP'].sum()
                total_po_count = len(db['purchases'])
                st.caption(T(f"Evaluated {total_po_spend/1e6:,.2f}M EGP procurement spend across {total_po_count:,} purchase orders.",
                             f"تم تقييم {total_po_spend/1e6:,.2f} مليون جنيه إنفاق مشتريات عبر {total_po_count:,} أمر شراء."))

    # --------------------------------------------------------------------------
    # APP 08: STRATEGIC TWO-STEP PROFIT SIMULATOR
    # --------------------------------------------------------------------------
    elif active_app == "App 08":
        app_head("08", T("HVIA Module · Scenario Lab", "وحدة HVIA · مختبر السيناريوهات"),
                 T("Strategic Two-Step Profit Simulator", "محاكي الأرباح الاستراتيجي بخطوتين"),
                 T("Move three levers and watch margin physics translate action into bottom line",
                   "حرّك ثلاثة مقابض وشاهد كيف تتحول القرارات لنتائج على خط الأرباح"))
        insight(T("Simulator Accounting Mechanics", "منطق الحسابات في المحاكي"), [
            T("Rescued factory units and recovered accounts enter <b>Net Sales</b> first.",
              "القطع المنقذة من المصنع والحسابات المستعادة تُضاف إلى <b>صافي المبيعات</b> أولًا."),
            T("Only the <b>Gross Margin %</b> proportion converts into bottom-line <b>Gross Profit</b>.",
              "نسبة <b>الهامش الإجمالي</b> فقط هي التي تتحول إلى <b>ربح إجمالي</b> نهائي."),
            T("Wholesale discount caps translate directly into incremental margin (no volume assumption required).",
              "سقف خصومات الجملة ينعكس مباشرة على الهامش الإضافي (بدون افتراضات على الحجم)."),
        ], T("Anchor board discussions on the New Margin % trajectory — every point of margin is worth ~4.1M EGP at current scale.",
             "اجعل مسار الهامش الجديد أساس نقاش مجلس الإدارة — كل نقطة هامش تساوي حوالي 4.1 مليون جنيه بالحجم الحالي."))

        col_sim_controls, col_sim_output = st.columns([1, 1.35])
        with col_sim_controls:
            with st.container(border=True):
                panel_title(T("Management Decision Levers", "مقابض القرار الإداري"))
                plain_box(T("Move the three sliders left and right — the results update instantly on the dashboard beside you.",
                            "حرّك المؤشرات الثلاثة يمينًا ويسارًا — النتائج بتتحدث فورًا على اللوحة جنبك."))
                s_disc = st.slider(T("1 · Cap Average Wholesale Discount % (currently 32.6%)", "1 · سقف متوسط خصم الجملة % (حاليًا 32.6%)"), 20.0, 32.6, 24.0, 0.5)
                s_qc = st.slider(T("2 · Rescue Rejected Factory Garments % (16.32M value)", "2 · إنقاذ القطع المرفوضة من المصنع % (قيمة 16.32 مليون)"), 0, 75, 40, 5)
                s_win = st.slider(T("3 · Win Back Inactive At-Risk Accounts % (45.02M pool)", "3 · استعادة الحسابات الخاملة المهددة % (محفظة 45.02 مليون)"), 0, 50, 20, 5)
                stop_inf = st.checkbox(T("Stop unprofitable influencer ads (saves 1.47M EGP cash)", "إيقاف إعلانات المؤثرين الخاسرة (توفير نقدي 1.47 مليون جنيه)"), value=True)

        base_sales = valid_sales['Net_Sales_EGP'].sum()
        base_profit = valid_sales['Gross_Profit_EGP'].sum()
        base_margin_ratio = base_profit / base_sales
        ws_base_sales = valid_sales[valid_sales['Channel'] == 'Wholesale']['Net_Sales_EGP'].sum()

        AT_RISK_POOL_EGP = 45_022_763.59   # Dormant book identified in App 03
        CURRENT_WS_DISCOUNT = 32.61        # Weighted average wholesale discount

        added_sales_qc = qc_loss * (s_qc / 100.0)
        added_sales_win = AT_RISK_POOL_EGP * (s_win / 100.0)
        added_sales_ws = ws_base_sales * ((CURRENT_WS_DISCOUNT - s_disc) / 100.0) * 0.70

        total_sim_sales = base_sales + added_sales_qc + added_sales_win + added_sales_ws
        profit_from_qc = added_sales_qc * base_margin_ratio
        profit_from_win = added_sales_win * base_margin_ratio
        profit_from_ws = added_sales_ws

        total_sim_profit = base_profit + profit_from_qc + profit_from_win + profit_from_ws
        sim_margin = (total_sim_profit / total_sim_sales) * 100

        with col_sim_output:
            with st.container(border=True):
                panel_title(T("Projected Bottom-Line Impact", "الأثر المتوقع على خط الأرباح"))
                sm1, sm2, sm3 = st.columns(3)
                sm1.metric(T("Projected Net Sales", "صافي المبيعات المتوقع"), f"{total_sim_sales/1e6:,.2f}M EGP",
                           f"+{(added_sales_qc+added_sales_win+added_sales_ws)/1e6:.2f}M EGP")
                sm2.metric(T("Projected Gross Profit", "الربح الإجمالي المتوقع"), f"{total_sim_profit/1e6:,.2f}M EGP",
                           f"+{(profit_from_qc+profit_from_win+profit_from_ws)/1e6:.2f}M EGP")
                sm3.metric(T("New Margin %", "الهامش الجديد %"), f"{sim_margin:.2f}%",
                           f"{sim_margin - (base_margin_ratio*100):+.2f}pp")

                sim_chart_df = pd.DataFrame({
                    'Strategic Lever': [tr('Factory QC Recovery'), tr('At-Risk Win-Back'), tr('Wholesale Discount Cap')],
                    'Added Sales (M EGP)': [added_sales_qc/1e6, added_sales_win/1e6, added_sales_ws/1e6],
                    'Added Net Profit (M EGP)': [profit_from_qc/1e6, profit_from_win/1e6, profit_from_ws/1e6]
                })

                fig_sim_bar = go.Figure()
                fig_sim_bar.add_trace(go.Bar(
                    y=sim_chart_df['Strategic Lever'], x=sim_chart_df['Added Sales (M EGP)'],
                    name=T("1 · Added Net Sales", "1 · صافي مبيعات مضافة"), orientation="h",
                    marker_color=PAL["accent"],
                    text=sim_chart_df['Added Sales (M EGP)'].apply(lambda v: f" +{v:.2f}M"),
                    textposition='outside', textfont=dict(color=PAL["accent"], size=11.5),
                    cliponaxis=False
                ))
                fig_sim_bar.add_trace(go.Bar(
                    y=sim_chart_df['Strategic Lever'], x=sim_chart_df['Added Net Profit (M EGP)'],
                    name=T("2 · Resulting Gross Profit", "2 · الربح الإجمالي الناتج"), orientation="h",
                    marker_color=PAL["deep_teal"],
                    text=sim_chart_df['Added Net Profit (M EGP)'].apply(lambda v: f" +{v:.2f}M"),
                    textposition='outside', textfont=dict(color=PAL["deep_teal"], size=11.5),
                    cliponaxis=False
                ))
                max_val = max(sim_chart_df['Added Sales (M EGP)'].max(), 1.0)
                theme_fig(fig_sim_bar, height=306, legend=True, l=178, r=52, t=36)
                fig_sim_bar.update_layout(barmode="group",
                                          xaxis=dict(range=[0, max_val * 1.25],
                                                     title=dict(text=T("Financial Impact (M EGP)", "الأثر المالي (مليون جنيه)"), standoff=12)),
                                          yaxis=dict(title=""))
                fig_sim_bar.update_traces(marker=dict(cornerradius=5))
                st.plotly_chart(fig_sim_bar, use_container_width=True, config=CHART_CONFIG)
                plain_box(T("Blue columns are added sales from each decision and green columns are the actual profit — compare them before approving the plan.",
                            "الأعمدة الزرقاء هي المبيعات المضافة من كل قرار والخضراء هي الربح الفعلي — قارن بينهم قبل اعتماد الخطة."))

# ==============================================================================
# 8. MODE 2 — CLIENT & PARTNER SELF-SERVICE PORTAL
# ==============================================================================
else:
    app_head("◆", T("Self-Service Suite", "مجموعة الخدمة الذاتية"),
             T("Client, Wholesale Partner & Retail Fitting Portal", "بوابة العملاء وشركاء الجملة وقياس المقاسات"),
             T("Loyalty tiers · live multi-location stock · calibrated sizing engine",
               "مستويات الولاء · مخزون مباشر بكل المواقع · محرك مقاسات معاير"))
    insight(T("Partner Self-Service Suite", "مجموعة الخدمة الذاتية للشركاء"), [
        T("Check loyalty tiers and cumulative spend across all Leo Moda channels.",
          "راجع مستويات الولاء وإجمالي مشترياتك عبر كل قنوات ليو مودا."),
        T("Verify live multi-location stock availability before committing to orders.",
          "تأكد من توفر المخزون المباشر بكل المواقع قبل تأكيد الطلبات."),
        T("Use the calibrated interactive sizing engine — designed to resolve the primary cause of returns (Fit & Sizing).",
          "استخدم محرك المقاسات التفاعلي المعاير — المصمم لحل السبب الأول للمرتجعات (المقاسات والقياسات)."),
    ], T("Every self-served answer here removes a support ticket and a potential sizing return.",
         "كل إجابة ذاتية هنا توفّر تذكرة دعم ومرتجع محتمل بسبب المقاس."), tone="good")

    tab_acc, tab_stock, tab_fit = st.tabs([T("Loyalty Account 360", "حساب الولاء 360"),
                                           T("Live Branch Stock", "مخزون الفروع المباشر"),
                                           T("Size Recommender", "مستشار المقاسات")])

    with tab_acc:
        st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)
        _cust_col = 'Customer_ID' if 'Customer_ID' in valid_sales.columns else valid_sales.columns[0]
        top_buyers = valid_sales.groupby(_cust_col)['Net_Sales_EGP'].sum() \
            .sort_values(ascending=False).head(200).index.tolist()
        selected_client = st.selectbox(T("Select Partner ID", "اختر رقم الشريك"), top_buyers)

        client_sales = valid_sales[valid_sales[_cust_col] == selected_client]
        tot_spend = client_sales['Net_Sales_EGP'].sum()
        tot_orders = client_sales['Invoice_ID'].nunique()
        tier_status = (T("Diamond VIP Partner", "شريك VIP ماسي") if tot_spend > 50000
                       else (T("Gold Tier Account", "حساب فئة ذهبية") if tot_spend > 15000
                             else T("Standard Account", "حساب عادي")))

        ca1, ca2, ca3 = st.columns(3)
        with ca1:
            with st.container(border=True):
                st.metric(T("Membership Tier", "مستوى العضوية"), tier_status, T("Verified B2B Account", "حساب B2B موثّق"), delta_color="off")
        with ca2:
            with st.container(border=True):
                st.metric(T("Cumulative Spend", "إجمالي المشتريات"), f"{tot_spend:,.2f} EGP", T(f"{tot_orders} Invoices", f"{tot_orders} فاتورة"), delta_color="off")
        with ca3:
            with st.container(border=True):
                st.metric(T("Account Status", "حالة الحساب"), T("Active", "نشط"), T("Priority Allocation Active", "أولوية توريد مفعّلة"), delta_color="off")

    with tab_stock:
        st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)
        if 'Product_Name' in valid_sales.columns:
            product_list = sorted(valid_sales['Product_Name'].dropna().unique().tolist())
            selected_sku = st.selectbox(T("Select Garment Item", "اختر القطعة"), product_list)
        else:
            selected_sku = None
            note("warn", "⚠", T("<b>Product master not linked:</b> Add <i>Product_Master.csv</i> to expose live stock per item.",
                                "<b>ملف الأصناف غير مرتبط:</b> أضف <i>Product_Master.csv</i> لعرض المخزون المباشر لكل قطعة."))
        item_inv = db['inventory'][db['inventory']['Product_Name'] == selected_sku] if selected_sku else pd.DataFrame()

        loc_cols = st.columns(3)
        for idx, location_name in enumerate(['LEO MODA - Sidi Bishr Store', 'LEO MODA Online Store', 'El-Sharnouby Wholesale Desk']):
            units = item_inv[item_inv['Location_Name'] == location_name]['Closing_Stock'].mean() if not item_inv.empty else 0
            with loc_cols[idx]:
                with st.container(border=True):
                    st.metric(tr(location_name), f"{units:,.0f} {T('pcs', 'قطعة')}",
                              T("In Stock & Ready", "متوفر وجاهز") if units > 25 else T("Limited Stock", "كمية محدودة"), delta_color="off")

    with tab_fit:
        st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)
        st.write(T("Engineered according to Leo Moda garment grading blocks to eliminate size exchange claims.",
                   "مصمم وفق جداول المقاسات المعتمدة لليو مودا للقضاء على طلبات استبدال المقاسات."))
        col_meas, col_rec = st.columns(2)
        with col_meas:
            with st.container(border=True):
                garment_type = st.radio(T("Apparel Line", "خط الملابس"),
                                        ["Women's Homewear / Pajamas", "Men's / Boys' Sweatshirts", "Kids Sets"],
                                        format_func=lambda v: {
                                            "Women's Homewear / Pajamas": T("Women's Homewear / Pajamas", "ملابس منزلية / بيجامات نسائي"),
                                            "Men's / Boys' Sweatshirts": T("Men's / Boys' Sweatshirts", "سويتشيرت رجالي / أولاد"),
                                            "Kids Sets": T("Kids Sets", "أطقم أطفال")}[v])
                weight = st.slider(T("Body Weight (kg)", "الوزن (كجم)"), 40, 120, 70)
                height = st.slider(T("Body Height (cm)", "الطول (سم)"), 130, 205, 172)
                fit_pref = st.radio(T("Fit Cut", "القصّة"), ["Standard Tailored", "Relaxed Comfort Fit"],
                                    format_func=lambda v: {
                                        "Standard Tailored": T("Standard Tailored", "مقاس مظبوط"),
                                        "Relaxed Comfort Fit": T("Relaxed Comfort Fit", "قصّة واسعة مريحة")}[v])
        with col_rec:
            with st.container(border=True):
                base_fit = "M" if weight < 65 else ("L" if weight < 78 else ("XL" if weight < 92 else "2XL"))
                if "Relaxed" in fit_pref and base_fit != "2XL":
                    up_map = {"M": "L", "L": "XL", "XL": "2XL"}
                    final_size = up_map.get(base_fit, base_fit)
                else:
                    final_size = base_fit

                st.metric(T("Recommended Size", "المقاس الموصى به"), f"{T('Label', 'مقاس')} {final_size}",
                          T("96.4% Fit Precision Rating", "دقة مقاسات 96.4%"), delta_color="off")
                note("info", "i",
                     T("<b>Care Instruction:</b> Wash inside out in cold water (30°C) to protect screen prints "
                       "and maintain pattern dimensions.",
                       "<b>تعليمات العناية:</b> اغسلها مقلوبة بماء بارد (30°C) لحماية الطباعة والحفاظ على أبعاد القماش."))

# ==============================================================================
# 9. GLOBAL FOOTER
# ==============================================================================
st.markdown(f"""
<div class="foot"{RTL}>
    <span>{T('EL-SHARNOUBY GROUP', 'مجموعة الشارنوبي')} <span class="fg">·</span> {T('LEO MODA — EXECUTIVE INTELLIGENCE SUITE', 'ليو مودا — سويت ذكاء الأعمال')}</span>
    <span>{T('HVIA ARCHITECTURE', 'هيكل HVIA')} <span class="fg">v2.4.2</span> · {T('DATA WINDOW', 'نطاق البيانات')} {f_start:%b %Y} — {f_end:%b %Y}</span>
</div>
""", unsafe_allow_html=True)