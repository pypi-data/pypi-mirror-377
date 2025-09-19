from ._version import __version__
from .datasets import load, datasets, dataset_table
from .hybrid_nb import HybridNB

__all__ = ["HybridNB", "load", "datasets", "dataset_table"]

__doc__ = f"""
DSF package: Example datasets for Python users

Available datasets:
{dataset_table()}

# Load a dataset from the DSF package as a pandas DataFrame

>>> import dsf
>>> df = dsf.load('<dataset_name>')  # Load a dataset as a pandas DataFrame
>>> dsf.version()  # DSF version {__version__}


# Example usage of HybridNB

>>> from dsf import HybridNB
>>> hnb = HybridNB(
...     num_cols=num_cols,               # continuous numeric features
...     cat_cols=multinomial_cat_cols,   # categorical (Multinomial)
...     count_cols=count_cols,           # counts (MultinomialNB)
...     bernoulli_cols=bernoulli_cols,   # binary (BernoulliNB)
...     alpha=1.0
... )
>>> hnb.fit(X_train, y_train)
>>> y_pred = hnb.predict(X_test)
>>> y_proba = hnb.predict_proba(X_test)
"""