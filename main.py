from flask import Flask, jsonify
import cloudscraper
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

@app.route('/latest-episodes')
def latest_episodes():
    domains = ["https://anime4up.com/", "https://anime4up.tv/", "https://wl.anime4up.rest/"]
    scraper = cloudscraper.create_scraper()
    
    html_content = ""
    working_domain = ""
    
    for domain in domains:
        try:
            response = scraper.get(domain, timeout=15)
            if response.status_code == 200:
                html_content = response.content.decode('utf-8', errors='ignore')
                working_domain = domain
                break
        except:
            continue
            
    if not html_content:
        return jsonify({"error": "Could not reach Anime4Up"}), 500

    soup = BeautifulSoup(html_content, 'html.parser')
    results = []
    seen_titles = set() # لمنع التكرار

    # البحث عن أي رابط يحتوي على /anime/ أو /episode/
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        if '/anime/' in href or '/episode/' in href:
            # البحث عن الصورة داخل الرابط أو بجانبه
            img_tag = a_tag.find('img')
            if not img_tag and a_tag.parent:
                img_tag = a_tag.parent.find('img')
                
            # استخراج العنوان
            title = a_tag.text.strip()
            if not title and img_tag:
                title = img_tag.get('alt', '').strip()
                
            # استخراج الصورة
            img_url = ""
            if img_tag:
                img_url = img_tag.get('src') or img_tag.get('data-src') or img_tag.get('data-lazy-src') or ""
                if img_url.startswith("//"): img_url = "https:" + img_url
                
            # تنظيف العنوان والتأكد من أنه ليس فارغاً
            title = re.sub(r'\s+', ' ', title)
            if title and len(title) > 3 and title not in seen_titles and img_url:
                seen_titles.add(title)
                results.append({
                    "title": title,
                    "poster": img_url,
                    "url": href
                })

    if not results:
        return jsonify({"message": "Could not find anime links using brute force."})

    return jsonify(results[:20]) # إرجاع أول 20 أنمي فقط

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)