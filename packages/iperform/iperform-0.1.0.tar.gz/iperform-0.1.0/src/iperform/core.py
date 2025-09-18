
"""
Created on Sun Sep 14 09:57:39 2025

@author: 'patrick ILUNGA'
"""

from typing import Union
import pandas as pd
import numpy as np
from calendar import isleap

# from .formatting import format_kpi 


# ----------------------------------------------------------------------------------------------------------------------
# FUNCTION DDAY
# ----------------------------------------------------------------------------------------------------------------------

def dday(
    data: pd.DataFrame,
    date: str,
    x: str,
    d: int = 0,
    zone: str = 'RDC',
    factor: str = 'All_Factor',
    unite: float = 1,
    decimal: int = 0
    ) -> Union[float, int, None]:
    """
    Calcule la valeur d'une série numérique à une date spécifique (éventuellement décalée).
    Args :
        data (pd.DataFrame): DataFrame contenant au moins les colonnes 'date', 'zone', 'factor' et la série x.
        date (str): Date cible au format 'YYYY-MM-DD'.
        x (str): Nom de la colonne de la série à extraire.
        d (int): Décalage en jours par rapport à la date (ex: -1 pour hier). Par défaut 0.
        zone (str): Filtre par zone géographique. 'RDC' pour tout le pays. Par défaut 'RDC'.
        factor (str): Filtre par facteur (ex: opérateur, segment). 'All_Factor' = tous (sauf agrégats si besoin).
        unite (float): Diviseur pour ajuster l'échelle (ex: 1e6 pour millions). Par défaut 1.
        decimal (int): Nombre de décimales après arrondi. Par défaut 0.
    Returns:
        float, int ou None: Valeur de la série à la date décalée, divisée par `unite`, arrondie à `decimal` chiffres.
                            Retourne `None` si la date n'existe pas.

    Raises:
        ValueError: Si les colonnes manquent, si la date est invalide, etc.

    Example:
        >>> import pandas as pd
        >>> date = pd.date_range("2023-01-01", periods=222, freq="D")
        >>> x = np.random.normal(50, 6.3, 222)
        >>> df = pd.DataFrame({"date": date, "x": x, "zone": "RDC", "operator": "Orange"})
        >>> dday(df, date="2023-07-06", x="x", d=0, unite=1, decimal=2)
        48.23
    """
    # Validation des entrées
    if not isinstance(data, pd.DataFrame):
        raise ValueError("data doit être un DataFrame pandas.")

    if 'date' not in data.columns:
        raise ValueError("La colonne 'date' est manquante dans le DataFrame.")
    if x not in data.columns:
        raise ValueError(f"La colonne '{x}' est introuvable dans le DataFrame.")
    if zone != 'RDC' and 'zone' not in data.columns:
        raise ValueError("La colonne 'zone' est requise pour filtrer.")
    if factor != 'All_Factor' and 'factor' not in data.columns and 'operator' not in data.columns:
        raise ValueError("La colonne 'factor' ou 'operator' est requise pour filtrer.")

    # Convertir la colonne 'date' si nécessaire
    if not pd.api.types.is_datetime64_any_dtype(data['date']):
        data['date'] = pd.to_datetime(data['date'])

    # Appliquer les filtres
    filtered = data.copy()

    if zone != 'RDC':
        filtered = filtered[filtered['zone'] == zone]

    if factor == 'All_Factor':
        # Optionnel : exclure les lignes où factor est un agrégat (si pertinent)
        # Ex: filtered = filtered[filtered['factor'] != 'All_Factor']
        pass
    else:
        col_factor = 'factor' if 'factor' in filtered.columns else 'operator'
        filtered = filtered[filtered[col_factor] == factor]

    if filtered.empty:
        return None

    # Calculer la date cible
    target_date = pd.to_datetime(date) + pd.Timedelta(days=d)

    # Filtrer sur la date exacte
    mask = filtered['date'].dt.date == target_date.date()
    if mask.any():
        value = filtered.loc[mask, x].iloc[-1]  # Dernière valeur du jour si plusieurs
        return round(float(value / unite), decimal)
    else:
        return None  # Pas de données à cette date



# ----------------------------------------------------------------------------------------------------------------------
# FONCTION WTD
# ----------------------------------------------------------------------------------------------------------------------


def wtd(
    data,
    date: str,
    value: str,
    w: int = 0,
    zone: str = 'RDC',
    factor: str = 'All_Factor',
    unite: float = 1,
    decimal: int = 0,
    cumul: bool = False
    ) -> Union[float, int, None]:
    """
    Calcule le Week-to-Date (WTD) d'une série numérique.

    Par défaut, la semaine commence le **dimanche** (comme dans la version R).
    La fonction somme les valeurs depuis le dernier dimanche jusqu'à la date cible.

    Si `cumul=False` : somme des valeurs du début de la semaine jusqu'à la date.  
    Si `cumul=True` : prend la valeur exacte du jour cible (car déjà cumulée, ex: stock).

    Args:
        data (pd.DataFrame): DataFrame avec colonnes 'date', 'zone', 'factor' (ou 'operator'), et la variable.
        date (str): Date de fin de période (format 'YYYY-MM-DD').
        value (str): Nom de la colonne à analyser.
        w (int): Décalage en semaines par rapport à la semaine de la date. Ex: w=-1 → semaine précédente. Par défaut 0.
        zone (str): Filtre par zone géographique. 'RDC' = tout le pays. Par défaut 'RDC'.
        factor (str): Filtre par facteur (ex: opérateur). 'All_Factor' = tous.
        unite (float): Diviseur pour échelle (ex: 1e6 pour millions). Par défaut 1.
        decimal (int): Nombre de décimales après arrondi. Par défaut 0.
        cumul (bool): Si True, la série est déjà cumulée (stock), donc on prend la valeur du jour.  
                      Si False, on fait une somme (flux). Par défaut False.

    Returns:
        float, int ou None: Valeur WTD, divisée par `unite`, arrondie à `decimal` chiffres.  
                            Retourne `None` si aucune donnée.

    Example:
        >>> wtd(df, date="2023-08-01", value="revenu_usd")  # Du dimanche 30 juillet au mardi 1er août
        >>> wtd(df, date="2023-08-01", value="user_actif", cumul=True)  # Valeur du 1er août
        >>> wtd(df, date="2023-08-01", value="revenu_usd", w=-1)  # Semaine précédente
    """
    # Validation des entrées
    if not isinstance(data, pd.DataFrame):
        raise ValueError("data doit être un DataFrame pandas.")
    if 'date' not in data.columns:
        raise ValueError("La colonne 'date' est requise.")
    if value not in data.columns:
        raise ValueError(f"La colonne '{value}' est introuvable.")
    if zone != 'RDC' and 'zone' not in data.columns:
        raise ValueError("La colonne 'zone' est nécessaire pour filtrer.")
    if factor != 'All_Factor':
        col_factor = 'factor' if 'factor' in data.columns else 'operator'
        if col_factor not in data.columns:
            raise ValueError(f"La colonne '{col_factor}' est requise pour filtrer par factor.")

    # Convertir la colonne 'date' si nécessaire
    if not pd.api.types.is_datetime64_any_dtype(data['date']):
        data['date'] = pd.to_datetime(data['date'])

    target_date = pd.to_datetime(date)

    # Trouver le dimanche précédent (début de la semaine ISO)
    # En Python, Monday=0 → Dimanche=6
    day_of_week = target_date.dayofweek  # Lundi=0, Dimanche=6
    days_since_sunday = (day_of_week + 1) % 7  # Pour que dimanche=0
    start_of_week = target_date - pd.Timedelta(days=days_since_sunday)

    # Appliquer le décalage de semaine
    shifted_start = start_of_week + pd.Timedelta(weeks=w)
    end_date = shifted_start + pd.Timedelta(days=6)  # Fin de la semaine (samedi)

    # Filtrer les données
    filtered = data.copy()

    if zone != 'RDC':
        filtered = filtered[filtered['zone'] == zone]

    if factor != 'All_Factor':
        col_factor = 'factor' if 'factor' in filtered.columns else 'operator'
        filtered = filtered[filtered[col_factor] == factor]

    # Filtrer par plage de dates
    mask = (filtered['date'] >= shifted_start) & (filtered['date'] <= end_date)
    filtered = filtered[mask]

    if filtered.empty:
        return None

    # Calcul selon type de série
    if cumul:
        # Prendre la dernière valeur disponible à end_date (jour cible)
        day_mask = filtered['date'].dt.date == target_date.date()
        if day_mask.any():
            val = filtered.loc[day_mask, value].iloc[-1]
        else:
            return None
    else:
        # Somme des valeurs (flux)
        val = filtered[value].sum()

    return round(float(val / unite), decimal)




# ----------------------------------------------------------------------------------------------------------------------
# FUNCTION MTD
# ----------------------------------------------------------------------------------------------------------------------

