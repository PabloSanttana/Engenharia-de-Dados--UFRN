<h1 align="center">
    <a href="https://docs.docker.com/">🔗 Docker</a>
</h1>
<p align="center">🚀 Primiera Atividade de Docker</p>

- [Roteiro](./roteiro.docx)

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

##### crie dois repositorios

##### clientetcp

##### servidortcp

### Construir as imagens a partir dos arquivos Dockerfile.

#### Imagem cliente:

```bash

    docker build -f Dockerfile.client -t <usuario-dockerhub>/clientetcp:v1 .

```

#### Imagem servidor:

```bash

   docker build -f Dockerfile.server -t <usuario-dockerhub>/servidortcp:v1 .

```

### enviar o arquivo client

```bash

  docker push <usuario-dockerhub>/clientetcp:v1

```

### Servidor

```bash
    docker run -p 30000:30000 -it <usuario-dockerhub>/servidortcp:v1

```

### cliente

```bash

    docker run <usuario-dockerhub>/clientetcp:v1 <ip-do-servidor>

```
