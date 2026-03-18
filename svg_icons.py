# -*- coding: utf-8 -*-
from __future__ import annotations
import base64
from functools import lru_cache
from pathlib import Path

# Ikonice kataloga — vizualno identične 2D prikazu na zidu (1:1).
# Ručke: crni filled pravougaonik (kao u visualization.py HANDLE_FILL="#000000").
# Dimenzije ručki proporcionalne stvarnim (200mm ručka, 20mm širina).
# Izlaz uvek 52×46 px.
#
# ViewBox proporcije odgovaraju stvarnim dimenzijama elementa:
#   TALL  (600×2100mm) → viewBox "0 0 40 80"   — uski, visoki
#   WALL  (600×720mm)  → viewBox "0 0 80 54"   — široki, srednji
#   BASE  (600×720mm)  → viewBox "0 0 80 60"   — široki, viši
#   WALL_UPPER (600×400mm) → "0 0 80 50"       — široki, nizak
#   TALL_TOP  (600×400mm)  → "0 0 80 50"       — široki, nizak (kao WU)

_W = 52
_H = 46
_HERE = Path(__file__).resolve().parent
_PHOTO_ICON_MAP = {}


@lru_cache(maxsize=64)
def _photo_data_uri(path_str: str) -> str:
    p = Path(path_str)
    raw = p.read_bytes()
    b64 = base64.b64encode(raw).decode("ascii")
    return f"data:image/png;base64,{b64}"


