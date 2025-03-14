import pandas as pd
from pathlib import Path
from datetime import datetime
import streamlit as st

# Constantes
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
                "VALOR DE SERVIÇO", "VALOR TOTAL", "COMENTÁRIOS DA OS", "DATA DE ABERTURA", "HORA DE ABERTURA", 
                "DATA DE INÍCIO", "HORA DE INÍCIO", "DATA DE TÉRMINO", "HORA DE TÉRMINO"
            ],
            errors='ignore',
            inplace=True
        )              
        
        # Salvar o DataFrame no arquivo gerado
        metricas_df = calculo_metricas(df)
        #print("*********************")  
        #print(metricas_df[(metricas_df['Ano'] == 2025) & (metricas_df['Mês'] == 2)]['OS Abertas'].values[0])
        #print("*********************")        
        #print(metricas_df)

        # Gerar o nome do arquivo com base na data atual
        current_date = datetime.now().strftime('%Y%m%d')
        output_file_name = f'dados_{current_date}.csv'        
        df.to_csv(f'dados/{output_file_name}', index=False, encoding='utf-8')        
    except Exception as e:
        print(f"Erro ao processar o arquivo: {e}")
        return None

    return df

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

def exibir_corretivas(df):
    """
    Exibe o Dataframe de OS corretivos.
        Args:
        df (pandas.DataFrame): DataFrame com os dados para exibição.
    """    
  
    df_corretivas = df[COLUNAS_EXIBICAO].copy()
    # Garantir que as colunas de data e hora estejam no formato datetime
  
    # Renomear colunas
    df_corretivas = df_corretivas.rename(columns=MAPEAMENTO_COLUNAS)
    # Coloca cor na coluna Status
    df_corretivas = df_corretivas.style.map(colorir_status, subset=["STATUS"])  
    
    # Exibir os dados em uma tabela      
    col1, col2, col3 = st.columns([2, 12, 1])  # Ajusta o tamanho das colunas
    with col2:
        # Exibir os dados em uma tabela      
        #filtered_df = dataframe_explorer(df_corretivas, case=False)
        #st.dataframe(filtered_df, use_container_width=True, hide_index=True )        
        st.dataframe(
            df_corretivas ,
            height=400,
            hide_index=True       
        )
def calculo_metricas(df):
    """
    Calcula os totais mensais de OS abertas, não atendidas, atendidas e atendidas do backlog. 
    Args:
        df (pandas.DataFrame): DataFrame com os dados de OS.
    Returns:
        pandas.DataFrame: DataFrame com os totais mensais.
    """
    totais_mensais = []

    for ano in df['DTH_ABERTURA'].dt.year.unique():
        for mes in range(1, 13):
            df_mes_abertura = df[(df['DTH_ABERTURA'].dt.year == ano) & (df['DTH_ABERTURA'].dt.month == mes)]
            df_mes_termino = df[(df['DTH_TÉRMINO'].dt.year == ano) & (df['DTH_TÉRMINO'].dt.month == mes)]

            if df_mes_abertura.empty and df_mes_termino.empty:
                continue

            os_abertas_mes = df_mes_abertura.shape[0]
            os_n_atendidas = df_mes_abertura[df_mes_abertura['STATUS'] != 'ATENDIDO'].shape[0]
            # OS atendidas no mesmo mês de abertura
            os_atendidas = df_mes_abertura[(df_mes_abertura['STATUS'] == 'ATENDIDO') &
                                           (df_mes_abertura['DTH_TÉRMINO'].dt.year == ano) &
                                           (df_mes_abertura['DTH_TÉRMINO'].dt.month == mes)].shape[0] 


            #os_atendidas = df_mes_abertura[df_mes_abertura['STATUS'] == 'ATENDIDO'].shape[0]
            os_at_backlog = df_mes_termino[df_mes_termino['STATUS'] == 'ATENDIDO'].shape[0] 
            totais_mensais.append({
                'Ano': ano,
                'Mês': mes,
                'OS Abertas': os_abertas_mes,
                'OS Não Atendidas': os_n_atendidas,
                'OS Atendidas': os_atendidas,
                'OS Atendidas do Backlog': os_at_backlog
            })

    return pd.DataFrame(totais_mensais)
