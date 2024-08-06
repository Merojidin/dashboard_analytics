import pandas as pd
from connector import set_connection

def read_query(query_name):
    with open(f'queries/{query_name}.sql', 'r') as f:
        return f.read()

def get_data(query_name):
    query = read_query(query_name)
    with set_connection() as ps:
        return pd.read_sql(query, ps)
    
def get_data_xlsx(csv_name):
    file_path = f'source/{csv_name}.xlsx'
    df = pd.read_excel(file_path)
    df.columns = [col.lower().replace(' ', '').replace('-', '') for col in df.columns]
    df = df.apply(lambda col: col.map(lambda x: x.strip().replace(',', '') if isinstance(x, str) else x))
    return df
