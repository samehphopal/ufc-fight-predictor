import os
import re
import urllib.parse
from pathlib import Path
import pandas as pd
import requests

ASSET_DIR = Path("assets/fighters")
DATA_DIR = Path("data")
ASSET_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "UFCPredictorApp/1.0 (https://github.com/samehphopal/ufc-fight-predictor; contact@ufcengine.local)",
    "Accept": "application/json,image/*"
})

def generate_slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")

def resolve_and_save_asset(name: str, wiki_title: str, slug: str) -> str:
    local_file = ASSET_DIR / f"{slug}.png"
    
    # If a valid image file already exists locally (> 2KB), keep it
    if local_file.exists() and local_file.stat().st_size > 2048:
        print(f"  ⚡ [CACHED] {slug}.png ({local_file.stat().st_size // 1024} KB)")
        return str(local_file)
        
    try:
        title_encoded = urllib.parse.quote(wiki_title.replace(" ", "_"))
        api_url = f"https://en.wikipedia.org/w/api.php?action=query&titles={title_encoded}&prop=pageimages&format=json&pithumbsize=400"
        resp = SESSION.get(api_url, timeout=5)
        if resp.status_code == 200:
            pages = resp.json().get("query", {}).get("pages", {})
            page = next(iter(pages.values()))
            img_url = page.get("thumbnail", {}).get("source")
            if img_url:
                img_resp = SESSION.get(img_url, timeout=8)
                if img_resp.status_code == 200 and len(img_resp.content) > 1000:
                    with open(local_file, "wb") as f:
                        f.write(img_resp.content)
                    print(f"  ✅ [FETCHED] {slug}.png ({len(img_resp.content) // 1024} KB)")
                    return str(local_file)
    except Exception:
        pass

    print(f"  ℹ️ [AVATAR BADGE ACTIVE] {slug}")
    return ""

