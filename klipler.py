"""SketchUp montaj animasyonu karelerinden ürün başına tek MP4 üretir; kılavuz 'İleri'ye basınca yalnız o adımın
aralığını oynatıp adım sonunda durur. Adım başlarına anahtar kare konur, böylece her adıma anında atlanır.
Kullanım: python klipler.py <kare klasörü> "<Ürün adı>" [--fps 20]

Kareler SketchUp'ta kurulum motoruyla alınır (ürünün .rb dosyası yüklü, model kurulmuş):
    OzcanKurulum::<Modül>.kaydet('C:/kareler/<ürün>', fps: 20, gen: 960, yuk: 540)
Klasördeki basliklar.json her adımın başlangıç saniyesini verir. Çıktı: klip/<slug>.mp4 ve klip/<slug>.json
(adım aralıkları). Ardından olustur.py'yi çalıştırın."""
import argparse
import glob
import json
import os
import shutil
import subprocess

from olustur import BURASI, slug

FFMPEG = shutil.which('ffmpeg') or 'ffmpeg'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('kareler')
    ap.add_argument('urun')
    ap.add_argument('--fps', type=int, default=20)
    a = ap.parse_args()

    basliklar = json.load(open(os.path.join(a.kareler, 'basliklar.json'), encoding='utf-8'))
    toplam = len(glob.glob(os.path.join(a.kareler, 'f[0-9]*.png')))
    # Adım sınırları kare numarasına yuvarlanır; zaman = kare / fps (anahtar kare tam bu karelere düşer).
    sinir = [round(t * a.fps) for t, _ in basliklar] + [toplam]
    adimlar = [{'no': n, 'baslik': b, 'bas': sinir[n] / a.fps, 'son': max(sinir[n + 1], sinir[n] + 1) / a.fps}
               for n, (_, b) in enumerate(basliklar)]
    os.makedirs(os.path.join(BURASI, 'klip'), exist_ok=True)
    hedef = os.path.join(BURASI, 'klip', slug(a.urun))
    anahtar = ','.join(f'{x["bas"]:.3f}' for x in adimlar)
    subprocess.run([FFMPEG, '-nostdin', '-y', '-loglevel', 'error', '-framerate', str(a.fps),
                    '-i', os.path.join(a.kareler, 'f%05d.png'), '-c:v', 'libx264', '-preset', 'slow', '-crf', '25',
                    '-pix_fmt', 'yuv420p', '-g', str(2 * a.fps), '-force_key_frames', anahtar,
                    '-movflags', '+faststart', '-an', hedef + '.mp4'], check=True)
    json.dump({'fps': a.fps, 'adimlar': adimlar}, open(hedef + '.json', 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print(f'{a.urun}: {len(adimlar)} adım, {toplam / a.fps:.0f} sn, {os.path.getsize(hedef + ".mp4") / 1e6:.1f} MB')


if __name__ == '__main__':
    main()