def mtd(
    data: pd.DataFrame,
    date: str,
    value : str,
    m: int = 0,
    zone: str = 'RDC',
    factor: str = 'All_Factor',
    unite: float = 1,
    decimal: int = 0,
    cumul: bool = False
    ) -> Union[float, int, None]:
    """
    Calcule le Month-to-Date (MTD) d'une série numérique.

    Si `cumul=False` : somme des valeurs du 1er au jour cible du mois.  
    Si `cumul=True` : prend la valeur exacte du jour cible (car déjà cumulée, ex: base clients).

    Args:
        data (pd.DataFrame): DataFrame avec colonnes 'date', 'zone', 'factor', et la variable value.
        date (str): Date de fin de période (format 'YYYY-MM-DD').
        value (str): Nom de la colonne à analyser.
        m (int): Décalage en mois par rapport au mois de la date. Ex: m=-1 → mois précédent. Par défaut 0.
        zone (str): Filtre par zone géographique. 'RDC' = tout le pays. Par défaut 'RDC'.
        factor (str): Filtre par facteur (ex: opérateur). 'All_Factor' = tous (sauf agrégats si pertinent).
        unite (float): Diviseur pour échelle (ex: 1e6 pour millions). Par défaut 1.
        decimal (int): Nombre de décimales après arrondi. Par défaut 0.
        cumul (bool): Si True, la série est déjà cumulée (ex: stock), donc on prend la valeur du jour.  
                      Si False, on fait une somme (flux). Par défaut False.

    Returns:
        float, int ou None: Valeur MTD, divisée par `unite`, arrondie à `decimal` chiffres.  
                            Retourne `None` si aucune donnée.

    Example:
        >>> mtd(df, date="2023-08-04", value="revenu_usd")  # Somme du 1er au 4 août
        >>> mtd(df, date="2023-08-04", value="user_actif", cumul=True)  # Valeur du 4 août
        >>> mtd(df, date="2023-08-04", value="revenu_usd", m=-1)  # Jusqu'au 4 juillet
    """
    # Validation des entrées
    if not isinstance(data, pd.DataFrame):
        raise ValueError("data doit être un DataFrame pandas.")
    if 'date' not in data.columns:
        raise ValueError("La colonne 'date' est requise.")
    if x not in data.columns:
        raise ValueError(f"La colonne '{value}' est introuvable.")
    if zone != 'RDC' and 'zone' not in data.columns:
        raise ValueError("La colonne 'zone' est nécessaire pour filtrer.")
    if factor != 'All_Factor':
        col_factor = 'factor' if 'factor' in data.columns else 'operator'
        if col_factor not in data.columns:
            raise ValueError(f"La colonne '{col_factor}' est requise pour filtrer par factor.")

    # Convertir la date si nécessaire
    if not pd.api.types.is_datetime64_any_dtype(data['date']):
        data['date'] = pd.to_datetime(data['date'])

    target_date = pd.to_datetime(date)
    year_ref = target_date.year
    month_ref = target_date.month + m
    day_ref = target_date.day

    # Ajuster l'année si le mois sort de [1-12]
    if month_ref == 0:
        month_ref = 12
        year_ref -= 1
    elif month_ref > 12:
        month_ref = month_ref % 12
        year_ref += (target_date.month + m - 1) // 12

    # Gérer les dates invalides (ex: 30 février)
    try:
        end_date = pd.to_datetime(f"{year_ref}-{month_ref:02d}-{day_ref}")
    except ValueError:
        # Si le jour n'existe pas, prendre la fin du mois
        end_date = pd.to_datetime(f"{year_ref}-{month_ref:02d}-01") + pd.offsets.MonthEnd(0)
        day_ref = end_date.day

    # Filtrer par date : du 1er du mois à end_date inclus
    start_of_month = pd.to_datetime(f"{year_ref}-{month_ref:02d}-01")
    
    filtered = data.copy()

    # Appliquer les filtres
    if zone != 'RDC':
        filtered = filtered[filtered['zone'] == zone]

    if factor != 'All_Factor':
        col_factor = 'factor' if 'factor' in filtered.columns else 'operator'
        filtered = filtered[filtered[col_factor] == factor]

    # Filtrer par plage de dates
    mask = (filtered['date'] >= start_of_month) & (filtered['date'] <= end_date)
    filtered = filtered[mask]

    if filtered.empty:
        return None

    # Calcul selon type de série
    if cumul:
        # Prendre la dernière valeur disponible à day_ref (stock)
        day_mask = filtered['date'].dt.day == day_ref
        if day_mask.any():
            value = filtered.loc[day_mask, value].iloc[-1]  # Dernière valeur du jour
        else:
            return None
    else:
        # Somme des valeurs (flux)
        value = filtered[value].sum()

    return round(float(value / unite), decimal)



# ----------------------------------------------------------------------------------------------------------------------
# FONCTION QTD
# ----------------------------------------------------------------------------------------------------------------------

# iperform/core.py



