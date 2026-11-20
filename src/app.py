import streamlit as st

try:
    from src.client import extrair_tarefas
except ImportError:
    from client import extrair_tarefas

st.set_page_config(page_title="Extrator de Tarefas", page_icon="📋")

st.title("📋 Extrator de Tarefas de Reunião")
st.caption("Cole as anotações ou transcrição da reunião para extrair tarefas, responsáveis e prazos.")

anotacao = st.text_area(
    "Anotação da reunião:",
    height=180,
    placeholder="Ex: A Maria vai enviar o relatório financeiro até sexta às 18h e o Carlos vai agendar a reunião de alinhamento."
)

if st.button("Extrair Tarefas", type="primary"):
    texto_limpo = anotacao.strip()
    
    if not texto_limpo:
        st.error("A anotação não pode estar vazia.")
    elif len(texto_limpo) < 10:
        st.warning("Anotação muito curta. Forneça mais contexto sobre a reunião.")
    else:
        with st.spinner("Analisando texto com o modelo..."):
            try:
                resultado = extrair_tarefas(texto_limpo)
                st.subheader("Tarefas Identificadas")
                st.markdown(resultado)
            except Exception as e:
                st.error(f"Falha na operação: {e}")