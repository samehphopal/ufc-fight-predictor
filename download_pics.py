import re, time, unicodedata, urllib.request
from pathlib import Path
import pandas as pd

IMG_DIR = Path("assets/fighters")
IMG_DIR.mkdir(parents=True, exist_ok=True)
PARQUET = Path("data/fighters_master.parquet")
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def to_slug(name, sep="-"):
    clean = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", sep, clean.lower()).strip(sep)

df = pd.read_parquet(PARQUET)
paths = []
saved_count = 0

for name in df["name"]:
    file_path = IMG_DIR / f"{to_slug(name, '_')}.png"
    if file_path.exists() and file_path.stat().st_size > 1000:
        paths.append(str(file_path).replace("\\", "/"))
        saved_count += 1
        continue

    url = f"https://www.ufc.com/athlete/{to_slug(name, '-')}"
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        html = urllib.request.urlopen(req, timeout=10).read().decode("utf-8", errors="ignore")
        match = re.search(
            r'((?:https://[^"\'\s]+)?/images/styles/(?:teaser|event_results_athlete_headshot|athlete_bio_full_body)/[^"\'\s]+\.(?:png|webp|jpg))',
            html
        )
        if match:
            img_url = match.group(1)
            if img_url.startswith("/"):
                img_url = "https://www.ufc.com" + img_url
            img_req = urllib.request.Request(img_url, headers=HEADERS)
            file_path.write_bytes(urllib.request.urlopen(img_req, timeout=10).read())
            paths.append(str(file_path).replace("\\", "/"))
            saved_count += 1
            print(f"Saved: {file_path.name}")
        else:
            print(f"No image found: {name}")
            paths.append(None)
    except Exception as e:
        print(f"Skipped {name}: {e}")
        paths.append(None)
    time.sleep(0.3)

df["local_image_path"] = paths
df.to_parquet(PARQUET, index=False)
print(f"Finished! {saved_count}/{len(df)} fighter images ready.")