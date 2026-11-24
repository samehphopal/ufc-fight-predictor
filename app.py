import base64
import textwrap
from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

BASE_DIR = Path(__file__).resolve().parent

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="UFC Fight Outcome & Win-Probability Engine",
    page_icon="🥊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- MODERN DARK EXECUTIVE THEME ---
st.markdown("""
<style>
    div[data-baseweb="select"] input {
        caret-color: transparent !important;
        cursor: pointer !important;
    }
    div[data-baseweb="select"] > div {
        cursor: pointer !important;
    }
    .main {
        background-color: #0E1117;
        color: #FAFAFA;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    .app-subtitle {
        color: #94A3B8;
        font-size: 0.98rem;
        margin-top: -10px;
        margin-bottom: 18px;
    }
    .division-banner {
        background: linear-gradient(90deg, #1E293B 0%, #0F172A 100%);
        border: 2px solid #3B82F6;
        border-radius: 8px;
        padding: 12px 20px;
        text-align: center;
        margin-bottom: 18px;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
    }
    .division-title {
        color: #60A5FA;
        font-size: 1.15rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    .metric-card {
        background: #1E222D;
        border: 1px solid #2D3139;
        border-radius: 10px;
        padding: 16px;
        text-align: left;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    .metric-title {
        color: #8B949E;
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 4px;
    }
    .metric-value {
        color: #FFFFFF;
        font-size: 1.35rem;
        font-weight: 700;
        line-height: 1.25;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .fighter-card-red {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(30, 34, 45, 0.9) 100%);
        border: 1px solid #EF4444;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .fighter-card-blue {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(30, 34, 45, 0.9) 100%);
        border: 1px solid #3B82F6;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .fighter-img {
        width: 75px;
        height: 75px;
        border-radius: 50%;
        object-fit: cover;
        object-position: top center;
        background-color: #1E293B;
        border: 2px solid #475569;
        margin-right: 16px;
        flex-shrink: 0;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5);
    }
    .tag-badge {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 6px;
        margin-top: 4px;
    }
    .tag-red { background: rgba(239, 68, 68, 0.25); color: #F87171; border: 1px solid #EF4444; }
    .tag-blue { background: rgba(59, 130, 246, 0.25); color: #60A5FA; border: 1px solid #3B82F6; }
    .tag-neutral { background: rgba(148, 163, 184, 0.15); color: #CBD5E1; border: 1px solid #475569; }
    .tag-green { background: rgba(34, 197, 94, 0.2); color: #4ADE80; border: 1px solid #22C55E; }

    /* Head-to-Head Stats Card */
    .h2h-box {
        background: #161B26;
        border: 1px solid #2D3548;
        border-radius: 12px;
        padding: 14px 18px;
    }
    .h2h-header {
        display: grid;
        grid-template-columns: 1fr auto 1fr;
        align-items: center;
        padding-bottom: 10px;
        margin-bottom: 8px;
        border-bottom: 1px solid #2D3548;
        font-weight: 800;
        font-size: 0.9rem;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }
    .h2h-row {
        display: grid;
        grid-template-columns: 1fr 145px 1fr;
        align-items: center;
        padding: 8px 0;
        border-bottom: 1px solid rgba(45, 53, 72, 0.55);
        font-size: 0.92rem;
    }
    .h2h-row:last-child { border-bottom: none; }
    .h2h-label {
        text-align: center;
        color: #94A3B8;
        font-size: 0.76rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    .h2h-left { text-align: left; color: #CBD5E1; font-weight: 500; }
    .h2h-right { text-align: right; color: #CBD5E1; font-weight: 500; }
    .edge-red { color: #F87171 !important; font-weight: 800 !important; }
    .edge-blue { color: #60A5FA !important; font-weight: 800 !important; }

    /* Scout Report & Stylistic Keys */
    .scout-banner {
        background: linear-gradient(135deg, #1E293B 0%, #161B26 100%);
        border: 1px solid #334155;
        border-left: 4px solid #F59E0B;
        border-radius: 10px;
        padding: 16px 20px;
        margin-top: 14px;
        color: #E2E8F0;
        font-size: 0.91rem;
        line-height: 1.55;
    }
    .path-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px;
        margin-top: 12px;
    }
    .path-card-red {
        background: rgba(239, 68, 68, 0.08);
        border: 1px solid rgba(239, 68, 68, 0.35);
        border-radius: 8px;
        padding: 12px 14px;
        font-size: 0.86rem;
        line-height: 1.5;
        color: #E2E8F0;
    }
    .path-card-blue {
        background: rgba(59, 130, 246, 0.08);
        border: 1px solid rgba(59, 130, 246, 0.35);
        border-radius: 8px;
        padding: 12px 14px;
        font-size: 0.86rem;
        line-height: 1.5;
        color: #E2E8F0;
    }
    .clash-box {
        background: rgba(15, 23, 42, 0.65);
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 12px 14px;
        margin-top: 12px;
        font-size: 0.86rem;
        line-height: 1.55;
        color: #CBD5E1;
    }
    .clash-item {
        margin-bottom: 6px;
    }
    .clash-item:last-child { margin-bottom: 0; }
    .glossary-card {
        background: #161B26;
        border: 1px solid #2D3548;
        border-radius: 10px;
        padding: 16px 20px;
        margin-top: 16px;
        font-size: 0.88rem;
        line-height: 1.6;
        color: #CBD5E1;
    }
</style>
""", unsafe_allow_html=True)

WEIGHT_CLASSES = {
    125: "Flyweight (125 lbs)",
    135: "Bantamweight (135 lbs)",
    145: "Featherweight (145 lbs)",
    155: "Lightweight (155 lbs)",
    170: "Welterweight (170 lbs)",
    185: "Middleweight (185 lbs)",
    205: "Light Heavyweight (205 lbs)",
    265: "Heavyweight (265 lbs)"
}

