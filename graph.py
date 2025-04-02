# Gerar gráficos e salvar planilha Excel com todos os indicadores mensais

# Caminho do arquivo Excel
excel_output_path = "/mnt/data/Indicadores_Mensais_Completos.xlsx"
tabela_mensal.to_excel(excel_output_path, index=False)

# Gráficos
plt.figure(figsize=(10, 6))
plt.plot(tabela_mensal["Referência"], tabela_mensal["OS Abertas"], label="OS Abertas", marker="o")
plt.plot(tabela_mensal["Referência"], tabela_mensal["OS Atendidas"], label="OS Atendidas", marker="o")
plt.plot(tabela_mensal["Referência"], tabela_mensal["OS Não Atendidas"], label="OS Não Atendidas", marker="o")
plt.title("Volume de Ordens de Serviço por Mês")
plt.xlabel("Mês")
plt.ylabel("Quantidade")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

plt.figure(figsize=(10, 6))
plt.plot(tabela_mensal["Referência"], tabela_mensal["Backlogs"], label="Backlog", marker="o")
plt.plot(tabela_mensal["Referência"], tabela_mensal["Backlogs Atendidos"], label="Backlogs Atendidos", marker="o")
plt.title("Backlog de Ordens de Serviço")
plt.xlabel("Mês")
plt.ylabel("Quantidade")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

plt.figure(figsize=(10, 6))
plt.plot(tabela_mensal["Referência"], tabela_mensal["TME (h)"], label="TME", marker="o")
plt.plot(tabela_mensal["Referência"], tabela_mensal["TMA (h)"], label="TMA", marker="o")
plt.plot(tabela_mensal["Referência"], tabela_mensal["TMS (h)"], label="TMS", marker="o")
plt.title("Tempos Médios de Manutenção")
plt.xlabel("Mês")
plt.ylabel("Horas")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

plt.figure(figsize=(10, 6))
plt.plot(tabela_mensal["Referência"], tabela_mensal["% Atendimento"], label="% Atendimento", marker="o")
plt.plot(tabela_mensal["Referência"], tabela_mensal["Índice Crescimento Backlog"], label="Crescimento Backlog (%)", marker="o")
plt.plot(tabela_mensal["Referência"], tabela_mensal["Índice de Reação (TMA/TME)"], label="Índice de Reação (TMA/TME)", marker="o")
plt.title("Indicadores Analíticos de Manutenção")
plt.xlabel("Mês")
plt.ylabel("Indicador (%) ou razão")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# Retornar o caminho do arquivo Excel gerado
excel_output_path
