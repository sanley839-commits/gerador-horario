import streamlit as st
import pandas as pd

# --- Configuração de Elite: Layout Largo ---
st.set_page_config(page_title="Horário Pro", layout="wide")

# Estilização extra para parecer mais com uma planilha
st.markdown("""
    <style>
    .stDataTable {
        border: 1px solid #d3d3d3;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📅 Horário Pro - Grade Quadriculada")
st.markdown("---")

with st.sidebar:
    st.header("⚙️ Painel de Controle")
    turmas_input = st.text_input("Turmas (Ex: 9A, 9B, 101)", "9A, 9B")
    
    # Campo para digitar as 8 aulas (ou mais)
    num_aulas = st.number_input("Total de aulas por dia", min_value=1, max_value=20, value=8)
    
    dias = ["SEGUNDA", "TERÇA", "QUARTA", "QUINTA", "SEXTA"]
    
    if st.button("🆕 Gerar Grade Quadriculada"):
        turmas = [t.strip() for t in turmas_input.split(",")]
        # Cria os nomes das linhas (Ex: SEGUNDA - 1ª Aula)
        slots = [f"{d} ({i+1}ª)" for d in dias for i in range(num_aulas)]
        
        # Cria a matriz (planilha)
        df_init = pd.DataFrame("", index=slots, columns=turmas)
        st.session_state['horario_data'] = df_init

# --- Exibição da Planilha ---
if 'horario_data' in st.session_state:
    st.subheader("📝 Edição Direta")
    st.caption("Podes copiar e colar dados de outras planilhas aqui dentro também!")
    
    # O data_editor cria o visual "quadriculado" e permite edição
    editado_df = st.data_editor(
        st.session_state['horario_data'],
        use_container_width=True, # Faz ocupar a tela toda
        num_rows="fixed",         # Trava o número de linhas para não bagunçar
        height=600                # Altura fixa para scroll se houver muitas aulas
    )
    
    st.session_state['horario_data'] = editado_df

    st.markdown("---")
    # Botão de exportação
    csv = editado_df.to_csv().encode('utf-8-sig') # utf-8-sig para o Excel abrir com acentos corretos
    st.download_button(
        label="📥 Descarregar Planilha (Excel/CSV)",
        data=csv,
        file_name="horario_escolar_pro.csv",
        mime="text/csv",
    )
else:
    st.warning("Define as turmas e o número de aulas na lateral e clica em 'Gerar Grade'.")
