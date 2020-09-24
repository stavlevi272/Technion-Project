import pandas as pd

class CsvReader:
    def __init__(self):
        pass

    def read_all_csv(self, filename):
        return pd.read_csv(str(filename)+'.csv')

    def read_partial_csv(self, data, colunms):
        return data[colunms]
