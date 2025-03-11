import streamlit as st
import pandas as pd
from pathlib import Path

def parse_time(time_str):
    if not time_str or pd.isnull(time_str):
        return None
    try:
        return pd.to_datetime(time_str, format='%H:%M:%S').time()
    except Exception:
        try:
            return pd.to_datetime(time_str, format='%H:%M').time()
        except Exception:
            return None
#@st.cache_data
#@st.cache_resource

def load_excel_data(file_name: str):
    """
    Carrega a primeira planilha de um arquivo Excel localizado na pasta 'dados'.
    Considera a linha 7 como cabeçalho com os nomes das colunas e remove a última linha.
    
    Parâmetros:
      file_name (str): Nome do arquivo Excel.
    
    Retorna:
      DataFrame com os dados processados ou None se ocorrer um erro.
    """
 

    file_path = Path('dados') / file_name

    try:
        # Ler o arquivo Excel com a linha 7 (índice 6) como cabeçalho
        xls = pd.ExcelFile(file_path)
        df = xls.parse(xls.sheet_names[0], header=6)
        # Remover a última linha e reiniciar o índice
        df = df.iloc[:-1].reset_index(drop=True)
        # Remover colunas indesejadas

        # Formata datas para DATETIME e cria colunas com nomenclatura com underscore
        df['DATA DE ABERTURA'] = pd.to_datetime(df['DATA DE ABERTURA'], format='%d/%m/%Y')
        df['HORA DE ABERTURA'] = df['HORA DE ABERTURA'].apply(parse_time)
        df['DTH_ABERTURA'] = pd.to_datetime(
            df['DATA DE ABERTURA'].dt.strftime('%d/%m/%Y') + ' ' +
            df['HORA DE ABERTURA'].apply(lambda t: t.strftime('%H:%M:%S') if (t is not None and t is not pd.NaT) else "00:00:00"),
            format='%d/%m/%Y %H:%M:%S'
        )

        df['DATA DE INÍCIO'] = pd.to_datetime(df['DATA DE INÍCIO'], format='%d/%m/%Y')
        df['HORA DE INÍCIO'] = df['HORA DE INÍCIO'].apply(parse_time)
        df['DTH_INICIO'] = pd.to_datetime(
            df['DATA DE INÍCIO'].dt.strftime('%d/%m/%Y') + ' ' +
            df['HORA DE INÍCIO'].apply(lambda t: t.strftime('%H:%M:%S') if (t is not None and t is not pd.NaT) else "00:00:00"),
            format='%d/%m/%Y %H:%M:%S'
        )
        # Processa data e hora de término, se existirem; senão, cria coluna com NaT
        if 'DATA DE TÉRMINO' in df.columns and 'HORA DE TÉRMINO' in df.columns:
            df['DATA DE TÉRMINO'] = pd.to_datetime(df['DATA DE TÉRMINO'], format='%d/%m/%Y', errors='coerce')
            df['HORA DE TÉRMINO'] = df['HORA DE TÉRMINO'].apply(parse_time)
            df['DTH_TÉRMINO'] = pd.to_datetime(
                df['DATA DE TÉRMINO'].dt.strftime('%d/%m/%Y') + ' ' +
                df['HORA DE TÉRMINO'].apply(lambda t: t.strftime('%H:%M:%S') if (t is not None and t is not pd.NaT) else "00:00:00"),
                format='%d/%m/%Y %H:%M:%S'
            )                 
        else:
            df['DTH_TÉRMINO'] = pd.NaT
        df.drop(
            columns=[
                "CLIENTE", "TIPO DE NEGÓCIO", "LOCAL", "TELEFONE", "E-MAIL", "FAMÍLIA",
                "DATA MÁXIMA ATENDIMENTO", "HORA MÁXIMA ATENDIMENTO", "DATA DE FECHAMENTO",
                "HORA DE FECHAMENTO", "TEMPO DE SERVIÇO", "NOME TÉCNICO (ASSINATURA)", "CONTRATO",
                "PRESTADOR", "EMPRESA", "NO PRAZO", "AVALIAÇÃO", "MOTIVO PENDÊNCIA", "NOTA PESQUISA",
                "COMENTÁRIO PESQUISA", "QTD REABERTURA", "VALOR DE MATERIAL", "VALOR DE DESPESAS",
                "VALOR DE SERVIÇO", "VALOR TOTAL", "COMENTÁRIOS DA OS","HORA DE ABERTURA", 
                "DATA DE INÍCIO", "HORA DE INÍCIO", "DATA DE TÉRMINO", "HORA DE TÉRMINO"
            ],
            errors='ignore',
            inplace=True
        )                 
        print(df.columns)
    except Exception as e:
        print(f"Erro ao processar o arquivo: {e}")
        return None

    return df
