"""Her ürünün kurulum sayfası için QR kod üretir (kutu etiketi, broşür).
Kullanım: python qr.py [site adresi]   (önce olustur.py çalışmış olmalı)

Çıktı qr/ klasörüne: <slug>.svg (baskı için, saf siyah), <slug>.png (altında ürün adı yazan etiket)
ve index.html (hepsini A4'e dizen baskı sayfası). QR, sitenin <adres>#<slug> sayfasını açar."""
import html
import io
import json
import os
import sys

import segno
from PIL import Image, ImageDraw, ImageFont

from olustur import BURASI

SITE = sys.argv[1] if len(sys.argv) > 1 else 'https://emirhan00zcan-debug.github.io/kurulum-kilavuzu/'
QR = os.path.join(BURASI, 'qr')
KALIN = 'C:/Windows/Fonts/segoeuib.ttf'
NORMAL = 'C:/Windows/Fonts/segoeui.ttf'
KOYU = (18, 39, 45)


def etiket(qr, ad, adres, hedef):
    """QR + ürün adı + adres; kutu üstüne basılacak 1000 px genişlikte PNG."""
    b = io.BytesIO()
    qr.save(b, kind='png', scale=24, border=0)
    kod = Image.open(b).convert('RGB')
    kod = kod.resize((760, 760), Image.NEAREST)
    im = Image.new('RGB', (1000, 1180), 'white')
    im.paste(kod, (120, 90))
    d = ImageDraw.Draw(im)
    boy = 64
    while d.textlength(ad, font=ImageFont.truetype(KALIN, boy)) > 900 and boy > 30:
        boy -= 2
    d.text((500, 920), ad, font=ImageFont.truetype(KALIN, boy), fill=KOYU, anchor='mm')
    d.text((500, 1000), 'Kurulum kılavuzu · telefonla okutun', font=ImageFont.truetype(NORMAL, 36), fill=(85, 105, 110),
           anchor='mm')
    d.text((500, 1070), adres.replace('https://', ''), font=ImageFont.truetype(NORMAL, 24), fill=(120, 135, 140),
           anchor='mm')
    im.save(hedef, optimize=True)


def main():
    s = open(os.path.join(BURASI, 'veri.js'), encoding='utf-8').read()
    urunler = json.loads(s[s.index('=') + 1:].strip().rstrip(';'))['urunler']
    os.makedirs(QR, exist_ok=True)
    kartlar = []
    for u in urunler:
        adres = SITE + '#' + u['slug']
        qr = segno.make_qr(adres, error='q')
        qr.save(os.path.join(QR, u['slug'] + '.svg'), scale=10, border=0, dark='#000')
        etiket(qr, u['ad'], adres, os.path.join(QR, u['slug'] + '.png'))
        kartlar.append(f'<figure><img src="{u["slug"]}.svg" alt="{html.escape(u["ad"])} QR kodu">'
                       f'<figcaption><b>{html.escape(u["ad"])}</b><a href="{adres}">{html.escape(adres.replace("https://", ""))}</a>'
                       f'<a class="png" href="{u["slug"]}.png" download>PNG etiket</a></figcaption></figure>')
        print(f'{u["ad"]}: {adres}')
    sayfa = f'''<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Kurulum QR Kodları · Özcan Mobilya</title>
<style>
  :root {{ --murekkep: #12272D; --soluk: #55696E; --cizgi: #D4DDDE; --zemin: #F1F4F4; --marka: #00495A; }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; background: var(--zemin); color: var(--murekkep); font: 15px/1.45 'Segoe UI', system-ui, sans-serif;
         padding: 24px max(16px, env(safe-area-inset-left, 0px)); }}
  header {{ max-width: 1100px; margin: 0 auto 20px; display: flex; flex-wrap: wrap; gap: 8px 24px; align-items: end; justify-content: space-between; }}
  h1 {{ margin: 0; font-size: 28px; }}
  header p {{ margin: 4px 0 0; color: var(--soluk); max-width: 60ch; }}
  header button {{ font: inherit; font-weight: 600; padding: 10px 18px; border-radius: 999px; border: 0; background: var(--marka); color: #fff; cursor: pointer; }}
  main {{ max-width: 1100px; margin: 0 auto; display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 220px), 1fr)); gap: 14px; }}
  figure {{ margin: 0; background: #fff; border: 1px solid var(--cizgi); border-radius: 10px; padding: 18px 16px 14px; text-align: center; break-inside: avoid; }}
  figure img {{ width: 100%; max-width: 180px; aspect-ratio: 1; image-rendering: pixelated; }}
  figcaption {{ display: grid; gap: 2px; margin-top: 10px; }}
  figcaption b {{ font-size: 16px; }}
  figcaption a {{ color: var(--soluk); font-size: 12px; word-break: break-all; text-decoration: none; }}
  figcaption a.png {{ color: var(--marka); font-weight: 600; margin-top: 4px; }}
  @media print {{
    @page {{ size: A4; margin: 12mm; }}
    body {{ background: #fff; padding: 0; }}
    header p, header button, a.png {{ display: none; }}
    main {{ grid-template-columns: repeat(3, 1fr); gap: 8mm; }}
    figure {{ border-color: #bbb; }}
  }}
</style>
</head>
<body>
<header>
  <div>
    <h1>Kurulum QR kodları</h1>
    <p>Her kod, ürünün kurulum kılavuzunu telefonda açar. Kutu etiketine ya da broşüre basın; kodun kenarında en az 4 mm boşluk bırakın, kenar uzunluğu 2 cm'den küçük olmasın.</p>
  </div>
  <button type="button" onclick="print()">Yazdır</button>
</header>
<main>
{chr(10).join(kartlar)}
</main>
</body>
</html>
'''
    open(os.path.join(QR, 'index.html'), 'w', encoding='utf-8').write(sayfa)
    print(f'{len(urunler)} QR → qr/')


if __name__ == '__main__':
    main()
