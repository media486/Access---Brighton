# Access Brighton — Daily Disability News

A static website that automatically updates every morning with the latest disability news from Brighton & Hove and Sussex.

**Powered by:** Anthropic Claude + Web Search · Hosted on GitHub Pages · Updated via GitHub Actions

---

## How it works

1. Every day at ~7am UK time, GitHub Actions runs `generate_site.py`
2. The script asks Claude to search the web for Brighton disability news
3. Claude generates structured news content and the script renders `index.html`
4. GitHub Actions commits the new `index.html` and GitHub Pages serves it live

---

## One-time setup

### 1. Add your Anthropic API key as a GitHub Secret

- Go to your repo → **Settings** → **Secrets and variables** → **Actions**
- Click **New repository secret**
- Name: `ANTHROPIC_API_KEY`
- Value: your key from [console.anthropic.com](https://console.anthropic.com)

### 2. Enable GitHub Pages

- Go to your repo → **Settings** → **Pages**
- Under **Source**, select **Deploy from a branch**
- Branch: `main` · Folder: `/ (root)`
- Click **Save**

Your site will be live at: `https://YOUR-USERNAME.github.io/access-brighton`

### 3. Trigger the first run manually

- Go to **Actions** tab → **Daily News Update** → **Run workflow**
- This generates the first real news page immediately

---

## Local testing (optional)

```bash
pip install anthropic
export ANTHROPIC_API_KEY=your_key_here
python generate_site.py
# Open index.html in your browser
```

---

## Customisation

Edit `generate_site.py` to change:
- The search queries (line ~25) to focus on different topics
- The update schedule in `.github/workflows/daily-update.yml` (cron line)
- The HTML template at the bottom of the script
