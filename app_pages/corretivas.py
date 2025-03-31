import streamlit as st
import pandas as pd
from components import titulo_page
from datetime import datetime


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
        'Nº OS', 'STATUS', 'TIPO DE OS','NATUREZA', 'SOLICITANTE', 'DESCRIÇÃO', 
        'QTD_TECNICOS', 'TECNICO', 'EQUIPE',  'Data/Hora Abertura', 'Data/Hora Início',
       'Data/Hora Término', 'Atendimento', 'Solução', 'Execução'
    ]

    df = df.reindex(columns=COLUNAS_EXIBICAO)
     # Coloca cor na coluna Status
    df = df.style.map(colorir_status, subset=["STATUS"])  
      
    return df


# FUNÇÂO PRINCIPAL DO MÓDULO


def corretivas(): 
    st.markdown(titulo_page('OS Corretivas', 'Criadas no mês, Abertas e Encerradas no Mês'), unsafe_allow_html=True)
    with st.expander("Filtros"):
            st.write('''
                The chart above shows some numbers I picked for you.
                I rolled actual dice for these, so they're *guaranteed* to
                be random.
            ''')    
    st.dataframe(exibir_corretivas(), selection_mode="multi", use_container_width= True, hide_index=True)
if __name__ == "__page__":
    corretivas()