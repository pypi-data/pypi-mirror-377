import catboost as cb
import xgboost as xgb
import lightgbm as lgbm
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, ExtraTreesClassifier, ExtraTreesRegressor
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.svm import LinearSVC, LinearSVR

import pandas as pd
import sklearn.metrics as metrics
import numpy as np
from tqdm.notebook import tqdm

from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold, KFold
from sklearn.preprocessing import LabelEncoder
from sklearn.impute import KNNImputer
from functools import partial
import optuna
import warnings
warnings.filterwarnings('ignore')

from dataset import FeelTheAgiDataset


class ProgressBarCallback:
    """Callback для отображения прогресса Optuna в tqdm"""
    def __init__(self, n_trials):
        self.pbar = tqdm(total=n_trials, desc="Optimizing hyperparameters")
        self.best_value = None
        
    def __call__(self, study, trial):
        if self.best_value is None or trial.value != self.best_value:
            self.best_value = trial.value
            if study.direction == optuna.study.StudyDirection.MAXIMIZE:
                self.pbar.set_postfix(best_value=f"{trial.value:.4f}", refresh=False)
            else:
                self.pbar.set_postfix(best_value=f"{-trial.value:.4f}", refresh=False)
        self.pbar.update(1)
        
    def close(self):
        self.pbar.close()


