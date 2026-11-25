# Relatório Técnico - Extrator de Tarefas e Compromissos de Reunião (P0)

---

## 1. O que Faz o Projeto e Qual o Seu Objetivo?

O **Extrator de Tarefas e Compromissos de Reunião** é uma aplicação em Python projetada para processar anotações, atas ou transcrições livres de reuniões e convertê-las em uma lista estruturada e padronizada de tarefas operacionais.

### Problema Resolvido:
Em ambientes corporativos e de projetos, reuniões geram anotações dispersas, informais e não estruturadas. Isso frequentemente leva a omissões de prazos, incertezas sobre responsabilidades e retrabalho.

### Solução Entregue:
A aplicação realiza a análise semântica do texto através de um Modelo de Linguagem de Grande Porte (LLM) — local ou hospedado na plataforma **Devel LLM Portal (Softex)** —, isolando e extraindo:
- **Descrição clara da tarefa**
- **Responsável designado** (ou indicação de *"Não informado"*)
- **Prazo estipulado** (ou indicação de *"Não informado"*)

A saída é gerada estritamente no formato padronizado:
```text
- Tarefa: [Descrição] | Responsável: [Nome] | Prazo: [Data ou Hora]
```

O projeto oferece suporte duplo de interface: **Linha de Comando (CLI)** para execuções rápidas e **Interface Web (Streamlit)** para interação visual no navegador dentro de container Docker.

---

## 2. Escolhas Técnicas de Cada Parte do Projeto e Seus Porquês

A arquitetura do projeto foi estruturada visando modularidade, resiliência, boas práticas de engenharia de software e atendimento rigoroso aos requisitos da plataforma de implantação.

### 2.1. Estrutura Modular e Separação de Responsabilidades
O código foi desacoplado em camadas bem definidas:
- **`src/client.py` (Lógica de Negócio e Conectividade)**: Centraliza a validação de regras de entrada, a formatação de prompts, a comunicação HTTP com a API da LLM e o tratamento de erros.
- **`src/app.py` (Interface CLI)**: Entrada via terminal, permitindo testes ágeis sem overhead gráfico.
- **`src/web.py` (Interface Web - Streamlit)**: Interface gráfica intuitiva para o usuário final no navegador.
- **`tests/test_cliente.py` (Testes Automatizados)**: Garantia de qualidade contínua e cobertura das funções centrais.

> **Por quê?** O princípio de responsabilidade única (Single Responsibility Principle) permite alterar ou trocar a interface visual sem encostar na lógica de integração da IA, além de viabilizar testes unitários automatizados sem subir servidor web.

---

### 2.2. Camada de Integração com LLM (`src/client.py`)

#### A. Estratégia de Rota Dupla com Fallback Automático
O cliente implementa comunicação resiliente:
1. Primeira tentativa na rota nativa do **Ollama** (`/api/generate`), comumente utilizada no desenvolvimento local.
2. Caso o endpoint retorne `404 Not Found`, o cliente realiza automaticamente o fallback para a rota padrão **OpenAI-compatible** (`/v1/chat/completions`), utilizada por diversos gateways da plataforma Devel/Softex.
> **Por quê?** Garante que o mesmo código funcione de forma transparente tanto na máquina do desenvolvedor (Ollama local) quanto no servidor de produção da Softex sem requerer alterações de código.

#### B. Gestão de Certificado SSL e Segurança de Rede
Foi configurado `verify=VERIFY_SSL` e supressão de alertas com `urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)`.
> **Por quê?** A infraestrutura interna da Softex (`https://llm-internal.softex:9001`) opera sob um certificado SSL autogerado/autoassinado. A verificação estrita de SSL causaria falha imediata de handshake (`SSLError`).

#### C. Engenharia de Prompt e Temperatura
O prompt utiliza a técnica **Few-Shot Prompting**, incluindo instruções de sistema restritivas (*"Não invente"*, *"Separe múltiplas tarefas em linhas individuais"*, *"Se não informado, escreva Não informado"*) e exemplos diretos de entrada e saída. A temperatura foi fixada em `0.1`.
> **Por quê?** Tarefas de extração exigem precisão cirúrgica e determinismo. Uma temperatura baixa (0.1) reduz drasticamente alucinações, enquanto os exemplos instruem o modelo a seguir rigidamente a sintaxe exigida.

#### D. Validação Preventiva de Entrada (`validar_anotacao`)
Antes de despachar qualquer requisição à rede, o texto é higienizado (`strip()`), checando se está vazio ou excessivamente curto (< 10 caracteres).
> **Por quê?** Economiza requisições desnecessárias, poupa latência de rede e evita sobrecarga de processamento na LLM com entradas vazias ou sem contexto.

---

### 2.3. Interfaces com o Usuário

- **Streamlit (`src/web.py`)**:
  - Biblioteca Python moderna para criação de dashboards e web apps orientados a dados.
  - Implementa caixa de texto expansível (`st.text_area`), botão de ação primário, feedback visual de processamento (`st.spinner`) e blocos de alerta amigáveis (`st.error`).
  > **Por quê?** Reduz a complexidade de desenvolvimento front-end (dispensando HTML/CSS/JavaScript complexos) e atende perfeitamente ao formato de demonstração pública do Devel LLM Portal.

