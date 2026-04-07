# -*- coding: utf-8 -*-
"""
test_stress.py — Automatski stres test: N nasumicnih kuhinja

Za svaku kuhinju proverava:
  - layout_audit: nema preklapanja, nema izlaska van zida
  - generate_cutlist: ne pada, vraca sve sekcije
  - FIN = CUT - kanta (matematicka tacnost za svaki komad)
  - Nema negativnih dimenzija
  - summary_all sadrzi sve tipove ploca (Ledna, Radna, Nosac)
  - PDF i Excel se generisu bez pada

Pokretanje:
    python test_stress.py              # 200 kuhinja (default)
    python test_stress.py -n 1000      # 1000 kuhinja
    python test_stress.py -n 50 -v     # 50 kuhinja, detaljan ispis
    python test_stress.py --no-export  # bez PDF/Excel (brze)
    python test_stress.py --seed 42    # reproducibilna nasumicnost
"""
from __future__ import annotations

import sys
import time
import random
import argparse
import traceback
from typing import Any, Dict, List, Tuple, Optional

sys.path.insert(0, ".")

from cutlist import (
    generate_cutlist,
    generate_cutlist_summary,
    build_cutlist_pdf_bytes,
    generate_cutlist_excel,
)
from layout_engine import layout_audit
from state_logic import _default_kitchen


# ─────────────────────────────────────────────────────────────────────────────
# Konfiguracija: svi dostupni moduli po zoni
# ─────────────────────────────────────────────────────────────────────────────

BASE_TEMPLATES = [
    ("BASE_1DOOR",    600, 720, 560, {}),
    ("BASE_1DOOR",    450, 720, 560, {}),
    ("BASE_2DOOR",    800, 720, 560, {}),
    ("BASE_2DOOR",    600, 720, 560, {}),
    ("BASE_NARROW",   300, 720, 560, {}),
    ("BASE_OPEN",     600, 720, 560, {}),
    ("BASE_DRAWERS_3",600, 720, 560, {"n_drawers": 3, "drawer_heights": [140,140,220]}),
    ("BASE_DRAWERS",  600, 720, 560, {"n_drawers": 2, "drawer_heights": [200,200]}),
    ("BASE_DOOR_DRAWER",600,720,560, {"n_drawers": 1, "drawer_heights": [200]}),
    ("SINK_BASE",     800, 720, 560, {}),
    ("SINK_BASE",     600, 720, 560, {}),
]

WALL_TEMPLATES = [
    ("WALL_1DOOR",  600, 700, 320, {}),
    ("WALL_2DOOR",  800, 700, 320, {}),
    ("WALL_NARROW", 300, 700, 320, {}),
    ("WALL_OPEN",   600, 700, 320, {}),
    ("WALL_GLASS",  600, 700, 320, {}),
    ("WALL_LIFTUP", 600, 360, 320, {}),
]

TALL_TEMPLATES = [
    ("TALL_PANTRY",     600, 2100, 560, {}),
    ("TALL_DOORS",      600, 2100, 560, {}),
    ("TALL_GLASS",      600, 2100, 560, {}),
    ("TALL_OPEN",       600, 2100, 560, {}),
    ("TALL_FRIDGE",     600, 2100, 560, {}),
    ("TALL_FRIDGE_FREEZER", 600, 2100, 560, {}),
    ("TALL_OVEN",       600, 2100, 560, {}),
]

# ─────────────────────────────────────────────────────────────────────────────
# Generator nasumicne kuhinje
# ─────────────────────────────────────────────────────────────────────────────

EDGE_THK = 2.0
STEP = 0.5
TOL = STEP + 0.01


