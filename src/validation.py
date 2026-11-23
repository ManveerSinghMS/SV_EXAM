"""Shared validation tools for blocks B, C and the final link.

Why one shared file: cities close to each other have almost the same weather and pollution.
In a random cross-validation a Po Valley city is predicted after the model has seen its
neighbours, so the score looks better than it is. Every block must use the SAME geographic
blocks, so that the numbers in the slides agree with each other.

Usage in a notebook:

    import sys; sys.path.append("../src")
    from validation import spatial_blocks, compare_cv, out_of_fold
    # the three groups of cities: groups.add_groups(cities); their colours: style.GROUP_COLOURS

    blocks = spatial_blocks(cities)                     # one block number per city
    table = compare_cv(model, X, y, blocks, metric=roc_auc_score)
"""
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.model_selection import GroupKFold, StratifiedKFold, KFold, cross_val_predict

N_BLOCKS = 12      # geographic blocks: each about 24 cities on average
SEED = 0           # fixed, so every block gets the same blocks


def spatial_blocks(cities, n_blocks=N_BLOCKS, seed=SEED):
    """Split the cities into geographic blocks with k-means on latitude and longitude.

    Cities in the same block are close to each other, so leaving a block out of training removes
    most of the neighbours of its cities. It does not remove all of them: blocks are groups of
    nearby cities, not administrative regions, and they impose no minimum distance, so a city at
    the edge of a held-out block can have neighbours in a training block (e.g. Torino is not in the
    block of the other 24 Po Valley cities). Say "the model was not trained on the cities of the
    held-out blocks", not "the model never saw the region".
    """
    coords = cities[["lat", "lon"]].to_numpy()
    return KMeans(n_clusters=n_blocks, n_init=20, random_state=seed).fit_predict(coords)


def compare_cv(model, X, y, blocks, metric, method="predict_proba", n_splits=6, classification=True):
    """Score the same model with a random CV and with a geographic CV, side by side.

    The predictions of all the folds are pooled and scored once (cross_val_predict), because with
    geographic blocks some folds contain no city over the limit, and AUC cannot be computed on one fold.
    metric: a function metric(y_true, prediction), e.g. sklearn.metrics.roc_auc_score or r2_score.
    method: "predict_proba" (classification, probability of the positive class) or "predict".
    Report BOTH rows in the slides: the gap is how much the random CV is helped by neighbours.
    """
    if classification:
        random_cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=SEED)
    else:
        random_cv = KFold(n_splits=n_splits, shuffle=True, random_state=SEED)
    rows = []
    for name, cv, groups in [("random", random_cv, None), ("geographic blocks", GroupKFold(n_splits=n_splits), blocks)]:
        pred = cross_val_predict(model, X, y, cv=cv, groups=groups, method=method)
        if method == "predict_proba":
            pred = pred[:, 1]
        rows.append({"cross-validation": name, "score": metric(y, pred)})
    return pd.DataFrame(rows)


def out_of_fold(model, X, y, blocks, method="predict", n_splits=6):
    """Out-of-fold predictions with the geographic CV: every city is predicted by a model
    not trained on the cities of its block. Use these (not in-sample predictions) for the final link."""
    pred = cross_val_predict(model, X, y, cv=GroupKFold(n_splits=n_splits), groups=blocks, method=method)
    return pred[:, 1] if method == "predict_proba" else pred
