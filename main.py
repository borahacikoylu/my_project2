
import time
import re
import requests as req
import sqlite3
import math
from datetime import datetime

magaza = input("Mağaza ID giriniz: ")

response = req.get("https://www.trendyol.com/sr?mid=" + magaza)
html_content = response.text
pattern = r'(\d+) sonuç'
matches = re.search(pattern, html_content)

sayfa_sayisi = math.ceil(int(matches.group(1)) / 24)

for a in range(1, sayfa_sayisi + 1):
    time.sleep(0.5)
    a = str(a)
    request = req.get("https://www.trendyol.com/sr?mid=" + magaza + "&os=1&pi=" + a)
    html_content = request.text

    pattern_basliklar = r'<span class="prdct-desc-cntnr-name(?: hasRatings)?" title="[^"]+">([^<]+)</span>'
    
    pattern_fiyat = r'<div class="prc-box-dscntd">([^<]+ TL)</div>(?!</span>)'



    pattern_linkler = r'<div class="p-card-chldrn-cntnr card-border".*?><a\s+href="([^"]+)"'

    basliklar = re.findall(pattern_basliklar, html_content)
    fiyatlar = re.findall(pattern_fiyat, html_content)
    linkler = re.findall(pattern_linkler, html_content)
    
    
   
    for i in range(len(linkler)):
        linkler[i] = "https://www.trendyol.com/pd" + linkler[i]

    if len(basliklar) != len(fiyatlar) or len(basliklar) != len(linkler):
        print("Hata! Veri sayıları eşleşmiyor.")
        break

    vt = sqlite3.connect("trendyol.db")
    im = vt.cursor()
    im.execute("CREATE TABLE IF NOT EXISTS urunler (satici_id TEXT, urun_adi TEXT, urun_fiyati TEXT, urun_linki TEXT, duzenlenme_saati TEXT)")

    for i in range(len(basliklar)):
        im.execute("SELECT * FROM urunler WHERE satici_id = ? AND urun_adi = ? AND urun_fiyati = ? AND urun_linki = ?", (magaza, basliklar[i], fiyatlar[i], linkler[i]))
        existing_data = im.fetchone()
        
        if existing_data:
            im.execute("UPDATE urunler SET duzenlenme_saati = ? WHERE satici_id = ? AND urun_adi = ? AND urun_fiyati = ? AND urun_linki = ?", (datetime.now().strftime("%m-%d %H:%M"), magaza, basliklar[i], fiyatlar[i], linkler[i]))
        else:
            im.execute("INSERT INTO urunler VALUES (?,?,?,?,?)", (magaza, basliklar[i], fiyatlar[i], linkler[i], datetime.now().strftime("%m-%d %H:%M")))
    
    vt.commit()

print("Veriler başarıyla işlendi...")



    