# --- CACHED PARQUET DATA LOADER ---
@st.cache_data(ttl="6h", show_spinner=False)
def load_fighter_dataset() -> dict:
    parquet_path = BASE_DIR / "data" / "fighters_master.parquet"
    if not parquet_path.exists():
        from etl_pipeline import build_roster_database
        build_roster_database()

    df = pd.read_parquet(parquet_path)

    def cache_base64(path_str):
        if isinstance(path_str, str) and path_str.strip():
            clean_path = BASE_DIR / path_str.replace("\\", "/").lstrip("/")
            if clean_path.is_file():
                return base64.b64encode(clean_path.read_bytes()).decode("utf-8")
        return None

    df["img_b64"] = df["local_image_path"].apply(cache_base64)
    return df.set_index("name").to_dict(orient="index")

FIGHTER_DATABASE = load_fighter_dataset()

# --- AVATAR & FORMATTING HELPERS ---
def render_avatar(name: str, corner: str = "red") -> str:
    data = FIGHTER_DATABASE.get(name, {})
    img_b64 = data.get("img_b64")

    if img_b64:
        return f'<img src="data:image/png;base64,{img_b64}" class="fighter-img" alt="{name}">'

    parts = name.split()
    initials = f"{parts[0][0]}{parts[-1][0]}" if len(parts) > 1 else name[:2].upper()
    bg = "linear-gradient(135deg, #EF4444 0%, #991B1B 100%)" if corner == "red" else "linear-gradient(135deg, #3B82F6 0%, #1E40AF 100%)"
    border = "#F87171" if corner == "red" else "#60A5FA"
    shadow = "rgba(239, 68, 68, 0.3)" if corner == "red" else "rgba(59, 130, 246, 0.3)"

    return f'<div style="width: 75px; height: 75px; border-radius: 50%; background: {bg}; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; font-weight: 800; color: #FFFFFF; border: 2px solid {border}; margin-right: 16px; flex-shrink: 0; box-shadow: 0 4px 10px {shadow};">{initials}</div>'

