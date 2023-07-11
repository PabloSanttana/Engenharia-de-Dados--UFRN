from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.bash import BashOperator
import pandas as pd
import requests
import json
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import base64
import numpy as np

# Defina a função de formatação para o eixo y
def formatar_eixo_y(valor, pos):
    return "{:,.0f}".format(valor).replace(",", ".")

# Defina a função de formatação para o eixo x
def formatar_eixo_x(data):
    data_str = data.strftime("%Y/%b/%d")
    return data_str

def get_data():
    url = 'https://olinda.bcb.gov.br/olinda/servico/SPI/versao/v1/odata/PixLiquidadosAtual?$top=100&$orderby=Data%20desc&$format=json&$select=Data,Quantidade,Total,Media'
    # Faça a solicitação HTTP para baixar o JSON
    response = requests.get(url)
    json_data = response.json()
    # Converter a resposta JSON para um objeto Python
    data = json_data['value']
    # Converter a resposta JSON para um objeto Python
    df_data = pd.DataFrame(data)
    # Exibir o resultado

    print(df_data)
    return df_data

def get_data_hours():
    url2 = 'https://olinda.bcb.gov.br/olinda/servico/SPI/versao/v1/odata/PixLiquidadosIntradia?$top=100&$format=json&$select=Horario,QuantidadeMedia,TotalMedio'
    response_hours = requests.get(url2)
    json_data_hours = response_hours.json()
    data_hours = json_data_hours['value']
    df_data_hours = pd.DataFrame(data_hours)
    print(df_data_hours)
    return df_data_hours

def process_data(ti):
    df = ti.xcom_pull(task_ids='get_data')
    df_data_hours = ti.xcom_pull(task_ids='get_data_hours')
    # Adicionar coluna com a data atual
    current_date = datetime.now().date()
    df['DataAtual'] = pd.to_datetime(current_date)
    print(df)
    # Converter a coluna 'Data' para o tipo datetime
    df['Data'] = pd.to_datetime(df['Data'])
    # Calcular a data limite (30 dias atrás)
    data_limite = pd.Timestamp(datetime.now().date() - timedelta(days=30))
    # Filtrar os dados mantendo apenas os últimos 30 dias
    df_filtrado = df[df['Data'] >= data_limite]
    # Exibir o DataFrame resultante
    print(df_filtrado)
    # Criar um novo DataFrame com as colunas 'Data' e 'Total'
    df_data_total = df_filtrado.loc[:, ['Data', 'Total']]
    df_data_qtd = df_filtrado.loc[:, ['Data', 'Quantidade']]
    df_data_md = df_filtrado.loc[:, ['Data', 'Media']]
    df_data_hours_total_md = df_data_hours.loc[:, ['Horario', 'TotalMedio']]
    df_data_hours_qtd_md = df_data_hours.loc[:, ['Horario', 'QuantidadeMedia']]
    print(df_data_total)
    print(df_data_qtd)
    print(df_data_md)
    return df_data_total, df_data_qtd, df_data_md, df_data_hours_total_md, df_data_hours_qtd_md


def table_total(ti):
    data = ti.xcom_pull(task_ids='process_data')
    df = data[0]
    df = df.sort_values('Data', ascending=True)
    # converter

    # Exiba o gráfico de barras
    ax = df.plot.bar(x="Data", y="Total", figsize=(16, 12))
    plt.xlabel("Valor")
    plt.ylabel("em R$")
    plt.title("Útimos 30 dias")
    plt.suptitle("Valores de Pix feitos diariamente")
    # Formate o eixo y para exibir valores em formato numérico normal
    ax.ticklabel_format(axis='y', style='plain')
    # Formate o eixo y usando a função de formatação
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(formatar_eixo_y))

    # Formate o eixo x usando a função de formatação
    print(df["Data"])
    ax.set_xticklabels(df["Data"].map(formatar_eixo_x))

    # Salvar o gráfico em um arquivo
    filename = '/opt/airflow/logs/graficDataTotal.png'
    plt.savefig(filename)

    print(df)
    return


def table_qtd(ti):
    data = ti.xcom_pull(task_ids='process_data')
    df = data[1]
    df = df.sort_values('Data', ascending=True)
    # converter

    # Exiba o gráfico de barras
    ax = df.plot.bar(x="Data", y="Quantidade", figsize=(16, 12))
    plt.xlabel("Quantidade")
    plt.ylabel("")
    plt.title("Útimos 30 dias")
    plt.suptitle("Quantidade de Pix feitos diariamente")
    # Formate o eixo y para exibir valores em formato numérico normal
    ax.ticklabel_format(axis='y', style='plain')
    # Formate o eixo y usando a função de formatação
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(formatar_eixo_y))

    # Formate o eixo x usando a função de formatação
    print(df["Data"])
    ax.set_xticklabels(df["Data"].map(formatar_eixo_x))

    # Salvar o gráfico em um arquivo
    filename = '/opt/airflow/logs/graficDataQuantidade.png'
    plt.savefig(filename)

    print(df)
    return


