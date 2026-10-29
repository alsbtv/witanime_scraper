from flask import Flask, jsonify, Response
import cloudscraper
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/latest-episodes')
def latest_episodes():
    domains = ["https://witanime.best/", "https://witanime.com/"]
    scraper = cloudscraper.create_scraper()
    
    html_content = ""
    working_domain = ""
    
    for domain in domains:
        try:
            response = scraper.get(domain, timeout=10)
            if response.status_code == 200:
                html_content = response.text
                working_domain = domain
                break
        except:
            continue
            
    if not html_content:
        return jsonify({"error": "All domains failed."}), 500

    soup = BeautifulSoup(html_content, 'html.parser')
    results = []
    
    # سنجرب أوسع كلاس ممكن
    items = soup.select("article, .post-item, .anime-card-container, .anime-card, .thumb")
    
    for item in items:
        # استخراج أي رابط موجود
        link_elem = item.select_one("a")
        link = link_elem.get("href", "") if link_elem else ""
        if link.startswith("/"): link = working_domain.rstrip("/") + link
        
        # استخراج أي صورة موجودة
        img_elem = item.select_one("img")
        poster = ""
        if img_elem:
            poster = img_elem.get("src") or img_elem.get("data-src") or img_elem.get("data-lazy-src") or ""
            if poster.startswith("//"): poster = "https:" + poster
            
        # استخراج أي نص كعنوان
        title = item.text.strip()[:50] # نأخذ أول 50 حرف كعنوان مؤقت
        
        if title and link:
            results.append({"title": title, "poster": poster, "url": link})

    if not results:
        return jsonify({"message": "Still no results", "items_found": len(items)})
        
    return jsonify(results)

# هذه الصفحة الجديدة ستطبع الكود الخام لنرى الكلاسات الحقيقية
@app.route('/html')
def get_html():
    scraper = cloudscraper.create_scraper()
    try:
        res = scraper.get("https://witanime.best/", timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        items = soup.select("article, .post-item, .anime-card-container, .anime-card, .thumb")
        if items:
            # نطبع أول عنصرين لكي نرى شكلهم
            html_snippet = "".join([item.prettify() for item in items[:2]])
            return Response(html_snippet, mimetype='text/html')
        return "No items found."
    except Exception as e:
        return str(e)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)