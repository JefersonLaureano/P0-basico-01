import sys

try:
    from src.client import chamar_modelo, validar_anotacao
except ImportError:
    from client import chamar_modelo, validar_anotacao


def iniciar_aplicacao():
    print("=" * 55)
    print("   Extrator de Tarefas e Compromissos de Reunião (P0)   ")
    print("=" * 55)
    print("Digite sua anotação ou digite 'sair' para encerrar.\n")

    while True:
        try:
            entrada = input("Anotação > ")

            if entrada.strip().lower() in ("sair", "exit", "quit"):
                print("\nEncerrando a aplicação. Até logo!")
                break

            valido, erro = validar_anotacao(entrada)
            if not valido:
                print(f"[ERRO] {erro}")
                continue

            print("\nProcessando com o modelo de linguagem...")
            resultado = chamar_modelo(entrada)

            print("\n" + "-" * 20 + " TAREFAS EXTRAÍDAS " + "-" * 20)
            print(resultado.strip())
            print("-" * 59 + "\n")

        except KeyboardInterrupt:
            print("\n\nExecução interrompida pelo usuário.")
            sys.exit(0)
        except Exception as e:
            print(f"\n[FALHA NA OPERAÇÃO]: {e}\n")


if __name__ == "__main__":
    iniciar_aplicacao()