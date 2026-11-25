import pytest
import requests
from unittest.mock import patch, MagicMock
from src.client import validar_anotacao, chamar_modelo


def test_validar_anotacao_vazia():
    valido, erro = validar_anotacao("   ")
    assert valido is False
    assert "vazia" in erro.lower()


def test_validar_anotacao_curta():
    valido, erro = validar_anotacao("Reunião")
    assert valido is False
    assert "curta" in erro.lower()


def test_validar_anotacao_valida():
    valido, erro = validar_anotacao("O Ricardo vai migrar o banco até segunda às 14h.")
    assert valido is True
    assert erro == ""


@patch("src.client.requests.post")
def test_chamar_modelo_ollama_sucesso(mock_post):
    resp_200 = MagicMock(status_code=200)
    resp_200.json.return_value = {
        "response": "- Tarefa: Migrar banco | Responsável: Ricardo | Prazo: Segunda às 14h"
    }
    mock_post.return_value = resp_200

    resultado = chamar_modelo("O Ricardo vai migrar o banco até segunda às 14h.")
    assert "Ricardo" in resultado
    assert mock_post.call_count == 1


@patch("src.client.requests.post")
def test_chamar_modelo_fallback_openai_v1(mock_post):
    resp_404 = MagicMock(status_code=404)
    resp_200 = MagicMock(status_code=200)
    resp_200.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": "- Tarefa: Enviar relatório | Responsável: João | Prazo: Amanhã"
                }
            }
        ]
    }
    mock_post.side_effect = [resp_404, resp_200]

    resultado = chamar_modelo("O João vai enviar o relatório amanhã.")
    assert "João" in resultado
    assert mock_post.call_count == 2


@patch("src.client.requests.post")
def test_chamar_modelo_erro_conexao(mock_post):
    mock_post.side_effect = requests.exceptions.ConnectionError("Falha de rede")
    with pytest.raises(ConnectionError):
        chamar_modelo("Texto válido para testar falha de conexão com o servidor.")