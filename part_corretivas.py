import streamlit as st
from datasets.ds_corretivas import load_excel_data

FILE_XLS = 'historico_oss_corretivas.xls'
CORES_STATUS = {
    "ATENDIDO": "green",
    "ABERTO": "red"
}
COLUNAS_EXIBICAO = [
    'Nº OS', 'STATUS', 'NATUREZA', 'TIPO DE OS', 'DESCRIÇÃO', 
    'SOLICITANTE'
]
MAPEAMENTO_COLUNAS = {
    'DTH_ABERTURA': 'Data/Hora Abertura',
    'DTH_INÍCIO': 'Data/Hora Início',
    'DTH_TÉRMINO': 'Data/Hora Término'
}

def colorir_status(value):
    """
    Função para aplicar cores na coluna STATUS.
    
    Args:
        value: Valor da célula.
        
    Returns:
        str: String CSS para estilizar a célula.
    """
    if isinstance(value, str) and value in CORES_STATUS:
        return f"color: {CORES_STATUS[value]}; font-weight: bold;"
    return ""

def exibir_corretivas():
    """
    Exibe a aba de dados corretivos.
    
    Args:
        df (pandas.DataFrame): DataFrame com os dados para exibição.
    """
    df = load_excel_data(FILE_XLS)    

    df_corretivas = df[COLUNAS_EXIBICAO].copy()
    # Renomear colunas
    df_corretivas = df_corretivas.rename(columns=MAPEAMENTO_COLUNAS)
    # Coloca cor na coluna Status
    df_corretivas = df_corretivas.style.map(colorir_status, subset=["STATUS"])  
    
    # Exibir os dados em uma tabela      
    col1, col2, col3 = st.columns([1, 12, 1])  # Ajusta o tamanho das colunas
    with col2:
        # Exibir os dados em uma tabela      
        st.dataframe(
            df_corretivas ,
            height=400,
            hide_index=True       
        )