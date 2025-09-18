
"""
Created on Sun Sep 14 09:30:57 2025

@author: patrickilunga
"""


"""
iperform - Tableau de bord analytique dynamique pour telecom & banque

Conçu pour être simple, complet et communautaire.
Toutes les fonctions principales sont accessibles via `ip.fonction()`.

Pour les fonctionnalités avancées (prévision SARIMAX, narration, alertes),
voir `iperform_cloud` : https://www.ipgeodata.com
"""

# --- Version du package ---
__version__ = "0.1.0"

# --- Fonctions principales (exposées au niveau racine) ---
from .core import (
    get_summary_day,
    get_summary_month,
    get_summary_quarter,
    get_column_day,
    get_column_month,
    get_column_quarter,
    dday,
    mtd, qtd, ytd, htd, wtd,
    full_w, full_m, full_q, full_h, full_y,
    forecast_m
    )

# --- Plotting des KPIs ---
from .plotting import (
    graph_trend_day,
    plot_kpi,
    graph_season
    )

# --- Formatage des KPIs ---
from .formatting import format_kpi

# --- Utilitaires ---
from .utils import load_sample_data


# --- Contrôle de `from iperform import *` ---
__all__ = ["get_summary_day", "get_summary_month", "get_summary_quarter",
           "get_column_day", "get_column_month", "get_column_quarter",
           "graph_trend_day", "plot_kpi", "graph_season",
           "dday",
           "mtd", "qtd", "ytd", "htd", "wtd",
           "full_w", "full_m", "full_q", "full_h", "full_y",
           "forecast_m",
           "format_kpi",
           "load_sample_data",
           "__version__"
           ]