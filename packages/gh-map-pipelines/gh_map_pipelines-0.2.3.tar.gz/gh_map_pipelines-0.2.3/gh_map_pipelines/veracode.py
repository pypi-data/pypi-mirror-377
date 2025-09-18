# -*- coding: utf-8 -*-

import os
import pandas as pd
from veracode_api_py import Applications, SummaryReport

def main():
    """
    Main function to fetch Veracode data and generate a vulnerability report.
    """
    print("Iniciando o script para buscar dados de vulnerabilidades da Veracode...")

    # --- Configuração de Credenciais ---
    # Para segurança, é altamente recomendável usar variáveis de ambiente
    # para armazenar suas credenciais da API Veracode.
    # Exemplo:
    # no seu terminal, execute:
    # export VERACODE_API_KEY_ID="SEU_ID_AQUI"
    # export VERACODE_API_KEY_SECRET="SUA_CHAVE_SECRETA_AQUI"
    #
    # Se não estiver usando variáveis de ambiente, descomente as linhas abaixo
    # e insira suas credenciais diretamente (não recomendado para produção).
    # os.environ['VERACODE_API_KEY_ID'] = 'SEU_ID_AQUI'
    # os.environ['VERACODE_API_KEY_SECRET'] = 'SUA_CHAVE_SECRETA_AQUI'

    # Verifica se as credenciais foram configuradas
    if 'VERACODE_API_KEY_ID' not in os.environ or 'VERACODE_API_KEY_SECRET' not in os.environ:
        print("\nERRO: As credenciais da API Veracode não foram encontradas.")
        print("Por favor, configure as variáveis de ambiente VERACODE_API_KEY_ID e VERACODE_API_KEY_SECRET.")
        return

    try:
        # Lista para armazenar os dados de cada aplicação
        report_data = []

        print("Buscando a lista de aplicações...")
        # Busca todas as aplicações na sua conta Veracode
        apps = Applications().get_all()
        print(f"Encontradas {len(apps)} aplicações.")

        # Itera sobre cada aplicação para obter os detalhes
        for app in apps:
            app_guid = app.get('guid')
            app_name = app.get('profile', {}).get('name', 'Nome não encontrado')

            print(f"Processando aplicação: {app_name} (GUID: {app_guid})")

            # Busca o relatório de resumo para a aplicação atual
            summary = SummaryReport().get_summary_report(app_guid)

            # Extrai a contagem de falhas por severidade
            severities = summary.get('severity', [])
            
            # Inicializa um dicionário para armazenar as contagens
            severity_counts = {
                'Very High': 0,
                'High': 0,
                'Medium': 0,
                'Low': 0,
                'Very Low': 0,
                'Informational': 0
            }

            # Preenche o dicionário com os dados da API
            for severity in severities:
                print(severity)
                level = int(severity.get('level'))
                count = int(severity.get('count'))
                if level == 5:
                    severity_counts['Very High'] = count
                elif level == 4:
                    severity_counts['High'] = count
                elif level == 3:
                    severity_counts['Medium'] = count
                elif level == 2:
                    severity_counts['Low'] = count
                elif level == 1:
                    severity_counts['Very Low'] = count
                elif level == 0:
                    severity_counts['Informational'] = count

            # Adiciona os dados coletados à nossa lista de relatórios
            report_data.append({
                'NomeApp': app_name,
                'Very High': severity_counts['Very High'],
                'High': severity_counts['High'],
                'Medium': severity_counts['Medium'],
                'Low': severity_counts['Low']
            })

        # Verifica se algum dado foi coletado
        if not report_data:
            print("Nenhum dado de aplicação foi processado. Encerrando.")
            return

        # Cria um DataFrame do Pandas com os dados coletados
        df = pd.DataFrame(report_data)

        # Reordena as colunas para garantir a ordem desejada
        df = df[['NomeApp', 'Very High', 'High', 'Medium', 'Low']]

        print("\n--- Relatório de Vulnerabilidades por Aplicação ---")
        print(df.to_string())

        # Opcional: Salvar o DataFrame em um arquivo CSV
        output_filename = 'veracode_vulnerability_report.csv'
        df.to_csv(output_filename, index=False)
        print(f"\nRelatório salvo com sucesso no arquivo: {output_filename}")

    except Exception as e:
        print(f"\nOcorreu um erro durante a execução do script: {e}")
        print("Verifique suas credenciais e permissões na API Veracode.")

if __name__ == '__main__':
    main()