class FeelTheAgiAutoML:
    def __init__(self, task:str ='multi_classification', text_columns: list =[], kfold_training: bool=False, 
                 imputer_strategy:str ='zero', n_trials:int =20, timeout:int =300, cv_folds:int =5, random_state:int =42):
        self.task = task
        self.kfold_training = kfold_training
        self.best_models = None
        self.cat_encoders = {}
        self.imputer_strategy = imputer_strategy
        self.text_columns = text_columns
        self.knn_imputer = None
        self.nans_models = {}
        self.training_cols = None
        self.max_classes = None
        self.data = None
        self.n_trials = n_trials
        self.timeout = timeout
        self.cv_folds = cv_folds
        self.random_state = random_state
        self.best_params = {}
        self.cv_scores = {}
    
    def set_data(self, data):
        """Метод для установки данных"""
        self.data = data

    def set_data(self, data):
        """Метод для установки данных"""
        self.data = data
    
    def get_cv_strategy(self):
        """Получение стратегии кросс-валидации"""
        if self.task != 'regression':
            return StratifiedKFold(n_splits=self.cv_folds, shuffle=True, random_state=self.random_state)
        else:
            return KFold(n_splits=self.cv_folds, shuffle=True, random_state=self.random_state)
    
    def get_models(self, params_dict=None):
        """Получение моделей с оптимизированными параметрами"""
        if params_dict is None:
            params_dict = {}
        
        # Функция для удаления префиксов из параметров
        def remove_prefix(params, prefix):
            cleaned_params = {}
            for key, value in params.items():
                if key.startswith(prefix):
                    cleaned_key = key.replace(prefix, '')
                    cleaned_params[cleaned_key] = value
                else:
                    cleaned_params[key] = value
            return cleaned_params
        
        # Очищаем параметры для каждой модели
        cleaned_params = {}
        for model_name in ["CatBoost", "XGBoost", "LightGBM", "RandomForest"]:
            if model_name in params_dict:
                if model_name == "CatBoost":
                    cleaned_params[model_name] = remove_prefix(params_dict[model_name], 'cb_')
                elif model_name == "XGBoost":
                    cleaned_params[model_name] = remove_prefix(params_dict[model_name], 'xgb_')
                elif model_name == "LightGBM":
                    cleaned_params[model_name] = remove_prefix(params_dict[model_name], 'lgbm_')
                # elif model_name == "RandomForest":
                #     cleaned_params[model_name] = remove_prefix(params_dict[model_name], 'rf_')
            else:
                cleaned_params[model_name] = {}
        
        if self.task in ['multi_classification', 'binary_classification']:
            models = {
                "CatBoost": cb.CatBoostClassifier(
                    verbose=0, 
                    random_state=self.random_state,
                    **cleaned_params["CatBoost"]
                ),
                "XGBoost": xgb.XGBClassifier(
                    verbose=0, 
                    random_state=self.random_state,
                    **cleaned_params["XGBoost"]
                ),
                "LightGBM": lgbm.LGBMClassifier(
                    verbose=0, 
                    random_state=self.random_state,
                    **cleaned_params["LightGBM"]
                ),
                # "RandomForest": RandomForestClassifier(
                #     random_state=self.random_state, 
                #     n_jobs=-1,
                #     **cleaned_params["RandomForest"]
                # ),
            }
        else:
            models = {
                "CatBoost": cb.CatBoostRegressor(
                    verbose=0, 
                    random_state=self.random_state,
                    **cleaned_params["CatBoost"]
                ),
                "XGBoost": xgb.XGBRegressor(
                    verbose=0, 
                    random_state=self.random_state,
                    **cleaned_params["XGBoost"]
                ),
                "LightGBM": lgbm.LGBMRegressor(
                    verbose=0, 
                    random_state=self.random_state,
                    **cleaned_params["LightGBM"]
                ),
                # "RandomForest": RandomForestRegressor(
                #     random_state=self.random_state, 
                #     n_jobs=-1,
                #     **cleaned_params["RandomForest"]
                # ),
            }
        return models
    
    def data_preprocessing(self, data: FeelTheAgiDataset, is_train=True):
        assert type(data) is FeelTheAgiDataset
        pandas_df = data.transform('pandas').copy()

        # Определяем числовые и категориальные колонки
        num_cols = pandas_df.select_dtypes(include=['int', 'float']).columns.tolist()
        cat_cols = pandas_df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        # Сохраняем для использования в других методах
        if is_train:
            self.num_cols = num_cols
            self.cat_cols = cat_cols

        # Заполняем пропуски в текстовых колонках
        print(f'===================Заполняю пропуски. Стратегия: {self.imputer_strategy}===================')
        for col in self.text_columns:
            if col in pandas_df.columns and pandas_df[col].isna().sum() > 0:
                pandas_df[col] = pandas_df[col].fillna('')

        # Обработка пропусков
        if self.imputer_strategy == 'zero':
            for col in num_cols:
                pandas_df[col] = pandas_df[col].fillna(0)
            
            for col in cat_cols:
                if col not in self.text_columns:
                    pandas_df[col] = pandas_df[col].fillna('')
        elif self.imputer_strategy == 'mean':
            for col in num_cols:
                pandas_df[col] = pandas_df[col].fillna(pandas_df[col].mean())
                
            for col in cat_cols:
                if col not in self.text_columns:
                    pandas_df[col] = pandas_df[col].fillna('')
        elif self.imputer_strategy == 'median':
            for col in num_cols:
                pandas_df[col] = pandas_df[col].fillna(pandas_df[col].median())
            
            for col in cat_cols:
                if col not in self.text_columns:
                    pandas_df[col] = pandas_df[col].fillna('')
        elif self.imputer_strategy == 'KNN':
            if is_train:
                knn_imputer = KNNImputer()
                pandas_df[num_cols] = pd.DataFrame(
                    knn_imputer.fit_transform(pandas_df[num_cols]), 
                    columns=num_cols, 
                    index=pandas_df.index
                )
                self.knn_imputer = knn_imputer
            else:
                knn_imputer = self.knn_imputer
                pandas_df[num_cols] = pd.DataFrame(
                    knn_imputer.transform(pandas_df[num_cols]), 
                    columns=num_cols, 
                    index=pandas_df.index
                )
            
            for col in cat_cols:
                if col not in self.text_columns:
                    pandas_df[col] = pandas_df[col].fillna('')
        elif self.imputer_strategy == 'predict':
            # Сначала заполняем текстовые колонки
            for col in self.text_columns:
                if col in pandas_df.columns and pandas_df[col].isna().sum() > 0:
                    pandas_df[col] = pandas_df[col].fillna('')
            
            for col in cat_cols:
                if col not in self.text_columns:
                    pandas_df[col] = pandas_df[col].fillna('')

            pandas_df_copy = pandas_df.copy()
            target_col = data.get_target_col()
            
            for col in num_cols:
                if pandas_df_copy[col].isna().sum() > 0:
                    if pandas_df_copy[col].nunique() / len(pandas_df_copy) >= 0.5:
                        # REGRESSION
                        if is_train:
                            not_nans_df = pandas_df_copy.dropna(subset=[col])
                            if len(not_nans_df) > 0:
                                X = not_nans_df.drop(columns=[col, target_col])
                                y = not_nans_df[col]
                                
                                if len(X) > 1:
                                    X_train, X_val, y_train, y_val = train_test_split(X, y, random_state=42, shuffle=True)
                                    
                                    # Исключаем текстовые колонки
                                    features_to_drop = [col for col in self.text_columns if col in X.columns]
                                    X_train = X_train.drop(columns=features_to_drop)
                                    X_val = X_val.drop(columns=features_to_drop)
                                    
                                    # Подготовка категориальных признаков для CatBoost
                                    cat_features = [col for col in cat_cols if col not in self.text_columns and col in X_train.columns]
                                    
                                    if len(cat_features) > 0:
                                        nans_model = cb.CatBoostRegressor(verbose=0, cat_features=cat_features)
                                    else:
                                        nans_model = cb.CatBoostRegressor(verbose=0)
                                    
                                    nans_model.fit(X_train, y_train, eval_set=(X_val, y_val), use_best_model=True)
                                    self.nans_models[col] = nans_model
                                    
                                    # Заполняем пропуски
                                    mask = pandas_df_copy[col].isna()
                                    if mask.sum() > 0:
                                        nans_df = pandas_df_copy.loc[mask].drop(columns=[col, target_col])
                                        nans_df = nans_df.drop(columns=features_to_drop)
                                        nans_predicted = nans_model.predict(nans_df)
                                        pandas_df_copy.loc[mask, col] = nans_predicted
                        else:
                            if col in self.nans_models:
                                nans_model = self.nans_models[col]
                                mask = pandas_df_copy[col].isna()
                                if mask.sum() > 0:
                                    nans_df = pandas_df_copy.loc[mask].drop(columns=[col, target_col])
                                    features_to_drop = [col for col in self.text_columns if col in nans_df.columns]
                                    nans_df = nans_df.drop(columns=features_to_drop)
                                    nans_predicted = nans_model.predict(nans_df)
                                    pandas_df_copy.loc[mask, col] = nans_predicted
                    else:
                        # CLASSIFICATION
                        if is_train:
                            not_nans_df = pandas_df_copy.dropna(subset=[col])
                            if len(not_nans_df) > 0:
                                X = not_nans_df.drop(columns=[col, target_col])
                                y = not_nans_df[col]
                                
                                if len(X) > 1:
                                    X_train, X_val, y_train, y_val = train_test_split(X, y, random_state=42, shuffle=True)
                                    
                                    features_to_drop = [col for col in self.text_columns if col in X.columns]
                                    X_train = X_train.drop(columns=features_to_drop)
                                    X_val = X_val.drop(columns=features_to_drop)
                                    
                                    cat_features = [col for col in cat_cols if col not in self.text_columns and col in X_train.columns]
                                    
                                    if len(cat_features) > 0:
                                        nans_model = cb.CatBoostClassifier(verbose=0, cat_features=cat_features)
                                    else:
                                        nans_model = cb.CatBoostClassifier(verbose=0)
                                    
                                    nans_model.fit(X_train, y_train, eval_set=(X_val, y_val), use_best_model=True)
                                    self.nans_models[col] = nans_model
                                    
                                    mask = pandas_df_copy[col].isna()
                                    if mask.sum() > 0:
                                        nans_df = pandas_df_copy.loc[mask].drop(columns=[col, target_col])
                                        nans_df = nans_df.drop(columns=features_to_drop)
                                        nans_predicted = nans_model.predict(nans_df)
                                        pandas_df_copy.loc[mask, col] = nans_predicted
                        else:
                            if col in self.nans_models:
                                nans_model = self.nans_models[col]
                                mask = pandas_df_copy[col].isna()
                                if mask.sum() > 0:
                                    nans_df = pandas_df_copy.loc[mask].drop(columns=[col, target_col])
                                    features_to_drop = [col for col in self.text_columns if col in nans_df.columns]
                                    nans_df = nans_df.drop(columns=features_to_drop)
                                    nans_predicted = nans_model.predict(nans_df)
                                    pandas_df_copy.loc[mask, col] = nans_predicted
            
            pandas_df = pandas_df_copy

        print(f'===================Кодирование категориальных переменных===================')
        if is_train:
            for col in cat_cols:
                if col in self.text_columns:
                    continue
                le = LabelEncoder()
                pandas_df[col] = le.fit_transform(pandas_df[col].astype(str))
                self.cat_encoders[col] = le
        else:
            for col in cat_cols:
                if col in self.text_columns:
                    continue
                if col in self.cat_encoders:
                    le = self.cat_encoders[col]
                    # Обработка новых категорий в тестовых данных
                    unique_values = set(pandas_df[col].astype(str).unique())
                    trained_values = set(le.classes_)
                    new_values = unique_values - trained_values
                    
                    if new_values:
                        # Заменяем новые значения на наиболее частую категорию
                        most_frequent = le.classes_[0]
                        pandas_df[col] = pandas_df[col].astype(str).apply(lambda x: x if x in trained_values else most_frequent)
                    
                    pandas_df[col] = le.transform(pandas_df[col].astype(str))
        
        return FeelTheAgiDataset().from_pandas(pandas_df, data.get_target_col())

    def get_model_hyperparameters(self, model_name, trial):
        """Генерация гиперпараметров для Optuna"""
        if model_name == "CatBoost":
            if self.task in ['multi_classification', 'binary_classification']:
                params = {
                    'iterations': trial.suggest_int('cb_iterations', 100, 1000),
                    'depth': trial.suggest_int('cb_depth', 3, 10),
                    'learning_rate': trial.suggest_loguniform('cb_learning_rate', 0.01, 0.3),
                    'l2_leaf_reg': trial.suggest_loguniform('cb_l2_leaf_reg', 1, 10),
                    'border_count': trial.suggest_int('cb_border_count', 32, 255),
                    'random_strength': trial.suggest_loguniform('cb_random_strength', 1e-9, 10),
                }
            else:
                params = {
                    'iterations': trial.suggest_int('cb_iterations', 100, 1000),
                    'depth': trial.suggest_int('cb_depth', 3, 10),
                    'learning_rate': trial.suggest_loguniform('cb_learning_rate', 0.01, 0.3),
                    'l2_leaf_reg': trial.suggest_loguniform('cb_l2_leaf_reg', 1, 10),
                }
        
        elif model_name == "XGBoost":
            if self.task in ['multi_classification', 'binary_classification']:
                params = {
                    'n_estimators': trial.suggest_int('xgb_n_estimators', 50, 500),
                    'max_depth': trial.suggest_int('xgb_max_depth', 3, 10),
                    'learning_rate': trial.suggest_loguniform('xgb_learning_rate', 0.01, 0.3),
                    'subsample': trial.suggest_float('xgb_subsample', 0.6, 1.0),
                    'colsample_bytree': trial.suggest_float('xgb_colsample_bytree', 0.6, 1.0),
                    'gamma': trial.suggest_float('xgb_gamma', 0, 5),
                    'reg_alpha': trial.suggest_float('xgb_reg_alpha', 0, 10),
                    'reg_lambda': trial.suggest_float('xgb_reg_lambda', 1, 10),
                }
            else:
                params = {
                    'n_estimators': trial.suggest_int('xgb_n_estimators', 50, 500),
                    'max_depth': trial.suggest_int('xgb_max_depth', 3, 10),
                    'learning_rate': trial.suggest_loguniform('xgb_learning_rate', 0.01, 0.3),
                    'subsample': trial.suggest_float('xgb_subsample', 0.6, 1.0),
                    'colsample_bytree': trial.suggest_float('xgb_colsample_bytree', 0.6, 1.0),
                }
        
        elif model_name == "LightGBM":
            if self.task in ['multi_classification', 'binary_classification']:
                params = {
                    'n_estimators': trial.suggest_int('lgbm_n_estimators', 50, 500),
                    'max_depth': trial.suggest_int('lgbm_max_depth', 3, 12),
                    'learning_rate': trial.suggest_loguniform('lgbm_learning_rate', 0.01, 0.3),
                    'num_leaves': trial.suggest_int('lgbm_num_leaves', 20, 100),
                    'subsample': trial.suggest_float('lgbm_subsample', 0.6, 1.0),
                    'colsample_bytree': trial.suggest_float('lgbm_colsample_bytree', 0.6, 1.0),
                    'reg_alpha': trial.suggest_float('lgbm_reg_alpha', 0, 10),
                    'reg_lambda': trial.suggest_float('lgbm_reg_lambda', 0, 10),
                }
            else:
                params = {
                    'n_estimators': trial.suggest_int('lgbm_n_estimators', 50, 500),
                    'max_depth': trial.suggest_int('lgbm_max_depth', 3, 12),
                    'learning_rate': trial.suggest_loguniform('lgbm_learning_rate', 0.01, 0.3),
                    'num_leaves': trial.suggest_int('lgbm_num_leaves', 20, 100),
                }
        
        elif model_name == "RandomForest":
            if self.task in ['multi_classification', 'binary_classification']:
                params = {
                    'n_estimators': trial.suggest_int('rf_n_estimators', 50, 300),
                    'max_depth': trial.suggest_int('rf_max_depth', 3, 20),
                    'min_samples_split': trial.suggest_int('rf_min_samples_split', 2, 20),
                    'min_samples_leaf': trial.suggest_int('rf_min_samples_leaf', 1, 10),
                    'max_features': trial.suggest_categorical('rf_max_features', ['sqrt', 'log2', None]),
                }
            else:
                params = {
                    'n_estimators': trial.suggest_int('rf_n_estimators', 50, 300),
                    'max_depth': trial.suggest_int('rf_max_depth', 3, 20),
                    'min_samples_split': trial.suggest_int('rf_min_samples_split', 2, 20),
                    'min_samples_leaf': trial.suggest_int('rf_min_samples_leaf', 1, 10),
                }
        
        return params

    def optimize_hyperparameters(self, X, y, model_name):
        """Оптимизация гиперпараметров для конкретной модели с кросс-валидацией"""
        def objective(trial):
            # Получаем параметры для текущей модели
            params = self.get_model_hyperparameters(model_name, trial)
            
            # Очищаем параметры от префиксов для обучения
            if model_name == "CatBoost":
                cleaned_params = {k.replace('cb_', ''): v for k, v in params.items()}
            elif model_name == "XGBoost":
                cleaned_params = {k.replace('xgb_', ''): v for k, v in params.items()}
            elif model_name == "LightGBM":
                cleaned_params = {k.replace('lgbm_', ''): v for k, v in params.items()}
            elif model_name == "RandomForest":
                cleaned_params = {k.replace('rf_', ''): v for k, v in params.items()}
            else:
                cleaned_params = params
            
            # Создаем модель с предложенными параметрами
            if model_name == "CatBoost":
                if self.task in ['multi_classification', 'binary_classification']:
                    model = cb.CatBoostClassifier(verbose=0, random_state=self.random_state, **cleaned_params)
                else:
                    model = cb.CatBoostRegressor(verbose=0, random_state=self.random_state, **cleaned_params)
            elif model_name == "XGBoost":
                if self.task in ['multi_classification', 'binary_classification']:
                    model = xgb.XGBClassifier(verbose=0, random_state=self.random_state, **cleaned_params)
                else:
                    model = xgb.XGBRegressor(verbose=0, random_state=self.random_state, **cleaned_params)
            elif model_name == "LightGBM":
                if self.task in ['multi_classification', 'binary_classification']:
                    model = lgbm.LGBMClassifier(verbose=0, random_state=self.random_state, **cleaned_params)
                else:
                    model = lgbm.LGBMRegressor(verbose=0, random_state=self.random_state, **cleaned_params)
            elif model_name == "RandomForest":
                if self.task in ['multi_classification', 'binary_classification']:
                    model = RandomForestClassifier(random_state=self.random_state, n_jobs=-1, **cleaned_params)
                else:
                    model = RandomForestRegressor(random_state=self.random_state, n_jobs=-1, **cleaned_params)
            
            # Кросс-валидация для оценки качества
            cv = self.get_cv_strategy()
            
            if self.task != 'regression':
                scores = cross_val_score(model, X, y, cv=cv, scoring='f1_macro', n_jobs=-1)
                score = np.mean(scores)
                score_std = np.std(scores)
            else:
                scores = cross_val_score(model, X, y, cv=cv, scoring='neg_root_mean_squared_error', n_jobs=-1)
                score = -np.mean(scores)
                score_std = np.std(scores)
            
            # Сохраняем стандартное отклонение для анализа стабильности
            trial.set_user_attr('cv_std', score_std)
            
            return score
        
        # Создаем исследование Optuna с прогресс-баром
        study = optuna.create_study(direction='maximize' if self.task != 'regression' else 'minimize')
        
        # Создаем callback с прогресс-баром
        progress_callback = ProgressBarCallback(self.n_trials)
        
        try:
            study.optimize(
                objective, 
                n_trials=self.n_trials, 
                timeout=self.timeout,
                callbacks=[progress_callback],
                show_progress_bar=False
            )
        finally:
            progress_callback.close()
        
        # Возвращаем параметры с префиксами (для сохранения)
        return study.best_params, study.best_value, study.best_trial.user_attrs.get('cv_std', 0)

    def train_with_cross_validation(self, X, y, model, model_name):
        """Обучение модели с кросс-валидацией и возвратом OOF предсказаний"""
        cv = self.get_cv_strategy()
        oof_preds = np.zeros(len(y))
        oof_probas = None
        models = []
        
        if self.task != 'regression':
            oof_probas = np.zeros((len(y), len(np.unique(y))))
        
        print(f"  Cross-validation for {model_name} ({self.cv_folds} folds):")
        
        for fold, (train_idx, val_idx) in enumerate(tqdm(cv.split(X, y), total=self.cv_folds, desc=f"CV {model_name}")):
            X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
            y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
            
            # Клонируем модель для каждого фолда
            if hasattr(model, 'copy'):
                fold_model = model.copy()
            else:
                if hasattr(model, '__copy__'):
                    fold_model = model.__copy__()
                else:
                    fold_model = model
            
            fold_model.fit(X_train, y_train)
            models.append(fold_model)
            
            if self.task == 'regression':
                fold_preds = fold_model.predict(X_val)
                oof_preds[val_idx] = fold_preds
            else:
                if hasattr(fold_model, 'predict_proba'):
                    fold_probas = fold_model.predict_proba(X_val)
                    oof_probas[val_idx] = fold_probas
                    oof_preds[val_idx] = np.argmax(fold_probas, axis=1)
                else:
                    fold_preds = fold_model.predict(X_val)
                    oof_preds[val_idx] = fold_preds
        
        # Вычисляем метрики OOF
        if self.task != 'regression':
            oof_score = metrics.f1_score(y, oof_preds, average='macro')
            print(f"  {model_name} OOF F1: {oof_score:.4f}")
        else:
            oof_score = metrics.mean_squared_error(y, oof_preds) ** 0.5
            print(f"  {model_name} OOF RMSE: {oof_score:.4f}")
        
        return models, oof_preds, oof_probas, oof_score

    def train(self, data: FeelTheAgiDataset, time_limit=None, max_models_for_blend=3, optimize_hyperparams=True, use_cv_training=False):
        """Основной метод обучения с кросс-валидацией"""
        self.data = data
        processed_data = self.data_preprocessing(data)
        
        X = processed_data.transform().drop(columns=[processed_data.get_target_col()])
        y = processed_data.transform()[processed_data.get_target_col()]

        # Определяем количество классов для классификации
        if self.task != 'regression':
            self.max_classes = len(np.unique(y))
        
        self.training_cols = X.columns.tolist()

        if use_cv_training:
            print("===================Training with Cross-Validation===================")
            models_dict = self.get_models()
            training_info = {}
            models_cv = {}  # Список моделей для каждого фолда
            oof_predictions = {}
            oof_probas_dict = {}
            oof_scores = {}
            
            # Определяем категориальные признаки для CatBoost
            cat_features_indices = []
            if 'CatBoost' in models_dict:
                for i, col in enumerate(X.columns):
                    if col in self.cat_cols and col not in self.text_columns:
                        cat_features_indices.append(i)

            # Оптимизация гиперпараметров
            optimized_params = {}
            if optimize_hyperparams:
                print("===================Optimizing Hyperparameters with CV===================")
                for model_name in tqdm(models_dict.keys(), desc="Optimizing models"):
                    print(f"\nOptimizing {model_name}...")
                    best_params, best_score, cv_std = self.optimize_hyperparameters(X, y, model_name)
                    optimized_params[model_name] = best_params
                    
                    if self.task != 'regression':
                        print(f"{model_name} best CV F1: {best_score:.4f} ± {cv_std:.4f}")
                    else:
                        print(f"{model_name} best CV RMSE: {best_score:.4f} ± {cv_std:.4f}")
                
                self.best_params = optimized_params
                # Обновляем модели с оптимизированными параметрами
                models_dict = self.get_models(optimized_params)

            # Обучение моделей с кросс-валидацией
            for model_name in tqdm(models_dict, desc="Training CV models"):
                print(f'\nTraining {model_name} with {self.cv_folds}-fold CV...')
                model = models_dict[model_name]

                # Особенная обработка для CatBoost с категориальными признаками
                if model_name == 'CatBoost' and cat_features_indices:
                    model.set_params(cat_features=cat_features_indices)
                
                # Обучение с кросс-валидацией
                cv_models, oof_preds, oof_probas, oof_score = self.train_with_cross_validation(X, y, model, model_name)
                
                models_cv[model_name] = cv_models
                oof_predictions[model_name] = oof_preds
                oof_probas_dict[model_name] = oof_probas
                oof_scores[model_name] = oof_score
                training_info[model_name] = oof_score
            
            self.models_cv = models_cv
            self.oof_predictions = oof_predictions
            self.oof_probas_dict = oof_probas_dict
            
            # Блендинг OOF предсказаний
            print('\n===================Blending OOF Predictions===================')
            if self.task == 'regression':
                sorted_models = sorted(training_info.items(), key=lambda x: x[1])
            else:
                sorted_models = sorted(training_info.items(), key=lambda x: x[1], reverse=True)
            
            top_models_names = [name for name, _ in sorted_models[:max_models_for_blend]]
            
            if self.task == 'regression':
                # Блендинг для регрессии
                blended_preds = np.zeros(len(y))
                for model_name in top_models_names:
                    blended_preds += oof_predictions[model_name] / len(top_models_names)
                
                blended_score = metrics.mean_squared_error(y, blended_preds) ** 0.5
                print(f'Blended OOF RMSE: {blended_score:.4f}')
                best_single_score = sorted_models[0][1]
                is_better = blended_score < best_single_score
            else:
                # Блендинг для классификации
                blended_probas = np.zeros((len(y), self.max_classes))
                for model_name in top_models_names:
                    if oof_probas_dict[model_name] is not None:
                        # Модель возвращает вероятности
                        blended_probas += oof_probas_dict[model_name] / len(top_models_names)
                    else:
                        # Модель не возвращает вероятности - создаем one-hot encoding
                        preds_onehot = np.zeros((len(y), self.max_classes))
                        # Убедимся, что предсказания целочисленные
                        preds_int = oof_predictions[model_name].astype(int)
                        preds_onehot[np.arange(len(y)), preds_int] = 1
                        blended_probas += preds_onehot / len(top_models_names)
                
                blended_preds = np.argmax(blended_probas, axis=1)
                blended_score = metrics.f1_score(y, blended_preds, average='macro')
                print(f'Blended OOF F1: {blended_score:.4f}')
                best_single_score = sorted_models[0][1]
                is_better = blended_score > best_single_score

            if is_better:
                print(f'Best model: blending {", ".join(top_models_names)}')
                self.best_models = [models_cv[name] for name in top_models_names]
                self.blend_weights = [1.0/len(top_models_names)] * len(top_models_names)
            else:
                best_model_name = sorted_models[0][0]
                print(f'Best model: {best_model_name}')
                self.best_models = [models_cv[best_model_name]]
                self.blend_weights = [1.0]
                
        else:
            # Старая логика без кросс-валидации
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, shuffle=True, random_state=self.random_state, test_size=0.2
            )
            
            models_dict = self.get_models()
            training_info = {}
            models = {}

            # Определяем категориальные признаки для CatBoost
            cat_features_indices = []
            if 'CatBoost' in models_dict:
                for i, col in enumerate(X.columns):
                    if col in self.cat_cols and col not in self.text_columns:
                        cat_features_indices.append(i)

            for model_name in tqdm(models_dict, desc="Training models"):
                print(f'\nTraining {model_name}...')
                model = models_dict[model_name]

                if model_name == 'CatBoost' and cat_features_indices:
                    model.set_params(cat_features=cat_features_indices)
                
                model.fit(X_train, y_train)

                if self.task != 'regression':
                    y_pred = model.predict(X_test)
                    f1_macro = metrics.f1_score(y_test, y_pred, average='macro')
                    training_info[model_name] = f1_macro
                    models[model_name] = model
                    print(f'{model_name} f1 macro is {f1_macro:.4f}')
                else:
                    y_pred = model.predict(X_test)
                    rmse = metrics.mean_squared_error(y_test, y_pred) ** 0.5
                    training_info[model_name] = rmse
                    models[model_name] = model
                    print(f'{model_name} RMSE is {rmse:.4f}')
            
            # Блендинг
            print('\n===================Blending===================')
            if self.task == 'regression':
                sorted_models = sorted(training_info.items(), key=lambda x: x[1])
            else:
                sorted_models = sorted(training_info.items(), key=lambda x: x[1], reverse=True)
            
            top_models_names = [name for name, _ in sorted_models[:max_models_for_blend]]
            top_models_list = [models[name] for name in top_models_names]

            if self.task == 'regression':
                preds = np.zeros(len(X_test))
                for model in top_models_list:
                    preds += model.predict(X_test) / len(top_models_list)
                
                blended_rmse = metrics.mean_squared_error(y_test, preds) ** 0.5
                print(f'RMSE after blend: {blended_rmse:.4f}')
                best_single_rmse = sorted_models[0][1]
                is_better = blended_rmse < best_single_rmse
            else:
                preds = np.zeros((len(X_test), self.max_classes))
                for model in top_models_list:
                    if hasattr(model, 'predict_proba'):
                        preds += model.predict_proba(X_test) / len(top_models_list)
                    else:
                        preds_temp = np.zeros((len(X_test), self.max_classes))
                        preds_temp[np.arange(len(X_test)), model.predict(X_test)] = 1
                        preds += preds_temp / len(top_models_list)
                
                blended_preds = np.argmax(preds, axis=1)
                f1_macro = metrics.f1_score(y_test, blended_preds, average='macro')
                print(f'F1 macro after blend: {f1_macro:.4f}')
                best_single_f1 = sorted_models[0][1]
                is_better = f1_macro > best_single_f1

            if is_better:
                print(f'Best model: blending {", ".join(top_models_names)}')
                self.best_models = top_models_list
            else:
                best_model_name = sorted_models[0][0]
                print(f'Best model: {best_model_name}')
                self.best_models = [models[best_model_name]]

    
    def predict(self, test_data: FeelTheAgiDataset):
        """Предсказание с использованием моделей, обученных через CV"""
        processed_test_data = self.data_preprocessing(test_data, is_train=False)
        X_test = processed_test_data.transform()[self.training_cols]
        
        if hasattr(self, 'models_cv') and self.models_cv:
            # Предсказание для моделей, обученных через CV
            if self.task == 'regression':
                preds = np.zeros(len(X_test))
                for i, model_list in enumerate(self.best_models):
                    weight = self.blend_weights[i]
                    for model in model_list:
                        preds += model.predict(X_test) * weight / len(model_list)
                return preds
            else:
                preds = np.zeros((len(X_test), self.max_classes))
                for i, model_list in enumerate(self.best_models):
                    weight = self.blend_weights[i]
                    for model in model_list:
                        if hasattr(model, 'predict_proba'):
                            preds += model.predict_proba(X_test) * weight / len(model_list)
                        else:
                            preds_temp = np.zeros((len(X_test), self.max_classes))
                            preds_temp[np.arange(len(X_test)), model.predict(X_test)] = 1
                            preds += preds_temp * weight / len(model_list)
                return np.argmax(preds, axis=1)
        else:
            # Старая логика предсказания
            if self.task == 'regression':
                preds = np.zeros(len(X_test))
                for model in self.best_models:
                    preds += model.predict(X_test) / len(self.best_models)
                return preds
            else:
                if all(hasattr(model, 'predict_proba') for model in self.best_models):
                    preds = np.zeros((len(X_test), self.max_classes))
                    for model in self.best_models:
                        preds += model.predict_proba(X_test) / len(self.best_models)
                    return np.argmax(preds, axis=1)
                else:
                    preds = np.zeros(len(X_test))
                    for model in self.best_models:
                        preds += model.predict(X_test) / len(self.best_models)
                    return np.round(preds).astype(int)
    
    def predict_proba(self, test_data: FeelTheAgiDataset):
        """Предсказание вероятностей (только для классификации)"""
        if self.task == 'regression':
            raise ValueError("predict_proba is only available for classification tasks")
        
        processed_test_data = self.data_preprocessing(test_data, is_train=False)
        X_test = processed_test_data.transform()[self.training_cols]
        
        preds = np.zeros((len(X_test), self.max_classes))
        for model in self.best_models:
            if hasattr(model, 'predict_proba'):
                preds += model.predict_proba(X_test) / len(self.best_models)
            else:
                # Для моделей без predict_proba создаем one-hot encoding
                preds_temp = np.zeros((len(X_test), self.max_classes))
                preds_temp[np.arange(len(X_test)), model.predict(X_test)] = 1
                preds += preds_temp / len(self.best_models)
        
        return preds


# # Example of usage:

# data = FeelTheAgiDataset('data/train.csv', 'target')
# automl = FeelTheAgiAutoML(task='multi_classification', n_trials=7, timeout=900)
# automl.train(data, optimize_hyperparams=True, max_models_for_blend=3, use_cv_training=True)

# test_data = FeelTheAgiDataset('data/test.csv')
# preds = automl.predict(test_data)