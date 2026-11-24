"""Fetch last week's top Reddit posts + best comments, drop self-promo, save JSON.
Usage: python3 reddit_reader.py [days]   -> writes data/reddit_YYYY-MM-DD.json
"""
import json, re, sys, time, urllib.request, datetime, os

SUBS = ["AI_Agents", "gtmengineering", "consulting", "sales", "coldemail", "Entrepreneur",
        "agency", "automation", "n8n", "LocalLLaMA", "ClaudeAI", "smallbusiness",
        "startups_italia", "B2BSales", "LinkedInTips"]
POSTS_PER_SUB = 12
COMMENTS_PER_POST = 6
MIN_SCORE = 15
PROMO = re.compile(r"\b(dm me|book a call|my agency|we help|hire us|link in bio|check out my|"
                   r"free trial|sign up|waitlist|my saas|i built a tool|launching)\b", re.I)
import base64, urllib.parse
UA = {"User-Agent": "mac:learning-hub-reader:v0.2 (personal use)"}

def load_env():
    env = {}
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(path):
        for line in open(path):
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.strip().split("=", 1); env[k.strip()] = v.strip()
    return env

def token():
    e = load_env()
    cid, sec = e.get("REDDIT_CLIENT_ID"), e.get("REDDIT_CLIENT_SECRET")
    if not cid or not sec or "paste" in cid:
        sys.exit("Missing Reddit key: fill in REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET in hub/.env")
    req = urllib.request.Request("https://www.reddit.com/api/v1/access_token",
        data=urllib.parse.urlencode({"grant_type": "client_credentials"}).encode(),
        headers={**UA, "Authorization": "Basic " + base64.b64encode(f"{cid}:{sec}".encode()).decode()})
    with urllib.request.urlopen(req, timeout=20) as r:
        UA["Authorization"] = "bearer " + json.load(r)["access_token"]

def get(url):
    for i in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20) as r:
                return json.load(r)
        except Exception as e:
            time.sleep(3 * (i + 1)); err = e
    print("skip", url, err, file=sys.stderr); return None

def main():
    token()
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    cutoff = time.time() - days * 86400
    out, skipped = [], []
    for sub in SUBS:
        d = get(f"https://oauth.reddit.com/r/{sub}/top?t=week&limit={POSTS_PER_SUB}")
        time.sleep(1.5)
        if not d: skipped.append({"sub": sub, "why": "fetch failed"}); continue
        for c in d["data"]["children"]:
            p = c["data"]
            if p["created_utc"] < cutoff or p["score"] < MIN_SCORE or p.get("stickied"):
                continue
            text = (p.get("selftext") or "")
            if PROMO.search(p["title"] + " " + text[:500]):
                skipped.append({"sub": sub, "title": p["title"], "why": "self-promo"}); continue
            th = get(f"https://oauth.reddit.com{p['permalink']}?sort=top&limit={COMMENTS_PER_POST}")
            time.sleep(1.5)
            comments = []
            if th and len(th) > 1:
                for cc in th[1]["data"]["children"]:
                    cd = cc.get("data", {})
                    if cc.get("kind") == "t1" and cd.get("score", 0) >= 3 and len(cd.get("body", "")) > 80:
                        comments.append({"score": cd["score"], "body": cd["body"][:2500]})
            out.append({"sub": sub, "title": p["title"], "score": p["score"],
                        "n_comments": p["num_comments"], "url": "https://www.reddit.com" + p["permalink"],
                        "date": datetime.date.fromtimestamp(p["created_utc"]).isoformat(),
                        "text": text[:4000], "comments": comments[:COMMENTS_PER_POST]})
    os.makedirs("data", exist_ok=True)
    fn = f"data/reddit_{datetime.date.today().isoformat()}.json"
    json.dump({"posts": out, "skipped": skipped}, open(fn, "w"), ensure_ascii=False, indent=1)
    print(fn, len(out), "kept,", len(skipped), "skipped")

if __name__ == "__main__":
    main()
