# 🥊 UFC Fight Outcome & Win-Probability Engine

**[🚀 Launch Live Interactive App](https://sameh-ufc-predictor.streamlit.app)**

An interactive MMA matchup simulator and sports-analytics dashboard built with Python and Streamlit. It combines fighter performance stats, post-weigh-in fight-night weight modeling, and stylistic analysis to generate calibrated win probabilities and benchmark them against live sportsbook odds.

## Why I Built This
Anyone who watches MMA closely knows box-score stats never tell the full story. Two fighters can both make 155 lbs on Friday morning, yet step into the cage Saturday night 15 pounds apart as a true weight bully takes over the grappling exchanges. A sharp technical striker with clean hands can look unbeatable on paper until a relentless wrestler forces them to lower their guard, or a dangerous finisher changes the fight with one clean shot.

Most sports models miss these dynamics completely. They feed flat career averages into a black box and output a win percentage with zero context. I built this engine to model the real variables that decide matchups: fight-night weight rehydration, frame leverage (Ape Index), finishing danger versus technical striking volume, stylistic clashes like boxer versus kicker or grappler versus striker, five-round cardio scaling, and division-specific aging curves. Every prediction breaks down the exact drivers behind a fighter's path to victory, enforces smart guardrails against unrealistic weight cuts, and gets audited against closing sportsbook odds using win rate, +EV ROI, and Brier calibration.

This is just the first release. Future updates will incorporate additional calibration factors and variables to push accuracy even further, all while keeping the interface clean, intuitive, and visually sharp.

---

## Key Features

- **64-Fighter Ranked Roster:** Covers all 8 UFC men's divisions (`etl_pipeline.py` -> `data/fighters_master.parquet`) with official athlete portraits and division filtering.
- **Explainable Win-Probability Model:** Scores 6 core drivers (Grappling & Control, Striking & Damage Efficiency, Fight-Night Size, Reach & Frame, Cardio & Pace, and Non-Linear Prime Age Curve) with temperature-scaled logistic calibration for 4-oz glove MMA variance.
- **Fight-Night Weight & Cut Guardrails:** Estimates actual in-cage weight using California State Athletic Commission (CSAC) rehydration baselines and triggers automated UX warnings for unrealistic weight cuts, late-career cuts, or extreme cross-division size gaps.
- **Fight Analyst Scout Report:** Generates dynamic paths to victory and stylistic clash callouts (Boxing vs. Muay Thai kicking range, open-stance dynamics, "lighter man's skill," and defensive craft).
- **Round-by-Round & Finish Projections:** Visualizes cardio-adjusted win probability across 3- or 5-round bouts alongside KO/TKO, Submission, and Decision splits.
- **Transparent Historical Backtest Audit:** Benchmarks 10 featured main-card bouts against closing Vegas moneylines, dynamically computing Overall Win Rate, High-Conviction Win Rate (`>=70%`), `+EV` Flat-Bet ROI, and **Brier Calibration Score**, complete with a built-in metrics guide.

---

## Tech Stack

- **Frontend & Deployment:** Streamlit, Custom CSS, Streamlit Community Cloud
- **Data & Modeling:** Python, Pandas, NumPy, PyArrow (Parquet), Requests
- **Visualization:** Plotly (Factor Impact Bar Charts, Skill Profile Radar, Round & Finish Distributions)

---

## Run Locally

```bash
git clone [https://github.com/samehphopal/ufc-fight-predictor.git](https://github.com/samehphopal/ufc-fight-predictor.git)
cd ufc-fight-predictor
pip install -r requirements.txt
streamlit run app.py
