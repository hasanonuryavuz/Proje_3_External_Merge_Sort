import csv
import heapq
import tempfile
import time
from contextlib import ExitStack
from pathlib import Path

CHUNK_SIZE = 10_000
INPUT_FILE = Path(__file__).resolve().parent / "girdi.csv"
OUTPUT_FILE = Path(__file__).resolve().parent / "sirali_sonuc.csv"
MERGE_FAN_IN = 64


def ornek_veri_olustur():
    if INPUT_FILE.exists():
        return

    import random
    rng = random.Random(42)

    with INPUT_FILE.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for _ in range(100_000):
            writer.writerow([rng.randint(1, 1_000_000)])


def parcalara_bol(klasor):
    if CHUNK_SIZE <= 0:
        raise ValueError("Blok boyutu pozitif olmalıdır.")
    dosyalar = []
    blok = []

    with INPUT_FILE.open("r", newline="", encoding="utf-8-sig") as f:
        for satir in csv.reader(f):
            if not satir:
                continue

            if len(satir) != 1:
                raise ValueError("CSV tek sütunda tam sayılar içermelidir.")
            blok.append(int(satir[0]))

            if len(blok) == CHUNK_SIZE:
                dosyalar.append(parca_kaydet(blok, klasor, len(dosyalar)))
                blok = []

    if blok:
        dosyalar.append(parca_kaydet(blok, klasor, len(dosyalar)))

    return dosyalar


def parca_kaydet(blok, klasor, indeks):
    blok.sort()
    yol = Path(klasor) / f"parca_{indeks}.csv"

    with yol.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for sayi in blok:
            writer.writerow([sayi])

    return yol


def satir_jeneratoru(dosya):
    for satir in csv.reader(dosya):
        if satir:
            yield int(satir[0])


def _grubu_birlestir(dosyalar, cikti):
    with ExitStack() as stack:
        akimlar = [
            satir_jeneratoru(stack.enter_context(
                Path(yol).open("r", newline="", encoding="utf-8")
            )) for yol in dosyalar
        ]
        with Path(cikti).open("w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerows((sayi,) for sayi in heapq.merge(*akimlar))


def birlestir(dosyalar, output_file=None):
    """Her adımda en fazla 64 girdi dosyası açarak birleştirir."""
    hedef = Path(output_file) if output_file is not None else OUTPUT_FILE
    with tempfile.TemporaryDirectory() as klasor:
        aktif = list(dosyalar)
        tur = 0
        while len(aktif) > MERGE_FAN_IN:
            sonraki = []
            for i in range(0, len(aktif), MERGE_FAN_IN):
                yol = Path(klasor) / f"tur_{tur}_{i}.csv"
                _grubu_birlestir(aktif[i:i + MERGE_FAN_IN], yol)
                sonraki.append(yol)
            # İlk parçaların sahibi çağıran fonksiyondur.
            if tur > 0:
                for yol in aktif:
                    yol.unlink()
            aktif = sonraki
            tur += 1
        _grubu_birlestir(aktif, hedef)


def external_sort(input_path, output_path, chunk_size):
    """Arayüzlerin ortak kullandığı, global ayarları değiştirmeyen API."""
    if not isinstance(chunk_size, int) or chunk_size <= 0:
        raise ValueError("Blok boyutu pozitif bir tam sayı olmalıdır.")
    start = time.perf_counter()
    row_count = 0
    with tempfile.TemporaryDirectory() as temp:
        chunks, block = [], []
        with Path(input_path).open("r", newline="", encoding="utf-8-sig") as f:
            for row in csv.reader(f):
                if not row:
                    continue
                if len(row) != 1:
                    raise ValueError("CSV tek sütunda tam sayılar içermelidir.")
                block.append(int(row[0]))
                row_count += 1
                if len(block) == chunk_size:
                    chunks.append(parca_kaydet(block, temp, len(chunks)))
                    block = []
        if block:
            chunks.append(parca_kaydet(block, temp, len(chunks)))
        birlestir(chunks, output_path)
    return {"rows": row_count, "parts": len(chunks),
            "seconds": round(time.perf_counter() - start, 3)}


def main():
    baslangic = time.perf_counter()
    ornek_veri_olustur()

    sonuc = external_sort(INPUT_FILE, OUTPUT_FILE, CHUNK_SIZE)
    print(f"Parca sayisi: {sonuc['parts']}")
    print(f"Toplam satir: {sonuc['rows']}")

    sure = time.perf_counter() - baslangic

    print(f"Girdi: {INPUT_FILE}")
    print(f"Cikti: {OUTPUT_FILE}")
    print(f"Sure: {sure:.3f} saniye")
    print("Gecici dosyalar temizlendi.")
    print("Siralama tamamlandi!")


if __name__ == "__main__":
    main()