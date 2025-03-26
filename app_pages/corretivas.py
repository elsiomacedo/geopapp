import streamlit as st
import pandas as pd
from components import load_css, header_page
#from datasets.ds_corretivas import exibir_corretivas

def colorir_status(value):
    """
    Função para aplicar cores na coluna STATUS.
        Args:
        value: Valor da célula. 
    Returns:
        str: String CSS para estilizar a célula.
    """
    CORES_STATUS = {
        "ATENDIDO": "green",
        "ABERTO": "red"
    }       
    if isinstance(value, str) and value in CORES_STATUS:
             return f"color: {CORES_STATUS[value]}; font-weight: bold;"
    return ""

def exibir_corretivas():
    """
    Exibe o Dataframe de OS corretivos.
        Args:
        df (pandas.DataFrame): DataFrame com os dados para exibição.
    """    
    df = pd.read_csv('dados/DBCorretivas.csv', encoding='utf-8')    

    COLUNAS_EXIBICAO = [
        'Nº OS', 'STATUS', 'TIPO DE OS','NATUREZA',  
        'SOLICITANTE', 'DESCRIÇÃO', 'TECNICO', 'TIPO TECNICO', 'DTH_ABERTURA', 'DTH_INICIO', 'DTH_TERMINO'
    ]
    MAPEAMENTO_COLUNAS = {
        'TIPO TECNICO' : 'EQUIPE',
        'DTH_ABERTURA' : 'Data/Hora Abertura',
        'DTH_INICIO': 'Data/Hora Início',
        'DTH_TÉRMINO': 'Data/Hora Término'
    }
    df_corretivas = df[COLUNAS_EXIBICAO].copy()

    # Renomear colunas
    df_corretivas = df_corretivas.rename(columns=MAPEAMENTO_COLUNAS)
    # Coloca cor na coluna Status
    df_corretivas = df_corretivas.style.map(colorir_status, subset=["STATUS"])  
    # Converta o DataFrame para HTML
      
    return df_corretivas


"""
FUNÇÂO PRINCIPAL DO MÓDULO
"""

def corretivas(): 

    st.title('Ordens de Serviço Corretivas')
    st.write('Criadas no mês, Abertas e Encerradas no Mês')
    with st.expander("Filtros"):
            st.write('''
                The chart above shows some numbers I picked for you.
                I rolled actual dice for these, so they're *guaranteed* to
                be random.
            ''')    
    st.dataframe(exibir_corretivas())
if __name__ == "__page__":
    corretivas()