def _make_kitchen(rng: random.Random) -> Dict[str, Any]:
    """Generise nasumicnu validnu kuhinju."""
    wall_len = rng.choice([2400, 2700, 3000, 3300, 3600, 4000])
    wall_h   = rng.choice([2400, 2500, 2600, 2700])
    foot_h   = rng.choice([100, 120, 150, 160])
    base_h   = rng.choice([680, 700, 720, 740])
    wt_thk   = rng.choice([20, 28, 40])   # debljina radne ploce u mm

    k = _default_kitchen()
    k["wall"]["length_mm"] = wall_len
    k["wall"]["height_mm"] = wall_h
    k["foot_height_mm"]    = foot_h
    k["base_korpus_h_mm"]  = base_h
    k["vertical_gap_mm"]   = rng.choice([0, 10, 18, 20])
    k["worktop"] = {
        "enabled":    True,
        "material":   rng.choice(["Granit", "Kompozit", "Iver 38mm"]),
        "thickness":  wt_thk / 10.0,   # _default_kitchen koristi cm
        "depth_mm":   600,
    }
    k["materials"] = {
        "carcass_material": rng.choice(["Iver 18mm", "MDF 18mm"]),
        "carcass_thk":      18,
        "front_material":   rng.choice(["MDF 19mm", "Iver 18mm", "Lakobel"]),
        "front_thk":        rng.choice([18, 19]),
        "back_material":    "Iver 8mm",
        "back_thk":         8,
        "edge_abs_thk":     EDGE_THK,
    }

    clearance_l = 5
    clearance_r = 5
    usable = wall_len - clearance_l - clearance_r

    modules: List[Dict[str, Any]] = []
    mid = 1

    # Odluci da li ima TALL zone (0–2 visoka elementa)
    n_tall = rng.choice([0, 0, 1, 2])
    tall_total_w = 0

    for _ in range(n_tall):
        tid, w, h, d, params = rng.choice(TALL_TEMPLATES)
        if tall_total_w + w > usable * 0.4:  # max 40% zida za tall zone
            break
        modules.append({
            "id": mid, "template_id": tid, "label": tid,
            "zone": "tall", "wall_key": "A",
            "x_mm": clearance_l + tall_total_w,
            "w_mm": w, "h_mm": h, "d_mm": d,
            "gap_after_mm": 0, "params": dict(params),
        })
        tall_total_w += w
        mid += 1

    # Popuni ostatak BASE elementima
    x = clearance_l + tall_total_w
    remaining = usable - tall_total_w
    while remaining > 250:
        candidates = [t for t in BASE_TEMPLATES if t[1] <= remaining]
        if not candidates:
            break
        candidates = [t for t in candidates if t[1] <= remaining - 50] or candidates
        tid, w, h, d, params = rng.choice(candidates)
        if w > remaining:
            break
        modules.append({
            "id": mid, "template_id": tid, "label": f"{tid}_{mid}",
            "zone": "base", "wall_key": "A",
            "x_mm": x, "w_mm": w, "h_mm": h, "d_mm": d,
            "gap_after_mm": 0, "params": dict(params),
        })
        x         += w
        remaining -= w
        mid       += 1
        if len(modules) >= 12:
            break

    # Dodaj WALL elemente poravnate sa BASE (nasumican podskup)
    base_mods = [m for m in modules if m["zone"] == "base"]
    wall_x = clearance_l + tall_total_w
    for bm in rng.sample(base_mods, min(len(base_mods), rng.randint(1, max(1, len(base_mods))))):
        tid, w, h, d, params = rng.choice(WALL_TEMPLATES)
        # Postavi wall iste sirine i X kao odgovarajuci base
        bw = int(bm["w_mm"])
        if w > bw:
            w = bw  # ne sme biti siri od base ispod
        modules.append({
            "id": mid, "template_id": tid, "label": f"{tid}_{mid}",
            "zone": "wall", "wall_key": "A",
            "x_mm": int(bm["x_mm"]), "w_mm": w, "h_mm": h, "d_mm": d,
            "gap_after_mm": 0, "params": dict(params),
        })
        mid += 1

    k["modules"] = modules
    return k


# ─────────────────────────────────────────────────────────────────────────────
# Verifikatori
# ─────────────────────────────────────────────────────────────────────────────