def table_md(ti):
    data = ti.xcom_pull(task_ids='process_data')
    df = data[2]
    df = df.sort_values('Data', ascending=True)
    # converter
    # Exiba o gráfico de barras
    ax = df.plot.bar(x="Data", y="Media", figsize=(16, 12))
    plt.xlabel("Valor R$ médio")
    plt.ylabel("em R$")
    plt.title("Útimos 30 dias")
    plt.suptitle("Valores médio de movimentação de Pix diariamente")

    # Formate o eixo y para exibir valores em formato numérico normal
    ax.ticklabel_format(axis='y', style='plain')
    # Formate o eixo y usando a função de formatação
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(formatar_eixo_y))

    # Formate o eixo x usando a função de formatação
    print(df["Data"])
    ax.set_xticklabels(df["Data"].map(formatar_eixo_x))

    # Salvar o gráfico em um arquivo
    filename = '/opt/airflow/logs/graficDataMedia.png'
    plt.savefig(filename)

    print(df)
    return


def table_hours_total_md(ti):
    data = ti.xcom_pull(task_ids='process_data')
    df = data[3]
    # converter
    # Exiba o gráfico de barras
    ax = df.plot(x="Horario", y="TotalMedio", linewidth=2, marker='o', markersize=6, figsize=(16, 12))
    plt.xlabel("Valor R$  médio")
    plt.grid(True)
    plt.ylabel("em R$")
    plt.title("Útimos 30 dias")
    plt.suptitle("Valores médio de movimentação de Pix")
    # Formate o eixo y para exibir valores em formato numérico normal
    ax.ticklabel_format(axis='y', style='plain')
    # Formate o eixo y usando a função de formatação
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(formatar_eixo_y))
    # Formate o eixo x usando a função de formatação
    x = np.arange(0, len(df['Horario']), 2)
    labels = df["Horario"].iloc[::2].tolist()  # Valores dos rótulos pulando 2 casas
    plt.xticks(x, labels)
    print(df)

    # Salvar o gráfico em um arquivo
    filename = '/opt/airflow/logs/graficoHoursTotalMedia.png'
    plt.savefig(filename)

    print(df)
    return


def table_hours_qtd_md(ti):
    data = ti.xcom_pull(task_ids='process_data')
    df = data[4]
    # converter
    # Exiba o gráfico de barras
    ax = df.plot(x="Horario", y="QuantidadeMedia", linewidth=2, marker='o', markersize=6, figsize=(16, 12))
    plt.xlabel("Quantidade Media")
    plt.grid(True)
    plt.ylabel("")
    plt.title("Útimos 30 dias")
    plt.suptitle("Quantidade Media de movimentação de Pix")
    # Formate o eixo y para exibir valores em formato numérico normal
    ax.ticklabel_format(axis='y', style='plain')
    # Formate o eixo y usando a função de formatação
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(formatar_eixo_y))
    # Formate o eixo x usando a função de formatação
    x = np.arange(0, len(df['Horario']), 2)
    labels = df["Horario"].iloc[::2].tolist()  # Valores dos rótulos pulando 2 casas
    plt.xticks(x, labels)
    print(df)

    # Salvar o gráfico em um arquivo
    filename = '/opt/airflow/logs/graficoHoursQtdMedia.png'
    plt.savefig(filename)

    print(df)
    return