- **CLI (`src/app.py`)**:
  - Loop iterativo no terminal com comandos de controle (`sair`, `exit`) e captura limpa de interrupções de teclado (`KeyboardInterrupt`).
  > **Por quê?** Oferece um caminho de execução leve, ideal para ambientes de servidor sem navegador ou testes rápidos de terminal.

---

### 2.4. Qualidade e Testes Automatizados (`tests/test_cliente.py`)

- Utilização do framework **`pytest`** em conjunto com **`unittest.mock.patch`**.
- Casos de teste cobrem:
  - Validação de anotação vazia (deve reprovar).
  - Validação de anotação com tamanho insuficiente (deve reprovar).
  - Validação de anotação completa (deve aprovar).
  - Chamada bem-sucedida via endpoint nativo Ollama (mock de resposta 200).
  - Mecanismo de fallback para a rota OpenAI `/v1/chat/completions` quando a primeira rota retorna 404.
  - Tratamento correto de exceção de falha de conexão (`ConnectionError`).
> **Por quê?** Testes com mocks são rápidos, determinísticos e não consomem recursos de rede nem exigem que o servidor da LLM esteja online para validar a integridade do código.

---

### 2.5. Conteinerização e Empacotamento Docker (`dockerfile`)

- **Imagem Base**: `python:3.11-slim`.
- **Instalação Enxuta**: `pip install --no-cache-dir -r requirements.txt`.
- **Porta**: Exposição na porta `80`.
- **Comando de Execução**: `streamlit run src/web.py --server.port=80 --server.address=0.0.0.0 --server.headless=true --browser.gatherUsageStats=false`.
- **Exportação TAR**: Formato `<identificador_aluno>.tar` (ex: `aluno.tar`), seguindo a regra de nomenclatura da plataforma de utilizar o identificador único sem caracteres especiais.
> **Por quê?** 
> 1. A plataforma Softex estipula um limite estrito de **até 1024 MB (1 GB)** por imagem de container. A imagem slim com cache limpo mantém o pacote compacto e veloz no carregamento.
> 2. As flags `--server.headless=true` e `--browser.gatherUsageStats=false` impedem que o Streamlit trave aguardando interações manuais de terminal ou envio de telemetria.

---

### 2.6. Segurança e Conformidade (12-Factor App)

- **`python-dotenv`**: Configurações (`BASE_URL`, `MODELO`, `VERIFY_SSL`, `TIMEOUT`) são lidas de variáveis de ambiente.
- **`.gitignore`**: Proteção ativa contra vazamento de credenciais locais (`.env` e `replace_keys.txt`), isolando-os do repositório remoto.
- **`.env.example`**: Fornecido como documentação pública das variáveis necessárias.
> **Por quê?** Segue o padrão da indústria para aplicações seguras e portáveis, permitindo alternar ambientes (local vs. produção) sem alterar uma única linha de código.

---

## 3. Declaração do Uso de Inteligência Artificial

Em conformidade com as diretrizes acadêmicas e de integridade do projeto, declara-se que ferramentas de Inteligência Artificial Generativa (assistente de desenvolvimento **Antigravity / Gemini**) foram utilizadas de forma colaborativa durante o ciclo de desenvolvimento da seguinte forma:

### Onde e Como a IA foi Utilizada:
1. **Concepção Arquitetural**: Discussão e definição da estrutura de diretórios (`src`, `tests`, `docs`) e do padrão de projeto com separação estrita entre cliente de API (`client.py`) e visualização (`web.py`/`app.py`).
2. **Refinamento da Engenharia de Prompts**: Apoio na elaboração e ajuste das diretrizes de Few-Shot prompting para que o modelo retornasse estritamente o formato delimitado por barras verticais (`|`), eliminando prolixidade e alucinações.
3. **Resiliência de Integração**: Sugestão da implementação de fallback duplo entre a rota Ollama (`/api/generate`) e a rota OpenAI (`/v1/chat/completions`), solucionando divergências entre o Ollama local e o gateway da Softex.
4. **Construção de Testes Unitários**: Auxílio na estruturação dos cenários de teste com `unittest.mock` para simular retornos HTTP e falhas de rede de forma determinística no `pytest`.
5. **Diagnóstico da Plataforma e Otimização do Docker**: Apoio na interpretação das regras do documento *Guia da plataforma - Devel LLM Portal*, com foco na mitigação de falhas de SSL interno, respeito ao limite de 1024 MB na imagem e parametrização correta da execução headless do Streamlit.

### Responsabilidade Humana e Validação:
Todas as sugestões de código, escolhas técnicas, arquivos de configuração e comandos foram ativamente revisados, implementados, testados localmente e validados pelo desenvolvedor responsável, que compreende e atesta a finalidade e a correção de cada componente entregue.

---

## 4. Conclusão

O projeto atinge plenamente os objetivos propostos para o nível P0: entrega uma solução funcional de ponta a ponta, com código testado e aprovado (100% de sucesso nos testes unitários), documentado, seguro contra vazamento de chaves e pronto para operação em nuvem via container Docker no Devel LLM Portal.
