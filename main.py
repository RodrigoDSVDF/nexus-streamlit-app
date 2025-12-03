import streamlit as st
import time
from datetime import datetime
import base64
import gspread
import json
import pandas as pd

# --- IMPORTS DO USUÁRIO ---
# Certifique-se de que estes arquivos existem no seu diretório
try:
    from components.ai_interfaces import AI_INTERFACES
    from config import AI_LINKS
    # Assumindo que AI_TOOLS também vem de config ou está definido aqui. 
    # Vou definir um placeholder abaixo caso não venha do config.
    from config import AI_TOOLS 
except ImportError:
    # Fallback para evitar erro se o usuário estiver testando apenas este arquivo
    st.warning("⚠️ Arquivos 'config.py' ou 'components/' não encontrados. Usando dados de exemplo.")
    AI_LINKS = {}
    AI_TOOLS = {
        "gpt4": {"title": "GPT-4 Omni", "icon": "🧠", "description": "Inteligência Geral Avançada", "status": "Online"},
        "midjourney": {"title": "Midjourney", "icon": "🎨", "description": "Geração de Imagens Artísticas", "status": "Online"},
        "claude": {"title": "Claude 3.5", "icon": "🤖", "description": "Análise e Coding Avançado", "status": "Online"}
    }
    def create_particles(): pass # Placeholder

# =======================================================
# CONFIGURAÇÕES DO GOOGLE SHEETS (Backend)
# =======================================================
GCP_SECRET_KEY = "gcp_service_account"
SHEET_URL = "https://docs.google.com/spreadsheets/d/1hPEVs08u7KE76OheFk0p94cbwrGkzkX6Z5ucJdkXxoA/edit?usp=drivesdk"
SERVICE_ACCOUNT_EMAIL = "appnexusteste@appnexus-480003.iam.gserviceaccount.com"

