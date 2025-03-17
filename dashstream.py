import pandas as pd
import streamlit as st
import plotly.express as px

# Configuração da página
st.set_page_config(page_title="Dashboard de Gestão de OS", layout="wide")

# Título do dashboard
st.title("Dashboard de Gestão de Ordens de Serviço")

# Carregar os dados do arquivo CSV
@st.cache_data  # Cache para melhorar o desempenho
def load_data():
    df = pd.read_csv('dados.csv', sep=';')
    # Converter colunas de data para o formato datetime
    df['DTH_ABERTURA'] = pd.to_datetime(df['DTH_ABERTURA'], format='%d/%m/%Y %H:%M')
    df['DTH_TÉRMINO'] = pd.to_datetime(df['DTH_TÉRMINO'], format='%d/%m/%Y %H:%M')
    # Calcular o tempo de atendimento
    df['TEMPO_ATENDIMENTO'] = (df['DTH_TÉRMINO'] - df['DTH_ABERTURA']).dt.total_seconds() / 3600  # em horas
    return df

df = load_data()

# Sidebar para filtros
st.sidebar.header("Filtros")
area_selecionada = st.sidebar.selectbox("Selecione a Área/Andar", df['ÁREA'].unique())
prioridade_selecionada = st.sidebar.selectbox("Selecione a Prioridade", df['PRIORIDADE'].unique())

# Filtrar os dados com base nas seleções
df_filtrado = df[(df['ÁREA'] == area_selecionada) & (df['PRIORIDADE'] == prioridade_selecionada)]
df_filtrado = df
col1, col2, col3= st.columns(3)
# Gráfico 1: Distribuição de OS por Tipo de Problema
with col1:
   st.subheader("OS x Tipo de Problema")
    # Criar DataFrame com contagem de OS por tipo de problema
   df_tipo_problema = df_filtrado['TIPO DE OS'].value_counts().reset_index()
    # Renomear as colunas corretamente
   df_tipo_problema.columns = ['Tipo de Problema', 'Número de OS']
    # Criar o gráfico de barras
   fig1 = px.bar(df_tipo_problema, 
                x='Tipo de Problema', y='Número de OS', 
                labels={'Tipo de Problema': 'Tipo de Problema', 'Número de OS': 'Número de OS'})
   st.plotly_chart(fig1, use_container_width=True)
with col2:
    # Gráfico 2: Tempo Médio de Atendimento por Prioridade
    st.subheader("TMA x Prioridade")
    tempo_medio = df_filtrado.groupby('PRIORIDADE')['TEMPO_ATENDIMENTO'].mean().reset_index()
    fig2 = px.bar(tempo_medio, 
                x='PRIORIDADE', y='TEMPO_ATENDIMENTO', 
                labels={'PRIORIDADE': 'Prioridade', 'TEMPO_ATENDIMENTO': 'Tempo Médio (horas)'})
    st.plotly_chart(fig2, use_container_width=True)
with col1:
# Gráfico 3: Taxa de Conclusão de OS
    st.subheader("Taxa de Conclusão")
    taxa_conclusao = df_filtrado['STATUS'].value_counts(normalize=True).reset_index()
    # Renomear as colunas corretamente
    taxa_conclusao.columns = ['Status', 'Proporção']
    fig3 = px.pie(taxa_conclusao, 
                values='Proporção', names='Status')
    st.plotly_chart(fig3, use_container_width=True)
with col3:
    # Gráfico 4: Distribuição de OS por Área/Andar
    st.subheader("OS x Local")
    df_area = df_filtrado['ÁREA'].value_counts().reset_index()
    # Renomear as colunas corretamente
    df_area.columns = ['Área/Andar', 'Número de OS']
    fig4 = px.bar(df_area, 
                x='Área/Andar', y='Número de OS', 
                labels={'Área/Andar': 'Área/Andar', 'Número de OS': 'Número de OS'})
    st.plotly_chart(fig4, use_container_width=True)

# Tabela de OS Pendentes
st.subheader("OS Pendentes x Andamento")
os_pendentes = df_filtrado[df_filtrado['STATUS'].isin(['PENDENTE', 'EM ANDAMENTO', 'ABERT0','RECEBIDO','DESPACHADO' ])]
st.dataframe(os_pendentes[['Nº OS', 'ÁREA', 'STATUS','DESCRIÇÃO', 'PRIORIDADE', 'DTH_ABERTURA']])