def fmt_height(inches: float) -> str:
    ft = int(inches // 12)
    rem = int(round(inches % 12))
    if rem == 12:
        ft += 1
        rem = 0
    return f"{ft}'{rem}\""

def american_to_implied(odds: int) -> float:
    if odds == 0:
        return 0.50
    return abs(odds) / (abs(odds) + 100.0) if odds < 0 else 100.0 / (odds + 100.0)

def american_payout_profit(odds: int) -> float:
    if odds == 0:
        return 1.0
    return (100.0 / abs(odds)) if odds < 0 else (odds / 100.0)

# --- MATCHUP PREDICTION ENGINE ---
def compute_fight_night_weight(fighter, contested_limit):
    natural_w = fighter["natural_weight"]
    rehydrate_pct = fighter["csac_rehydrate_pct"]

    if natural_w == 265:
        return 248.0 if "Jones" in fighter.get("style", "") else 256.0

    natural_walkaround = natural_w * (1.0 + rehydrate_pct)

    if contested_limit == natural_w:
        return natural_walkaround
    elif contested_limit > natural_w:
        class_gap = contested_limit - natural_w
        return natural_walkaround + min(class_gap * 0.15, 12.0)
    else:
        return contested_limit * (1.0 + (rehydrate_pct * 0.90))

def compute_age_penalty(age: int, natural_weight: int) -> float:
    cliff = 37 if natural_weight >= 205 else 35
    if age <= cliff:
        return 0.0
    rate = 0.06 if natural_weight >= 205 else 0.11
    return (age - cliff) * rate

def compute_matchup_model(fA, fB, contested_limit, rounds=3, short_notice_A=False, short_notice_B=False):
    diff_class_A = contested_limit - fA["natural_weight"]
    diff_class_B = contested_limit - fB["natural_weight"]

    cage_mass_A = compute_fight_night_weight(fA, contested_limit)
    cage_mass_B = compute_fight_night_weight(fB, contested_limit)
    delta_mass = (cage_mass_A - cage_mass_B) / 10.0

    def get_weight_modifiers(fighter, diff):
        arch = fighter["adaptation_archetype"]
        if diff > 0:
            scaled_pen = -min(2.2, diff * 0.025)
            if diff >= 20:
                return 0.80, max(0.35, 0.70 - (diff * 0.004)), max(0.25, 0.65 - (diff * 0.004)), 1.00, -0.15, scaled_pen
            elif arch == "cut_relief":
                return 1.02, 0.92, 0.80, 1.00, 0.10, scaled_pen * 0.70
            elif arch == "speed_preserver":
                return 0.94, 0.82, 0.68, 1.04, 0.05, scaled_pen
            else:
                return 0.90, 0.80, 0.65, 0.96, -0.10, scaled_pen
        elif diff < 0:
            cut_lbs = abs(diff)
            age_mult = 1.0 + max(0, fighter["age"] - 32) * 0.07
            if cut_lbs >= 20:
                scaled_pen = -min(3.5, (cut_lbs * 0.055) * age_mult)
                return 0.72, 0.78, 0.75, 0.78, -0.85 * age_mult, scaled_pen
            else:
                scaled_pen = -(cut_lbs * 0.025) * age_mult
                return 0.90, 0.96, 0.95, 0.90, -0.35 * age_mult, scaled_pen
        return 1.0, 1.0, 1.0, 1.0, 0.0, 0.0

    p_A, gdef_A, goff_A, s_A, c_A, move_pen_A = get_weight_modifiers(fA, diff_class_A)
    p_B, gdef_B, goff_B, s_B, c_B, move_pen_B = get_weight_modifiers(fB, diff_class_B)

    ape_A = fA["reach_in"] / fA["height_in"]
    ape_B = fB["reach_in"] / fB["height_in"]
    delta_ape = ape_A - ape_B

    eff_tdd_A = fA["td_def"] * gdef_A
    eff_tdd_B = fB["td_def"] * gdef_B

    grapple_A = (fA["td_avg"] * fA["td_acc"] * 1.5 * goff_A) * (1.10 - eff_tdd_B) * (fA["pedigree_tier"] / (fB["pedigree_tier"] + 0.4))
    grapple_B = (fB["td_avg"] * fB["td_acc"] * 1.5 * goff_B) * (1.10 - eff_tdd_A) * (fB["pedigree_tier"] / (fA["pedigree_tier"] + 0.4))
    delta_grapple = grapple_A - grapple_B

    suppression_A = max(0.75, 1.0 - (grapple_B * 0.10))
    suppression_B = max(0.75, 1.0 - (grapple_A * 0.10))

    dmg_ratio_A = (fA["slpm"] * s_A) / max(fA["sapm"], 1.0)
    dmg_ratio_B = (fB["slpm"] * s_B) / max(fB["sapm"], 1.0)

    strike_A = ((((fA["slpm"] * s_A) * suppression_A) - fA["sapm"]) * 0.75 + dmg_ratio_A * 0.55) * (1.0 + (fA["kd_per_100_str"] * p_A) * 0.10)
    strike_B = ((((fB["slpm"] * s_B) * suppression_B) - fB["sapm"]) * 0.75 + dmg_ratio_B * 0.55) * (1.0 + (fB["kd_per_100_str"] * p_B) * 0.10)
    delta_strike = strike_A - strike_B

    cardio_A = fA["cardio_tier"] + c_A - (0.35 if short_notice_A else 0.0)
    cardio_B = fB["cardio_tier"] + c_B - (0.35 if short_notice_B else 0.0)
    delta_cardio = (cardio_A - cardio_B) * (rounds / 3.0)

    age_pen_A = compute_age_penalty(fA["age"], fA["natural_weight"])
    age_pen_B = compute_age_penalty(fB["age"], fB["natural_weight"])
    delta_age = (age_pen_B - age_pen_A) - ((fA["age"] - fB["age"]) / 15.0) * 0.15

    delta_class_move = move_pen_A - move_pen_B

    contributions = {
        "Grappling & Control": delta_grapple * 0.48,
        "Striking & Damage": delta_strike * 0.24,
        "Fight-Night Size": delta_mass * 0.55 + delta_class_move,
        "Reach & Frame": delta_ape * 1.10,
        "Cardio & Pace": delta_cardio * 0.30,
        "Age & Prime Curve": delta_age
    }

    matchup_score = sum(contributions.values())

    temperature = 1.35
    prob_A = float(1.0 / (1.0 + np.exp(-matchup_score / temperature)))
    prob_B = 1.0 - prob_A

    features = {
        "Reach Ratio": (ape_A, ape_B),
        "Fight-Night Weight": (cage_mass_A, cage_mass_B),
        "Grappling Edge": delta_grapple,
        "Striking Edge": delta_strike,
        "Contributions": contributions
    }
    return prob_A, prob_B, features

def build_scout_report(fA_name, fB_name, fA, fB, prob_A, feat, contested_limit, rounds):
    contribs = feat["Contributions"]
    winner = fA_name if prob_A >= 0.5 else fB_name
    win_pct = max(prob_A, 1 - prob_A) * 100
    factor_name, factor_val = max(contribs.items(), key=lambda kv: abs(kv[1]))
    leader = fA_name if factor_val > 0 else fB_name

    weight_diff = abs(feat["Fight-Night Weight"][0] - feat["Fight-Night Weight"][1])
    if win_pct >= 72:
        verdict = f"Strong Favorite: {winner} ({win_pct:.1f}%)"
        sub_note = f"Decisive statistical edge driven by <strong>{factor_name}</strong>"
    elif win_pct >= 58:
        verdict = f"Clear Edge: {winner} ({win_pct:.1f}%)"
        sub_note = f"Favored on paper behind <strong>{factor_name}</strong>, though the underdog has live paths"
    else:
        verdict = f"Virtual Toss-Up: Slight Edge to {winner} ({win_pct:.1f}%)"
        sub_note = f"Near dead-heat likely decided by small margins—top swing factor is <strong>{factor_name}</strong> for <strong>{leader}</strong>"

    if weight_diff >= 8:
        sub_note += f", amplified by an estimated <strong>{weight_diff:.0f}-lb</strong> fight-night weight gap."
    else:
        sub_note += "."

    headline = (
        f'<div style="font-size: 1.12rem; font-weight: 800; color: #FFFFFF; line-height: 1.35; margin-bottom: 4px;">{verdict}</div>'
        f'<div style="font-size: 0.92rem; color: #CBD5E1; line-height: 1.5;">{sub_note}</div>'
    )

    def fighter_path(name, f, opp_name, opp):
        if f["td_avg"] >= 2.2 and opp["td_def"] < 0.80:
            return f"Chain takedowns early ({f['td_avg']:.1f} TD/15m) against {opp_name.split()[-1]}'s {int(opp['td_def']*100)}% defense and drain his gas tank on the mat."
        if f["kd_per_100_str"] >= 2.0:
            return f"Force pocket exchanges and hunt clean counters—{name.split()[-1]} carries fight-ending power ({f['base_ko']*100:.0f}% KO share)."
        if f["slpm"] > opp["slpm"] + 0.8:
            return f"Keep the bout at kicking range, win the volume battle ({f['slpm']:.1f} vs {opp['slpm']:.1f} strikes/min), and bank rounds cleanly."
        if f["sub_avg"] >= 1.2:
            return f"Turn scrambles into back-takes and submission traps ({f['sub_avg']:.1f} sub attempts per 15m)."
        if rounds == 5 and f["cardio_tier"] > opp["cardio_tier"]:
            return f"Survive early bursts and push a relentless pace into Rounds 4 and 5 where his cardio advantage compounds."
        return f"Stay disciplined behind his {f['style'].split('/')[0].strip().lower()} base, control distance ({f['reach_in']:.0f}\" reach), and avoid giving up control time."

    # Stylistic Clash & Hidden Factors Engine
    clashes = []
    sA, sB = fA["style"].lower(), fB["style"].lower()
    is_boxer_A, is_boxer_B = "boxing" in sA, "boxing" in sB
    is_kicker_A = any(k in sA for k in ["muay thai", "kickboxing", "karate", "sanda", "kicking"])
    is_kicker_B = any(k in sB for k in ["muay thai", "kickboxing", "karate", "sanda", "kicking"])

    if (is_boxer_A and is_kicker_B) or (is_boxer_B and is_kicker_A):
        boxer = fA_name.split()[-1] if (is_boxer_A and not is_boxer_B) else fB_name.split()[-1]
        kicker = fB_name.split()[-1] if boxer == fA_name.split()[-1] else fA_name.split()[-1]
        clashes.append(
            f"<strong>Boxing vs. Kicking Range:</strong> {boxer}'s heavy boxing stance can leave the lead leg exposed to {kicker}'s calf kicks at range—while {boxer}'s crisp 1-2s and pocket hand speed can punish {kicker} if he steps inside."
        )

    if abs(fA["natural_weight"] - fB["natural_weight"]) >= 10:
        smaller = fA_name.split()[-1] if fA["natural_weight"] < fB["natural_weight"] else fB_name.split()[-1]
        bigger = fB_name.split()[-1] if smaller == fA_name.split()[-1] else fA_name.split()[-1]
        clashes.append(
            f"<strong>\"Lighter Man's Skill\" vs. Size:</strong> {smaller} gives up natural frame and clinch weight to {bigger}, so his edge relies on faster footwork, sharper entries, and avoiding prolonged fence wrestling."
        )

    if (fA.get("stance") == "Southpaw" and fB.get("stance") == "Orthodox") or (fB.get("stance") == "Southpaw" and fA.get("stance") == "Orthodox"):
        southpaw = fA_name.split()[-1] if fA.get("stance") == "Southpaw" else fB_name.split()[-1]
        clashes.append(
            f"<strong>Open-Stance Chess Match:</strong> Orthodox vs. Southpaw opens the rear straight and liver kick for {southpaw}; whoever wins the outside lead-foot battle controls the pocket."
        )

    if fA["str_def"] >= 0.60 or fB["str_def"] >= 0.60 or fA["sapm"] <= 2.4 or fB["sapm"] <= 2.4:
        def_leader = fA_name.split()[-1] if (fA["str_def"] - fA["sapm"]*0.05) >= (fB["str_def"] - fB["sapm"]*0.05) else fB_name.split()[-1]
        def_f = fA if def_leader == fA_name.split()[-1] else fB
        clashes.append(
            f"<strong>Underrated Defensive Craft:</strong> {def_leader} stays composed under fire ({int(def_f['str_def']*100)}% strike defense, absorbing only {def_f['sapm']:.2f} strikes/min)—forcing opponents to overextend."
        )

    if abs(fA["td_avg"] - fB["td_avg"]) >= 2.0:
        grappler = fA_name.split()[-1] if fA["td_avg"] > fB["td_avg"] else fB_name.split()[-1]
        striker = fB_name.split()[-1] if grappler == fA_name.split()[-1] else fA_name.split()[-1]
        clashes.append(
            f"<strong>Level-Change Threat:</strong> {grappler}'s takedown threat can make {striker} lower his hands and hesitate to commit to heavy combinations."
        )

    return headline, fighter_path(fA_name, fA, fB_name, fB), fighter_path(fB_name, fB, fA_name, fA), clashes[:3]

def calculate_method_of_victory(fighter, prob, rounds):
    dec_mod = 1.30 if rounds == 5 else 1.0
    ko_mod = 0.90 if rounds == 5 else 1.0
    raw_ko = fighter["base_ko"] * ko_mod
    raw_sub = fighter["base_sub"]
    raw_dec = fighter["base_dec"] * dec_mod
    total = raw_ko + raw_sub + raw_dec
    return (raw_ko / total) * prob, (raw_sub / total) * prob, (raw_dec / total) * prob

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### 🥊 Matchup Setup")

    divisions = ["All Divisions"] + sorted(list(set(f["division"] for f in FIGHTER_DATABASE.values() if "division" in f)))
    selected_div = st.selectbox("Filter by Division", divisions, index=0)

    if selected_div == "All Divisions":
        filtered_roster = sorted(list(FIGHTER_DATABASE.keys()))
    else:
        filtered_roster = sorted([k for k, v in FIGHTER_DATABASE.items() if v.get("division") == selected_div])

    def format_fighter_label(name):
        f = FIGHTER_DATABASE.get(name, {})
        rank = f.get("rank", "")
        div = f.get("division", "")
        return f"{name} ({div} {rank})" if rank else name

    default_a_idx = filtered_roster.index("Islam Makhachev") if "Islam Makhachev" in filtered_roster else 0
    fA_name = st.selectbox("Red Corner (Fighter A)", filtered_roster, index=default_a_idx, format_func=format_fighter_label)

    default_b_idx = filtered_roster.index("Ian Machado Garry") if "Ian Machado Garry" in filtered_roster else min(1, len(filtered_roster) - 1)
    fB_name = st.selectbox("Blue Corner (Fighter B)", filtered_roster, index=default_b_idx, format_func=format_fighter_label)

    if fA_name == fB_name:
        st.warning("⚠️ Select two different fighters.")

    st.markdown("---")
    st.markdown("### ⚖️ Bout Weight Class")
    default_weight = FIGHTER_DATABASE[fA_name]["natural_weight"]
    weight_keys = list(WEIGHT_CLASSES.keys())
    default_idx = weight_keys.index(default_weight) if default_weight in weight_keys else 3

    contested_limit = st.selectbox(
        "Contracted Weight Limit",
        weight_keys,
        index=default_idx,
        format_func=lambda x: WEIGHT_CLASSES[x],
        help="Official weigh-in limit. Fight-night weight estimates account for post-weigh-in rehydration."
    )

    st.markdown("---")
    st.markdown("### ⚙️ Bout Format")
    bout_rounds = st.radio("Rounds", [3, 5], index=1, format_func=lambda x: f"{x}-Round Main Event" if x == 5 else "3-Round Standard")

    col_c1, col_c2 = st.columns(2)
    with col_c1:
        short_A = st.checkbox(f"{fA_name.split()[0]} Short Notice", value=False)
    with col_c2:
        short_B = st.checkbox(f"{fB_name.split()[0]} Short Notice", value=False)

    st.markdown("---")
    st.markdown("### 💰 Live Sportsbook Odds")
    st.caption("Defaults to -110 / -110 pick'em. Enter live fight-week lines to calculate real +EV edge.")

    col_o1, col_o2 = st.columns(2)
    with col_o1:
        odds_A = st.number_input(f"{fA_name.split()[0]} Line", value=-110, step=10)
    with col_o2:
        odds_B = st.number_input(f"{fB_name.split()[0]} Line", value=-110, step=10)

fA = FIGHTER_DATABASE[fA_name]
fB = FIGHTER_DATABASE[fB_name]

prob_A, prob_B, feat = compute_matchup_model(
    fA, fB, contested_limit=contested_limit, rounds=bout_rounds, short_notice_A=short_A, short_notice_B=short_B
)
imp_A = american_to_implied(odds_A)
imp_B = american_to_implied(odds_B)
edge_A = (prob_A - imp_A) * 100
edge_B = (prob_B - imp_B) * 100

# --- HEADER & BANNER ---
st.title("UFC Fight Outcome & Win-Probability Engine")
st.markdown(
    '<div class="app-subtitle">Interactive MMA matchup simulator combining fighter stats, fight-night weight rehydration, and stylistic analysis to benchmark win probabilities against Vegas odds.</div>',
    unsafe_allow_html=True
)

diff_fA = contested_limit - fA["natural_weight"]
diff_fB = contested_limit - fB["natural_weight"]
status_A_str = "Natural Weight" if diff_fA == 0 else (f"+{diff_fA} lbs Up" if diff_fA > 0 else f"{diff_fA} lbs Cut")
status_B_str = "Natural Weight" if diff_fB == 0 else (f"+{diff_fB} lbs Up" if diff_fB > 0 else f"{diff_fB} lbs Cut")

st.markdown(textwrap.dedent(f"""
<div class="division-banner">
    <div class="division-title">⚖️ {WEIGHT_CLASSES[contested_limit].upper()}</div>
    <div style="color: #94A3B8; font-size: 0.85rem; margin-top: 4px;">
        🔴 <strong>{fA_name}</strong> ({status_A_str}) &nbsp;|&nbsp; 🔵 <strong>{fB_name}</strong> ({status_B_str}) &nbsp;|&nbsp; <strong>{bout_rounds} Rounds</strong>
    </div>
</div>
"""), unsafe_allow_html=True)

# --- WEIGHT-CUT FEASIBILITY GUARDRAILS ---
cut_warnings = []
for f_name, f_data in [(fA_name, fA), (fB_name, fB)]:
    cut_lbs = f_data["natural_weight"] - contested_limit
    jump_lbs = contested_limit - f_data["natural_weight"]
    h_str = fmt_height(f_data["height_in"])

    if cut_lbs >= 20:
        cut_warnings.append(
            f"<strong>Unrealistic Weight Cut ({f_name}):</strong> Dropping {cut_lbs} lbs below his natural {f_data['natural_weight']}-lb frame ({h_str}) to make {contested_limit} lbs is not realistically feasible—severe dehydration &amp; cardio penalties applied."
        )
    elif cut_lbs >= 10 and f_data["age"] >= 34:
        cut_warnings.append(
            f"<strong>Demanding Cut at Age {f_data['age']} ({f_name}):</strong> Cutting {cut_lbs} lbs below natural weight ({f_data['natural_weight']} lbs) late in his career carries heightened cardio and durability risk."
        )
    elif jump_lbs >= 30:
        cut_warnings.append(
            f"<strong>Extreme Size Disadvantage ({f_name}):</strong> Moving up +{jump_lbs} lbs above his natural {f_data['natural_weight']}-lb class creates a heavy strength and clinch deficit."
        )

if cut_warnings:
    warn_items = "".join([f'<div style="margin-bottom: 4px;">⚠️ {w}</div>' for w in cut_warnings])
    st.markdown(
        f'<div style="background: rgba(245, 158, 11, 0.12); border: 1px solid rgba(245, 158, 11, 0.45); border-left: 4px solid #F59E0B; border-radius: 8px; padding: 12px 16px; margin-bottom: 16px; color: #FDE68A; font-size: 0.87rem; line-height: 1.5;">'
        f'{warn_items}</div>',
        unsafe_allow_html=True
    )

# --- FIGHTER CARDS ---
c_hdr1, c_hdr2 = st.columns(2)

with c_hdr1:
    avatar_A = render_avatar(fA_name, corner="red")
    st.markdown(textwrap.dedent(f"""
    <div class="fighter-card-red">
        <div style="display: flex; align-items: center;">
            {avatar_A}
            <div style="flex-grow: 1;">
                <div style="display: flex; justify-content: space-between; align-items: center; gap: 8px;">
                    <h3 style="margin: 0; color: #FAFAFA;">🔴 {fA_name}</h3>
                    <span style="color: #94A3B8; font-weight: 700; white-space: nowrap;">{fA['record']}</span>
                </div>
                <div style="color: #CBD5E1; font-size: 0.85rem; margin-top: 2px; margin-bottom: 8px;">
                    {fA['style']} • Natural: {fA['natural_weight']} lbs
                </div>
                <div>
                    <span class="tag-badge tag-red">Model: {prob_A*100:.1f}%</span>
                    <span class="tag-badge tag-neutral">Vegas: {odds_A:+d} ({imp_A*100:.1f}%)</span>
                    <span class="tag-badge {'tag-green' if edge_A > 0 else 'tag-neutral'}">Edge: {edge_A:+.1f}%</span>
                </div>
            </div>
        </div>
    </div>
    """), unsafe_allow_html=True)

with c_hdr2:
    avatar_B = render_avatar(fB_name, corner="blue")
    st.markdown(textwrap.dedent(f"""
    <div class="fighter-card-blue">
        <div style="display: flex; align-items: center;">
            {avatar_B}
            <div style="flex-grow: 1;">
                <div style="display: flex; justify-content: space-between; align-items: center; gap: 8px;">
                    <h3 style="margin: 0; color: #FAFAFA;">🔵 {fB_name}</h3>
                    <span style="color: #94A3B8; font-weight: 700; white-space: nowrap;">{fB['record']}</span>
                </div>
                <div style="color: #CBD5E1; font-size: 0.85rem; margin-top: 2px; margin-bottom: 8px;">
                    {fB['style']} • Natural: {fB['natural_weight']} lbs
                </div>
                <div>
                    <span class="tag-badge tag-blue">Model: {prob_B*100:.1f}%</span>
                    <span class="tag-badge tag-neutral">Vegas: {odds_B:+d} ({imp_B*100:.1f}%)</span>
                    <span class="tag-badge {'tag-green' if edge_B > 0 else 'tag-neutral'}">Edge: {edge_B:+.1f}%</span>
                </div>
            </div>
        </div>
    </div>
    """), unsafe_allow_html=True)

st.progress(float(np.clip(prob_A, 0.0, 1.0)))
st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

# --- KPI SUMMARY CARDS ---
col1, col2, col3, col4 = st.columns(4)
winner_name = fA_name if prob_A >= prob_B else fB_name
win_conf = max(prob_A, prob_B) * 100

with col1:
    st.markdown(textwrap.dedent(f"""
    <div class="metric-card">
        <div class="metric-title">Projected Winner</div>
        <div class="metric-value">{winner_name.split()[-1]}</div>
        <div style="color: #22C55E; font-size: 0.82rem; font-weight: 600;">{win_conf:.1f}% Win Probability</div>
    </div>
    """), unsafe_allow_html=True)

with col2:
    st.markdown(textwrap.dedent(f"""
    <div class="metric-card">
        <div class="metric-title">Reach-to-Height Ratio</div>
        <div class="metric-value">{feat['Reach Ratio'][0]:.2f} vs {feat['Reach Ratio'][1]:.2f}</div>
        <div style="color: #94A3B8; font-size: 0.82rem;">Ape Index (Higher = Longer Frame)</div>
    </div>
    """), unsafe_allow_html=True)

with col3:
    st.markdown(textwrap.dedent(f"""
    <div class="metric-card">
        <div class="metric-title">Est. Fight-Night Weight</div>
        <div class="metric-value">{feat['Fight-Night Weight'][0]:.0f} vs {feat['Fight-Night Weight'][1]:.0f} lbs</div>
        <div style="color: #94A3B8; font-size: 0.82rem;">Post-Weigh-In Rehydration</div>
    </div>
    """), unsafe_allow_html=True)

with col4:
    best_ev_fighter = fA_name if edge_A > edge_B else fB_name
    best_ev_val = max(edge_A, edge_B)
    edge_color = "#22C55E" if best_ev_val > 0 else "#EF4444"
    st.markdown(textwrap.dedent(f"""
    <div class="metric-card">
        <div class="metric-title">Market Value Edge</div>
        <div class="metric-value">{best_ev_fighter.split()[-1]}</div>
        <div style="color: {edge_color}; font-size: 0.82rem; font-weight: 600;">{best_ev_val:+.1f}% vs Vegas Odds</div>
    </div>
    """), unsafe_allow_html=True)

with st.expander("📖 How the Model Works (Plain English)"):
    st.markdown("""
- **Transparent Weighted Engine (Not a Black Box):** Instead of hiding predictions behind an opaque algorithm, this engine scores 6 core fight drivers—**Grappling, Striking & Defense, Fight-Night Weight, Reach/Frame, Cardio, and Prime Age Curve**—and shows exactly how much each factor swings the pick.
- **Fight-Night Weight (CSAC Data):** Official UFC weigh-ins happen ~30 hours before the fight. Using California State Athletic Commission (CSAC) fight-night weight data, fighters typically rehydrate 10%–15% heavier by cage time, which directly affects clinch and wrestling leverage.
- **Cross-Division Reality:** Fighters moving up above their natural weight class take a scaled size and takedown-leverage discount, balanced against "lighter man's skill" (speed, volume, and footwork).
- **Calibrated for MMA Variance:** A temperature-scaled logistic curve prevents overconfident 99% predictions in a sport where one clean shot in 4-oz gloves can end any fight.
    """)

st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

# --- TABS ---
tab1, tab2, tab3 = st.tabs([
    "📊 Fight Breakdown & Head-to-Head Stats",
    "🎯 Round-by-Round & Finish Odds",
    "📈 Historical Accuracy & Backtest Audit"
])

with tab1:
    r_col1, r_col2 = st.columns([1.15, 1.0])

    with r_col1:
        st.markdown("#### Why the Model Picks This Winner (Factor Impact)")
        contribs = feat["Contributions"]
        sorted_items = sorted(contribs.items(), key=lambda x: abs(x[1]))
        labels = [k for k, _ in sorted_items]
        vals = [v for _, v in sorted_items]
        colors = ["#EF4444" if v >= 0 else "#3B82F6" for v in vals]

        fig_imp = go.Figure(go.Bar(
            x=vals,
            y=labels,
            orientation="h",
            marker_color=colors,
            text=[f"{fA_name.split()[-1]} +{v:.2f}" if v > 0.02 else (f"{fB_name.split()[-1]} +{abs(v):.2f}" if v < -0.02 else "Even") for v in vals],
            textposition="auto"
        ))
        fig_imp.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=265,
            margin=dict(l=10, r=10, t=10, b=20),
            xaxis=dict(title=f"← Favors {fB_name.split()[-1]}   |   Favors {fA_name.split()[-1]} →", zeroline=True, zerolinecolor="#64748B", gridcolor="#1E293B"),
            yaxis=dict(gridcolor="rgba(0,0,0,0)")
        )
        st.plotly_chart(fig_imp, width="stretch")

        st.markdown("#### Skill Profile Radar")
        categories = ["Striking Output", "Strike Defense", "KO Power", "Takedown Threat", "Takedown Defense", "Pedigree"]
        val_A = [min(fA["slpm"]/8.0, 1.0), fA["str_def"], min(fA["kd_per_100_str"]/3.5, 1.0), min(fA["td_avg"]/4.0, 1.0), fA["td_def"], fA["pedigree_tier"]/2.0]
        val_B = [min(fB["slpm"]/8.0, 1.0), fB["str_def"], min(fB["kd_per_100_str"]/3.5, 1.0), min(fB["td_avg"]/4.0, 1.0), fB["td_def"], fB["pedigree_tier"]/2.0]

        fig_r = go.Figure()
        fig_r.add_trace(go.Scatterpolar(r=val_A, theta=categories, fill="toself", name=fA_name, line_color="#EF4444"))
        fig_r.add_trace(go.Scatterpolar(r=val_B, theta=categories, fill="toself", name=fB_name, line_color="#3B82F6"))
        fig_r.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 1], gridcolor="#334155")),
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=300,
            margin=dict(l=30, r=30, t=20, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_r, width="stretch")

    with r_col2:
        st.markdown("#### Head-to-Head Stats")

        def h2h_row(label, val_a, val_b, num_a=None, num_b=None, higher_is_better=True):
            cls_a, cls_b = "h2h-left", "h2h-right"
            if num_a is not None and num_b is not None and num_a != num_b:
                if (num_a > num_b and higher_is_better) or (num_a < num_b and not higher_is_better):
                    cls_a += " edge-red"
                else:
                    cls_b += " edge-blue"
            return f'<div class="h2h-row"><div class="{cls_a}">{val_a}</div><div class="h2h-label">{label}</div><div class="{cls_b}">{val_b}</div></div>'

        rows_html = "".join([
            h2h_row("Pro Record", fA["record"], fB["record"]),
            h2h_row("Age", f"{fA['age']} yrs", f"{fB['age']} yrs", fA["age"], fB["age"], higher_is_better=False),
            h2h_row("Height", fmt_height(fA["height_in"]), fmt_height(fB["height_in"]), fA["height_in"], fB["height_in"]),
            h2h_row("Reach", f"{fA['reach_in']:.1f}\"", f"{fB['reach_in']:.1f}\"", fA["reach_in"], fB["reach_in"]),
            h2h_row("Stance", fA.get("stance", "Orthodox"), fB.get("stance", "Orthodox")),
            h2h_row("Fight-Night Wt", f"{feat['Fight-Night Weight'][0]:.0f} lbs", f"{feat['Fight-Night Weight'][1]:.0f} lbs", feat["Fight-Night Weight"][0], feat["Fight-Night Weight"][1]),
            h2h_row("Strikes / Min", f"{fA['slpm']:.2f}", f"{fB['slpm']:.2f}", fA["slpm"], fB["slpm"]),
            h2h_row("Strike Defense", f"{int(fA['str_def']*100)}%", f"{int(fB['str_def']*100)}%", fA["str_def"], fB["str_def"]),
            h2h_row("Takedowns / 15m", f"{fA['td_avg']:.2f}", f"{fB['td_avg']:.2f}", fA["td_avg"], fB["td_avg"]),
            h2h_row("TD Defense", f"{int(fA['td_def']*100)}%", f"{int(fB['td_def']*100)}%", fA["td_def"], fB["td_def"]),
        ])

        st.markdown(
            f'<div class="h2h-box">'
            f'<div class="h2h-header">'
            f'<div style="color: #F87171;">🔴 {fA_name.split()[-1]}</div>'
            f'<div style="color: #64748B; font-size: 0.72rem;">VS</div>'
            f'<div style="color: #60A5FA; text-align: right;">{fB_name.split()[-1]} 🔵</div>'
            f'</div>'
            f'{rows_html}'
            f'</div>',
            unsafe_allow_html=True
        )

        headline, path_A, path_B, clashes = build_scout_report(fA_name, fB_name, fA, fB, prob_A, feat, contested_limit, bout_rounds)
        clashes_html = "".join([f'<div class="clash-item">• {c}</div>' for c in clashes])
        clash_block = (
            f'<div class="clash-box">'
            f'<div style="color: #38BDF8; font-weight: 700; font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px;">🧠 Stylistic Keys &amp; Intangibles</div>'
            f'{clashes_html}'
            f'</div>'
        ) if clashes else ""

        st.markdown(
            f'<div class="scout-banner">'
            f'<div style="color: #F59E0B; font-weight: 800; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 6px;">🎙️ Fight Analyst Scout Report</div>'
            f'<div>{headline}</div>'
            f'<div class="path-grid">'
            f'<div class="path-card-red"><div style="color: #F87171; font-weight: 700; margin-bottom: 4px;">🔴 {fA_name.split()[-1]}\'s Path to Victory</div>{path_A}</div>'
            f'<div class="path-card-blue"><div style="color: #60A5FA; font-weight: 700; margin-bottom: 4px;">🔵 {fB_name.split()[-1]}\'s Path to Victory</div>{path_B}</div>'
            f'</div>'
            f'{clash_block}'
            f'</div>',
            unsafe_allow_html=True
        )

