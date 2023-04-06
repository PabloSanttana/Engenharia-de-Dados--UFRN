<h1 align="center">
    <a href="https://docs.docker.com/">🔗 Docker</a>
</h1>
<p align="center">🚀 Segunda Atividade de Docker</p>

- [Roteiro](./aula_4_-_roteiro_docker_-_Docker_Compose.pdf)

##### Tutorial atividade com base no roteiro acima

##### O projeto pode ser feito direto sua maquina ou play-with-docker

- [play-with-docker](https://labs.play-with-docker.com)

##### CMD: do play-with-docker

```bash

   vim Dockerfile.client

```

```python

    FROM python:3-slim
    WORKDIR /app
    COPY clienteTCP.py /app
    ENTRYPOINT ["python","clienteTCP.py"]

```

```bash

   vim Dockerfile.server

```

```python

    FROM python:3-slim
    WORKDIR /app
    COPY servidorTCP.py /app
    ENTRYPOINT ["python","servidorTCP.py"]

```

#### salvar é sair CMD :wq!

#### Agora baixar os scripts clienteTCP.py e servidorTCP.py

- [clienteTCP.py](https://www.dca.ufrn.br/~viegas/disciplinas/DCA0132/files/Sockets/clienteTCP.py)

- [servidorTCP.py](https://www.dca.ufrn.br/~viegas/disciplinas/DCA0132/files/Sockets/servidorTCP.py)

```bash

   vim servidorTCP.py

```

```python

    # SCRIPT SERVIDOR TCP (python3) #
    # COMO EXECUTAR?
    # ?> python servidorTCP.py #

    # importacao das bibliotecas
    from socket import * # sockets

    # definicao das variaveis
    serverPort = 30000 # porta a servir
    serverSocket = socket(AF_INET,SOCK_STREAM) # criacao do socket TCP
    serverSocket.bind(('',serverPort)) # bind do ip do servidor com a porta
    serverSocket.listen(1) # socket pronto para 'ouvir' conexoes
    serverIP=gethostbyname(gethostname())
    print ('> servidor iniciado em %s:%d ...' % (serverIP,serverPort))
    while 1:
    connectionSocket, addr = serverSocket.accept() # aceita as conexoes dos clientes
    sentence = connectionSocket.recv(1024) # recebe dados do cliente
    sentence = sentence.decode('utf-8') # codifica em utf-8
    print ('> mensagem recebida de %s -> %s' % (addr, sentence))
    connectionSocket.close() # encerra o socket com o cliente
    serverSocket.close() # encerra o socket do servidor

```

#### salvar é sair :wq!

```bahs
    vim clienteTCP.py
```

```python

    # SCRIPT CLIENTE TCP (python3)
    #
    # COMO EXECUTAR?
    # ?> python clienteTCP.py <endereco-ip-do-servidor>
    #

    # importacao das bibliotecas
    from socket import *
    import sys
    import time

    # definicao das variaveis
    serverName = str(sys.argv[1])
    serverPort = 30000 # porta a se conectar
    clientSocket = socket(AF_INET,SOCK_STREAM) # criacao do socket TCP
    clientSocket.connect((serverName, serverPort)) # conecta o socket ao servidor

    sentence = 'hostname: ' + gethostname() + ' ip: ' + gethostbyname(gethostname())
    print ('> enviando para o servidor -> %s' % sentence)
    clientSocket.send(sentence.encode('utf-8')) # envia o texto para o servidor
    time.sleep(2)
    clientSocket.close() # encerramento o socket do cliente

```

#### salvar é sair :wq!

### Acesse seu dockerHub

- [hub.docker](https://hub.docker.com/)

#### Usando as images da <a href="https://github.com/PabloSanttana/Engenharia-de-Dados--UFRN/tree/master/Atividade01" target="_blank">primaira atividade</a>

```bash
# Indica a versão do Docker Compose que será utilizada
version: "3.9"
#No docker-compose.yml deve ser definida uma rede com a faixa de ip específica na rede 172.18.0.0/24.
#Como sugestão, segue parte da especificação dessa rede:
networks:
  main-redes:
    driver: bridge
    ipam:
      driver: default
      config:
        - subnet: 172.18.0.0/24
# Serviços que serão executados nos containers
services:
  # Nome do serviço a ser criado
  servidor:
    # Nome do container que será executado
    container_name: servidortcp
    # Imagem que será executada no container
    # A imagem é obtida localmente ou a partir do Dockerhub
    image:  <nome-do-usuario-dockerhub>/servidortcp:v1
    build:
      context: .
      dockerfile: ./Dockerfile.server
    # Especificando a rede do servidor
    networks:
      main-redes:
        ipv4_address: 172.18.0.2
    ports:
      - 30000:30000
    # Permite a exibição de texto na tela do terminal
    tty: true
  # Nome do segundo serviço a ser criado
  cliente:
    container_name: cliente1
    # O depends_on faz com que este serviço seja executado após outro
    depends_on:
      - servidor
    image: <nome-do-usuario-dockerhub>/clientetcp:v1
    build:
      # O caminho do diretorio que contem o dockerfile
      context: .
      dockerfile: ./Dockerfile.client
    # Conectando o cliente na mesma rede do servidor
    networks:
      main-redes:
        ipv4_address: 172.18.0.3
    # comando a serem executados no cliente logo apos o container ser inicializado passado ip do servidor
    entrypoint: ["python", "clienteTCP.py", "172.18.0.2"]

    tty: true
    # Quando o container terminar a sua execução, sempre irá reiniciar
    restart: always

  cliente2:
    container_name: cliente2
    depends_on:
      - servidor
    image: <nome-do-usuario-dockerhub>/clientetcp:v1
    build:
      context: .
      dockerfile: ./Dockerfile.client
    networks:
      main-redes:
        ipv4_address: 172.18.0.4

    entrypoint: ["python", "clienteTCP.py", "172.18.0.2"]
    tty: true
    restart: always


```

#### Para executar os containers por meio do Docker Compose, basta executar no terminal:

```bash
    docker compose up
```

### Ou ainda, executar um serviço de forma específica:

```bash
    docker compose up <serviço>
```
