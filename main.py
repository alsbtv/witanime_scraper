from flask import Flask, jsonify
import cloudscraper
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/latest-episodes')
def latest_episodes():
    # قائمة بالروابط المحتملة للموقع
    domains = ["https://witanime.com/", "https://witanime.cyou/", "https://witanime.best/"]
    scraper = cloudscraper.create_scraper() # متصفح وهمي يتجاوز الحماية
    
    html_content = ""
    working_domain = ""
    
    # 1. تجربة الروابط حتى نجد واحداً يعمل
    for domain in domains:
        try:
            response = scraper.get(domain, timeout=10)
            if response.status_code == 200 and "anime" in response.text.lower():
                html_content = response.text
                working_domain = domain
                break
        except:
            continue
            
    if not html_content:
        return jsonify({"error": "All domains failed to load. Blocked by Cloudflare or network."}), 500

    soup = BeautifulSoup(html_content, 'html.parser')
    results = []
    
    # 2. محاولة استخدام أكثر من كلاس للبحث عن البطاقات
    containers = [".anime-card-container", ".post-item", ".anime-card", "article", ".thumb"]
    items = []
    for c in containers:
        items = soup.select(c)
        if items: break # إذا وجدنا عناصر، نتوقف عن تجربة الباقي
        
    for item in items:
        # 3. محاولة استخدام أكثر من كلاس للعنوان
        title = ""
        for t in [".anime-card-title", "h2", "h3", "h3 a", "a.title"]:
            title_elem = item.select_one(t)
            if title_elem and title_elem.text.strip():
                title = title_elem.text.strip()
                break
                
        # 4. محاولة استخدام أكثر من كلاس للصورة
        poster = ""
        img_elem = item.select_one("img")
        if img_elem:
            poster = img_elem.get("src") or img_elem.get("data-src") or img_elem.get("data-lazy-src") or ""
            if poster.startswith("//"): poster = "https:" + poster
            
        # 5. محاولة استخدام أكثر من كلاس للرابط
        link = ""
        link_elem = item.select_one("a")
        if link_elem:
            link = link_elem.get("href", "")
            if link.startswith("/"): link = working_domain.rstrip("/") + link

        if title and poster:
            results.append({
                "title": title,
                "poster": poster,
                "url": link
            })

    # إذا لم يجد أي شيء، سيظهر لك في المتصفح عدد العناصر التي تم العثور عليها لتساعدنا في التشخيص
    if not results:
        return jsonify({"message": f"Found {len(items)} items but no title/poster.", "domain": working_domain})
        
    return jsonify(results)

# صفحة للتشخيص (إذا فشل كل شيء)
@app.route('/debug')
def debug():
    scraper = cloudscraper.create_scraper()
    try:
        res = scraper.get("https://witanime.com/", timeout=10)
        return f"Status: {res.status_code}<br><br>{res.text[:1000]}"
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)