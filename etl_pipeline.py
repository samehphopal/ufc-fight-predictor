import re
import time
import unicodedata
from pathlib import Path
import pandas as pd
import requests

ASSET_DIR = Path("assets/fighters")
DATA_DIR = Path("data")
ASSET_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
})

def to_slug(name: str, sep: str = "-") -> str:
    clean = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii").replace("'", "")
    return re.sub(r"[^a-z0-9]+", sep, clean.lower()).strip(sep)

def resolve_and_save_asset(name: str) -> str:
    file_slug = to_slug(name, "_")
    url_slug = to_slug(name, "-")
    local_file = ASSET_DIR / f"{file_slug}.png"

    # Keep valid existing UFC cutouts (> 1KB) without re-downloading
    if local_file.exists() and local_file.stat().st_size > 1000:
        return f"assets/fighters/{file_slug}.png"

    # Try standard slug and fallback slug variations for special names
    slug_candidates = [url_slug]
    if "o-malley" in name.lower() or "omalley" in name.lower():
        slug_candidates.extend(["sean-omalley", "sean-o-malley"])

    for candidate in dict.fromkeys(slug_candidates):
        try:
            url = f"https://www.ufc.com/athlete/{candidate}"
            resp = SESSION.get(url, timeout=10)
            if resp.status_code == 200:
                match = re.search(
                    r'((?:https://[^"\'\s]+)?/images/styles/(?:teaser|event_results_athlete_headshot|athlete_bio_full_body)/[^"\'\s]+\.(?:png|webp|jpg))',
                    resp.text
                )
                if match:
                    img_url = match.group(1)
                    if img_url.startswith("/"):
                        img_url = "https://www.ufc.com" + img_url
                    img_resp = SESSION.get(img_url, timeout=10)
                    if img_resp.status_code == 200 and len(img_resp.content) > 1000:
                        local_file.write_bytes(img_resp.content)
                        print(f"  [SAVED] {file_slug}.png")
                        time.sleep(0.25)
                        return f"assets/fighters/{file_slug}.png"
        except Exception:
            pass

    print(f"  [BADGE FALLBACK] {name}")
    return ""

