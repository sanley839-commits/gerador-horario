import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from supabase import create_client, Client

# --- Inicialização do Banco de Dados ---
# Certifique-se de que as chaves estão nos "Secrets" do Streamlit!
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception:
    st.error("Erro: As chaves do Supabase não foram encontradas nos Secrets.")
    st.stop()

st.set_page_config(page_title="Horário Pro", layout="wide")

# --- Funções de Apoio ---
def calcular_horarios(num_aulas):
    horarios = []
    atual = datetime.strptime("07:30", "%H:%M")
    for i in range(1, num_aulas + 1):
        inicio = atual.strftime("%H:%M")
        fim = (atual + timedelta(minutes=55)).strftime("%H:%M")
        horarios.append(f"{i}ª Aula ({inicio}-{fim})")
        proximo = atual + timedelta(minutes=55)
        if i == 2: proximo += timedelta(minutes=20)   # Intervalo Manhã
        elif i == 4: proximo += timedelta(minutes=90) # Almoço
        elif i == 6: proximo += timedelta(minutes=20) # Intervalo Tarde
        atual = proximo
    return horarios

# --- Sistema de Login ---
if 'user' not in st.session_state:
    st.session_state.user = None

def autenticacao():
    st.sidebar.title("🔐 Acesso")
    aba = st.sidebar.radio("Escolha", ["Login", "Criar Conta"])
    email = st.sidebar.text_input("E-mail")
    senha = st.sidebar.text_input("Senha", type="password")
    
    if aba == "Criar Conta":
        if st.sidebar.button("Registar"):
            try:
                supabase.auth.sign_up({"email": email, "password": senha})
                st.sidebar.success("Conta criada! Agora faça Login.")
            except Exception as e: st.sidebar.error(f"Erro: {e}")
    else:
        if st.sidebar.button("Entrar"):
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": senha})
                st.session_state.user = res.user
                st.rerun()
            except Exception: st.sidebar.error("Dados incorretos.")

# --- Conteúdo Principal ---
if st.session_state.user is None:
    st.title("📅 Horário Pro")
    st.info("Faça login para criar e salvar seu histórico escolar.")
    autenticacao()
else:
    st.sidebar.write(f"Usuário: {st.session_state.user.email}")
    if st.sidebar.button("Sair"):
        st.session_state.user = None
        st.rerun()

    st.title("📝 Minha Planilha de Aulas")
    
    dias = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]
    grade_referencia = {}
    
    # Criar a lógica das aulas conforme os seus dias
    for dia in dias:
        n = 7 if dia in ["Segunda", "Terça", "Sexta"] else 8
        lista = calcular_horarios(n)
        if n == 7: lista.append("---") # Espaço vazio para alinhar a tabela
        grade_referencia[dia] = lista

    df_ref = pd.DataFrame(grade_referencia, index=[f"{i+1}º Horário" for i in range(8)])
    
    st.write("🕒 **Horários de Referência:**")
    st.table(df_ref)
    
    st.markdown("---")
    st.subheader("✍️ Edite sua Grade Abaixo")
    
    # Tabela editável (Planilha Quadriculada)
    if 'dados_atuais' not in st.session_state:
        st.session_state.dados_atuais = pd.DataFrame("", index=df_ref.index, columns=dias)

    grade_editavel = st.data_editor(st.session_state.dados_atuais, use_container_width=True)

    if st.button("💾 Salvar no Histórico"):
        # Lógica para enviar para o Supabase (Tabela 'grades')
        dados_json = grade_editavel.to_json()
        try:
            supabase.table("grades").insert({
                "user_id": st.session_state.user.id,
                "dados_grade": dados_json,
                "nome_grade": f"Grade_{datetime.now().strftime('%Y-%m-%d')}"
            }).execute()
            st.success("Histórico salvo com sucesso!")
        except Exception as e:
            st.error(f"Erro ao salvar: {e}")
