from flask import Flask, jsonify
import cloudscraper
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/latest-episodes')
def latest_episodes():
    # استخدام موقع Anime4Up كبديل
    domains = ["https://anime4up.com/", "https://anime4up.tv/"]
    scraper = cloudscraper.create_scraper()
    
    html_content = ""
    working_domain = ""
    
    for domain in domains:
        try:
            response = scraper.get(domain, timeout=15)
            if response.status_code == 200 and "anime" in response.text.lower():
                html_content = response.text
                working_domain = domain
                break
        except:
            continue
            
    if not html_content:
        return jsonify({"error": "Could not reach Anime4Up"}), 500

    soup = BeautifulSoup(html_content, 'html.parser')
    results = []
    
    # المحددات الخاصة بموقع Anime4Up
    items = soup.select(".anime-card-container")
    
    for item in items:
        title_elem = item.select_one(".anime-card-title")
        img_elem = item.select_one("img")
        link_elem = item.select_one("a")
        
        if title_elem and img_elem:
            title = title_elem.text.strip()
            img = img_elem.get("src") or img_elem.get("data-src") or ""
            if img.startswith("//"): img = "https:" + img
            link = link_elem.get("href") if link_elem else ""
            
            results.append({
                "title": title,
                "poster": img,
                "url": link
            })
            
    # إذا لم يجد شيئاً (احتياطي)
    if not results:
        for item in soup.select("article"):
            title_elem = item.select_one("h2, h3, .title, .anime-card-title")
            img_elem = item.select_one("img")
            if title_elem and img_elem:
                title = title_elem.text.strip()
                img = img_elem.get("src") or img_elem.get("data-src") or ""
                if img.startswith("//"): img = "https:" + img
                results.append({
                    "title": title,
                    "poster": img,
                    "url": working_domain
                })

    if not results:
        return jsonify({"message": "Reached site but couldn't find anime. Selectors might be wrong."})

    return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)