import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client
import io  # Necessário para converter o arquivo para baixar

# --- 1. CONFIGURAÇÃO VISUAL ---
st.set_page_config(
    page_title="Horário Pro | Digital",
    layout="wide",
    page_icon="📅"
)

# Estilo CSS Profissional
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
    }
    .download-btn {
        background-color: #217346 !important; /* Cor do Excel */
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONEXÃO SUPABASE ---
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception:
    st.error("⚠️ Erro nas chaves do Supabase.")
    st.stop()

# --- 3. DADOS POR EXTENSO ---
dados_reais = {
    "Segunda-feira": ["Inglês", "Geografia", "Matemática", "Matemática", "Estudo Orientado", "Ciências", "Matemática", "-"],
    "Terça-feira": ["Português", "Geografia", "Artes", "Português", "Inglês", "Inglês", "Int. Metodologia Científica", "-"],
    "Quarta-feira": ["Português", "Ciências", "Formação Cidadã", "Aprofundamento Oratória", "Matemática", "Matemática", "Projeto de Vida", "Projeto de Vida"],
    "Quinta-feira": ["Geografia", "Português", "Português", "Português", "Matemática", "Matemática", "Práticas Experimentais", "História"],
    "Sexta-feira": ["História", "Geografia", "Eletivas", "Eletivas", "Educação Física", "Educação Física", "História", "-"]
}
df_padrao = pd.DataFrame(dados_reais, index=[f"{i+1}º Horário" for i in range(8)])

# --- 4. LÓGICA DE LOGIN ---
if 'user' not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    st.title("📅 Horário Pro")
    email = st.sidebar.text_input("E-mail")
    senha = st.sidebar.text_input("Senha", type="password")
    if st.sidebar.button("Entrar"):
        try:
            res = supabase.auth.sign_in_with_password({"email": email, "password": senha})
            st.session_state.user = res.user
            st.rerun()
        except: st.sidebar.error("Erro no login.")
else:
    # --- INTERFACE LOGADA ---
    st.title("📝 Minha Grade Escolar")
    
    if 'grade_editavel' not in st.session_state:
        st.session_state.grade_editavel = df_padrao.copy()

    # Editor de Dados
    grade_final = st.data_editor(st.session_state.grade_editavel, use_container_width=True)

    # --- FUNÇÃO DE DOWNLOAD EXCEL ---
    def converter_para_excel(df):
        output = io.BytesIO()
        # Usa o motor 'openpyxl' para criar o .xlsx
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=True, sheet_name='Meu_Horario')
        return output.getvalue()

    excel_data = converter_para_excel(grade_final)

    # --- BOTÕES DE AÇÃO ---
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💾 Salvar na Nuvem"):
            try:
                supabase.table("grades").insert({
                    "user_id": st.session_state.user.id,
                    "nome_grade": f"Grade_{datetime.now().strftime('%d/%m/%Y')}",
                    "dados_grade": grade_final.to_json()
                }).execute()
                st.success("Sincronizado!")
            except Exception as e: st.error(f"Erro: {e}")

    with col2:
        # Botão Nativo de Download do Streamlit
        st.download_button(
            label="📥 Baixar em Excel (.xlsx)",
            data=excel_data,
            file_name=f"meu_horario_{datetime.now().strftime('%d_%m_%Y')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    if st.sidebar.button("Sair"):
        st.session_state.user = None
        st.rerun()
