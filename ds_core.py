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


def load_excel_corretivas(file_name: str) -> Optional[pd.DataFrame]:
    """
    Carrega e processa um arquivo Excel de ordens de serviço corretivas.
    Remove colunas desnecessárias, formata datas, calcula tempos (TMS, TMA, TEX) e salva o resultado em um arquivo CSV.

    Parâmetros:
        file_name (str): Nome do arquivo Excel.

    Retorna:
        pd.DataFrame ou None: DataFrame com os dados processados ou None em caso de erro.
    """
    # Define o caminho do arquivo
    file_path = Path('dados') / file_name

    try:
        # Ler o arquivo Excel com a linha 7 (índice 6) como cabeçalho
        xls = pd.ExcelFile(file_path)
        df = xls.parse(xls.sheet_names[0], header=6)

        # Remover a última linha e reiniciar o índice
        df = df.iloc[:-1].reset_index(drop=True)

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
        output_file_name = f'dados_{current_date}.csv'
        df.to_csv(f'dados/{output_file_name}', index=False, encoding='utf-8')

    except Exception as e:
        print(f"Erro ao processar o arquivo: {e}")
        return None

    return df

def load_excel_cortecnicos(file_name: str) -> Optional[pd.DataFrame]:
    """
    Carrega e processa um arquivo Excel dos técnico e apropriação de horas
    Remove colunas desnecessárias, formata datas, calcula tempos (TMS, TMA, TEX) e salva o resultado em um arquivo CSV.
    Parâmetros:
        file_name (str): Nome do arquivo Excel.
    Retorna:
        pd.DataFrame ou None: DataFrame com os dados processados ou None em caso de erro.
    """
    # Define o caminho do arquivo
    file_path = Path('dados') / file_name

    try:
        # Ler o arquivo Excel com a linha 7 (índice 6) como cabeçalho
        xls = pd.ExcelFile(file_path)
        df = xls.parse(xls.sheet_names[0], header=6)

        # Remover a última linha e reiniciar o índice
        df = df.iloc[:-1].reset_index(drop=True)

        # Formata datas e horas de início
        df['DATA INICIO'] = pd.to_datetime(df['DATA INICIO'], format='%d/%m/%Y')
        df['HORA INICIO'] = df['HORA INICIO'].apply(parse_time)
        df['DTH_INICIO'] = pd.to_datetime(
            df['DATA INICIO'].dt.strftime('%d/%m/%Y') + ' ' +
            df['HORA INICIO'].apply(lambda t: t.strftime('%H:%M:%S') if t else "00:00:00"),
            format='%d/%m/%Y %H:%M:%S'
        )

        # Formata datas e horas de término, se existirem
        if 'DATA DE TERMINO' in df.columns and 'HORA TERMINO' in df.columns:
            df['DATA TERMINO'] = pd.to_datetime(df['DATA DE TERMINO'], format='%d/%m/%Y', errors='coerce')
            df['HORA TERMINO'] = df['HORA TERMINO'].apply(parse_time)
            df['DTH_TERMINO'] = pd.to_datetime(
                df['DATA TERMINO'].dt.strftime('%d/%m/%Y') + ' ' +
                df['HORA TERMINO'].apply(lambda t: t.strftime('%H:%M:%S') if t else "00:00:00"),
                format='%d/%m/%Y %H:%M:%S'
            )
        else:
            df['DTH_TERMINO'] = pd.NaT

        # Remove colunas desnecessárias
        columns_to_drop = ["TIPO DE NEGÓCIO", "LOCAL", "DATA INICIO", "HORA INICIO", "DATA TERMINO", "HORA TERMINO"]
        df.drop(columns=columns_to_drop, errors='ignore', inplace=True)
        # Converte a coluna 'ID' para inteiro e depois para string
        df['ID'] = pd.to_numeric(df['ID'], errors='coerce').fillna(0).astype(int).astype(str)
        # Salva o DataFrame processado em um arquivo CSV
        current_date = datetime.now().strftime('%Y%m%d')
        output_file_name = f'tecno_dados_{current_date}.csv'
        df.to_csv(f'dados/{output_file_name}', index=False, encoding='utf-8')

    except Exception as e:
        print(f"Erro ao processar o arquivo: {e}")
        return None

    return df

# Executa a função e exibe o DataFrame resultante
df_core = load_excel_corretivas("historico_oss_corretivas.xls")
df_tecno = load_excel_cortecnicos("relatorio_historico_atendimento.xls")

print(df_core)
print(df_core.columns)
print(df_tecno)
print(df_tecno.columns)