def gererate_html(ti):
    df = ti.xcom_pull(task_ids='get_data')
    df_data_hours = ti.xcom_pull(task_ids='get_data_hours')

    html = """
    <html>
    <head>
        <title>Projeto Engenharia de dados</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.0.0/dist/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
        <script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
        <script src="https://cdn.jsdelivr.net/npm/popper.js@1.12.9/dist/umd/popper.min.js" integrity="sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q" crossorigin="anonymous"></script>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.0.0/dist/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>
    </head>
    <body class="bg-secondary">

    <div class="container bg-light border pb-5">

        <h1 class="text-center my-5">Projeto Engenharia de dados</h1>
        <img src="./graficDataTotal.png" class="img-fluid my-3" alt="Responsive image"/>
        <img src="./graficDataMedia.png" class="img-fluid my-3" alt="Responsive image"/>
        <img src="./graficDataQuantidade.png" class="img-fluid my-3" alt="Responsive image"/>
        <img src="./graficoHoursTotalMedia.png" class="img-fluid my-3" alt="Responsive image"/>
        <img src="./graficoHoursQtdMedia.png" class="img-fluid my-3" alt="Responsive image"/>


        <h2 class="text-center my-3">Pix Evolução Diária</h2>

    <div style=" max-height: 400px; overflow:auto">
        <table  class="table table-striped my-3">
        <thead>
            <tr>
                <th scope="col">Data</th>
                <th scope="col">Quantidade</th>
                <th scope="col">Media</th>
                <th scope="col">Total</th>
            </tr>
        </thead>
        <tbody>
        
    """

    # Iterar sobre as linhas do DataFrame df e adicionar como linhas na tabela HTML
    for _, row in df.iterrows():
        Media = "{:,.2f}".format(row['Media']).replace(",", ".")
        Quantidade = "{:,.2f}".format(row['Quantidade']).replace(",", ".")
        Total = "{:,.2f}".format(row['Total']).replace(",", ".")
        html += f"<tr><td>{row['Data']}</td><td>{Quantidade}</td><td>R$: {Media}</td><td>R$: {Total}</td></tr>"

    html += """
        </tbody>
        </table>
        </div>
         <h2 class="text-center my-3">Pix Evolução Diária em horas</h2>
         <div style=" max-height: 400px; overflow:auto">
        <table class="table table-striped my-3">
        </thead>
            <tr>
                <th scope="col">Horario</th>
                <th scope="col">Quantidade Média</th>
                <th scope="col">Total Médio</th>
            </tr>
        </thead>
        <tbody>
    """

    # Iterar sobre as linhas do DataFrame df_data_hours e adicionar como linhas na tabela HTML
    for _, row in df_data_hours.iterrows():
        QuantidadeMedia = "{:,.2f}".format(row['QuantidadeMedia']).replace(",", ".")
        TotalMedio = "{:,.2f}".format(row['TotalMedio']).replace(",", ".")
        html += f"<tr><td>{row['Horario']}</td><td>{QuantidadeMedia}</td><td>R$: {TotalMedio}</td></tr>"

    html += """
        </tbody>
        </table>
         </div>
        </div>
    </body>
    </html>
    """

    # Salvar o HTML gerado em um arquivo
    with open('/opt/airflow/logs/index.html', 'w') as f:
        f.write(html)
    return


def check_previous_tasks(ti):
    # Lista das tarefas anteriores
    previous_tasks = ['table_total', 'table_qtd', 'table_md', 'table_hours_total_md', 'table_hours_qtd_md']

    # Verificar se todas as tarefas anteriores foram concluídas
    for task in previous_tasks:
        task_status = ti.xcom_pull(task_ids=task, key='return_value')
        if task_status != 'success':
            return 'wait_for_previous_tasks'  # Se alguma tarefa não foi concluída, aguardar

    return 'generate_html'  # Todas as tarefas anteriores concluídas, prosseguir para gerar o HTML


default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 7, 2),
    'schedule_interval': '10 * * * *',
    'catchup': False
}

with DAG('projeto_eng_dados', default_args=default_args) as dag:
    get_data = PythonOperator(
        task_id='get_data',
        python_callable=get_data
    )

    get_data_hours = PythonOperator(
        task_id='get_data_hours',
        python_callable=get_data_hours
    )

    process_data = PythonOperator(
        task_id='process_data',
        python_callable=process_data
    )

    table_total = PythonOperator(
        task_id='table_total',
        python_callable=table_total
    )

    table_qtd = PythonOperator(
        task_id='table_qtd',
        python_callable=table_qtd
    )

    table_md = PythonOperator(
        task_id='table_md',
        python_callable=table_md
    )

    table_hours_total_md = PythonOperator(
        task_id='table_hours_total_md',
        python_callable=table_hours_total_md
    )

    table_hours_qtd_md = PythonOperator(
        task_id='table_hours_qtd_md',
        python_callable=table_hours_qtd_md
    )

    generate_html_op = PythonOperator(
        task_id='generate_html',
        python_callable=gererate_html
    )

    finsh = BashOperator(
        task_id='finsh',
        bash_command="echo '-----finsh-----'"
    )

    check_previous_tasks_op = BranchPythonOperator(
        task_id='check_previous_tasks',
        python_callable=check_previous_tasks,
    )

    wait_for_previous_tasks_op = BashOperator(
        task_id='wait_for_previous_tasks',
        bash_command="echo 'Waiting for previous tasks to complete'"
    )

    check_previous_tasks_op >> wait_for_previous_tasks_op
    wait_for_previous_tasks_op >> generate_html_op >> finsh

    get_data >> get_data_hours >> process_data

    process_data >> table_total
    process_data >> table_qtd
    process_data >> table_md
    process_data >> table_hours_total_md
    process_data >> table_hours_qtd_md

    table_total >> check_previous_tasks_op
    table_qtd >> check_previous_tasks_op
    table_md >> check_previous_tasks_op
    table_hours_total_md >> check_previous_tasks_op
    table_hours_qtd_md >> check_previous_tasks_op
