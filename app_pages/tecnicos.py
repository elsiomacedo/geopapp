import streamlit as st
import pandas as pd
from components import titulo_page

def colorir_status(value):
    """
    Função para aplicar cores na coluna STATUS.
        Args:
        value: Valor da célula. 
    Returns:
        str: String CSS para estilizar a célula.
    """
    CORES_STATUS = {
        "OS Corretiva": "blue",
        "Checklist": "green"
    }       
    if isinstance(value, str) and value in CORES_STATUS:
             return f"color: {CORES_STATUS[value]}; font-weight: bold;"
    return ""

def exibir_tecnicos():
    """
    Exibe o Dataframe de OS corretivos.
        Args:
        df (pandas.DataFrame): DataFrame com os dados para exibição.
    """    
    df = pd.read_csv('dados/DBTecno_All.csv', encoding='utf-8')    

     # Coloca cor na coluna Status
    df = df.style.map(colorir_status, subset=["TIPO"])  
      
    return df

def tecnicos(): 
    with st.sidebar.expander("Filtros"):
        st.write('''
            The chart above shows some numbers I picked for you.
            I rolled actual dice for these, so they're *guaranteed* to
            be random.
        ''')     
    st.markdown(titulo_page('Equipe Técnica', 'Produtividade Mês Atual'), unsafe_allow_html=True)
       
    df = pd.read_csv('dados/DBTecno_All.csv', encoding='utf-8')      
    st.dataframe(exibir_tecnicos(), selection_mode="multi", use_container_width= True, hide_index=True)  
if __name__ == "__page__":
    tecnicos()