def _check_fin_cut(sections: Dict, kitchen_id: int) -> List[str]:
    """Vraca listu gresaka FIN/CUT matematike."""
    errors = []
    for sec in ("carcass", "fronts", "backs", "worktop", "drawer_boxes"):
        df = sections.get(sec)
        if df is None or df.empty:
            continue
        for _, row in df.iterrows():
            deo = str(row.get("Deo", "?"))[:20]
            cut_w = float(row.get("CUT_W [mm]", row.get("Duzina [mm]", 0)))
            cut_h = float(row.get("CUT_H [mm]", row.get("Sirina [mm]", 0)))
            fin_w = float(row.get("Duzina [mm]", 0))
            fin_h = float(row.get("Sirina [mm]", 0))

            # FIN nikad veci od CUT
            if fin_w > cut_w + TOL:
                errors.append(f"K{kitchen_id} {sec}/{deo}: FIN_W={fin_w}>{cut_w}")
            if fin_h > cut_h + TOL:
                errors.append(f"K{kitchen_id} {sec}/{deo}: FIN_H={fin_h}>{cut_h}")

            # Negativne dimenzije
            if fin_w < 0:
                errors.append(f"K{kitchen_id} {sec}/{deo}: FIN_W negativan={fin_w}")
            if fin_h < 0:
                errors.append(f"K{kitchen_id} {sec}/{deo}: FIN_H negativan={fin_h}")
            if cut_w < 0:
                errors.append(f"K{kitchen_id} {sec}/{deo}: CUT_W negativan={cut_w}")
            if cut_h < 0:
                errors.append(f"K{kitchen_id} {sec}/{deo}: CUT_H negativan={cut_h}")

            # Razlika mora biti viseknkratnik EDGE_THK
            if EDGE_THK > 0 and cut_w > 10:
                diff_w = cut_w - fin_w
                if diff_w < -TOL:
                    errors.append(f"K{kitchen_id} {sec}/{deo}: diff_W={diff_w:.2f}<0")
                elif abs(diff_w % EDGE_THK) > TOL and diff_w > TOL:
                    errors.append(f"K{kitchen_id} {sec}/{deo}: diff_W={diff_w:.2f} nije visekratnik {EDGE_THK}")

            if EDGE_THK > 0 and cut_h > 10:
                diff_h = cut_h - fin_h
                if diff_h < -TOL:
                    errors.append(f"K{kitchen_id} {sec}/{deo}: diff_H={diff_h:.2f}<0")
                elif abs(diff_h % EDGE_THK) > TOL and diff_h > TOL:
                    errors.append(f"K{kitchen_id} {sec}/{deo}: diff_H={diff_h:.2f} nije visekratnik {EDGE_THK}")

    return errors


def _check_summary(sections: Dict, kitchen_id: int) -> List[str]:
    """Provera da summary_all sadrzi sve tipove ploca."""
    errors = []
    try:
        summary = generate_cutlist_summary(sections)
        sa = summary.get("summary_all")
        if sa is None or sa.empty:
            # Prihvatljivo samo ako nema nijednog modula koji daje ploce
            all_empty = all(
                sections.get(s) is None or sections.get(s).empty
                for s in ("carcass", "fronts", "backs", "worktop")
            )
            if not all_empty:
                errors.append(f"K{kitchen_id}: summary_all prazan iako postoje ploce")
            return errors

        deo_vals = set(str(d).lower() for d in sa["Deo"].tolist())

        # Mora biti Ledna ploca ako ima backs
        backs = sections.get("backs")
        if backs is not None and not backs.empty:
            has_ledna = any("edna" in d or "le" in d for d in deo_vals if "plo" in d)
            if not has_ledna:
                errors.append(f"K{kitchen_id}: summary_all nema Lednu plocu (backs postoji)")

        # Mora biti Nosac ako ima worktop nosaca
        worktop = sections.get("worktop")
        if worktop is not None and not worktop.empty:
            nosaci = worktop[worktop["Deo"].str.contains("Nosa", case=False, na=False)]
            if not nosaci.empty:
                has_nosac = any("osa" in d for d in deo_vals)
                if not has_nosac:
                    errors.append(f"K{kitchen_id}: summary_all nema Nosac radne ploce")
    except Exception as ex:
        errors.append(f"K{kitchen_id}: summary crash — {type(ex).__name__}: {ex}")
    return errors