def build_roster_database():
    print("🚀 Compiling Contenders Dataset & Serializing to Parquet...\n")
    
    fighters = [
        # --- HEAVYWEIGHT (265 LBS) ---
        {
            "name": "Tom Aspinall", "division": "Heavyweight", "rank": "Champion", "record": "15-3-0", "natural_weight": 265,
            "style": "Heavyweight Boxing / BJJ Black Belt", "adaptation_archetype": "natural_frame",
            "slpm": 7.72, "str_acc": 0.66, "sapm": 2.77, "str_def": 0.67,
            "td_avg": 3.38, "td_acc": 1.00, "td_def": 1.00, "sub_avg": 1.70,
            "reach_in": 78.0, "height_in": 77.0, "age": 31, "stance": "Orthodox",
            "csac_rehydrate_pct": 0.000, "kd_per_100_str": 3.8, "pedigree_tier": 1.8, "cardio_tier": 1.75,
            "base_ko": 0.75, "base_sub": 0.20, "base_dec": 0.05, "vegas_baseline": -240,
            "wiki_title": "Tom Aspinall",
            "trivia": "Averages the shortest fight time in UFC history at 2 minutes and 2 seconds."
        },
        {
            "name": "Jon Jones", "division": "Heavyweight", "rank": "#1 Contender", "record": "28-1-0", "natural_weight": 265,
            "style": "Greco-Roman Wrestling / Gaidojutsu", "adaptation_archetype": "natural_frame",
            "slpm": 4.30, "str_acc": 0.58, "sapm": 2.22, "str_def": 0.64,
            "td_avg": 1.85, "td_acc": 0.45, "td_def": 0.95, "sub_avg": 0.80,
            "reach_in": 84.5, "height_in": 76.0, "age": 37, "stance": "Orthodox",
            "csac_rehydrate_pct": 0.000, "kd_per_100_str": 1.4, "pedigree_tier": 2.0, "cardio_tier": 1.85,
            "base_ko": 0.38, "base_sub": 0.28, "base_dec": 0.34, "vegas_baseline": -260,
            "wiki_title": "Jon Jones",
            "trivia": "Holds an 84.5-inch reach—the longest wingspan in modern UFC history."
        },
        {
            "name": "Ciryl Gane", "division": "Heavyweight", "rank": "#2 Contender", "record": "12-2-0", "natural_weight": 265,
            "style": "Technical Muay Thai / Distance Movement", "adaptation_archetype": "speed_preserver",
            "slpm": 5.26, "str_acc": 0.59, "sapm": 2.25, "str_def": 0.62,
            "td_avg": 0.61, "td_acc": 0.21, "td_def": 0.55, "sub_avg": 0.50,
            "reach_in": 81.0, "height_in": 76.0, "age": 34, "stance": "Orthodox",
            "csac_rehydrate_pct": 0.000, "kd_per_100_str": 1.1, "pedigree_tier": 1.2, "cardio_tier": 1.90,
            "base_ko": 0.50, "base_sub": 0.25, "base_dec": 0.25, "vegas_baseline": +185,
            "wiki_title": "Ciryl Gane",
            "trivia": "Maintains an elite +3.01 significant strike differential at Heavyweight."
        },
        {
            "name": "Alexander Volkov", "division": "Heavyweight", "rank": "#3 Contender", "record": "38-10-0", "natural_weight": 265,
            "style": "Tsu Shin Gen Karate / Long-Range Kickboxing", "adaptation_archetype": "natural_frame",
            "slpm": 5.15, "str_acc": 0.57, "sapm": 3.05, "str_def": 0.54,
            "td_avg": 0.52, "td_acc": 0.66, "td_def": 0.73, "sub_avg": 0.20,
            "reach_in": 80.0, "height_in": 79.0, "age": 36, "stance": "Orthodox",
            "csac_rehydrate_pct": 0.000, "kd_per_100_str": 1.0, "pedigree_tier": 1.3, "cardio_tier": 1.80,
            "base_ko": 0.63, "base_sub": 0.11, "base_dec": 0.26, "vegas_baseline": +120,
            "wiki_title": "Alexander Volkov (fighter)",
            "trivia": "Stands 6'7\" with an extensive 48-fight international heavyweight combat record."
        },

        # --- LIGHT HEAVYWEIGHT (205 LBS) ---
        {
            "name": "Alex Pereira", "division": "Light Heavyweight", "rank": "Champion", "record": "12-2-0", "natural_weight": 205,
            "style": "Glory 2-Division Kickboxing Champion", "adaptation_archetype": "cut_relief",
            "slpm": 5.10, "str_acc": 0.62, "sapm": 3.65, "str_def": 0.51,
            "td_avg": 0.18, "td_acc": 1.00, "td_def": 0.73, "sub_avg": 0.00,
            "reach_in": 79.0, "height_in": 76.0, "age": 37, "stance": "Orthodox",
            "csac_rehydrate_pct": 0.135, "kd_per_100_str": 3.4, "pedigree_tier": 1.9, "cardio_tier": 1.45,
            "base_ko": 0.85, "base_sub": 0.00, "base_dec": 0.15, "vegas_baseline": -140,
            "wiki_title": "Alex Pereira",
            "trivia": "Holds an 85% KO finish rate in UFC title bouts with signature left-hook torque."
        },
        {
            "name": "Magomed Ankalaev", "division": "Light Heavyweight", "rank": "#1 Contender", "record": "19-1-1", "natural_weight": 205,
            "style": "Master of Sport Combat Sambo / Counter Striking", "adaptation_archetype": "natural_frame",
            "slpm": 3.64, "str_acc": 0.52, "sapm": 2.24, "str_def": 0.58,
            "td_avg": 1.02, "td_acc": 0.31, "td_def": 0.86, "sub_avg": 0.10,
            "reach_in": 75.0, "height_in": 75.0, "age": 32, "stance": "Southpaw",
            "csac_rehydrate_pct": 0.125, "kd_per_100_str": 1.5, "pedigree_tier": 1.8, "cardio_tier": 1.80,
            "base_ko": 0.53, "base_sub": 0.00, "base_dec": 0.47, "vegas_baseline": -125,
            "wiki_title": "Magomed Ankalaev",
            "trivia": "Maintains an 86% takedown defense rate alongside a 12-fight promotional unbeaten run."
        },
        {
            "name": "Jiri Prochazka", "division": "Light Heavyweight", "rank": "#2 Contender", "record": "30-5-1", "natural_weight": 205,
            "style": "Bushido Chaos Striking / High-Variance Power", "adaptation_archetype": "natural_frame",
            "slpm": 5.75, "str_acc": 0.55, "sapm": 5.43, "str_def": 0.40,
            "td_avg": 0.68, "td_acc": 0.60, "td_def": 0.68, "sub_avg": 0.30,
            "reach_in": 80.0, "height_in": 75.0, "age": 32, "stance": "Orthodox",
            "csac_rehydrate_pct": 0.130, "kd_per_100_str": 2.2, "pedigree_tier": 1.3, "cardio_tier": 1.85,
            "base_ko": 0.83, "base_sub": 0.10, "base_dec": 0.07, "vegas_baseline": +110,
            "wiki_title": "Jiří Procházka",
            "trivia": "Has finished 29 of his 30 career wins inside the distance."
        },
        {
            "name": "Jan Blachowicz", "division": "Light Heavyweight", "rank": "#4 Contender", "record": "29-10-1", "natural_weight": 205,
            "style": "Legendary Polish Power / Muay Thai & BJJ Black Belt", "adaptation_archetype": "natural_frame",
            "slpm": 3.41, "str_acc": 0.49, "sapm": 2.81, "str_def": 0.54,
            "td_avg": 0.97, "td_acc": 0.53, "td_def": 0.68, "sub_avg": 0.20,
            "reach_in": 78.0, "height_in": 74.0, "age": 42, "stance": "Orthodox",
            "csac_rehydrate_pct": 0.135, "kd_per_100_str": 1.3, "pedigree_tier": 1.4, "cardio_tier": 1.70,
            "base_ko": 0.31, "base_sub": 0.31, "base_dec": 0.38, "vegas_baseline": +145,
            "wiki_title": "Jan Błachowicz",
            "trivia": "Handed Israel Adesanya his first career defeat using heavy top control wrestling."
        },

        # --- MIDDLEWEIGHT (185 LBS) ---
        {
            "name": "Dricus Du Plessis", "division": "Middleweight", "rank": "Champion", "record": "22-2-0", "natural_weight": 185,
            "style": "Awkward Pressure Kickboxing / Judo Black Belt", "adaptation_archetype": "natural_frame",
            "slpm": 6.49, "str_acc": 0.55, "sapm": 4.77, "str_def": 0.55,
            "td_avg": 3.00, "td_acc": 0.50, "td_def": 0.50, "sub_avg": 1.20,
            "reach_in": 76.0, "height_in": 73.0, "age": 31, "stance": "Switch",
            "csac_rehydrate_pct": 0.140, "kd_per_100_str": 1.5, "pedigree_tier": 1.5, "cardio_tier": 1.85,
            "base_ko": 0.45, "base_sub": 0.45, "base_dec": 0.10, "vegas_baseline": -120,
            "wiki_title": "Dricus du Plessis",
            "trivia": "Finished 20 of his 22 career wins inside the distance across KO and submission methods."
        },
        {
            "name": "Khamzat Chimaev", "division": "Middleweight", "rank": "#1 Contender", "record": "14-0-0", "natural_weight": 185,
            "style": "Freestyle Wrestling 6x Swedish National Champ", "adaptation_archetype": "cut_relief",
            "slpm": 4.10, "str_acc": 0.58, "sapm": 1.15, "str_def": 0.56,
            "td_avg": 3.99, "td_acc": 0.53, "td_def": 1.00, "sub_avg": 1.50,
            "reach_in": 75.0, "height_in": 74.0, "age": 30, "stance": "Orthodox",
            "csac_rehydrate_pct": 0.135, "kd_per_100_str": 2.1, "pedigree_tier": 2.0, "cardio_tier": 1.25,
            "base_ko": 0.44, "base_sub": 0.42, "base_dec": 0.14, "vegas_baseline": -210,
            "wiki_title": "Khamzat Chimaev",
            "trivia": "Absorbed only a single strike across his first four UFC bouts combined."
        },
        {
            "name": "Sean Strickland", "division": "Middleweight", "rank": "#2 Contender", "record": "29-6-0", "natural_weight": 185,
            "style": "Philly Shell Boxing / Defensive Teep Pressure", "adaptation_archetype": "natural_frame",
            "slpm": 5.95, "str_acc": 0.41, "sapm": 4.20, "str_def": 0.62,
            "td_avg": 0.85, "td_acc": 0.64, "td_def": 0.85, "sub_avg": 0.20,
            "reach_in": 76.0, "height_in": 73.0, "age": 33, "stance": "Orthodox",
            "csac_rehydrate_pct": 0.125, "kd_per_100_str": 0.4, "pedigree_tier": 1.1, "cardio_tier": 2.00,
            "base_ko": 0.38, "base_sub": 0.14, "base_dec": 0.48, "vegas_baseline": +105,
            "wiki_title": "Sean Strickland",
            "trivia": "Lands nearly 6 significant strikes per minute with an elite 85% takedown defense rate."
        },
        {
            "name": "Israel Adesanya", "division": "Middleweight", "rank": "#3 Contender", "record": "24-4-0", "natural_weight": 185,
            "style": "Elite Kickboxing Counter Striking / Feint Master", "adaptation_archetype": "speed_preserver",
            "slpm": 3.93, "str_acc": 0.48, "sapm": 3.11, "str_def": 0.56,
            "td_avg": 0.05, "td_acc": 0.14, "td_def": 0.77, "sub_avg": 0.10,
            "reach_in": 80.0, "height_in": 76.0, "age": 35, "stance": "Switch",
            "csac_rehydrate_pct": 0.090, "kd_per_100_str": 1.8, "pedigree_tier": 1.7, "cardio_tier": 1.95,
            "base_ko": 0.67, "base_sub": 0.00, "base_dec": 0.33, "vegas_baseline": -115,
            "wiki_title": "Israel Adesanya",
            "trivia": "Holds 8 title-fight knockdowns and an 80-inch reach at Middleweight."
        },

        # --- WELTERWEIGHT (170 LBS) ---
        {
            "name": "Belal Muhammad", "division": "Welterweight", "rank": "Champion", "record": "24-3-0", "natural_weight": 170,
            "style": "High-Pressure Wrestling / Boxing", "adaptation_archetype": "natural_frame",
            "slpm": 4.55, "str_acc": 0.43, "sapm": 3.64, "str_def": 0.57,
            "td_avg": 2.20, "td_acc": 0.35, "td_def": 0.91, "sub_avg": 0.20,
            "reach_in": 72.0, "height_in": 70.0, "age": 36, "stance": "Orthodox",
            "csac_rehydrate_pct": 0.120, "kd_per_100_str": 0.4, "pedigree_tier": 1.6, "cardio_tier": 2.00,
            "base_ko": 0.20, "base_sub": 0.05, "base_dec": 0.75, "vegas_baseline": +160,
            "wiki_title": "Belal Muhammad",
            "trivia": "Mounted a 10-fight unbeaten streak utilizing continuous forward pressure."
        },
        {
            "name": "Shavkat Rakhmonov", "division": "Welterweight", "rank": "#1 Contender", "record": "18-0-0", "natural_weight": 170,
            "style": "Combat Sambo / Master of Sport", "adaptation_archetype": "natural_frame",
            "slpm": 4.38, "str_acc": 0.59, "sapm": 2.61, "str_def": 0.53,
            "td_avg": 2.91, "td_acc": 0.50, "td_def": 1.00, "sub_avg": 1.60,
            "reach_in": 77.0, "height_in": 73.0, "age": 30, "stance": "Orthodox",
            "csac_rehydrate_pct": 0.135, "kd_per_100_str": 1.8, "pedigree_tier": 1.9, "cardio_tier": 1.80,
            "base_ko": 0.44, "base_sub": 0.56, "base_dec": 0.00, "vegas_baseline": -240,
            "wiki_title": "Shavkat Rakhmonov",
            "trivia": "Maintains a 100% professional finish rate with 8 KOs and 10 submissions."
        },
        {
            "name": "Ian Machado Garry", "division": "Welterweight", "rank": "#2 Contender", "record": "15-1-0", "natural_weight": 170,
            "style": "Dynamic Muay Thai / Distance Striker", "adaptation_archetype": "speed_preserver",
            "slpm": 6.27, "str_acc": 0.55, "sapm": 3.58, "str_def": 0.53,
            "td_avg": 0.65, "td_acc": 0.50, "td_def": 0.72, "sub_avg": 0.20,
            "reach_in": 74.5, "height_in": 75.0, "age": 27, "stance": "Orthodox",
            "csac_rehydrate_pct": 0.110, "kd_per_100_str": 1.2, "pedigree_tier": 0.9, "cardio_tier": 1.80,
            "base_ko": 0.45, "base_sub": 0.08, "base_dec": 0.47, "vegas_baseline": +180,
            "wiki_title": "Ian Machado Garry",
            "trivia": "Lands 6.27 strikes per minute with a +4.5 inch height and reach frame advantage."
        },
        {
            "name": "Leon Edwards", "division": "Welterweight", "rank": "#3 Contender", "record": "22-4-0", "natural_weight": 170,
            "style": "Technical Southpaw Striking / Clinch Control", "adaptation_archetype": "natural_frame",
            "slpm": 2.75, "str_acc": 0.53, "sapm": 2.15, "str_def": 0.54,
            "td_avg": 1.24, "td_acc": 0.35, "td_def": 0.68, "sub_avg": 0.30,
            "reach_in": 74.0, "height_in": 72.0, "age": 33, "stance": "Southpaw",
            "csac_rehydrate_pct": 0.130, "kd_per_100_str": 1.1, "pedigree_tier": 1.4, "cardio_tier": 1.85,
            "base_ko": 0.32, "base_sub": 0.14, "base_dec": 0.54, "vegas_baseline": -130,
            "wiki_title": "Leon Edwards",
            "trivia": "Defended the Welterweight title twice with elite distance management."
        },

        # --- LIGHTWEIGHT (155 LBS) ---
        {
            "name": "Islam Makhachev", "division": "Lightweight", "rank": "Champion", "record": "27-1-0", "natural_weight": 155,
            "style": "Combat Sambo / Master of Sport", "adaptation_archetype": "natural_frame",
            "slpm": 2.46, "str_acc": 0.60, "sapm": 1.27, "str_def": 0.61,
            "td_avg": 3.17, "td_acc": 0.61, "td_def": 0.90, "sub_avg": 1.15,
            "reach_in": 70.0, "height_in": 70.0, "age": 33, "stance": "Southpaw",
            "csac_rehydrate_pct": 0.155, "kd_per_100_str": 0.8, "pedigree_tier": 2.0, "cardio_tier": 1.95,
            "base_ko": 0.20, "base_sub": 0.50, "base_dec": 0.30, "vegas_baseline": -220,
            "wiki_title": "Islam Makhachev",
            "trivia": "Absorbs just 1.27 significant strikes per minute in UFC Lightweight history."
        },
        {
            "name": "Arman Tsarukyan", "division": "Lightweight", "rank": "#1 Contender", "record": "22-3-0", "natural_weight": 155,
            "style": "Freestyle Wrestling / Explosive Muay Thai", "adaptation_archetype": "natural_frame",
            "slpm": 3.89, "str_acc": 0.48, "sapm": 1.93, "str_def": 0.54,
            "td_avg": 3.32, "td_acc": 0.36, "td_def": 0.75, "sub_avg": 0.40,
            "reach_in": 72.5, "height_in": 67.0, "age": 28, "stance": "Orthodox",
            "csac_rehydrate_pct": 0.150, "kd_per_100_str": 1.4, "pedigree_tier": 1.8, "cardio_tier": 1.90,
            "base_ko": 0.43, "base_sub": 0.24, "base_dec": 0.33, "vegas_baseline": +175,
            "wiki_title": "Arman Tsarukyan",
            "trivia": "Holds an elite 1.08 Ape Index for the Lightweight division."
        },
        {
            "name": "Charles Oliveira", "division": "Lightweight", "rank": "#2 Contender", "record": "34-10-0", "natural_weight": 155,
            "style": "Chute Boxe Muay Thai / 3rd Degree BJJ Black Belt", "adaptation_archetype": "cut_relief",
            "slpm": 3.54, "str_acc": 0.53, "sapm": 3.19, "str_def": 0.51,
            "td_avg": 2.38, "td_acc": 0.40, "td_def": 0.55, "sub_avg": 2.70,
            "reach_in": 74.0, "height_in": 70.0, "age": 35, "stance": "Orthodox",
            "csac_rehydrate_pct": 0.140, "kd_per_100_str": 1.8, "pedigree_tier": 2.0, "cardio_tier": 1.65,
            "base_ko": 0.28, "base_sub": 0.62, "base_dec": 0.10, "vegas_baseline": +140,
            "wiki_title": "Charles Oliveira",
            "trivia": "Holds the all-time UFC records for most finishes (20) and most submissions (16)."
        },
        {
            "name": "Justin Gaethje", "division": "Lightweight", "rank": "#3 Contender", "record": "25-5-0", "natural_weight": 155,
            "style": "D1 All-American / Violence Kickboxing", "adaptation_archetype": "natural_frame",
            "slpm": 7.03, "str_acc": 0.60, "sapm": 7.50, "str_def": 0.53,
            "td_avg": 0.13, "td_acc": 0.25, "td_def": 0.75, "sub_avg": 0.00,
            "reach_in": 70.0, "height_in": 71.0, "age": 36, "stance": "Orthodox",
            "csac_rehydrate_pct": 0.135, "kd_per_100_str": 2.3, "pedigree_tier": 1.2, "cardio_tier": 1.80,
            "base_ko": 0.76, "base_sub": 0.04, "base_dec": 0.20, "vegas_baseline": -110,
            "wiki_title": "Justin Gaethje",
            "trivia": "Maintains a 60% strike accuracy while throwing over 7 significant strikes per minute."
        },
        {
            "name": "Dustin Poirier", "division": "Lightweight", "rank": "#4 Contender", "record": "30-9-0", "natural_weight": 155,
            "style": "Boxing Shoulder Roll / BJJ Black Belt", "adaptation_archetype": "cut_relief",
            "slpm": 5.45, "str_acc": 0.51, "sapm": 4.30, "str_def": 0.53,
            "td_avg": 1.34, "td_acc": 0.36, "td_def": 0.64, "sub_avg": 1.20,
            "reach_in": 72.0, "height_in": 69.0, "age": 36, "stance": "Southpaw",
            "csac_rehydrate_pct": 0.145, "kd_per_100_str": 1.6, "pedigree_tier": 1.4, "cardio_tier": 1.85,
            "base_ko": 0.53, "base_sub": 0.27, "base_dec": 0.20, "vegas_baseline": +130,
            "wiki_title": "Dustin Poirier",
            "trivia": "Holds 15 post-fight bonuses with some of the highest power metrics in division history."
        },

        # --- FEATHERWEIGHT (145 LBS) ---
        {
            "name": "Ilia Topuria", "division": "Featherweight", "rank": "Champion", "record": "16-0-0", "natural_weight": 145,
            "style": "Greco-Roman Wrestling / Precision Boxing", "adaptation_archetype": "speed_preserver",
            "slpm": 4.54, "str_acc": 0.46, "sapm": 3.10, "str_def": 0.65,
            "td_avg": 1.92, "td_acc": 0.56, "td_def": 0.92, "sub_avg": 1.30,
            "reach_in": 69.0, "height_in": 67.0, "age": 28, "stance": "Orthodox",
            "csac_rehydrate_pct": 0.145, "kd_per_100_str": 2.6, "pedigree_tier": 1.8, "cardio_tier": 1.90,
            "base_ko": 0.55, "base_sub": 0.30, "base_dec": 0.15, "vegas_baseline": -165,
            "wiki_title": "Ilia Topuria",
            "trivia": "Possesses a 92% takedown defense rate alongside elite rotational knockout power."
        },
        {
            "name": "Alexander Volkanovski", "division": "Featherweight", "rank": "#1 Contender", "record": "26-4-0", "natural_weight": 145,
            "style": "Freestyle Wrestling / Kickboxing", "adaptation_archetype": "speed_preserver",
            "slpm": 6.19, "str_acc": 0.57, "sapm": 3.42, "str_def": 0.58,
            "td_avg": 1.84, "td_acc": 0.37, "td_def": 0.73, "sub_avg": 0.20,
            "reach_in": 71.5, "height_in": 66.0, "age": 36, "stance": "Orthodox",
            "csac_rehydrate_pct": 0.145, "kd_per_100_str": 0.9, "pedigree_tier": 1.4, "cardio_tier": 2.00,
            "base_ko": 0.42, "base_sub": 0.12, "base_dec": 0.46, "vegas_baseline": +125,
            "wiki_title": "Alexander Volkanovski",
            "trivia": "Fought at 214 lbs during his semi-pro rugby career before capturing the Featherweight belt."
        },
        {
            "name": "Max Holloway", "division": "Featherweight", "rank": "#2 Contender", "record": "26-8-0", "natural_weight": 145,
            "style": "Hawaiian Volume Boxing / BJJ Brown Belt", "adaptation_archetype": "cut_relief",
            "slpm": 7.17, "str_acc": 0.48, "sapm": 4.79, "str_def": 0.59,
            "td_avg": 0.27, "td_acc": 0.53, "td_def": 0.84, "sub_avg": 0.30,
            "reach_in": 69.0, "height_in": 71.0, "age": 32, "stance": "Orthodox",
            "csac_rehydrate_pct": 0.140, "kd_per_100_str": 0.6, "pedigree_tier": 0.8, "cardio_tier": 2.00,
            "base_ko": 0.44, "base_sub": 0.06, "base_dec": 0.50, "vegas_baseline": +135,
            "wiki_title": "Max Holloway",
            "trivia": "Holds the UFC all-time record for total significant strikes landed with over 3,300."
        },
        {
            "name": "Diego Lopes", "division": "Featherweight", "rank": "#3 Contender", "record": "26-6-0", "natural_weight": 145,
            "style": "Explosive BJJ Black Belt / Power Hook Striking", "adaptation_archetype": "natural_frame",
            "slpm": 3.34, "str_acc": 0.53, "sapm": 3.91, "str_def": 0.42,
            "td_avg": 0.72, "td_acc": 0.45, "td_def": 0.50, "sub_avg": 3.80,
            "reach_in": 72.5, "height_in": 71.0, "age": 30, "stance": "Orthodox",
            "csac_rehydrate_pct": 0.145, "kd_per_100_str": 2.1, "pedigree_tier": 1.8, "cardio_tier": 1.80,
            "base_ko": 0.46, "base_sub": 0.46, "base_dec": 0.08, "vegas_baseline": -120,
            "wiki_title": "Diego Lopes (fighter)",
            "trivia": "Averages an incredible 3.8 submission attempts per 15 minutes of fight time."
        },

        # --- BANTAMWEIGHT (135 LBS) ---
        {
            "name": "Merab Dvalishvili", "division": "Bantamweight", "rank": "Champion", "record": "18-4-0", "natural_weight": 135,
            "style": "Sambo / High-Pace Relentless Wrestling", "adaptation_archetype": "natural_frame",
            "slpm": 4.50, "str_acc": 0.42, "sapm": 2.40, "str_def": 0.62,
            "td_avg": 6.43, "td_acc": 0.36, "td_def": 0.80, "sub_avg": 0.30,
            "reach_in": 68.0, "height_in": 66.0, "age": 34, "stance": "Orthodox",
            "csac_rehydrate_pct": 0.155, "kd_per_100_str": 0.3, "pedigree_tier": 1.9, "cardio_tier": 2.00,
            "base_ko": 0.18, "base_sub": 0.08, "base_dec": 0.74, "vegas_baseline": -190,
            "wiki_title": "Merab Dvalishvili",
            "trivia": "Attempted an all-time record 49 takedowns in 25 minutes against Petr Yan."
        },
        {
            "name": "Sean O'Malley", "division": "Bantamweight", "rank": "#1 Contender", "record": "18-2-0", "natural_weight": 135,
            "style": "Feint-Heavy Counter Sniping Boxing", "adaptation_archetype": "speed_preserver",
            "slpm": 7.25, "str_acc": 0.61, "sapm": 3.52, "str_def": 0.62,
            "td_avg": 0.35, "td_acc": 0.42, "td_def": 0.65, "sub_avg": 0.40,
            "reach_in": 72.0, "height_in": 71.0, "age": 30, "stance": "Switch",
            "csac_rehydrate_pct": 0.140, "kd_per_100_str": 1.9, "pedigree_tier": 0.9, "cardio_tier": 1.85,
            "base_ko": 0.68, "base_sub": 0.05, "base_dec": 0.27, "vegas_baseline": +155,
            "wiki_title": "Sean O'Malley (fighter)",
            "trivia": "Maintains a 61% striking accuracy—ranking in the 99th percentile across UFC Bantamweight history."
        },
        {
            "name": "Umar Nurmagomedov", "division": "Bantamweight", "rank": "#2 Contender", "record": "18-0-0", "natural_weight": 135,
            "style": "Dagestani Combat Sambo / Kicking Arsenal", "adaptation_archetype": "natural_frame",
            "slpm": 4.75, "str_acc": 0.69, "sapm": 0.85, "str_def": 0.68,
            "td_avg": 4.25, "td_acc": 0.52, "td_def": 1.00, "sub_avg": 0.90,
            "reach_in": 69.0, "height_in": 68.0, "age": 29, "stance": "Southpaw",
            "csac_rehydrate_pct": 0.145, "kd_per_100_str": 0.9, "pedigree_tier": 2.0, "cardio_tier": 1.95,
            "base_ko": 0.22, "base_sub": 0.39, "base_dec": 0.39, "vegas_baseline": -230,
            "wiki_title": "Umar Nurmagomedov",
            "trivia": "Absorbs less than 1.0 significant strike per minute with a 100% takedown defense record."
        },
        {
            "name": "Petr Yan", "division": "Bantamweight", "rank": "#3 Contender", "record": "17-5-0", "natural_weight": 135,
            "style": "Master of Sport Boxing / High-Guard Pressure", "adaptation_archetype": "natural_frame",
            "slpm": 5.11, "str_acc": 0.54, "sapm": 4.02, "str_def": 0.59,
            "td_avg": 1.71, "td_acc": 0.52, "td_def": 0.85, "sub_avg": 0.20,
            "reach_in": 67.0, "height_in": 67.0, "age": 32, "stance": "Switch",
            "csac_rehydrate_pct": 0.140, "kd_per_100_str": 1.4, "pedigree_tier": 1.6, "cardio_tier": 1.95,
            "base_ko": 0.41, "base_sub": 0.06, "base_dec": 0.53, "vegas_baseline": -125,
            "wiki_title": "Petr Yan",
            "trivia": "Maintains an 85% takedown defense while switching stances with elite boxing combinations."
        },

        # --- FLYWEIGHT (125 LBS) ---
        {
            "name": "Alexandre Pantoja", "division": "Flyweight", "rank": "Champion", "record": "28-5-0", "natural_weight": 125,
            "style": "Aggressive BJJ Black Belt / Muay Thai Brawl", "adaptation_archetype": "natural_frame",
            "slpm": 4.41, "str_acc": 0.49, "sapm": 3.75, "str_def": 0.53,
            "td_avg": 2.65, "td_acc": 0.45, "td_def": 0.67, "sub_avg": 1.20,
            "reach_in": 67.0, "height_in": 65.0, "age": 34, "stance": "Orthodox",
            "csac_rehydrate_pct": 0.150, "kd_per_100_str": 0.9, "pedigree_tier": 1.8, "cardio_tier": 1.95,
            "base_ko": 0.32, "base_sub": 0.39, "base_dec": 0.29, "vegas_baseline": -180,
            "wiki_title": "Alexandre Pantoja",
            "trivia": "Has executed 11 submission victories across elite competition at 125 lbs."
        },
        {
            "name": "Brandon Royval", "division": "Flyweight", "rank": "#1 Contender", "record": "17-7-0", "natural_weight": 125,
            "style": "High-Chaos Scramble Grappling / Volume Boxing", "adaptation_archetype": "speed_preserver",
            "slpm": 3.90, "str_acc": 0.43, "sapm": 3.35, "str_def": 0.51,
            "td_avg": 0.70, "td_acc": 1.00, "td_def": 0.65, "sub_avg": 1.70,
            "reach_in": 70.0, "height_in": 67.0, "age": 32, "stance": "Southpaw",
            "csac_rehydrate_pct": 0.135, "kd_per_100_str": 1.4, "pedigree_tier": 1.3, "cardio_tier": 1.90,
            "base_ko": 0.29, "base_sub": 0.53, "base_dec": 0.18, "vegas_baseline": +150,
            "wiki_title": "Brandon Royval",
            "trivia": "Maintains an exceptionally high submission attempt rate of 1.7 per 15 minutes."
        },
        {
            "name": "Brandon Moreno", "division": "Flyweight", "rank": "#2 Contender", "record": "21-8-2", "natural_weight": 125,
            "style": "Technical Mexican Boxing / Scramble BJJ", "adaptation_archetype": "natural_frame",
            "slpm": 3.80, "str_acc": 0.43, "sapm": 3.40, "str_def": 0.56,
            "td_avg": 1.73, "td_acc": 0.45, "td_def": 0.65, "sub_avg": 0.60,
            "reach_in": 70.0, "height_in": 67.0, "age": 31, "stance": "Orthodox",
            "csac_rehydrate_pct": 0.140, "kd_per_100_str": 0.7, "pedigree_tier": 1.5, "cardio_tier": 1.95,
            "base_ko": 0.24, "base_sub": 0.52, "base_dec": 0.24, "vegas_baseline": -135,
            "wiki_title": "Brandon Moreno",
            "trivia": "First Mexican-born champion in UFC history with two undisputed title reigns."
        }
    ]
    
    df = pd.DataFrame(fighters)
    df["slug"] = df["name"].apply(generate_slug)
    
    print("📥 Ingesting fighter assets into assets/fighters/...")
    df["local_image_path"] = df.apply(
        lambda r: resolve_and_save_asset(r["name"], r["wiki_title"], r["slug"]), 
        axis=1
    )
    
    parquet_path = DATA_DIR / "fighters_master.parquet"
    df.to_parquet(parquet_path, engine="pyarrow", index=False)
    print(f"\n✨ System synchronized successfully: {len(df)} UFC contenders saved to {parquet_path}\n")

if __name__ == "__main__":
    build_roster_database()