def qtd(data, date: str, x: str, q: int = 0,
    zone: str = 'RDC',
    factor: str = 'All_Factor',
    unite: float = 1,
    decimal: int = 0,
    cumul: bool = False
    ) -> Union[float, int, None]:
    """
    Calcule le Quarter-to-Date (QTD) d'une série numérique.

    Si `cumul=False` : somme des valeurs du 1er jour du trimestre jusqu'à la date cible.  
    Si `cumul=True` : prend la valeur exacte du jour cible (car déjà cumulée, ex: base clients).

    Args:
        data (pd.DataFrame): DataFrame avec colonnes 'date', 'zone', 'factor' (ou 'operator'), et la variable x.
        date (str): Date de fin de période (format 'YYYY-MM-DD').
        x (str): Nom de la colonne à analyser.
        q (int): Décalage en trimestres par rapport au trimestre de la date. Ex: q=-1 → trimestre précédent. Par défaut 0.
        zone (str): Filtre par zone géographique. 'RDC' = tout le pays. Par défaut 'RDC'.
        factor (str): Filtre par facteur (ex: opérateur). 'All_Factor' = tous (sauf agrégats si pertinent).
        unite (float): Diviseur pour échelle (ex: 1e6 pour millions). Par défaut 1.
        decimal (int): Nombre de décimales après arrondi. Par défaut 0.
        cumul (bool): Si True, la série est déjà cumulée (stock), donc on prend la valeur du jour.  
                      Si False, on fait une somme (flux). Par défaut False.

    Returns:
        float, int ou None: Valeur QTD, divisée par `unite`, arrondie à `decimal` chiffres.  
                            Retourne `None` si aucune donnée.

    Example:
        >>> qtd(df, date="2023-07-06", x="revenu_usd")  # Somme du 1er avril au 6 juillet
        >>> qtd(df, date="2023-07-06", x="user_actif", cumul=True)  # Valeur du 6 juillet
        >>> qtd(df, date="2023-07-06", x="revenu_usd", q=-1)  # Jusqu'au 6 avril (T1)
    """
    # Validation des entrées
    if not isinstance(data, pd.DataFrame):
        raise ValueError("data doit être un DataFrame pandas.")
    if 'date' not in data.columns:
        raise ValueError("La colonne 'date' est requise.")
    if x not in data.columns:
        raise ValueError(f"La colonne '{x}' est introuvable.")
    if zone != 'RDC' and 'zone' not in data.columns:
        raise ValueError("La colonne 'zone' est nécessaire pour filtrer.")
    if factor != 'All_Factor':
        col_factor = 'factor' if 'factor' in data.columns else 'operator'
        if col_factor not in data.columns:
            raise ValueError(f"La colonne '{col_factor}' est requise pour filtrer par factor.")

    # Convertir la date si nécessaire
    if not pd.api.types.is_datetime64_any_dtype(data['date']):
        data['date'] = pd.to_datetime(data['date'])

    target_date = pd.to_datetime(date)
    year_ref = target_date.year
    month_ref = target_date.month
    day_of_year_ref = target_date.dayofyear

    # Calculer le trimestre de référence (1=jan-mar, etc.)
    quarter_ref = ((month_ref - 1) // 3) + 1
    shifted_quarter = quarter_ref + q

    # Ajuster année et trimestre
    while shifted_quarter < 1:
        shifted_quarter += 4
        year_ref -= 1
    while shifted_quarter > 4:
        shifted_quarter -= 4
        year_ref += 1

    # Déterminer le premier jour du trimestre ajusté
    start_day_by_quarter = {
        1: 1,           # 1er janvier
        2: 91 + (1 if isleap(year_ref) else 0),  # 1er avril
        3: 182 + (1 if isleap(year_ref) else 0), # 1er juillet
        4: 274 + (1 if isleap(year_ref) else 0)  # 1er octobre
        }
    start_doy = start_day_by_quarter[shifted_quarter]

    # Calculer le jour cible dans l'année (décalé proportionnellement)
    n_days_since_start = day_of_year_ref - (start_day_by_quarter[quarter_ref] if quarter_ref == quarter_ref else 0)
    target_doy = start_doy + n_days_since_start

    # Gérer les dépassements (ex: 366 en non-bissextile)
    max_doy = 366 if isleap(year_ref) else 365
    if target_doy > max_doy:
        target_doy = max_doy

    try:
        end_date = pd.to_datetime(f"{year_ref}-01-01") + pd.Timedelta(days=target_doy - 1)
        start_date = pd.to_datetime(f"{year_ref}-01-01") + pd.Timedelta(days=start_doy - 1)
    except ValueError:
        return None  # Cas très rare de date invalide

    # Filtrer les données
    filtered = data.copy()

    if zone != 'RDC':
        filtered = filtered[filtered['zone'] == zone]

    if factor != 'All_Factor':
        col_factor = 'factor' if 'factor' in filtered.columns else 'operator'
        filtered = filtered[filtered[col_factor] == factor]

    # Filtrer par plage de dates
    mask = (filtered['date'] >= start_date) & (filtered['date'] <= end_date)
    filtered = filtered[mask]

    if filtered.empty:
        return None

    # Calcul selon type de série
    if cumul:
        # Prendre la valeur exacte à end_date (jour cible)
        day_mask = filtered['date'].dt.date == end_date.date()
        if day_mask.any():
            value = filtered.loc[day_mask, x].iloc[-1]
        else:
            return None
    else:
        # Somme des valeurs (flux)
        value = filtered[x].sum()

    return round(float(value / unite), decimal)



# ----------------------------------------------------------------------------------------------------------------------
# FONCTION HTD
# ----------------------------------------------------------------------------------------------------------------------


def htd(
    data,
    date: str,
    value: str,  # ← Aligné sur 'value' au lieu de 'x'
    h: int = 0,
    zone: str = 'RDC',
    factor: str = 'All_Factor',
    unite: float = 1,
    decimal: int = 0,
    cumul: bool = False) -> Union[float, int, None]:
    """
    Calcule le Half-to-Date (HTD) d'une série numérique.

    Le semestre est défini comme :
      - Semestre 1 : 1er janvier → 30 juin
      - Semestre 2 : 1er juillet → 31 décembre

    Si `cumul=False` : somme des valeurs du 1er jour du semestre jusqu'à la date cible.  
    Si `cumul=True` : prend la valeur exacte du jour cible (car déjà cumulée, ex: base clients).

    Args:
        data (pd.DataFrame): DataFrame avec colonnes 'date', 'zone', 'factor' (ou 'operator'), et la variable.
        date (str): Date de fin de période (format 'YYYY-MM-DD').
        value (str): Nom de la colonne à analyser.
        h (int): Décalage en semestres par rapport au semestre de la date. Ex: h=-1 → semestre précédent. Par défaut 0.
        zone (str): Filtre par zone géographique. 'RDC' = tout le pays. Par défaut 'RDC'.
        factor (str): Filtre par facteur (ex: opérateur). 'All_Factor' = tous (sauf agrégats si pertinent).
        unite (float): Diviseur pour échelle (ex: 1e6 pour millions). Par défaut 1.
        decimal (int): Nombre de décimales après arrondi. Par défaut 0.
        cumul (bool): Si True, la série est déjà cumulée (stock), donc on prend la valeur du jour.  
                      Si False, on fait une somme (flux). Par défaut False.

    Returns:
        float, int ou None: Valeur HTD, divisée par `unite`, arrondie à `decimal` chiffres.  
                            Retourne `None` si aucune donnée.

    Example:
        >>> htd(df, date="2023-07-06", value="revenu_usd")  # Du 1er juillet au 6 juillet
        >>> htd(df, date="2023-07-06", value="user_actif", cumul=True)  # Valeur du 6 juil
        >>> htd(df, date="2023-07-06", value="revenu_usd", h=-1)  # T1 2023 (janvier–juin)
    """
    # Validation des entrées
    if not isinstance(data, pd.DataFrame):
        raise ValueError("data doit être un DataFrame pandas.")
    if 'date' not in data.columns:
        raise ValueError("La colonne 'date' est requise.")
    if value not in data.columns:
        raise ValueError(f"La colonne '{value}' est introuvable.")
    if zone != 'RDC' and 'zone' not in data.columns:
        raise ValueError("La colonne 'zone' est nécessaire pour filtrer.")
    if factor != 'All_Factor':
        col_factor = 'factor' if 'factor' in data.columns else 'operator'
        if col_factor not in data.columns:
            raise ValueError(f"La colonne '{col_factor}' est requise pour filtrer par factor.")

    # Convertir la colonne 'date' si nécessaire
    if not pd.api.types.is_datetime64_any_dtype(data['date']):
        data['date'] = pd.to_datetime(data['date'])

    target_date = pd.to_datetime(date)
    year_ref = target_date.year
    month_ref = target_date.month
    day_of_year_ref = target_date.dayofyear

    # Déterminer le semestre de référence
    semester_ref = 1 if month_ref <= 6 else 2
    shifted_semester = semester_ref + h

    # Ajuster l'année et le semestre
    while shifted_semester < 1:
        shifted_semester += 2
        year_ref -= 1
    while shifted_semester > 2:
        shifted_semester -= 2
        year_ref += 1

    # Jour de l'année du début du semestre ajusté
    is_leap = (year_ref % 4 == 0 and year_ref % 100 != 0) or (year_ref % 400 == 0)
    start_doy = 1 if shifted_semester == 1 else 182 + (1 if is_leap else 0)  # 1er juillet

    # Calculer la date cible dans l'année (proportionnelle)
    current_start_doy = 1 if semester_ref == 1 else 182 + (1 if (year_ref == target_date.year and is_leap) else 0)
    n_days_since_start = day_of_year_ref - current_start_doy
    target_doy = start_doy + n_days_since_start

    # Gérer les dépassements
    max_doy = 366 if is_leap else 365
    if target_doy > max_doy:
        target_doy = max_doy

    try:
        start_date = pd.to_datetime(f"{year_ref}-01-01") + pd.Timedelta(days=start_doy - 1)
        end_date = pd.to_datetime(f"{year_ref}-01-01") + pd.Timedelta(days=target_doy - 1)
    except ValueError:
        return None

    # Filtrer les données
    filtered = data.copy()

    if zone != 'RDC':
        filtered = filtered[filtered['zone'] == zone]

    if factor != 'All_Factor':
        col_factor = 'factor' if 'factor' in filtered.columns else 'operator'
        filtered = filtered[filtered[col_factor] == factor]

    # Filtrer par plage de dates
    mask = (filtered['date'] >= start_date) & (filtered['date'] <= end_date)
    filtered = filtered[mask]

    if filtered.empty:
        return None

    # Calcul selon type de série
    if cumul:
        # Prendre la valeur exacte à end_date
        day_mask = filtered['date'].dt.date == end_date.date()
        if day_mask.any():
            val = filtered.loc[day_mask, value].iloc[-1]
        else:
            return None
    else:
        # Somme des valeurs (flux)
        val = filtered[value].sum()

    return round(float(val / unite), decimal)



# ----------------------------------------------------------------------------------------------------------------------
# FONCTION YTD
# ----------------------------------------------------------------------------------------------------------------------


def ytd(
    data,
    date: str,
    value: str,  # ← Changé de 'x' à 'value' pour alignement
    a: int = 0,
    zone: str = 'RDC',
    factor: str = 'All_Factor',
    unite: float = 1,
    decimal: int = 0,
    cumul: bool = False) -> Union[float, int, None]:
    """
    Calcule le Year-to-Date (YTD) d'une série numérique.

    Si `cumul=False` : somme des valeurs du 1er janvier jusqu'à la date cible.  
    Si `cumul=True` : prend la valeur exacte du jour cible (car déjà cumulée, ex: base clients).

    Args:
        data (pd.DataFrame): DataFrame avec colonnes 'date', 'zone', 'factor' (ou 'operator'), et la variable.
        date (str): Date de fin de période (format 'YYYY-MM-DD').
        value (str): Nom de la colonne à analyser (anciennement 'x').
        a (int): Décalage en années par rapport à l'année de la date. Ex: a=-1 → année précédente. Par défaut 0.
        zone (str): Filtre par zone géographique. 'RDC' = tout le pays. Par défaut 'RDC'.
        factor (str): Filtre par facteur (ex: opérateur). 'All_Factor' = tous (sauf agrégats si pertinent).
        unite (float): Diviseur pour échelle (ex: 1e6 pour millions). Par défaut 1.
        decimal (int): Nombre de décimales après arrondi. Par défaut 0.
        cumul (bool): Si True, la série est déjà cumulée (stock), donc on prend la valeur du jour.  
                      Si False, on fait une somme (flux). Par défaut False.

    Returns:
        float, int ou None: Valeur YTD, divisée par `unite`, arrondie à `decimal` chiffres.  
                            Retourne `None` si aucune donnée.

    Example:
        >>> ytd(df, date="2023-01-08", value="revenu_usd")  # Somme du 1er janv au 8 janv 2023
        >>> ytd(df, date="2023-01-08", value="user_actif", cumul=True)  # Valeur du 8 janv
        >>> ytd(df, date="2023-01-08", value="revenu_usd", a=-1)  # Jusqu'au 8 janv 2022
    """
    # Validation des entrées
    if not isinstance(data, pd.DataFrame):
        raise ValueError("data doit être un DataFrame pandas.")
    if 'date' not in data.columns:
        raise ValueError("La colonne 'date' est requise.")
    if value not in data.columns:
        raise ValueError(f"La colonne '{value}' est introuvable.")
    if zone != 'RDC' and 'zone' not in data.columns:
        raise ValueError("La colonne 'zone' est nécessaire pour filtrer.")
    if factor != 'All_Factor':
        col_factor = 'factor' if 'factor' in data.columns else 'operator'
        if col_factor not in data.columns:
            raise ValueError(f"La colonne '{col_factor}' est requise pour filtrer par factor.")

    # Convertir la colonne 'date' si nécessaire
    if not pd.api.types.is_datetime64_any_dtype(data['date']):
        data['date'] = pd.to_datetime(data['date'])

    target_date = pd.to_datetime(date)
    year_ref = target_date.year + a  # Année décalée

    try:
        end_date = pd.to_datetime(f"{year_ref}-{target_date.month:02d}-{target_date.day:02d}")
    except ValueError:
        # Gérer les dates invalides (ex: 29 février hors bissextile)
        end_date = pd.to_datetime(f"{year_ref}-01-01") + pd.offsets.MonthEnd(0)  # Dernier jour du mois

    start_date = pd.to_datetime(f"{year_ref}-01-01")

    # Filtrer les données
    filtered = data.copy()

    if zone != 'RDC':
        filtered = filtered[filtered['zone'] == zone]

    if factor != 'All_Factor':
        col_factor = 'factor' if 'factor' in filtered.columns else 'operator'
        filtered = filtered[filtered[col_factor] == factor]

    # Filtrer par plage de dates
    mask = (filtered['date'] >= start_date) & (filtered['date'] <= end_date)
    filtered = filtered[mask]

    if filtered.empty:
        return None

    # Calcul selon type de série
    if cumul:
        # Prendre la dernière valeur disponible à end_date (jour cible)
        day_mask = filtered['date'].dt.date == end_date.date()
        if day_mask.any():
            val = filtered.loc[day_mask, value].iloc[-1]
        else:
            return None
    else:
        # Somme des valeurs (flux)
        val = filtered[value].sum()

    return round(float(val / unite), decimal)



# ----------------------------------------------------------------------------------------------------------------------
# FONCTION FULL WEEK
# ----------------------------------------------------------------------------------------------------------------------

# iperform/core.py


def full_w(
    data,
    date: str,
    value: str,
    w: int = 0,
    zone: str = 'RDC',
    factor: str = 'All_Factor',
    unite: float = 1,
    decimal: int = 0,
    cumul: bool = False) -> Union[float, int, None] :
    """
    Calcule la performance complète d'une semaine (Full Week).

    Par défaut, la semaine commence le dimanche.
    La fonction agrège toutes les valeurs de la semaine contenant la date donnée (décalée par `w`).

    Si `cumul=False` : somme des valeurs sur toute la semaine.  
    Si `cumul=True` : prend la valeur du **dernier jour de la semaine** (samedi), car stock cumulé.

    Args:
        data (pd.DataFrame): DataFrame avec colonnes 'date', 'zone', 'factor' (ou 'operator'), et la variable.
        date (str): Date servant à identifier la semaine cible (format 'YYYY-MM-DD').
        value (str): Nom de la colonne à analyser.
        w (int): Décalage en semaines. Ex: w=-1 → semaine précédente. Par défaut 0.
        zone (str): Filtre par zone géographique. 'RDC' = tout le pays. Par défaut 'RDC'.
        factor (str): Filtre par facteur (ex: opérateur). 'All_Factor' = tous.
        unite (float): Diviseur pour échelle (ex: 1e6 pour millions). Par défaut 1.
        decimal (int): Nombre de décimales après arrondi. Par défaut 0.
        cumul (bool): Si True, la série est cumulée (stock), donc on prend la valeur du dernier jour.  
                      Si False, on fait une somme (flux). Par défaut False.

    Returns:
        float, int ou None: Valeur totale de la semaine, divisée par `unite`, arrondie à `decimal` chiffres.  
                            Retourne `None` si aucune donnée.

    Example:
        >>> full_w(df, date="2023-01-08", value="revenu_usd")  # Semaine du 7 au 13 janvier
        >>> full_w(df, date="2023-01-08", value="user_actif", cumul=True)  # Valeur du samedi
        >>> full_w(df, date="2023-01-08", value="revenu_usd", w=-1)  # Semaine précédente
    """
    # Validation des entrées
    if not isinstance(data, pd.DataFrame):
        raise ValueError("data doit être un DataFrame pandas.")
    if 'date' not in data.columns:
        raise ValueError("La colonne 'date' est requise.")
    if value not in data.columns:
        raise ValueError(f"La colonne '{value}' est introuvable.")
    if zone != 'RDC' and 'zone' not in data.columns:
        raise ValueError("La colonne 'zone' est nécessaire pour filtrer.")
    if factor != 'All_Factor':
        col_factor = 'factor' if 'factor' in data.columns else 'operator'
        if col_factor not in data.columns:
            raise ValueError(f"La colonne '{col_factor}' est requise pour filtrer par factor.")

    # Convertir la colonne 'date' si nécessaire
    if not pd.api.types.is_datetime64_any_dtype(data['date']):
        data['date'] = pd.to_datetime(data['date'])

    target_date = pd.to_datetime(date)

    # Trouver le dimanche de la semaine (début)
    day_of_week = target_date.dayofweek  # Lundi=0, Dimanche=6
    days_since_sunday = (day_of_week + 1) % 7
    start_of_week = target_date - pd.Timedelta(days=days_since_sunday)
    
    # Appliquer le décalage
    shifted_start = start_of_week + pd.Timedelta(weeks=w)
    shifted_end = shifted_start + pd.Timedelta(days=6)  # Samedi suivant

    # Filtrer les données
    filtered = data.copy()

    if zone != 'RDC':
        filtered = filtered[filtered['zone'] == zone]

    if factor != 'All_Factor':
        col_factor = 'factor' if 'factor' in filtered.columns else 'operator'
        filtered = filtered[filtered[col_factor] == factor]

    # Filtrer par plage de dates
    mask = (filtered['date'] >= shifted_start) & (filtered['date'] <= shifted_end)
    filtered = filtered[mask]

    if filtered.empty:
        return None

    # Calcul selon type de série
    if cumul:
        # Prendre la dernière valeur disponible dans la semaine (généralement samedi)
        last_day_in_week = filtered['date'].max()
        day_mask = filtered['date'].dt.date == last_day_in_week.date()
        if day_mask.any():
            val = filtered.loc[day_mask, value].iloc[-1]
        else:
            return None
    else:
        # Somme des valeurs (flux)
        val = filtered[value].sum()

    return round(float(val / unite), decimal)


# ----------------------------------------------------------------------------------------------------------------------
# FONCTION FULL MONTH
# ----------------------------------------------------------------------------------------------------------------------


def full_m(
    data,
    date: str,
    value: str,
    m: int = 0,
    zone: str = 'RDC',
    factor: str = 'All_Factor',
    unite: float = 1,
    decimal: int = 0,
    cumul: bool = False) -> Union[float, int, None]:
    """
    Calcule la performance complète d'un mois (Full Month).
    Si `cumul=False` : somme des valeurs sur tout le mois.
    Si `cumul=True` : prend la valeur du dernier jour du mois.
    """
    # Validation des entrées (inchangée)
    if not isinstance(data, pd.DataFrame):
        raise ValueError("data doit être un DataFrame pandas.")
    if 'date' not in data.columns:
        raise ValueError("La colonne 'date' est requise.")
    if value not in data.columns:
        raise ValueError(f"La colonne '{value}' est introuvable.")
    if zone != 'RDC' and 'zone' not in data.columns:
        raise ValueError("La colonne 'zone' est nécessaire pour filtrer.")
    if factor != 'All_Factor':
        col_factor = 'factor' if 'factor' in data.columns else 'operator'
        if col_factor not in data.columns:
            raise ValueError(f"La colonne '{col_factor}' est requise pour filtrer par factor.")

    # Convertir la colonne 'date' si nécessaire
    if not pd.api.types.is_datetime64_any_dtype(data['date']):
        data['date'] = pd.to_datetime(data['date'])

    target_date = pd.to_datetime(date)
    year_ref = target_date.year
    month_ref = target_date.month + m

    # Ajuster l'année si nécessaire
    while month_ref < 1:
        month_ref += 12
        year_ref -= 1
    while month_ref > 12:
        month_ref -= 12
        year_ref += 1

    # Définir les bornes du mois
    start_date = pd.to_datetime(f"{year_ref}-{month_ref:02d}-01")
    end_date = start_date + pd.offsets.MonthEnd(0)  # Dernier jour du mois

    # Filtrer les données
    filtered = data.copy()

    if zone != 'RDC':
        filtered = filtered[filtered['zone'] == zone]

    if factor != 'All_Factor':
        col_factor = 'factor' if 'factor' in filtered.columns else 'operator'
        filtered = filtered[filtered[col_factor] == factor]

    # Filtrer par plage de dates
    mask = (filtered['date'] >= start_date) & (filtered['date'] <= end_date)
    filtered = filtered[mask]

    if filtered.empty:
        return None

    # Calcul selon type de série
    if cumul:
        # Prendre la dernière valeur disponible dans le mois
        last_day_in_month = filtered['date'].max()
        day_mask = filtered['date'].dt.date == last_day_in_month.date()
        if day_mask.any():
            val = filtered.loc[day_mask, value].iloc[-1]
        else:
            return None
    else:
        # Somme des valeurs (flux)
        val = filtered[value].sum()

    return round(float(val / unite), decimal)


# ----------------------------------------------------------------------------------------------------------------------
# FONCTION FULL QUARTER
# ----------------------------------------------------------------------------------------------------------------------


def full_q(
    data,
    date: str,
    value: str,
    q: int = 0,
    zone: str = 'RDC',
    factor: str = 'All_Factor',
    unite: float = 1,
    decimal: int = 0,
    cumul: bool = False) -> Union[float, int, None]:
    """
    Calcule la performance complète d'un trimestre (Full Quarter).

    Si `cumul=False` : somme des valeurs sur tout le trimestre.  
    Si `cumul=True` : prend la valeur du **dernier jour du trimestre** (car déjà cumulée, ex: base clients).

    Args:
        data (pd.DataFrame): DataFrame avec colonnes 'date', 'zone', 'factor' (ou 'operator'), et la variable.
        date (str): Date servant à identifier le trimestre cible (format 'YYYY-MM-DD').
        value (str): Nom de la colonne à analyser.
        q (int): Décalage en trimestres. Ex: q=-1 → trimestre précédent. Par défaut 0.
        zone (str): Filtre par zone géographique. 'RDC' = tout le pays. Par défaut 'RDC'.
        factor (str): Filtre par facteur (ex: opérateur). 'All_Factor' = tous.
        unite (float): Diviseur pour échelle (ex: 1e6 pour millions). Par défaut 1.
        decimal (int): Nombre de décimales après arrondi. Par défaut 0.
        cumul (bool): Si True, la série est cumulée (stock), donc on prend la valeur du dernier jour.  
                      Si False, on fait une somme (flux). Par défaut False.

    Returns:
        float, int ou None: Valeur totale du trimestre, divisée par `unite`, arrondie à `decimal` chiffres.  
                            Retourne `None` si aucune donnée.

    Example:
        >>> full_q(df, date="2023-01-08", value="revenu_usd")  # T1 2023 complet
        >>> full_q(df, date="2023-01-08", value="user_actif", cumul=True)  # Valeur du 31 mars
        >>> full_q(df, date="2023-01-08", value="revenu_usd", q=-1)  # T4 2022
    """
    # Validation des entrées
    if not isinstance(data, pd.DataFrame):
        raise ValueError("data doit être un DataFrame pandas.")
    if 'date' not in data.columns:
        raise ValueError("La colonne 'date' est requise.")
    if value not in data.columns:
        raise ValueError(f"La colonne '{value}' est introuvable.")
    if zone != 'RDC' and 'zone' not in data.columns:
        raise ValueError("La colonne 'zone' est nécessaire pour filtrer.")
    if factor != 'All_Factor':
        col_factor = 'factor' if 'factor' in data.columns else 'operator'
        if col_factor not in data.columns:
            raise ValueError(f"La colonne '{col_factor}' est requise pour filtrer par factor.")

    # Convertir la colonne 'date' si nécessaire
    if not pd.api.types.is_datetime64_any_dtype(data['date']):
        data['date'] = pd.to_datetime(data['date'])

    target_date = pd.to_datetime(date)
    year_ref = target_date.year
    month_ref = target_date.month
    quarter_ref = ((month_ref - 1) // 3) + 1
    shifted_quarter = quarter_ref + q

    # Ajuster année et trimestre
    while shifted_quarter < 1:
        shifted_quarter += 4
        year_ref -= 1
    while shifted_quarter > 4:
        shifted_quarter -= 4
        year_ref += 1

    # Définir les bornes du trimestre
    start_month_by_quarter = {1: 1, 2: 4, 3: 7, 4: 10}
    start_month = start_month_by_quarter[shifted_quarter]
    
    start_date = pd.to_datetime(f"{year_ref}-{start_month:02d}-01")
    end_date = start_date + pd.offsets.MonthEnd(3)  # Fin du 3e mois du trimestre

    # Filtrer les données
    filtered = data.copy()

    if zone != 'RDC':
        filtered = filtered[filtered['zone'] == zone]

    if factor != 'All_Factor':
        col_factor = 'factor' if 'factor' in filtered.columns else 'operator'
        filtered = filtered[filtered[col_factor] == factor]

    # Filtrer par plage de dates
    mask = (filtered['date'] >= start_date) & (filtered['date'] <= end_date)
    filtered = filtered[mask]

    if filtered.empty:
        return None

    # Calcul selon type de série
    if cumul:
        # Prendre la dernière valeur disponible dans le trimestre
        last_day_in_quarter = filtered['date'].max()
        day_mask = filtered['date'].dt.date == last_day_in_quarter.date()
        if day_mask.any():
            val = filtered.loc[day_mask, value].iloc[-1]
        else:
            return None
    else:
        # Somme des valeurs (flux)
        val = filtered[value].sum()

    return round(float(val / unite), decimal)


# ----------------------------------------------------------------------------------------------------------------------
# FONCTION FULL HALF
# ----------------------------------------------------------------------------------------------------------------------


def full_h(
    data,
    date: str,
    value: str,  # ← Aligné sur 'value' au lieu de 'x'
    h: int = 0,
    zone: str = 'RDC',
    factor: str = 'All_Factor',
    unite: float = 1,
    decimal: int = 0,
    cumul: bool = False) -> Union[float, int, None]:
    """
    Calcule la performance complète d'un semestre (Full Semester).

    Si `cumul=False` : somme des valeurs sur tout le semestre.  
    Si `cumul=True` : prend la valeur du **dernier jour du semestre** (car déjà cumulée, ex: base clients).

    Semestre 1 : 1er janvier → 30 juin  
    Semestre 2 : 1er juillet → 31 décembre

    Args:
        data (pd.DataFrame): DataFrame avec colonnes 'date', 'zone', 'factor' (ou 'operator'), et la variable.
        date (str): Date servant à identifier le semestre cible (format 'YYYY-MM-DD').
        value (str): Nom de la colonne à analyser.
        h (int): Décalage en semestres. Ex: h=-1 → semestre précédent. Par défaut 0.
        zone (str): Filtre par zone géographique. 'RDC' = tout le pays. Par défaut 'RDC'.
        factor (str): Filtre par facteur (ex: opérateur). 'All_Factor' = tous.
        unite (float): Diviseur pour échelle (ex: 1e6 pour millions). Par défaut 1.
        decimal (int): Nombre de décimales après arrondi. Par défaut 0.
        cumul (bool): Si True, la série est cumulée (stock), donc on prend la valeur du dernier jour.  
                      Si False, on fait une somme (flux). Par défaut False.

    Returns:
        float, int ou None: Valeur totale du semestre, divisée par `unite`, arrondie à `decimal` chiffres.  
                            Retourne `None` si aucune donnée.

    Example:
        >>> full_h(df, date="2023-01-08", value="revenu_usd")  # S1 2023 complet
        >>> full_h(df, date="2023-01-08", value="user_actif", cumul=True)  # Valeur du 30 juin
        >>> full_h(df, date="2023-01-08", value="revenu_usd", h=1)  # S2 2023
    """
    # Validation des entrées
    if not isinstance(data, pd.DataFrame):
        raise ValueError("data doit être un DataFrame pandas.")
    if 'date' not in data.columns:
        raise ValueError("La colonne 'date' est requise.")
    if value not in data.columns:
        raise ValueError(f"La colonne '{value}' est introuvable.")
    if zone != 'RDC' and 'zone' not in data.columns:
        raise ValueError("La colonne 'zone' est nécessaire pour filtrer.")
    if factor != 'All_Factor':
        col_factor = 'factor' if 'factor' in data.columns else 'operator'
        if col_factor not in data.columns:
            raise ValueError(f"La colonne '{col_factor}' est requise pour filtrer par factor.")

    # Convertir la colonne 'date' si nécessaire
    if not pd.api.types.is_datetime64_any_dtype(data['date']):
        data['date'] = pd.to_datetime(data['date'])

    target_date = pd.to_datetime(date)
    year_ref = target_date.year
    month_ref = target_date.month
    semester_ref = 1 if month_ref <= 6 else 2
    shifted_semester = semester_ref + h

    # Ajuster année et semestre
    while shifted_semester < 1:
        shifted_semester += 2
        year_ref -= 1
    while shifted_semester > 2:
        shifted_semester -= 2
        year_ref += 1

    # Définir les bornes du semestre
    if shifted_semester == 1:
        start_date = pd.to_datetime(f"{year_ref}-01-01")
        end_date = pd.to_datetime(f"{year_ref}-06-30")
    else:  # semestre 2
        start_date = pd.to_datetime(f"{year_ref}-07-01")
        end_date = pd.to_datetime(f"{year_ref}-12-31")

    # Filtrer les données
    filtered = data.copy()

    if zone != 'RDC':
        filtered = filtered[filtered['zone'] == zone]

    if factor != 'All_Factor':
        col_factor = 'factor' if 'factor' in filtered.columns else 'operator'
        filtered = filtered[filtered[col_factor] == factor]

    # Filtrer par plage de dates
    mask = (filtered['date'] >= start_date) & (filtered['date'] <= end_date)
    filtered = filtered[mask]

    if filtered.empty:
        return None

    # Calcul selon type de série
    if cumul:
        # Prendre la dernière valeur disponible dans le semestre
        last_day_in_semester = filtered['date'].max()
        day_mask = filtered['date'].dt.date == last_day_in_semester.date()
        if day_mask.any():
            val = filtered.loc[day_mask, value].iloc[-1]
        else:
            return None
    else:
        # Somme des valeurs (flux)
        val = filtered[value].sum()

    return round(float(val / unite), decimal)




# ----------------------------------------------------------------------------------------------------------------------
# FONCTION FULL YEAR
# ----------------------------------------------------------------------------------------------------------------------


def full_y(
    data,
    date: str,
    value: str,  # ← Aligné sur 'value' au lieu de 'x'
    a: int = 0,
    zone: str = 'RDC',
    factor: str = 'All_Factor',
    unite: float = 1,
    decimal: int = 0,
    cumul: bool = False
    ) -> Union[float, int, None]:
    """
    Calcule la performance complète d'une année (Full Year).

    Si `cumul=False` : somme des valeurs sur toute l'année.  
    Si `cumul=True` : prend la valeur du **dernier jour de l'année** (31 décembre), car déjà cumulée (ex: base clients).

    Args:
        data (pd.DataFrame): DataFrame avec colonnes 'date', 'zone', 'factor' (ou 'operator'), et la variable.
        date (str): Date servant à identifier l'année cible (format 'YYYY-MM-DD').
        value (str): Nom de la colonne à analyser.
        a (int): Décalage en années. Ex: a=-1 → année précédente. Par défaut 0.
        zone (str): Filtre par zone géographique. 'RDC' = tout le pays. Par défaut 'RDC'.
        factor (str): Filtre par facteur (ex: opérateur). 'All_Factor' = tous.
        unite (float): Diviseur pour échelle (ex: 1e6 pour millions). Par défaut 1.
        decimal (int): Nombre de décimales après arrondi. Par défaut 0.
        cumul (bool): Si True, la série est cumulée (stock), donc on prend la valeur du dernier jour.  
                      Si False, on fait une somme (flux). Par défaut False.

    Returns:
        float, int ou None: Valeur totale de l'année, divisée par `unite`, arrondie à `decimal` chiffres.  
                            Retourne `None` si aucune donnée.

    Example:
        >>> full_y(df, date="2023-01-08", value="revenu_usd")  # Année 2023 complète
        >>> full_y(df, date="2023-01-08", value="user_actif", cumul=True)  # Valeur du 31/12/2023
        >>> full_y(df, date="2023-01-08", value="revenu_usd", a=-1)  # Année 2022
    """
    # Validation des entrées
    if not isinstance(data, pd.DataFrame):
        raise ValueError("data doit être un DataFrame pandas.")
    if 'date' not in data.columns:
        raise ValueError("La colonne 'date' est requise.")
    if value not in data.columns:
        raise ValueError(f"La colonne '{value}' est introuvable.")
    if zone != 'RDC' and 'zone' not in data.columns:
        raise ValueError("La colonne 'zone' est nécessaire pour filtrer.")
    if factor != 'All_Factor':
        col_factor = 'factor' if 'factor' in data.columns else 'operator'
        if col_factor not in data.columns:
            raise ValueError(f"La colonne '{col_factor}' est requise pour filtrer par factor.")

    # Convertir la colonne 'date' si nécessaire
    if not pd.api.types.is_datetime64_any_dtype(data['date']):
        data['date'] = pd.to_datetime(data['date'])

    target_date = pd.to_datetime(date)
    year_ref = target_date.year + a  # Année décalée

    # Définir les bornes de l'année
    start_date = pd.to_datetime(f"{year_ref}-01-01")
    end_date = pd.to_datetime(f"{year_ref}-12-31")

    # Filtrer les données
    filtered = data.copy()

    if zone != 'RDC':
        filtered = filtered[filtered['zone'] == zone]

    if factor != 'All_Factor':
        col_factor = 'factor' if 'factor' in filtered.columns else 'operator'
        filtered = filtered[filtered[col_factor] == factor]

    # Filtrer par plage de dates
    mask = (filtered['date'] >= start_date) & (filtered['date'] <= end_date)
    filtered = filtered[mask]

    if filtered.empty:
        return None

    # Calcul selon type de série
    if cumul:
        # Prendre la dernière valeur disponible dans l'année (idéalement 31/12)
        last_day_in_year = filtered['date'].max()
        day_mask = filtered['date'].dt.date == last_day_in_year.date()
        if day_mask.any():
            val = filtered.loc[day_mask, value].iloc[-1]
        else:
            return None
    else:
        # Somme des valeurs (flux)
        val = filtered[value].sum()

    return round(float(val / unite), decimal)



# ----------------------------------------------------------------------------------------------------------------------
# FONCTION FORECAST_M
# ----------------------------------------------------------------------------------------------------------------------


def forecast_m(
    data,
    date: str,
    value: str,
    zone: str = 'RDC',
    factor: str = 'All_Factor',
    unite: float = 1,
    decimal: int = 0,
    cumul: bool = False
    ) -> Union[float, int, None] :
    """
    Estime le total mensuel complet à partir du MTD (Month-to-Date) et du nombre de jours restants.

    Méthode : projection linéaire basée sur la moyenne journalière observée.
    Ex: Si on a 300k de revenu en 15 jours → projection = 300k + (300k / 15) * 15 = 600k

    Args:
        data (pd.DataFrame): DataFrame avec colonnes 'date', 'zone', 'factor', et la variable.
        date (str): Date de référence (format 'YYYY-MM-DD').
        value (str): Nom de la colonne à projeter.
        zone (str): Filtre par zone géographique. 'RDC' = tout le pays. Par défaut 'RDC'.
        factor (str): Filtre par facteur (ex: opérateur). 'All_Factor' = tous.
        unite (float): Diviseur pour échelle (ex: 1e6 pour millions). Par défaut 1.
        decimal (int): Nombre de décimales après arrondi. Par défaut 0.
        cumul (bool): Si True, la série est cumulée (ex: stock), donc on utilise la valeur du jour.  
                      Si False, on somme (flux). Par défaut False.

    Returns:
        float, int ou None: Projection du total mensuel, divisée par `unite`, arrondie à `decimal` chiffres.  
                            Retourne `None` si impossible à calculer.

    Example:
        >>> forecast_m(df, date="2023-01-25", value="revenu_usd")  # Projection du mois de janvier
        >>> forecast_m(df, date="2023-01-25", value="user_actif", cumul=True)  # Pour stocks
    """
    # Validation des entrées
    if not isinstance(data, pd.DataFrame):
        raise ValueError("data doit être un DataFrame pandas.")
    if 'date' not in data.columns:
        raise ValueError("La colonne 'date' est requise.")
    if value not in data.columns:
        raise ValueError(f"La colonne '{value}' est introuvable.")
    if zone != 'RDC' and 'zone' not in data.columns:
        raise ValueError("La colonne 'zone' est nécessaire pour filtrer.")
    if factor != 'All_Factor':
        col_factor = 'factor' if 'factor' in data.columns else 'operator'
        if col_factor not in data.columns:
            raise ValueError(f"La colonne '{col_factor}' est requise pour filtrer par factor.")

    # Convertir la date si nécessaire
    if not pd.api.types.is_datetime64_any_dtype(data['date']):
        data['date'] = pd.to_datetime(data['date'])

    target_date = pd.to_datetime(date)
    year_ref = target_date.year
    month_ref = target_date.month
    day_ref = target_date.day

    # Calculer le nombre de jours dans le mois
    if month_ref == 2:
        if (year_ref % 4 == 0 and year_ref % 100 != 0) or (year_ref % 400 == 0):
            nb_jr = 29  # Année bissextile
        else:
            nb_jr = 28
    elif month_ref in [4, 6, 9, 11]:
        nb_jr = 30
    else:
        nb_jr = 31

    jours_observes = day_ref
    jours_restants = nb_jr - jours_observes

    if jours_observes == 0:
        return None

    # Utiliser la fonction mtd() déjà définie
    mtd_value = mtd(data, date = date, value=value, zone=zone, factor=factor, cumul=cumul)

    if mtd_value is None or mtd_value == 0:
        return None

    # Projection linéaire : MTD + (MTD / jours_passés) * jours_restants
    daily_avg = mtd_value / jours_observes
    forecasted = mtd_value + (daily_avg * jours_restants)

    return round(float(forecasted / unite), decimal)





# ----------------------------------------------------------------------------------------------------------------------
# FONCTION GET SUMMARY DAY
# ----------------------------------------------------------------------------------------------------------------------



def get_summary_day(df, date='last', zone='RDC', operator='All_Operator', devise='USD', value='revenu', unit=1):
    """
    Calcule 8 indicateurs journaliers dynamiques selon la date de référence.

    Args:
        df (pd.DataFrame): DataFrame avec colonnes 'date' (datetime), 'month', 'year', 'day', etc.
        date (str or 'last'): Date de référence au format 'YYYY-MM-DD'. Si 'last', prend la dernière date.
        zone (str): Zone géographique. Par défaut 'RDC'.
        operator (str): Opérateur. Par défaut 'All_Operator'.
        devise (str): 'USD' (par défaut) ou 'CDF'.
        value (str): Colonne KPI à analyser.
        unit (float): Diviseur (ex: 1e6 pour millions)

    Returns:
        list: [
            d_prior,        # Valeur du même jour, semaine précédente
            d_prev,         # Valeur du jour précédent
            d_current,      # Valeur du jour courant
            delta_spld,     # ∆ vs jour précédent
            delta_splw,     # ∆ vs même jour semaine dernière
            mtd_prior,      # MTD mois précédent (valeur du jour_ref en mois-1)
            mtd_current,    # MTD mois courant (valeur du jour_ref)
            delta_mtd       # ∆ MTD
        ]
    """
    df = df.copy()

    # 1. Convertir 'date' en datetime si nécessaire
    if not pd.api.types.is_datetime64_any_dtype(df['date']):
        df['date'] = pd.to_datetime(df['date'])

    # 2. Définir la date de référence
    if date == 'last':
        date_ref = df['date'].max()
    else:
        date_ref = pd.to_datetime(date)

    year_ref = date_ref.year
    month_ref = date_ref.month
    day_ref = date_ref.day

    # 3. Filtrer par zone et opérateur
    if zone != 'RDC':
        df = df[df['zone'] == zone]

    if operator == 'All_Operator':
        df = df[df['operator'] != 'All_Operator']
    else:
        df = df[df['operator'] == operator]

    # 4. Ajuster pour la devise CDF (seulement pour les revenus)
    if devise == 'CDF' and value.startswith('rev'):
        if 'rate_cdf' not in df.columns:
            raise ValueError("Colonne 'rate_cdf' manquante pour la conversion en CDF.")
        df[value] = df[value] * df['rate_cdf']

    # 5. Définir les dates clés
    current_date = date_ref
    prev_date = current_date - pd.Timedelta(days=1)
    prior_date = current_date - pd.Timedelta(days=7)

    # Helper: Filtrer par date exacte
    def filter_day(df, date):
        target = pd.to_datetime(date).date()
        return df[df['date'].dt.date == target]

    # Helper: Filtrer MTD (du 1er au jour_ref inclus)
    def filter_mtd(df, year, month, max_day):
        start = pd.to_datetime(f'{year}-{month:02d}-01')
        try:
            end = pd.to_datetime(f'{year}-{month:02d}-{max_day}')
        except ValueError:
            # Si le jour n'existe pas (ex: 30-02), on prend la fin du mois
            end = start + pd.offsets.MonthEnd(0)
        return df[(df['date'] >= start) & (df['date'] <= end)]

    # Calculer prev_month et prev_year en amont (utile pour user_ et flux)
    if month_ref > 1:
        prev_month = month_ref - 1
        prev_year = year_ref
    else:
        prev_month = 12
        prev_year = year_ref - 1

    # 6. Déterminer le type de métrique
    is_user_metric = value.startswith('user_')

    # Valeur du jour courant
    df_current = filter_day(df, current_date)
    d_current = df_current[value].iloc[-1] / unit if not df_current.empty else np.nan

    # Valeur du jour précédent
    df_prev = filter_day(df, prev_date)
    d_prev = df_prev[value].iloc[-1] / unit if not df_prev.empty else np.nan

    # Valeur du même jour semaine dernière
    df_prior = filter_day(df, prior_date)
    d_prior = df_prior[value].iloc[-1] / unit if not df_prior.empty else np.nan

    # --- Calcul de MTD_current et MTD_prior ---
    if is_user_metric:
        # Pour les indicateurs utilisateurs : MTD = valeur du jour de référence
        mtd_current = d_current

        # Rechercher la valeur du même jour dans le mois précédent
        try:
            prior_month_date = pd.to_datetime(f'{prev_year}-{prev_month:02d}-{day_ref}')
            df_mtd_prior_day = filter_day(df, prior_month_date)
            mtd_prior = df_mtd_prior_day[value].iloc[-1] / unit if not df_mtd_prior_day.empty else np.nan
        except ValueError:
            mtd_prior = np.nan
    else:
        # Pour les flux : MTD = somme du 1er au jour_ref
        mtd_current = filter_mtd(df, year_ref, month_ref, day_ref)[value].sum() / unit

        # Vérifier si le jour existe dans le mois précédent
        try:
            pd.to_datetime(f'{prev_year}-{prev_month:02d}-{day_ref}')
            mtd_prior = filter_mtd(df, prev_year, prev_month, day_ref)[value].sum() / unit
        except ValueError:
            mtd_prior = np.nan

    # 7. Calculer les variations
    def safe_pct_change(new, old):
        if pd.isna(old) or old == 0:
            return np.nan
        return (new / old) - 1

    delta_spld = safe_pct_change(d_current, d_prev).round(3)   # vs J-1
    delta_splw = safe_pct_change(d_current, d_prior).round(3)   # vs J-7
    delta_mtd = safe_pct_change(mtd_current, mtd_prior).round(3) # vs MTD mois précédent

    # 8. Retourner la liste
    return [d_prior, d_prev, d_current, delta_spld, delta_splw, mtd_prior, mtd_current, delta_mtd]




# ----------------------------------------------------------------------------------------------------------------------
# FONCTION GET SUMMARY MONTH
# ----------------------------------------------------------------------------------------------------------------------


def get_summary_month(df, date='last', zone='RDC', operator='All_Operator', devise='USD', value='revenu', unit=1):
    """
    Calcule 8 indicateurs mensuels dynamiques selon la date de référence.
    
    Args:
        df (pd.DataFrame): DataFrame avec colonnes 'date' (datetime), 'month', 'year', 'month_num', etc.
        date (str or 'last'): Date de référence au format 'YYYY-MM-DD'. Si 'last', prend la dernière date du DataFrame.
        zone (str): Zone géographique. Par défaut 'RDC'.
        operator (str): Opérateur. Par défaut 'All_Operator'.s
        devise (str): 'USD' (par défaut) ou 'CDF'.
        value (str): Colonne KPI à analyser.
        unit (float): Diviseur (ex: 1e6 pour millions)

    Returns:
        list: [
            mois_antérieur_même_année_précédente,  # ex: Juin-23
            mois_précédent,                         # ex: Mai-24
            mois_courant,                           # ex: Juin-24
            ∆ SPLM (vs mois précédent, ajusté 30j),
            ∆ SPLY (vs même mois année précédente),
            YTD_année_précédente,                   # somme jan → même mois N-1
            YTD_année_courante,                     # somme jan → mois_ref N
            ∆ YTD
        ]
    """
    
    df = df.copy()
    
    # 1. Convertir 'date' en datetime si nécessaire
    if not pd.api.types.is_datetime64_any_dtype(df['date']):
        df['date'] = pd.to_datetime(df['date'])
    
    # 2. Définir la date de référence
    if date == 'last':
        date_ref = df['date'].max()
    else:
        date_ref = pd.to_datetime(date)
    
    year_ref = date_ref.year
    month_ref = date_ref.month
    
    # 3. Filtrer par zone et opérateur
    if zone != 'RDC':
        df = df[df['zone'] == zone]
        
    # Gestion robuste de l'opérateur
    if operator == 'All_Operator':
        df = df[df['operator'] != 'All_Operator']
    else:
        df = df[df['operator'] == operator]
    
    # 4. Ajuster pour la devise CDF
    if devise == 'CDF' and value.startswith('rev'):
        if 'rate_cdf' not in df.columns:
            raise ValueError("Colonne 'rate_cdf' manquante pour la conversion en CDF.")
        df[value] = df[value] * df['rate_cdf']
    
    # 5. Définir les périodes dynamiques
    # Mois courant
    current_month = month_ref
    current_year = year_ref
    
    # Mois précédent (dans la même année)
    if current_month > 1:
        prev_month = current_month - 1
        prev_year = current_year
    else:
        prev_month = 12
        prev_year = current_year - 1
    
    # Même mois, année précédente
    prior_month = current_month
    prior_year = current_year - 1
    
    # Helper: Filtrer par année et mois
    def filter_month(df, year, month):
        return df[(df['year'] == year) & (df['month_num'] == month)]
    
    # Helper: Filtrer YTD (Year-To-Date) → de janvier au mois max inclus
    def filter_ytd(df, year, max_month=None):
        if max_month is None:
            return df[df['year'] == year]
        else:
            return df[(df['year'] == year) & (df['month_num'] <= max_month)]
    
    # 6. Calculer les valeurs
    is_user_metric = value.startswith('user_')
    
    # NOUVEAU : Fonction pour extraire la dernière valeur du mois (pour user_)
    def get_last_value(group):
        if group.empty:
            return np.nan
        # Trier par date et prendre la dernière
        return group.sort_values('date')[value].iloc[-1]

    if is_user_metric:
        # CORRECTION : on ne fait PAS .sum(), on prend la dernière valeur du mois
        # (celle du dernier jour disponible)
        m_prior = get_last_value(filter_month(df, prior_year, prior_month)) / unit
        m_prev = get_last_value(filter_month(df, prev_year, prev_month)) / unit
        m_current = get_last_value(filter_month(df, current_year, current_month)) / unit
        
        # YTD = somme des dernières valeurs de chaque mois ? Non.
        # En télécom, YTD pour un stock = valeur du mois de référence
        # Donc on garde : YTD = valeur du mois (pas cumul)
        ytd_prior = m_prior  # ← valeur du mois de référence en N-1
        ytd_current = m_current  # ← valeur du mois courant
    else:
        # somme les valeurs du mois
        m_prior = filter_month(df, prior_year, prior_month)[value].sum() / unit if not filter_month(df, prior_year, prior_month).empty else np.nan
        m_prev = filter_month(df, prev_year, prev_month)[value].sum() / unit if not filter_month(df, prev_year, prev_month).empty else np.nan
        m_current = filter_month(df, current_year, current_month)[value].sum() / unit if not filter_month(df, current_year, current_month).empty else np.nan
        
        # YTD = somme de janvier au mois de référence
        ytd_prior = filter_ytd(df, prior_year, max_month=month_ref)[value].sum() / unit if not filter_ytd(df, prior_year, max_month=month_ref).empty else np.nan
        ytd_current = filter_ytd(df, current_year, max_month=month_ref)[value].sum() / unit if not filter_ytd(df, current_year, max_month=month_ref).empty else np.nan
    
    # 7. Calculer les variations
    def safe_pct_change(new, old):
        if pd.isna(old) or old == 0:
            return np.nan
        return (new / old) - 1

    # Ajustement SPLM : normalisation sur 30 jours
    def get_days_in_month(year, month):
        """Retourne le nombre de jours dans un mois donné."""
        if month == 2:
            if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
                return 29  # année bissextile
            else:
                return 28
        elif month in [4, 6, 9, 11]:
            return 30
        else:
            return 31

    # Normaliser les valeurs comme si tous les mois avaient 30 jours
    days_prev = get_days_in_month(prev_year, prev_month)
    days_current = get_days_in_month(current_year, current_month)
    
    # Ajuster les valeurs pour comparaison
    m_prev_adj = (m_prev / days_prev) * 30 if not pd.isna(m_prev) else np.nan
    m_current_adj = (m_current / days_current) * 30 if not pd.isna(m_current) else np.nan

    delta_splm = safe_pct_change(m_current_adj, m_prev_adj).round(3)   # vs mois précédent, ajusté 30j
    delta_sply = safe_pct_change(m_current, m_prior).round(3)          # vs même mois année précédente
    delta_ytd = safe_pct_change(ytd_current, ytd_prior).round(3)       # vs YTD précédent

    # 8. Retourner la liste
    return [m_prior, m_prev, m_current, delta_splm, delta_sply, ytd_prior, ytd_current, delta_ytd]


# ----------------------------------------------------------------------------------------------------------------------
# FONCTION GET SUMMARY QUARTER
# ----------------------------------------------------------------------------------------------------------------------


def get_summary_quarter(df, date='last', zone='RDC', operator='All_Operator', devise='USD', value='revenu', unit=1):
    """
    Calcule 8 indicateurs trimestriels dynamiques selon la date de référence.
    
    Args:
        df (pd.DataFrame): DataFrame avec colonnes 'date' (datetime), 'month', 'year', 'quarter', etc.
        date (str or 'last'): Date de référence au format 'YYYY-MM-DD'. Si 'last', prend la dernière date du DataFrame.
        zone (str): Zone géographique. Par défaut 'RDC'.
        operator (str): Opérateur. Par défaut 'All_Operator'.
        devise (str): 'USD' (par défaut) ou 'CDF'.
        value (str): Colonne KPI à analyser.

    Returns:
        list: [période_antérieure, période_précédente, période_courante, ∆ SPLT, ∆ SPLY, YTD_antérieur, YTD_courant, ∆ YTD]
    """
    
    df = df.copy()
    
    # 1. Convertir 'date' en datetime si nécessaire
    if not pd.api.types.is_datetime64_any_dtype(df['date']):
        df['date'] = pd.to_datetime(df['date'])
    
    # 2. Définir la date de référence
    if date == 'last':
        date_ref = df['date'].max()
    else:
        date_ref = pd.to_datetime(date)
    
    year_ref = date_ref.year
    quarter_ref = (date_ref.month - 1) // 3 + 1  # 1, 2, 3, 4
    
    # 3. Filtrer par zone et opérateur
    if zone != 'RDC':
        df = df[df['zone'] == zone]
        
    # Gestion robuste de l'opérateur
    if operator == 'All_Operator':
        # Exclure la ligne "All_Operator" si elle existe, et sommer les autres opérateurs
        df = df[df['operator'] != 'All_Operator']
    else:
        # Filtrer par l'opérateur spécifique demandé
        df = df[df['operator'] == operator]
    
    # 4. Ajuster pour la devise CDF
    if devise == 'CDF' and value.startswith('rev'):
        if 'rate_cdf' not in df.columns:
            raise ValueError("Colonne 'rate_cdf' manquante pour la conversion en CDF.")
        df[value] = df[value] * df['rate_cdf']
    
    # 5. Définir les périodes dynamiques
    # Période courante = trimestre de référence
    current_quarter = quarter_ref
    current_year = year_ref
    
    # Période précédente = trimestre précédent (dans la même année)
    if current_quarter > 1:
        prev_quarter = current_quarter - 1
        prev_year = current_year
    else:
        prev_quarter = 4
        prev_year = current_year - 1
    
    # Période antérieure = même trimestre l'année précédente
    prior_quarter = current_quarter
    prior_year = current_year - 1
    
    # Helper: Filtrer par année et mois
    def filter_month(df, year, month):
        return df[(df['year'] == year) & (df['month_num'] == month)]
    
    # Helper: Filtrer par trimestre
    def filter_quarter(df, year, quarter):
        months = {1: [1,2,3], 2: [4,5,6], 3: [7,8,9], 4: [10,11,12]}
        return df[(df['year'] == year) & (df['month_num'].isin(months[quarter]))]
    
    # Helper: Filtrer YTD (Year-To-Date)
    def filter_ytd(df, year, max_month=None):
        if max_month is None:
            return df[df['year'] == year]
        else:
            return df[(df['year'] == year) & (df['month_num'] <= max_month)]
    
    # 6. Calculer les valeurs
    is_user_metric = value.startswith('user_')
    
    if is_user_metric:
        # Prendre la dernière valeur du mois de fin de période
        q_prior = filter_month(df, prior_year, 3 * prior_quarter)[value].sum()/unit if not filter_month(df, prior_year, 3 * prior_quarter).empty else np.nan
        q_prev = filter_month(df, prev_year, 3 * prev_quarter)[value].sum()/unit if not filter_month(df, prev_year, 3 * prev_quarter).empty else np.nan
        q_current = filter_month(df, current_year, 3 * current_quarter)[value].sum()/unit if not filter_month(df, current_year, 3 * current_quarter).empty else np.nan
        
        # YTD = dernière valeur du mois de décembre (si année complète) ou du mois de référence
        ytd_prior = filter_month(df, prior_year, 12)[value].sum()/unit if not filter_month(df, prior_year, 12).empty else np.nan
        if current_quarter == 4:
            ytd_current = filter_month(df, current_year, 12)[value].sum()/unit if not filter_month(df, current_year, 12).empty else np.nan
        else:
            ytd_current = filter_month(df, current_year, 3 * current_quarter)[value].sum()/unit if not filter_month(df, current_year, 3 * current_quarter).empty else np.nan
    else:
        # Prendre la somme sur la période
        q_prior = filter_quarter(df, prior_year, prior_quarter)[value].sum()/unit if not filter_quarter(df, prior_year, prior_quarter).empty else np.nan
        q_prev = filter_quarter(df, prev_year, prev_quarter)[value].sum()/unit if not filter_quarter(df, prev_year, prev_quarter).empty else np.nan
        q_current = filter_quarter(df, current_year, current_quarter)[value].sum()/unit if not filter_quarter(df, current_year, current_quarter).empty else np.nan
        
        # YTD = somme de janvier au mois de fin de période
        ytd_prior = filter_ytd(df, prior_year, date_ref.month)[value].sum() / unit if not filter_ytd(df, prior_year, date_ref.month).empty else np.nan
        ytd_current = filter_ytd(df, current_year, date_ref.month)[value].sum()/unit if not filter_ytd(df, current_year, date_ref.month).empty else np.nan
    
    # 7. Calculer les variations
    def safe_pct_change(new, old):
        if pd.isna(old) or old == 0:
            return np.nan
        return (new / old) - 1

    delta_splt = safe_pct_change(q_current, q_prev).round(3)   # vs trimestre précédent
    delta_sply = safe_pct_change(q_current, q_prior).round(3)  # vs même trimestre année précédente
    delta_ytd = safe_pct_change(ytd_current, ytd_prior).round(3)  # vs YTD précédent

    # 8. Retourner la liste
    return [q_prior, q_prev, q_current, delta_splt, delta_sply, ytd_prior, ytd_current, delta_ytd]



# ----------------------------------------------------------------------------------------------------------------------
# FONCTION GET COLONNE DAY
# ----------------------------------------------------------------------------------------------------------------------


def get_column_day(date_ref):
    """
    Génère les noms de colonnes pour un tableau de bord JOURNALIER.

    Args:
        date_ref (str or datetime): Date de référence (ex: '2018-10-20')

    Returns:
        list: Liste des noms de colonnes, ex:
              ["KPIs", "13-oct.", "19-oct.", "20-oct.", "∆ DoD", "∆ SDLW", "MTD-1", "MTD", "∆ MTD"]
    """
    if isinstance(date_ref, str):
        date_ref = pd.to_datetime(date_ref)

    # Dates clés
    current_date = date_ref
    prev_date = current_date - pd.Timedelta(days=1)          # J-1
    prior_date = current_date - pd.Timedelta(days=7)         # J-7 (Same Day Last Week)

    # Dictionnaire mois → abréviation en français
    mois_abbr = {
        1: "janv.", 2: "févr.", 3: "mars", 4: "avr.",
        5: "mai", 6: "juin", 7: "juil.", 8: "août",
        9: "sept.", 10: "oct.", 11: "nov.", 12: "déc."
        }

    # Format : jj-mmm. (ex: 20-oct.)
    def format_day(date):
        day = date.day
        month_abbr = mois_abbr[date.month]
        return f"{day}-{month_abbr}"

    # Générer les libellés
    d_prior = format_day(prior_date)     # ex: 13-oct.
    d_prev = format_day(prev_date)       # ex: 19-oct.
    d_current = format_day(current_date) # ex: 20-oct.

    columns = [
        "KPIs",           # Colonne de description
        d_prior,          # Même jour semaine dernière
        d_prev,           # Jour précédent
        d_current,        # Jour courant
        "∆ DoD",          # Day-over-Day (vs J-1)
        "∆ SDLW",         # Same Day Last Week (vs J-7)
        "MTD-1",          # MTD mois précédent (même plage)
        "MTD",            # MTD mois courant
        "∆ MTD"           # Évolution MTD vs mois précédent
        ]
    
    return columns


# ----------------------------------------------------------------------------------------------------------------------
# FONCTION GET COLONNE MONTH
# ----------------------------------------------------------------------------------------------------------------------


def get_column_month(date_ref):
    """
    Génère les noms de colonnes pour un tableau de bord MENSUEL.
    
    Args:
        date_ref (str or datetime): Date de référence (ex: '2025-03-31')
    
    Returns:
        list: Liste des noms de colonnes, ex: ["Déc-23", "Nov-24", "Déc-24", "∆ SPLM", ...]
    """
    if isinstance(date_ref, str):
        date_ref = pd.to_datetime(date_ref)
    
    year_ref = date_ref.year
    month_ref = date_ref.month

    # Mois courant
    current_month = month_ref
    current_year = year_ref

    # Mois précédent (dans la même année)
    if current_month > 1:
        prev_month = current_month - 1
        prev_year = current_year
    else:
        prev_month = 12
        prev_year = current_year - 1

    # Même mois, année précédente
    prior_month = current_month
    prior_year = current_year - 1

    # Dictionnaire mois → abréviation
    mois_abbr = {
        1: "Jan", 2: "Fév", 3: "Mar", 4: "Avr",
        5: "Mai", 6: "Jun", 7: "Jul", 8: "Aoû",
        9: "Sep", 10: "Oct", 11: "Nov", 12: "Déc"
        }

    # Générer les libellés
    m_prior = f"{mois_abbr[prior_month]}-{str(prior_year)[-2:]}"
    m_prev = f"{mois_abbr[prev_month]}-{str(prev_year)[-2:]}"
    m_current = f"{mois_abbr[current_month]}-{str(current_year)[-2:]}"

    columns = [
        "KPIs",
        m_prior,      # ex: Déc-23
        m_prev,       # ex: Nov-24
        m_current,    # ex: Déc-24
        "∆ SPLM",     # vs mois précédent (ajusté 30j)
        "∆ SPLY",     # vs même mois année précédente
        f"YTD-{prior_year}",  # YTD année précédente
        f"YTD-{current_year}",  # YTD année courante
        "∆ YTD"
        ]
    
    return columns





# ----------------------------------------------------------------------------------------------------------------------
# FONCTION GET COLONNE QUARTER
# ----------------------------------------------------------------------------------------------------------------------


def get_column_quarter(date_ref):
    """
    Génère dynamiquement les noms de colonnes du tableau de bord trimestriel
    en fonction de la date de référence.
    
    Args:
        date_ref (str or datetime): Date de référence au format 'YYYY-MM-DD'
    
    Returns:
        list: Liste des noms de colonnes, ex: ["Indicateur", "Q2-24", "Q1-25", "Q2-25", "∆ SPLQ", ...]
    """
    # Convertir en datetime si ce n'est pas déjà fait
    if isinstance(date_ref, str):
        date_ref = pd.to_datetime(date_ref)
    
    year_ref = date_ref.year
    month_ref = date_ref.month
    
    # Déterminer le trimestre de référence
    quarter_ref = (month_ref - 1) // 3 + 1  # 1, 2, 3 ou 4

    # Calculer les périodes dynamiques
    if quarter_ref == 1:  # T1 → comparer avec T4-23 et T4-24
        q_prior = f"Q1-{year_ref - 1}"   # T1-24
        q_prev = f"Q4-{year_ref - 1}"   # T4-24
        q_current = f"Q1-{year_ref}"    # T1-25
    elif quarter_ref == 2:  # T2 → comparer avec T1-25 et T2-24
        q_prior = f"Q2-{year_ref - 1}"  # T2-24
        q_prev = f"Q1-{year_ref}"       # T1-25
        q_current = f"Q2-{year_ref}"    # T2-25
    elif quarter_ref == 3:  # T3 → comparer avec T2-25 et T3-24
        q_prior = f"Q3-{year_ref - 1}"  # T3-24
        q_prev = f"Q2-{year_ref}"       # T2-25
        q_current = f"Q3-{year_ref}"    # T3-25
    elif quarter_ref == 4:  # T4 → comparer avec T3-25 et T4-24
        q_prior = f"Q4-{year_ref - 1}"  # T4-24
        q_prev = f"Q3-{year_ref}"       # T3-25
        q_current = f"Q4-{year_ref}"    # T4-25
    else:
        raise ValueError("Trimestre invalide")

    # Générer les noms de colonnes
    columns = [
        "KPIs",
        q_prior,      # ex: T2-24
        q_prev,       # ex: T1-25
        q_current,    # ex: T2-25
        "∆ SPLQ",     # vs trimestre précédent (q_current / q_prev - 1)
        "∆ SPLY",     # vs même trimestre année précédente (q_current / q_prior - 1)
        f"YTD-{year_ref - 1}",  # YTD année précédente
        f"YTD-{year_ref}",      # YTD année courante
        "∆ YTD"       # YTD courant / YTD précédent - 1
        ]
    
    return columns





# ----------------------------------------------------------------------------------------------------------------------
# FONCTION COMPLETE SERIE
# ----------------------------------------------------------------------------------------------------------------------



def complete_series(df, k=0):
    """
    Complète une série temporelle mensuelle en ajoutant les mois manquants.
    
    Paramètres :
    -----------
    df : DataFrame avec index datetime64 ou Period[monthly], une seule colonne (ex: 'X_t')
    k : int
        - k = 0 : remplace les mois manquants par 0
        - k >= 1 : remplace par la moyenne mobile des k derniers mois disponibles (avant le trou)
    
    Retourne :
    ---------
    DataFrame avec tous les mois complétés, trié par date.
    """
    if df.empty:
        raise ValueError("Le DataFrame est vide.")
    
    # S'assurer que l'index est en datetime
    if isinstance(df.index, pd.PeriodIndex):
        df = df.copy()
        df.index = df.index.to_timestamp()
    
    # Trier l'index
    df = df.sort_index()
    
    # Créer une séquence complète de mois
    start = df.index.min()
    end = df.index.max()
    full_index = pd.date_range(start=start, end=end, freq='MS')  # MS = début du mois
    
    # Reindexer pour ajouter les mois manquants
    df_full = df.reindex(full_index)
    
    if k == 0:
        # Remplacer par 0
        df_full = df_full.fillna(0)
    else:
        # Remplacer par la moyenne des k derniers mois disponibles
        # On fait un remplissage itératif
        values = df_full.iloc[:, 0].copy()
        for i, (idx, val) in enumerate(values.items()):
            if pd.isna(val):
                # Récupérer les k mois précédents disponibles (non NaN)
                prev_values = values.iloc[:i].dropna().tail(k)
                if len(prev_values) == 0:
                    values.iloc[i] = 0  # si pas assez de données, mettre 0
                else:
                    values.iloc[i] = prev_values.mean()
        df_full.iloc[:, 0] = values
    
    print(f"Nombre de mois avant : {len(df)}")
    print(f"Nombre de mois après : {len(df_full)}")
    print("Premier mois :", df_full.index.min())
    print("Dernier mois :", df_full.index.max())
    
    return df_full



