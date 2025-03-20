import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Optional

def parse_time(time_str: str) -> Optional[datetime.time]:
    """
    Converte uma string de tempo no formato 'HH:MM:SS' ou 'HH:MM' para um objeto datetime.time.
    Retorna None se a string estiver vazia, for nula ou inválida.

    Parâmetros:
        time_str (str): String contendo o tempo.

    Retorna:
        datetime.time ou None: Objeto de tempo ou None em caso de erro.
    """
    if not time_str or pd.isnull(time_str):
        return None
    try:
        return pd.to_datetime(time_str, format='%H:%M:%S').time()
    except ValueError:
        try:
            return pd.to_datetime(time_str, format='%H:%M').time()
        except ValueError:
            return None

def load_excel(file_name: str) -> Optional[pd.DataFrame]:
    """
    Carrega e processa um arquivo Excel Exportado pelo OPTIMUS
    Salva o Resultado em Aqruivo CSV
       Parâmetros:
        file_name (str): Nome do arquivo Excel.
    Retorna:
        pd.DataFrame ou None: DataFrame com os dados importados  ou None em caso de erro.
    """
    # Define o caminho do arquivo
    file_path = Path('dados') / file_name

    try:
        # Ler o arquivo Excel com a linha 7 (índice 6) como cabeçalho
        xls = pd.ExcelFile(file_path)
        df = xls.parse(xls.sheet_names[0], header=6)
        # Remover a última linha e reiniciar o índice
        df = df.iloc[:-1].reset_index(drop=True)

    except Exception as e:
        print(f"Erro ao processar o arquivo: {e}")
        return None

    return df

def normalize_corretivas(df) -> Optional[pd.DataFrame]:
    """
    Carrega e processa um arquivo Excel de ordens de serviço corretivas.
    Remove colunas desnecessárias, formata datas, calcula tempos (TMS, TMA, TEX) e salva o resultado em um arquivo CSV.
    Parâmetros:
        pd.DataFrame ou None: DataFrame a ser normalizado.
    Retorna:
        pd.DataFrame ou None: DataFrame com os dados processados ou None em caso de erro.
    """
    # Formata datas e horas de abertura
    df['DATA DE ABERTURA'] = pd.to_datetime(df['DATA DE ABERTURA'], format='%d/%m/%Y')
    df['HORA DE ABERTURA'] = df['HORA DE ABERTURA'].apply(parse_time)
    df['DTH_ABERTURA'] = pd.to_datetime(
        df['DATA DE ABERTURA'].dt.strftime('%d/%m/%Y') + ' ' +
        df['HORA DE ABERTURA'].apply(lambda t: t.strftime('%H:%M:%S') if t else "00:00:00"),
        format='%d/%m/%Y %H:%M:%S'
    )

    # Formata datas e horas de início
    df['DATA DE INÍCIO'] = pd.to_datetime(df['DATA DE INÍCIO'], format='%d/%m/%Y')
    df['HORA DE INÍCIO'] = df['HORA DE INÍCIO'].apply(parse_time)
    df['DTH_INICIO'] = pd.to_datetime(
        df['DATA DE INÍCIO'].dt.strftime('%d/%m/%Y') + ' ' +
        df['HORA DE INÍCIO'].apply(lambda t: t.strftime('%H:%M:%S') if t else "00:00:00"),
        format='%d/%m/%Y %H:%M:%S'
    )

    # Formata datas e horas de término, se existirem
    if 'DATA DE TÉRMINO' in df.columns and 'HORA DE TÉRMINO' in df.columns:
        df['DATA DE TÉRMINO'] = pd.to_datetime(df['DATA DE TÉRMINO'], format='%d/%m/%Y', errors='coerce')
        df['HORA DE TÉRMINO'] = df['HORA DE TÉRMINO'].apply(parse_time)
        df['DTH_TERMINO'] = pd.to_datetime(
            df['DATA DE TÉRMINO'].dt.strftime('%d/%m/%Y') + ' ' +
            df['HORA DE TÉRMINO'].apply(lambda t: t.strftime('%H:%M:%S') if t else "00:00:00"),
            format='%d/%m/%Y %H:%M:%S'
        )
    else:
        df['DTH_TERMINO'] = pd.NaT

    # Converte a coluna 'PRIORIDADE' para inteiro
    df['PRIORIDADE'] = pd.to_numeric(df['PRIORIDADE'], errors='coerce').fillna(0).astype(int)

    # Remove colunas desnecessárias
    columns_to_drop = [
        "CLIENTE", "TIPO DE NEGÓCIO", "LOCAL", "TELEFONE", "E-MAIL", "FAMÍLIA",
        "DATA MÁXIMA ATENDIMENTO", "HORA MÁXIMA ATENDIMENTO", "DATA DE FECHAMENTO",
        "HORA DE FECHAMENTO", "TEMPO DE SERVIÇO", "NOME TÉCNICO (ASSINATURA)", "CONTRATO",
        "PRESTADOR", "EMPRESA", "NO PRAZO", "AVALIAÇÃO", "MOTIVO PENDÊNCIA", "NOTA PESQUISA",
        "COMENTÁRIO PESQUISA", "QTD REABERTURA", "VALOR DE MATERIAL", "VALOR DE DESPESAS",
        "VALOR DE SERVIÇO", "VALOR TOTAL", "COMENTÁRIOS DA OS", "DATA DE ABERTURA",
        "HORA DE ABERTURA", "DATA DE INÍCIO", "HORA DE INÍCIO", "DATA DE TÉRMINO", "HORA DE TÉRMINO"
    ]
    df.drop(columns=columns_to_drop, errors='ignore', inplace=True)

    # Calcula os tempos TMS, TMA e TEX para OS com STATUS ATENDIDO
    if 'STATUS' in df.columns:
        df['TS'] = None
        df['TA'] = None
        df['TE'] = None

        df_atendido = df[df['STATUS'] == 'ATENDIDO']
        df_atendido.loc[:, 'TS'] = (df_atendido['DTH_TERMINO'] - df_atendido['DTH_ABERTURA']).apply(lambda x: f"{int(x.total_seconds() // 3600):03}:{int((x.total_seconds() % 3600) // 60):02}" if pd.notnull(x) else None)
        df_atendido.loc[:, 'TA'] = (df_atendido['DTH_INICIO'] - df_atendido['DTH_ABERTURA']).apply(lambda x: f"{int(x.total_seconds() // 3600):03}:{int((x.total_seconds() % 3600) // 60):02}" if pd.notnull(x) else None)
        df_atendido.loc[:, 'TE'] = (df_atendido['DTH_TERMINO'] - df_atendido['DTH_INICIO']).apply(lambda x: f"{int(x.total_seconds() // 3600):03}:{int((x.total_seconds() % 3600) // 60):02}" if pd.notnull(x) else None)
        # Filtra apenas as OS com STATUS ATENDIDO

        # Atualiza o DataFrame original com os tempos calculados
        df.update(df_atendido)
         # Salva o DataFrame processado em um arquivo CSV
        current_date = datetime.now().strftime('%Y%m%d')
        output_file_name = f'core_dados_{current_date}.csv'
        df.to_csv(f'dados/{output_file_name}', index=False, encoding='utf-8')

    return df

