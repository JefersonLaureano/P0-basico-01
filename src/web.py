import streamlit as st

try:
    from src.client import chamar_modelo, validar_anotacao
except ImportError:
    from client import chamar_modelo, validar_anotacao

st.set_page_config(page_title="Extrator de Tarefas", page_icon="📋")

st.title("📋 Extrator de Tarefas de Reunião")
st.caption("Cole as anotações ou transcrição da reunião para extrair tarefas, responsáveis e prazos.")

anotacao = st.text_area(
    "Anotação da reunião:",
    height=180,
    placeholder="Ex: A Maria vai enviar o relatório financeiro até sexta às 18h e o Carlos vai agendar a apresentação."
)

if st.button("Extrair Tarefas", type="primary"):
    valido, erro = validar_anotacao(anotacao)
    if not valido:
        st.error(erro)
    else:
        with st.spinner("Analisando texto com o modelo..."):
            try:
                resultado = chamar_modelo(anotacao)
                st.subheader("Tarefas Identificadas")
                st.markdown(resultado)
            except Exception as e:
                st.error(f"Falha na operação: {e}")