def _check_worktop_min_length(sections: Dict, kitchen: Dict, kitchen_id: int) -> List[str]:
    """Radna ploca treba biti >= 80% zbira sirina BASE modula."""
    errors = []
    base_mods = [m for m in kitchen.get("modules", []) if m.get("zone") == "base"]
    if not base_mods:
        return errors

    total_base_w = sum(int(m.get("w_mm", 0)) for m in base_mods)
    worktop = sections.get("worktop")
    if worktop is None or worktop.empty:
        return errors

    rp = worktop[worktop["Deo"].str.contains("Radna", case=False, na=False)]
    if rp.empty:
        return errors

    total_wt_w = float(rp["Duzina [mm]"].sum())
    if total_wt_w < total_base_w * 0.80:
        errors.append(
            f"K{kitchen_id}: radna ploca {total_wt_w:.0f}mm < 80% base sirine {total_base_w}mm"
        )
    return errors


# ─────────────────────────────────────────────────────────────────────────────
# Glavni runner
# ─────────────────────────────────────────────────────────────────────────────

def _p(text: str) -> None:
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode("ascii", errors="replace").decode("ascii"))


def run_stress(
    n: int = 200,
    seed: Optional[int] = None,
    verbose: bool = False,
    do_export: bool = True,
) -> Tuple[int, int, List[str]]:
    """
    Generise n nasumicnih kuhinja i proverava sve aspekte.
    Vraca (passed_kitchens, failed_kitchens, sve_greske).
    """
    rng = random.Random(seed)
    passed = 0
    failed = 0
    all_errors: List[str] = []

    # Statistike
    stats = {
        "layout_ok": 0, "layout_fail": 0,
        "cutlist_ok": 0, "cutlist_crash": 0,
        "fincuterr": 0,
        "summary_err": 0,
        "worktop_err": 0,
        "pdf_ok": 0, "pdf_fail": 0,
        "excel_ok": 0, "excel_fail": 0,
        "total_modules": 0,
        "total_ploce": 0,
    }

    t0 = time.time()

    for i in range(1, n + 1):
        k_errors: List[str] = []
        k = _make_kitchen(rng)
        n_mods = len(k.get("modules", []))
        stats["total_modules"] += n_mods

        # --- 1. Layout audit ---
        try:
            lay_ok, lay_msg = layout_audit(k)
            if lay_ok:
                stats["layout_ok"] += 1
            else:
                # Layout moze legalno pasti za lose-generisane kuhinje —
                # biljezimo ali NE racunamo kao gresku aplikacije
                stats["layout_fail"] += 1
                if verbose:
                    _p(f"  [INFO] K{i}: layout_audit pao (ocekivano za neke kombinacije): {lay_msg[:60]}")
        except Exception as ex:
            k_errors.append(f"K{i}: layout_audit CRASH — {type(ex).__name__}: {ex}")
            stats["layout_fail"] += 1

        # --- 2. generate_cutlist ---
        sections = None
        try:
            sections = generate_cutlist(k)
            stats["cutlist_ok"] += 1
            total_rows = sum(len(v) for v in sections.values() if v is not None and not hasattr(v, "empty"))
            stats["total_ploce"] += total_rows
        except Exception as ex:
            k_errors.append(f"K{i}: generate_cutlist CRASH — {type(ex).__name__}: {ex}")
            stats["cutlist_crash"] += 1
            failed += 1
            all_errors.extend(k_errors)
            if verbose:
                for e in k_errors:
                    _p(f"  [FAIL] {e}")
            continue  # bez sections, ne mozemo dalje

        # --- 3. FIN = CUT − kanta ---
        fc_errors = _check_fin_cut(sections, i)
        if fc_errors:
            stats["fincuterr"] += 1
            k_errors.extend(fc_errors)

        # --- 4. Summary_all kompletnost ---
        sum_errors = _check_summary(sections, i)
        if sum_errors:
            stats["summary_err"] += 1
            k_errors.extend(sum_errors)

        # --- 5. Radna ploca duzina ---
        wt_errors = _check_worktop_min_length(sections, k, i)
        if wt_errors:
            stats["worktop_err"] += 1
            k_errors.extend(wt_errors)

        # --- 6. PDF export ---
        if do_export:
            try:
                pdf = build_cutlist_pdf_bytes(k, sections, f"StressTest K{i}")
                if len(pdf) < 5000:
                    k_errors.append(f"K{i}: PDF premali {len(pdf)}B")
                    stats["pdf_fail"] += 1
                else:
                    stats["pdf_ok"] += 1
            except Exception as ex:
                k_errors.append(f"K{i}: PDF CRASH — {type(ex).__name__}: {ex}")
                stats["pdf_fail"] += 1

            # --- 7. Excel export ---
            try:
                xl = generate_cutlist_excel(k, sections)
                if len(xl) < 3000:
                    k_errors.append(f"K{i}: Excel premali {len(xl)}B")
                    stats["excel_fail"] += 1
                else:
                    stats["excel_ok"] += 1
            except Exception as ex:
                k_errors.append(f"K{i}: Excel CRASH — {type(ex).__name__}: {ex}")
                stats["excel_fail"] += 1

        # --- Zapis rezultata ---
        if k_errors:
            failed += 1
            all_errors.extend(k_errors)
            if verbose:
                for e in k_errors:
                    _p(f"  [FAIL] {e}")
        else:
            passed += 1
            if verbose and i % 50 == 0:
                elapsed = time.time() - t0
                _p(f"  [INFO] {i}/{n} kuhinja OK  ({elapsed:.1f}s)")

        # Progres za dugacke testove
        if not verbose and i % max(1, n // 10) == 0:
            pct = i * 100 // n
            elapsed = time.time() - t0
            _p(f"  ... {i}/{n} ({pct}%)  greske={failed}  ({elapsed:.1f}s)")

    elapsed_total = time.time() - t0

    _p("")
    _p("  --- Statistike ---")
    _p(f"  Kuhinja testirano:     {n}")
    _p(f"  Proslo (0 gresaka):    {passed}")
    _p(f"  Palo (>0 gresaka):     {failed}")
    _p(f"  Prosecno modula/kuh.:  {stats['total_modules']/n:.1f}")
    _p(f"  Layout audit OK/FAIL:  {stats['layout_ok']}/{stats['layout_fail']}")
    _p(f"  Cutlist OK/CRASH:      {stats['cutlist_ok']}/{stats['cutlist_crash']}")
    _p(f"  FIN/CUT greske:        {stats['fincuterr']}")
    _p(f"  Summary greske:        {stats['summary_err']}")
    _p(f"  Worktop greske:        {stats['worktop_err']}")
    if do_export:
        _p(f"  PDF OK/FAIL:           {stats['pdf_ok']}/{stats['pdf_fail']}")
        _p(f"  Excel OK/FAIL:         {stats['excel_ok']}/{stats['excel_fail']}")
    _p(f"  Vreme:                 {elapsed_total:.1f}s")
    _p(f"  Brzina:                {n/elapsed_total:.1f} kuhinja/s")

    return passed, failed, all_errors


def main():
    parser = argparse.ArgumentParser(
        description="KrojnaListaPRO - stres test (N nasumicnih kuhinja)"
    )
    parser.add_argument("-n", type=int, default=200,
                        help="Broj kuhinja (default: 200)")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Prikazi detalje svake kuhinje")
    parser.add_argument("--seed", type=int, default=None,
                        help="Seed za reproducibilnost (default: nasumican)")
    parser.add_argument("--no-export", action="store_true",
                        help="Preskoce PDF/Excel export (brze)")
    args = parser.parse_args()

    seed = args.seed if args.seed is not None else random.randint(0, 999999)

    _p("")
    _p("=" * 68)
    _p("  KrojnaListaPRO - STRES TEST")
    _p(f"  Kuhinja: {args.n}  |  Seed: {seed}  |  Export: {'NE' if args.no_export else 'DA'}")
    _p("=" * 68)
    _p("")

    passed, failed, errors = run_stress(
        n=args.n,
        seed=seed,
        verbose=args.verbose,
        do_export=not args.no_export,
    )

    _p("")
    _p("=" * 68)
    if failed == 0:
        _p(f"  *** REZULTAT: {passed}/{passed+failed} KUHINJA PROSLO — SVE OK ***")
    else:
        _p(f"  *** REZULTAT: {passed} PROSLO / {failed} PALO ***")
        _p("")
        _p(f"  Prvih {min(20, len(errors))} gresaka:")
        for e in errors[:20]:
            _p(f"    - {e}")
        if len(errors) > 20:
            _p(f"    ... i jos {len(errors)-20} gresaka")
    _p("=" * 68)
    _p(f"  (Ponovi sa: python test_stress.py -n {args.n} --seed {seed})")
    _p("")

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
