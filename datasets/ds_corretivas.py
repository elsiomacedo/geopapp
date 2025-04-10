import pandas as pd

def carrega_dataset():
    # Definir o caminho do arquivo CSV
    csv_path = "dados/DBCorretivas.csv"
    df = pd.read_csv('dados/DBCorretivas.csv', encoding='utf-8')           
    return df    