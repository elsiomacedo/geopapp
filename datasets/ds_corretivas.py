#import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Optional
import time

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

def exibir_corretivas(df):
    """
    Exibe o Dataframe de OS corretivos.
        Args:
        df (pandas.DataFrame): DataFrame com os dados para exibição.
    """    
    COLUNAS_EXIBICAO = [
        'Nº OS', 'STATUS', 'TIPO DE OS','NATUREZA',  
        'SOLICITANTE', 'DESCRIÇÃO', 'TÉCNICO', 'TIPO TÉCNICO', 'DTH_ABERTURA', 'DTH_INICIO', 'DTH_TERMINO'
    ]
    MAPEAMENTO_COLUNAS = {
        'TIPO TÉCNICO' : 'EQUIPE',
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

def metricas_core(df):
    """
    Calcula os totais mensais de OS abertas, não atendidas, atendidas, backlogs atendidos e backlog acumulado.
    Args:
        df (pandas.DataFrame): DataFrame com os dados de OS.  
    Returns:
        pandas.DataFrame: DataFrame com os totais mensais.
    """
    totais_mensais = []

    # Garantir que as colunas de data estão no formato datetime
    df['DTH_ABERTURA'] = pd.to_datetime(df['DTH_ABERTURA'])
    df['DTH_TERMINO'] = pd.to_datetime(df['DTH_TERMINO'])

    # Ordenar DataFrame por data de abertura (garante a correta acumulação do backlog)
    df = df.sort_values('DTH_ABERTURA')

    for ano in df['DTH_ABERTURA'].dt.year.unique():
        for mes in range(1, 13):
            # Filtros para o mês atual
            df_mes_abertura = df[(df['DTH_ABERTURA'].dt.year == ano) & (df['DTH_ABERTURA'].dt.month == mes)]
            df_mes_termino = df[(df['DTH_TÉRMINO'].dt.year == ano) & (df['DTH_TÉRMINO'].dt.month == mes)]

            # Se não houver registros no mês, pule a iteração
            if df_mes_abertura.empty and df_mes_termino.empty:
                continue

            # Quantidade de OS abertas no mês
            os_abertas_mes = df_mes_abertura.shape[0]

            # OS não atendidas no mês (abertas no mês e não concluídas)
            os_n_atendidas = df_mes_abertura[df_mes_abertura['STATUS'] != 'ATENDIDO'].shape[0]

            # OS atendidas no mês (abertas e finalizadas no mesmo mês)
            os_atendidas = df_mes_abertura[(df_mes_abertura['STATUS'] == 'ATENDIDO') &
                                           (df_mes_abertura['DTH_TÉRMINO'].dt.year == ano) &
                                           (df_mes_abertura['DTH_TÉRMINO'].dt.month == mes)].shape[0]

            # OS do backlog atendidas no mês (abertas em meses anteriores e concluídas neste mês)
            os_at_backlog = df_mes_termino[(df_mes_termino['STATUS'] == 'ATENDIDO') &
                                           ((df_mes_termino['DTH_ABERTURA'].dt.year < ano) |
                                            ((df_mes_termino['DTH_ABERTURA'].dt.year == ano) &
                                             (df_mes_termino['DTH_ABERTURA'].dt.month < mes)))].shape[0]

            # Calcular o Backlog (OS não atendidas com abertura anterior ao mês atual)
            backlog = df[(df['STATUS'] != 'ATENDIDO') &
                         ((df['DTH_ABERTURA'].dt.year < ano) |
                          ((df['DTH_ABERTURA'].dt.year == ano) & (df['DTH_ABERTURA'].dt.month < mes)))].shape[0]

            # Armazenar os resultados
            totais_mensais.append({
                'Referência': f"{ano}-{mes:02d}",  # Formato "YYYY-MM"                
                'Backlogs': backlog,                
                'OS Abertas': os_abertas_mes,
                'OS Não Atendidas': os_n_atendidas,
                'OS Atendidas': os_atendidas,
                'Backlogs Atendidos': os_at_backlog,

            })

    return pd.DataFrame(totais_mensais)


"""
# Executa a função e exibe o DataFrame resultante
df_core = load_excel("historico_oss_corretivas.xls")
df_tecno = load_excel_cortecnicos("relatorio_historico_atendimento.xls")

print(df_core)
print(df_core.columns)
print(df_tecno)
print(df_tecno.columns)"
"""