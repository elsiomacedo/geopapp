import streamlit as st
from components import load_css, header_page
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Optional
import time

CORE_XLS = 'historico_oss_corretivas.xls'
TECNO_XLS = 'relatorio_historico_atendimento.xls'

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

def last_access(file_name):
    # Caminho do arquivo
    caminho_arquivo = Path('dados') / file_name     
    # Data da última modificação
    data_modificacao = time.strftime('%d/%m/%Y', time.localtime(caminho_arquivo.stat().st_mtime))
    return data_modificacao   

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
        #output_file_name = f'core_dados.csv'
        #df.to_csv(f'dados/{output_file_name}', index=False, encoding='utf-8')

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
    df['INICIO'] = pd.to_datetime(
        df['DATA INICIO'].dt.strftime('%d/%m/%Y') + ' ' +
        df['HORA INICIO'].apply(lambda t: t.strftime('%H:%M:%S') if t else "00:00:00"),
        format='%d/%m/%Y %H:%M:%S'
    )

    # Formata datas e horas de término, se existirem
    if 'DATA TERMINO' in df.columns and 'HORA TERMINO' in df.columns:
        df['DATA TERMINO'] = pd.to_datetime(df['DATA TERMINO'], format='%d/%m/%Y', errors='coerce')
        df['HORA TERMINO'] = df['HORA TERMINO'].apply(parse_time)
        df['TERMINO'] = pd.to_datetime(
            df['DATA TERMINO'].dt.strftime('%d/%m/%Y') + ' ' +
            df['HORA TERMINO'].apply(lambda t: t.strftime('%H:%M:%S') if t else "00:00:00"),
            format='%d/%m/%Y %H:%M:%S'
        )
    else:
        df['TERMINO'] = pd.NaT

    
    # Converte a coluna 'ID' para inteiro e depois para string
    df['Nº OS'] = pd.to_numeric(df['ID'], errors='coerce').fillna(0).astype(int).astype(str)    
    # Calcula o tempo de execução
    df['TEMPO EXECUCAO'] = (df['TERMINO'] - df['INICIO']).apply(lambda x: f"{int(x.total_seconds() // 3600):02}:{int((x.total_seconds() % 3600) // 60):02}" if pd.notnull(x) else None)

    df.columns = df.columns.str.strip()

    # Filtrar tecno_dados para incluir apenas OS CORRETIVA
    df_corretiva = df[df['TIPO'] == 'OS Corretiva']

    columns_to_drop = ["IS", 'TIPO',  "TIPO DE NEGÓCIO", "LOCAL", "DATA INICIO", "HORA INICIO", "DATA TERMINO", "HORA TERMINO"]

    df_corretiva = df_corretiva.drop(columns=columns_to_drop, errors='ignore')    

    COLUNAS_EXIBICAO = [
        'Nº OS', 'TECNICO', 'TIPO TECNICO', 'INICIO', 'TERMINO', 'TEMPO EXECUCAO'
    ]

    df_corretiva = df_corretiva[COLUNAS_EXIBICAO].copy()   

    # Salva o DataFrame processado em um arquivo CSV  
    #output_file_name = f'tecno_dados.csv'
    #df_corretiva.to_csv(f'dados/{output_file_name}', index=False, encoding='utf-8')
    
    return df

def Criadb(corretivas,  cortecnicos):

    # Selecionar colunas específicas de cada DataFrame
    core_cols = ['Nº OS', 'ANDAR', 'ÁREA', 'SOLICITANTE', 'DESCRIÇÃO', 'STATUS',
                    'NATUREZA', 'TIPO DE OS', 'PROBLEMA', 'TIPO DE EQUIPAMENTO',
                    'TAG EQUIPAMENTO', 'SERVIÇO EXECUTADO', 'OBSERVAÇÃO', 'PRIORIDADE', 
                    'DTH_ABERTURA', 'DTH_INICIO', 'DTH_TERMINO', 'TS', 'TA', 'TE'    
                ]
    tecno_cols = ['Nº OS', 'TECNICO', 'TIPO TECNICO', 'INICIO', 'TERMINO', 'TEMPO EXECUCAO']

    # Realizar o merge
    merged_df = pd.merge(
        corretivas[core_cols],
        cortecnicos[tecno_cols],
        on='Nº OS',
        how='left'
    )
    # Exibir o resultado

    return(merged_df)    

def gravacsv(arq_file):
    # Salva o DataFrame processado em um arquivo CSV  
    output_file_name = f'DBCorretivas.csv'
    arq_file.to_csv(f'dados/{output_file_name}', index=False, encoding='utf-8')

def geradb():
    """Carrega, normaliza e atualiza os dados dos arquivos Excel."""
    my_bar = st.progress(0, "Carregando, Analisando e Atualizando os dados. Aguarde...")

    core_data = load_excel(CORE_XLS)
    my_bar.progress(15, "Carregando OS Corretivas ............")
    df_coretivas = normalize_corretivas(core_data)    
    my_bar.progress(25, "Normalizando OS Corretivas ..........")   
    tecno_data = load_excel(TECNO_XLS)     
    my_bar.progress(40, "Carregando Dados dos Técnicos .......")   
    df_cortecnicos = normalize_cortecnicos(tecno_data)         
    my_bar.progress(60, "Normalizando Dados dos Técnicos .....")    
    my_bar.progress(75, "Construindo database ................")    
    dbarq = Criadb(df_coretivas, df_cortecnicos)    
    my_bar.progress(90, "Salvando Banco de Dados .............")    
    gravacsv(dbarq)
    my_bar.progress(100, text="Processamento Concluído")
    st.success("Dados atualizados com sucesso!")
    
    return df_coretivas,  df_cortecnicos

def atualdata(): 
    """Display the data update page with last update information and update button."""
    st.header('Atualiza dados do Sistema')

       # Display last update date
    last_update_date = last_access('DBCorretivas.csv')
    st.success(f'Data do Último Arquivo de Atualização: {last_update_date}')

    if 'clicked' not in st.session_state:
        st.session_state.clicked = False
    if 'button_state' not in st.session_state:
        st.session_state.button_state = False

    def click_button():
        st.session_state.button_state = True        
        st.session_state.clicked = True

    st.button(
        "Atualizar Dados", 
        icon=":material/sync:", 
        type="primary", 
        use_container_width=True,
        disabled= st.session_state.button_state, 
        on_click=click_button
        )

    if st.session_state.clicked:
        geradb()

if __name__ == "__page__":
    atualdata()    