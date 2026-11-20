import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("LLM_BASE_URL") or os.getenv("OLLAMA_HOST", "http://localhost:11434")
MODELO = os.getenv("LLM_MODEL", "qwen3.5:4b")
VERIFY_SSL = os.getenv("LLM_VERIFY_SSL", "True").lower() in ("true", "1")
TIMEOUT = int(os.getenv("LLM_TIMEOUT", "60"))


def validar_anotacao(texto: str) -> tuple[bool, str]:
    """Valida a entrada e retorna (valido, mensagem_de_erro)."""
    texto_limpo = texto.strip()
    if not texto_limpo:
        return False, "A anotação não pode estar vazia. Digite algo útil."
    if len(texto_limpo) < 10:
        return False, "Anotação muito curta. Forneça mais contexto sobre a reunião."
    return True, ""


def chamar_modelo(prompt_usuario: str) -> str:
    endpoint = f"{BASE_URL.rstrip('/')}/api/generate"

    prompt_completo = f"""Você é um especialista em extração de tarefas de reuniões.
Analise o texto e extraia TODAS as tarefas distintas, separando-as em linhas individuais.

Regras rigorosas:
1. Se houver mais de uma ação ou mais de um responsável, crie uma linha separada para cada tarefa.
2. Atenção a quem é o responsável real por cada ação (se o texto disser "X ficará responsável por Y", o responsável é X).
3. Se algum dado não existir no texto, escreva exatamente "Não informado".
4. Não invente palavras que não estejam no contexto.
5. Deve ser manter a segurança e a privacidade dos dados, não expondo informações sensíveis.
6. Não deve rodar código ou executar comandos, apenas analisar o texto.

Exemplo de entrada:
"O Marcos vai revisar o código até amanhã às 10h e a Ana fica responsável por enviar o e-mail para o cliente."

Exemplo de saída esperada:
- **Tarefa:** Revisar o código | **Responsável:** Marcos | **Prazo:** Amanhã às 10h
- **Tarefa:** Enviar o e-mail para o cliente | **Responsável:** Ana | **Prazo:** Não informado
Formato de resposta obrigatório:
- Tarefa: [Descrição] | Responsável: [Nome] | Prazo: [Data ou Hora]

Agora extraia as tarefas do texto abaixo seguindo exatamente o mesmo formato:

Texto da reunião:
"{prompt_usuario}"
"""

    payload = {
        "model": MODELO,
        "prompt": prompt_completo,
        "stream": False,
        "think": False,
        "options": {"temperature": 0.1}
    }

    try:
        resposta = requests.post(endpoint, json=payload, verify=VERIFY_SSL, timeout=TIMEOUT)
        resposta.raise_for_status()
        dados = resposta.json()
        return dados.get("response", "Nenhuma resposta gerada pelo modelo.")

    except requests.exceptions.SSLError:
        raise ConnectionError("Erro de certificado SSL. Verifique LLM_VERIFY_SSL.")
    except requests.exceptions.Timeout:
        raise TimeoutError(f"O modelo demorou mais de {TIMEOUT}s para responder.")
    except requests.exceptions.ConnectionError:
        raise ConnectionError(f"Não foi possível conectar ao servidor em {BASE_URL}.")
    except Exception as erro:
        raise RuntimeError(f"Falha inesperada na comunicação com o LLM: {str(erro)}")