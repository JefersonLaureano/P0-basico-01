# Extrator de Tarefas de Reunião com LLM

Aplicação web desenvolvida em Python e Streamlit para extrair tarefas, responsáveis e prazos de anotações ou transcrições de reuniões utilizando Modelos de Linguagem (LLMs). O cliente suporta tanto servidores Ollama locais (`/api/generate`) quanto APIs compatíveis com o padrão OpenAI (`/v1/chat/completions`), como o ambiente institucional Devel LLM.

---

## 📋 Requisitos de Ambiente

- **Linguagem:** Python 3.11 ou superior
- **Dependências:** Listadas em `requirements.txt` (`streamlit`, `requests`, `python-dotenv`, `pytest`)
- **Provedor LLM (execução local):** Ollama em execução (`http://localhost:11434`) com o modelo `qwen3.5:4b`
- **Provedor LLM (ambiente institucional):** Devel LLM (`https://llm-internal.softex:9001/v1`) com o modelo `qwen3.5:9b-q4_K_M`
- **Containerização (opcional):** Docker Engine / Docker Desktop

---

## ⚙️ Variáveis de Ambiente

Copie o arquivo de exemplo para criar sua configuração local:

```bash
cp .env.example .env
```

| Variável         | Descrição                             | Valor Padrão (Local)     | Valor Institucional (Devel)        |
| :--------------- | :------------------------------------ | :----------------------- | :--------------------------------- |
| `LLM_BASE_URL`   | URL base do servidor LLM              | `http://localhost:11434` | `https://llm-internal.softex:9001` |
| `LLM_MODEL`      | Identificador do modelo ativo         | `qwen3.5:4b`             | `qwen3.5:9b-q4_K_M`                |
| `LLM_VERIFY_SSL` | Verificação de certificado SSL        | `True`                   | `False`                            |
| `LLM_TIMEOUT`    | Tempo limite da requisição (segundos) | `90`                     | `90`                               |

---

## 🚀 Instalação e Execução (Ambiente Limpo)

### Opção 1: Execução Local com Python

1. **Clone o repositório e acesse a pasta:**

   ```bash
   git clone [https://github.com/JefersonLaureano/P0-basico-01.git](https://github.com/JefersonLaureano/P0-basico-01.git)
   cd P0-basico-01
   ```

2. **Crie e ative o ambiente virtual:**
   - **Windows (PowerShell):**
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```
   - **Linux / macOS:**
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

3. **Instale as dependências:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Baixe o modelo local no Ollama:**

   ```bash
   ollama pull qwen3.5:4b
   ```

5. **Execute a aplicação web:**
   ```bash
   streamlit run src/web.py
   ```
   Acesse no navegador: `http://localhost:8501`.

### Opção 2: Execução via Docker

1. **Construa a imagem:**

   ```bash
   docker build -t extrator-tarefas:latest .
   ```

2. **Inicie o container conectando ao Ollama local:**
   ```bash
   docker run -p 8080:80 \
     -e LLM_BASE_URL=[http://host.docker.internal:11434](http://host.docker.internal:11434) \
     -e LLM_MODEL=qwen3.5:4b \
     extrator-tarefas:latest
   ```
   Acesse no navegador: `http://localhost:8080`.

---

## 🧪 Como Testar

Os testes automatizados validam as regras de entrada (texto vazio, curto ou válido), tratamento de exceções (SSL, timeout, conexão) e o fallback automático entre `/api/generate` e `/v1/chat/completions`:

```bash
pytest -v
```

---

## 📁 Estrutura do Repositório

```text
├── docs/
│   ├── relatorio.md          # Relatório principal (decisões técnicas, evidências e registro de uso de IA)
│   └── evidencias/           # Capturas de tela da execução local, testes e deploy no Devel LLM
├── src/
│   ├── client.py             # Validação de entrada e integração dual (Ollama / OpenAI API)
│   └── app.py                # Interface básica para rodar no terminal
│   └── web.py                # Interface web em Streamlit
├── tests/
│   └── test_client.py        # Casos de teste automatizados (pytest)
├── .dockerignore             # Exclusão de arquivos locais do build Docker
├── .env.example              # Modelo de variáveis de ambiente (sem segredos)
├── .gitignore                # Exclusão de .env, .venv, __pycache__ e arquivos .tar
├── Dockerfile                # Definição de imagem para deploy em container (porta 80)
├── requirements.txt          # Dependências do projeto
└── README.md                 # Instruções de reprodutibilidade e acesso aos artefatos
```

---

## ⚠️ Limitações Conhecidas

- **Tempo de inicialização no ambiente institucional:** No portal Devel LLM, o servidor interno entra em hibernação e exige de 1 a 2 minutos após o início do container para responder às primeiras chamadas.
- **Certificado SSL autoassinado:** O endpoint interno (`https://llm-internal.softex:9001`) requer `LLM_VERIFY_SSL=False` na rede isolada do ambiente.
- **Ambiguidade textual:** Anotações sem verbos de ação claros ou com referências implícitas podem resultar na atribuição de `"Não informado"` para responsável ou prazo.
- **Ausência de persistência:** Os resultados são processados em sessão e não são gravados em banco de dados.

---

## 🔗 Artefatos de Avaliação

- **Relatório Principal e Registros** [`docs/relatorio.md`](docs/relatorio.md)
- **Evidências de Execução:** [`docs/evidencias/`](docs/evidencias/)
- **Vídeo de Demonstração:** _[Inserir link do YouTube/Drive aqui antes do push final]_
- **Releases / Tags:** Consulte a aba _Releases_ do repositório (`v0.1.0-p0` / tags dos três níveis conforme cronograma).
