from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.naive_bayes import GaussianNB, CategoricalNB, MultinomialNB, BernoulliNB
import pandas as pd
import numpy as np

class HybridNB(BaseEstimator, ClassifierMixin):
    """
    Mixed-type Naive Bayes classifier for Gaussian, multinomial, count, and Bernoulli features.
    Works directly with pandas DataFrames.
    User must explicitly specify the columns for each type.
    """
    def __init__(self, gaussian_cols=None, multinomial_cols=None, count_cols=None, bernoulli_cols=None, alpha=1.0, binarize=0.0):
        self.gaussian_cols = list(gaussian_cols) if gaussian_cols is not None else []
        self.multinomial_cols = list(multinomial_cols) if multinomial_cols is not None else []
        self.count_cols = list(count_cols) if count_cols is not None else []
        self.bernoulli_cols = list(bernoulli_cols) if bernoulli_cols is not None else []
        self.alpha = alpha
        self.binarize = binarize

        self.gnb_ = None
        self.cnb_ = None
        self.mnb_ = None
        self.bnb_ = None

    def _validate_columns(self, X: pd.DataFrame):
        # Gaussian columns
        for col in self.gaussian_cols:
            if not pd.api.types.is_numeric_dtype(X[col]):
                raise TypeError(f"Gaussian column '{col}' must be numeric (int or float).")

        # Multinomial columns
        for col in self.multinomial_cols:
            if not pd.api.types.is_integer_dtype(X[col]):
                raise TypeError(f"Multinomial column '{col}' must contain integers.")

        # Count columns
        for col in self.count_cols:
            if not pd.api.types.is_integer_dtype(X[col]):
                raise TypeError(f"Count column '{col}' must contain integers.")
            if (X[col] < 0).any():
                raise ValueError(f"Count column '{col}' contains negative values.")

        # Bernoulli columns
        for col in self.bernoulli_cols:
            if not pd.api.types.is_numeric_dtype(X[col]):
                raise TypeError(f"Bernoulli column '{col}' must be numeric (0 or 1).")
            if not X[col].isin([0, 1]).all():
                raise ValueError(f"Bernoulli column '{col}' must contain only 0 or 1.")

    def fit(self, X: pd.DataFrame, y):
        self._validate_columns(X)

        # Fit Gaussian
        if len(self.gaussian_cols) > 0:
            self.gnb_ = GaussianNB()
            self.gnb_.fit(X[self.gaussian_cols].to_numpy(), y)

        # Fit Multinomial
        if len(self.multinomial_cols) > 0:
            self.cnb_ = CategoricalNB(alpha=self.alpha)
            self.cnb_.fit(X[self.multinomial_cols].to_numpy(), y)

        # Fit Count
        if len(self.count_cols) > 0:
            self.mnb_ = MultinomialNB(alpha=self.alpha)
            self.mnb_.fit(X[self.count_cols].to_numpy(), y)

        # Fit Bernoulli
        if len(self.bernoulli_cols) > 0:
            self.bnb_ = BernoulliNB(alpha=self.alpha, binarize=self.binarize)
            self.bnb_.fit(X[self.bernoulli_cols].to_numpy(), y)

        return self

    def predict_proba(self, X: pd.DataFrame):
        self._validate_columns(X)
        proba_combined = None

        if len(self.gaussian_cols) > 0:
            proba_gauss = self.gnb_.predict_proba(X[self.gaussian_cols].to_numpy())
            proba_combined = proba_gauss if proba_combined is None else proba_combined * proba_gauss

        if len(self.multinomial_cols) > 0:
            proba_multi = self.cnb_.predict_proba(X[self.multinomial_cols].to_numpy())
            proba_combined = proba_multi if proba_combined is None else proba_combined * proba_multi

        if len(self.count_cols) > 0:
            proba_count = self.mnb_.predict_proba(X[self.count_cols].to_numpy())
            proba_combined = proba_count if proba_combined is None else proba_combined * proba_count

        if len(self.bernoulli_cols) > 0:
            proba_bern = self.bnb_.predict_proba(X[self.bernoulli_cols].to_numpy())
            proba_combined = proba_bern if proba_combined is None else proba_combined * proba_bern

        # Normalize
        proba_combined /= proba_combined.sum(axis=1, keepdims=True)
        return proba_combined

    def predict(self, X: pd.DataFrame):
        return np.argmax(self.predict_proba(X), axis=1)