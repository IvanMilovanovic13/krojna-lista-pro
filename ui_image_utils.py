# -*- coding: utf-8 -*-
from __future__ import annotations

from io import BytesIO
import base64


def fig_to_data_uri_exact(fig) -> str:
    """Save without tight bbox so pixel dimensions stay deterministic."""
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=120)
    buf.seek(0)
    return f"data:image/png;base64,{base64.b64encode(buf.read()).decode('ascii')}"
