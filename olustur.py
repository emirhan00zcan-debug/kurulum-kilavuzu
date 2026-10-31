"""Dijital kurulum kılavuzu verisini üretir: çıktılar/<Ürün>/NN[abc]_*.png karelerinden img/ (WebP) ve veri.js,
uygulama.html'den de index.html (GitHub Pages'te yayınlanan, bilgisayarda çift tıkla da açılan sayfa).
Kullanım: python olustur.py [çıktılar klasörü]

Adım başlıkları sırasıyla: <ürün klasörü>/liste.json (adim_gorselleri çıktısı), yoksa basliklar.json, yoksa 'Adım N'.
Yeni ürün eklemek için kareleri çıktılar'a koyup (liste.json ile birlikte) betiği yeniden çalıştırmak yeterli.
Kart görseli: img/<slug>/magaza.webp varsa (magaza.py ile mağazadan indirilen fotoğraf) o, yoksa son kareden üretilen.
klip/<slug>.mp4 ve .json varsa (klipler.py çıktısı) adımlar kılavuzda montaj animasyonuyla oynar; yoksa yalnız
görseller gösterilir."""
import datetime
import json
import os
import re
import sys

from PIL import Image, ImageOps

BURASI = os.path.dirname(os.path.abspath(__file__))
CIKTI = sys.argv[1] if len(sys.argv) > 1 else r'C:/Users/pc/OneDrive/Ekler/Masaüstü/çıktılar'
IMG = os.path.join(BURASI, 'img')
GEN, YUK, KALITE = 1600, 900, 82
KARE = re.compile(r'^(\d\d)([abc])?_\w+\.png$')
TR = str.maketrans('çğıİöşüÇĞÖŞÜ', 'cgiiosucgosu')


def slug(ad):
    return re.sub(r'[^a-z0-9]+', '-', ad.translate(TR).lower()).strip('-')


def guncel(kaynak, hedef):
    return os.path.exists(hedef) and os.path.getmtime(hedef) >= os.path.getmtime(kaynak)


def webp(kaynak, hedef):
    if not guncel(kaynak, hedef):
        Image.open(kaynak).convert('RGB').resize((GEN, YUK), Image.LANCZOS).save(hedef, 'WEBP', quality=KALITE, method=6)


def bant_sil(im):
    """adim_baslik.py'nin bastığı başlık bandını, hemen altındaki satırı yukarı uzatarak siler.
    Bandın sağ ucu, üst çerçeve çizgisi (208,210,214) soldan takip edilerek bulunur."""
    k = im.width / 1920
    x0, y0, h = int(54 * k), int(48 * k), int(70 * k)
    cerceve = lambda p: abs(p[0] - 208) < 20 and abs(p[2] - 214) < 20 and p[0] < 240 and abs(p[0] - p[1]) < 8
    x, bosluk = x0 + int(16 * k), 0
    while x < im.width - 1 and bosluk <= 2:
        bosluk = 0 if cerceve(im.getpixel((x, y0))) or cerceve(im.getpixel((x, y0 + 1))) else bosluk + 1
        x += 1
    a, b = max(0, x0 - 4), min(im.width, x + int(18 * k))
    alt = y0 + h + 4
    im.paste(im.crop((a, alt, b, alt + 1)).resize((b - a, alt - (y0 - 4))), (a, y0 - 4))
    return im