def normalize_cortecnicos(df) -> Optional[pd.DataFrame]:
    """
    Carrega e processa um arquivo Excel dos técnico e apropriação de horas
    Remove colunas desnecessárias, formata datas, calcula tempos (TMS, TMA, TEX) e salva o resultado em um arquivo CSV.
    Parâmetros:
        pd.DataFrame ou None: DataFrame a ser normalizado.
    Retorna:
        pd.DataFrame ou None: DataFrame com os dados processados ou None em caso de erro.
    """
    # Formata datas e horas de início
    df['DATA INICIO'] = pd.to_datetime(df['DATA INICIO'], format='%d/%m/%Y')
    df['HORA INICIO'] = df['HORA INICIO'].apply(parse_time)
    df['DTH_INICIO'] = pd.to_datetime(
        df['DATA INICIO'].dt.strftime('%d/%m/%Y') + ' ' +
        df['HORA INICIO'].apply(lambda t: t.strftime('%H:%M:%S') if t else "00:00:00"),
        format='%d/%m/%Y %H:%M:%S'
    )

    # Formata datas e horas de término, se existirem
    if 'DATA TERMINO' in df.columns and 'HORA TERMINO' in df.columns:
        df['DATA TERMINO'] = pd.to_datetime(df['DATA TERMINO'], format='%d/%m/%Y', errors='coerce')
        df['HORA TERMINO'] = df['HORA TERMINO'].apply(parse_time)
        df['DTH_TERMINO'] = pd.to_datetime(
            df['DATA TERMINO'].dt.strftime('%d/%m/%Y') + ' ' +
            df['HORA TERMINO'].apply(lambda t: t.strftime('%H:%M:%S') if t else "00:00:00"),
            format='%d/%m/%Y %H:%M:%S'
        )
    else:
        df['DTH_TERMINO'] = pd.NaT

    
    # Converte a coluna 'ID' para inteiro e depois para string
    df['N° OS'] = pd.to_numeric(df['ID'], errors='coerce').fillna(0).astype(int).astype(str)    
    # Calcula o tempo de execução
    df['TEMPO EXECUCAO'] = (df['DTH_TERMINO'] - df['DTH_INICIO']).apply(lambda x: f"{int(x.total_seconds() // 3600):02}:{int((x.total_seconds() % 3600) // 60):02}" if pd.notnull(x) else None)
    # Remove colunas desnecessárias
    columns_to_drop = ["IS", "TIPO DE NEGÓCIO", "LOCAL", "DATA INICIO", "HORA INICIO", "DATA TERMINO", "HORA TERMINO"]
    df.drop(columns=columns_to_drop, errors='ignore', inplace=True)
    COLUNAS_EXIBICAO = [
        'N° OS', 'TIPO', 'TECNICO', 'TIPO TECNICO','ANDAR', 'ÁREA','EQUIPAMENTO', 'DTH_INICIO', 'DTH_TERMINO', 'TEMPO EXECUCAO'
    ]

    df = df[COLUNAS_EXIBICAO].copy()   

    # Salva o DataFrame processado em um arquivo CSV
    current_date = datetime.now().strftime('%Y%m%d')
    output_file_name = f'tecno_dados_{current_date}.csv'
    df.to_csv(f'dados/{output_file_name}', index=False, encoding='utf-8')
    print(df)
    return df

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
    
    st.dataframe(df_corretivas, height=400, hide_index=True)

    return

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