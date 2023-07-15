from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.bash import BashOperator
import pandas as pd
import requests
import pytz

# Defina a função de formatação para o eixo y
def formatar_eixo_y(valor, pos):
    return "{:,.0f}".format(valor).replace(",", ".")

# Defina a função de formatação para o eixo x
def formatar_eixo_x(data):
    data_str = data.strftime("%Y/%b/%d")
    return data_str

def get_data():
    url = 'https://olinda.bcb.gov.br/olinda/servico/SPI/versao/v1/odata/PixLiquidadosAtual?$top=365&$orderby=Data%20desc&$format=json&$select=Data,Quantidade,Total,Media'
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

 
    df['Data'] = pd.to_datetime(df['Data'], format='%Y-%m-%d')
    df['Ano'] = df['Data'].dt.year
    df['Mes'] = df['Data'].dt.month

    df_soma = df.groupby(['Ano', 'Mes']).agg({'Total': 'sum', 'Quantidade': 'sum'}).reset_index()
    df_soma['Ano_Mes'] = df_soma['Ano'].astype(str) + '/' + df_soma['Mes'].astype(str)

    print(df_data_total)
    print(df_data_qtd)
    print(df_data_md)
    print(df_soma)
    return df_data_total, df_data_qtd, df_data_md, df_data_hours_total_md, df_data_hours_qtd_md,df_soma


def table_total(ti):
    data = ti.xcom_pull(task_ids='process_data')
    df = data[0]
    df = df.sort_values('Data', ascending=True)
    df['Data'] = df['Data'].apply(lambda x: formatar_eixo_x(x))
    table_name = 'Valor do Pix Total'
    print(table_name)
    return {
    'table_name': table_name,
    'total_values': df['Total'].tolist(),
    'data_values': df['Data'].tolist()
}


def table_qtd(ti):
    data = ti.xcom_pull(task_ids='process_data')
    df = data[1]
    df = df.sort_values('Data', ascending=True)
    table_name = 'Quantidade de Pix feitos'
    # converter
    df['Data'] = df['Data'].apply(lambda x: formatar_eixo_x(x))
    # Exiba o gráfico de barras
    print(table_name)
    return {
    'table_name': table_name,
    'total_values': df['Quantidade'].tolist(),
    'data_values': df['Data'].tolist()
    }


def table_md(ti):
    data = ti.xcom_pull(task_ids='process_data')
    df = data[2]
    df = df.sort_values('Data', ascending=True)
    table_name = 'Valor R$ médio do Pix'
    # converter
    df['Data'] = df['Data'].apply(lambda x: formatar_eixo_x(x))
    return {
    'table_name': table_name,
    'total_values': df['Media'].tolist(),
    'data_values': df['Data'].tolist()
    }


def table_hours_total_md(ti):
    data = ti.xcom_pull(task_ids='process_data')
    df = data[3]
    table_name = 'Valor Total médio do Pix'
    return {
    'table_name': table_name,
    'total_values': df['TotalMedio'].tolist(),
    'data_values': df['Horario'].tolist()
    }


def table_hours_qtd_md(ti):
    data = ti.xcom_pull(task_ids='process_data')
    df = data[4]
    table_name = 'Quantidade Media do Pix'
    return {
    'table_name': table_name,
    'total_values': df['QuantidadeMedia'].tolist(),
    'data_values': df['Horario'].tolist()
    }
   

