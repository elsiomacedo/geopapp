import streamlit as st
import pandas as pd
from pathlib import Path
from typing import Optional
from datetime import datetime
import time
from components import titulo_page
from metricas import metricascorretivas

CORE_XLS = 'historico_oss_corretivas.xls'
TECNO_XLS = 'relatorio_historico_atendimento.xls'

def parse_time(time_str: str) -> Optional[datetime.time]:
    """Converte string de hora em datetime.time."""
    if not time_str or pd.isnull(time_str):
        return None
    for fmt in ('%H:%M:%S', '%H:%M'):
        try:
            return pd.to_datetime(time_str, format=fmt).time()
        except ValueError:
            continue
    return None

def last_access(file_name: str) -> str:
    """Retorna a data da última modificação de um arquivo."""
    caminho_arquivo = Path('dados') / file_name
    return time.strftime('%d/%m/%Y', time.localtime(caminho_arquivo.stat().st_mtime))

def combinar_data_hora(data_col, hora_col) -> pd.Series:
    return pd.to_datetime(
        data_col.dt.strftime('%d/%m/%Y') + ' ' +
        hora_col.apply(lambda t: t.strftime('%H:%M:%S') if t else "00:00:00"),
        format='%d/%m/%Y %H:%M:%S'
    )

def calcular_tempo(delta) -> Optional[str]:
    if not isinstance(delta, pd.Timedelta) or pd.isnull(delta):
        return None
    total_seconds = delta.total_seconds()
    horas = int(total_seconds // 3600)
    minutos = int((total_seconds % 3600) // 60)
    return f"{horas:03}:{minutos:02}"

def load_excel(file_name: str) -> Optional[pd.DataFrame]:
    """Lê planilha Excel exportada do OPTIMUS."""
    file_path = Path('dados') / file_name
    try:
        xls = pd.ExcelFile(file_path)
        df = xls.parse(xls.sheet_names[0], header=6)
        return df.iloc[:-1].reset_index(drop=True)
    except Exception as e:
        st.error(f"Erro ao processar o arquivo '{file_name}': {e}")
        return None

def normalizar_datas(df: pd.DataFrame, col_data: str, col_hora: str, col_destino: str):
    df[col_data] = pd.to_datetime(df[col_data], format='%d/%m/%Y', errors='coerce')
    df[col_hora] = df[col_hora].apply(parse_time)
    df[col_destino] = combinar_data_hora(df[col_data], df[col_hora])

def normalize_corretivas(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    """Normaliza e processa dados de OS corretivas."""
    normalizar_datas(df, 'DATA DE ABERTURA', 'HORA DE ABERTURA', 'DTH_ABERTURA')
    normalizar_datas(df, 'DATA DE INÍCIO', 'HORA DE INÍCIO', 'DTH_INICIO')

    if 'DATA DE TÉRMINO' in df.columns and 'HORA DE TÉRMINO' in df.columns:
        normalizar_datas(df, 'DATA DE TÉRMINO', 'HORA DE TÉRMINO', 'DTH_TERMINO')
    else:
        df['DTH_TERMINO'] = pd.NaT

    df['PRIORIDADE'] = pd.to_numeric(df['PRIORIDADE'], errors='coerce').fillna(0).astype(int)

    df.drop(columns=[
        "CLIENTE", "TIPO DE NEGÓCIO", "LOCAL", "TELEFONE", "E-MAIL", "FAMÍLIA",
        "DATA MÁXIMA ATENDIMENTO", "HORA MÁXIMA ATENDIMENTO", "DATA DE FECHAMENTO",
        "HORA DE FECHAMENTO", "TEMPO DE SERVIÇO", "NOME TÉCNICO (ASSINATURA)", "CONTRATO",
        "PRESTADOR", "EMPRESA", "NO PRAZO", "AVALIAÇÃO", "MOTIVO PENDÊNCIA", "NOTA PESQUISA",
        "COMENTÁRIO PESQUISA", "QTD REABERTURA", "VALOR DE MATERIAL", "VALOR DE DESPESAS",
        "VALOR DE SERVIÇO", "VALOR TOTAL", "COMENTÁRIOS DA OS",
        "DATA DE ABERTURA", "HORA DE ABERTURA", "DATA DE INÍCIO", "HORA DE INÍCIO",
        "DATA DE TÉRMINO", "HORA DE TÉRMINO"
    ], errors='ignore', inplace=True)

    if 'STATUS' in df.columns:
        df['TS'] = df['TA'] = df['TE'] = None
        atendido = df['STATUS'] == 'ATENDIDO'
        df.loc[atendido, 'TS'] = (df.loc[atendido, 'DTH_TERMINO'] - df.loc[atendido, 'DTH_ABERTURA']).apply(calcular_tempo)
        df.loc[atendido, 'TA'] = (df.loc[atendido, 'DTH_INICIO'] - df.loc[atendido, 'DTH_ABERTURA']).apply(calcular_tempo)
        df.loc[atendido, 'TE'] = (df.loc[atendido, 'DTH_TERMINO'] - df.loc[atendido, 'DTH_INICIO']).apply(calcular_tempo)

    return df

def normalize_cortecnicos(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    """Normaliza dados de técnicos e calcula tempo de execução."""
    normalizar_datas(df, 'DATA INICIO', 'HORA INICIO', 'INICIO')

    if 'DATA TERMINO' in df.columns and 'HORA TERMINO' in df.columns:
        normalizar_datas(df, 'DATA TERMINO', 'HORA TERMINO', 'TERMINO')
    else:
        df['TERMINO'] = pd.NaT

    df['Nº OS'] = pd.to_numeric(df['ID'], errors='coerce').fillna(0).astype(int).astype(str)
    df['TEMPO EXECUCAO'] = (df['TERMINO'] - df['INICIO']).apply(calcular_tempo)
    df.columns = df.columns.str.strip()
    #df = df[df['TIPO'] == 'OS Corretiva']

    drop_cols = ["IS", "TIPO DE NEGÓCIO", "LOCAL", "DATA INICIO", "HORA INICIO", "DATA TERMINO", "HORA TERMINO"]
    df.drop(columns=drop_cols, errors='ignore', inplace=True)
    df.rename(columns={
            'TIPO TECNICO': 'EQUIPE',
            'DTH_ABERTURA': 'Data/Hora Abertura',
            'INICIO': 'Início',
            'TERMINO': 'Término',
            'TEMPO EXECUCAO': 'Tempo'
        }, inplace=True)    

    COLUNAS_EXIBICAO = [
        'TECNICO', 'EQUIPE', 'TIPO', 'Nº OS', 'Início', 'Término','Tempo'
        ]

    df = df.reindex(columns=COLUNAS_EXIBICAO)
    return df.copy()

def db_corretivas_all(corretivas: pd.DataFrame, cortecnicos: pd.DataFrame) -> pd.DataFrame:
    core_cols = [
        'Nº OS', 'ANDAR', 'ÁREA', 'SOLICITANTE', 'DESCRIÇÃO', 'STATUS', 'NATUREZA',
        'TIPO DE OS', 'PROBLEMA', 'TIPO DE EQUIPAMENTO', 'TAG EQUIPAMENTO',
        'SERVIÇO EXECUTADO', 'OBSERVAÇÃO', 'PRIORIDADE', 'DTH_ABERTURA', 'DTH_INICIO',
        'DTH_TERMINO', 'TS', 'TA', 'TE'
    ]

    cortecnicos = cortecnicos[cortecnicos['TIPO'] == 'OS Corretiva']    
    tecno_cols = ['TECNICO', 'EQUIPE', 'TIPO', 'Nº OS', 'Início', 'Término','Tempo']
    return pd.merge(corretivas[core_cols], cortecnicos[tecno_cols], on='Nº OS', how='left')

def agrupa_db(corretivas_all: pd.DataFrame) -> pd.DataFrame:
    
    agrupado = corretivas_all.groupby('Nº OS').agg({
        'STATUS': 'first',
        'ANDAR': 'first',
        'ÁREA': 'first',
        'PROBLEMA': 'first',
        'OBSERVAÇÃO': 'first',
        'TIPO DE OS': 'first',
        'NATUREZA': 'first',
        'SOLICITANTE': 'first',
        'DESCRIÇÃO': 'first',
        'TIPO DE EQUIPAMENTO': 'first',
        'TAG EQUIPAMENTO': 'first',
        'SERVIÇO EXECUTADO': 'first',        
        'TECNICO': lambda x: ', '.join(str(t) for t in x.dropna().unique()),
        'EQUIPE': 'first',
        'TIPO': 'first',
        'DTH_ABERTURA': 'first',
        'DTH_INICIO': 'first',
        'DTH_TERMINO': 'first',
        'TA': 'first',
        'TS': 'first',
        'TE': 'first'
    }).reset_index()

    agrupado['QTD_TECNICOS'] = corretivas_all.groupby('Nº OS')['TECNICO'].nunique().values
    agrupado.rename(columns={
        'TIPO TECNICO': 'EQUIPE',
        'DTH_ABERTURA': 'Data/Hora Abertura',
        'DTH_INICIO': 'Data/Hora Início',
        'DTH_TERMINO': 'Data/Hora Término',
        'TA': 'Atendimento',
        'TS': 'Solução',
        'TE': 'Execução'
    }, inplace=True)

    colunas = [
        'Nº OS', 'STATUS', 'ANDAR', 'ÁREA', 'TIPO DE OS', 'NATUREZA', 'SOLICITANTE', 'DESCRIÇÃO','SERVIÇO EXECUTADO',
        'QTD_TECNICOS', 'TECNICO', 'EQUIPE', 'Data/Hora Abertura', 'Data/Hora Início',
        'Data/Hora Término', 'Atendimento', 'Solução', 'Execução', 'TEMPO EXECUCAO'
    ]
    return agrupado.reindex(columns=colunas)


def gravacsv(df: pd.DataFrame, output_file_name: str):
    df.to_csv(f'dados/{output_file_name}', index=False, encoding='utf-8')

def gerar_bases():
    """Executa o pipeline completo de leitura, normalização e exportação de dados."""
    my_bar = st.progress(0, "Carregando, analisando e atualizando os dados. Aguarde...")

    my_bar.progress(10, "Carregando OS Corretivas........")
    corretivas = normalize_corretivas(load_excel(CORE_XLS))

    my_bar.progress(30, "Carregando dados dos técnicos...")
    tecnicos = normalize_cortecnicos(load_excel(TECNO_XLS))

    my_bar.progress(50, "Agrupando base completa...")
    base_completa = db_corretivas_all(corretivas, tecnicos)

    my_bar.progress(65, "Gerando base de exibição...")
    db_corretivas = agrupa_db(base_completa)

    my_bar.progress(75, "Gerando base por técnico...")
    db_tecnicos = gerar_base_tecnicos(base_completa)

    my_bar.progress(85, "Salvando arquivos CSV...")
    gravacsv(db_corretivas, 'DBCorretivas.csv')    
    #gravacsv(base_mes, 'DBCor_Mes.csv')
    #gravacsv(tecnicos, 'DBTecno_All.csv')
    
    my_bar.progress(90, "Salvando arquivos CSV...")    
    gravacsv(tecnicos, 'DBTecno_All.csv')

    my_bar.progress(100, "Processamento concluído.")
    st.success("Dados atualizados com sucesso!")

def gerar_base_resumo(df: pd.DataFrame) -> pd.DataFrame:
    """Gera DataFrame de OS com agrupamento e resumo por mês."""
    hoje = datetime.now()
    df['Data/Hora Abertura'] = pd.to_datetime(df['Data/Hora Abertura'], errors='coerce')
    df['Data/Hora Término'] = pd.to_datetime(df['Data/Hora Término'], errors='coerce')

    filtro = (
        (df['Data/Hora Abertura'].dt.month == hoje.month) & (df['Data/Hora Abertura'].dt.year == hoje.year)
        | (df['Data/Hora Término'].dt.month == hoje.month) & (df['Data/Hora Término'].dt.year == hoje.year)
        | (df['STATUS'] != 'ATENDIDO') & (df['STATUS'] != 'CANCELADO')
    )
 
    df_filtrado = df[filtro]

    colunas = [
        'Nº OS', 'ANDAR', 'ÁREA','STATUS', 'TIPO DE OS', 'NATUREZA', 'SOLICITANTE', 'DESCRIÇÃO',
        'QTD_TECNICOS', 'TECNICO', 'EQUIPE', 'Data/Hora Abertura', 'Data/Hora Início',
        'Data/Hora Término', 'Atendimento', 'Solução', 'Execução', 'TEMPO EXECUCAO'
    ]
    return df_filtrado.reindex(columns=colunas)

def gerar_base_tecnicos(df: pd.DataFrame) -> pd.DataFrame:
    """Gera base agrupada por técnico com OS atendidas."""
    df_filtrado = df[df['STATUS'] == 'ATENDIDO']
    df_filtrado = df_filtrado.rename(columns={
        'TIPO TECNICO': 'EQUIPE',
        'DTH_ABERTURA': 'Data/Hora Abertura',
        'TA': 'Atendimento',
        'TS': 'Solução',
        'TE': 'Execução'
    })
    colunas = [
        'TECNICO', 'EQUIPE', 'TIPO', 'Nº OS', 'TIPO DE OS', 'NATUREZA', 'SOLICITANTE', 'DESCRIÇÃO',
        'Data/Hora Abertura', 'INICIO', 'TERMINO', 'Atendimento', 'Solução', 'Execução', 'Execução'
    ]
    return df_filtrado.reindex(columns=colunas).sort_values(by='TECNICO')

def atualdata():
    """Interface do botão de atualização com data da última execução."""
    st.markdown(titulo_page('Atualiza dados do Sistema',
                            f'Data do Último Arquivo de Atualização: {last_access("DBCorretivas.csv")}'),
                unsafe_allow_html=True)

    if 'clicked' not in st.session_state:
        st.session_state.clicked = False
    if 'button_state' not in st.session_state:
        st.session_state.button_state = False

    def click_button():
        st.session_state.button_state = True
        st.session_state.clicked = True

    st.button("Atualizar Dados", icon=":material/sync:", type="primary",
              use_container_width=True, disabled=st.session_state.button_state,
              on_click=click_button)

    if st.session_state.clicked:
        gerar_bases()

if __name__ == "__page__":
    atualdata()