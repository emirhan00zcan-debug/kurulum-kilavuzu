"""Kılavuzun ürün kartlarına mağazadaki (magaza.ozcanmobilya.com) ürün fotoğrafını koyar.
Kullanım: python magaza.py   (sonra python olustur.py)

magaza.json'daki eşleşme: kılavuzdaki ürün → mağaza adresinin son parçası (…/products/<bu kısım>).
Her ürünün mağazadaki ilk görseli (vitrinde, ürüne tıklamadan önce görünen) özgün boyutunda indirilir,
kareye ortalanıp img/<slug>/magaza.webp olarak kaydedilir; olustur.py varsa kartta bunu gösterir.
Mağazada karşılığı olmayan ürünlerin kartında SketchUp görseli kalır."""
import io
import json
import os
import urllib.request

from PIL import Image, ImageOps

from olustur import BURASI, IMG

BOY, KALITE = 1000, 86


def indir(adres):
    istek = urllib.request.Request(adres, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(istek, timeout=60) as yanit:
        return yanit.read()


def main():
    ayar = json.load(open(os.path.join(BURASI, 'magaza.json'), encoding='utf-8'))
    urunler = json.loads(indir(ayar['site'] + '/products.json?limit=250'))['products']
    ilk = {u['handle']: u['images'][0]['src'] for u in urunler if u['images']}
    for s, handle in ayar['eslesme'].items():
        if handle not in ilk:
            print(f'  ! {s}: mağazada "{handle}" yok ya da görseli yok')
            continue
        im = Image.open(io.BytesIO(indir(ilk[handle]))).convert('RGB')
        os.makedirs(os.path.join(IMG, s), exist_ok=True)
        ImageOps.fit(im, (BOY, BOY), Image.LANCZOS).save(os.path.join(IMG, s, 'magaza.webp'), 'WEBP',
                                                         quality=KALITE, method=6)
        print(f'{s} ← {handle} ({im.width}x{im.height})')
    kalan = sorted(set(ilk) - set(ayar['eslesme'].values()))
    if kalan:
        print('Mağazada olup kılavuzda eşleşmeyen: ' + ', '.join(kalan))


if __name__ == '__main__':
    main()