def svg_for_tid(tid: str) -> str:  # noqa: C901
    t = tid.upper()

    # Real photo icon override (for templates where we have image assets).
    _img_p = _PHOTO_ICON_MAP.get(t)
    if _img_p and _img_p.exists():
        try:
            _src = _photo_data_uri(str(_img_p))
            return (
                f'<img src="{_src}" width="{_W}" height="{_H}" '
                'style="display:block; object-fit:cover; border:1px solid #c8c8c8; '
                'border-radius:2px; background:#f5f5f5;" />'
            )
        except Exception:
            # Fallback below to SVG icon if image loading fails.
            pass

    # ── Grundne helpers ────────────────────────────────────────────────────
    def r(x, y, w, h, sw=1.5, fill="white"):
        return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" '
                f'stroke="#383838" stroke-width="{sw}" fill="{fill}"/>')

    def ln(x1, y1, x2, y2, sw=1.2, sc="#383838", dash=""):
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
                f'stroke="{sc}" stroke-width="{sw}"{dash_attr}/>')

    def el(cx, cy, rx, ry, sw=1.2, sc="#383838", fill="none"):
        return (f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" '
                f'stroke="{sc}" stroke-width="{sw}" fill="{fill}"/>')

    def circ(cx, cy, rad, sc="#383838", fill="none", sw=1.0):
        return (f'<circle cx="{cx}" cy="{cy}" r="{rad}" '
                f'stroke="{sc}" stroke-width="{sw}" fill="{fill}"/>')

    def hv(x, y1, y2):
        """Vertikalna ručka — crni filled pravougaonik (kao viz.py bar handle)."""
        return (f'<rect x="{x - 1.2:.1f}" y="{y1}" width="2.5" '
                f'height="{y2 - y1}" fill="#111111" rx="1.2"/>')

    def hh(x1, x2, y):
        """Horizontalna ručka — crni filled pravougaonik."""
        return (f'<rect x="{x1}" y="{y - 1.2:.1f}" width="{x2 - x1}" '
                f'height="2.5" fill="#111111" rx="1.2"/>')

    # ══════════════════════════════════════════════════════
    # VISOKI  –  viewBox 40×80  (uski, visoki, ~600×2100mm)
    # Ručka: 200mm / 2100mm * 68 ≈ 6.5 jedin. — blizu VRHA  (jer visoka vrata
    #         se hvataju blizu vrha pri otvaranju: handle_cy = h - 150mm)
    # ══════════════════════════════════════════════════════

    if "TALL_FRIDGE_FREEZER" in t:
        # Integrisani frižider+zamrzivač u koloni:
        # gornji frižider (~55% visine) + donji zamrzivač (~45%)
        # Ručka frižidera: blizu vrha gornje sekcije
        # Ručka zamrzivača: blizu vrha donje sekcije
        vb = "0 0 40 80"
        body = (r(3, 2, 34, 76)
                + r(6, 5, 28, 71, sw=0.7, fill="#F1E7D4")
                + ln(3, 44, 37, 44)           # linija frižider / zamrzivač
                + hv(30, 8, 15)               # ručka frižidera
                + hv(30, 48, 55))             # ručka zamrzivača

    elif "TALL_FRIDGE" in t:
        # Integrisani frižider — jedan panel, ručka desno blizu vrha
        vb = "0 0 40 80"
        body = (r(3, 2, 34, 76)
                + r(6, 5, 28, 71, sw=0.7, fill="#F1E7D4")   # neutralni front panel
                + ln(3, 44, 37, 44, sw=0.7)  # razdvajač (friz/zamrz)
                + hv(30, 8, 15)               # ručka frižidera (blizu vrha)
                + hv(30, 48, 55))             # ručka zamrzivača

    elif "TALL_OVEN_MICRO" in t:
        # Kolona: mikrovalna gore + rerna u sredini + storage najdole
        # Horizontalne ručke za svaki uređaj (otvaraju se prema napred)
        vb = "0 0 40 80"
        body = (r(3, 2, 34, 76)               # okvir
                + r(6, 5, 28, 18)             # mikrovalna — vrata/prozor
                + hh(7, 33, 25)               # micro horizontalna ručka
                + r(6, 30, 28, 20)            # rerna — prozor
                + hh(7, 33, 52)               # rerna horizontalna ručka
                + ln(3, 58, 37, 58)           # linija ispod rerne
                + ln(14, 64, 26, 64))         # donja sekcija — linija

    elif "TALL_OVEN" in t:
        # Visoki sa rernom + storage ispod/iznad
        vb = "0 0 40 80"
        body = (r(3, 2, 34, 76)               # okvir
                + r(6, 17, 28, 27)            # rerna — prozor (tamni okvir)
                + hh(7, 33, 48)               # horizontalna ručka rerne
                + ln(3, 54, 37, 54)           # linija razdvajanja
                + ln(14, 61, 26, 61))         # donja sekcija — linija

    elif "TALL_TOP_OPEN" in t:
        # Popuna iznad visokog elementa — otvorene police (600×400mm → WIDE!)
        vb = "0 0 80 50"
        _wc = "#D8CBBB"; _bc = "#BEBAB7"
        body = (r(3, 3, 74, 44, fill=_bc, sw=1.5)
                + r(3, 3, 74, 5, sw=0, fill=_wc)      # gornja ploča
                + r(3, 42, 74, 5, sw=0, fill=_wc)     # donja ploča
                + r(3, 3, 5, 44, sw=0, fill=_wc)      # leva ploča
                + r(72, 3, 5, 44, sw=0, fill=_wc)     # desna ploča
                + r(3, 19, 74, 4, sw=0.5, fill=_wc)   # polica 1
                + r(3, 31, 74, 4, sw=0.5, fill=_wc)   # polica 2
                + r(3, 3, 74, 44, fill="none", sw=1.5))

    elif "TALL_TOP" in t:
        # Popuna iznad visokog — sa 2 vrata (600×400mm → WIDE!)
        vb = "0 0 80 50"
        body = (r(3, 3, 74, 44)
                + ln(40, 3, 40, 47)           # srednja vertikala
                + r(6, 7, 31, 36) + r(43, 7, 31, 36)   # 2 panela vrata
                + hv(34, 12, 21) + hv(46, 12, 21))     # 2 ručke prema sredini

    elif "TALL_CORNER" in t:
        # Visoki ugaoni — L-oblik punom visinom
        vb = "0 0 40 80"
        body = ('<path d="M3 2 H30 V38 H20 V78 H3 Z" '
                'stroke="#383838" stroke-width="1.5" fill="white"/>'
                + ln(3, 78, 30, 2, sw=0.7, sc="#C0C0C0", dash="3,2.5"))

    elif "TALL_OPEN" in t:
        # Visoki otvoreni — police vidljive (bez vrata)
        vb = "0 0 40 80"
        _wc = "#D8CBBB"; _bc = "#BEBAB7"
        body = (r(3, 2, 34, 76, fill=_bc, sw=1.5)
                + r(3, 2, 34, 5, sw=0, fill=_wc)      # gornja ploča
                + r(3, 73, 34, 5, sw=0, fill=_wc)     # donja ploča
                + r(3, 2, 5, 76, sw=0, fill=_wc)      # leva ploča
                + r(32, 2, 5, 76, sw=0, fill=_wc)     # desna ploča
                + r(3, 23, 34, 3, sw=0.5, fill=_wc)   # polica 1
                + r(3, 40, 34, 3, sw=0.5, fill=_wc)   # polica 2
                + r(3, 57, 34, 3, sw=0.5, fill=_wc)   # polica 3
                + r(3, 2, 34, 76, fill="none", sw=1.5))

    elif "TALL_PANTRY" in t:
        # Ostava — 2 staklena vrata + police vidljive iza stakla
        # Ručke okrenute prema sredini (kao u 2D prikazu)
        vb = "0 0 40 80"
        body = (r(3, 2, 34, 76)               # okvir
                + ln(20, 2, 20, 78)           # srednja vertikala
                + r(5, 5, 12, 68, sw=0.8, fill="#DDF0FB")   # leva staklo vrata
                + r(23, 5, 12, 68, sw=0.8, fill="#DDF0FB")  # desna staklo vrata
                + ln(5, 22, 17, 22, sw=0.7)   # polica L1
                + ln(5, 42, 17, 42, sw=0.7)   # polica L2
                + ln(5, 60, 17, 60, sw=0.7)   # polica L3
                + ln(23, 22, 35, 22, sw=0.7)  # polica D1
                + ln(23, 42, 35, 42, sw=0.7)  # polica D2
                + ln(23, 60, 35, 60, sw=0.7)  # polica D3
                + hv(16, 8, 15)               # ručka levih vrata (prema sredini)
                + hv(24, 8, 15))              # ručka desnih vrata (prema sredini)

    elif "TALL_GLASS" in t:
        # Vitrina — 2 staklena vrata + police iza stakla + refleksije (plavi fill)
        vb = "0 0 40 80"
        body = (r(3, 2, 34, 76)               # okvir
                + ln(20, 2, 20, 78)           # srednja vertikala
                + r(5, 5, 12, 68, sw=0.8, fill="#D4E9F7")   # levo staklo (plavi fill)
                + r(23, 5, 12, 68, sw=0.8, fill="#D4E9F7")  # desno staklo (plavi fill)
                + ln(5, 5, 17, 73, sw=0.6, sc="#B0CCE0")    # refleksija L (dijagonala)
                + ln(23, 5, 35, 73, sw=0.6, sc="#B0CCE0")   # refleksija D (dijagonala)
                + ln(5, 22, 17, 22, sw=0.7)   # polica L1
                + ln(5, 42, 17, 42, sw=0.7)   # polica L2
                + ln(5, 60, 17, 60, sw=0.7)   # polica L3
                + ln(23, 22, 35, 22, sw=0.7)  # polica D1
                + ln(23, 42, 35, 42, sw=0.7)  # polica D2
                + ln(23, 60, 35, 60, sw=0.7)  # polica D3
                + hv(16, 8, 15)               # ručka L (prema sredini)
                + hv(24, 8, 15))              # ručka D (prema sredini)

    elif "TALL" in t:
        # TALL_DOORS — 1 ili 2 vrata (punom visinom)
        vb = "0 0 40 80"
        _is_wardrobe = "WARDROBE" in t
        _hy1, _hy2 = (34, 46) if _is_wardrobe else (8, 15)

        # ── Unutrašnje sekcije ormara — otvorene, bez vrata ──────────────────
        if "INT_SHELVES" in t:
            # Sekcija: samo police (vidljive horizontalne linije)
            body = (r(3, 2, 34, 76)
                    + ln(3, 20, 37, 20, sw=0.9)   # polica 1
                    + ln(3, 38, 37, 38, sw=0.9)   # polica 2
                    + ln(3, 56, 37, 56, sw=0.9)   # polica 3
                    + ln(3, 70, 37, 70, sw=0.7))  # dno (polica)
        elif "INT_DRAWERS" in t:
            # Sekcija: fioke (vidljivi frontovi s ručkama)
            body = (r(3, 2, 34, 76)
                    + r(5, 6, 30, 14)             # fioka 1
                    + r(5, 23, 30, 14)            # fioka 2
                    + r(5, 40, 30, 14)            # fioka 3
                    + r(5, 57, 30, 14)            # fioka 4
                    + hh(10, 30, 13) + hh(10, 30, 30)
                    + hh(10, 30, 47) + hh(10, 30, 64))  # ručke fioka
        elif "INT_HANG" in t:
            # Sekcija: šipka za vješanje + siluete odjeće
            body = (r(3, 2, 34, 76)
                    + ln(6, 22, 34, 22, sw=2.2, sc="#555555")   # šipka (deblja)
                    + ln(12, 22, 12, 56, sw=0.8)  # vješalica 1
                    + ln(20, 22, 20, 56, sw=0.8)  # vješalica 2
                    + ln(28, 22, 28, 56, sw=0.8)  # vješalica 3
                    + ln(3, 64, 37, 64, sw=0.8))  # donja polica

        elif "2DOOR" in t or "DOORS" in t:
            body = (r(3, 2, 34, 76)
                    + ln(20, 2, 20, 78)       # srednja vertikala
                    + r(5, 5, 12, 68)         # levo vrata panel
                    + r(23, 5, 12, 68)        # desno vrata panel
                    + hv(16, _hy1, _hy2)      # ručka L (prema sredini)
                    + hv(24, _hy1, _hy2))     # ručka D (prema sredini)
        else:
            # 1DOOR — ručka desno, blizu vrha
            body = (r(3, 2, 34, 76)
                    + r(6, 5, 28, 68)         # vrata panel
                    + hv(30, _hy1, _hy2))     # ručka desno

    # ══════════════════════════════════════════════════════
    # WALL_UPPER  –  viewBox 80×50  (širok, nizak, ~600×400mm)
    # Ručka: 200mm / 400mm * 36 ≈ 18 jedin. — proportionalna
    # ══════════════════════════════════════════════════════

    elif "WALL_UPPER" in t:
        vb = "0 0 80 50"
        if "2DOOR" in t:
            body = (r(3, 3, 74, 44)
                    + ln(40, 3, 40, 47)
                    + r(6, 7, 31, 36) + r(43, 7, 31, 36)
                    + hv(34, 12, 22) + hv(46, 12, 22))
        elif "LIFTUP" in t:
            body = (r(3, 3, 74, 44)
                    + r(7, 7, 66, 36)
                    + ln(7, 7, 73, 27)        # dijagonala: klapna se otvara prema gore
                    + hh(26, 54, 43))         # horizontalna ručka pri dnu
        elif "OPEN" in t:
            _wc = "#D8CBBB"; _bc = "#BEBAB7"
            body = (r(3, 3, 74, 44, fill=_bc, sw=1.5)
                    + r(3, 3, 74, 5, sw=0, fill=_wc)      # gornja ploča
                    + r(3, 42, 74, 5, sw=0, fill=_wc)     # donja ploča
                    + r(3, 3, 5, 44, sw=0, fill=_wc)      # leva ploča
                    + r(72, 3, 5, 44, sw=0, fill=_wc)     # desna ploča
                    + r(3, 19, 74, 4, sw=0.5, fill=_wc)   # polica 1
                    + r(3, 31, 74, 4, sw=0.5, fill=_wc)   # polica 2
                    + r(3, 3, 74, 44, fill="none", sw=1.5))
        else:
            # 1DOOR default
            body = (r(3, 3, 74, 44)
                    + r(7, 7, 66, 36)
                    + hv(68, 11, 21))         # ručka desno

    # ══════════════════════════════════════════════════════
    # GORNJI / WALL  –  viewBox 80×54  (širok, srednji, ~600×720mm)
    # Ručka: 200mm/720mm * 40 ≈ 11 jedin. — centar na ~21% od vrha panela
    # ══════════════════════════════════════════════════════

    elif "WALL_CORNER_DIAGONAL" in t:
        # Ugaoni gornji dijagonalni — petougaoni front
        vb = "0 0 80 54"
        body = ('<path d="M3 3 H54 V28 L24 51 H3 Z" '
                'stroke="#383838" stroke-width="1.5" fill="white"/>'
                + hh(31, 47, 37))   # ručka na dijagonalnom frontu

    elif "WALL_CORNER" in t or ("WALL" in t and "CORNER" in t):
        # Ugaoni gornji element — L-oblik
        vb = "0 0 80 54"
        body = ('<path d="M3 3 H54 V24 H24 V51 H3 Z" '
                'stroke="#383838" stroke-width="1.5" fill="white"/>'
                + ln(3, 51, 54, 3, sw=0.7, sc="#C0C0C0", dash="3,2.5"))

    elif "HOOD" in t:
        # Napa/aspirator — trapezoidni oblik + rešetka (3 linije)
        vb = "0 0 80 54"
        body = ('<path d="M10 6 H70 L60 48 H20 Z" '
                'stroke="#383838" stroke-width="1.5" fill="#E8E8E8"/>'
                + ln(14, 20, 66, 20)          # rešetka linija 1
                + ln(17, 32, 63, 32)          # rešetka linija 2
                + ln(19, 44, 61, 44)          # rešetka linija 3
                + circ(40, 13, 3.5, fill="white", sw=0.8))  # ventilator dugme

    elif "MICRO" in t:
        # Mikrotalasna — vrata/prozor levo + dial dugme desno + ručka
        vb = "0 0 80 54"
        body = (r(3, 3, 74, 48)
                + r(7, 8, 44, 34)             # prozor/vrata
                + el(65, 25, 8, 8)            # točkić/dial
                + ln(3, 44, 77, 44, sw=0.8)   # kontrolna linija
                + hh(10, 50, 45))             # horizontalna ručka

    elif "WALL" in t:
        vb = "0 0 80 54"
        if "2DOOR" in t:
            body = (r(3, 3, 74, 48)
                    + ln(40, 3, 40, 51)       # srednja vertikala
                    + r(6, 7, 31, 40) + r(43, 7, 31, 40)
                    + hv(34, 13, 24) + hv(46, 13, 24))  # ručke prema sredini
        elif "GLASS" in t:
            # Staklena vrata — plavi fill + dijagonalne refleksije + ručke
            body = (r(3, 3, 74, 48)
                    + ln(40, 3, 40, 51)       # srednja vertikala
                    + r(6, 7, 31, 40, sw=0.8, fill="#D4E9F7")    # levo staklo
                    + r(43, 7, 31, 40, sw=0.8, fill="#D4E9F7")   # desno staklo
                    + ln(6, 7, 37, 47, sw=0.7, sc="#B0CCE0")     # refleksija L
                    + ln(43, 7, 74, 47, sw=0.7, sc="#B0CCE0")    # refleksija D
                    + hv(34, 13, 24) + hv(46, 13, 24))           # ručke prema sredini
        elif "LIFTUP" in t:
            # Klapna — panel + dijagonalna strelica prema gore + horizontalna ručka
            body = (r(3, 3, 74, 48)
                    + r(7, 7, 66, 40)
                    + ln(7, 7, 73, 30, sw=1.0)  # dijagonala (smer otvaranja gore)
                    + hh(26, 54, 47))            # horizontalna ručka pri dnu
        elif "NARROW" in t:
            # Uski gornji (začini, ulje) — unutrašnji panel + ručka desno
            body = (r(22, 3, 36, 48)
                    + r(25, 7, 30, 40)
                    + hv(51, 13, 23))
        elif "OPEN" in t:
            # Otvoreni gornji — vidljive police (bez vrata, bez ručke)
            _wc = "#D8CBBB"; _bc = "#BEBAB7"
            body = (r(3, 3, 74, 48, fill=_bc, sw=1.5)
                    + r(3, 3, 74, 5, sw=0, fill=_wc)      # gornja ploča
                    + r(3, 46, 74, 5, sw=0, fill=_wc)     # donja ploča
                    + r(3, 3, 5, 48, sw=0, fill=_wc)      # leva ploča
                    + r(72, 3, 5, 48, sw=0, fill=_wc)     # desna ploča
                    + r(3, 20, 74, 4, sw=0.5, fill=_wc)   # polica 1
                    + r(3, 33, 74, 4, sw=0.5, fill=_wc)   # polica 2
                    + r(3, 3, 74, 48, fill="none", sw=1.5))
        else:
            # WALL_1DOOR default — panel + ručka desno
            body = (r(3, 3, 74, 48)
                    + r(7, 7, 66, 40)
                    + hv(68, 13, 24))

    # ══════════════════════════════════════════════════════
    # DONJI + UGRADNI  –  viewBox 80×60  (širok, viši, ~600×720mm)
    # Ručka: 200mm/720mm * 46 ≈ 13 jedin. — centar na ~21% od vrha panela
    # ══════════════════════════════════════════════════════

    elif "BASE_CORNER_DIAGONAL" in t:
        # Ugaoni donji dijagonalni — petougaoni front
        vb = "0 0 80 60"
        body = ('<path d="M3 3 H52 V35 L24 57 H3 Z" '
                'stroke="#383838" stroke-width="1.5" fill="white"/>'
                + hh(32, 44, 46))   # ručka na dijagonalnom frontu

    elif "CORNER" in t:
        # Ugaoni donji element — L-oblik + dijagonalna linija
        vb = "0 0 80 60"
        body = ('<path d="M3 3 H52 V26 H24 V57 H3 Z" '
                'stroke="#383838" stroke-width="1.5" fill="white"/>'
                + ln(3, 57, 52, 3, sw=0.7, sc="#C0C0C0", dash="3,2.5"))

    elif "COOKING_UNIT" in t:
        # Ugradna ploča + rerna + fioka (front prikaz)
        vb = "0 0 80 60"
        body = (
            r(3, 3, 74, 54)                                    # korpus
            # Hob / radna ploča
            + r(3, 3, 74, 7, sw=0.8, fill="#B9B9B9")           # inox ram
            + r(12, 3.8, 56, 5.2, sw=0.6, fill="#1A1A1A")      # crna staklokeramika
            + el(24, 6.4, 7, 2.2, sw=0.7, sc="#7E7E7E")
            + el(56, 6.4, 7, 2.2, sw=0.7, sc="#7E7E7E")
            # Kontrolna traka rerne
            + r(7, 11, 66, 7.5, sw=0.8, fill="#D8D8D8")
            + circ(20, 14.7, 2.3, sc="#777", fill="#E5E5E5", sw=0.7)
            + circ(60, 14.7, 2.3, sc="#777", fill="#E5E5E5", sw=0.7)
            + r(35, 12.6, 10, 4.2, sw=0.6, fill="#161616")
            # Vrata rerne
            + r(9, 19.5, 62, 24.5, sw=0.9, fill="#BFC3C8")
            + r(12, 22, 56, 18.5, sw=0.6, fill="#1A1A1A")
            + hh(22, 39.2, 37)
            # Donja fioka
            + r(8, 45.5, 64, 10, sw=0.8, fill="#D7B98A")
            + hh(26, 51.0, 28)
            # Bočni razdelnici
            + ln(9, 11, 9, 55, sw=0.6, sc="#9A9A9A")
            + ln(71, 11, 71, 55, sw=0.6, sc="#9A9A9A")
        )

    elif "DISHWASHER" in t:
        # Mašina za sudove — vrata se otvaraju PREMA DOLJE, ručka je GORE u sredini
        vb = "0 0 80 60"
        body = (r(3, 3, 74, 54)
                + r(3, 3, 74, 11, sw=0.6, fill="#D0D0D0")      # kontrolna traka na vrhu
                + circ(18, 8.5, 1.8, sc="#666", fill="#888", sw=0.6)   # LED/dugme 1
                + circ(30, 8.5, 1.8, sc="#666", fill="#888", sw=0.6)   # LED/dugme 2
                + circ(42, 8.5, 1.8, sc="#666", fill="#888", sw=0.6)   # LED/dugme 3
                + r(7, 16, 66, 37)            # vrata panel
                + hh(27, 53, 21))             # horizontalna ručka pri vrhu vrata (centar)

    elif "SINK" in t:
        # Sudopera (do 600mm = 1 vrata, ručka desno) + česma iznad radne ploče
        # Ikona prikazuje default stanje: 600mm = 1 vrata (kao u _draw_sink)
        vb = "0 -10 80 70"
        body = (r(3, 3, 74, 54)              # korpus
                + r(6, 7, 68, 44)            # jedno vrata (puna sirina)
                + hv(68, 11, 24)             # vertikalna ručka desno
                # Česma iznad radne ploče (gooseneck)
                + '<line x1="38" y1="-7" x2="38" y2="3" '
                  'stroke="#383838" stroke-width="2.0"/>'        # stub
                + '<path d="M38 -7 Q38 -12 43 -12 Q49 -12 49 -7" '
                  'stroke="#383838" stroke-width="1.8" fill="none"/>'   # gooseneck luk
                + '<line x1="49" y1="-7" x2="49" y2="-3" '
                  'stroke="#383838" stroke-width="1.5"/>/')       # izlaz vode

    elif "FRIDGE_UNDER" in t:
        # Donji dio ugradnog frižidera (base zona) — integrisani panel (bijeli front)
        # Horizontal pregrad ~28% od vrha + ručka desno + "F" oznaka
        vb = "0 0 80 60"
        body = (r(3, 3, 74, 54)                                  # korpus
                + r(7, 7, 66, 46, sw=0.8)                        # bijeli door panel (no fill = white)
                + ln(9, 20, 71, 20, sw=0.7, dash="3,2")          # horizontalni pregrad (dashed)
                + hv(68, 25, 38)                                  # ručka desno
                + '<text x="33" y="41" font-size="9" font-style="italic" '
                  'fill="#555555" opacity="0.6">F</text>'         # oznaka frižidera
                )

    elif "FRIDGE" in t or "FREEZER" in t:
        # BASE ugradni frižider: gornje ~60% = frižider, donje ~40% = zamrzivač
        # Horizontalna linija razdvajanja + 2 ručke desno (svaka sekcija)
        # Odgovara _draw_fridge() u visualization.py: split_y = y + h * 0.40 (od dna)
        vb = "0 0 80 60"
        body = (r(3, 3, 74, 54)
                + r(7, 7, 66, 46, sw=0.8, fill="#F1E7D4")       # neutralni front panel
                + ln(3, 35, 77, 35, sw=1.0)                     # razdvajač: frižider / zamrzivač
                + hv(68, 14, 28)                                 # ručka frižidera (gornja sekcija)
                + hv(68, 38, 51))                               # ručka zamrzivača (donja sekcija)

    elif "DOOR_DRAWER" in t:
        # Donji kombinirani: fioka GORE (~28%) + 2 vrata DOLE (~72%)
        # (isti raspored kao u 2D viz: _draw_base_doors_drawers)
        vb = "0 0 80 60"
        body = (r(3, 3, 74, 54)
                + ln(3, 19, 77, 19)           # linija fioka / vrata
                + hh(26, 54, 11)              # horizontalna ručka fioke
                + ln(40, 19, 40, 57)          # vertikalna podjela vrata (2 krila)
                + r(6, 22, 30, 31) + r(44, 22, 30, 31)   # 2 vrata panela
                + hv(34, 30, 41) + hv(46, 30, 41))        # vertikalne ručke vrata

    elif "DRAWERS" in t:
        # Donji samo fioke (3 fioke jednakih visina)
        # Horizontalne ručke centrirane u svakoj fioci
        vb = "0 0 80 60"
        body = (r(3, 3, 74, 54)
                + ln(3, 21, 77, 21)           # razdvajač fioka 1/2
                + ln(3, 39, 77, 39)           # razdvajač fioka 2/3
                + hh(26, 54, 12)              # ručka fioke 1 (gornja)
                + hh(26, 54, 30)              # ručka fioke 2 (srednja)
                + hh(26, 54, 47))             # ručka fioke 3 (donja)

    elif "NARROW" in t:
        # Uski BASE (flase, ulje, začini) — panel + ručka desno
        vb = "0 0 80 60"
        body = (r(3, 3, 74, 54)
                + r(24, 7, 32, 46)
                + hv(52, 12, 25))

    elif "OPEN" in t:
        # Donji otvoreni — police vidljive (bez vrata)
        vb = "0 0 80 60"
        _wc = "#D8CBBB"; _bc = "#BEBAB7"
        body = (r(3, 3, 74, 54, fill=_bc, sw=1.5)
                + r(3, 3, 74, 5, sw=0, fill=_wc)      # gornja ploča
                + r(3, 52, 74, 5, sw=0, fill=_wc)     # donja ploča
                + r(3, 3, 5, 54, sw=0, fill=_wc)      # leva ploča
                + r(72, 3, 5, 54, sw=0, fill=_wc)     # desna ploča
                + r(3, 22, 74, 4, sw=0.5, fill=_wc)   # polica 1
                + r(3, 37, 74, 4, sw=0.5, fill=_wc)   # polica 2
                + r(3, 3, 74, 54, fill="none", sw=1.5))

    elif "2DOOR" in t:
        # BASE 2-vrata — panel levo i desno, ručke prema sredini
        vb = "0 0 80 60"
        body = (r(3, 3, 74, 54)
                + ln(40, 3, 40, 57)           # srednja vertikala
                + r(6, 7, 30, 46) + r(44, 7, 30, 46)
                + hv(34, 12, 25) + hv(46, 12, 25))

    elif "GLASS" in t:
        # BASE staklo — plavi fill + dijagonalne refleksije + ručka
        vb = "0 0 80 60"
        body = (r(3, 3, 74, 54)
                + r(7, 7, 66, 46, sw=0.8, fill="#D4E9F7")       # staklo fill
                + ln(7, 7, 73, 53, sw=0.7, sc="#B0CCE0")        # refleksija 1
                + ln(73, 7, 7, 53, sw=0.7, sc="#B0CCE0")        # refleksija 2
                + hv(68, 12, 25))             # ručka desno

    elif "LIFTUP" in t:
        # BASE klapna — panel + dijagonalna linija + horizontalna ručka dole
        vb = "0 0 80 60"
        body = (r(3, 3, 74, 54)
                + r(7, 7, 66, 46)
                + ln(7, 53, 73, 28, sw=1.0)   # dijagonala (smer gore)
                + hh(26, 54, 51))             # horizontalna ručka pri dnu

    elif "OVEN" in t:
        # Ugradna rerna — prozor + horizontalna ručka + linija razdvajanja
        vb = "0 0 80 60"
        body = (r(3, 3, 74, 54)
                + r(8, 7, 64, 30)             # prozor rerne
                + hh(26, 54, 42)              # horizontalna ručka rerne
                + ln(3, 46, 77, 46)           # linija razdvajanja
                + ln(26, 52, 54, 52))         # donja sekcija

    elif "TRASH" in t:
        # Sortirnik — 2 vrata sa ovalima koji naznačuju kante za otpad
        vb = "0 0 80 60"
        body = (r(3, 3, 74, 54)
                + ln(40, 3, 40, 57)           # srednja vertikala
                + r(6, 7, 30, 46) + r(44, 7, 30, 46)    # 2 vrata
                + hv(34, 12, 25) + hv(46, 12, 25)        # ručke prema sredini
                + el(21, 33, 8, 11, sc="#666666", sw=0.8)  # kanta L (oval)
                + el(21, 24, 3, 2, sc="#666666", sw=0.6)   # poklopac L (oval mali)
                + el(59, 33, 8, 11, sc="#666666", sw=0.8)  # kanta D (oval)
                + el(59, 24, 3, 2, sc="#666666", sw=0.6))  # poklopac D (oval mali)

    elif "HOB" in t:
        # Samostalna ploča za kuvanje — tamna gornja ploča sa 4 ringlje + vrata ispod
        vb = "0 0 80 60"
        body = (r(3, 3, 74, 54)
                + r(3, 3, 74, 22, sw=0.6, fill="#1A1A1A")   # tamna kuhinjska ploča
                + el(26, 13, 9, 6, sw=0.9, sc="#888888")     # ring levi
                + el(26, 13, 4, 3, sw=0.7, sc="#888888", fill="#555555")  # centar L
                + el(54, 13, 9, 6, sw=0.9, sc="#888888")     # ring desni
                + el(54, 13, 4, 3, sw=0.7, sc="#888888", fill="#555555")  # centar D
                + r(6, 26, 68, 25)            # vrata panel (ispod ploče)
                + hv(68, 29, 42))             # ručka desno

    elif "FILLER_PANEL" in t or "FILLER" in t:
        # Filer panel — uski popunjač prikazan kao tanka ploča u centru viewBox-a
        vb = "0 0 80 60"
        body = (r(31, 3, 18, 54)             # tanka ploča (filer)
                + ln(34, 12, 48, 12, sw=0.5, sc="#CCCCCC")  # drvena žila 1
                + ln(34, 24, 48, 24, sw=0.5, sc="#CCCCCC")  # drvena žila 2
                + ln(34, 36, 48, 36, sw=0.5, sc="#CCCCCC")  # drvena žila 3
                + ln(34, 47, 48, 47, sw=0.5, sc="#CCCCCC"))  # drvena žila 4

    elif "END_PANEL" in t:
        vb = "0 0 80 60"
        body = (r(24, 3, 28, 54, sw=1.1, fill="#EEE8DC")
                + r(52, 6, 6, 48, sw=0.7, fill="#D7CFBF")
                + ln(28, 15, 48, 15, sw=0.5, sc="#D0C9B8")
                + ln(28, 28, 48, 28, sw=0.5, sc="#D0C9B8")
                + ln(28, 41, 48, 41, sw=0.5, sc="#D0C9B8")
                + ln(52, 6, 58, 10, sw=0.6, sc="#B8AF9F")
                + ln(52, 54, 58, 50, sw=0.6, sc="#B8AF9F"))

    elif "END_PANEL_OLD_UNUSED" in t:
        # Završna bočna ploča — prikazana face-on kao dekorativna drvena ploča
        vb = "0 0 80 60"
        body = (r(3, 3, 74, 54)              # puna ploča (face view)
                + r(6, 6, 68, 48, sw=0.6, fill="#EEE8DC")   # drvo fill (topli ton)
                + ln(6, 18, 74, 18, sw=0.5, sc="#D0C9B8")   # drvena žila 1
                + ln(6, 32, 74, 32, sw=0.5, sc="#D0C9B8")   # drvena žila 2
                + ln(6, 44, 74, 44, sw=0.5, sc="#D0C9B8"))  # drvena žila 3

    else:
        # BASE_1DOOR i default — panel + ručka desno
        vb = "0 0 80 60"
        body = (r(3, 3, 74, 54)
                + r(7, 7, 66, 46)
                + hv(68, 12, 25))             # ručka desno (standardno)

    return (
        f'<svg viewBox="{vb}" width="{_W}" height="{_H}" '
        f'style="flex-shrink:0" preserveAspectRatio="xMidYMid meet">'
        f'{body}</svg>'
    )
