# -*- coding: utf-8 -*-

import numpy as np

from joblib import Parallel

from convst.transformers import R_DST, Raw, Derivate, Periodigram
from sklearn.utils.fixes import delayed
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.linear_model import RidgeClassifierCV

# Most of the following have been developed for the ATM case using a binary classification.
# Multi-class might not be supported for all functions and some would need to be adapted.
from sklearn.utils.extmath import softmax
from sklearn.metrics import accuracy_score, make_scorer
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline


class _internalRidgeCV(RidgeClassifierCV): 
    
    def __init__(self, **kwargs):
        super().__init__(
            store_cv_values=True,
            scoring=make_scorer(accuracy_score),
            alphas=np.logspace(-3,3,20),
            **kwargs
        )
    
    def fit(self, X, y):
        self.scaler = StandardScaler().fit(X)
        return super().fit(self.scaler.transform(X), y)
    
    def predict(self, X):
        return super().predict(self.scaler.transform(X))
    
    def predict_proba(self, X):
        d = self.decision_function(self.scaler.transform(X))
        if len(d.shape) == 1:
            d = np.c_[-d, d]
        return softmax(d)
    
    def get_loocv_train_acc(self, y_train):
        if self.store_cv_values:
            alpha_idx = np.where(self.alphas == self.alpha_)[0]
            cv_vals = self.cv_values_[:,:,alpha_idx]
            if cv_vals.shape[1] == 1:
                return accuracy_score((cv_vals[:,0]>0).astype(int), y_train)
            else:
                return accuracy_score(cv_vals.argmax(axis=1), y_train)
        else:
            raise ValueError('LOOCV training accuracy is only available with store_cv_values to True')


def _parallel_fit(X, y, model):
    return model.fit(X, y)

def _parallel_predict(X, model, w):
    return model.predict_proba(X) * w

class R_DST_Ensemble(BaseEstimator, ClassifierMixin):
    def __init__(
        self,
        n_shapelets_per_estimator=10000,
        shapelet_sizes=[11],
        n_samples=None,
        n_jobs=1,
        n_jobs_rdst=1,
        backend="processes",
        random_state=None,
        shp_alpha=0.5,
        a_w = 4
    ):
        self.n_shapelets_per_estimator=n_shapelets_per_estimator
        self.shapelet_sizes=shapelet_sizes
        self.n_jobs = n_jobs
        self.backend=backend
        self.n_jobs_rdst = n_jobs_rdst
        self.random_state = random_state
        self.n_samples=n_samples
        self.shp_alpha = shp_alpha
        self.a_w = a_w
        
    def fit(self, X, y):
        input_transformer = [
            Raw(),
            Derivate(),
            Periodigram()
        ]
        p_norms = [0.8, 0.8, 0.8]
        models = Parallel(
            n_jobs=self.n_jobs,
            prefer=self.backend,
        )(
            delayed(_parallel_fit)(
                X, y, 
                make_pipeline(
                    input_transformer[i],
                    R_DST(
                        n_shapelets=self.n_shapelets_per_estimator,
                        alpha=self.shp_alpha, n_samples=self.n_samples, p_norm=p_norms[i],
                        n_jobs=self.n_jobs_rdst, shapelet_sizes=self.shapelet_sizes
                    ),
                    _internalRidgeCV()
                )
            )
            for i in range(len(input_transformer))
        )
            
        self.models = models
        self.model_weights = [model['_internalridgecv'].get_loocv_train_acc(y)**self.a_w
                              for model in models]
        
        return self


    def predict(self, X):
        preds_proba = Parallel(
            n_jobs=self.n_jobs,
            prefer=self.backend,
        )(
            delayed(_parallel_predict)(
                X,
                self.models[i],
                self.model_weights[i]
            )
            for i in range(len(self.model_weights))
        )
        #n_samples, n_models
        preds_proba = np.asarray(preds_proba).sum(axis=0)
        return preds_proba.argmax(axis=1)

    
        