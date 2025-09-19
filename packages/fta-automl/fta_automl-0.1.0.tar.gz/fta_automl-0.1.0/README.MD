# FTA - AutoML Library

Example of usage:

```py
from fta_automl.dataset import FeelTheAgiDataset
from fta_automl.FTAutoML import FeelTheAgiAutoML

data = FeelTheAgiDataset('data/train.csv', 'target')
automl = FeelTheAgiAutoML(task='multi_classification', n_trials=7, timeout=900)
automl.train(data, optimize_hyperparams=True, max_models_for_blend=3, use_cv_training=True)

test_data = FeelTheAgiDataset('data/test.csv')
preds = automl.predict(test_data)
```