def kapak(kaynak, hedef, pay=40):
    """Bitmiş ürün karesinden kart görseli: başlık bandı silinir, beyaz kenarlar kırpılır, kareye ortalanır.
    Mağazada fotoğrafı olan üründe kart onu gösterir (magaza.py); bu görsel yalnız diğerleri için kullanılır."""
    if guncel(kaynak, hedef) and Image.open(hedef).size == (720, 720):
        return
    im = bant_sil(Image.open(kaynak).convert('RGB'))
    kutu = ImageOps.invert(im).point(lambda v: 255 if v > 12 else 0).getbbox()
    if kutu:
        x0, y0, x1, y1 = kutu
        im = im.crop((max(0, x0 - pay), max(0, y0 - pay), min(im.width, x1 + pay), min(im.height, y1 + pay)))
    g = max(im.width, im.height)
    zemin = Image.new('RGB', (g, g), 'white')
    zemin.paste(im, ((g - im.width) // 2, (g - im.height) // 2))
    zemin.resize((720, 720), Image.LANCZOS).save(hedef, 'WEBP', quality=KALITE, method=6)


def basliklar(klasor, urun, yedek):
    liste = os.path.join(klasor, 'liste.json')
    if os.path.exists(liste):
        b = {}
        for ad, baslik in json.load(open(liste, encoding='utf-8')):
            b.setdefault(int(ad[:2]), baslik)
        return b
    return dict(enumerate(yedek.get(urun, [])))


def ayir(baslik, n, son):
    """'N · metin' / 'Kutu içeriği — detay' / 'Kurulum tamamlandı — detay' başlığını parçalar."""
    if n == 0:
        tur = 'kutu'
    elif n == son:
        tur = 'son'
    else:
        tur = 'adim'
    if baslik is None:
        baslik = {'kutu': 'Kutu içeriği', 'son': 'Kurulum tamamlandı'}.get(tur, f'Adım {n}')
    m = re.match(r'^(\d+) · (.*)$', baslik)
    if m:
        baslik = m.group(2)
    ana, _, detay = baslik.partition(' — ') if tur != 'adim' else (baslik, '', '')
    return {'tur': tur, 'baslik': ana[:1].upper() + ana[1:], 'detay': detay}


def aletler(adimlar):
    metin = ' '.join(a['baslik'] + ' ' + a['detay'] for a in adimlar).lower()
    alyan = 'alyan' in metin
    a = []
    if (not alyan and re.search(r'vida|tornavida|minifi|rafix', metin)) or 'tornavida' in metin:
        a.append('Yıldız tornavida')
    if alyan:
        a.append('Alyan anahtarı (kutuda)')
    if re.search(r'çivi|çakın', metin):
        a.append('Çekiç')
    if 'dübel' in metin:
        a.append('Matkap ve dübel')
    return a


def main():
    yedek = json.load(open(os.path.join(BURASI, 'basliklar.json'), encoding='utf-8'))
    urunler = []
    adlar = [d for d in os.listdir(CIKTI) if os.path.isdir(os.path.join(CIKTI, d)) and not d.startswith(('_', 'pdf_'))]
    for urun in sorted(adlar, key=lambda d: d.translate(TR).lower()):
        klasor = os.path.join(CIKTI, urun)
        kareler = {}
        for f in os.listdir(klasor):
            m = KARE.match(f)
            if m:
                kareler.setdefault(int(m.group(1)), {})[m.group(2) or 'k'] = f
        if len(kareler) < 2:
            continue
        s = slug(urun)
        os.makedirs(os.path.join(IMG, s), exist_ok=True)
        bas = basliklar(klasor, urun, yedek)
        son = max(kareler)
        klip_json = os.path.join(BURASI, 'klip', s + '.json')
        klip = json.load(open(klip_json, encoding='utf-8')) if os.path.exists(klip_json) else {'adimlar': []}
        araliklar = {k['no']: k for k in klip['adimlar']}
        if araliklar and len(araliklar) != len(kareler):
            print(f'  ! {urun}: animasyonda {len(araliklar)} adım var ama {len(kareler)} adım görseli; animasyon kullanılmadı')
            araliklar = {}
        adimlar = []
        for n in sorted(kareler):
            a = ayir(bas.get(n), n, son)
            a['no'] = n
            if n in araliklar:
                a['klip'] = {'bas': araliklar[n]['bas'], 'son': araliklar[n]['son']}
            a['kareler'] = []
            for tur in 'kabc':
                if tur in kareler[n]:
                    ad = f'{n:02d}{"" if tur == "k" else tur}.webp'
                    webp(os.path.join(klasor, kareler[n][tur]), os.path.join(IMG, s, ad))
                    a['kareler'].append({'tur': tur, 'src': f'img/{s}/{ad}'})
            adimlar.append(a)
        son_kare = kareler[son].get('c') or next(iter(kareler[son].values()))
        kapak(os.path.join(klasor, son_kare), os.path.join(IMG, s, 'kapak.webp'))
        foto = os.path.exists(os.path.join(IMG, s, 'magaza.webp'))
        eksik = sum(1 for n in kareler if n not in bas)
        u = {'slug': s, 'ad': urun, 'kapak': f'img/{s}/{"magaza" if foto else "kapak"}.webp', 'aletler': aletler(adimlar),
             'adimlar': adimlar}
        if araliklar:
            u['video'], u['fps'] = f'klip/{s}.mp4', klip['fps']
        urunler.append(u)
        print(f'{urun}: {son - 1} adım, {sum(len(a["kareler"]) for a in adimlar)} kare'
              + (', animasyonlu' if araliklar else '') + (f'  (! {eksik} adımın başlığı yok)' if eksik else ''))

    veri = {'tarih': datetime.date.today().strftime('%d.%m.%Y'), 'urunler': urunler}
    with open(os.path.join(BURASI, 'veri.js'), 'w', encoding='utf-8') as f:
        f.write('window.KILAVUZ = ' + json.dumps(veri, ensure_ascii=False, separators=(',', ':')) + ';\n')

    # Yerelde çift tıkla açılan sürüm: artifact iskeletini uygulama.html'in başına ekler.
    govde = open(os.path.join(BURASI, 'uygulama.html'), encoding='utf-8').read()
    iskelet = ('<!doctype html>\n<html lang="tr">\n<head>\n<meta charset="utf-8">\n'
               '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
               '<style>html{color-scheme:light}body{margin:0;font:14px system-ui,sans-serif}img{max-width:100%}'
               '[hidden]{display:none!important}</style>\n</head>\n<body>\n')
    with open(os.path.join(BURASI, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(iskelet + govde + '\n</body>\n</html>\n')
    print(f'{len(urunler)} ürün → veri.js, img/, index.html')


if __name__ == '__main__':
    main()