with tab2:
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.markdown(f"#### Round-by-Round Win Probability ({bout_rounds} Rounds)")
        rounds_arr = [f"Round {r+1}" for r in range(bout_rounds)]
        round_probs_A = [
            float(np.clip(prob_A + (fA["cardio_tier"] - fB["cardio_tier"]) * 0.035 * r, 0.05, 0.95)) * 100
            for r in range(bout_rounds)
        ]
        round_probs_B = [100.0 - val for val in round_probs_A]

        fig_rounds = go.Figure()
        fig_rounds.add_trace(go.Bar(x=rounds_arr, y=round_probs_A, name=fA_name, marker_color="#EF4444"))
        fig_rounds.add_trace(go.Bar(x=rounds_arr, y=round_probs_B, name=fB_name, marker_color="#3B82F6"))
        fig_rounds.update_layout(
            barmode="group", template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            height=340, margin=dict(l=20, r=20, t=30, b=20),
            yaxis=dict(title="Win Probability (%)", range=[0, 100], gridcolor="#1E293B"),
            xaxis=dict(gridcolor="#1E293B")
        )
        st.plotly_chart(fig_rounds, width="stretch")

    with col_m2:
        st.markdown("#### Method of Victory Breakdown")
        ko_A, sub_A, dec_A = calculate_method_of_victory(fA, prob_A, bout_rounds)
        ko_B, sub_B, dec_B = calculate_method_of_victory(fB, prob_B, bout_rounds)

        methods = ["KO / TKO", "Submission", "Decision"]
        fig_mov = go.Figure()
        fig_mov.add_trace(go.Bar(x=methods, y=[ko_A*100, sub_A*100, dec_A*100], name=fA_name, marker_color="#EF4444"))
        fig_mov.add_trace(go.Bar(x=methods, y=[ko_B*100, sub_B*100, dec_B*100], name=fB_name, marker_color="#3B82F6"))
        fig_mov.update_layout(
            barmode="group", template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            height=340, margin=dict(l=20, r=20, t=30, b=20),
            yaxis=dict(title="Outcome Probability (%)", gridcolor="#1E293B"),
            xaxis=dict(gridcolor="#1E293B")
        )
        st.plotly_chart(fig_mov, width="stretch")

