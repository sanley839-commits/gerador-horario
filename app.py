import streamlit as st
import pandas as pd

# --- Configuração da Página ---
st.set_page_config(page_title="Horário Pro", layout="wide")

st.title("📅 Horário Pro - Gerador e Editor")
st.markdown("---")

# --- Interface de Entrada ---
with st.sidebar:
    st.header("Configurações")
    turmas = st.text_input("Turmas (separe por vírgula)", "9A, 9B").split(",")
    dias = ["SEG", "TER", "QUA", "QUI", "SEX"]
    num_aulas = st.slider("Aulas por dia", 1, 6, 5)
    
    if st.button("Resetar/Gerar Base"):
        # Cria uma tabela vazia para começar
        slots = [f"{d}-{i+1}ª" for d in dias for i in range(num_aulas)]
        df_init = pd.DataFrame("", index=slots, columns=[t.strip() for t in turmas])
        st.session_state['horario_data'] = df_init

# --- Área de Edição ---
if 'horario_data' in st.session_state:
    st.subheader("📝 Edite sua Grade Horária")
    st.info("Clique em qualquer célula para digitar ou alterar o professor/disciplina.")
    
    # O componente 'data_editor' permite que você mude os valores na hora
    editado_df = st.data_editor(
        st.session_state['horario_data'],
        use_container_width=True,
        num_rows="fixed"
    )
    
    # Salvar alterações
    st.session_state['horario_data'] = editado_df

    # --- Exportação ---
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        csv = editado_df.to_csv().encode('utf-8')
        st.download_button("📥 Baixar em Excel/CSV", csv, "horario_escolar.csv", "text/csv")
    with col2:
        if st.button("Limpar Tudo"):
            del st.session_state['horario_data']
            st.rerun()
else:
    st.warning("Ajuste as turmas na lateral e clique em 'Gerar Base' para começar.")
