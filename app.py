#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
app.py — Yulia's Personal Finance Dashboard
Run with:  streamlit run app.py
"""

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

# ─── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="דשבורד פיננסי | יוליה",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── CSS: RTL, dark navy theme, no sidebar, typography ───────────────────────
st.markdown("""
<style>
/* UNIVERSAL OVERRIDE: Arial font on all elements */
* { font-family: Arial, sans-serif !important; }

/* Global RTL + base font */
html, body, [class*="css"] {
    direction: rtl;
    text-align: right;
    font-family: Arial, sans-serif !important;
    background-color: #0b0f1e !important;
    color: #e2e8f0;
}
.main, .block-container, [data-testid="stAppViewContainer"],
[data-testid="stMain"], section.main { background-color: #0b0f1e !important; }

/* Hide sidebar */
[data-testid="stSidebar"]                { display: none !important; }
[data-testid="stSidebarCollapsedControl"]{ display: none !important; }

/* Main padding */
.main .block-container { padding-top: 0.5rem; padding-left: 2rem; padding-right: 2rem; }

/* ── KPI cards ──────────────────────────────────────────────────────────── */
.kpi-card {
    background: #141929;
    border-radius: 14px;
    padding: 22px 24px;
    text-align: center;
    border: 1px solid rgba(99,102,241,0.18);
    box-shadow: 0 4px 28px rgba(0,0,0,0.5);
}
.kpi-label {
    font-size: 1.2rem;
    color: #94a3b8;
    font-weight: 600;
    font-family: Arial, sans-serif;
    margin-bottom: 10px;
    letter-spacing: 0;
    text-transform: none;
}
.kpi-value         { font-size: 2.1rem; font-weight: 800; line-height: 1.1; letter-spacing: -0.01em; }
.kpi-value.income  { color: #10b981; }
.kpi-value.expense { color: #f43f5e; }
.kpi-value.net-pos { color: #22d3ee; }
.kpi-value.net-neg { color: #fb923c; }

/* ── Focus / tracking cards ─────────────────────────────────────────────── */
.focus-card {
    background: #141929;
    border-radius: 10px;
    text-align: center;
    border: 1px solid rgba(255,255,255,0.06);
    border-top: 3px solid;
}
.focus-label { font-size: 0.92rem; color: #94a3b8; font-weight: 600;
               font-family: Arial, sans-serif;
               margin-bottom: 6px; text-transform: none; letter-spacing: 0; }
.focus-value { font-size: 1.0rem; font-weight: 800; }

/* ── Section headers ────────────────────────────────────────────────────── */
.section-header {
    font-size: 1.35rem;
    font-weight: 700;
    color: #e2e8f0;
    font-family: Arial, sans-serif;
    padding: 0 0 10px 0;
    border-bottom: 2px solid rgba(99,102,241,0.30);
    margin-bottom: 18px;
    letter-spacing: -0.01em;
}

/* ── Insurance drill-down items ─────────────────────────────────────────── */
.ins-item {
    background: #1a2035;
    border-radius: 8px;
    padding: 8px 14px;
    margin: 4px 0;
    display: flex;
    justify-content: space-between;
    font-size: 0.92rem;
    color: #e2e8f0;
    border: 1px solid rgba(255,255,255,0.06);
}
.ins-amount { color: #8b5cf6; font-weight: 700; }

/* ── Dataframe / data_editor RTL ────────────────────────────────────────── */
.stDataFrame { direction: rtl; }
.stDataFrame th, .stDataFrame td { text-align: right !important; }

/* ── INPUT FIELDS: Cream background with dark text ────────────────────────── */
/* Text inputs, search, number inputs */
input[type="text"],
input[type="search"],
input[type="number"],
input[type="date"],
input[type="time"],
textarea,
[data-baseweb="input"] input {
    background-color: #FFFEF0 !important;
    color: #000000 !important;
    font-family: Arial, sans-serif !important;
}

/* Selectbox / Combobox when closed (normal state) */
[data-baseweb="select"] > div:first-child,
[role="combobox"] {
    background-color: #FFFEF0 !important;
    color: #000000 !important;
}

/* Placeholder text - light gray for helper text */
input::placeholder,
textarea::placeholder {
    color: #888888 !important;
}

/* ── DROPDOWN LISTS: Keep original white styling (DO NOT CHANGE) ────────────── */
/* When user opens a dropdown - keep white background and dark text */
[data-baseweb="popover"],
[data-baseweb="menu"],
[data-baseweb="select"] [role="listbox"],
[data-baseweb="list"] {
    background-color: #ffffff !important;
    color: #1e293b !important;
}
[data-baseweb="popover"] *,
[data-baseweb="menu"] *,
[data-baseweb="select"] [role="listbox"] *,
[data-baseweb="list"] * {
    color: #1e293b !important;
}
[data-baseweb="option"],
[data-baseweb="menu-item"],
li[role="option"] {
    background-color: #ffffff !important;
    color: #1e293b !important;
}
[data-baseweb="option"]:hover,
[data-baseweb="menu-item"]:hover,
li[role="option"]:hover {
    background-color: #d1fae5 !important;
    color: #064e3b !important;
}
[data-baseweb="option"][aria-selected="true"],
li[role="option"][aria-selected="true"] {
    background-color: #6ee7b7 !important;
    color: #064e3b !important;
}
/* Search / input inside dropdown */
[data-baseweb="popover"] input,
[data-baseweb="select"] input {
    color: #1e293b !important;
    background-color: #f8fafc !important;
}
[data-baseweb="popover"] input::placeholder { color: #94a3b8 !important; }

/* ── Widget labels ──────────────────────────────────────────────────────── */
label, .stSelectbox label, .stRadio label, .stTextInput label {
    color: #7c8db5 !important;
    font-weight: 600 !important;
    font-size: 0.80rem !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* ── Tabs — real tab-strip look ─────────────────────────────────────────── */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background-color: #0b0f1e !important;
    border-bottom: 2px solid rgba(99,102,241,0.30) !important;
    gap: 6px !important;
    align-items: flex-end !important;
    padding: 0 4px !important;
}
[data-testid="stTabs"] button[data-baseweb="tab"] {
    color: #64748b !important;
    font-size: 1.53rem !important;
    font-weight: 700 !important;
    font-family: Arial, sans-serif !important;
    background: #0b0f1e !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
    border-bottom: none !important;
    border-radius: 10px 10px 0 0 !important;
    padding: 10px 28px 12px !important;
    margin-bottom: -2px !important;
    transition: background 0.15s !important;
}
[data-testid="stTabs"] button[data-baseweb="tab"]:hover {
    background: #253858 !important;
    color: #cbd5e1 !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: #22d3ee !important;
    font-weight: 800 !important;
    background: #0b0f1e !important;
    border-color: rgba(99,102,241,0.40) !important;
    border-bottom: 2px solid #ef4444 !important;
}
[data-testid="stTabPanel"] { background-color: #0b0f1e !important; }

/* ── Hide Streamlit chrome ──────────────────────────────────────────────── */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }

/* ── Radio button spacing + option text ─────────────────────────────────── */
div[data-testid="stRadio"] label { gap: 8px !important; }
div[data-testid="stRadio"] label p { margin: 0 !important; color: #e2e8f0 !important;
    font-size: 0.95rem !important; text-transform: none !important; letter-spacing: 0 !important; }

/* ── INPUT FIELDS: Cream background with dark text ────────────────────────── */
/* Text inputs, search, number inputs */
input[type="text"],
input[type="search"],
input[type="number"],
input[type="date"],
input[type="time"],
textarea,
[data-baseweb="input"] input {
    background-color: #FFFEF0 !important;
    color: #000000 !important;
    font-family: Arial, sans-serif !important;
}

/* Selectbox / Combobox when closed (normal state) */
[data-baseweb="select"] > div:first-child,
[role="combobox"] {
    background-color: #FFFEF0 !important;
    color: #000000 !important;
}

/* Placeholder text - light gray for helper text */
input::placeholder,
textarea::placeholder {
    color: #888888 !important;
}

/* ── DROPDOWN LISTS: Keep original white styling (DO NOT CHANGE) ────────────── */
/* When user opens a dropdown - keep white background and dark text */
[data-baseweb="popover"],
[data-baseweb="menu"],
[data-baseweb="select"] [role="listbox"],
[data-baseweb="list"] {
    background-color: #ffffff !important;
    color: #1e293b !important;
}
[data-baseweb="popover"] *,
[data-baseweb="menu"] *,
[data-baseweb="select"] [role="listbox"] *,
[data-baseweb="list"] * {
    color: #1e293b !important;
}
[data-baseweb="option"],
[data-baseweb="menu-item"],
li[role="option"] {
    background-color: #ffffff !important;
    color: #1e293b !important;
}
[data-baseweb="option"]:hover,
[data-baseweb="menu-item"]:hover,
li[role="option"]:hover {
    background-color: #d1fae5 !important;
    color: #064e3b !important;
}
[data-baseweb="option"][aria-selected="true"],
li[role="option"][aria-selected="true"] {
    background-color: #6ee7b7 !important;
    color: #064e3b !important;
}
/* Search / input inside dropdown */
[data-baseweb="popover"] input,
[data-baseweb="select"] input {
    color: #1e293b !important;
    background-color: #f8fafc !important;
}
[data-baseweb="popover"] input::placeholder { color: #94a3b8 !important; }

/* ── Sticky top-controls bar ────────────────────────────────────────────── */
section[data-testid="stMain"] > div.block-container
    > div[data-testid="stVerticalBlock"]
    > div[data-testid="stVerticalBlock"]:first-child {
    position: sticky !important;
    top: 0 !important;
    z-index: 999 !important;
    background-color: #0b0f1e !important;
    padding-bottom: 10px !important;
    border-bottom: 1px solid rgba(255,255,255,0.08) !important;
}

/* ── All buttons — dashboard font + size ───────────────────────────────── */
[data-testid="stButton"] > button,
[data-testid="stFormSubmitButton"] > button {
    font-family: Arial, sans-serif !important;
    font-size: 1.05rem !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
}

/* ── Primary buttons → light green ─────────────────────────────────────── */
[data-testid="stButton"] > button[kind="primaryFormSubmit"],
[data-testid="stButton"] > button[kind="primary"],
[data-testid="stFormSubmitButton"] > button,
button[data-testid="baseButton-primary"],
button[data-testid="baseButton-primaryFormSubmit"] {
    background-color: #6ee7b7 !important;
    color: #1e293b !important;
    border: 1px solid #34d399 !important;
    font-weight: 700 !important;
}
[data-testid="stButton"] > button[kind="primaryFormSubmit"]:hover,
[data-testid="stButton"] > button[kind="primary"]:hover,
button[data-testid="baseButton-primary"]:hover,
button[data-testid="baseButton-primaryFormSubmit"]:hover {
    background-color: #34d399 !important;
    border-color: #10b981 !important;
}

/* ── Refresh button — compact, large icon, dark color on green ──────────── */
button[data-testid="baseButton-primary"][kind="primary"] {
    padding: 4px 18px !important;
    min-height: 34px !important;
    font-size: 1.6rem !important;
    line-height: 1 !important;
    color: #064e3b !important;
    border: 1px solid #34d399 !important;
}

/* ── Multiselect selected tags → dark text on light green ───────────────── */
[data-baseweb="tag"] {
    background-color: #6ee7b7 !important;
    border-color: #34d399 !important;
}
[data-baseweb="tag"] span { color: #064e3b !important; font-weight: 600 !important; }
[data-baseweb="tag"] svg { fill: #065f46 !important; }

/* ── Radio selection circle → light green ───────────────────────────────── */
[data-baseweb="radio"] > div:first-child { border-color: #6ee7b7 !important; }
[data-baseweb="radio"][aria-checked="true"] > div:first-child {
    background-color: #6ee7b7 !important;
    border-color: #6ee7b7 !important;
}
label[aria-checked="true"] [data-baseweb="radio"] > div:first-child {
    background-color: #6ee7b7 !important;
    border-color: #6ee7b7 !important;
}

/* ── Metrics ────────────────────────────────────────────────────────────── */
[data-testid="stMetric"] { background: #141929; border-radius: 10px; padding: 12px 16px;
                           border: 1px solid rgba(255,255,255,0.06); }
[data-testid="stMetricLabel"] p { color: #7c8db5 !important; font-size: 0.78rem !important;
                                   text-transform: uppercase; letter-spacing: 0.06em; }
[data-testid="stMetricValue"] { color: #e2e8f0 !important; }
</style>
""", unsafe_allow_html=True)

# ─── JS: inject into parent doc — dropdown styles + canvas cell-selection patch ──
components.html("""<script>
(function() {
  var win = window.parent;
  var doc = win.document;

  /* ── 1. Inject CSS for dropdown portals + tab classes ── */
  var style = doc.getElementById('gdg-dropdown-override');
  if (!style) {
    style = doc.createElement('style');
    style.id = 'gdg-dropdown-override';
    doc.head.appendChild(style);
  }
  style.textContent = [
    '[role="listbox"]{background-color:#ffffff!important}',
    '[role="option"]{color:#1e293b!important;background-color:#ffffff!important}',
    '[role="option"]:hover{background-color:#d1fae5!important;color:#064e3b!important}',
    '[role="option"][aria-selected="true"]{background-color:#6ee7b7!important;color:#064e3b!important;font-weight:700!important}'
  ].join('');

  /* ── 2. Monkey-patch canvas fillStyle/strokeStyle to turn Streamlit red → green ── */
  var proto = win.CanvasRenderingContext2D.prototype;
  if (!proto.__gdgPatched) {
    proto.__gdgPatched = true;
    var descFill   = Object.getOwnPropertyDescriptor(proto, 'fillStyle');
    var descStroke = Object.getOwnPropertyDescriptor(proto, 'strokeStyle');
    function mapRed(c) {
      if (typeof c !== 'string') return c;
      var s = c.replace(/\\s/g,'').toLowerCase();
      if (s === '#ff4b4b' || s === 'rgb(255,75,75)') return '#6ee7b7';
      if (s.indexOf('rgba(255,75,75,') === 0 || s.indexOf('rgba(255, 75, 75,') === 0)
        return s.replace('255,75,75','110,231,183').replace('255, 75, 75','110, 231, 183');
      return c;
    }
    Object.defineProperty(proto, 'fillStyle',   {set:function(v){descFill.set.call(this,mapRed(v));},get:function(){return descFill.get.call(this);},configurable:true});
    Object.defineProperty(proto, 'strokeStyle', {set:function(v){descStroke.set.call(this,mapRed(v));},get:function(){return descStroke.get.call(this);},configurable:true});
  }

})();
</script>""", height=0)


# ══════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ══════════════════════════════════════════════════════════════════════════════
DATA_FILE      = Path(__file__).parent / "Master_Data.csv"
RULES_FILE     = Path(__file__).parent / "MY BUDGET" / "Mapping_Rules.json"
LEVELS_FILE    = Path(__file__).parent / "MY BUDGET" / "Categories_Leveling.json"
OVERRIDES_FILE = Path(__file__).parent / "MY BUDGET" / "Manual_Overrides.json"
if not RULES_FILE.exists():
    RULES_FILE = Path(__file__).parent / "Mapping_Rules.json"

HEB_MONTH_ORDER = {
    "ינואר": 1, "פברואר": 2, "מרץ": 3, "אפריל": 4,
    "מאי": 5, "יוני": 6, "יולי": 7, "אוגוסט": 8,
    "ספטמבר": 9, "אוקטובר": 10, "נובמבר": 11, "דצמבר": 12,
}

# Maps any category value → main group (for pie chart grouping)
# Keyword-based: if the category string contains any of the keywords → group
CATEGORY_TO_GROUP = [
    # ⚠️ IMPORTANT: Only add entries here for KNOWN VARIANTS that differ from JSON
    # The primary mapping is from _CATEGORY_MAPPING (built from JSON)
    # These are ONLY for legacy/alternate names that might appear in data

    # Known variants and alternate spellings found in data
    ("יעוץ אנשי מקצוע (משפחה)", "משפחה והשכלה"),  # Variant with parentheses
    ("שירותי בריאות",               "בריאות וטיפוח"),  # Short version
    ("יעוץ אנשי מקצוע (עסק)",       "שירותים עסקיים"),  # Variant with parentheses
]

FOCUS_DEFS = [
    ("מזון",           "מזון, סופר ומכולת",  "#6366f1"),
    ("דלק",            "דלק וטעינה",          "#fb923c"),
    ("תחבורה ציבורית", "תחבורה ציבורית",      "#10b981"),
    ("אוכלים בחוץ",   "אוכלים בחוץ",         "#f43f5e"),
    ("ביטוחים",        "ביטוח",               "#8b5cf6"),
    ("בינה מלאכותית",  "בינה מלאכותית",       "#22d3ee"),
    ("בגדים",          "בגדים, נעליים",       "#f9a8d4"),
    ("כבישי אגרה",     "כבישי אגרה",          "#94a3b8"),
]

# ── Category ordering (follows Categories_Leveling.json) ──────────────────────
# Maps data's MainCategory names → display order index
_MAIN_CAT_ORDER = {
    "קניות לבית":       0,
    "בריאות וטיפוח":    1,
    "משק בית":          2,
    "רכב ותחבורה":      3,
    "פנאי והעשרה":      4,   # JSON label: "פנאי, תרבות והעשרה"
    "משפחה והשכלה":     5,
    "שירותים פיננסיים": 6,
    "העסק שלי":         7,   # JSON label: "שירותים עסקיים"
    "תרומות":           8,
}

def _build_sub_cat_order():
    """Load subcategory ordering from Categories_Leveling.json."""
    order = {}
    try:
        with open(LEVELS_FILE, encoding="utf-8") as f:
            levels = json.load(f)
        idx = 0
        for section_cats in levels.values():   # הוצאות, הכנסות
            for subcats in section_cats.values():
                for sub in subcats:
                    if sub not in order:
                        order[sub] = idx
                        idx += 1
    except Exception:
        pass
    return order

_SUB_CAT_ORDER = _build_sub_cat_order()


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def month_sort_key(display_month):
    parts = str(display_month).strip().split()
    if len(parts) == 2:
        return (int(parts[1]), HEB_MONTH_ORDER.get(parts[0], 0))
    return (0, 0)


def short_label(display_month):
    """'דצמבר 2025' → '12/25'"""
    parts = str(display_month).strip().split()
    if len(parts) == 2:
        return f"{HEB_MONTH_ORDER.get(parts[0], 0)}/{str(parts[1])[-2:]}"
    return display_month


def fmt_ils(amount):
    return f"₪{amount:,.0f}"


def _build_category_mapping():
    """Build category → main_category mapping directly from Categories_Leveling.json"""
    mapping = {}
    try:
        with open(LEVELS_FILE, encoding="utf-8") as f:
            levels = json.load(f)
        # Iterate through "הוצאות" and "הכנסות" sections
        for section_name, groups in levels.items():
            # For each main category (like "קניות לבית", "משפחה והשכלה")
            for main_cat, subcats_list in groups.items():
                if isinstance(subcats_list, list):
                    # Map each subcategory to its main category
                    for subcat in subcats_list:
                        if subcat:  # Skip empty strings
                            mapping[subcat] = main_cat
    except Exception as e:
        st.error(f"שגיאה בקריאת קובץ קטגוריות: {e}")
    return mapping

_CATEGORY_MAPPING = _build_category_mapping()

def get_main_category(cat):
    """
    Get main category for a given category name.
    Searches in order:
    1. Exact match from JSON hierarchy
    2. Case-insensitive match from JSON hierarchy
    3. Fallback to CATEGORY_TO_GROUP (for legacy variants)
    4. Return category itself (never invent new groups)
    """
    if not cat or cat == "לא מסווג":
        return "לא מסווג"

    cat_str = str(cat).strip()

    # First: exact match in JSON mapping
    if cat_str in _CATEGORY_MAPPING:
        return _CATEGORY_MAPPING[cat_str]

    # Second: case-insensitive exact match
    cat_lower = cat_str.lower()
    for json_cat, main_cat in _CATEGORY_MAPPING.items():
        if json_cat.lower() == cat_lower:
            return main_cat

    # Third: fallback to CATEGORY_TO_GROUP for variants/legacy names
    for keyword, group in CATEGORY_TO_GROUP:
        if keyword.lower() in cat_lower:
            return group

    # If no match found, return the category itself (don't invent "אחר")
    # This ensures subcategories won't be lost
    return cat_str


def build_category_options(extra_cats=None):
    """Return flat list for SelectboxColumn: group headers prefixed with ── , subcats as-is.
    extra_cats: set of existing category values to append if not already in the hierarchy."""
    try:
        with open(LEVELS_FILE, encoding="utf-8") as f:
            tree = json.load(f)
    except Exception:
        tree = {}

    options = []
    in_hierarchy = set()

    for type_label, groups in tree.items():   # הוצאות / הכנסות
        options.append(f"══ {type_label} ══")
        for group, subs in groups.items():
            if subs:
                options.append(f"── {group}")
                for sub in subs:
                    options.append(sub)
                    in_hierarchy.add(sub)
            else:
                options.append(group)          # leaf group (e.g. אוכלים בחוץ)
                in_hierarchy.add(group)

    # Append any existing-in-data categories not yet in the hierarchy
    # so current cell values are always found and displayed correctly
    if extra_cats:
        leftover = sorted(c for c in extra_cats if c not in in_hierarchy and not is_separator(c))
        if leftover:
            options.append("── קיים בנתונים")
            options.extend(leftover)

    return options


def is_separator(val):
    return str(val).startswith("══") or str(val).startswith("──")


def months_in_range(all_months_asc, from_m, to_m):
    f = month_sort_key(from_m)
    t = month_sort_key(to_m)
    return [m for m in all_months_asc if f <= month_sort_key(m) <= t]


# ══════════════════════════════════════════════════════════════════════════════
# DATA LOADING
# ══════════════════════════════════════════════════════════════════════════════

def load_overrides():
    """Manual per-row category overrides keyed by 'Date|Merchant|Amount'."""
    if OVERRIDES_FILE.exists():
        with open(OVERRIDES_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_overrides(overrides):
    with open(OVERRIDES_FILE, "w", encoding="utf-8") as f:
        json.dump(overrides, f, ensure_ascii=False, indent=4)


def override_key(date_str, merchant, amount):
    """Stable key for a specific transaction."""
    return f"{date_str}|{merchant.strip()}|{round(float(amount), 2)}"


def _tdate_str(val):
    """Convert תאריך cell (datetime or str) → 'DD/MM/YYYY' string."""
    if hasattr(val, "strftime"):
        return val.strftime("%d/%m/%Y")
    return str(val)


@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(DATA_FILE, encoding="utf-8-sig", dtype={"Description": str})
    df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%Y", errors="coerce")
    df["Description"] = df["Description"].fillna("")
    df["Amount_ILS"] = pd.to_numeric(df["Amount_ILS"], errors="coerce").fillna(0)
    df["IsInsurance"] = df["IsInsurance"].astype(str).str.lower().isin(["true", "1", "yes"])
    # Apply manual per-row overrides (survive process_budget.py reruns)
    overrides = load_overrides()
    if overrides:
        def apply_override(row):
            date_str = ""
            if pd.notna(row["Date"]):
                date_str = row["Date"].strftime("%d/%m/%Y") if hasattr(row["Date"], "strftime") else str(row["Date"])
            key = override_key(
                date_str,
                str(row["Merchant"]),
                row["Amount_ILS"],
            )
            val = overrides.get(key)
            if val is None:
                return row["Category"]
            if isinstance(val, dict):
                return val.get("category", row["Category"])
            return val  # backward compat: plain string = category

        def apply_type_override(row):
            date_str = ""
            if pd.notna(row["Date"]):
                date_str = row["Date"].strftime("%d/%m/%Y") if hasattr(row["Date"], "strftime") else str(row["Date"])
            key = override_key(
                date_str,
                str(row["Merchant"]),
                row["Amount_ILS"],
            )
            val = overrides.get(key)
            if isinstance(val, dict) and "type" in val:
                return val["type"]
            return row["Type"]

        df["Category"] = df.apply(apply_override, axis=1)
        df["Type"]     = df.apply(apply_type_override, axis=1)
    df["MainCategory"] = df["Category"].apply(get_main_category)
    # Remove rows with NaT dates (invalid date entries)
    df = df[df["Date"].notna()]
    return df


def load_rules():
    if RULES_FILE.exists():
        with open(RULES_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_rules(rules):
    with open(RULES_FILE, "w", encoding="utf-8") as f:
        json.dump(rules, f, ensure_ascii=False, indent=4)


# ══════════════════════════════════════════════════════════════════════════════
# GUARD
# ══════════════════════════════════════════════════════════════════════════════

if not DATA_FILE.exists():
    st.error("קובץ Master_Data.csv לא נמצא.")
    st.info("כדי ליצור אותו, הרץ בטרמינל:\n```bash\npython3 process_budget.py\n```")
    st.stop()

df_all = load_data()

# Sorted ascending (for range logic), descending for UI display
# Exclude months with < 10 rows from CHARTS/AVERAGES (stray installment rows, artifacts)
_month_counts = df_all.groupby("Display_Month").size()
_valid_months = set(_month_counts[_month_counts >= 10].index)
all_months_asc  = sorted(_valid_months, key=month_sort_key)
all_months_desc = list(reversed(all_months_asc))  # latest first in dropdown (charts/averages)

# All months (no count filter) — for the transaction table so manually added rows always appear
_all_months_set     = set(df_all["Display_Month"].dropna().unique())
all_months_asc_all  = sorted(_all_months_set, key=month_sort_key)
all_months_desc_all = list(reversed(all_months_asc_all))



# ══════════════════════════════════════════════════════════════════════════════
# PAGE NAVIGATION TABS
# ══════════════════════════════════════════════════════════════════════════════

tab_dashboard, tab_averages = st.tabs(["דשבורד", "ממוצעים חודשיים"])

with tab_dashboard:
    @st.fragment
    def _dashboard_fragment():
        # ══════════════════════════════════════════════════════════════════════════════
        # TOP CONTROLS BAR (FIX 13 — no sidebar)
        # ══════════════════════════════════════════════════════════════════════════════

        with st.container():
            ctrl1, ctrl2, ctrl3, ctrl4 = st.columns([2, 3, 3, 1])

            with ctrl1:
                view_mode = st.radio(
                    "תצוגה",
                    options=["חודש בודד", "תקופה"],
                    index=0,
                    horizontal=True,
                    key="view_mode",
                )

            if view_mode == "חודש בודד":
                with ctrl2:
                    selected_month = st.selectbox(
                        "בחרי חודש",
                        options=all_months_desc,
                        index=0,
                        key="sel_single",
                    )
                with ctrl3:
                    st.markdown("<div style='margin-top:28px'></div>", unsafe_allow_html=True)
                    if st.button("⟳", key="refresh_btn", type="primary"):
                        st.cache_data.clear()
                        st.rerun(scope="app")
                selected_months = [selected_month]
                period_label = selected_month
            else:
                with ctrl2:
                    from_month = st.selectbox("מחודש", options=all_months_desc, index=len(all_months_desc) - 1, key="sel_from")
                with ctrl3:
                    to_month = st.selectbox("עד חודש", options=all_months_desc, index=0, key="sel_to")
                with ctrl4:
                    st.markdown("<div style='margin-top:28px'></div>", unsafe_allow_html=True)
                    if st.button("⟳", key="refresh_btn", type="primary"):
                        st.cache_data.clear()
                        st.rerun(scope="app")
                # Ensure from <= to
                if month_sort_key(from_month) > month_sort_key(to_month):
                    from_month, to_month = to_month, from_month
                selected_months = months_in_range(all_months_asc, from_month, to_month)
                period_label = f"{from_month} — {to_month}"

        st.markdown(f"<h2 style='text-align:right; color:#e2e8f0; margin:0 0 12px 0;'>דשבורד פיננסי — {period_label}</h2>",
                    unsafe_allow_html=True)

        # ── Filter to selected period ──────────────────────────────────────────────────
        df_period = df_all[df_all["Display_Month"].isin(selected_months)].copy()
        df_exp    = df_period[df_period["Type"] == "הוצאה"]
        df_inc    = df_period[df_period["Type"] == "הכנסה"]
        df_cred   = df_period[df_period["Type"] == "זיכוי"]

        total_income   = df_inc["Amount_ILS"].sum()
        total_credits  = df_cred["Amount_ILS"].sum()
        total_expense  = df_exp["Amount_ILS"].sum() - total_credits  # net of credits
        net_balance    = total_income - total_expense

        # חישוב ממוצע תקין - מספר כל החודשים בטווח, לא רק חודשים עם נתונים
        if view_mode == "חודש בודד":
            n_months = 1
        else:
            # מחשבים את מספר החודשים הכולל בטווח (כולל חודשים ללא נתונים)
            from_idx = all_months_asc.index(from_month) if from_month in all_months_asc else 0
            to_idx = all_months_asc.index(to_month) if to_month in all_months_asc else len(all_months_asc) - 1
            n_months = max(to_idx - from_idx + 1, 1)

        is_single     = (n_months == 1)


        # ══════════════════════════════════════════════════════════════════════════════
        # KPI CARDS
        # ══════════════════════════════════════════════════════════════════════════════

        avg_income  = total_income  / n_months
        avg_expense = total_expense / n_months
        avg_net     = avg_income - avg_expense
        kpi_suffix  = "" if is_single else " (ממוצע חודשי)"

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"""<div class="kpi-card">
                <div class="kpi-label">{'סך הכנסות' if is_single else 'ממוצע הכנסה חודשי'}</div>
                <div class="kpi-value income">{fmt_ils(avg_income)}</div>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""<div class="kpi-card">
                <div class="kpi-label">{'סך הוצאות' if is_single else 'ממוצע הוצאה חודשי'}</div>
                <div class="kpi-value expense">{fmt_ils(avg_expense)}</div>
            </div>""", unsafe_allow_html=True)
        with c3:
            net_class = "net-pos" if avg_net >= 0 else "net-neg"
            net_sign  = "+" if avg_net >= 0 else ""
            net_label = "יתרה נטו" if is_single else ("ממוצע חיסכון חודשי" if avg_net >= 0 else "ממוצע גרעון חודשי")
            st.markdown(f"""<div class="kpi-card">
                <div class="kpi-label">{net_label}</div>
                <div class="kpi-value {net_class}">{net_sign}{fmt_ils(avg_net)}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)


        # ══════════════════════════════════════════════════════════════════════════════
        # FOCUS PANEL (FIX 8: total for single month, avg for range)
        # ══════════════════════════════════════════════════════════════════════════════

        st.markdown('<div class="section-header">מעקב שוטף</div>', unsafe_allow_html=True)
        focus_cols = st.columns(8)

        for col, (label, keyword, color) in zip(focus_cols, FOCUS_DEFS):
            raw_exp  = df_exp[df_exp["Category"].str.contains(keyword, na=False, regex=False)]["Amount_ILS"].sum()
            raw_cred = df_cred[df_cred["Category"].str.contains(keyword, na=False, regex=False)]["Amount_ILS"].sum()
            raw    = raw_exp - raw_cred
            amount = raw if is_single else raw / n_months
            with col:
                st.markdown(f"""<div class="focus-card" style="border-color:{color};padding:10px 6px;">
                    <div class="focus-label" style="font-size:0.70rem">{label}</div>
                    <div class="focus-value" style="color:{color};font-size:1.05rem">{fmt_ils(amount)}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)




        # ══════════════════════════════════════════════════════════════════════════════
        # CHARTS ROW 2 — income vs expenses bar | savings/deficit bar
        # ══════════════════════════════════════════════════════════════════════════════

        bar_left, bar_right = st.columns(2, gap="large")

        # Last 12 valid months only (no future / artifact months)
        _trend_months_12 = all_months_asc[-12:] if len(all_months_asc) >= 12 else all_months_asc

        # ─── Income vs Expenses bar ───────────────────────────────────────────────────
        with bar_left:
            st.markdown('<div class="section-header">הכנסות מול הוצאות לאורך תקופה</div>', unsafe_allow_html=True)

            exp_by_m  = df_all[df_all["Type"]=="הוצאה"].groupby("Display_Month")["Amount_ILS"].sum()
            cred_by_m = df_all[df_all["Type"]=="זיכוי"].groupby("Display_Month")["Amount_ILS"].sum()
            inc_by_m  = df_all[df_all["Type"]=="הכנסה"].groupby("Display_Month")["Amount_ILS"].sum()
            trend_rows = []
            for m in _trend_months_12:
                net_exp = exp_by_m.get(m, 0) - cred_by_m.get(m, 0)
                # Allow negative values when credits exceed expenses
                trend_rows.append({"Display_Month": m, "Type": "הוצאות", "Amount_ILS": net_exp})
                trend_rows.append({"Display_Month": m, "Type": "הכנסות", "Amount_ILS": inc_by_m.get(m, 0)})
            trend = pd.DataFrame(trend_rows)
            trend["sort_key"]    = trend["Display_Month"].apply(month_sort_key)
            trend["short_month"] = trend["Display_Month"].apply(short_label)
            trend = trend.sort_values("sort_key")

            # KPIs — divide by 12 (full year period) even if only 8 months have data
            # Allow negative values when credits exceed expenses
            _avg_inc_12 = sum(inc_by_m.get(m, 0) for m in _trend_months_12) / 12
            _avg_exp_12 = sum(exp_by_m.get(m,0)-cred_by_m.get(m,0) for m in _trend_months_12) / 12

            bar_chart_col, bar_kpi_col = st.columns([5, 1])
            with bar_kpi_col:
                st.markdown(f"""
                <div style="margin-top:30px;text-align:center">
                    <div style="color:#10b981;font-size:0.78rem;font-weight:600;margin-bottom:2px">הכנסה ממוצעת</div>
                    <div style="color:#10b981;font-size:1.05rem;font-weight:800">{fmt_ils(_avg_inc_12)}</div>
                    <div style="border-top:1px solid rgba(255,255,255,0.08);margin:10px 0"></div>
                    <div style="color:#f43f5e;font-size:0.78rem;font-weight:600;margin-bottom:2px">הוצאה ממוצעת</div>
                    <div style="color:#f43f5e;font-size:1.05rem;font-weight:800">{fmt_ils(_avg_exp_12)}</div>
                </div>""", unsafe_allow_html=True)

            with bar_chart_col:
                fig_bar = px.bar(
                    trend, x="short_month", y="Amount_ILS", color="Type",
                    barmode="group",
                    color_discrete_map={"הוצאות": "#f38ba8", "הכנסות": "#a6e3a1"},
                    labels={"Amount_ILS": "סכום (₪)", "short_month": "חודש", "Type": ""},
                )
                fig_bar.update_traces(
                    texttemplate="₪%{y:,.0f}",
                    textposition="outside",
                    textfont=dict(size=10, color="#e2e8f0", family="Arial"),
                    hovertemplate="<b>%{x}</b><br>₪%{y:,.0f}<extra></extra>",
                    cliponaxis=False,
                )

                # Add horizontal line at y=0 to show the axis clearly for negative values
                fig_bar.add_hline(y=0, line=dict(color="rgba(255,255,255,0.20)", width=1, dash="dash"))

                selected_short = [short_label(m) for m in selected_months]
                short_list = trend["short_month"].unique().tolist()
                for sm in selected_short:
                    if sm in short_list:
                        idx = short_list.index(sm)
                        fig_bar.add_shape(
                            type="rect", x0=idx - 0.5, x1=idx + 0.5, y0=0, y1=1,
                            xref="x", yref="paper",
                            fillcolor="rgba(99,102,241,0.10)",
                            line=dict(color="#6366f1", width=1, dash="dot"),
                        )

                # Calculate axis range to include negative values with proper padding
                trend_min = trend["Amount_ILS"].min()
                trend_max = trend["Amount_ILS"].max()

                # Calculate padding (20% of range or minimum 10% above/below zero)
                if trend_min < 0 and trend_max > 0:
                    # Both positive and negative values exist
                    range_span = trend_max - trend_min
                    padding = range_span * 0.15
                    axis_min = trend_min - padding
                    axis_max = trend_max + padding
                elif trend_min < 0:
                    # All negative - add padding below and above zero
                    axis_min = trend_min * 1.2
                    axis_max = 0
                else:
                    # All positive - start from zero
                    axis_min = 0
                    axis_max = trend_max * 1.2

                fig_bar.update_layout(
                    paper_bgcolor="#0b0f1e", plot_bgcolor="#0b0f1e",
                    font=dict(color="#e2e8f0", size=12),
                    xaxis=dict(tickangle=-35, gridcolor="rgba(255,255,255,0.06)", title_text="",
                               tickfont=dict(color="#b0bec5", size=12),
                               showticklabels=True, type="category"),
                    yaxis=dict(gridcolor="rgba(255,255,255,0.06)", tickformat=",.0f", tickprefix="₪", title_text="",
                               tickfont=dict(color="#b0bec5", size=12),
                               range=[axis_min, axis_max],
                               autorange=False),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                                font=dict(size=12, color="#e2e8f0"),
                                bgcolor="rgba(0,0,0,0)", title_text=""),
                    margin=dict(t=60, b=60, l=10, r=10), height=400, bargap=0.25,
                    uniformtext=dict(minsize=7, mode="hide"),
                )
                st.plotly_chart(fig_bar, use_container_width=True)

        # ─── Savings / Deficit bar ────────────────────────────────────────────────────
        with bar_right:
            st.markdown('<div class="section-header">חיסכון / גרעון לאורך תקופה</div>', unsafe_allow_html=True)

            inc_by_month  = df_all[df_all["Type"] == "הכנסה"].groupby("Display_Month")["Amount_ILS"].sum()
            exp_by_month  = df_all[df_all["Type"] == "הוצאה"].groupby("Display_Month")["Amount_ILS"].sum()
            cred_by_month = df_all[df_all["Type"] == "זיכוי"].groupby("Display_Month")["Amount_ILS"].sum()
            savings_df = pd.DataFrame({"Display_Month": _trend_months_12})
            savings_df["income"]  = savings_df["Display_Month"].map(inc_by_month).fillna(0)
            savings_df["expense"] = savings_df["Display_Month"].map(exp_by_month).fillna(0) - \
                                    savings_df["Display_Month"].map(cred_by_month).fillna(0)
            savings_df["net"]     = savings_df["income"] - savings_df["expense"]
            savings_df["sort_key"]    = savings_df["Display_Month"].apply(month_sort_key)
            savings_df["short_month"] = savings_df["Display_Month"].apply(short_label)
            savings_df = savings_df.sort_values("sort_key")
            savings_df["color"] = savings_df["net"].apply(lambda v: "#a6e3a1" if v >= 0 else "#f38ba8")

            # KPI: single overall average (positive = savings, negative = deficit)
            _avg_net_12 = savings_df["net"].mean()
            _net_color  = "#10b981" if _avg_net_12 >= 0 else "#f43f5e"
            _net_label  = "חיסכון ממוצע" if _avg_net_12 >= 0 else "גרעון ממוצע"
            _net_prefix = "+" if _avg_net_12 >= 0 else ""

            sav_chart_col, sav_kpi_col = st.columns([5, 1])
            with sav_kpi_col:
                st.markdown(f"""
                <div style="margin-top:30px;text-align:center">
                    <div style="color:{_net_color};font-size:0.78rem;font-weight:600;margin-bottom:2px">{_net_label}</div>
                    <div style="color:{_net_color};font-size:1.05rem;font-weight:800">{_net_prefix}{fmt_ils(_avg_net_12)}</div>
                </div>""", unsafe_allow_html=True)

            with sav_chart_col:
                fig_sav = go.Figure(go.Bar(
                    x=savings_df["short_month"],
                    y=savings_df["net"],
                    marker_color=savings_df["color"],
                    text=savings_df["net"].apply(lambda v: f"{'+'if v>=0 else ''}₪{v:,.0f}"),
                    textposition="outside",
                    textfont=dict(size=11, color="#e2e8f0", family="Arial"),
                    hovertemplate="<b>%{x}</b><br>%{text}<extra></extra>",
                    cliponaxis=False,
                ))

                for sm in selected_short:
                    if sm in savings_df["short_month"].values:
                        fig_sav.add_shape(
                            type="rect",
                            x0=list(savings_df["short_month"]).index(sm) - 0.5,
                            x1=list(savings_df["short_month"]).index(sm) + 0.5,
                            y0=savings_df["net"].min() * 1.15, y1=savings_df["net"].max() * 1.15,
                            xref="x", yref="y",
                            fillcolor="rgba(99,102,241,0.10)",
                            line=dict(color="#6366f1", width=1, dash="dot"),
                        )

                fig_sav.add_hline(y=0, line=dict(color="rgba(255,255,255,0.20)", width=1, dash="dot"))

                # Calculate proper axis range for savings chart with negative values
                sav_min = savings_df["net"].min()
                sav_max = savings_df["net"].max()
                if sav_min < 0 and sav_max > 0:
                    range_span = sav_max - sav_min
                    padding = range_span * 0.15
                    sav_axis_min = sav_min - padding
                    sav_axis_max = sav_max + padding
                elif sav_min < 0:
                    sav_axis_min = sav_min * 1.2
                    sav_axis_max = 0
                else:
                    sav_axis_min = 0
                    sav_axis_max = sav_max * 1.2

                fig_sav.update_layout(
                    paper_bgcolor="#0b0f1e", plot_bgcolor="#0b0f1e",
                    font=dict(color="#e2e8f0", size=12),
                    xaxis=dict(tickangle=-35, gridcolor="rgba(255,255,255,0.06)", title_text="",
                               tickfont=dict(color="#b0bec5", size=12), type="category"),
                    yaxis=dict(gridcolor="rgba(255,255,255,0.06)", tickformat=",.0f", tickprefix="₪", title_text="",
                               tickfont=dict(color="#b0bec5", size=12),
                               range=[sav_axis_min, sav_axis_max],
                               autorange=False),
                    margin=dict(t=30, b=60, l=65, r=10), height=380, bargap=0.3,
                    uniformtext=dict(minsize=7, mode="hide"),
                )
                st.plotly_chart(fig_sav, use_container_width=True)


        # ══════════════════════════════════════════════════════════════════════════════
        # CATEGORY TREND — bar chart (fragment to prevent scroll jump)
        # ══════════════════════════════════════════════════════════════════════════════

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-header">מה היה בשנה האחרונה - לפי קטגוריה</div>', unsafe_allow_html=True)

        CAT_TICK  = "#b0bec5"
        CAT_LABEL = "#e2e8f0"
        CAT_GRID  = "rgba(255,255,255,0.06)"

        @st.fragment
        def _cat_trend_fragment():
            all_categories_trend = sorted(df_all["Category"].unique())

            ctrl_c1, ctrl_c2 = st.columns([3, 1])
            with ctrl_c1:
                selected_cats = st.multiselect(
                    "בחרי קטגוריות:",
                    options=all_categories_trend,
                    default=[all_categories_trend[0]] if all_categories_trend else [],
                    key="cat_trend",
                )
            with ctrl_c2:
                display_mode = st.radio(
                    "תצוגה:",
                    options=["לפי קטגוריה", "סכום כולל"],
                    index=0,
                    horizontal=True,
                    key="cat_trend_mode",
                )

            if not selected_cats:
                st.info("בחרי לפחות קטגוריה אחת")
                return

            _cat_df = df_all[df_all["Category"].isin(selected_cats)]
            _cat_exp_grp  = _cat_df[_cat_df["Type"] == "הוצאה"].groupby(["Display_Month", "Category"])["Amount_ILS"].sum()
            _cat_cred_grp = _cat_df[_cat_df["Type"] == "זיכוי"].groupby(["Display_Month", "Category"])["Amount_ILS"].sum()
            _cat_inc_grp  = _cat_df[_cat_df["Type"] == "הכנסה"].groupby(["Display_Month", "Category"])["Amount_ILS"].sum()

            # IMPORTANT: Always use last 12 months for "מה היה בשנה האחרונה"
            # (not the selected period from the top controls)
            last_12_months = all_months_asc[-12:] if len(all_months_asc) >= 12 else all_months_asc

            # Show all months in the last 12 months (including those with zero data)
            # Allow negative values when credits exceed expenses
            _cat_rows = []
            for m in last_12_months:
                for cat in selected_cats:
                    net_exp = _cat_exp_grp.get((m, cat), 0) - _cat_cred_grp.get((m, cat), 0)
                    inc_val = _cat_inc_grp.get((m, cat), 0)
                    amount  = net_exp + inc_val
                    _cat_rows.append({"Display_Month": m, "Category": cat, "Amount_ILS": amount})

            cat_trend = pd.DataFrame(_cat_rows)
            cat_trend["sort_key"]    = cat_trend["Display_Month"].apply(month_sort_key)
            cat_trend["short_month"] = cat_trend["Display_Month"].apply(short_label)
            cat_trend = cat_trend.sort_values(["sort_key", "Category"])

            # Combined monthly totals for average line
            _cat_totals = cat_trend.groupby(["Display_Month", "short_month", "sort_key"])["Amount_ILS"].sum().reset_index()
            _cat_totals = _cat_totals.sort_values("sort_key")
            # Average divided by 12 months (full year period) since we're showing last 12 months
            cat_avg = _cat_totals["Amount_ILS"].sum() / len(last_12_months) if not _cat_totals.empty else 0

            cat_trend_col, cat_kpi_col = st.columns([4, 1])

            with cat_kpi_col:
                st.markdown(f"""<div class="kpi-card" style="margin-top:30px">
                    <div class="kpi-label">ממוצע חודשי</div>
                    <div class="kpi-value" style="color:#6366f1; font-size:1.4rem">{fmt_ils(cat_avg)}</div>
                </div>""", unsafe_allow_html=True)

            with cat_trend_col:
                _multi = len(selected_cats) > 1

                if display_mode == "סכום כולל" or not _multi:
                    # Show single combined bar per month
                    plot_df = _cat_totals.rename(columns={"Amount_ILS": "Amount_ILS"})
                    fig_cat = px.bar(
                        plot_df, x="short_month", y="Amount_ILS",
                        color_discrete_sequence=["#89b4fa"],
                        labels={"Amount_ILS": "", "short_month": ""},
                    )
                    fig_cat.update_traces(
                        text=[f"₪{v:,.0f}" for v in plot_df["Amount_ILS"]],
                        textposition="outside",
                        textfont=dict(size=12, color=CAT_LABEL, family="Arial"),
                        hovertemplate="<b>%{x}</b><br>₪%{y:,.0f}<extra></extra>",
                        cliponaxis=False,
                    )
                    # Calculate range for single chart
                    plot_min = plot_df["Amount_ILS"].min() if not plot_df.empty else 0
                    plot_max = plot_df["Amount_ILS"].max() if not plot_df.empty else 1
                else:
                    # Show grouped bars per category with value labels
                    fig_cat = px.bar(
                        cat_trend, x="short_month", y="Amount_ILS",
                        color="Category", barmode="group",
                        labels={"Amount_ILS": "", "short_month": "", "Category": "קטגוריה"},
                    )
                    fig_cat.update_traces(
                        text=cat_trend["Amount_ILS"].apply(lambda v: f"₪{v:,.0f}"),
                        textposition="outside",
                        textfont=dict(size=9, color=CAT_LABEL, family="Arial"),
                        hovertemplate="<b>%{x}</b><br>%{fullData.name}: ₪%{y:,.0f}<extra></extra>",
                        cliponaxis=False,
                    )
                    # Calculate range for grouped chart
                    plot_min = cat_trend["Amount_ILS"].min() if not cat_trend.empty else 0
                    plot_max = cat_trend["Amount_ILS"].max() if not cat_trend.empty else 1

                # Calculate proper axis range for category chart with negative values
                if plot_min < 0 and plot_max > 0:
                    range_span = plot_max - plot_min
                    padding = range_span * 0.15
                    cat_axis_min = plot_min - padding
                    cat_axis_max = plot_max + padding
                elif plot_min < 0:
                    cat_axis_min = plot_min * 1.2
                    cat_axis_max = 0
                else:
                    cat_axis_min = 0
                    cat_axis_max = plot_max * 1.4

                fig_cat.add_hline(
                    y=0,
                    line=dict(color="rgba(255,255,255,0.15)", width=1, dash="dash"),
                )
                fig_cat.add_hline(
                    y=cat_avg,
                    line=dict(color="#fb923c", width=2, dash="dot"),
                )
                fig_cat.add_annotation(
                    x=1.01, y=cat_avg,
                    xref="paper", yref="y",
                    text=f"ממוצע: ₪{cat_avg:,.0f}",
                    showarrow=False,
                    font=dict(color="#fb923c", size=11),
                    xanchor="left", yanchor="middle",
                    bgcolor="rgba(11,15,30,0.85)",
                )
                fig_cat.update_layout(
                    paper_bgcolor="#0b0f1e", plot_bgcolor="#0b0f1e",
                    font=dict(color=CAT_TICK, size=12, family="Arial"),
                    xaxis=dict(
                        tickangle=-30, gridcolor=CAT_GRID, title_text="",
                        tickfont=dict(color=CAT_TICK, size=13, family="Arial"),
                        showticklabels=True, type="category",
                    ),
                    yaxis=dict(
                        gridcolor=CAT_GRID, tickformat=",.0f", tickprefix="₪", title_text="",
                        tickfont=dict(color=CAT_TICK, size=12),
                        range=[cat_axis_min, cat_axis_max], showgrid=True,
                        autorange=False,
                    ),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                                font=dict(size=11, color="#e2e8f0")) if (_multi and display_mode == "לפי קטגוריה") else dict(visible=False),
                    margin=dict(t=30, b=70, l=20, r=130),
                    height=320, bargap=0.3,
                )
                st.plotly_chart(fig_cat, use_container_width=True)

        _cat_trend_fragment()


        # ══════════════════════════════════════════════════════════════════════════════
        # INSURANCE REPORT (FIX 6: bar chart + click drill-down + avg monthly)
        # ══════════════════════════════════════════════════════════════════════════════

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-header">ביטוחים - הוצאות בשנה האחרונה</div>', unsafe_allow_html=True)

        # Filter by category (more reliable than IsInsurance flag which can miss some rows)
        _is_ins_cat = (
            df_all["Category"].str.contains("ביטוח", na=False)
            & ~df_all["Category"].str.contains("ביטוח לאומי", na=False)
        )
        df_ins_all  = df_all[_is_ins_cat & (df_all["Type"] == "הוצאה")].copy()

        if not df_ins_all.empty:
            # Monthly gross totals (no credit subtraction — credits are refunds from old policies,
            # not offsets to current insurance spending)
            # IMPORTANT: Show last 12 months (not just months with data)
            _ins_exp_by_m  = df_ins_all.groupby("Display_Month")["Amount_ILS"].sum()
            ins_rows_list = []
            for m in _trend_months_12:
                gross = _ins_exp_by_m.get(m, 0)
                # Include all 12 months, even if no insurance data for that month (show as 0)
                ins_rows_list.append({"Display_Month": m, "Amount_ILS": gross})
            ins_by_month = pd.DataFrame(ins_rows_list) if ins_rows_list else pd.DataFrame(columns=["Display_Month", "Amount_ILS"])
            ins_by_month["sort_key"]    = ins_by_month["Display_Month"].apply(month_sort_key)
            ins_by_month["short_month"] = ins_by_month["Display_Month"].apply(short_label)
            ins_by_month = ins_by_month.sort_values("sort_key")

            n_ins_months  = len(ins_by_month)
            total_ins     = ins_by_month["Amount_ILS"].sum()
            # Average divided by 12 months (full year period) even if insurance data only exists in some months
            avg_monthly   = total_ins / 12 if n_ins_months > 0 else 0

            ins_col_chart, ins_col_kpi = st.columns([4, 1])

            with ins_col_kpi:
                st.markdown(f"""<div class="kpi-card" style="margin-top:30px">
                    <div class="kpi-label">ממוצע חודשי</div>
                    <div class="kpi-value" style="color:#8b5cf6; font-size:1.4rem">{fmt_ils(avg_monthly)}</div>
                </div>""", unsafe_allow_html=True)

            with ins_col_chart:
                fig_ins = px.bar(
                    ins_by_month, x="short_month", y="Amount_ILS",
                    color_discrete_sequence=["#cba6f7"],
                    labels={"Amount_ILS": "סכום (₪)", "short_month": "חודש"},
                    custom_data=["Display_Month"],   # carry full month name for drill-down
                )
                fig_ins.update_traces(
                    text=[f"₪{v:,.0f}" for v in ins_by_month["Amount_ILS"]],
                    textposition="outside",
                    textfont=dict(size=12, color="#e2e8f0", family="Arial"),
                    hovertemplate="<b>%{x}</b><br>₪%{y:,.0f}<extra></extra>",
                    cliponaxis=False,
                )
                fig_ins.add_hline(
                    y=avg_monthly,
                    line=dict(color="#fb923c", width=2, dash="dot"),
                )
                fig_ins.add_annotation(
                    x=1.01, y=avg_monthly,
                    xref="paper", yref="y",
                    text=f"ממוצע: ₪{avg_monthly:,.0f}",
                    showarrow=False,
                    font=dict(color="#fb923c", size=11),
                    xanchor="left", yanchor="middle",
                    bgcolor="rgba(11,15,30,0.85)",
                )
                fig_ins.update_layout(
                    paper_bgcolor="#0b0f1e", plot_bgcolor="#0b0f1e",
                    font=dict(color="#e2e8f0", size=12, family="Arial"),
                    xaxis=dict(tickangle=-25, gridcolor="rgba(255,255,255,0.06)", title_text="",
                               tickfont=dict(color="#b0bec5", size=13),
                               showticklabels=True, type="category"),
                    yaxis=dict(gridcolor="rgba(255,255,255,0.06)", tickformat=",.0f", tickprefix="₪", title_text="",
                               tickfont=dict(color="#b0bec5", size=12),
                               range=[0, ins_by_month["Amount_ILS"].max() * 1.40]),
                    margin=dict(t=30, b=70, l=10, r=130), height=320,
                )

                # FIX 6: click on bar → drill-down
                ins_event = st.plotly_chart(
                    fig_ins, use_container_width=True,
                    on_select="rerun", selection_mode=["points"], key="ins_chart",
                )

            # Handle click selection
            if ins_event and hasattr(ins_event, "selection") and ins_event.selection.points:
                clicked_idx = ins_event.selection.points[0].get("point_index", 0)
                clicked_month = ins_by_month.iloc[clicked_idx]["Display_Month"]
                st.session_state["ins_drill_month"] = clicked_month

            if "ins_drill_month" in st.session_state:
                dm = st.session_state["ins_drill_month"]
                df_ins_drill = df_ins_all[df_ins_all["Display_Month"] == dm].sort_values("Amount_ILS", ascending=False)
                if not df_ins_drill.empty:
                    st.markdown(f"<div class='section-header' style='font-size:0.95rem'>פירוט ביטוחים — {dm}</div>",
                                unsafe_allow_html=True)
                    for _, row in df_ins_drill.iterrows():
                        st.markdown(f"""<div class="ins-item">
                            <span>{row['Merchant']}</span>
                            <span class="ins-amount">{fmt_ils(row['Amount_ILS'])}</span>
                        </div>""", unsafe_allow_html=True)
                    st.markdown(f"""<div class="ins-item" style="border-top:1px solid rgba(255,255,255,0.10); margin-top:6px; font-weight:700">
                        <span>סה״כ {dm}</span>
                        <span class="ins-amount">{fmt_ils(df_ins_drill['Amount_ILS'].sum())}</span>
                    </div>""", unsafe_allow_html=True)
                    if st.button("סגור", key="close_ins"):
                        del st.session_state["ins_drill_month"]
                        st.rerun()
        else:
            st.info("לא זוהו עסקאות ביטוח")


        # ══════════════════════════════════════════════════════════════════════════════
        # TRANSACTIONS TABLE — wrapped in fragment to prevent scroll-jump on filter
        # ══════════════════════════════════════════════════════════════════════════════

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-header">פירוט עסקאות</div>', unsafe_allow_html=True)

        # Switch month selectbox to newly-added transaction's month (set BEFORE fragment renders)
        if "add_txn_month" in st.session_state:
            _jump_month = st.session_state.pop("add_txn_month")
            if _jump_month in all_months_desc_all:
                st.session_state["tbl_sel_single"] = _jump_month

        @st.fragment
        def _txn_fragment():

            # ── Period selector ──────────────────────────────────────────────────────
            tbl_c1, tbl_c2, tbl_c3 = st.columns([2, 3, 3])
            with tbl_c1:
                tbl_view = st.radio("תצוגת רשימה", options=["חודש בודד", "תקופה"],
                                    index=0, horizontal=True, key="tbl_view_mode")
            if tbl_view == "חודש בודד":
                with tbl_c2:
                    tbl_month = st.selectbox("חודש לרשימה", options=all_months_desc_all,
                                             index=0, key="tbl_sel_single")
                tbl_months = [tbl_month]
                tbl_label  = tbl_month
            else:
                with tbl_c2:
                    tbl_from = st.selectbox("מחודש", options=all_months_desc_all,
                                            index=len(all_months_desc_all)-1, key="tbl_sel_from")
                with tbl_c3:
                    tbl_to = st.selectbox("עד חודש", options=all_months_desc_all,
                                          index=0, key="tbl_sel_to")
                if month_sort_key(tbl_from) > month_sort_key(tbl_to):
                    tbl_from, tbl_to = tbl_to, tbl_from
                tbl_months = [m for m in all_months_asc_all
                              if month_sort_key(tbl_from) <= month_sort_key(m) <= month_sort_key(tbl_to)]
                tbl_label  = f"{tbl_from} — {tbl_to}"

            df_table = df_all[df_all["Display_Month"].isin(tbl_months)].copy()

            # ── Category filter (right) + Search (left) ───────────────────────────────
            cat_col, search_col = st.columns([2, 3])
            with cat_col:
                all_cats_in_table = sorted(df_table["Category"].dropna().unique())
                prev_cats = st.session_state.get("catfilt_stable_val", [])
                if isinstance(prev_cats, str):
                    prev_cats = [prev_cats] if prev_cats != "הכל" else []
                valid_prev = [c for c in prev_cats if c in all_cats_in_table]
                cat_filt = st.multiselect("קטגוריה:", all_cats_in_table, default=valid_prev, key="catfilt_stable")
                st.session_state["catfilt_stable_val"] = cat_filt
            with search_col:
                search_q = st.text_input("חיפוש:", placeholder="שם בית עסק, תיאור, קטגוריה...",
                                         key="search_stable")

            df_view = df_table.copy()
            if search_q.strip():
                mask = (
                    df_view["Merchant"].str.contains(search_q, case=False, na=False)
                    | df_view["Description"].astype(str).str.contains(search_q, case=False, na=False)
                    | df_view["Category"].str.contains(search_q, case=False, na=False)
                )
                df_view = df_view[mask]
            if cat_filt:
                df_view = df_view[df_view["Category"].isin(cat_filt)]

            st.markdown(f"<div style='color:#7c8db5;font-size:0.82rem;margin-bottom:8px'>מציג: {tbl_label} | {len(df_view)} עסקאות</div>",
                        unsafe_allow_html=True)

            # ── Summary ───────────────────────────────────────────────────────────────
            _t_exp  = df_view[df_view["Type"] == "הוצאה"]["Amount_ILS"].sum()
            _t_cred = df_view[df_view["Type"] == "זיכוי"]["Amount_ILS"].sum()
            _t_inc  = df_view[df_view["Type"] == "הכנסה"]["Amount_ILS"].sum()

            if _t_cred > 0:
                ma, mb, mc, md, me = st.columns(5)
                ma.metric("רשומות", len(df_view))
                mb.metric("הוצאות ברוטו", fmt_ils(_t_exp))
                mc.metric("הוצאות נטו", fmt_ils(_t_exp - _t_cred))
                md.metric("זיכויים", fmt_ils(_t_cred))
                me.metric("הכנסות", fmt_ils(_t_inc))
            else:
                ma, mb, mc, md = st.columns(4)
                ma.metric("רשומות", len(df_view))
                mb.metric("הוצאות נטו", fmt_ils(_t_exp - _t_cred))
                mc.metric("זיכויים", fmt_ils(_t_cred))
                md.metric("הכנסות", fmt_ils(_t_inc))

            if df_view.empty:
                st.warning("לא נמצאו עסקאות התואמות את הסינון.")
            else:
                existing_cats = set(df_all["Category"].dropna().unique())
                hier_opts = build_category_options(extra_cats=existing_cats)
                if not hier_opts:
                    hier_opts = sorted(existing_cats)

                # Build display with delete column — sort by Date descending (newest first)
                df_display = df_view[["Date", "Merchant", "Description", "Amount_ILS", "Type", "Category", "Display_Month", "Source"]].copy()
                df_display["_sort_dt"] = pd.to_datetime(df_display["Date"], format="%d/%m/%Y", errors="coerce")
                df_display = df_display.sort_values("_sort_dt", ascending=False).drop(columns=["_sort_dt"])
                df_display = df_display.rename(columns={
                    "Date": "תאריך", "Merchant": "בית עסק", "Description": "תיאור",
                    "Amount_ILS": "סכום", "Type": "סוג", "Category": "קטגוריה", "Display_Month": "חודש", "Source": "מקור",
                })
                # Use DateColumn for proper chronological sorting in data_editor
                df_display["תאריך"] = pd.to_datetime(
                    df_display["תאריך"].dt.strftime("%d/%m/%Y"), format="%d/%m/%Y", errors="coerce"
                ) if hasattr(df_display["תאריך"], "dt") else pd.to_datetime(
                    df_display["תאריך"], format="%d/%m/%Y", errors="coerce"
                )
                df_display["סכום"]  = df_display["סכום"].round(2)
                df_display["מחק"]   = False
                df_display_reset = df_display.reset_index(drop=True)

                _editor_key = f"txn_ed_{tbl_label.replace(' ','_').replace('—','to')}"
                _unsaved_placeholder_top = st.empty()   # filled below after editor renders

                edited = st.data_editor(
                    df_display_reset,
                    column_config={
                        "מחק":     st.column_config.CheckboxColumn("🗑", width="small"),
                        "קטגוריה": st.column_config.SelectboxColumn("קטגוריה", options=hier_opts, required=True, width="large"),
                        "סכום":    st.column_config.NumberColumn("סכום (₪)", format="₪%.2f"),
                        "תאריך":   st.column_config.DateColumn("תאריך", format="DD/MM/YYYY", width="small"),
                        "בית עסק": st.column_config.TextColumn("בית עסק", width="medium"),
                        "תיאור":   st.column_config.TextColumn("תיאור",   width="medium"),
                        "סוג":     st.column_config.SelectboxColumn("סוג", width="small",
                                   options=["הוצאה", "הכנסה", "זיכוי"], required=True),
                        "חודש":    st.column_config.TextColumn("חודש (קריאה בלבד)", disabled=True, width="small"),
                        "מקור":    st.column_config.TextColumn("מקור (קריאה בלבד)", disabled=True, width="small"),
                    },
                    disabled=["מקור", "חודש"],
                    hide_index=True,
                    use_container_width=True,
                    height=min(600, max(200, (len(df_display_reset) + 1) * 38 + 40)),
                    key=_editor_key,
                )
                # ── Bottom warning placeholder (between table and button) ─────
                _unsaved_placeholder_bottom_local = st.empty()

                save_btn = st.button("שמור שינויים", type="primary", key="save_txn_btn")

                # ── Unsaved changes warning — fills placeholders ABOVE and BELOW the table ─────
                if not save_btn:
                    _has_type_change   = (edited["סוג"] != df_display_reset["סוג"]).any()
                    _has_cat_change    = ((edited["קטגוריה"] != df_display_reset["קטגוריה"]) & ~edited["קטגוריה"].apply(is_separator)).any()
                    _has_del_checked   = edited["מחק"].any()
                    if _has_type_change or _has_cat_change or _has_del_checked:
                        _warning_html = """<div style='background-color:#fbbf24;padding:12px 16px;border-radius:8px;margin:8px 0;
                            color:#000;font-weight:700;font-size:1.05rem;border-left:4px solid #FF9800;'>
                            ⚠️ יש שינויים שלא נשמרו — לחצי על <b>שמור שינויים</b> כדי לשמור
                            </div>"""
                        _unsaved_placeholder_top.markdown(_warning_html, unsafe_allow_html=True)
                        _unsaved_placeholder_bottom_local.markdown(_warning_html, unsafe_allow_html=True)
                    else:
                        _unsaved_placeholder_top.empty()
                        _unsaved_placeholder_bottom_local.empty()

                if save_btn:
                    # ── Delete checked rows — ask confirmation ────────────────────────
                    to_delete = edited[edited["מחק"] == True]
                    if not to_delete.empty:
                        st.session_state["pending_delete_rows"] = to_delete.to_dict("records")
                        st.rerun()

                    # ── Field changes: Date, Merchant, Amount, Description ────────────
                    def _calc_display_month(date_str):
                        """Calculate Display_Month from date."""
                        try:
                            dt = pd.to_datetime(date_str)
                            day = dt.day
                            month = dt.month
                            year = dt.year
                            if day >= 10:
                                next_month = month + 1 if month < 12 else 1
                                next_year = year if month < 12 else year + 1
                            else:
                                next_month = month
                                next_year = year
                            heb_month_num = next_month
                            heb_months_map = {1:"ינואר", 2:"פברואר", 3:"מרץ", 4:"אפריל", 5:"מאי", 6:"יוני",
                                             7:"יולי", 8:"אוגוסט", 9:"ספטמבר", 10:"אוקטובר", 11:"נובמבר", 12:"דצמבר"}
                            year_short = str(next_year)[-2:]
                            return f"{heb_months_map.get(heb_month_num, '?')} {year_short}"
                        except:
                            return ""

                    date_changed = edited["תאריך"] != df_display_reset["תאריך"]
                    merchant_changed = edited["בית עסק"] != df_display_reset["בית עסק"]
                    amount_changed = edited["סכום"] != df_display_reset["סכום"]
                    desc_changed = edited["תיאור"] != df_display_reset["תיאור"]

                    if (date_changed | merchant_changed | amount_changed | desc_changed).any():
                        _df_master_now = pd.read_csv(DATA_FILE, encoding="utf-8-sig")
                        for idx, row in edited.iterrows():
                            if idx >= len(df_display_reset):
                                continue
                            _date_str = _tdate_str(row["תאריך"])
                            _orig_date_str = _tdate_str(df_display_reset.at[idx, "תאריך"])
                            _merchant = str(row["בית עסק"]).strip()
                            _orig_merchant = str(df_display_reset.at[idx, "בית עסק"]).strip()
                            _amount = round(float(row["סכום"]), 2)
                            _orig_amount = round(float(df_display_reset.at[idx, "סכום"]), 2)

                            # Find matching row in master data
                            mask_row = (
                                (_df_master_now["Date"] == _orig_date_str)
                                & (_df_master_now["Merchant"].astype(str).str.strip() == _orig_merchant)
                                & (_df_master_now["Amount_ILS"].apply(lambda x: round(float(x), 2)) == _orig_amount)
                            )

                            if mask_row.any():
                                if date_changed.iloc[idx]:
                                    _df_master_now.loc[mask_row, "Date"] = _date_str
                                    _df_master_now.loc[mask_row, "Display_Month"] = _calc_display_month(_date_str)
                                if merchant_changed.iloc[idx]:
                                    _df_master_now.loc[mask_row, "Merchant"] = _merchant
                                if amount_changed.iloc[idx]:
                                    _df_master_now.loc[mask_row, "Amount_ILS"] = _amount
                                if desc_changed.iloc[idx]:
                                    _df_master_now.loc[mask_row, "Description"] = str(row["תיאור"]).strip()

                        _df_master_now.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")
                        load_data.clear()
                        st.success("✅ עסקאות עודכנו בהצלחה")
                        st.rerun(scope="app")

                    # ── Type changes ─────────────────────────────────────────────────
                    type_changed = edited["סוג"] != df_display_reset["סוג"]
                    if type_changed.any():
                        _overrides_now = load_overrides()
                        _df_master_now = pd.read_csv(DATA_FILE, encoding="utf-8-sig")
                        for idx, row in edited[type_changed].iterrows():
                            new_type = row["סוג"]
                            if new_type not in ("הוצאה", "הכנסה", "זיכוי"):
                                continue
                            _key = override_key(_tdate_str(row["תאריך"]), str(row["בית עסק"]), row["סכום"])
                            existing = _overrides_now.get(_key)
                            if isinstance(existing, dict):
                                existing["type"] = new_type
                            elif existing is not None:
                                _overrides_now[_key] = {"category": existing, "type": new_type}
                            else:
                                _overrides_now[_key] = {"type": new_type}
                            mask_row = (
                                (_df_master_now["Date"] == _tdate_str(row["תאריך"]))
                                & (_df_master_now["Merchant"].astype(str).str.strip() == str(row["בית עסק"]).strip())
                                & (_df_master_now["Amount_ILS"].apply(lambda x: round(float(x), 2)) == round(float(row["סכום"]), 2))
                            )
                            _df_master_now.loc[mask_row, "Type"] = new_type
                        _df_master_now.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")
                        save_overrides(_overrides_now)
                        load_data.clear()
                        st.success("סוג עסקה עודכן")
                        st.rerun(scope="app")

                    # ── Category changes ──────────────────────────────────────────────
                    cat_changed = (
                        (edited["קטגוריה"] != df_display_reset["קטגוריה"])
                        & ~edited["קטגוריה"].apply(is_separator)
                    )
                    if cat_changed.any():
                        pending_changes = []
                        for idx, row in edited[cat_changed].iterrows():
                            merchant = row["בית עסק"]
                            new_cat  = row["קטגוריה"]
                            if merchant and new_cat and not is_separator(new_cat):
                                all_count = int((df_all["Merchant"] == merchant).sum())
                                pending_changes.append({
                                    "merchant": merchant, "new_cat": new_cat,
                                    "old_cat":  df_display_reset.at[idx, "קטגוריה"],
                                    "all_count": all_count,
                                    "date":     _tdate_str(row["תאריך"]), "amount": row["סכום"],
                                })
                        st.session_state["pending_cat_changes"] = pending_changes
                    elif not type_changed.any():
                        st.info("לא זוהו שינויים")

                # ── Delete confirmation dialog ────────────────────────────────────────
                if "pending_delete_rows" in st.session_state:
                    rows_to_del = st.session_state["pending_delete_rows"]
                    st.markdown("""<div style='background:#1e1020;border-radius:12px;padding:18px 22px;
                                margin:14px 0;border:2px solid #f43f5e;'>
                        <div style='color:#f43f5e;font-weight:900;font-size:1.05rem;margin-bottom:10px;'>
                        למחוק את העסקאות הבאות?</div>""", unsafe_allow_html=True)
                    for r in rows_to_del:
                        st.markdown(
                            f"<div style='color:#e2e8f0;padding:4px 0'>"
                            f"<b>{r['בית עסק']}</b> | {_tdate_str(r['תאריך'])} | ₪{r['סכום']:,.2f}</div>",
                            unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                    _dcol1, _dcol2, _ = st.columns([1, 1, 3])
                    with _dcol1:
                        _confirm_del = st.button("כן, מחק", type="primary", key="confirm_del_btn")
                    with _dcol2:
                        _cancel_del = st.button("ביטול", key="cancel_del_btn")
                    if _cancel_del:
                        del st.session_state["pending_delete_rows"]
                        st.rerun()
                    if _confirm_del:
                        _df_master = pd.read_csv(DATA_FILE, encoding="utf-8-sig")
                        _overrides = load_overrides()
                        for r in rows_to_del:
                            mask = (
                                (_df_master["Date"] == _tdate_str(r["תאריך"]))
                                & (_df_master["Merchant"].astype(str).str.strip() == str(r["בית עסק"]).strip())
                                & (_df_master["Amount_ILS"].apply(lambda x: round(float(x), 2)) == round(float(r["סכום"]), 2))
                            )
                            _df_master = _df_master[~mask]
                            _key = override_key(_tdate_str(r["תאריך"]), str(r["בית עסק"]), r["סכום"])
                            _overrides.pop(_key, None)
                        _df_master.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")
                        save_overrides(_overrides)
                        del st.session_state["pending_delete_rows"]
                        load_data.clear()
                        st.success(f"נמחקו {len(rows_to_del)} עסקאות")
                        st.rerun(scope="app")

                # ── Scope dialog ──────────────────────────────────────────────────────
                pending = st.session_state.get("pending_cat_changes", [])
                if pending and not st.session_state.get("pending_delete_rows"):
                    SCOPE_OPTS = [
                        "עסקה זו בלבד",
                        "כל העסקאות של בית עסק זה בעבר",
                        "כל העסקאות של בית עסק זה בעתיד",
                        "כל העסקאות של בית עסק זה — עבר ועתיד",
                    ]
                    st.markdown("""<div style='background:#0f1628;border-radius:12px;padding:18px 22px;
                                margin:14px 0;border:2px solid #6366f1;'>
                        <div style='color:#e2e8f0;font-weight:900;font-size:1.05rem;margin-bottom:14px;'>
                        כיצד להחיל את השינוי?</div>""", unsafe_allow_html=True)
                    scope_choices = {}
                    for chg_i, chg in enumerate(pending):
                        st.markdown(
                            f"<div style='background:#131e30;border-radius:8px;padding:10px 14px;margin:6px 0;"
                            f"border-right:3px solid #6366f1;'>"
                            f"<b style='color:#e2e8f0;font-size:1rem'>{chg['merchant']}</b>"
                            f"<span style='color:#94a3b8;font-size:0.82rem;margin-right:10px'>{chg['date']} | ₪{chg['amount']:,.0f}</span><br>"
                            f"<span style='color:#f38ba8;font-weight:600'>{chg['old_cat']}</span> &nbsp;→&nbsp; "
                            f"<span style='color:#a6e3a1;font-weight:700'>{chg['new_cat']}</span>"
                            f"<span style='color:#94a3b8;font-size:0.8rem'> (סה״כ {chg['all_count']} עסקאות)</span></div>",
                            unsafe_allow_html=True)
                        scope_choices[chg_i] = st.radio("", options=SCOPE_OPTS, index=0,
                                                         key=f"scope_{chg_i}", horizontal=False,
                                                         label_visibility="collapsed")
                    st.markdown("</div>", unsafe_allow_html=True)
                    confirm_col, cancel_col, _ = st.columns([1, 1, 3])
                    with confirm_col:
                        confirm_btn = st.button("אישור", type="primary", key="confirm_cat")
                    with cancel_col:
                        cancel_btn = st.button("ביטול", key="cancel_cat")

                    if cancel_btn:
                        del st.session_state["pending_cat_changes"]
                        st.rerun()

                    if confirm_btn:
                        rules     = load_rules()
                        df_master = pd.read_csv(DATA_FILE, encoding="utf-8-sig")
                        summary   = []
                        errors    = []

                        def to_sortable(ddmmyyyy):
                            try:
                                d, mo, y = str(ddmmyyyy).split("/")
                                return f"{y}/{mo}/{d}"
                            except Exception:
                                return str(ddmmyyyy)

                        df_master["_sort_date"] = df_master["Date"].apply(to_sortable)
                        overrides = load_overrides()

                        for chg_i, chg in enumerate(pending):
                            m  = str(chg["merchant"]).strip()
                            nc = chg["new_cat"]
                            scope = scope_choices.get(chg_i, SCOPE_OPTS[0])
                            date_str = chg["date"]
                            amount   = round(float(chg["amount"]), 2)
                            sortable_date = to_sortable(date_str)
                            mask_merchant = df_master["Merchant"].astype(str).str.strip() == m
                            if mask_merchant.sum() == 0:
                                errors.append(f"לא נמצאו שורות עבור: {m}"); continue

                            if scope == "עסקה זו בלבד":
                                mask_row = mask_merchant & (df_master["Date"] == date_str) & \
                                           (df_master["Amount_ILS"].apply(lambda x: round(float(x), 2)) == amount)
                                if mask_row.sum() == 0:
                                    mask_row = mask_merchant & (df_master["Date"] == date_str)
                                if mask_row.sum() == 0:
                                    mask_row = df_master.index == df_master[mask_merchant].index[0]
                                df_master.loc[mask_row, "Category"] = nc
                                for _, row in df_master[mask_row].iterrows():
                                    key = override_key(row["Date"], str(row["Merchant"]), row["Amount_ILS"])
                                    existing = overrides.get(key)
                                    overrides[key] = {**(existing if isinstance(existing, dict) else {}), "category": nc} if isinstance(existing, dict) else nc
                                summary.append(f"✓ {m}: {int(mask_row.sum())} עסקה → {nc}")

                            elif scope == "כל העסקאות של בית עסק זה בעבר":
                                mask_row = mask_merchant & (df_master["_sort_date"] <= sortable_date)
                                df_master.loc[mask_row, "Category"] = nc
                                for _, row in df_master[mask_row].iterrows():
                                    key = override_key(row["Date"], str(row["Merchant"]), row["Amount_ILS"])
                                    existing = overrides.get(key)
                                    overrides[key] = {**(existing if isinstance(existing, dict) else {}), "category": nc} if isinstance(existing, dict) else nc
                                summary.append(f"✓ {m}: {int(mask_row.sum())} עסקאות עבר → {nc}")

                            elif scope == "כל העסקאות של בית עסק זה בעתיד":
                                mask_row = mask_merchant & (df_master["_sort_date"] >= sortable_date)
                                df_master.loc[mask_row, "Category"] = nc
                                rules[m] = nc
                                summary.append(f"✓ {m}: {int(mask_row.sum())} עסקאות עתיד → {nc}")

                            else:
                                df_master.loc[mask_merchant, "Category"] = nc
                                rules[m] = nc
                                summary.append(f"✓ {m}: {int(mask_merchant.sum())} עסקאות → {nc}")

                        df_master = df_master.drop(columns=["_sort_date"])
                        df_master.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")
                        save_rules(rules)
                        save_overrides(overrides)
                        load_data.clear()
                        del st.session_state["pending_cat_changes"]
                        if summary:
                            st.markdown(
                                f"""<div id='success-msg-{id(summary)}' style='background-color:#90EE90;padding:12px 16px;border-radius:8px;margin:8px 0;
                                color:#000;font-weight:700;font-size:1.05rem;border-left:4px solid #228B22;'>
                                ✅ נשמר! {" | ".join(summary)}
                                </div>
                                <script>
                                setTimeout(function() {{
                                    var el = document.getElementById('success-msg-{id(summary)}');
                                    if (el) {{
                                        el.style.transition = 'opacity 0.5s ease-out';
                                        el.style.opacity = '0';
                                        setTimeout(function() {{ el.remove(); }}, 500);
                                    }}
                                }}, 3000);
                                </script>""",
                                unsafe_allow_html=True
                            )
                        if errors:  st.error("שגיאות: " + " | ".join(errors))
                        st.rerun(scope="app")

            # ── Add transaction (INSIDE fragment — prevents scroll-jump on type change) ──
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div class="section-header">הוספת עסקה ידנית</div>', unsafe_allow_html=True)
            if st.session_state.get("add_txn_success"):
                st.success(st.session_state.pop("add_txn_success"))
            st.markdown("<div style='color:#7c8db5;font-size:0.8rem;margin-bottom:6px'>הזן תאריך כ-6 ספרות: DDMMYY (למשל 030226 = 03/02/2026)</div>",
                        unsafe_allow_html=True)

            # Type selector — narrow column so it doesn't span full width
            _type_col, _ = st.columns([1, 3])
            with _type_col:
                _add_type = st.selectbox("סוג עסקה", options=["הוצאה", "הכנסה", "זיכוי"], key="add_type_sel")

            _PLACEHOLDER = "── בחרי קטגוריה ──"
            if _add_type == "הכנסה":
                _cat_opts = [_PLACEHOLDER, "מזונות", "הכנסות עסק", "קצבת ילדים", "הכנסה אחרת"]
            else:
                _existing_add = set(df_all["Category"].dropna().unique())
                _cat_opts = [_PLACEHOLDER] + build_category_options(extra_cats=_existing_add)

            with st.form(key="add_txn_form", clear_on_submit=True):
                a1, a2, a3 = st.columns([2, 3, 2])
                with a1:
                    new_date_raw = st.text_input("תאריך (DDMMYY)", placeholder="030226", max_chars=8)
                with a2:
                    new_merchant = st.text_input("בית עסק / תיאור")
                with a3:
                    new_amount_str = st.text_input("סכום (₪)", placeholder="")

                b1, b2 = st.columns([3, 2])
                with b1:
                    new_cat = st.selectbox("קטגוריה", options=_cat_opts, index=0)
                with b2:
                    new_source = st.text_input("מקור", value="ידני")

                add_btn = st.form_submit_button("הוסף עסקה", type="primary")

            if add_btn:
                raw = new_date_raw.strip().replace("/", "").replace("-", "")
                if len(raw) == 6:
                    new_date = f"{raw[:2]}/{raw[2:4]}/20{raw[4:]}"
                elif len(raw) == 8:
                    new_date = f"{raw[:2]}/{raw[2:4]}/{raw[4:]}"
                else:
                    new_date = ""
                try:
                    new_amount = float(new_amount_str.replace(",", "").replace("₪", "").strip()) if new_amount_str.strip() else 0.0
                except ValueError:
                    new_amount = 0.0

                err = []
                if not new_date:                                              err.append("תאריך")
                if not new_merchant.strip():                                  err.append("בית עסק")
                if new_amount <= 0:                                           err.append("סכום")
                if new_cat == _PLACEHOLDER or is_separator(new_cat):         err.append("קטגוריה")

                if err:
                    st.error(f"חסרים שדות: {', '.join(err)}")
                else:
                    try:
                        _d = pd.to_datetime(new_date, format="%d/%m/%Y")
                    except Exception:
                        st.error(f"תאריך לא תקין: {new_date!r} — הזיני DDMMYY, למשל 030226")
                    else:
                        try:
                            # Calculate Display_Month correctly (2-digit year)
                            day, month, year = _d.day, _d.month, _d.year
                            if day >= 10:
                                next_month = month + 1 if month < 12 else 1
                                next_year = year if month < 12 else year + 1
                            else:
                                next_month = month
                                next_year = year
                            heb_months_map = {1:"ינואר", 2:"פברואר", 3:"מרץ", 4:"אפריל", 5:"מאי", 6:"יוני",
                                             7:"יולי", 8:"אוגוסט", 9:"ספטמבר", 10:"אוקטובר", 11:"נובמבר", 12:"דצמבר"}
                            _display_month = f"{heb_months_map.get(next_month, '?')} {str(next_year)[-2:]}"
                            _df_m = pd.read_csv(DATA_FILE, encoding="utf-8-sig")
                            _df_m = pd.concat([_df_m, pd.DataFrame([{
                                "Date": new_date, "Display_Month": _display_month,
                                "Merchant": new_merchant.strip(), "Description": "",
                                "Amount_ILS": round(new_amount, 2), "Type": _add_type,
                                "Category": new_cat, "IsInsurance": "ביטוח" in new_cat,
                                "Source": new_source.strip() or "ידני",
                            }])], ignore_index=True)
                            _df_m.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")
                            load_data.clear()
                            st.session_state["add_txn_success"] = f"✓ עסקה נוספה: {new_merchant.strip()} | {new_date} | ₪{new_amount:,.0f} | {new_cat}"
                            st.session_state["add_txn_month"] = _display_month
                            st.rerun(scope="app")
                        except Exception as e:
                            st.error(f"שגיאה בשמירה: {e}")

        # These run on the full-page rerun AFTER saving, BEFORE fragment renders
        if "add_txn_month" in st.session_state:
            _jm = st.session_state.pop("add_txn_month")
            if _jm in all_months_desc_all:
                st.session_state["tbl_sel_single"] = _jm

        _txn_fragment()

        st.markdown("---")
        st.markdown("<div style='color:#94a3b8;font-size:0.82rem;direction:rtl'>לעדכון נתונים הרץ: <code style='color:#6ee7b7;background:rgba(110,231,183,0.12);padding:1px 5px;border-radius:4px'>python3 process_budget.py</code> &nbsp;|&nbsp; לאחר מכן לחצי רענן 🔄</div>", unsafe_allow_html=True)


    _dashboard_fragment()

with tab_averages:

    # ── Helper functions (defined once, used inside fragment) ──────────────────
    INCOME_CATS_SHOW = ["מזונות", "הכנסות עסק", "קצבת ילדים", "הכנסה אחרת"]

    def _avg_rows(df_sub, n_months, df_credits=None):
        """Return list of (main_cat, avg, [(subcat, avg)...]) sorted by avg desc."""
        # חישוב ממוצע תקין - לחלק בכל החודשים בטווח, לא רק בחודשים עם נתונים
        total_months_in_range = max(n_months, 1)  # מספר כל החודשים בטווח

        cred_by_cat = {}
        if df_credits is not None and not df_credits.empty:
            for cat, cgrp in df_credits.groupby("Category"):
                cred_by_cat[cat] = cgrp["Amount_ILS"].sum()
        cred_by_main = {}
        if df_credits is not None and not df_credits.empty:
            for mc, cgrp in df_credits.groupby("MainCategory"):
                cred_by_main[mc] = cgrp["Amount_ILS"].sum()
        result = []
        for main_cat, grp in df_sub.groupby("MainCategory"):
            gross_main = grp["Amount_ILS"].sum()
            net_main   = gross_main - cred_by_main.get(main_cat, 0)
            if net_main <= 0:
                continue
            main_avg = net_main / total_months_in_range
            subcats = []
            for cat, sub_grp in grp.groupby("Category"):
                if cat != main_cat:
                    net_sub = sub_grp["Amount_ILS"].sum() - cred_by_cat.get(cat, 0)
                    # Show all subcategories with any value (positive or negative - credits)
                    if net_sub != 0:
                        subcats.append((cat, net_sub / total_months_in_range))
            # Sort subcats by Categories_Leveling.json order
            # (JSON already has insurance subcats last for בריאות וטיפוח, so we just use the standard order)
            subcats.sort(key=lambda x: _SUB_CAT_ORDER.get(x[0], 999))
            result.append((main_cat, main_avg, subcats))

        # Separate main categories into regular and special (end categories)
        # Special categories that should appear at the end in this order: תרומות, משיכה מכספומט, לא מסווג
        SPECIAL_CATS_ORDER = ["תרומות", "משיכה מכספומט", "לא מסווג"]
        regular_cats = []
        special_cats = []

        for item in result:
            main_cat = item[0]
            if main_cat in SPECIAL_CATS_ORDER:
                special_cats.append((SPECIAL_CATS_ORDER.index(main_cat), item))
            else:
                regular_cats.append(item)

        # Sort regular categories by JSON order
        regular_cats.sort(key=lambda x: _MAIN_CAT_ORDER.get(x[0], 999))

        # Sort special categories by their defined order
        special_cats.sort(key=lambda x: x[0])

        # Combine: regular categories first, then special categories at the end
        result = regular_cats + [item for _, item in special_cats]
        return result

    def _avg_rows_income(df_sub, n_months, filter_cats):
        result = []
        # חישוב ממוצע תקין - לחלק בכל החודשים בטווח, לא רק בחודשים עם נתונים
        # אם הטווח הוא 12 חודשים, חלק ב-12 גם אם יש נתונים רק ב-8 חודשים
        total_months_in_range = max(n_months, 1)  # מספר כל החודשים בטווח (בקירוב 12 לשנה)

        for cat, grp in df_sub.groupby("Category"):
            if cat not in filter_cats:
                continue
            avg = grp["Amount_ILS"].sum() / total_months_in_range
            result.append((cat, avg, []))
        result.sort(key=lambda x: -x[1])
        return result

    def _render_income_table(rows, total_avg):
        """Income table: dark header row with total, light data rows, no footer total."""
        rows_html = ""
        for cat, avg, _ in rows:
            pct = (avg / total_avg * 100) if total_avg > 0 else 0
            rows_html += f"""
            <tr class="inc-row">
              <td class="inc-name">{cat}</td>
              <td class="inc-pct">{pct:.1f}%</td>
              <td class="inc-amt">&#8362;{avg:,.0f}</td>
            </tr>"""
        full_html = f"""
        <html><head><meta charset="utf-8">
        <style>
          html, body {{ margin:0; padding:0; background:#0b0f1e; direction:rtl; font-family:Arial,sans-serif; color:#e2e8f0; }}
          table {{ width:100%; border-collapse:collapse; background:#0b0f1e; }}
          thead tr {{ background:#141929; border-bottom:2px solid #6366f1; }}
          th {{ text-align:right; padding:9px 10px; color:#e2e8f0; font-size:13px; font-weight:700; }}
          th.th-total {{ text-align:left; color:#10b981; font-size:14px; font-weight:900; }}
          tr.inc-row {{ border-bottom:1px solid rgba(255,255,255,0.08); background:#1e2d45; }}
          tr.inc-row:hover {{ background:#253858; }}
          td.inc-name {{ padding:9px 10px; color:#e2e8f0; font-size:14px; font-weight:700; }}
          td.inc-pct  {{ padding:9px 10px; color:#94a3b8; font-size:13px; text-align:left; width:55px; }}
          td.inc-amt  {{ padding:9px 10px; color:#e2e8f0; font-size:14px; font-weight:800; text-align:left; width:110px; }}
        </style></head>
        <body><table>
          <thead><tr>
            <th>קטגוריה</th>
            <th style="text-align:left;width:55px">%</th>
            <th class="th-total" style="width:110px">&#8362;{total_avg:,.0f}</th>
          </tr></thead>
          <tbody>{rows_html}</tbody>
        </table></body></html>"""
        height = max(80, 44 + len(rows) * 36)
        components.html(full_html, height=height, scrolling=False)

    def _render_table(rows, total_avg):
        """Render table using components.html to avoid Streamlit markdown size limits."""
        rows_html = ""
        for main_cat, main_avg, subcats in rows:
            pct = (main_avg / total_avg * 100) if total_avg > 0 else 0
            rows_html += f"""
            <tr class="main-row">
              <td class="cat-name">{main_cat}</td>
              <td class="pct">{pct:.1f}%</td>
              <td class="amt">&#8362;{main_avg:,.0f}</td>
            </tr>"""
            for scat, savg in subcats:
                rows_html += f"""
            <tr class="sub-row">
              <td class="sub-name">{scat}</td>
              <td></td>
              <td class="sub-amt">&#8362;{savg:,.0f}</td>
            </tr>"""

        full_html = f"""
        <html><head><meta charset="utf-8">
        <style>
          html, body {{ margin:0; padding:0; background:#0b0f1e; direction:rtl; font-family:Arial,sans-serif; color:#e2e8f0; }}
          table {{ width:100%; border-collapse:collapse; background:#0b0f1e; }}
          thead tr {{ background:#141929; border-bottom:2px solid #6366f1; }}
          th {{ text-align:right; padding:9px 10px; color:#e2e8f0; font-size:13px; font-weight:700; }}
          th.th-total {{ text-align:left; color:#f43f5e; font-size:14px; font-weight:900; }}
          tr.main-row {{ border-bottom:1px solid rgba(255,255,255,0.08); background:#1e2d45; }}
          tr.main-row:hover {{ background:#253858; }}
          td.cat-name {{ padding:9px 10px; font-weight:700; color:#e2e8f0; font-size:14px; }}
          td.pct  {{ padding:9px 10px; color:#94a3b8; font-size:13px; text-align:left; width:55px; }}
          td.amt  {{ padding:9px 10px; font-weight:800; color:#e2e8f0; font-size:14px; text-align:left; width:110px; }}
          tr.sub-row {{ border-bottom:1px solid rgba(255,255,255,0.05); background:#0b0f1e; }}
          tr.sub-row:hover {{ background:rgba(255,255,255,0.04); }}
          td.sub-name {{ padding:5px 10px 5px 28px; color:#b0bec5; font-size:13px; }}
          td.sub-amt  {{ padding:5px 10px; color:#b0bec5; font-size:13px; text-align:left; }}
        </style></head>
        <body>
        <table>
          <thead><tr>
            <th>קטגוריה</th>
            <th style="text-align:left;width:55px">%</th>
            <th class="th-total" style="width:110px">&#8362;{total_avg:,.0f}</th>
          </tr></thead>
          <tbody>{rows_html}</tbody>
        </table>
        </body></html>
        """
        n_rows = len(rows) + sum(len(s) for _, _, s in rows)
        height = max(100, 44 + n_rows * 32)
        components.html(full_html, height=height, scrolling=False)

    @st.fragment
    def _avg_tables_fragment():
        all_months_sorted_f = sorted(df_all["Display_Month"].dropna().unique(), key=month_sort_key)
        all_months_desc_avg = list(reversed(all_months_sorted_f))
        _last12_start = all_months_sorted_f[-12] if len(all_months_sorted_f) >= 12 else all_months_sorted_f[0]
        _default_from_idx = all_months_desc_avg.index(_last12_start) if _last12_start in all_months_desc_avg else len(all_months_desc_avg) - 1

        # ── Selection mode: single month vs. period ──────────────────────────────
        sel_c_mode, _, _, = st.columns([1.5, 1, 5])
        with sel_c_mode:
            avg_mode = st.radio(
                "בחירה:",
                options=["תקופה", "חודש בודד"],
                horizontal=True,
                key="avg_mode"
            )

        if avg_mode == "חודש בודד":
            # ── Single month mode ──────────────────────────────────────────────
            avg_sel_c1, _, avg_sel_c3 = st.columns([2, 2, 4])
            with avg_sel_c1:
                selected_month = st.selectbox(
                    "בחר חודש",
                    options=all_months_desc_avg,
                    index=0,
                    key="avg_single_month"
                )
            avg_months = [selected_month]
            avg_from = selected_month
            avg_to = selected_month
            with avg_sel_c3:
                st.markdown(
                    f"<div style='color:#7c8db5;font-size:0.85rem;margin-top:28px'>"
                    f"נתונים לחודש: {selected_month}</div>",
                    unsafe_allow_html=True,
                )
        else:
            # ── Period mode (from/to) ──────────────────────────────────────────
            avg_sel_c1, avg_sel_c2, avg_sel_c3 = st.columns([2, 2, 4])
            with avg_sel_c1:
                avg_from = st.selectbox("מחודש", options=all_months_desc_avg, index=_default_from_idx, key="avg_from")
            with avg_sel_c2:
                avg_to = st.selectbox("עד חודש", options=all_months_desc_avg, index=0, key="avg_to")
            if month_sort_key(avg_from) > month_sort_key(avg_to):
                avg_from, avg_to = avg_to, avg_from
            avg_months = months_in_range(all_months_sorted_f, avg_from, avg_to)
            with avg_sel_c3:
                st.markdown(
                    f"<div style='color:#7c8db5;font-size:0.85rem;margin-top:28px'>"
                    f"ממוצע על {len(avg_months)} חודשים: {avg_from} — {avg_to}</div>",
                    unsafe_allow_html=True,
                )
        # חישוב מספר החודשים הכולל בטווח (כולל חודשים ללא נתונים)
        # דוגמה: בין 2025-09 ל-2025-12 = 4 חודשים, גם אם רק 2 יש נתונים
        from_idx = all_months_sorted_f.index(avg_from) if avg_from in all_months_sorted_f else 0
        to_idx = all_months_sorted_f.index(avg_to) if avg_to in all_months_sorted_f else len(all_months_sorted_f) - 1
        n_avg_months = max(to_idx - from_idx + 1, 1)  # מספר החודשים בטווח (כולל חודשים ללא נתונים)
        df_avg = df_all[df_all["Display_Month"].isin(avg_months)].copy()
        df_avg_exp  = df_avg[df_avg["Type"] == "הוצאה"]
        df_avg_cred = df_avg[df_avg["Type"] == "זיכוי"]
        df_avg_inc  = df_avg[df_avg["Type"] == "הכנסה"]

        st.markdown("<br>", unsafe_allow_html=True)
        tbl_exp_col, tbl_inc_col = st.columns(2, gap="large")

        # ── EXPENSES TABLE ──────────────────────────────────────────────────────
        with tbl_exp_col:
            st.markdown('<div class="section-header">הוצאות - ממוצע חודשי</div>', unsafe_allow_html=True)
            # חישוב ממוצע תקין - לחלק בכל החודשים בטווח, לא רק בחודשים עם נתונים
            total_months_for_avg = max(n_avg_months, 1)
            exp_rows = _avg_rows(df_avg_exp, total_months_for_avg, df_credits=df_avg_cred)
            total_exp_avg = (df_avg_exp["Amount_ILS"].sum() - df_avg_cred["Amount_ILS"].sum()) / total_months_for_avg
            if exp_rows:
                _render_table(exp_rows, total_exp_avg)
            else:
                st.info("אין נתוני הוצאות")

        # ── INCOME TABLE ────────────────────────────────────────────────────────
        with tbl_inc_col:
            st.markdown('<div class="section-header">הכנסות - ממוצע חודשי</div>', unsafe_allow_html=True)
            # חישוב ממוצע תקין - לחלק בכל החודשים בטווח, לא רק בחודשים עם נתונים
            total_months_for_avg = max(n_avg_months, 1)
            inc_rows = _avg_rows_income(df_avg_inc, total_months_for_avg, INCOME_CATS_SHOW)
            total_inc_avg = sum(avg for _, avg, _ in inc_rows)
            if inc_rows:
                _render_income_table(inc_rows, total_inc_avg)
            else:
                st.info("אין נתוני הכנסות")

            # ── INSURANCE TABLE (below income) ──────────────────────────────────
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div class="section-header">ביטוחים - ממוצע חודשי</div>', unsafe_allow_html=True)
            df_ins_avg = df_avg_exp[
                df_avg_exp["Category"].str.contains("ביטוח", na=False)
                & ~df_avg_exp["Category"].str.contains("ביטוח לאומי", na=False)
            ].copy()
            df_ins_cred = df_avg_cred[
                df_avg_cred["Category"].str.contains("ביטוח", na=False)
                & ~df_avg_cred["Category"].str.contains("ביטוח לאומי", na=False)
            ].copy()
            if not df_ins_avg.empty:
                # חישוב ברוטו לפי קטגוריה, לאחר מכן הפחתת זיכויים
                cred_by_cat = df_ins_cred.groupby("Category")["Amount_ILS"].sum() if not df_ins_cred.empty else {}
                ins_by_cat = df_ins_avg.groupby("Category")["Amount_ILS"].sum()
                ins_rows = [(cat, (total - cred_by_cat.get(cat, 0)) / total_months_for_avg, [])
                            for cat, total in ins_by_cat.items()]
                ins_rows.sort(key=lambda x: -x[1])
                total_ins_avg = (df_ins_avg["Amount_ILS"].sum() - df_ins_cred["Amount_ILS"].sum()) / total_months_for_avg
                _render_income_table(ins_rows, total_ins_avg)
            else:
                st.info("אין נתוני ביטוח")

    _avg_tables_fragment()