# =======================================================
# CONFIGURAÇÃO DA PÁGINA
# =======================================================
st.set_page_config(
    page_title="Nexus - Ecossistema de IAs",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =======================================================
# FUNÇÕES DE AUTENTICAÇÃO E SHEETS
# =======================================================
@st.cache_resource(ttl=300)
def authenticate_sheets_client():
    try:
        creds_attr_dict = st.secrets[GCP_SECRET_KEY]
        creds_dict_standard = dict(creds_attr_dict)
        client = gspread.service_account_from_dict(creds_dict_standard)
        return client
    except Exception as e:
        st.error(f"Erro de conexão com banco de dados: {e}")
        return None

def save_to_sheets(client, email):
    if not client: return False
    try:
        spreadsheet = client.open_by_url(SHEET_URL)
        worksheet = spreadsheet.worksheet(spreadsheet.worksheets()[0].title)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        worksheet.append_row([email, timestamp])
        return True
    except Exception as e:
        st.error(f"Erro ao salvar: {e}")
        return False

# =======================================================
# ESTILOS E UI (CSS)
# =======================================================
def load_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;500;600;700&display=swap');
        
        .stApp {
            background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
            color: #ffffff;
        }
        
        /* Headers */
        .main-header {
            text-align: center;
            padding: 2rem 0;
            background: linear-gradient(45deg, #00d4ff, #00ff88);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-family: 'Orbitron', monospace;
            font-weight: 900;
            font-size: 3.5rem;
            text-shadow: 0 0 30px rgba(0, 212, 255, 0.5);
            margin-bottom: 1rem;
        }
        
        .subtitle {
            text-align: center;
            font-family: 'Rajdhani', sans-serif;
            font-size: 1.2rem;
            color: #a0a0a0;
            margin-bottom: 3rem;
        }

        /* Login Container Styles */
        .login-container {
            max-width: 500px;
            margin: 10vh auto;
            padding: 3rem;
            background: rgba(30, 30, 63, 0.7);
            border-radius: 20px;
            border: 1px solid rgba(0, 212, 255, 0.3);
            box-shadow: 0 0 50px rgba(0, 212, 255, 0.1);
            text-align: center;
            backdrop-filter: blur(10px);
        }

        /* Cards do Ecossistema */
        .ecosystem-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            padding: 2rem;
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .ai-card {
            background: linear-gradient(145deg, #1e1e3f, #2a2a5a);
            border-radius: 20px;
            padding: 2rem;
            border: 2px solid transparent;
            position: relative;
            overflow: hidden;
            transition: all 0.3s ease;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            margin-bottom: 1rem;
        }
        
        .ai-card:hover {
            transform: translateY(-10px) scale(1.02);
            box-shadow: 0 20px 40px rgba(0, 212, 255, 0.2);
            border-color: rgba(0, 212, 255, 0.3);
        }
        
        .ai-title {
            font-family: 'Orbitron', sans-serif;
            font-size: 1.5rem;
            margin-bottom: 0.5rem;
            color: #fff;
        }
        
        .ai-description {
            color: #a0a0a0;
            font-size: 0.9rem;
            margin-bottom: 1rem;
        }

        /* Links Styles */
        .links-container {
            background: rgba(255, 255, 255, 0.05);
            padding: 2rem;
            border-radius: 15px;
            margin-top: 2rem;
        }
        
        .link-item {
            margin: 1rem 0;
            padding: 1rem;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 10px;
            border-left: 3px solid #00ff88;
        }
        
        .link-item a {
            color: #ffffff;
            text-decoration: none;
            font-family: 'Rajdhani', sans-serif;
            font-size: 1.1rem;
            margin-left: 10px;
        }

        /* Stats */
        .stat-item {
            text-align: center;
            padding: 1.5rem;
            background: rgba(255, 255, 255, 0.03);
            border-radius: 15px;
            margin: 0.5rem;
        }
        .stat-number {
            font-family: 'Orbitron', sans-serif;
            font-size: 2rem;
            color: #00ff88;
        }
        .stat-label {
            color: #a0a0a0;
            font-size: 0.9rem;
        }
    </style>
    """, unsafe_allow_html=True)

# =======================================================
# LÓGICA DE PÁGINAS
# =======================================================

def render_login_page():
    """
    Renderiza a tela de Login/Captura de Email.
    """
    st.markdown('<h1 class="main-header">NEXUS ACCESS</h1>', unsafe_allow_html=True)
    
    # Container centralizado usando colunas para layout
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="login-container">
            <p style="font-family: 'Rajdhani'; font-size: 1.3rem; margin-bottom: 2rem;">
                Identifique-se para acessar o ecossistema.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            email = st.text_input("Seu E-mail Corporativo", placeholder="usuario@exemplo.com")
            submitted = st.form_submit_button("Inicializar Sistema 🚀", use_container_width=True)
            
            if submitted:
                if not email or "@" not in email:
                    st.warning("⚠️ Protocolo de identificação falhou: E-mail inválido.")
                else:
                    with st.spinner("Autenticando credenciais no servidor..."):
                        client = authenticate_sheets_client()
                        if client:
                            success = save_to_sheets(client, email)
                            if success:
                                st.session_state['access_granted'] = True
                                st.success("✅ Acesso Autorizado.")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("❌ Falha na conexão com o banco de dados.")
                        else:
                            st.error("❌ Erro crítico de autenticação interna.")

def render_ai_link_page(ai_key):
    """
    Renderiza a página de detalhes da IA selecionada.
    """
    ai_tool = AI_TOOLS.get(ai_key, {"title": "Desconhecido"})
    
    st.markdown(f'<h1 class="main-header">{ai_tool["title"]}</h1>', unsafe_allow_html=True)
    
    # Exibe links e ferramentas
    if ai_key in AI_LINKS and AI_LINKS[ai_key]:
        st.markdown('<div class="links-container"><h4>Ferramentas e Links de Acesso</h4>', unsafe_allow_html=True)
        for link_item in AI_LINKS[ai_key]:
            st.markdown(f"""
            <div class="link-item">
                <span class="icon">🔗</span>
                <a href="{link_item['url']}" target="_blank">{link_item['name']}</a>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.warning(f"Nenhuma ferramenta ou link relacionado foi encontrado para {ai_tool['title']}.")

    # Botão para voltar
    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("🔙 Voltar ao Ecossistema", use_container_width=True):
        del st.session_state.selected_ai
        st.rerun()

def render_main_page():
    """
    Renderiza a página principal do ecossistema com a grade de IAs.
    """
    st.markdown('<h1 class="main-header">NEXUS</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Ecossistema Inteligente de IAs para Produtividade</p>', unsafe_allow_html=True)

    # Estatísticas
    st.markdown('<div class="stats-container">', unsafe_allow_html=True)
    cols = st.columns(4)
    stats = [("18", "IAs Ativas"), ("24/7", "Status"), ("∞", "Potencial"), ("100%", "Seguro")]
    
    for i, (number, label) in enumerate(stats):
        with cols[i]:
            st.markdown(f"""
            <div class="stat-item">
                <div class="stat-number">{number}</div>
                <div class="stat-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)

    # Lógica de Seleção
    def select_ai(key):
        st.session_state.selected_ai = key

    # Grade de IAs
    st.markdown('<div class="ecosystem-container">', unsafe_allow_html=True)
    
    # Cria colunas para o grid (3 por linha)
    ai_keys = list(AI_TOOLS.keys())
    # Processando em chunks de 3 para melhor layout no Streamlit
    for i in range(0, len(ai_keys), 3):
        cols = st.columns(3)
        chunk = ai_keys[i:i+3]
        
        for idx, key in enumerate(chunk):
            ai_tool = AI_TOOLS[key]
            with cols[idx]:
                # Renderiza o Card Visual
                st.markdown(f"""
                <div class="ai-card">
                    <div style="font-size: 2rem; margin-bottom: 10px;">{ai_tool.get('icon', '🤖')}</div>
                    <div class="ai-title">{ai_tool['title']}</div>
                    <div class="ai-description">{ai_tool.get('description', '')}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Botão Funcional abaixo do card
                st.button(
                    f"Acessar {ai_tool['title']}", 
                    key=f"btn_{key}",
                    on_click=select_ai,
                    args=(key,),
                    use_container_width=True
                )
    
    st.markdown('</div>', unsafe_allow_html=True)

# =======================================================
# EXECUÇÃO PRINCIPAL (ROTEADOR)
# =======================================================
def main():
    load_css()
    
    # Tenta criar partículas se a função existir (do código original do usuário)
    try:
        from components.particles import create_particles # Assumindo local
        create_particles()
    except ImportError:
        pass

    # 1. Verifica se o usuário já fez login (Access Granted)
    if 'access_granted' not in st.session_state:
        st.session_state['access_granted'] = False

    # 2. Roteamento de Telas
    if not st.session_state['access_granted']:
        # Tela 01: Login
        render_login_page()
    else:
        # Tela 02: Ecossistema
        if 'selected_ai' in st.session_state:
            # Sub-tela: Detalhes da IA
            render_ai_link_page(st.session_state.selected_ai)
        else:
            # Tela Principal: Dashboard
            render_main_page()

if __name__ == "__main__":
    main()
