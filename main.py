from flask import Flask, jsonify
import cloudscraper
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/latest-episodes')
def latest_episodes():
    domains = ["https://anime4up.com/", "https://anime4up.tv/"]
    scraper = cloudscraper.create_scraper()
    
    html_content = ""
    working_domain = ""
    
    for domain in domains:
        try:
            response = scraper.get(domain, timeout=15)
            if response.status_code == 200:
                html_content = response.text
                working_domain = domain
                break
        except:
            continue
            
    if not html_content:
        return jsonify({"error": "Could not reach Anime4Up"}), 500

    soup = BeautifulSoup(html_content, 'html.parser')
    
    # البحث عن أي عنصر يشبه بطاقة الأنمي (تجربة عدة كلاسات)
    items = soup.select(".anime-card-container")
    if not items:
        items = soup.select("div.anime-card")
    if not items:
        items = soup.select("article")
        
    if not items:
        # إذا لم نجد شيئاً، نطبع جزءاً من الـ HTML لنعرف السبب
        return jsonify({
            "message": "Could not find anime cards. Here is a snippet of the HTML to debug:",
            "html_snippet": html_content[:1500] # أول 1500 حرف
        })

    results = []
    for item in items:
        title_elem = item.select_one(".anime-card-title")
        if not title_elem: title_elem = item.select_one("h3")
        if not title_elem: title_elem = item.select_one("h2")
        
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

    return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)