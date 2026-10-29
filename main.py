from flask import Flask, jsonify
import cloudscraper
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/latest-episodes')
def latest_episodes():
    # قائمة النطاقات المحتملة لموقع Anime4Up
    domains = ["https://anime4up.com/", "https://anime4up.tv/", "https://wl.anime4up.rest/"]
    scraper = cloudscraper.create_scraper()
    
    html_content = ""
    working_domain = ""
    
    for domain in domains:
        try:
            response = scraper.get(domain, timeout=15)
            if response.status_code == 200:
                # إصلاح اللغة العربية (UTF-8)
                html_content = response.content.decode('utf-8', errors='ignore')
                working_domain = domain
                break
        except:
            continue
            
    if not html_content:
        return jsonify({"error": "Could not reach Anime4Up"}), 500

    soup = BeautifulSoup(html_content, 'html.parser')
    results = []
    
    # البحث عن البطاقات بأكثر من كلاس محتمل
    items = soup.select(".anime-card-container")
    if not items: items = soup.select(".anime-card")
    if not items: items = soup.select("div.anime")
    
    if not items:
        # إذا لم نجد، نطبع جزءاً من الـ body لنرى الكلاسات الحقيقية
        body = soup.find('body')
        snippet = str(body)[:2500] if body else html_content[1000:3000]
        return jsonify({
            "message": "Could not find anime cards. Here is a snippet of the BODY to debug:",
            "body_snippet": snippet
        })

    for item in items:
        # البحث عن العنوان والصورة بأكثر من كلاس
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