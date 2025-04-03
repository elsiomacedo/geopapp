import pandas as pd
#from datetime import datetime

def metricascorretivas(df):

    # Conversão de datas
    df["Data/Hora Abertura"] = pd.to_datetime(df["Data/Hora Abertura"], errors='coerce')
    df["Data/Hora Início"] = pd.to_datetime(df["Data/Hora Início"], errors='coerce')
    df["Data/Hora Término"] = pd.to_datetime(df["Data/Hora Término"], errors='coerce')

    # Criar lista de meses únicos no dataset no formato aaaa/mm
    df["Mês Referência"] = df["Data/Hora Abertura"].dt.to_period("M").dt.strftime("%Y/%m").sort_values()
    meses = df["Mês Referência"].dropna().unique()

    # Lista para guardar os resultados
    resultados = []

    for mes in meses:
        inicio = pd.Timestamp(mes + "-01")
        fim = inicio + pd.offsets.MonthEnd(0)

        # Filtrar OS do mês atual
        df_mes = df[(df["Data/Hora Abertura"] >= inicio) & (df["Data/Hora Abertura"] <= fim)]

        os_abertas = len(df_mes)
        os_atendidas = df_mes["Data/Hora Término"].notna().sum()
        os_nao_atendidas = os_abertas - os_atendidas

        # Backlogs abertos antes do mês e não atendidos
        backlog = df[(df["Data/Hora Abertura"] < inicio) & (df["Data/Hora Término"].isna())].shape[0]

        # Backlogs atendidos no mês
        backlog_atendidos = df[(df["Data/Hora Abertura"] < inicio) &
                               (df["Data/Hora Término"] >= inicio) &
                               (df["Data/Hora Término"] <= fim)].shape[0]

        # Tempos
        df_exec = df_mes[df_mes["Data/Hora Início"].notna() & df_mes["Data/Hora Término"].notna()].copy()
        df_exec["TME (h)"] = (df_exec["Data/Hora Término"] - df_exec["Data/Hora Início"]).dt.total_seconds() / 3600
        df_exec["TMA (h)"] = (df_exec["Data/Hora Início"] - df_exec["Data/Hora Abertura"]).dt.total_seconds() / 3600
        df_exec["TMS (h)"] = (df_exec["Data/Hora Término"] - df_exec["Data/Hora Abertura"]).dt.total_seconds() / 3600

        tme = df_exec["TME (h)"].mean()
        tma = df_exec["TMA (h)"].mean()
        tms = df_exec["TMS (h)"].mean()

        resultados.append({
            "Referência": inicio.strftime("%Y-%m"),
            "Backlogs": backlog,
            "OS Abertas": os_abertas,
            "OS Não Atendidas": os_nao_atendidas,
            "OS Atendidas": os_atendidas,
            "Backlogs Atendidos": backlog_atendidos,
            "TME (h)": round(tme, 2),
            "TMA (h)": round(tma, 2),
            "TMS (h)": round(tms, 2)
        })

    # Criar DataFrame consolidado
    df_resultados = pd.DataFrame(resultados)
    #print(df_resultados)
    # Calcular indicadores adicionais
    df_resultados["% Atendimento"] = ((df_resultados["OS Atendidas"] / df_resultados["OS Abertas"]) * 100).round(1)
    df_resultados["Índice Crescimento Backlog"] = (df_resultados["Backlogs"].pct_change() * 100).round(1)
    df_resultados["Índice Atendimento Backlog"] = ((df_resultados["Backlogs Atendidos"] / df_resultados["Backlogs"].shift(1)) * 100).round(1)
    df_resultados["Índice de Reação (TMA/TME)"] = (df_resultados["TMA (h)"] / df_resultados["TME (h)"]).round(1)

    return df_resultados
