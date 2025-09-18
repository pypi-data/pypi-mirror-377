import pandas as pd
from joblib import Parallel, delayed, parallel_config
from tqdm import tqdm
from .utils import *
from .selector import Selector

class FeatureCombinatorialSearch(Selector):
    """
    Класс для перебора комбинаций признаков с целью нахождения лучшего набора
    по заданной метрике для задачи классификации.
    """
    
    def __init__(self, fixed_features=None, n_combinations=3):
        """
        Инициализация класса.
        
        Parameters:
        -----------
        fixed_features : list, optional
            Список признаков, которые всегда должны присутствовать
        n_combinations : int, default=3
            Количество комбинаций для перебора
        """
        self.fixed_features = fixed_features if fixed_features else []
        self.n_combinations = n_combinations
        self.results_df = None
        self.best_features_ = None
        self.best_score_ = None
        Selector.__init__(self)

    def _combinate_features(self, X):
        """Получение комбинаций"""
        all_features = X.columns.tolist()
        variable_features = [f for f in all_features if f not in self.fixed_features]
        assert len(variable_features) >= self.n_combinations, 'Кол-во признаков должно быть больше, чем кол-во указанных комбинаций'

        # Получение комбинаций
        self.feature_combinations = obtain_combinations(
            features_to_combinate=variable_features,
            fixed_features=self.fixed_features,
            n_comb=self.n_combinations
        )
        self._len_combinations = len(self.feature_combinations)
        
    def eval_function(self):
        # Валидация
        self._combinate_features(self._X_train)
        with parallel_config(backend='threading', n_jobs=self._n_jobs):
            results = Parallel()(delayed(self.validate_model_pipeline)(feature_set) for feature_set in tqdm(self.feature_combinations))      
        self.results_df = pd.DataFrame(results)

    @property
    def best_features(self):
        return self.results_df.sort_values(by=f'test_{self._metric_name}', ascending=True if not self._maximize_bool else False).iloc[0]['feature_set']
        

