# py-log-mjk

### **Um pacote de logging completo e profissional para aplicações Python.**

[![PyPI version](https://badge.fury.io/py/py-log-mjk.svg)](https://badge.fury.io/py/py-log-mjk)
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)

## **Visão Geral**

O `py-log-mjk` é uma solução de logging robusta e fácil de usar para projetos em Python. Ele foi projetado para ser configurado de forma declarativa, permitindo que você personalize o comportamento do logging sem precisar alterar o código da sua aplicação.

Com o `py-log-mjk`, você obtém:

- **Configuração Simples**: Gerenciamento de configurações através de um arquivo JSON.
- **Formatação Rica**: Saída de logs colorida e formatada com a biblioteca **`rich`**.
- **Logs Estruturados**: Logs em formato JSON para facilitar o monitoramento em ferramentas como o ELK Stack ou o Datadog.
- **Filtragem Avançada**: Controle de nível de log por módulo.
- **Processamento Assíncrono**: Desempenho otimizado com `QueueHandler` para processar logs em segundo plano.

## **Instalação**

Recomendamos usar o **Poetry** para gerenciar as dependências e o ambiente virtual.

```bash
# Adicione a biblioteca ao seu projeto
poetry add py-log-mjk

# Ou, se estiver desenvolvendo o pacote localmente, instale-o em modo editável
poetry install

Uso Básico
Basta importar a função get_logger e começar a usar.

# app.py
from py_log_mjk import get_logger

# Obtenha o logger. A configuração é automática.
logger = get_logger(__name__)

logger.info("A aplicação foi iniciada com sucesso!")
logger.debug("Esta é uma mensagem de depuração.")
logger.error("Ops, algo deu errado!", exc_info=True)

```

## **Créditos**
Este projeto é fruto de uma aula sobre logging do prof. Luiz Otávio Miranda!

```bash
Estude, copie, adapte, melhore e compartilhe! ☕

```