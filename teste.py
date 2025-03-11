import streamlit as st
import pandas as pd
from utils import header_page, header_side, widget, line_space
from datasets.ds_corretivas import dados, dados_nos, qtde_os_abertas, qtde_os_atendidas, qtde_corretivas, qtde_backlog, backlog, dados_sol, dados_tec, dados_tip, dados_nat
from datetime import datetime

#import plotly.express as px
#from dataset import df
#from utils import format_number
#from graficos import grafico_map_estado, grafico_rec_mensal, grafico_rec_estado, grafico_rec_categoria, grafico_rec_vendedores, grafico_vendas_vendedores

st.set_page_config(
    page_title='Geopapp',
    page_icon="imgs/roda.png",
    initial_sidebar_state="collapsed",
    layout="wide"
)
st.logo("imgs/roda.png")

# SIDEBAR
with st.sidebar:
    #st.image("imgs/casapark.png")
    #st..header("EMConsult")
    pass

st.sidebar.markdown(header_side, unsafe_allow_html=True)
 
#Pagina HOME  

# Cabeçalho da Página
st.markdown(header_page, unsafe_allow_html=True)

#Quadros de Métricas 

w_qtde_os = widget("Quantidade de OS", str(dados_nos), " ")
w_corretivas = widget("Corretivas", str(qtde_corretivas), " ")
w_backlogs = widget("BACKLOG", str(qtde_backlog), "   ")
w_atendidas = widget("OS Atendidas", str(qtde_os_atendidas), "   ")
w_abertas = widget("OS Abertas", str(qtde_os_abertas), "   ")

a, b, c, d, e = st.columns(5)

a.markdown(w_qtde_os, unsafe_allow_html=True)
b.markdown(w_backlogs, unsafe_allow_html=True)
c.markdown(w_corretivas, unsafe_allow_html=True)
d.markdown(w_atendidas, unsafe_allow_html=True)
e.markdown(w_abertas, unsafe_allow_html=True)

#st.markdown(line_space, unsafe_allow_html=True)




colunas = ['Nº OS', 'STATUS',  'NATUREZA', 'TIPO DE OS', 'DESCRIÇÃO', 'SOLICITANTE', 'TÉCNICO', 'DTH_ABERTURA', 'DTH_INÍCIO', 'DTH_TÉRMINO']
dados = dados[colunas]
# Renomear as colunas
dados = dados.rename(columns={
    'DTH_ABERTURA': 'Data/Hora Abertura',
    'DTH_INÍCIO': 'Data/Hora Início',
    'DTH_TÉRMINO': 'Data/Hora Término'
})

# Dicionário de cores para os status
cores = {
    "ATENDIDO": "green",
    "ABERTO": "red"
}


# Função para aplicar cores na coluna STATUS
def colorir_status(value):
    return f"color: {cores.get(value, 'black')}; font-weight: bold;" if isinstance(value, str) and value in cores else ""
aba1, aba2 = st.tabs(['Corretivas', 'Agrupados'])
with aba1:
    # Exibindo o DataFrame com tooltips e cores no Streamlit
    col1, col2, col3 = st.columns([1, 12, 1])  # Ajusta o tamanho das colunas
    with col2:
        st.dataframe(
            dados.style
            .map(colorir_status, subset=["STATUS"]),  # Aplica cores
            height=400,  # Ajuste a altura conforme necessário
            hide_index=True       
        )
with aba2:
    col1, col2, col3, col4 = st.columns([1,1,1,1])
    with col1:  
        st.dataframe(dados_tec)
    with col2:  
        st.dataframe(dados_sol)    
    with col3:  
        st.dataframe(dados_tip)     
    with col4:  
        st.dataframe(dados_nat)              