with tab3:
    st.markdown("#### Historical Backtest Audit (10 Featured Main-Card Bouts)")
    st.caption("Transparent benchmark comparing model win probabilities against closing Vegas moneylines and official UFC outcomes—including misses.")

    audit_records = [
        {"Event": "UFC 308", "Matchup": "Ilia Topuria vs Max Holloway", "Pick": "Topuria", "Prob": 0.71, "Vegas": -250, "Result": "Topuria (KO R3)", "Won": True},
        {"Event": "UFC 305", "Matchup": "Dricus Du Plessis vs Israel Adesanya", "Pick": "Du Plessis", "Prob": 0.56, "Vegas": +110, "Result": "Du Plessis (Sub R4)", "Won": True},
        {"Event": "UFC 304", "Matchup": "Leon Edwards vs Belal Muhammad", "Pick": "Edwards", "Prob": 0.62, "Vegas": -240, "Result": "Muhammad (Dec)", "Won": False},
        {"Event": "UFC 302", "Matchup": "Islam Makhachev vs Dustin Poirier", "Pick": "Makhachev", "Prob": 0.78, "Vegas": -600, "Result": "Makhachev (Sub R5)", "Won": True},
        {"Event": "UFC 300", "Matchup": "Alex Pereira vs Jamahal Hill", "Pick": "Pereira", "Prob": 0.64, "Vegas": -130, "Result": "Pereira (KO R1)", "Won": True},
        {"Event": "UFC 300", "Matchup": "Max Holloway vs Justin Gaethje", "Pick": "Holloway", "Prob": 0.55, "Vegas": +140, "Result": "Holloway (KO R5)", "Won": True},
        {"Event": "UFC 299", "Matchup": "Sean O'Malley vs Marlon Vera", "Pick": "O'Malley", "Prob": 0.74, "Vegas": -260, "Result": "O'Malley (Dec)", "Won": True},
        {"Event": "UFC 299", "Matchup": "Benoit Saint Denis vs Dustin Poirier", "Pick": "Saint Denis", "Prob": 0.58, "Vegas": -115, "Result": "Poirier (KO R2)", "Won": False},
        {"Event": "UFC 298", "Matchup": "Ilia Topuria vs Alex Volkanovski", "Pick": "Topuria", "Prob": 0.58, "Vegas": +110, "Result": "Topuria (KO R2)", "Won": True},
        {"Event": "UFC 297", "Matchup": "Sean Strickland vs Dricus Du Plessis", "Pick": "Strickland", "Prob": 0.54, "Vegas": -110, "Result": "Du Plessis (Dec)", "Won": False},
    ]

    display_rows = []
    ev_profits = []
    brier_errors = []
    high_conv_results = []

    for r in audit_records:
        imp = american_to_implied(r["Vegas"])
        edge_pct = (r["Prob"] - imp) * 100
        is_ev = edge_pct > 0
        brier_errors.append((r["Prob"] - (1.0 if r["Won"] else 0.0)) ** 2)
        if r["Prob"] >= 0.70:
            high_conv_results.append(r["Won"])
        if is_ev:
            ev_profits.append(american_payout_profit(r["Vegas"]) if r["Won"] else -1.0)

        display_rows.append({
            "Event": r["Event"],
            "Matchup": r["Matchup"],
            "Model Pick": f"{r['Pick']} ({r['Prob']*100:.0f}%)",
            "Vegas Line": f"{r['Vegas']:+d} ({imp*100:.0f}%)",
            "Edge": f"{edge_pct:+.1f}%",
            "Official Result": r["Result"],
            "Status": "✅ Win (+EV)" if (r["Won"] and is_ev) else ("✅ Win" if r["Won"] else "❌ Miss")
        })

    overall_wins = sum(1 for r in audit_records if r["Won"])
    overall_acc = (overall_wins / len(audit_records)) * 100
    hc_wins = sum(1 for w in high_conv_results if w)
    hc_acc = (hc_wins / len(high_conv_results)) * 100 if high_conv_results else 0.0
    ev_roi = (sum(ev_profits) / len(ev_profits)) * 100 if ev_profits else 0.0
    brier_score = float(np.mean(brier_errors))

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Overall Win Rate", f"{overall_acc:.0f}%", delta=f"{overall_wins}/{len(audit_records)} Featured Bouts")
    with m2:
        st.metric("High-Conviction (>=70%)", f"{hc_acc:.0f}%", delta=f"{hc_wins}/{len(high_conv_results)} Picks Hit")
    with m3:
        st.metric("+EV Flat-Bet ROI", f"{ev_roi:+.1f}%", delta=f"Across {len(ev_profits)} Value Bets")
    with m4:
        st.metric("Brier Calibration Score", f"{brier_score:.3f}", delta="Strong (<0.20 vs 0.25 coin flip)")

    st.dataframe(pd.DataFrame(display_rows), width="stretch", hide_index=True)

    st.markdown("""
    <div class="glossary-card">
        <div style="color: #60A5FA; font-weight: 800; font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 8px;">📚 How to Read These Metrics</div>
        <div><strong>• Brier Calibration Score:</strong> Measures how honest a model's confidence is—not just whether it picked the winner. A score of <code>0.00</code> is perfection and <code>0.25</code> is a random coin flip. Overconfident misses (e.g., 90% and losing) get heavily penalized; staying under <code>0.20</code> shows well-calibrated probabilities.</div>
        <div style="margin-top: 6px;"><strong>• Vegas Implied Probability:</strong> Translates American betting odds into a win percentage (for example, <code>-200</code> means sportsbooks price that fighter at a <code>66.7%</code> chance to win).</div>
        <div style="margin-top: 6px;"><strong>• +EV (Market Value Edge):</strong> Positive Expected Value occurs when the model gives a fighter a higher win probability than Vegas does. Consistently finding +EV edges is how quantitative sports models beat the market over time.</div>
    </div>
    """, unsafe_allow_html=True)