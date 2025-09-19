"""
Absfuyu: Data Analysis
----------------------
Data Analyst

Version: 5.8.0
Date updated: 16/09/2025 (dd/mm/yyyy)
"""

# Module level
# ---------------------------------------------------------------------------
__all__ = ["MatplotlibFormatString", "DADF"]


# Library
# ---------------------------------------------------------------------------
DA_MODE = False

try:
    import numpy as np
    import openpyxl
    import pandas as pd
    import xlsxwriter
except ImportError:
    from subprocess import run

    from absfuyu.config import ABSFUYU_CONFIG

    if ABSFUYU_CONFIG._get_setting("auto-install-extra").value:  # type: ignore
        cmd = "python -m pip install -U absfuyu[full]".split()
        run(cmd)
    else:
        raise SystemExit("This feature is in absfuyu[full] package")  # noqa: B904
else:
    DA_MODE = True

from absfuyu.extra.da.dadf import DADF
from absfuyu.extra.da.mplt import MatplotlibFormatString
