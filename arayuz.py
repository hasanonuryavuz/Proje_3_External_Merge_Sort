import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
import csv
from pathlib import Path

import main as sorter

BG = "#101827"
CARD = "#1E293B"
FG = "#F8FAFC"
MUTED = "#94A3B8"
ACCENT = "#6366F1"

root = tk.Tk()
root.title("PROJE 3 - External Merge Sort")
root.geometry("780x630")
root.configure(bg=BG)

dosya_var = tk.StringVar(value=str(sorter.INPUT_FILE))
blok_var = tk.StringVar(value="10000")
durum_var = tk.StringVar(value="Hazir")
parca_var = tk.StringVar(value="-")
sure_var = tk.StringVar(value="-")
kayit_var = tk.StringVar(value="-")


def etiket(parent, yazi, boyut=12, renk=FG):
    return tk.Label(
        parent, text=yazi, font=("Segoe UI", boyut),
        fg=renk, bg=parent["bg"]
    )


def dosya_sec():
    yol = filedialog.askopenfilename(
        title="CSV dosyasi sec",
        filetypes=[("CSV Dosyalari", "*.csv")]
    )
    if yol:
        dosya_var.set(yol)


def islemi_baslat():
    try:
        blok = int(blok_var.get())
        if blok <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Hata", "Pozitif bir blok boyutu girin.")
        return

    giris = Path(dosya_var.get())

    if not giris.exists():
        messagebox.showerror("Hata", "Girdi dosyasi bulunamadi.")
        return

    baslat_btn.config(state="disabled")
    durum_var.set("Siralama devam ediyor...")
    progress.start(12)

    def islem():
        try:
            sonuc = sorter.external_sort(giris, sorter.OUTPUT_FILE, blok)
            toplam = sonuc["parts"]
            sure = sonuc["seconds"]
            satir_sayisi = sonuc["rows"]

            def tamamla():
                parca_var.set(str(toplam))
                sure_var.set(f"{sure:.3f} saniye")
                kayit_var.set(f"{satir_sayisi:,}")
                durum_var.set("Siralama tamamlandi!")
                progress.stop()
                baslat_btn.config(state="normal")
                messagebox.showinfo(
                    "Basarili",
                    f"Cikti olusturuldu:\n{sorter.OUTPUT_FILE}"
                )

            root.after(0, tamamla)

        except Exception as hata:
            mesaj = str(hata)

            def hata_goster():
                progress.stop()
                baslat_btn.config(state="normal")
                durum_var.set("Hata olustu")
                messagebox.showerror("Hata", mesaj)

            root.after(0, hata_goster)

    threading.Thread(target=islem, daemon=True).start()


# BASLIK
header = tk.Frame(root, bg=BG)
header.pack(fill="x", padx=35, pady=(28, 12))

etiket(header, "PROJE 3  |  PYTHON", 11, "#A5B4FC").pack(anchor="w")
etiket(header, "External Merge Sort", 25).pack(anchor="w")
etiket(
    header, "Buyuk Dosya Siralama Yoneticisi", 12, MUTED
).pack(anchor="w")


# DOSYA VE AYARLAR
panel = tk.Frame(root, bg=CARD, padx=22, pady=20)
panel.pack(fill="x", padx=35, pady=15)

etiket(panel, "Girdi CSV Dosyasi", 12).pack(anchor="w")

dosya_satiri = tk.Frame(panel, bg=CARD)
dosya_satiri.pack(fill="x", pady=10)

tk.Entry(
    dosya_satiri, textvariable=dosya_var,
    font=("Segoe UI", 10), width=60
).pack(side="left", fill="x", expand=True)

tk.Button(
    dosya_satiri, text="Dosya Sec",
    command=dosya_sec, padx=12
).pack(side="left", padx=8)

etiket(panel, "Blok Boyutu (Satir)", 12).pack(
    anchor="w", pady=(12, 5)
)

tk.Entry(
    panel, textvariable=blok_var,
    font=("Segoe UI", 12), width=15
).pack(anchor="w")


# BASLAT
baslat_btn = tk.Button(
    root, text="▶  SIRALAMAYI BASLAT",
    command=islemi_baslat,
    bg=ACCENT, fg="white",
    font=("Segoe UI", 14, "bold"),
    relief="flat", pady=12,
    cursor="hand2"
)
baslat_btn.pack(fill="x", padx=35, pady=15)

progress = ttk.Progressbar(root, mode="indeterminate")
progress.pack(fill="x", padx=35, pady=5)


# ISTATISTIKLER
stats = tk.Frame(root, bg=BG)
stats.pack(fill="x", padx=35, pady=15)


def istatistik(baslik, degisken):
    kutu = tk.Frame(stats, bg=CARD, padx=18, pady=15)
    kutu.pack(side="left", fill="both", expand=True, padx=5)

    etiket(kutu, baslik, 10, MUTED).pack(anchor="w")
    tk.Label(
        kutu, textvariable=degisken,
        font=("Segoe UI", 17, "bold"),
        fg=FG, bg=CARD
    ).pack(anchor="w", pady=6)


istatistik("PARCA SAYISI", parca_var)
istatistik("ISLEM SURESI", sure_var)
istatistik("TOPLAM SATIR", kayit_var)


# DURUM
etiket(root, "Islem Durumu", 12, MUTED).pack(
    anchor="w", padx=40
)

tk.Label(
    root, textvariable=durum_var,
    font=("Segoe UI", 13, "bold"),
    fg="#4ADE80", bg=BG
).pack(anchor="w", padx=40, pady=8)

root.mainloop()