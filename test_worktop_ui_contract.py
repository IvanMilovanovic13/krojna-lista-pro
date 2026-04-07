# -*- coding: utf-8 -*-
from __future__ import annotations

import pandas as pd

from cutlist import get_final_cutlist_dataset
from test_export_consistency import build_sample_kitchen


def run_worktop_dataset_contract_check() -> tuple[bool, str]:
    final_ds = get_final_cutlist_dataset(build_sample_kitchen(), lang="en")
    worktop_df = final_ds["sections"].get("worktop", pd.DataFrame())
    if worktop_df is None or worktop_df.empty:
        return False, "worktop_section_missing"

    required_columns = {
        "Required length [mm]",
        "Purchase length [mm]",
        "Field cut",
        "Joint type",
        "Edge protection type",
        "Cutouts",
        "Napomena",
    }
    missing = [col for col in required_columns if col not in worktop_df.columns]
    if missing:
        return False, f"worktop_columns_missing:{','.join(sorted(missing))}"

    txt = " | ".join(worktop_df.astype(str).fillna("").values.flatten().tolist())
    if "Worktop" not in txt:
        return False, "worktop_row_missing"
    if "TRUE" not in txt:
        return False, "worktop_field_cut_flag_missing"
    return True, "ok"
