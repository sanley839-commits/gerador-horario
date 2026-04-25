import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client
import io

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Horário Pro | Digital", layout="wide", page_icon="📅")

# --- 2. DEFINIÇÃO DOS HORÁRIOS (CÁLCULO EXATO) ---
horarios_duracao = [
    "07:30 - 08:25", "08:25 - 09:20", "09:40 - 10:35", "10:35 - 11:30",
    "13:00 - 13:55", "13:55 - 14:50", "15:10 - 16:05", "16:05 - 17:00"
]

indice_aulas = [f"{i+1}ª Aula ({horarios_duracao[i]})" for i in range(8)]

# Dados reais conforme sua foto e ajustes
dados_reais = {
    "Segunda-feira": ["Inglês", "Geografia", "Matemática", "Matemática", "Estudo Orientado", "Ciências", "Matemática", "-"],
    "Terça-feira": ["Português", "Geografia", "Artes", "Português", "Inglês", "Inglês", "Int. Metodologia Científica", "-"],
    "Quarta-feira": ["Português", "Ciências", "Formação Cidadã", "Aprofundamento Oratória", "Matemática", "Matemática", "Projeto de Vida", "Projeto de Vida"],
    "Quinta-feira": ["Geografia", "Português", "Português", "Português", "Matemática", "Matemática", "Práticas Experimentais", "História"],
    "Sexta-feira": ["História", "Geografia", "Eletivas", "Eletivas", "Educação Física", "Educação Física", "História", "-"]
}

df_padrao = pd.DataFrame(dados_reais, index=indice_aulas)

# --- 3. CONEXÃO SUPABASE ---
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except:
    st.error("Chaves do Supabase não encontradas.")
    st.stop()

# --- 4. INTERFACE ---
if 'user' not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    st.title("📅 Horário Pro")
    with st.sidebar:
        email = st.text_input("E-mail")
        senha = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": senha})
                st.session_state.user = res.user
                st.rerun()
            except: st.error("Erro no login.")
else:
    st.title("📝 Minha Grade de Aulas")
    
    if 'grade_editavel' not in st.session_state:
        st.session_state.grade_editavel = df_padrao.copy()

    # Editor da Tabela
    grade_final = st.data_editor(st.session_state.grade_editavel, use_container_width=True)

    # --- AÇÕES ---
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💾 Salvar na Nuvem"):
            try:
                supabase.table("grades").insert({
                    "user_id": st.session_state.user.id,
                    "nome_grade": f"Grade_{datetime.now().strftime('%d/%m/%Y')}",
                    "dados_grade": grade_final.to_json()
                }).execute()
                st.success("Sincronizado com sucesso!")
            except Exception as e: st.error(f"Erro ao salvar: {e}")

    with col2:
        # Gerar Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            grade_final.to_excel(writer, index=True, sheet_name='Horário Escolar')
        
        st.download_button(
            label="📥 Baixar Planilha Excel (.xlsx)",
            data=output.getvalue(),
            file_name=f"grade_escolar_{st.session_state.user.email.split('@')[0]}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    if st.sidebar.button("Sair"):
        st.session_state.user = None
        st.rerun()
