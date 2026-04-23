import streamlit as st
import pandas as pd

# --- Configuração da Página ---
st.set_page_config(page_title="Horário Pro", layout="wide")

st.title("📅 Horário Pro - Gerador e Editor")
st.markdown("---")

# --- Interface de Entrada na Lateral ---
with st.sidebar:
    st.header("Configurações")
    turmas_input = st.text_input("Nomes das Turmas (separe por vírgula)", "9A, 9B")
    
    # AGORA VOCÊ DIGITA O NÚMERO (Ex: 8)
    num_aulas = st.number_input("Aulas por dia", min_value=1, max_value=15, value=8)
    
    dias = ["SEG", "TER", "QUA", "QUI", "SEX"]
    
    if st.button("Gerar Nova Grade"):
        # Cria a tabela com base no número digitado
        turmas = [t.strip() for t in turmas_input.split(",")]
        slots = [f"{d}-{i+1}ª" for d in dias for i in range(num_aulas)]
        df_init = pd.DataFrame("", index=slots, columns=turmas)
        st.session_state['horario_data'] = df_init

# --- Área de Edição ---
if 'horario_data' in st.session_state:
    st.subheader(f"📝 Grade Escolar ({num_aulas} aulas por dia)")
    st.info("Digite os nomes dos professores/disciplinas diretamente na tabela abaixo.")
    
    # Editor de dados de alta performance
    editado_df = st.data_editor(
        st.session_state['horario_data'],
        use_container_width=True,
        num_rows="fixed"
    )
    
    # Salva o que você digitou
    st.session_state['horario_data'] = editado_df

    st.markdown("---")
    csv = editado_df.to_csv().encode('utf-8')
    st.download_button("📥 Baixar Horário (Excel/CSV)", csv, "horario_pro.csv", "text/csv")
else:
    st.warning("Ajuste as turmas e o número de aulas ao lado, depois clique em 'Gerar Nova Grade'.")
