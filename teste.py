import streamlit as st
import pandas as pd
import os

# Carregar os arquivos CSV com encoding correto
core_dados = pd.read_csv('./dados/core_dados.csv', encoding='utf-8')
tecno_dados = pd.read_csv('./dados/tecno_dados.csv', encoding='utf-8')

# Remover espaços em branco e caracteres invisíveis dos nomes das colunas
core_dados.columns = core_dados.columns.str.strip()
tecno_dados.columns = tecno_dados.columns.str.strip()

# Filtrar tecno_dados para incluir apenas OS CORRETIVA
tecno_dados_corretiva = tecno_dados[tecno_dados['TIPO'] == 'OS Corretiva']
#print(core_dados.columns)
#print(tecno_dados)

#print("Valores únicos de 'N° OS' em core_dados:", core_dados['Nº OS'].unique())
#print("Valores únicos de 'N° OS' em tecno_dados_corretiva:", tecno_dados_corretiva['Nº OS'].unique())

# Selecionar colunas específicas de cada DataFrame
core_cols = ['Nº OS', 'ANDAR', 'ÁREA', 'SOLICITANTE', 'DESCRIÇÃO', 'STATUS',
                'NATUREZA', 'TIPO DE OS', 'PROBLEMA', 'TIPO DE EQUIPAMENTO',
                'TAG EQUIPAMENTO', 'SERVIÇO EXECUTADO', 'OBSERVAÇÃO', 'PRIORIDADE', 
                'DTH_ABERTURA', 'DTH_INICIO', 'DTH_TERMINO', 'TS', 'TA', 'TE'    
            ]
tecno_cols = ['Nº OS', 'TECNICO', 'TIPO TECNICO']

# Realizar o merge
merged_df = pd.merge(
    core_dados[core_cols],
    tecno_dados_corretiva[tecno_cols],
    on='Nº OS',
    how='left'
)
# Exibir o resultado
print(merged_df.columns)

print(merged_df)