def build_roster_database():
    print("Compiling 64-Fighter Contenders Dataset & Syncing UFC Cutouts...\n")

    fighters = [
        # --- HEAVYWEIGHT (265 LBS) ---
        {
            "name": "Ciryl Gane", "division": "Heavyweight", "rank": "Champion", "record": "15-2-1", "natural_weight": 265,
            "style": "Technical Muay Thai / Distance Movement", "adaptation_archetype": "speed_preserver",
            "slpm": 5.38, "str_acc": 0.61, "sapm": 2.30, "str_def": 0.62,
            "td_avg": 0.58, "td_acc": 0.21, "td_def": 0.60, "sub_avg": 0.40,
            "reach_in": 81.0, "height_in": 76.0, "age": 36, "stance": "Orthodox",
            "csac_rehydrate_pct": 0.000, "kd_per_100_str": 1.1, "pedigree_tier": 1.4, "cardio_tier": 1.95,
            "base_ko": 0.47, "base_sub": 0.20, "base_dec": 0.33, "vegas_baseline": -175,
            "trivia": "Maintains a +3.08 significant strike differential per minute at Heavyweight."
        },
        {
            "name": "Tom Aspinall", "division": "Heavyweight", "rank": "#1 Contender", "record": "15-3-0", "natural_weight": 265,
            "style": "Heavyweight Boxing / BJJ Black Belt", "adaptation_archetype": "natural_frame",
            "slpm": 7.72, "str_acc": 0.66, "sapm": 2.77, "str_def": 0.67,
            "td_avg": 3.38, "td_acc": 1.00, "td_def": 1.00, "sub_avg": 1.70,
            "reach_in": 78.0, "height_in": 77.0, "age": 33, "stance": "Orthodox",
            "csac_rehydrate_pct": 0.000, "kd_per_100_str": 3.8, "pedigree_tier": 1.8, "cardio_tier": 1.75,
            "base_ko": 0.75, "base_sub": 0.20, "base_dec": 0.05, "vegas_baseline": -220,
            "trivia": "Averages the shortest average fight time in UFC history at 2 minutes and 2 seconds."
        },
        {
            "name": "Alexander Volkov", "division": "Heavyweight", "rank": "#2 Contender", "record": "41-11-0", "natural_weight": 265,
            "style": "Tsu Shin Gen Karate / Long-Range Kickboxing", "adaptation_archetype": "natural_frame",
            "slpm": 5.15, "str_acc": 0.57, "sapm": 3.05, "str_def": 0.54,
            "td_avg": 0.52, "td_acc": 0.66, "td_def": 0.73, "sub_avg": 0.20,
            "reach_in": 80.0, "height_in": 79.0, "age": 38, "stance": "Orthodox",
            "csac_rehydrate_pct": 0.000, "kd_per_100_str": 1.0, "pedigree_tier": 1.3, "cardio_tier": 1.80,
            "base_ko": 0.61, "base_sub": 0.10, "base_dec": 0.29, "vegas_baseline": +125,
            "trivia": "Stands 6'7\" with over 50 professional heavyweight bouts."
        },
        {
            "name": "Sergei Pavlovich", "division": "Heavyweight", "rank": "#4 Contender", "record": "21-3-0", "natural_weight": 265,
            "style": "Greco-Roman Wrestling / Heavy Boxing", "adaptation_archetype": "natural_frame",
            "slpm": 6.45, "str_acc": 0.49, "sapm": 4.12, "str_def": 0.52,
            "td_avg": 0.20, "td_acc": 0.33, "td_def": 0.75, "sub_avg": 0.00,
            "reach_in": 84.0, "height_in": 75.0, "age": 34, "stance": "Southpaw",
            "csac_rehydrate_pct": 0.000, "kd_per_100_str": 3.5, "pedigree_tier": 1.4, "cardio_tier": 1.45,
            "base_ko": 0.86, "base_sub": 0.00, "base_dec": 0.14, "vegas_baseline": -135,
            "trivia": "Carries an 84-inch wingspan on a 6'3\" frame for a 1.12 Ape Index."
        },
        {
            "name": "Josh Hokit", "division": "Heavyweight", "rank": "#5 Contender", "record": "10-1-0", "natural_weight": 265,
            "style": "Collegiate Wrestling / Ground & Pound", "adaptation_archetype": "natural_frame",
            "slpm": 4.20, "str_acc": 0.52, "sapm": 3.40, "str_def": 0.51,
            "td_avg": 3.10, "td_acc": 0.44, "td_def": 0.72, "sub_avg": 0.30,
            "reach_in": 73.0, "height_in": 73.0, "age": 29, "stance": "Orthodox",
            "csac_rehydrate_pct": 0.000, "kd_per_100_str": 1.3, "pedigree_tier": 1.5, "cardio_tier": 1.85,
            "base_ko": 0.50, "base_sub": 0.10, "base_dec": 0.40, "vegas_baseline": +165,
            "trivia": "Former NCAA Division I wrestler at Fresno State who pushed Ciryl Gane five rounds."
        },
        {
            "name": "Curtis Blaydes", "division": "Heavyweight", "rank": "#7 Contender", "record": "20-6-0", "natural_weight": 265,
            "style": "NJCAA Wrestling / Top-Control Ground & Pound", "adaptation_archetype": "natural_frame",
            "slpm": 3.55, "str_acc": 0.50, "sapm": 2.15, "str_def": 0.58,
            "td_avg": 5.85, "td_acc": 0.53, "td_def": 0.35, "sub_avg": 0.00,
            "reach_in": 80.0, "height_in": 76.0, "age": 35, "stance": "Orthodox",
            "csac_rehydrate_pct": 0.000, "kd_per_100_str": 1.2, "pedigree_tier": 1.8, "cardio_tier": 1.75,
            "base_ko": 0.65, "base_sub": 0.00, "base_dec": 0.35, "vegas_baseline": -145,
            "trivia": "Holds the UFC Heavyweight all-time record for most career takedowns landed."
        },
        {
            "name": "Johnny Walker", "division": "Heavyweight", "rank": "#8 Contender", "record": "24-10-0", "natural_weight": 265,
            "style": "Explosive Muay Thai / Athletic Frame", "adaptation_archetype": "cut_relief",
            "slpm": 3.85, "str_acc": 0.54, "sapm": 3.10, "str_def": 0.45,
            "td_avg": 0.45, "td_acc": 0.60, "td_def": 0.58, "sub_avg": 0.50,
            "reach_in": 82.0, "height_in": 78.0, "age": 34, "stance": "Orthodox",
            "csac_rehydrate_pct": 0.000, "kd_per_100_str": 2.4, "pedigree_tier": 1.1, "cardio_tier": 1.50,
            "base_ko": 0.75, "base_sub": 0.13, "base_dec": 0.12, "vegas_baseline": +130,
            "trivia": "Transitioned up to Heavyweight with an 82-inch reach and high-variance knockout power."
        },
        {
            "name": "Jon Jones", "division": "Heavyweight", "rank": "Legacy #1", "record": "28-1-0", "natural_weight": 265,
            "style": "Greco-Roman Wrestling / Gaidojutsu", "adaptation_archetype": "natural_frame",
            "slpm": 4.30, "str_acc": 0.58, "sapm": 2.22, "str_def": 0.64,
            "td_avg": 1.85, "td_acc": 0.45, "td_def": 0.95, "sub_avg": 0.80,
            "reach_in": 84.5, "height_in": 76.0, "age": 39, "stance": "Orthodox",
            "csac_rehydrate_pct": 0.000, "kd_per_100_str": 1.4, "pedigree_tier": 2.0, "cardio_tier": 1.85,
            "base_ko": 0.38, "base_sub": 0.28, "base_dec": 0.34, "vegas_baseline": -260,
            "trivia": "Holds an 84.5-inch reach—the longest wingspan in UFC championship history."
        },

        # --- LIGHT HEAVYWEIGHT (205 LBS) ---
        {
            "name": "Carlos Ulberg", "division": "Light Heavyweight", "rank": "Champion", "record": "15-1-0", "natural_weight": 205,
            "style": "City Kickboxing Precision / Counter Left Hook", "adaptation_archetype": "natural_frame",
            "slpm": 6.85, "str_acc": 0.57, "sapm": 3.45, "str_def": 0.54,
            "td_avg": 0.55, "td_acc": 0.65, "td_def": 0.82, "sub_avg": 0.10,
            "reach_in": 77.0, "height_in": 76.0, "age": 35, "stance": "Orthodox",
            "csac_rehydrate_pct": 0.130, "kd_per_100_str": 2.5, "pedigree_tier": 1.6, "cardio_tier": 1.85,
            "base_ko": 0.67, "base_sub": 0.07, "base_dec": 0.26, "vegas_baseline": -155,
            "trivia": "Captured the 205-lb belt on a 10-fight winning streak out of City Kickboxing."
        },
        {
            "name": "Alex Pereira", "division": "Light Heavyweight", "rank": "#1 Contender", "record": "13-4-0", "natural_weight": 205,
            "style": "Glory 2-Division Kickboxing Champion", "adaptation_archetype": "cut_relief",
            "slpm": 5.10, "str_acc": 0.62, "sapm": 3.65, "str_def": 0.51,
            "td_avg": 0.18, "td_acc": 1.00, "td_def": 0.73, "sub_avg": 0.00,
            "reach_in": 79.0, "height_in": 76.0, "age": 39, "stance": "Orthodox",
            "csac_rehydrate_pct": 0.135, "kd_per_100_str": 3.4, "pedigree_tier": 1.9, "cardio_tier": 1.45,
            "base_ko": 0.85, "base_sub": 0.00, "base_dec": 0.15, "vegas_baseline": -140,
            "trivia": "Former two-division UFC champion with signature left-hook knockout torque."
        },
        {
            "name": "Magomed Ankalaev", "division": "Light Heavyweight", "rank": "#2 Contender", "record": "20-1-1", "natural_weight": 205,
            "style": "Master of Sport Combat Sambo / Counter Striking", "adaptation_archetype": "natural_frame",
            "slpm": 3.64, "str_acc": 0.52, "sapm": 2.24, "str_def": 0.58,
            "td_avg": 1.02, "td_acc": 0.31, "td_def": 0.86, "sub_avg": 0.10,
            "reach_in": 75.0, "height_in": 75.0, "age": 34, "stance": "Southpaw",
            "csac_rehydrate_pct": 0.125, "kd_per_100_str": 1.5, "pedigree_tier": 1.8, "cardio_tier": 1.80,
            "base_ko": 0.53, "base_sub": 0.00, "base_dec": 0.47, "vegas_baseline": -130,
            "trivia": "Maintains an 86% takedown defense rate alongside elite counter-left accuracy."
        },
        {
            "name": "Jiri Prochazka", "division": "Light Heavyweight", "rank": "#3 Contender", "record": "31-5-1", "natural_weight": 205,
            "style": "Bushido Chaos Striking / High-Variance Power", "adaptation_archetype": "natural_frame",
            "slpm": 5.75, "str_acc": 0.55, "sapm": 5.43, "str_def": 0.40,
            "td_avg": 0.68, "td_acc": 0.60, "td_def": 0.68, "sub_avg": 0.30,
            "reach_in": 80.0, "height_in": 75.0, "age": 34, "stance": "Orthodox",
            "csac_rehydrate_pct": 0.130, "kd_per_100_str": 2.2, "pedigree_tier": 1.3, "cardio_tier": 1.85,
            "base_ko": 0.83, "base_sub": 0.10, "base_dec": 0.07, "vegas_baseline": +110,
            "trivia": "Has finished 30 of his 31 career wins inside the distance."
        },
        {
            "name": "Dominick Reyes", "division": "Light Heavyweight", "rank": "#4 Contender", "record": "15-4-0", "natural_weight": 205,
            "style": "Athletic Southpaw Counter Left / Kickboxing", "adaptation_archetype": "natural_frame",
            "slpm": 4.95, "str_acc": 0.50, "sapm": 3.45, "str_def": 0.49,
            "td_avg": 0.35, "td_acc": 0.25, "td_def": 0.80, "sub_avg": 0.20,
            "reach_in": 77.0, "height_in": 76.0, "age": 36, "stance": "Southpaw",
            "csac_rehydrate_pct": 0.125, "kd_per_100_str": 1.8, "pedigree_tier": 1.3, "cardio_tier": 1.65,
            "base_ko": 0.67, "base_sub": 0.13, "base_dec": 0.20, "vegas_baseline": +135,
            "trivia": "Rebounded into the Top 5 with consecutive first-round knockout finishes."
        },
        {
            "name": "Khalil Rountree Jr.", "division": "Light Heavyweight", "rank": "#6 Contender", "record": "14-6-0", "natural_weight": 205,
            "style": "Bangkok Ready Muay Thai / Explosive Southpaw", "adaptation_archetype": "natural_frame",
            "slpm": 3.88, "str_acc": 0.40, "sapm": 4.15, "str_def": 0.50,
            "td_avg": 0.00, "td_acc": 0.00, "td_def": 0.58, "sub_avg": 0.10,
            "reach_in": 76.5, "height_in": 73.0, "age": 36, "stance": "Southpaw",
            "csac_rehydrate_pct": 0.130, "kd_per_100_str": 2.4, "pedigree_tier": 1.2, "cardio_tier": 1.60,
            "base_ko": 0.71, "base_sub": 0.00, "base_dec": 0.29, "vegas_baseline": +120,
            "trivia": "Has zero career UFC takedown attempts—100% committed to violent stand-up pressure."
        },
        {
            "name": "Reinier de Ridder", "division": "Light Heavyweight", "rank": "#8 Contender", "record": "19-2-0", "natural_weight": 205,
            "style": "Judo & BJJ Black Belt / Long-Frame Chain Grappling", "adaptation_archetype": "cut_relief",
            "slpm": 3.15, "str_acc": 0.51, "sapm": 2.65, "str_def": 0.52,
            "td_avg": 3.65, "td_acc": 0.48, "td_def": 0.65, "sub_avg": 2.30,
            "reach_in": 78.0, "height_in": 76.0, "age": 36, "stance": "Southpaw",
            "csac_rehydrate_pct": 0.125, "kd_per_100_str": 0.7, "pedigree_tier": 1.8, "cardio_tier": 1.75,
            "base_ko": 0.21, "base_sub": 0.63, "base_dec": 0.16, "vegas_baseline": +115,
            "trivia": "Former simultaneous two-division ONE Championship titleholder."
        },
        {
            "name": "Jan Blachowicz", "division": "Light Heavyweight", "rank": "#9 Contender", "record": "29-11-1", "natural_weight": 205,
            "style": "Legendary Polish Power / Muay Thai & BJJ Black Belt", "adaptation_archetype": "natural_frame",
            "slpm": 3.41, "str_acc": 0.49, "sapm": 2.81, "str_def": 0.54,
            "td_avg": 0.97, "td_acc": 0.53, "td_def": 0.68, "sub_avg": 0.20,
            "reach_in": 78.0, "height_in": 74.0, "age": 43, "stance": "Orthodox",
            "csac_rehydrate_pct": 0.135, "kd_per_100_str": 1.3, "pedigree_tier": 1.4, "cardio_tier": 1.70,
            "base_ko": 0.31, "base_sub": 0.31, "base_dec": 0.38, "vegas_baseline": +150,
            "trivia": "Former UFC Light Heavyweight champion with heavy body kicks and top control."
        },

        # --- MIDDLEWEIGHT (185 LBS) ---
        {
            "name": "Sean Strickland", "division": "Middleweight", "rank": "Champion", "record": "31-7-0", "natural_weight": 185,
            "style": "Philly Shell Boxing / Defensive Teep Pressure", "adaptation_archetype": "natural_frame",
            "slpm": 6.02, "str_acc": 0.41, "sapm": 4.15, "str_def": 0.63,
            "td_avg": 0.82, "td_acc": 0.64, "td_def": 0.85, "sub_avg": 0.20,
            "reach_in": 76.0, "height_in": 73.0, "age": 35, "stance": "Orthodox",
            "csac_rehydrate_pct": 0.125, "kd_per_100_str": 0.5, "pedigree_tier": 1.3, "cardio_tier": 2.00,
            "base_ko": 0.35, "base_sub": 0.13, "base_dec": 0.52, "vegas_baseline": -115,
            "trivia": "Reclaimed the 185-lb belt behind an elite 85% takedown defense and relentless jab output."
        },
        {
            "name": "Khamzat Chimaev", "division": "Middleweight", "rank": "#1 Contender", "record": "15-1-0", "natural_weight": 185,
            "style": "Freestyle Wrestling 6x Swedish National Champ", "adaptation_archetype": "cut_relief",
            "slpm": 4.15, "str_acc": 0.56, "sapm": 1.55, "str_def": 0.56,
            "td_avg": 4.10, "td_acc": 0.55, "td_def": 1.00, "sub_avg": 1.40,
            "reach_in": 75.0, "height_in": 74.0, "age": 32, "stance": "Orthodox",
            "csac_rehydrate_pct": 0.135, "kd_per_100_str": 2.0, "pedigree_tier": 2.0, "cardio_tier": 1.35,
            "base_ko": 0.40, "base_sub": 0.40, "base_dec": 0.20, "vegas_baseline": -200,
            "trivia": "Holds a 100% career takedown defense rate with explosive opening-round chain wrestling."
        },
        {
            "name": "Dricus Du Plessis", "division": "Middleweight", "rank": "#2 Contender", "record": "24-3-0", "natural_weight": 185,
            "style": "Awkward Pressure Kickboxing / Judo Black Belt", "adaptation_archetype": "natural_frame",
            "slpm": 6.45, "str_acc": 0.54, "sapm": 4.72, "str_def": 0.55,
            "td_avg": 2.85, "td_acc": 0.50, "td_def": 0.52, "sub_avg": 1.15,
            "reach_in": 76.0, "height_in": 73.0, "age": 32, "stance": "Switch",
            "csac_rehydrate_pct": 0.140, "kd_per_100_str": 1.5, "pedigree_tier": 1.5, "cardio_tier": 1.85,
            "base_ko": 0.42, "base_sub": 0.42, "base_dec": 0.16, "vegas_baseline": -125,
            "trivia": "Finished 20 of his 24 career victories inside the distance across KOs and submissions."
        },
        {
            "name": "Nassourdine Imavov", "division": "Middleweight", "rank": "#3 Contender", "record": "17-4-0", "natural_weight": 185,
            "style": "Technical French Boxing / Clinch Knees", "adaptation_archetype": "natural_frame",
            "slpm": 4.65, "str_acc": 0.54, "sapm": 3.25, "str_def": 0.59,
            "td_avg": 1.05, "td_acc": 0.38, "td_def": 0.78, "sub_avg": 0.90,
            "reach_in": 75.0, "height_in": 75.0, "age": 30, "stance": "Orthodox",
            "csac_rehydrate_pct": 0.125, "kd_per_100_str": 1.2, "pedigree_tier": 1.4, "cardio_tier": 1.85,
            "base_ko": 0.41, "base_sub": 0.24, "base_dec": 0.35, "vegas_baseline": -130,
            "trivia": "Outstruck Caio Borralho across five rounds in Paris to cement Top-3 contender status."
        },
        {
            "name": "Brendan Allen", "division": "Middleweight", "rank": "#4 Contender", "record": "28-7-0", "natural_weight": 185,
            "style": "Aggressive BJJ Black Belt / Back-Take Specialist", "adaptation_archetype": "natural_frame",
            "slpm": 4.10, "str_acc": 0.53, "sapm": 3.65, "str_def": 0.48,
            "td_avg": 1.85, "td_acc": 0.44, "td_def": 0.58, "sub_avg": 1.80,
            "reach_in": 75.0, "height_in": 74.0, "age": 30, "stance": "Orthodox",
            "csac_rehydrate_pct": 0.130, "kd_per_100_str": 0.8, "pedigree_tier": 1.6, "cardio_tier": 1.80,
            "base_ko": 0.18, "base_sub": 0.54, "base_dec": 0.28, "vegas_baseline": +115,
            "trivia": "Owns 15 career submission wins, specializing in rear-naked chokes in scrambles."
        },
        {
            "name": "Caio Borralho", "division": "Middleweight", "rank": "#5 Contender", "record": "19-2-0", "natural_weight": 185,
            "style": "Fighting Nerds Tactical Southpaw / BJJ Black Belt", "adaptation_archetype": "natural_frame",
            "slpm": 3.85, "str_acc": 0.57, "sapm": 2.45, "str_def": 0.60,
            "td_avg": 1.75, "td_acc": 0.56, "td_def": 0.76, "sub_avg": 0.60,
            "reach_in": 75.0, "height_in": 73.0, "age": 33, "stance": "Southpaw",
            "csac_rehydrate_pct": 0.125, "kd_per_100_str": 1.0, "pedigree_tier": 1.6, "cardio_tier": 1.90,
            "base_ko": 0.26, "base_sub": 0.21, "base_dec": 0.53, "vegas_baseline": -120,
            "trivia": "Maintains a 57% significant strike accuracy with high positional control discipline."
        },
        {
            "name": "Robert Whittaker", "division": "Middleweight", "rank": "#6 Contender", "record": "26-8-0", "natural_weight": 185,
            "style": "Shotokan Karate Blitz / Freestyle Wrestling", "adaptation_archetype": "natural_frame",
            "slpm": 4.58, "str_acc": 0.43, "sapm": 3.44, "str_def": 0.60,
            "td_avg": 0.85, "td_acc": 0.38, "td_def": 0.82, "sub_avg": 0.10,
            "reach_in": 73.5, "height_in": 72.0, "age": 35, "stance": "Orthodox",
            "csac_rehydrate_pct": 0.125, "kd_per_100_str": 1.3, "pedigree_tier": 1.6, "cardio_tier": 1.85,
            "base_ko": 0.38, "base_sub": 0.19, "base_dec": 0.43, "vegas_baseline": -110,
            "trivia": "Former UFC Middleweight champion known for explosive 1-2 high-kick combinations."
        },
        {
            "name": "Israel Adesanya", "division": "Middleweight", "rank": "#7 Contender", "record": "24-5-0", "natural_weight": 185,
            "style": "Elite Kickboxing Counter Striking / Feint Master", "adaptation_archetype": "speed_preserver",
            "slpm": 3.93, "str_acc": 0.48, "sapm": 3.11, "str_def": 0.56,
            "td_avg": 0.05, "td_acc": 0.14, "td_def": 0.77, "sub_avg": 0.10,
            "reach_in": 80.0, "height_in": 76.0, "age": 37, "stance": "Switch",
            "csac_rehydrate_pct": 0.090, "kd_per_100_str": 1.8, "pedigree_tier": 1.7, "cardio_tier": 1.95,
            "base_ko": 0.67, "base_sub": 0.00, "base_dec": 0.33, "vegas_baseline": -115,
            "trivia": "Two-time Middleweight champion with an 80-inch reach and elite distance control."
        },

        # --- WELTERWEIGHT (170 LBS) ---
        {
            "name": "Islam Makhachev", "division": "Welterweight", "rank": "Champion", "record": "29-1-0", "natural_weight": 170,
            "style": "Combat Sambo / Master of Sport", "adaptation_archetype": "cut_relief",
            "slpm": 2.55, "str_acc": 0.60, "sapm": 1.30, "str_def": 0.62,
            "td_avg": 3.25, "td_acc": 0.61, "td_def": 0.90, "sub_avg": 1.15,
            "reach_in": 70.5, "height_in": 70.0, "age": 35, "stance": "Southpaw",
            "csac_rehydrate_pct": 0.135, "kd_per_100_str": 0.9, "pedigree_tier": 2.0, "cardio_tier": 2.00,
            "base_ko": 0.21, "base_sub": 0.48, "base_dec": 0.31, "vegas_baseline": -280,
            "trivia": "Men's #1 Pound-for-Pound fighter and two-division UFC champion after moving up to 170 lbs."
        },
        {
            "name": "Carlos Prates", "division": "Welterweight", "rank": "#1 Contender", "record": "22-6-0", "natural_weight": 170,
            "style": "Fighting Nerds Muay Thai / Sniper Left Straight", "adaptation_archetype": "natural_frame",
            "slpm": 4.45, "str_acc": 0.56, "sapm": 2.65, "str_def": 0.55,
            "td_avg": 0.20, "td_acc": 0.50, "td_def": 0.80, "sub_avg": 0.10,
            "reach_in": 78.0, "height_in": 73.0, "age": 33, "stance": "Southpaw",
            "csac_rehydrate_pct": 0.130, "kd_per_100_str": 2.8, "pedigree_tier": 1.4, "cardio_tier": 1.80,
            "base_ko": 0.77, "base_sub": 0.14, "base_dec": 0.09, "vegas_baseline": -135,
            "trivia": "Carries a 78-inch reach at Welterweight with 17 career knockout victories."
        },
        {
            "name": "Ian Machado Garry", "division": "Welterweight", "rank": "#2 Contender", "record": "16-1-0", "natural_weight": 170,
            "style": "Dynamic Muay Thai / Distance Striker", "adaptation_archetype": "speed_preserver",
            "slpm": 6.10, "str_acc": 0.55, "sapm": 3.45, "str_def": 0.54,
            "td_avg": 0.75, "td_acc": 0.50, "td_def": 0.74, "sub_avg": 0.30,
            "reach_in": 74.5, "height_in": 75.0, "age": 28, "stance": "Orthodox",
            "csac_rehydrate_pct": 0.115, "kd_per_100_str": 1.2, "pedigree_tier": 1.1, "cardio_tier": 1.85,
            "base_ko": 0.44, "base_sub": 0.06, "base_dec": 0.50, "vegas_baseline": +135,
            "trivia": "Lands over 6 significant strikes per minute with long-range lateral footwork."
        },
        {
            "name": "Michael Morales", "division": "Welterweight", "rank": "#3 Contender", "record": "18-0-0", "natural_weight": 170,
            "style": "Ecuadorian Judo & Wrestling / Heavy Right Hand", "adaptation_archetype": "natural_frame",
            "slpm": 5.35, "str_acc": 0.48, "sapm": 3.10, "str_def": 0.56,
            "td_avg": 1.25, "td_acc": 0.46, "td_def": 0.88, "sub_avg": 0.10,
            "reach_in": 79.0, "height_in": 72.0, "age": 27, "stance": "Orthodox",
            "csac_rehydrate_pct": 0.135, "kd_per_100_str": 2.2, "pedigree_tier": 1.5, "cardio_tier": 1.80,
            "base_ko": 0.72, "base_sub": 0.06, "base_dec": 0.22, "vegas_baseline": -145,
            "trivia": "Undefeated contender boasting a 79-inch reach and 88% takedown defense."
        },
        {
            "name": "Jack Della Maddalena", "division": "Welterweight", "rank": "#4 Contender", "record": "18-2-0", "natural_weight": 170,
            "style": "High-Volume Pocket Boxing / Body Rip Combinations", "adaptation_archetype": "natural_frame",
            "slpm": 6.84, "str_acc": 0.53, "sapm": 4.45, "str_def": 0.64,
            "td_avg": 0.25, "td_acc": 0.20, "td_def": 0.71, "sub_avg": 0.30,
            "reach_in": 73.0, "height_in": 71.0, "age": 30, "stance": "Switch",
            "csac_rehydrate_pct": 0.125, "kd_per_100_str": 1.9, "pedigree_tier": 1.3, "cardio_tier": 1.85,
            "base_ko": 0.67, "base_sub": 0.11, "base_dec": 0.22, "vegas_baseline": -125,
            "trivia": "Averages nearly 7 significant strikes per minute with seamless switch-stance pocket boxing."
        },
        {
            "name": "Shavkat Rakhmonov", "division": "Welterweight", "rank": "#5 Contender", "record": "19-1-0", "natural_weight": 170,
            "style": "Combat Sambo / Master of Sport", "adaptation_archetype": "natural_frame",
            "slpm": 4.25, "str_acc": 0.58, "sapm": 2.65, "str_def": 0.53,
            "td_avg": 2.75, "td_acc": 0.48, "td_def": 0.94, "sub_avg": 1.50,
            "reach_in": 77.0, "height_in": 73.0, "age": 32, "stance": "Orthodox",
            "csac_rehydrate_pct": 0.135, "kd_per_100_str": 1.7, "pedigree_tier": 1.9, "cardio_tier": 1.80,
            "base_ko": 0.42, "base_sub": 0.53, "base_dec": 0.05, "vegas_baseline": -180,
            "trivia": "95% career finish rate across knockout and submission victories."
        },
        {
            "name": "Sean Brady", "division": "Welterweight", "rank": "#6 Contender", "record": "18-1-0", "natural_weight": 170,
            "style": "Renzo Gracie BJJ Black Belt / Pressure Wrestling", "adaptation_archetype": "natural_frame",
            "slpm": 3.85, "str_acc": 0.54, "sapm": 3.15, "str_def": 0.60,
            "td_avg": 3.65, "td_acc": 0.56, "td_def": 0.85, "sub_avg": 1.20,
            "reach_in": 72.5, "height_in": 70.0, "age": 33, "stance": "Orthodox",
            "csac_rehydrate_pct": 0.130, "kd_per_100_str": 0.4, "pedigree_tier": 1.8, "cardio_tier": 1.85,
            "base_ko": 0.17, "base_sub": 0.33, "base_dec": 0.50, "vegas_baseline": -120,
            "trivia": "Dominant top-control grappler averaging 3.65 takedowns per 15 minutes."
        },
        {
            "name": "Belal Muhammad", "division": "Welterweight", "rank": "#7 Contender", "record": "24-4-0", "natural_weight": 170,
            "style": "High-Pressure Wrestling / Boxing", "adaptation_archetype": "natural_frame",
            "slpm": 4.55, "str_acc": 0.43, "sapm": 3.64, "str_def": 0.57,
            "td_avg": 2.20, "td_acc": 0.35, "td_def": 0.91, "sub_avg": 0.20,
            "reach_in": 72.0, "height_in": 70.0, "age": 38, "stance": "Orthodox",
            "csac_rehydrate_pct": 0.120, "kd_per_100_str": 0.4, "pedigree_tier": 1.6, "cardio_tier": 2.00,
            "base_ko": 0.20, "base_sub": 0.05, "base_dec": 0.75, "vegas_baseline": +140,
            "trivia": "Former Welterweight champion known for high-output cardio and pace."
        },

        # --- LIGHTWEIGHT (155 LBS) ---
        {
            "name": "Justin Gaethje", "division": "Lightweight", "rank": "Champion", "record": "28-5-0", "natural_weight": 155,
            "style": "D1 All-American / Violence Kickboxing", "adaptation_archetype": "natural_frame",
            "slpm": 7.03, "str_acc": 0.60, "sapm": 7.20, "str_def": 0.54,
            "td_avg": 0.15, "td_acc": 0.25, "td_def": 0.76, "sub_avg": 0.00,
            "reach_in": 70.0, "height_in": 71.0, "age": 37, "stance": "Orthodox",
            "csac_rehydrate_pct": 0.135, "kd_per_100_str": 2.3, "pedigree_tier": 1.3, "cardio_tier": 1.85,
            "base_ko": 0.75, "base_sub": 0.04, "base_dec": 0.21, "vegas_baseline": +125,
            "trivia": "Undisputed UFC Lightweight Champion and #4 Men's Pound-for-Pound fighter."
        },
        {
            "name": "Ilia Topuria", "division": "Lightweight", "rank": "#1 Contender", "record": "17-1-0", "natural_weight": 155,
            "style": "Greco-Roman Wrestling / Precision Boxing", "adaptation_archetype": "cut_relief",
            "slpm": 4.62, "str_acc": 0.47, "sapm": 3.15, "str_def": 0.65,
            "td_avg": 1.92, "td_acc": 0.56, "td_def": 0.92, "sub_avg": 1.30,
            "reach_in": 69.0, "height_in": 67.0, "age": 29, "stance": "Orthodox",
            "csac_rehydrate_pct": 0.140, "kd_per_100_str": 2.6, "pedigree_tier": 1.9, "cardio_tier": 1.90,
            "base_ko": 0.53, "base_sub": 0.29, "base_dec": 0.18, "vegas_baseline": -190,
            "trivia": "Former Featherweight champion ranked #1 at Lightweight and #5 Pound-for-Pound."
        },
        {
            "name": "Arman Tsarukyan", "division": "Lightweight", "rank": "#2 Contender", "record": "23-3-0", "natural_weight": 155,
            "style": "Freestyle Wrestling / Explosive Muay Thai", "adaptation_archetype": "natural_frame",
            "slpm": 3.89, "str_acc": 0.48, "sapm": 1.93, "str_def": 0.54,
            "td_avg": 3.32, "td_acc": 0.36, "td_def": 0.75, "sub_avg": 0.40,
            "reach_in": 72.5, "height_in": 67.0, "age": 30, "stance": "Orthodox",
            "csac_rehydrate_pct": 0.150, "kd_per_100_str": 1.4, "pedigree_tier": 1.8, "cardio_tier": 1.90,
            "base_ko": 0.43, "base_sub": 0.22, "base_dec": 0.35, "vegas_baseline": -155,
            "trivia": "Holds an elite 1.08 Ape Index for the Lightweight division."
        },
        {
            "name": "Charles Oliveira", "division": "Lightweight", "rank": "#3 Contender", "record": "35-10-0", "natural_weight": 155,
            "style": "Chute Boxe Muay Thai / 3rd Degree BJJ Black Belt", "adaptation_archetype": "cut_relief",
            "slpm": 3.54, "str_acc": 0.53, "sapm": 3.19, "str_def": 0.51,
            "td_avg": 2.38, "td_acc": 0.40, "td_def": 0.55, "sub_avg": 2.70,
            "reach_in": 74.0, "height_in": 70.0, "age": 37, "stance": "Orthodox",
            "csac_rehydrate_pct": 0.140, "kd_per_100_str": 1.8, "pedigree_tier": 2.0, "cardio_tier": 1.65,
            "base_ko": 0.29, "base_sub": 0.60, "base_dec": 0.11, "vegas_baseline": +135,
            "trivia": "Holds the all-time UFC records for most finishes (20) and most submissions (16)."
        },
        {
            "name": "Max Holloway", "division": "Lightweight", "rank": "#4 Contender", "record": "27-8-0", "natural_weight": 155,
            "style": "Hawaiian Volume Boxing / BJJ Brown Belt", "adaptation_archetype": "cut_relief",
            "slpm": 7.17, "str_acc": 0.48, "sapm": 4.75, "str_def": 0.59,
            "td_avg": 0.27, "td_acc": 0.53, "td_def": 0.84, "sub_avg": 0.30,
            "reach_in": 69.0, "height_in": 71.0, "age": 34, "stance": "Orthodox",
            "csac_rehydrate_pct": 0.135, "kd_per_100_str": 0.7, "pedigree_tier": 1.0, "cardio_tier": 2.00,
            "base_ko": 0.44, "base_sub": 0.07, "base_dec": 0.49, "vegas_baseline": -115,
            "trivia": "Holds the UFC all-time record for total significant strikes landed with over 3,400."
        },
        {
            "name": "Paddy Pimblett", "division": "Lightweight", "rank": "#5 Contender", "record": "23-3-0", "natural_weight": 155,
            "style": "Next Generation MMA BJJ / Scramble Submissions", "adaptation_archetype": "natural_frame",
            "slpm": 4.95, "str_acc": 0.52, "sapm": 3.45, "str_def": 0.44,
            "td_avg": 1.45, "td_acc": 0.35, "td_def": 0.55, "sub_avg": 2.10,
            "reach_in": 73.0, "height_in": 70.0, "age": 31, "stance": "Orthodox",
            "csac_rehydrate_pct": 0.150, "kd_per_100_str": 1.0, "pedigree_tier": 1.5, "cardio_tier": 1.75,
            "base_ko": 0.26, "base_sub": 0.48, "base_dec": 0.26, "vegas_baseline": +125,
            "trivia": "Climbed into the Lightweight Top 5 with dangerous triangle and armbar transitions."
        },
        {
            "name": "Benoit Saint Denis", "division": "Lightweight", "rank": "#8 Contender", "record": "15-3-0", "natural_weight": 155,
            "style": "Judo Black Belt / Relentless Southpaw Pressure", "adaptation_archetype": "natural_frame",
            "slpm": 5.30, "str_acc": 0.53, "sapm": 4.55, "str_def": 0.44,
            "td_avg": 4.10, "td_acc": 0.39, "td_def": 0.70, "sub_avg": 1.70,
            "reach_in": 73.0, "height_in": 71.0, "age": 30, "stance": "Southpaw",
            "csac_rehydrate_pct": 0.145, "kd_per_100_str": 1.5, "pedigree_tier": 1.5, "cardio_tier": 1.75,
            "base_ko": 0.27, "base_sub": 0.73, "base_dec": 0.00, "vegas_baseline": -115,
            "trivia": "100% finish rate across all 15 professional wins via KO or submission."
        },
        {
            "name": "Mateusz Gamrot", "division": "Lightweight", "rank": "#9 Contender", "record": "25-3-0", "natural_weight": 155,
            "style": "ADCC European Grappling / Chain Takedown Pace", "adaptation_archetype": "natural_frame",
            "slpm": 3.25, "str_acc": 0.50, "sapm": 3.05, "str_def": 0.60,
            "td_avg": 5.20, "td_acc": 0.36, "td_def": 0.90, "sub_avg": 0.40,
            "reach_in": 70.5, "height_in": 70.0, "age": 35, "stance": "Southpaw",
            "csac_rehydrate_pct": 0.140, "kd_per_100_str": 0.5, "pedigree_tier": 1.9, "cardio_tier": 2.00,
            "base_ko": 0.32, "base_sub": 0.20, "base_dec": 0.48, "vegas_baseline": -130,
            "trivia": "Averages over 5 takedowns per 15 minutes with a 90% takedown defense rate."
        },

        # --- FEATHERWEIGHT (145 LBS) ---
        {
            "name": "Alexander Volkanovski", "division": "Featherweight", "rank": "Champion", "record": "29-4-0", "natural_weight": 145,
            "style": "Freestyle Wrestling / Kickboxing", "adaptation_archetype": "speed_preserver",
            "slpm": 6.19, "str_acc": 0.57, "sapm": 3.40, "str_def": 0.59,
            "td_avg": 1.84, "td_acc": 0.37, "td_def": 0.74, "sub_avg": 0.20,
            "reach_in": 71.5, "height_in": 66.0, "age": 38, "stance": "Orthodox",
            "csac_rehydrate_pct": 0.145, "kd_per_100_str": 0.9, "pedigree_tier": 1.5, "cardio_tier": 2.00,
            "base_ko": 0.41, "base_sub": 0.10, "base_dec": 0.49, "vegas_baseline": -155,
            "trivia": "Reclaimed the Featherweight title and sits #2 in the Men's Pound-for-Pound rankings."
        },
        {
            "name": "Movsar Evloev", "division": "Featherweight", "rank": "#1 Contender", "record": "19-1-0", "natural_weight": 145,
            "style": "Greco-Roman Wrestling / Control Grappling", "adaptation_archetype": "natural_frame",
            "slpm": 4.05, "str_acc": 0.48, "sapm": 2.75, "str_def": 0.61,
            "td_avg": 4.65, "td_acc": 0.48, "td_def": 0.72, "sub_avg": 0.20,
            "reach_in": 72.5, "height_in": 67.0, "age": 32, "stance": "Orthodox",
            "csac_rehydrate_pct": 0.145, "kd_per_100_str": 0.3, "pedigree_tier": 1.9, "cardio_tier": 1.95,
            "base_ko": 0.16, "base_sub": 0.21, "base_dec": 0.63, "vegas_baseline": -145,
            "trivia": "Averages 4.65 takedowns per 15 minutes with relentless scrambles."
        },
        {
            "name": "Diego Lopes", "division": "Featherweight", "rank": "#2 Contender", "record": "27-6-0", "natural_weight": 145,
            "style": "Explosive BJJ Black Belt / Power Hook Striking", "adaptation_archetype": "natural_frame",
            "slpm": 3.55, "str_acc": 0.53, "sapm": 3.85, "str_def": 0.44,
            "td_avg": 0.75, "td_acc": 0.45, "td_def": 0.52, "sub_avg": 3.60,
            "reach_in": 72.5, "height_in": 71.0, "age": 31, "stance": "Orthodox",
            "csac_rehydrate_pct": 0.145, "kd_per_100_str": 2.1, "pedigree_tier": 1.8, "cardio_tier": 1.80,
            "base_ko": 0.44, "base_sub": 0.44, "base_dec": 0.12, "vegas_baseline": -130,
            "trivia": "Averages 3.6 submission attempts per 15 minutes with explosive first-round power."
        },
        {
            "name": "Lerone Murphy", "division": "Featherweight", "rank": "#3 Contender", "record": "16-0-1", "natural_weight": 145,
            "style": "Manchester Technical Muay Thai / Counter Footwork", "adaptation_archetype": "natural_frame",
            "slpm": 4.95, "str_acc": 0.54, "sapm": 2.55, "str_def": 0.60,
            "td_avg": 1.35, "td_acc": 0.52, "td_def": 0.70, "sub_avg": 0.20,
            "reach_in": 73.5, "height_in": 69.0, "age": 35, "stance": "Orthodox",
            "csac_rehydrate_pct": 0.135, "kd_per_100_str": 1.3, "pedigree_tier": 1.2, "cardio_tier": 1.90,
            "base_ko": 0.44, "base_sub": 0.00, "base_dec": 0.56, "vegas_baseline": -120,
            "trivia": "Undefeated Top-3 Featherweight boasting a +2.40 significant strike differential."
        },
        {
            "name": "Aljamain Sterling", "division": "Featherweight", "rank": "#4 Contender", "record": "25-5-0", "natural_weight": 145,
            "style": "D3 All-American Wrestling / Human Backpack BJJ", "adaptation_archetype": "cut_relief",
            "slpm": 4.65, "str_acc": 0.52, "sapm": 2.35, "str_def": 0.58,
            "td_avg": 2.35, "td_acc": 0.26, "td_def": 0.48, "sub_avg": 0.80,
            "reach_in": 71.0, "height_in": 67.0, "age": 37, "stance": "Orthodox",
            "csac_rehydrate_pct": 0.145, "kd_per_100_str": 0.3, "pedigree_tier": 1.8, "cardio_tier": 1.90,
            "base_ko": 0.12, "base_sub": 0.32, "base_dec": 0.56, "vegas_baseline": -115,
            "trivia": "Former Bantamweight champion thriving at 145 lbs with elite back-control grappling."
        },
        {
            "name": "Jean Silva", "division": "Featherweight", "rank": "#5 Contender", "record": "16-2-0", "natural_weight": 145,
            "style": "Fighting Nerds Muay Thai / Heavy Hands", "adaptation_archetype": "natural_frame",
            "slpm": 5.45, "str_acc": 0.53, "sapm": 3.90, "str_def": 0.55,
            "td_avg": 0.85, "td_acc": 0.55, "td_def": 0.82, "sub_avg": 0.50,
            "reach_in": 69.0, "height_in": 67.0, "age": 29, "stance": "Orthodox",
            "csac_rehydrate_pct": 0.140, "kd_per_100_str": 2.9, "pedigree_tier": 1.3, "cardio_tier": 1.80,
            "base_ko": 0.75, "base_sub": 0.13, "base_dec": 0.12, "vegas_baseline": -140,
            "trivia": "88% career finish rate with high-torque uppercuts and elbow counters."
        },
        {
            "name": "Aaron Pico", "division": "Featherweight", "rank": "#9 Contender", "record": "13-4-0", "natural_weight": 145,
            "style": "Freestyle Wrestling World Champ / Golden Gloves Boxing", "adaptation_archetype": "natural_frame",
            "slpm": 4.85, "str_acc": 0.54, "sapm": 3.10, "str_def": 0.55,
            "td_avg": 3.80, "td_acc": 0.58, "td_def": 0.86, "sub_avg": 0.30,
            "reach_in": 70.5, "height_in": 68.0, "age": 30, "stance": "Orthodox",
            "csac_rehydrate_pct": 0.140, "kd_per_100_str": 2.3, "pedigree_tier": 1.9, "cardio_tier": 1.80,
            "base_ko": 0.69, "base_sub": 0.15, "base_dec": 0.16, "vegas_baseline": -125,
            "trivia": "Former Bellator standout who entered the UFC Top 10 with elite wrestling and body-shot boxing."
        },
        {
            "name": "Patricio Pitbull", "division": "Featherweight", "rank": "#12 Contender", "record": "37-8-0", "natural_weight": 145,
            "style": "Pitbull Brothers Counter Boxing / Guillotine Specialist", "adaptation_archetype": "natural_frame",
            "slpm": 3.75, "str_acc": 0.49, "sapm": 2.95, "str_def": 0.58,
            "td_avg": 1.15, "td_acc": 0.45, "td_def": 0.80, "sub_avg": 0.90,
            "reach_in": 65.5, "height_in": 66.0, "age": 39, "stance": "Orthodox",
            "csac_rehydrate_pct": 0.135, "kd_per_100_str": 1.8, "pedigree_tier": 1.7, "cardio_tier": 1.75,
            "base_ko": 0.35, "base_sub": 0.32, "base_dec": 0.33, "vegas_baseline": +120,
            "trivia": "Former two-division Bellator champion ranked inside the UFC Featherweight Top 15."
        },

        # --- BANTAMWEIGHT (135 LBS) ---
        {
            "name": "Petr Yan", "division": "Bantamweight", "rank": "Champion", "record": "21-5-0", "natural_weight": 135,
            "style": "Master of Sport Boxing / High-Guard Pressure", "adaptation_archetype": "natural_frame",
            "slpm": 5.25, "str_acc": 0.55, "sapm": 3.90, "str_def": 0.60,
            "td_avg": 1.75, "td_acc": 0.53, "td_def": 0.86, "sub_avg": 0.20,
            "reach_in": 67.0, "height_in": 67.0, "age": 33, "stance": "Switch",
            "csac_rehydrate_pct": 0.140, "kd_per_100_str": 1.4, "pedigree_tier": 1.7, "cardio_tier": 2.00,
            "base_ko": 0.38, "base_sub": 0.05, "base_dec": 0.57, "vegas_baseline": -145,
            "trivia": "Two-time UFC Bantamweight champion and #3 Men's Pound-for-Pound fighter."
        },
        {
            "name": "Merab Dvalishvili", "division": "Bantamweight", "rank": "#1 Contender", "record": "19-5-0", "natural_weight": 135,
            "style": "Sambo / High-Pace Relentless Wrestling", "adaptation_archetype": "natural_frame",
            "slpm": 4.50, "str_acc": 0.42, "sapm": 2.40, "str_def": 0.62,
            "td_avg": 6.43, "td_acc": 0.36, "td_def": 0.80, "sub_avg": 0.30,
            "reach_in": 68.0, "height_in": 66.0, "age": 35, "stance": "Orthodox",
            "csac_rehydrate_pct": 0.155, "kd_per_100_str": 0.3, "pedigree_tier": 1.9, "cardio_tier": 2.00,
            "base_ko": 0.16, "base_sub": 0.05, "base_dec": 0.79, "vegas_baseline": -175,
            "trivia": "Holds the UFC record for most career takedowns landed across all divisions."
        },
        {
            "name": "Sean O'Malley", "division": "Bantamweight", "rank": "#2 Contender", "record": "19-2-0", "natural_weight": 135,
            "style": "Feint-Heavy Counter Sniping Boxing", "adaptation_archetype": "speed_preserver",
            "slpm": 7.25, "str_acc": 0.61, "sapm": 3.52, "str_def": 0.62,
            "td_avg": 0.35, "td_acc": 0.42, "td_def": 0.65, "sub_avg": 0.40,
            "reach_in": 72.0, "height_in": 71.0, "age": 32, "stance": "Switch",
            "csac_rehydrate_pct": 0.140, "kd_per_100_str": 1.9, "pedigree_tier": 0.9, "cardio_tier": 1.85,
            "base_ko": 0.68, "base_sub": 0.05, "base_dec": 0.27, "vegas_baseline": +125,
            "trivia": "Maintains a 61% striking accuracy—ranking in the 99th percentile in Bantamweight history."
        },
        {
            "name": "Song Yadong", "division": "Bantamweight", "rank": "#3 Contender", "record": "23-8-1", "natural_weight": 135,
            "style": "Sanda Kickboxing / Explosive Pocket Power", "adaptation_archetype": "natural_frame",
            "slpm": 4.75, "str_acc": 0.43, "sapm": 3.85, "str_def": 0.56,
            "td_avg": 0.65, "td_acc": 0.42, "td_def": 0.74, "sub_avg": 0.20,
            "reach_in": 67.0, "height_in": 68.0, "age": 28, "stance": "Orthodox",
            "csac_rehydrate_pct": 0.145, "kd_per_100_str": 1.6, "pedigree_tier": 1.3, "cardio_tier": 1.80,
            "base_ko": 0.43, "base_sub": 0.13, "base_dec": 0.44, "vegas_baseline": +115,
            "trivia": "Entered the Bantamweight Top 3 with heavy combination boxing and 74% takedown defense."
        },
        {
            "name": "Umar Nurmagomedov", "division": "Bantamweight", "rank": "#4 Contender", "record": "19-1-0", "natural_weight": 135,
            "style": "Dagestani Combat Sambo / Kicking Arsenal", "adaptation_archetype": "natural_frame",
            "slpm": 4.65, "str_acc": 0.66, "sapm": 1.25, "str_def": 0.66,
            "td_avg": 4.10, "td_acc": 0.50, "td_def": 0.92, "sub_avg": 0.85,
            "reach_in": 69.0, "height_in": 68.0, "age": 30, "stance": "Southpaw",
            "csac_rehydrate_pct": 0.145, "kd_per_100_str": 0.9, "pedigree_tier": 2.0, "cardio_tier": 1.90,
            "base_ko": 0.21, "base_sub": 0.37, "base_dec": 0.42, "vegas_baseline": -210,
            "trivia": "Blends switch-stance body kicks with Dagestani chain wrestling and 92% takedown defense."
        },
        {
            "name": "Cory Sandhagen", "division": "Bantamweight", "rank": "#6 Contender", "record": "18-5-0", "natural_weight": 135,
            "style": "Switch-Stance Creative Kickboxing / Flying Knees", "adaptation_archetype": "speed_preserver",
            "slpm": 5.35, "str_acc": 0.44, "sapm": 3.45, "str_def": 0.58,
            "td_avg": 1.15, "td_acc": 0.32, "td_def": 0.64, "sub_avg": 0.30,
            "reach_in": 70.0, "height_in": 71.0, "age": 34, "stance": "Switch",
            "csac_rehydrate_pct": 0.135, "kd_per_100_str": 1.1, "pedigree_tier": 1.3, "cardio_tier": 1.95,
            "base_ko": 0.44, "base_sub": 0.17, "base_dec": 0.39, "vegas_baseline": -130,
            "trivia": "5'11\" Bantamweight striker utilizing constant stance switches and level-change takedowns."
        },
        {
            "name": "Payton Talbott", "division": "Bantamweight", "rank": "#7 Contender", "record": "11-1-0", "natural_weight": 135,
            "style": "High-Output Sniper Boxing / Rising Finisher", "adaptation_archetype": "speed_preserver",
            "slpm": 7.45, "str_acc": 0.56, "sapm": 3.80, "str_def": 0.54,
            "td_avg": 0.60, "td_acc": 0.50, "td_def": 0.72, "sub_avg": 0.40,
            "reach_in": 70.0, "height_in": 70.0, "age": 28, "stance": "Switch",
            "csac_rehydrate_pct": 0.135, "kd_per_100_str": 2.2, "pedigree_tier": 1.1, "cardio_tier": 1.85,
            "base_ko": 0.73, "base_sub": 0.09, "base_dec": 0.18, "vegas_baseline": -135,
            "trivia": "Lands over 7.4 significant strikes per minute with an 82% career finish rate."
        },

        # --- FLYWEIGHT (125 LBS) ---
        {
            "name": "Joshua Van", "division": "Flyweight", "rank": "Champion", "record": "18-2-0", "natural_weight": 125,
            "style": "High-Pace Pocket Boxing / Body-Head Volume", "adaptation_archetype": "natural_frame",
            "slpm": 8.25, "str_acc": 0.55, "sapm": 5.40, "str_def": 0.56,
            "td_avg": 0.95, "td_acc": 0.55, "td_def": 0.81, "sub_avg": 0.10,
            "reach_in": 65.0, "height_in": 65.0, "age": 25, "stance": "Orthodox",
            "csac_rehydrate_pct": 0.140, "kd_per_100_str": 1.4, "pedigree_tier": 1.4, "cardio_tier": 2.00,
            "base_ko": 0.50, "base_sub": 0.11, "base_dec": 0.39, "vegas_baseline": -145,
            "trivia": "UFC Flyweight Champion and #6 Pound-for-Pound fighter averaging over 8 strikes per minute."
        },
        {
            "name": "Alexandre Pantoja", "division": "Flyweight", "rank": "#1 Contender", "record": "29-6-0", "natural_weight": 125,
            "style": "Aggressive BJJ Black Belt / Muay Thai Brawl", "adaptation_archetype": "natural_frame",
            "slpm": 4.41, "str_acc": 0.49, "sapm": 3.75, "str_def": 0.53,
            "td_avg": 2.65, "td_acc": 0.45, "td_def": 0.67, "sub_avg": 1.20,
            "reach_in": 67.0, "height_in": 65.0, "age": 36, "stance": "Orthodox",
            "csac_rehydrate_pct": 0.150, "kd_per_100_str": 0.9, "pedigree_tier": 1.8, "cardio_tier": 1.95,
            "base_ko": 0.31, "base_sub": 0.38, "base_dec": 0.31, "vegas_baseline": -165,
            "trivia": "Former Flyweight champion with 11 submission victories at 125 lbs."
        },
        {
            "name": "Manel Kape", "division": "Flyweight", "rank": "#2 Contender", "record": "21-7-0", "natural_weight": 125,
            "style": "Explosive Counter Boxing / Flying Knee Finisher", "adaptation_archetype": "natural_frame",
            "slpm": 5.15, "str_acc": 0.53, "sapm": 4.10, "str_def": 0.58,
            "td_avg": 0.65, "td_acc": 0.35, "td_def": 0.77, "sub_avg": 0.40,
            "reach_in": 68.0, "height_in": 65.0, "age": 33, "stance": "Southpaw",
            "csac_rehydrate_pct": 0.145, "kd_per_100_str": 2.1, "pedigree_tier": 1.3, "cardio_tier": 1.80,
            "base_ko": 0.62, "base_sub": 0.24, "base_dec": 0.14, "vegas_baseline": -130,
            "trivia": "Former Rizin Bantamweight champion boasting an 86% career finish rate."
        },
        {
            "name": "Brandon Royval", "division": "Flyweight", "rank": "#3 Contender", "record": "17-8-0", "natural_weight": 125,
            "style": "High-Chaos Scramble Grappling / Volume Boxing", "adaptation_archetype": "speed_preserver",
            "slpm": 3.90, "str_acc": 0.43, "sapm": 3.35, "str_def": 0.51,
            "td_avg": 0.70, "td_acc": 1.00, "td_def": 0.65, "sub_avg": 1.70,
            "reach_in": 70.0, "height_in": 67.0, "age": 34, "stance": "Southpaw",
            "csac_rehydrate_pct": 0.135, "kd_per_100_str": 1.4, "pedigree_tier": 1.3, "cardio_tier": 1.90,
            "base_ko": 0.29, "base_sub": 0.53, "base_dec": 0.18, "vegas_baseline": +135,
            "trivia": "Maintains a high submission attempt rate of 1.7 per 15 minutes with a 70-inch reach."
        },
        {
            "name": "Tatsuro Taira", "division": "Flyweight", "rank": "#4 Contender", "record": "17-1-0", "natural_weight": 125,
            "style": "Okinawan Shooto Grappling / Back-Take Triangles", "adaptation_archetype": "natural_frame",
            "slpm": 3.25, "str_acc": 0.62, "sapm": 1.85, "str_def": 0.54,
            "td_avg": 2.45, "td_acc": 0.46, "td_def": 0.62, "sub_avg": 2.20,
            "reach_in": 70.0, "height_in": 67.0, "age": 26, "stance": "Orthodox",
            "csac_rehydrate_pct": 0.145, "kd_per_100_str": 0.7, "pedigree_tier": 1.7, "cardio_tier": 1.85,
            "base_ko": 0.29, "base_sub": 0.47, "base_dec": 0.24, "vegas_baseline": -150,
            "trivia": "Carries a 70-inch wingspan at 125 lbs with suffocating body-triangle control."
        },
        {
            "name": "Kyoji Horiguchi", "division": "Flyweight", "rank": "#5 Contender", "record": "34-5-0", "natural_weight": 125,
            "style": "Traditional Shotokan Karate Blitz / Explosive Wrestling", "adaptation_archetype": "speed_preserver",
            "slpm": 4.25, "str_acc": 0.48, "sapm": 2.35, "str_def": 0.63,
            "td_avg": 2.35, "td_acc": 0.52, "td_def": 0.78, "sub_avg": 0.60,
            "reach_in": 66.0, "height_in": 65.0, "age": 36, "stance": "Orthodox",
            "csac_rehydrate_pct": 0.130, "kd_per_100_str": 1.6, "pedigree_tier": 1.8, "cardio_tier": 1.90,
            "base_ko": 0.44, "base_sub": 0.15, "base_dec": 0.41, "vegas_baseline": -135,
            "trivia": "Former Rizin and Bellator champion ranked inside the UFC Flyweight Top 5."
        },
        {
            "name": "Brandon Moreno", "division": "Flyweight", "rank": "#8 Contender", "record": "22-8-2", "natural_weight": 125,
            "style": "Technical Mexican Boxing / Scramble BJJ", "adaptation_archetype": "natural_frame",
            "slpm": 3.85, "str_acc": 0.44, "sapm": 3.40, "str_def": 0.56,
            "td_avg": 1.73, "td_acc": 0.45, "td_def": 0.65, "sub_avg": 0.60,
            "reach_in": 70.0, "height_in": 67.0, "age": 32, "stance": "Orthodox",
            "csac_rehydrate_pct": 0.140, "kd_per_100_str": 0.7, "pedigree_tier": 1.5, "cardio_tier": 1.95,
            "base_ko": 0.23, "base_sub": 0.50, "base_dec": 0.27, "vegas_baseline": -125,
            "trivia": "Two-time UFC Flyweight champion with high-volume jab combinations."
        }
    ]

    df = pd.DataFrame(fighters)
    df["slug"] = df["name"].apply(lambda n: to_slug(n, "-"))

    print("Syncing UFC athlete cutouts into assets/fighters/...")
    df["local_image_path"] = df["name"].apply(resolve_and_save_asset)

    parquet_path = DATA_DIR / "fighters_master.parquet"
    df.to_parquet(parquet_path, engine="pyarrow", index=False)
    print(f"\nSynchronized {len(df)} UFC contenders to {parquet_path}")

if __name__ == "__main__":
    build_roster_database()