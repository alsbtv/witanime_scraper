from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/latest-episodes')
def latest_episodes():
    try:
        url = "https://witanime.com/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        results = []
        # المحددات الصحيحة للموقع
        cards = soup.select('.anime-card-container')
        for card in cards:
            title_elem = card.select_one('.anime-card-title')
            img_elem = card.select_one('img')
            link_elem = card.select_one('a')
            
            if title_elem and img_elem:
                title = title_elem.text.strip()
                img = img_elem.get('src') or img_elem.get('data-src') or ''
                if img.startswith('//'): img = 'https:' + img
                link = link_elem.get('href') if link_elem else ''
                
                results.append({
                    "title": title,
                    "poster": img,
                    "url": link
                })
        
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
