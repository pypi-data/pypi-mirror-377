# iperform

**iperform** est un package Python conçu pour générer des **tableaux de bord analytiques dynamiques** et suivre les performances du business.  
Spécialement pensé pour les secteurs **télécom** et **bancaire**, il s’adapte à tout domaine utilisant des **séries chronologiques** :  Vente d’articles, production pétrolière, logistique, retail, etc.

Grâce à une API simple et cohérente, `iperform` permet de calculer rapidement :
- Des indicateurs temporels (MTD, YTD, QoQ)
- Des résumés comparatifs (vs J-1, vs N-1)
- Des prévisions basiques
- Des visualisations interactives

Et tout cela en quelques lignes de code.

## Fonctionnalités principales

Le package offre une large gamme des fonctions qui renvoient la (les) d'une série temporelles pour une date donnée en argument, à l'exemple de :
- `mtd()` : month-to-date (MTD), somme des valeurs allant du premier jour du mois jusqu'à la date de référence dans le même mois  
- `ytd()` : year-to-date : (YTD), somme des valeurs de la série allant du premier janvier jusqu'à date
- `get_summary_day()` : une suite des indicateurs dynamiques
- `get_dashboard()` : tableau de bord avec plusieurs KPIs calculés
- `graph_trend_day()` : graphiques interactifs
- `format_kpi()` : Formatage automatique (millions, %, etc.)

## Installation

```bash
pip install iperform
```

## Exemple d'utilisation

```python
import pandas as pd

date = pd.date_range("2023-01-01", periods=222, freq="D")
x = np.random.normal(50, 6.3, 222)
df = pd.DataFrame({"date": date, "x": x, "zone": "RDC", "operator": "Orange"})
dday(df, date="2023-07-06", x="x", d=0, unite=1, decimal=2)

```

## Organisation des fonctions

Les fonctions de *iperform* se regroupent en 4 catégories :  

- “Les performances” : Indicateurs de performance sur une période donnée.  

  `dday()`, `wtd()`, `mtd()`, `qtd()`, `htd()`, `ytd()`, `full_w()`,
  `full_m()`, `full_q()`, `full_h()` et `full_y()`.

- “Les aperçus” : Résumés dynamiques avec comparaisons (vs période précédente, vs année passée).  

  `get_summary_day()`, `get_summary_month()` et `get_summary_quarter()`.

- “Les previsions” : Estimations futures basées sur les tendances observées.  

  `forecast_m()`, `get_sarimax()` : Bientôt disponible (dans iperform_cloud), `split_data()`.

- “Les visuelles” : Visualisation et mise en forme des résultats.

  `plot_kpi()`, `graph_trend_day()`, `graph_season()`, `format_kpi()`, `get_columns_day()`.


## Obtenir de l’aide

Besoin d’un coup de main ? Voici comment t’aider :  

  - Consulte la [documentation]()  (bientôt disponible)
  - Signale un bug ou demande une fonctionnalité : [GitHub Issues]() 
  - Rejoins la communauté sur LinkedIn ou Slack (à créer)
  - Contact : buabua@internet.ru 

## Contribuer 

Toute contribution est la bienvenue !
Que ce soit pour corriger une erreur, ajouter une fonction, ou améliorer la documentation. 

Consulte le fichier [CONTRIBUTING.md]()  pour commencer.


## Licence 

Ce projet est sous licence MIT – tu peux l’utiliser librement, même à des fins commerciales. 
