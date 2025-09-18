# Lacrei Models

Pacote centralizado para os modelos de domínio (`models.py`) do ecossistema Lacrei.

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Linter: flake8](https://img.shields.io/badge/linter-flake8-green.svg)](https://flake8.pycqa.org/)
[![Built with: Poetry](https://img.shields.io/badge/built%20with-Poetry-20B2AA.svg)](https://python-poetry.org/)

---

## 🎯 Objetivo

Este repositório centraliza todos os modelos (`models.py`) do Django utilizados pelas aplicações do ecossistema Lacrei. A criação deste pacote visa atingir os seguintes objetivos:

* **Modularidade:** Desacoplar a camada de dados da lógica de aplicação, facilitando a manutenção.
* **Reuso:** Permitir que diferentes serviços consumam os mesmos modelos de forma consistente.
* **Governança:** Ter um ponto único de verdade para a estrutura de dados, controlando alterações de forma centralizada.
* **Consistência:** Garantir que a definição dos dados seja a mesma em todo o ecossistema.

Este pacote é uma dependência interna e privada, destinado a ser consumido por outras aplicações da Lacrei, como a `lacrei-api`.

## ⚙️ Instalação e Uso (Para Consumidores)

Para utilizar este pacote em outro projeto (como a `lacrei-api`), adicione-o como uma dependência usando Poetry.

**1. Configuração do Repositório Privado:**
Lembre-se que seu Poetry precisa estar configurado para acessar nosso repositório de pacotes privado (ex: GitHub Packages).

**2. Adicionando a Dependência:**
```bash
poetry add lacrei-models
```

**3. Exemplo de Uso no Código:**

Após a instalação, você pode importar os modelos usando o caminho absoluto do pacote:

```python
from lacrei_models.address.models import Address
from lacrei_models.lacreiid.models import User
```

## 🛠️ Ambiente de Desenvolvimento (Para Contribuidores)

Para trabalhar no desenvolvimento do lacrei-models, siga os passos abaixo. O projeto utiliza um Makefile para padronizar os comandos.

**1. Clone o Repositório:**

```bash
git clone git@github.com:Lacrei/lacrei-models.git
cd lacrei-models
```

**2. Instale as Dependências:**
O comando `make install` cuidará de tudo: instalar o Poetry, as dependências do projeto e os hooks de pre-commit.

```bash
make install
```

**3. Ative o Ambiente Virtual:**
Para rodar comandos diretamente, ative o shell do Poetry:

```bash
poetry shell
```

## ✅ Qualidade de Código e Testes

Utilizamos `black` para formatação, `flake8` para linting e `pre-commit` para garantir a qualidade antes de cada commit. O Makefile fornece atalhos para todas as tarefas de qualidade.

**Rodar os testes de importação:**

```bash
make test
```

**Formatar o código:**

```bash
make format
```

**Verificar erros e estilo:**

```bash
make lint
```

**Rodar todas as verificações em sequência (ideal antes de um PR):**

```bash
make quality
```

## 🚀 Publicando uma Nova Versão

O processo de lançamento de uma nova versão deve ser feito a partir da branch `main`, após o merge de um Pull Request.

**1. Atualize a Versão:**
Altere o número da versão no arquivo `pyproject.toml` (ex: de `0.1.0` para `0.1.1`).

**2. Faça o Commit da Mudança:**

```bash
git add pyproject.toml
git commit -m "chore: bump version to 0.1.1"
git push
```

**3. Crie a Tag Git:**
A tag deve corresponder à versão do pacote.

```bash
git tag v0.1.1
git push origin v0.1.1
```

**4. Publique o Pacote:**
Use o comando do Makefile para construir e publicar no nosso repositório privado.

```bash
make publish
```
