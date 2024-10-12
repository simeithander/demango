<div align="center">
    <picture>
      <img src="static/img/python.svg" alt="Demango" width="100" height="100"/>
    </picture>
  <h1>Demango - Demandas + Django</h1>
</div>

Demango é um sistema desenvolvido inteiramente em Django, voltado para a gestão eficiente das demandas diárias de um desenvolvedor. A plataforma permite a consulta e organização de demandas por meio de pesquisas que podem ser filtradas por intervalos de datas. Além disso, o sistema oferece a funcionalidade de gerar relatórios em PDF contendo informações detalhadas sobre cada demanda, como suas atividades associadas, o responsável e outros dados relevantes. Dessa forma, o Demango otimiza o controle e acompanhamento do trabalho, proporcionando uma visão clara e organizada das demandas e suas execuções.

<div align="center">
    <a href="https://github.com/simeithander/demango/blob/main/screenshots/login.png?raw=true">
      <img src="https://github.com/simeithander/demango/blob/main/screenshots/login.png?raw=true" alt="CD" width="300"/>
    </a>
    <a href="https://github.com/simeithander/demango/blob/main/screenshots/visualizar_demandas.png?raw=true">
      <img src="https://github.com/simeithander/demango/blob/main/screenshots/visualizar_demandas.png?raw=true" alt="CD" width="300"/>
    </a>
    <a href="https://github.com/simeithander/demango/blob/main/screenshots/editar_demanda.png?raw=true">
      <img src="https://github.com/simeithander/demango/blob/main/screenshots/editar_demanda.png?raw=true" target="_blank" alt="CD" width="300"/>
    </a>
    <a href="https://raw.githubusercontent.com/simeithander/demango/refs/heads/main/screenshots/cadastrar_demanda.png">
      <img src="https://raw.githubusercontent.com/simeithander/demango/refs/heads/main/screenshots/cadastrar_demanda.png" alt="CD" width="300"/>
    </a>
</div>

- Python 3.12
- Pip 24
- Django 5.1.1

LOCAL:

1 - Crie uma env

2 - Inicie:

```
 source .venv/bin/activate
```

3 - Crie o .env com base no env.example adicionando sua chave

4 - Execute as dependencias

```
pip install -r requirements.txt
```

5 - Execute as migrações

```
python3 manage.py migrate
```

6 - Crie um usuário inicial

```
python3 manage.py createsuperuser
```

7 - Execute

```
python3 manage.py runserver
```

8 - Acesse

```
http://127.0.0.1:8000/
```

DOCKER:

1 - Instale o docker/docker-compose


2 - Crie o .env com base no env.example adicionando sua chave

3 - Execute

```
docker-compose up -d
```

4 - Acesse o container e crie um super usuário

```
docker exec -it ID_CONTAINER bash
python manage.py createsuperuser
```

5 - Acesse:

```
http://localhost:8000
```

OBS:

Adicione seu nome e sobrenome em configurações para o nome sair no relatório
