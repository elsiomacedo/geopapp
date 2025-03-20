import pandas as pd
from pathlib import Path
from datetime import datetime
import streamlit as st


def calculo_metricas(df):
    """
    Calcula os totais mensais de OS abertas, não atendidas, atendidas, backlogs atendidos e backlog acumulado.

    Args:
        df (pandas.DataFrame): DataFrame com os dados de OS.
    
    Returns:
        pandas.DataFrame: DataFrame com os totais mensais.
    """
    totais_mensais = []

    # Garantir que as colunas de data estão no formato datetime
    df['DTH_ABERTURA'] = pd.to_datetime(df['DTH_ABERTURA'], format='%d-%m-%Y %H:%M:%S')
    df['DTH_TÉRMINO'] = pd.to_datetime(df['DTH_TÉRMINO'], format='%d-%m-%Y %H:%M:%S')

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
