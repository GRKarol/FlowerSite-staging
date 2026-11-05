#!/usr/bin/env python3
"""Karty z kodem rabatowym do pudełka (90 x 55 mm, ze spadem 3 mm).

Użycie:
  python3 karty/generuj.py                 # trzy próbne karty (10%, 5%, 25 zł)
  python3 karty/generuj.py kody.csv        # po jednej karcie na każdy kod z pliku CSV

Plik CSV ma kolumny: kod,rabat   (rabat: "10%", "5%" albo "25 zł"), np.
  FLWR-7KQ2-M9,10%
  FLWR-25ZL-AB,25 zł

Wynik: karty/wydruk/<kod>-awers.html i -rewers.html. Do PDF i PNG: node karty/render.cjs
Potrzebne: pip install qrcode
"""
import base64, csv, io, pathlib, sys
import qrcode, qrcode.image.svg

ROOT = pathlib.Path(__file__).resolve().parent
OUT = ROOT / "wydruk"
SITE = "https://flower-device.com"          # po zmianie domeny wpisz tu nową

LOGO = base64.b64encode((ROOT.parent / "logo-seed.png").read_bytes()).decode()


def qr_svg(url: str) -> str:
    q = qrcode.QRCode(border=0, error_correction=qrcode.constants.ERROR_CORRECT_M)
    q.add_data(url); q.make(fit=True)
    img = q.make_image(image_factory=qrcode.image.svg.SvgPathImage)
    buf = io.BytesIO(); img.save(buf)
    svg = buf.getvalue().decode()
    return svg[svg.index("<svg"):]


CSS = """
@page{size:96mm 61mm;margin:0}
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:96mm;height:61mm}
body{font-family:'Newsreader',Georgia,serif;color:#1A1A1A;-webkit-print-color-adjust:exact;print-color-adjust:exact}
.sheet{position:relative;width:96mm;height:61mm;overflow:hidden}
.trim{position:absolute;left:3mm;top:3mm;width:90mm;height:55mm}
.mono{font-family:'JetBrains Mono',ui-monospace,monospace}
.fr{font-family:'Fraunces',Georgia,serif;font-variation-settings:"opsz" 144}
/* front */
.front{background:#F4F1EA}
.front .seed{position:absolute;opacity:.07;width:22mm}
.front .brand{position:absolute;left:6mm;top:5.5mm;display:flex;align-items:center;gap:2mm}
.front .brand img{width:7mm;height:7mm}
.front .brand span{font-size:12pt;font-weight:340;letter-spacing:-.03em}
.front .lbl{position:absolute;left:6mm;top:16.6mm;font-size:5.6pt;letter-spacing:.14em;text-transform:uppercase;color:#5E5A52}
.front .big{position:absolute;left:5.4mm;top:18.9mm;font-size:35pt;font-weight:300;font-style:italic;letter-spacing:-.045em;line-height:1}
.front .big small{font-size:14pt;font-style:normal;letter-spacing:-.02em;font-weight:340}
.front .sub{position:absolute;left:6mm;top:32.6mm;font-size:7.8pt;color:#3A3730;line-height:1.3}
.front .code{position:absolute;left:6mm;bottom:4.6mm;font-size:9pt;letter-spacing:.06em;padding:1.5mm 2.4mm;border:.25mm solid #1A1A1A;border-radius:1.6mm}
.front .qr{position:absolute;right:6mm;bottom:5.4mm;width:19mm;height:19mm;background:#fff;padding:1.4mm;border-radius:1.6mm}
.front .qr svg{width:100%;height:100%;display:block}
.front .qrn{position:absolute;right:6mm;top:23.4mm;text-align:right;font-size:5.6pt;letter-spacing:.14em;text-transform:uppercase;color:#5E5A52;line-height:1.5}
/* back */
.back{background:#1488D8;color:#F4F1EA}
.back .seed{position:absolute;filter:invert(1);opacity:.9}
.back .line{position:absolute;left:6mm;bottom:5.5mm;font-size:15pt;font-style:italic;font-weight:300;letter-spacing:-.03em;line-height:1.06;width:50mm}
.back .web{position:absolute;right:6mm;bottom:5.8mm;font-size:6.4pt;letter-spacing:.08em;opacity:.92}
.back .word{position:absolute;left:6mm;top:5.5mm;font-size:12pt;font-weight:340;letter-spacing:-.03em}
"""

HEAD = """<!doctype html><html lang="pl"><head><meta charset="utf-8"><title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300..500;1,9..144,300..500&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,400&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>{css}</style></head><body>"""


def front(code: str, rabat: str) -> str:
    url = f"{SITE}/?kod={code}"
    if rabat.endswith("%"):
        big = f"&minus;{rabat[:-1]}<small>%</small>"
    else:
        num, unit = rabat.split(" ", 1)
        big = f"&minus;{num}<small>&nbsp;{unit}</small>"
    seeds = "".join(
        f'<img class="seed" src="data:image/png;base64,{LOGO}" style="left:{x}mm;top:{y}mm;transform:rotate({r}deg);width:{w}mm" alt="">'
        for x, y, r, w in ((52, -6, 24, 24), (73, 8, -18, 12))
    )
    return (HEAD.format(title=f"flower {code} awers", css=CSS) +
        f'<div class="sheet front"><div class="trim">{seeds}'
        f'<div class="brand"><img src="data:image/png;base64,{LOGO}" alt=""><span class="fr">flower</span></div>'
        f'<div class="lbl mono">Rabat na flowera</div>'
        f'<div class="big fr">{big}</div>'
        f'<div class="sub">Jeden raz, ważny 12 miesięcy.<br>Dla ciebie albo dla kogoś, kto lubi czytać.</div>'
        f'<div class="code mono">{code}</div>'
        f'<div class="qrn mono">Zeskanuj<br>kod QR</div>'
        f'<div class="qr">{qr_svg(url)}</div>'
        f'</div></div></body></html>')


def back() -> str:
    seeds = "".join(
        f'<img class="seed" src="data:image/png;base64,{LOGO}" style="left:{x}mm;top:{y}mm;transform:rotate({r}deg);width:{w}mm;opacity:{o}" alt="">'
        for x, y, r, w, o in ((48, 4, 18, 30, .95), (70, 24, -22, 17, .55), (36, 32, 44, 11, .4), (82, 5, 60, 9, .35))
    )
    return (HEAD.format(title="flower awers", css=CSS).replace("awers", "rewers") +
        f'<div class="sheet back"><div class="trim">{seeds}'
        f'<div class="word fr">flower</div>'
        f'<div class="line fr">Każda chwila może być rozdziałem.</div>'
        f'<div class="web mono">{SITE.replace("https://", "")}</div>'
        f'</div></div></body></html>')


def main():
    OUT.mkdir(exist_ok=True)
    if len(sys.argv) > 1:
        rows = [(r[0].strip(), r[1].strip()) for r in csv.reader(open(sys.argv[1], encoding="utf-8")) if r and r[0].strip()]
    else:
        rows = [("FLWR-7KQ2-M9", "10%"), ("FLWR-5XNB-4D", "5%"), ("FLWR-25ZL-AB", "25 zł")]
    for code, rabat in rows:
        (OUT / f"{code}-awers.html").write_text(front(code, rabat), encoding="utf-8")
    (OUT / "rewers.html").write_text(back(), encoding="utf-8")
    print(f"{len(rows)} kart, rewers wspólny -> {OUT}")


if __name__ == "__main__":
    main()
