import pandas as pd

class FeelTheAgiDataset:
    def __init__(self, data_path='none', target_col='class'):
        if data_path == 'none':
            self.data = None
            self.target = None
        else:
            if '.csv' in data_path:
                self.data = pd.read_csv(data_path)
            elif '.parquet' in data_path:
                self.data = pd.read_parquet(data_path)
            elif '.xlsx' in data_path:
                self.data = pd.read_excel(data_path)
            else:
                raise ValueError('Make sure you are uploading a csv, xlsx or parquet spreadsheet.')
            self.target = target_col
    
    def from_pandas(self, df, target_col):
        self.data = df
        self.target = target_col
        return self
    
    def transform(self, data_type='pandas'):
        if data_type == 'pandas':
            return self.data
        elif data_type == 'numpy':
            return self.data.to_numpy()
    
    def get_target_col(self):
        return self.target