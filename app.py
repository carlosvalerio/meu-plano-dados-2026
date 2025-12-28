import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import google.generativeai as genai


# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="DataPath AI 2026", layout="wide", page_icon="🚀")

# --- BANCO DE DADOS (SQLite) ---
def init_db():
    conn = sqlite3.connect('datapath.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS roda_vida (
            area TEXT PRIMARY KEY,
            nota INTEGER
        )
    ''')
    areas = ['Saúde', 'Intelectual', 'Profissional', 'Financeiro', 'Família', 'Social', 'Lazer', 'Espiritual']
    for area in areas:
        cursor.execute('INSERT OR IGNORE INTO roda_vida (area, nota) VALUES (?, ?)', (area, 0))
    conn.commit()
    return conn

conn = init_db()

def update_nota(area, nota):
    cursor = conn.cursor()
    # O comando correto precisa do SET para atribuir o novo valor
    cursor.execute('UPDATE roda_vida SET nota = ? WHERE area = ?', (nota, area))
    conn.commit()

def get_notas():
    df = pd.read_sql_query("SELECT * FROM roda_vida", conn)
    return dict(zip(df['area'], df['nota']))

# --- INTEGRAÇÃO COM IA (Gemini) ---
# Aqui ele tenta pegar a chave dos "Secrets" do Streamlit Cloud ou do código local
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    API_KEY = "SUA_CHAVE_AQUI_PARA_TESTE_LOCAL"

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-pro')

# --- INTERFACE FRONTEND ---
st.title("🚀 DataPath AI: Seu Mentor de Dados 2026")
st.markdown("Transformando seus estudos de **Python, SQL e BI** em realidade.")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📊 Sua Roda da Vida")
    notas_atuais = get_notas()
    
    # Sliders para atualizar notas na barra lateral ou aqui
    with st.expander("Ajustar Níveis Atuais"):
        for area, nota in notas_atuais.items():
            nova_nota = st.slider(f"{area}", 0, 10, nota, key=area)
            if nova_nota != nota:
                update_nota(area, nova_nota)
                st.rerun()

    # Criar Gráfico Radar
    df_plot = pd.DataFrame(dict(
        r=list(notas_atuais.values()),
        theta=list(notas_atuais.keys())
    ))
    fig = px.line_polar(df_plot, r='r', theta='theta', line_close=True, 
                        range_r=[0,10], color_discrete_sequence=['#00CC96'])
    fig.update_polars(radialaxis_showticklabels=True)
    fig.update_traces(fill='toself')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("🤖 Mentor IA Vertical")
    st.info("Eu conheço seu progresso e suas metas de 2026. Pergunte qualquer coisa sobre Dados ou Carreira.")
    
    user_input = st.text_input("Dúvida técnica ou de carreira:", placeholder="Ex: Como integrar SQL com Power BI?")
    
    if st.button("Consultar Mentor"):
        if user_input:
            with st.spinner("Analisando dados e gerando insight..."):
                contexto = f"O usuário está estudando Ciência de Dados (Python, SQL, BI). Notas atuais da Roda da Vida: {notas_atuais}."
                prompt = f"{contexto}\nPergunta: {user_input}\nResponda como um mentor sênior de dados."
                
                try:
                    response = model.generate_content(prompt)
                    st.markdown("---")
                    st.markdown(f"**Resposta do DataPath AI:**\n\n{response.text}")
                except Exception as e:
                    st.error(f"Erro ao conectar com a IA: {e}")
        else:
            st.warning("Por favor, digite uma pergunta.")

# --- RODAPÉ ---
st.markdown("---")

st.caption("Foco 2026: Consistência é melhor que intensidade. Continue estudando!")



