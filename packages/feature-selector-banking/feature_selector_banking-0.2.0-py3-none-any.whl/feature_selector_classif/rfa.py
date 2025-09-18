import pandas as pd
from joblib import Parallel, delayed, parallel_config
from tqdm import tqdm
from .utils import *
from .selector import Selector
import numpy as np
import matplotlib.pyplot as plt

class RecoursiveFeatureAddition(Selector):
    """
    Класс для перебора комбинаций признаков с целью нахождения лучшего набора
    по заданной метрике для задачи классификации.
    """
    
    def __init__(self, fixed_features=None, max_iter=3, maximization='test'):
        """
        Инициализация класса.
        
        Parameters:
        -----------
        fixed_features : list, optional
            Список признаков, которые всегда должны присутствовать
        n_combinations : int, default=3
            Количество комбинаций для перебора
        maximization: str
            Какая метрика максимизируется: test, (test + train) / 2
        """
        self.fixed_features = fixed_features if fixed_features else []
        self.max_iter = max_iter
        self.results_df = None
        self.best_features_ = None
        self.best_score_ = None
        self.maximization = maximization
        Selector.__init__(self)

    def _pipeline_init_lists(self, X):
        """Получение списка признаков"""
        all_features = X.columns.tolist()
        self.selected_features = self.fixed_features.copy()
        self.remaining_features = [f for f in all_features if f not in self.fixed_features]
        assert len(self.remaining_features) >= self.max_iter, 'Кол-во признаков должно быть больше, чем кол-во итераций rfa'
    
    def _update_lists(self, feature):
        self.selected_features.append(feature)
        self.remaining_features.remove(feature)
        
    def eval_function(self):
        # Валидация
        self._pipeline_init_lists(self._X_train)
        self.results_df = pd.DataFrame([self.validate_model_pipeline(self.fixed_features)])

        if self._maximize_bool:
            find_best_fn = np.argmax
        else:
            find_best_fn = np.argmin

        for iter_ in range(self.max_iter):
            with parallel_config(backend='threading', n_jobs=self._n_jobs):
                results = Parallel()(delayed(self.validate_model_pipeline)(self.selected_features + [remaining_feature]) for remaining_feature in tqdm(self.remaining_features))    
            
            if self.maximization == 'test':
                metric_values = [item[f'test_{self._metric_name}'] for item in results]
            elif self.maximization == 'train+test':
                metric_values = [item[f'test_{self._metric_name}'] + item[f'train_{self._metric_name}'] for item in results]
            
            best_idx = find_best_fn(metric_values)
            results[best_idx]['appended_feature'] = self.remaining_features.copy()[best_idx]
            df_to_append = pd.DataFrame([results[best_idx]])
            self._update_lists(self.remaining_features[best_idx])
            self.results_df = pd.concat([self.results_df, df_to_append], axis=0, ignore_index=True)

    def plot_evals(self, filename, figsize=(15, 8)):
        plt.figure(figsize=figsize)
        plt.title(self._metric_name)
        iter_list = range(self.max_iter + 1)
        plt.scatter(iter_list, self.results_df[f'train_{self._metric_name}'], color='r')
        plt.plot(iter_list, self.results_df[f'train_{self._metric_name}'], color='r', label='train', linestyle='--')
        plt.scatter(iter_list, self.results_df[f'test_{self._metric_name}'], color='b')
        plt.plot(iter_list, self.results_df[f'test_{self._metric_name}'], color='b', label='test', linestyle='--')
        plt.xticks(iter_list, self.results_df['appended_feature'], rotation=45)
        plt.legend()
        plt.savefig(filename)