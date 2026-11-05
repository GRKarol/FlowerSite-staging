#!/usr/bin/env python3
"""Karty z kodem do pudełka flowera (90 x 55 mm, ze spadem 3 mm).

Użycie:
  python3 karty/generuj.py              # trzy próbne karty (10%, 5%, 25 zł)
  python3 karty/generuj.py kody.csv     # po jednej karcie na kod z pliku CSV

CSV: kolumny kod,rabat  (rabat: "10%", "5%" albo "25 zł"), np.
  FLWR-7KQ2-M9,10%
  FLWR-25ZL-AB,25 zł

Wynik: karty/wydruk/<kod>-awers.html oraz rewers.html. PDF i PNG: node karty/render.cjs
Potrzebne: pip install qrcode
"""
import base64, csv, io, pathlib, sys
import qrcode, qrcode.image.svg

ROOT = pathlib.Path(__file__).resolve().parent
OUT = ROOT / "wydruk"
SITE = "https://flower-device.com"          # po zmianie domeny wpisz tu nową
LOGO = base64.b64encode((ROOT.parent / "logo-seed.png").read_bytes()).decode()


def qr_svg(url):
    q = qrcode.QRCode(border=0, error_correction=qrcode.constants.ERROR_CORRECT_M)
    q.add_data(url); q.make(fit=True)
    img = q.make_image(image_factory=qrcode.image.svg.SvgPathImage)
    buf = io.BytesIO(); img.save(buf)
    svg = buf.getvalue().decode()
    return svg[svg.index("<svg"):]


def seed(x, y, w, rot, op=1, white=False):
    f = "filter:invert(1);" if white else ""
    return (f'<img class="seed" src="data:image/png;base64,{LOGO}" alt="" '
            f'style="{f}left:{x}mm;top:{y}mm;width:{w}mm;opacity:{op};transform:rotate({rot}deg)">')


CSS = """
@page{size:96mm 61mm;margin:0}
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:96mm;height:61mm}
body{font-family:'Newsreader',Georgia,serif;color:#1A1A1A;-webkit-print-color-adjust:exact;print-color-adjust:exact}
.sheet{position:relative;width:96mm;height:61mm;overflow:hidden}
.trim{position:absolute;left:3mm;top:3mm;width:90mm;height:55mm}
.seed{position:absolute}
.mono{font-family:'JetBrains Mono',ui-monospace,monospace}
.fr{font-family:'Fraunces',Georgia,serif;font-variation-settings:"opsz" 144}
.front{background:#F4F1EA}
.front .brand{position:absolute;left:6mm;top:5mm;display:flex;align-items:center;gap:1.8mm}
.front .brand img{width:6mm;height:6mm}
.front .brand span{font-size:10.5pt;font-weight:340;letter-spacing:-.03em}
.front .tag{position:absolute;right:6mm;top:6.4mm;font-size:5.4pt;letter-spacing:.16em;text-transform:uppercase;color:#5E5A52}
.front h1{position:absolute;left:6mm;top:13.6mm;font-size:21pt;font-weight:300;font-style:italic;letter-spacing:-.04em;line-height:1}
.front p{position:absolute;left:6mm;top:23.6mm;width:53mm;font-size:7.9pt;line-height:1.36;color:#2B2924}
.front p b{font-weight:500;font-style:italic;color:#0F6CB0}
.front .how{position:absolute;left:6mm;bottom:4.6mm;width:52mm;font-size:5.4pt;letter-spacing:.04em;color:#5E5A52;line-height:1.55}
.front .qr{position:absolute;right:6mm;top:20.4mm;width:20mm;height:20mm;background:#fff;padding:1.5mm;border-radius:1.8mm}
.front .qr svg{width:100%;height:100%;display:block}
.front .code{position:absolute;right:6mm;top:43mm;width:20mm;text-align:center;font-size:6.6pt;letter-spacing:.04em;padding:1.2mm 0;border:.25mm solid #1A1A1A;border-radius:1.4mm;white-space:nowrap}
.back{background:#1488D8;color:#F4F1EA}
.back .word{position:absolute;left:6mm;top:5mm;font-size:10.5pt;font-weight:340;letter-spacing:-.03em}
.back h1{position:absolute;left:6mm;top:15mm;font-size:25pt;font-weight:300;font-style:italic;letter-spacing:-.045em;line-height:.98;width:50mm}
.back .write{position:absolute;left:6mm;top:40mm;width:46mm;border-bottom:.3mm solid rgba(244,241,234,.85)}
.back .write span{position:absolute;left:0;top:2mm;font-size:5.5pt;letter-spacing:.14em;text-transform:uppercase;opacity:.85}
.back .web{position:absolute;right:6mm;bottom:5.2mm;font-size:6pt;letter-spacing:.08em;opacity:.9}
"""

HEAD = """<!doctype html><html lang="pl"><head><meta charset="utf-8"><title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300..500;1,9..144,300..500&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,400&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>{css}</style></head><body>"""


def front(code, rabat):
    taniej = f"o&nbsp;{rabat[:-1]}%&nbsp;taniej" if rabat.endswith("%") else "o&nbsp;" + rabat.replace(" ", "&nbsp;") + "&nbsp;taniej"
    seeds = seed(55, -7, 27, 24, .07) + seed(73, 31, 12, -22, .07)
    return (HEAD.format(title=f"flower {code} awers", css=CSS) +
        f'<div class="sheet front"><div class="trim">{seeds}'
        f'<div class="brand"><img src="data:image/png;base64,{LOGO}" alt=""><span class="fr">flower</span></div>'
        f'<div class="tag mono">Nasionko</div>'
        f'<h1 class="fr">Puść to dalej.</h1>'
        f'<p>Kupiłeś flowera i dlatego ta karta leży w pudełku. Daj ją komuś, kto od lat obiecuje sobie, że wróci do książek. '
        f'Z tym kodem kupi swojego flowera <b>{taniej}</b>.</p>'
        f'<div class="how mono">Zeskanuj kod QR albo wpisz go na <span style="white-space:nowrap">{SITE.replace("https://", "")}</span>. Działa raz, przez rok.</div>'
        f'<div class="qr">{qr_svg(f"{SITE}/?kod={code}")}</div>'
        f'<div class="code mono">{code}</div>'
        f'</div></div></body></html>')


def back():
    seeds = (seed(46, 2, 33, 18, .96, True) + seed(72, 27, 17, -24, .6, True) + seed(81, 4, 9, 62, .4, True))
    return (HEAD.format(title="flower rewers", css=CSS) +
        f'<div class="sheet back"><div class="trim">{seeds}'
        f'<div class="word fr">flower</div>'
        f'<h1 class="fr">Komu go dasz?</h1>'
        f'<div class="write"><span class="mono">Wpisz imię</span></div>'
        f'<div class="web mono">{SITE.replace("https://", "")}</div>'
        f'</div></div></body></html>')


def main():
    OUT.mkdir(exist_ok=True)
    for old in OUT.glob("*"): old.unlink()
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