def gererate_html(ti):
    df = ti.xcom_pull(task_ids='get_data')
    data = ti.xcom_pull(task_ids='process_data')
    table_total_ano = data[5]
    df_data_hours = ti.xcom_pull(task_ids='get_data_hours')
    dataTable_total = ti.xcom_pull(task_ids='table_total')
    table_qtd = ti.xcom_pull(task_ids='table_qtd')
    table_md = ti.xcom_pull(task_ids='table_md')
    table_hours_total_md = ti.xcom_pull(task_ids='table_hours_total_md')
    table_hours_qtd_md = ti.xcom_pull(task_ids='table_hours_qtd_md')
    
    # Get the current time in the UTC time zone
    utc_now = datetime.now(pytz.utc)

    # Convert the UTC time to Brasília time zone
    brasilia_timezone = pytz.timezone('America/Sao_Paulo')
    brasilia_now = utc_now.astimezone(brasilia_timezone)

    # Format the Brasília time in the desired format
    formatted_datetime = brasilia_now.strftime("%d/%m/%Y %H:%M:%S")

    html = """
    <html>
    <head>
        <title>Projeto Engenharia de dados</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.0.0/dist/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
        <script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
        <script src="https://cdn.jsdelivr.net/npm/popper.js@1.12.9/dist/umd/popper.min.js" integrity="sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q" crossorigin="anonymous"></script>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.0.0/dist/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const ctx = document.getElementById('myChart').getContext('2d');
            const ctx2 = document.getElementById('myChart2').getContext('2d');
            const ctx3 = document.getElementById('myChart3').getContext('2d');
            const ctx4 = document.getElementById('myChart4').getContext('2d');
            const ctx5 = document.getElementById('myChart5').getContext('2d');
            const ctx6 = document.getElementById('myChart6').getContext('2d');
            const ctx7 = document.getElementById('myChart7').getContext('2d');
    
            new Chart(ctx, {
                type: 'bar',
                data: {
        """
    
    html += 'labels: ['
    labels = [f'"{label}"' for label in dataTable_total['data_values']]
    html += ','.join(labels)
    html += '],'
    html +="""datasets: [{
                        label: """f'"{str(dataTable_total["table_name"])}"'""",
    """
    html += 'data: ['
    data = [f'"{item}"' for item in dataTable_total["total_values"]]
    html += ','.join(data)
    html += '],'              
    html +="""
            borderWidth: 1,
            backgroundColor:['rgba(31, 119, 180, 0.4)'],
            borderColor:['#1f77b4'],
                            }]
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
     
            new Chart(ctx2, {
                        type: 'bar',
                        data: {
            """
    html += 'labels: ['
    labels = [f'"{label}"' for label in table_qtd['data_values']]
    html += ','.join(labels)
    html += '],'
    html +="""datasets: [{
                        label: """f'"{str(table_qtd["table_name"])}"'""",
    """
    html += 'data: ['
    data = [f'"{item}"' for item in table_qtd["total_values"]]
    html += ','.join(data)
    html += '],'              
    html +="""
            borderWidth: 1,
            backgroundColor:['rgba(31, 119, 180, 0.4)'],
            borderColor:['#1f77b4'],
                    }]
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
       

            new Chart(ctx3, {
                        type: 'bar',
                        data: {
            """
    html += 'labels: ['
    labels = [f'"{label}"' for label in table_md['data_values']]
    html += ','.join(labels)
    html += '],'
    html +="""datasets: [{
                        label: """f'"{str(table_md["table_name"])}"'""",
    """
    html += 'data: ['
    data = [f'"{item}"' for item in table_md["total_values"]]
    html += ','.join(data)
    html += '],'              
    html +="""
            borderWidth: 1,
            backgroundColor:['rgba(31, 119, 180, 0.4)'],
            borderColor:['#1f77b4'],
                    }]
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });

        new Chart(ctx4, {
            type: 'line',
            data: {
    """
    html += 'labels: ['
    labels = [f'"{label}"' for label in table_hours_total_md['data_values']]
    html += ','.join(labels)
    html += '],'
    html +="""datasets: [{
                        label: """f'"{str(table_hours_total_md["table_name"])}"'""",
    """
    html += 'data: ['
    data = [f'"{item}"' for item in table_hours_total_md["total_values"]]
    html += ','.join(data)
    html += '],'              
    html +="""
            fill: false,
            borderColor: 'rgb(75, 192, 192)',
            tension: 0.2
                }]
            },
            })

            
        new Chart(ctx5, {
            type: 'line',
            data: {
    """
    html += 'labels: ['
    labels = [f'"{label}"' for label in table_hours_qtd_md['data_values']]
    html += ','.join(labels)
    html += '],'
    html +="""datasets: [{
                        label: """f'"{str(table_hours_qtd_md["table_name"])}"'""",
    """
    html += 'data: ['
    data = [f'"{item}"' for item in table_hours_qtd_md["total_values"]]
    html += ','.join(data)
    html += '],'              
    html +="""
            fill: false,
            borderColor: 'rgb(75, 192, 192)',
            tension: 0.2
                }]
            },
            })


    
    new Chart(ctx6, {
            type: 'line',
            data: {
    """
    html += 'labels: ['
    labels = [f'"{label}"' for label in table_total_ano['Ano_Mes']]
    html += ','.join(labels)
    html += '],'
    html +="""datasets: [{
                        label: 'Valor Total Pix do mes',
    """
    html += 'data: ['
    data = [f'"{item}"' for item in table_total_ano["Total"]]
    html += ','.join(data)
    html += '],'              
    html +="""
            fill: false,
            borderColor: 'rgb(75, 192, 192)',
            tension: 0.2
                }]
            },
            })

      new Chart(ctx7, {
            type: 'line',
            data: {
    """
    html += 'labels: ['
    labels = [f'"{label}"' for label in table_total_ano['Ano_Mes']]
    html += ','.join(labels)
    html += '],'
    html +="""datasets: [{
                        label: 'Quantidade Total Pix do mes',
    """
    html += 'data: ['
    data = [f'"{item}"' for item in table_total_ano["Quantidade"]]
    html += ','.join(data)
    html += '],'              
    html +="""
            fill: false,
            borderColor: 'rgb(75, 192, 192)',
            tension: 0.2
                }]
            },
            })


        });
        </script>
    </head>
    <body class="bg-secondary">

    <div class="container bg-light border pb-5">
        <p class="text-center my-2">Atualizado em:"""+ f'{formatted_datetime}'+"""</p>
        <h1 class="text-center my-5">Projeto Engenharia de dados</h1>

        <p class="p-0 m-0"><strong style="font-size: 1.2rem;">Docente:</strong> CARLOS MANUEL DIAS VIEGAS</p>
        <p class="p-0 m-0"><strong style="font-size: 1.2rem;">Grupo:</strong> </p>
        <p class="p-0 m-0 ml-5"><strong style="font-size: 1.2rem;">Discente:</strong> GUILHERME PABLO DE SANTANA MACIEL
        </p>
        <p class="p-0 m-0 ml-5"><strong style="font-size: 1.2rem;">Discente:</strong> LUIZ HENRIQUE ARAÚJO DANTAS</p>

        <h2 class="text-center mb-2 mt-5">Gráficos</h2>
    

        <h3 class="text-center my-5">Valores Total do Pix feito diariamente</h1>
        <p class="text-center my-1">Útimos 30 dias</p>
        <div class="container bg-white my-5" >
            <canvas id="myChart"></canvas>
        </div>

        <h3 class="text-center my-5">Quantidade Pix feito diariamente</h1>
        <p class="text-center my-1">Útimos 30 dias</p>
        <div class="container bg-white my-5" >
            <canvas id="myChart2"></canvas>
        </div>

        <h3 class="text-center my-5">Valores médios de movimentação do Pix feito diariamente</h1>
        <p class="text-center my-1">Útimos 30 dias</p>
        <div class="container bg-white my-5" >
            <canvas id="myChart3"></canvas>
        </div>

        <h3 class="text-center my-5">Valores médio de movimentação do Pix</h1>
        <p class="text-center my-1">Útimos 30 dias</p>
        <div class="container bg-white my-5" >
            <canvas id="myChart4"></canvas>
        </div>

        

        <h3 class="text-center my-5">Quantidade média de movimentação do Pix</h1>
        <p class="text-center my-1">Útimos 30 dias</p>
        <div class="container bg-white my-5" >
            <canvas id="myChart5"></canvas>
        </div>

        <h3 class="text-center my-5">Valor Total de Pix</h1>
        <p class="text-center my-1">Útimos 12 meses</p>
        <div class="container bg-white my-5" >
            <canvas id="myChart6"></canvas>
        </div>

        <h3 class="text-center my-5">Quantidade de Pix feita</h1>
        <p class="text-center my-1">Útimos 12 meses</p>
        <div class="container bg-white my-5" >
            <canvas id="myChart7"></canvas>
        </div>


        <h2 class="text-center my-5">Tabelas</h2>

        <h3 class="text-center my-3">Pix Evolução Diária</h3>

        <div style="max-height: 400px; overflow:auto">
            <table class="table table-striped my-3">
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
         <h3 class="text-center my-3">Pix Evolução Diária em horas</h3>
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
    'start_date': datetime(2023, 7, 11),
    'schedule_interval': '30 * * * *',
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
