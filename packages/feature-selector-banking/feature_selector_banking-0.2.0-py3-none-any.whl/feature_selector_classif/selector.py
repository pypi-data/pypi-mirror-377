from sklearn.base import clone
from .utils import *
import pandas as pd

class Selector:
    def _fit_single(self, feature_set):
        model = clone(self._model)
        model.fit(self._X_train[feature_set], self._y_train, **self._fit_params)
        return model
    
    def validate_model_pipeline(self, feature_set):
        model = self._fit_single(feature_set)
        
        train_proba = model.predict_proba(self._X_train[feature_set])[:, 1]
        train_preds = model.predict(self._X_train[feature_set])

        test_proba = model.predict_proba(self._X_test[feature_set])[:, 1]
        test_preds = model.predict(self._X_test[feature_set])

        eval_results = dict()
        eval_results['feature_set'] = feature_set
        if 'auc' not in self._metric_name.lower():
            eval_results[f'train_{self._metric_name}'] = self._metric(self._y_train, train_preds)
            eval_results[f'test_{self._metric_name}'] = self._metric(self._y_test, test_preds)
        else:
            eval_results[f'train_{self._metric_name}'] = self._metric(self._y_train, train_proba)
            eval_results[f'test_{self._metric_name}'] = self._metric(self._y_test, test_proba)
        
        if self._maximize_bool:
            eval_results[f'difference_train_test'] = eval_results[f'train_{self._metric_name}'] - eval_results[f'test_{self._metric_name}']
        else:
            eval_results[f'difference_train_test'] = -(eval_results[f'train_{self._metric_name}'] - eval_results[f'test_{self._metric_name}'])
        
        return eval_results
    
    def fit(self, X, y, model, metric, metric_name, n_jobs=1, maximize_bool=True, fit_params=None, use_default_splitter=True, splitter=None, splitter_kwargs={}):
        """
        Выполняет поиск лучшей комбинации признаков.
        
        Parameters:
        -----------
        X : pandas.DataFrame или numpy.array
            Матрица признаков
        y : pandas.Series или numpy.array
            Целевая переменная
        model : object
            Модель машинного обучения с интерфейсом scikit-learn
        metric : str или callable
            Метрика для оценки (строка для scikit-learn или callable функция)
        fit_params : dict, optional
            Параметры для метода fit модели
        random_state: int, optional
            An integer for reproducibility; ensures the same split is generated each time the code is run.
        Returns:
        --------
        pandas.DataFrame
            DataFrame с результатами перебора
        """            
        # Преобразуем в DataFrame если это еще не сделано
        if not isinstance(X, pd.DataFrame):
            X = pd.DataFrame(X)
        
        # Параметры модели и фита
        self._model = clone(model)
        self._metric = metric
        self._metric_name = metric_name
        self._n_jobs = n_jobs
        self._maximize_bool = maximize_bool
        if fit_params is None:
            fit_params = {}
        self._fit_params = fit_params
        # Разбиение train + test:
        if use_default_splitter:
            splitter = default_splitter()
            self._X_train, self._X_test, self._y_train, self._y_test = splitter(X, y)
        else:
            self._X_train, self._X_test, self._y_train, self._y_test = splitter(X, y, **splitter_kwargs)

        self.eval_function()

    def save_df(self, filename, index=False):
        self.results_df.to_excel(filename, index=index)
