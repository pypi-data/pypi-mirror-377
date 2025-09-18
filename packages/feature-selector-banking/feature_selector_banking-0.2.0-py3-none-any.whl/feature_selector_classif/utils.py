from itertools import combinations
from sklearn.model_selection import train_test_split

def obtain_combinations(features_to_combinate: list, fixed_features: list, n_comb: int):
    """Получение комбинаций"""
    feature_combinations = list(combinations(features_to_combinate, n_comb))
    feature_combinations = [fixed_features.copy() + list(feature_combination) for feature_combination in feature_combinations]
    return feature_combinations

def default_splitter(test_size=0.25, random_state=33, shuffle=False, stratify=True):
    if not shuffle and stratify:
        return lambda X, y: train_test_split(X, y, test_size=test_size, random_state=random_state,  stratify=y)
    elif not shuffle and not stratify:
        return lambda X, y: train_test_split(X, y, test_size=test_size, random_state=random_state)
    else:
        return lambda X, y: train_test_split(X, y, test_size=test_size, random_state=random_state, shuffle=shuffle)