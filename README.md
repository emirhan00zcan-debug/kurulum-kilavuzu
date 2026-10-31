# Özcan Mobilya · Dijital Kurulum Kılavuzu

Ürünlerin kurulumunu adım adım gösteren web sayfası. Her adımda SketchUp'taki montaj animasyonu oynar
(parça yerine gider, vida sıkılır); adımın işlem, yakın çekim ve sonuç görselleri de sekmelerde durur.

- Site: https://emirhan00zcan-debug.github.io/kurulum-kilavuzu/
- Ürün sayfası: `…/kurulum-kilavuzu/#<ürün>` (ör. `#kahve-kosesi`, `#konsol.4` = 4. adım)
- QR kodları ve baskı sayfası: https://emirhan00zcan-debug.github.io/kurulum-kilavuzu/qr/

## Yeni ürün eklemek / güncellemek

1. SketchUp kurulum motoruyla adım görselleri `çıktılar/<Ürün>/` klasörüne alınır (`NN[abc]_*.png` + `liste.json`).
2. Animasyon kareleri alınır: ürünün `.rb` dosyası yüklüyken
   `OzcanKurulum::<Modül>.kaydet('C:/kareler/<ürün>', fps: 20, gen: 960, yuk: 540)`
3. Video: `python klipler.py C:/kareler/<ürün> "<Ürün adı>"`
4. Ürün mağazada satılıyorsa kart fotoğrafı: `magaza.json`'a `"<ürün>": "<mağaza adresinin son parçası>"`
   satırını ekleyip `python magaza.py` (magaza.ozcanmobilya.com/products/**bu-kısım**). Eklenmezse kartta SketchUp görseli kalır.
5. Sayfa verisi: `python olustur.py`, QR kodları: `python qr.py`
6. `git add -A && git commit -m "..." && git push` — GitHub Pages bir iki dakikada güncellenir.

## Dosyalar

| Dosya | Ne işe yarar |
|---|---|
| `uygulama.html` | Sayfanın kaynağı (tasarım ve oynatıcı) |
| `olustur.py` | `çıktılar/` görsellerinden `img/`, `veri.js` ve `index.html` üretir |
| `klipler.py` | Animasyon karelerinden `klip/<ürün>.mp4` ve adım aralıklarını üretir |
| `magaza.py` | `magaza.json` eşleşmesine göre mağazadaki ürün fotoğrafını kart görseli olarak indirir |
| `qr.py` | `qr/` klasörüne ürün QR kodlarını ve baskı sayfasını üretir |
| `basliklar.json` | `liste.json`'u olmayan ürünlerin adım başlıkları |
