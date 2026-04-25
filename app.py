import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client
import io

# --- 1. CONFIGURAÇÃO DE INTERFACE ---
st.set_page_config(
    page_title="Horário Pro | Digital",
    layout="wide",
    page_icon="📅",
    initial_sidebar_state="expanded"
)

# Estilização CSS para um visual "App"
st.markdown("""
    <style>
    /* Fundo e Container */
    .stApp {
        background-color: #0e1117;
    }
    
    /* Botões Personalizados */
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3em;
        font-weight: bold;
        transition: 0.3s;
        border: none;
    }
    
    /* Botão Salvar (Azul) */
    div[data-testid="stVerticalBlock"] > div:nth-child(1) button {
        background-color: #1E88E5;
        color: white;
    }
    
    /* Botão Excel (Verde) */
    div[data-testid="stVerticalBlock"] > div:nth-child(2) button {
        background-color: #217346;
        color: white;
    }

    /* Cards de Informação */
    .metric-card {
        background-color: #1d2127;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #30363d;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONEXÃO SUPABASE ---
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception:
    st.error("⚠️ Verifique as chaves nos Secrets do Streamlit.")
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

# --- 4. ÁREA DE ACESSO ---
if 'user' not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.write("") # Espaçador
        st.markdown("<h1 style='text-align: center; color: white;'>📅 Horário Pro</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #8b949e;'>Acesse sua grade escolar digital</p>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            email = st.text_input("E-mail")
            senha = st.text_input("Senha", type="password")
            if st.form_submit_button("Entrar no Painel"):
                try:
                    res = supabase.auth.sign_in_with_password({"email": email, "password": senha})
                    st.session_state.user = res.user
                    st.rerun()
                except:
                    st.error("Login inválido.")
else:
    # --- DASHBOARD LOGADO ---
    with st.sidebar:
        st.markdown("### 👤 Perfil")
        st.caption(f"Conectado como: \n{st.session_state.user.email}")
        st.divider()
        if st.button("🚪 Sair do Sistema"):
            st.session_state.user = None
            st.rerun()

    # Cabeçalho com métricas visuais
    st.title("🚀 Meu Horário Escolar")
    
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown('<div class="metric-card">🟢 <b>Status</b><br>Sincronizado</div>', unsafe_allow_html=True)
    with m2:
        hoje = datetime.now().weekday()
        aulas = "7 Aulas" if hoje in [0, 1, 4] else "8 Aulas"
        st.markdown(f'<div class="metric-card">📚 <b>Hoje</b><br>{aulas}</div>', unsafe_allow_html=True)
    with m3:
        st.markdown('<div class="metric-card">📅 <b>Ano</b><br>2026</div>', unsafe_allow_html=True)

    st.write("")
    
    # Tabela Editável
    if 'grade_editavel' not in st.session_state:
        st.session_state.grade_editavel = df_padrao.copy()

    grade_final = st.data_editor(
        st.session_state.grade_editavel,
        use_container_width=True,
        hide_index=False
    )

    # --- AÇÕES (SALVAR E EXCEL) ---
    st.divider()
    c_btn1, c_btn2, c_btn3 = st.columns([1, 1, 2])
    
    with c_btn1:
        if st.button("💾 Salvar na Nuvem"):
            try:
                supabase.table("grades").insert({
                    "user_id": st.session_state.user.id,
                    "nome_grade": f"Horario_{datetime.now().strftime('%d_%m_%Y')}",
                    "dados_grade": grade_final.to_json()
                }).execute()
                st.toast("Salvo com sucesso!", icon="✅")
            except Exception as e:
                st.error(f"Erro: {e}")

    with c_btn2:
        # Lógica Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            grade_final.to_excel(writer, index=True, sheet_name='Grade')
        excel_data = output.getvalue()
        
        st.download_button(
            label="📥 Baixar Excel (.xlsx)",
            data=excel_data,
            file_name=f"meu_horario_{datetime.now().strftime('%d_%m_%Y')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
