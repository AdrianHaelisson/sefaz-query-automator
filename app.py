"""
Sistema de Consulta SEFAZ - Interface Streamlit
Aplicacao web moderna para consulta e solicitacao de arquivos XML no portal SEFAZ
"""
import streamlit as st
import pandas as pd
import os
import sys
import time
from datetime import datetime
import json
import pickle
import hashlib

# Configuracao da pagina
st.set_page_config(
    page_title="Consulta SEFAZ",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Adiciona o diretorio do projeto ao path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Importa modulos do sistema
from src.sefaz_browser import SefazBrowser
from src.sefaz_actions import SefazActions
from src.utils import preparar_parametros
from src.config import (
    USUARIO_SEFAZ, 
    SENHA_SEFAZ, 
    SIMBOLOS, 
    HEADLESS_MODE,
    MAX_TENTATIVAS_RETRY,
    validar_configuracoes
)

# CSS customizado
st.markdown("""
<style>
    :root {
        --primary-color: #60a5fa;
        --primary-dark: #3b82f6;
        --accent-color: #34d399;
        --warning-color: #fb923c;
        --warning-bg: #451a03;
        --info-bg: #172554;
        --info-border: #1e40af;
        --instruction-bg: #064e3b;
        --instruction-border: #059669;
        --text-primary: #f1f5f9;
        --text-secondary: #cbd5e1;
        --border-color: #475569;
    }
    
    .main-header {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(45deg, var(--primary-color), var(--accent-color));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem;
    }
    
    .stButton > button {
        border-radius: 8px;
        transition: all 0.3s ease;
        border: none;
        background-color: var(--primary-color) !important;
        color: var(--text-primary) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(96, 165, 250, 0.3);
        background-color: var(--primary-dark) !important;
    }
    
    .log-container {
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 1.5rem;
        background: rgba(30, 41, 59, 0.5);
        color: var(--text-primary);
    }
    
    div[data-testid="stExpander"] {
        border-radius: 8px;
        border: 1px solid var(--border-color);
        background: rgba(30, 41, 59, 0.3);
    }
    
    .custom-info-box {
        background: var(--info-bg);
        border: 1px solid var(--info-border);
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
        color: var(--text-primary);
    }
    
    .custom-info-box ul {
        color: var(--text-secondary);
    }
    
    .custom-warning-box {
        background: var(--warning-bg);
        border: 1px solid var(--warning-color);
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
        color: var(--warning-color);
    }
    
    .instruction-box {
        background: var(--instruction-bg);
        border: 1px solid var(--instruction-border);
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
        color: var(--text-primary);
    }
    
    .instruction-box h3 {
        color: var(--accent-color);
        margin-bottom: 1rem;
    }
    
    .instruction-box ol {
        color: var(--text-secondary);
    }
    
    .controls-list {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .controls-list h4 {
        color: var(--primary-color);
        margin-bottom: 1rem;
    }
    
    .controls-list ul {
        list-style-type: none;
        padding-left: 0;
        margin: 0.5rem 0;
    }
    
    .controls-list li {
        padding: 0.8rem 0;
        border-bottom: 1px solid var(--border-color);
        color: var(--text-secondary);
    }
    
    .controls-list li:last-child {
        border-bottom: none;
    }
    
    .controls-list li strong {
        color: var(--primary-color);
    }
    
    /* Melhorar contraste de textos em geral */
    p, li, .stMarkdown {
        color: var(--text-primary);
    }
    
    /* Destaque para códigos inline */
    code {
        background: rgba(30, 41, 59, 0.7);
        color: var(--primary-color);
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 0.9em;
        border: 1px solid var(--border-color);
    }

    /* Ajustes para links e textos importantes */
    a, .important-text {
        color: var(--primary-color) !important;
    }

    /* Melhorar visibilidade de títulos */
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-primary) !important;
    }
</style>
""", unsafe_allow_html=True)

# Inicializacao do estado da sessao
for key, default in {
    'log_messages': [],
    'empresas_processadas': 0,
    'empresas_sucesso': 0,
    'empresas_erro': 0,
    'empresas_com_erro': [],
    'processando': False,
    'parar': False,
    'browser': None,
    'actions': None,
    'df_atual': None,
    'df_hash': None,
    'indice_atual': 0,
    'fase': 'inicial',
    'planilha_salva': False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# Diretorio para dados persistentes
DATA_DIR = 'sessao_data'
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Funcoes auxiliares
def adicionar_log(mensagem):
    """Adiciona mensagem ao log"""
    hora = datetime.now().strftime("%H:%M:%S")
    if 'log_messages' not in st.session_state:
        st.session_state.log_messages = []
    st.session_state.log_messages.append(f"[{hora}] {mensagem}")

def salvar_checkpoint():
    """Salva checkpoint do processamento"""
    try:
        checkpoint = {
            'indice_atual': st.session_state.indice_atual,
            'empresas_processadas': st.session_state.empresas_processadas,
            'empresas_sucesso': st.session_state.empresas_sucesso,
            'empresas_erro': st.session_state.empresas_erro,
            'empresas_com_erro': st.session_state.empresas_com_erro,
            'df_hash': st.session_state.df_hash,  # Salva hash da planilha
            'timestamp': datetime.now().isoformat()
        }
        with open('checkpoint.json', 'w', encoding='utf-8') as f:
            json.dump(checkpoint, f, indent=2, ensure_ascii=False)
        adicionar_log(f"{SIMBOLOS['info']} Checkpoint salvo")
    except Exception as e:
        adicionar_log(f"{SIMBOLOS['aviso']} Erro ao salvar checkpoint: {e}")

def carregar_checkpoint():
    """Carrega checkpoint se existir"""
    try:
        if os.path.exists('checkpoint.json'):
            with open('checkpoint.json', 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    return None

def limpar_checkpoint():
    """Remove checkpoint"""
    try:
        if os.path.exists('checkpoint.json'):
            os.remove('checkpoint.json')
    except:
        pass

def gerar_hash_arquivo(arquivo):
    """Gera hash unico para o arquivo"""
    arquivo.seek(0)
    conteudo = arquivo.read()
    arquivo.seek(0)
    return hashlib.md5(conteudo).hexdigest()

def salvar_planilha_sessao(df, file_hash):
    """Salva planilha na sessao persistente"""
    try:
        # Salva DataFrame
        caminho_df = os.path.join(DATA_DIR, f'planilha_{file_hash}.pkl')
        df.to_pickle(caminho_df)
        
        # Salva metadados
        metadados = {
            'hash': file_hash,
            'total_empresas': len(df),
            'timestamp': datetime.now().isoformat(),
            'nome_colunas': list(df.columns)
        }
        caminho_meta = os.path.join(DATA_DIR, f'meta_{file_hash}.json')
        with open(caminho_meta, 'w', encoding='utf-8') as f:
            json.dump(metadados, f, indent=2)
        
        adicionar_log(f"{SIMBOLOS['info']} Planilha salva na sessao (hash: {file_hash[:8]}...)")
        return True
    except Exception as e:
        adicionar_log(f"{SIMBOLOS['aviso']} Erro ao salvar: {e}")
        return False

def carregar_planilha_sessao(file_hash):
    """Carrega planilha da sessao persistente"""
    try:
        caminho_df = os.path.join(DATA_DIR, f'planilha_{file_hash}.pkl')
        if os.path.exists(caminho_df):
            df = pd.read_pickle(caminho_df)
            adicionar_log(f"{SIMBOLOS['sucesso']} Planilha recuperada da sessao")
            return df
    except Exception as e:
        adicionar_log(f"{SIMBOLOS['aviso']} Erro ao recuperar: {e}")
    return None

def listar_sessoes_salvas():
    """Lista todas as sessoes salvas"""
    sessoes = []
    try:
        for arquivo in os.listdir(DATA_DIR):
            if arquivo.startswith('meta_') and arquivo.endswith('.json'):
                caminho = os.path.join(DATA_DIR, arquivo)
                with open(caminho, 'r', encoding='utf-8') as f:
                    meta = json.load(f)
                    sessoes.append(meta)
    except:
        pass
    return sorted(sessoes, key=lambda x: x['timestamp'], reverse=True)

def limpar_sessoes_antigas(dias=7):
    """Remove sessoes mais antigas que X dias"""
    try:
        agora = datetime.now()
        for arquivo in os.listdir(DATA_DIR):
            caminho = os.path.join(DATA_DIR, arquivo)
            if os.path.isfile(caminho):
                mtime = datetime.fromtimestamp(os.path.getmtime(caminho))
                if (agora - mtime).days > dias:
                    os.remove(caminho)
    except:
        pass

def carregar_planilha(arquivo):
    """Carrega e valida a planilha"""
    try:
        colunas_necessarias = [
            "Inscricao Municipal", 
            "Tipo de Arquivo", 
            "Pesquisar Por", 
            "Data Inicial", 
            "Data Final"
        ]
        df = pd.read_excel(arquivo, usecols=colunas_necessarias).fillna("")
        
        if df.empty:
            st.error(f"{SIMBOLOS['erro']} Planilha vazia!")
            return None, None
        
        # Gera hash unico
        file_hash = gerar_hash_arquivo(arquivo)
        
        # Salva na sessao
        salvar_planilha_sessao(df, file_hash)
        
        adicionar_log(f"{SIMBOLOS['sucesso']} Planilha carregada: {len(df)} empresas")
        return df, file_hash
    except Exception as e:
        st.error(f"{SIMBOLOS['erro']} Erro: {e}")
        return None, None

# ============================================================================
# INTERFACE PRINCIPAL
# ============================================================================

# Cabecalho
st.markdown('<div class="main-header">🏢 Sistema de Consulta SEFAZ</div>', unsafe_allow_html=True)
st.markdown("### 🚀 Interface Automática de Consultas")
st.markdown("---")

# Verifica configuracoes (apenas alerta, nao bloqueia mais)
config_valida, mensagem_config = validar_configuracoes()
if not config_valida:
    st.markdown(f"""
        <div class="custom-warning-box">
            <h4 style="margin-top:0">⚠️ Atenção: Credenciais Necessárias</h4>
            <p>{mensagem_config}</p>
        </div>
        <div class="custom-info-box">
            <p>💡 Você pode configurar suas credenciais de duas formas:</p>
            <ul>
                <li>No arquivo <code>.env</code> (recomendado)</li>
                <li>Diretamente na interface através da barra lateral</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Configurações")
    
    # Configuracoes de Acesso
    with st.expander("🔐 Credenciais de Acesso", expanded=False):
        st.caption("💡 Opcional: Use apenas se quiser sobrescrever o .env")
        
        usuario_temp = st.text_input(
            "Usuario SEFAZ",
            value="",
            placeholder=f"Padrao: {USUARIO_SEFAZ[:2]}***" if USUARIO_SEFAZ else "Digite seu usuario",
            help="Deixe vazio para usar o .env"
        )
        
        senha_temp = st.text_input(
            "Senha SEFAZ",
            value="",
            type="password",
            placeholder="Senha do portal",
            help="Deixe vazio para usar o .env"
        )
        
        # Salva temporariamente no session_state
        if usuario_temp:
            st.session_state.usuario_override = usuario_temp
        if senha_temp:
            st.session_state.senha_override = senha_temp
    
    # Configuracoes do Navegador
    with st.expander("🌐 Configuracoes do Navegador", expanded=False):
        headless_toggle = st.toggle(
            "Modo Headless",
            value=HEADLESS_MODE,
            help="Ativado: navegador invisivel (mais rapido). Desativado: ve o navegador (debug)"
        )
        
        # Salva no session_state
        st.session_state.headless_override = headless_toggle
        
        if headless_toggle:
            st.caption("✅ Navegador invisivel (mais rapido)")
        else:
            st.caption("👁️ Navegador visivel (para debug)")
    
    st.divider()
    
    # Mostra configuracao atual
    usuario_atual = st.session_state.get('usuario_override', USUARIO_SEFAZ)
    st.info(f"""
    **Usuario em uso:** {usuario_atual[:2]}***  
    **Modo Headless:** {'Sim' if st.session_state.get('headless_override', HEADLESS_MODE) else 'Nao'}
    """)
    
    st.divider()
    
    # Sessoes salvas
    sessoes = listar_sessoes_salvas()
    if sessoes and not st.session_state.processando:
        st.subheader("Sessoes Salvas")
        for sessao in sessoes[:5]:  # Mostra ultimas 5
            dt = datetime.fromisoformat(sessao['timestamp'])
            if st.button(
                f"📂 {sessao['total_empresas']} empresas - {dt.strftime('%d/%m %H:%M')}",
                key=f"sessao_{sessao['hash']}",
                use_container_width=True
            ):
                # Carrega planilha da sessao
                df_recuperado = carregar_planilha_sessao(sessao['hash'])
                if df_recuperado is not None:
                    st.session_state.df_atual = df_recuperado
                    st.session_state.df_hash = sessao['hash']
                    st.session_state.planilha_salva = True
                    adicionar_log(f"{SIMBOLOS['sucesso']} Sessao recuperada!")
                    st.rerun()
        
        st.divider()
    
    # Upload
    st.subheader("Nova Planilha")
    arquivo = st.file_uploader(
        "Upload Excel",
        type=['xlsx', 'xls']
    )
    
    # Checkpoint
    checkpoint = carregar_checkpoint()
    if checkpoint and not st.session_state.processando:
        st.divider()
        st.warning(f"Checkpoint na empresa {checkpoint['indice_atual']}")
        if st.button("🔄 Retomar Checkpoint", use_container_width=True, type="primary"):
            # Recupera estado do checkpoint
            st.session_state.indice_atual = checkpoint['indice_atual']
            st.session_state.empresas_processadas = checkpoint['empresas_processadas']
            st.session_state.empresas_sucesso = checkpoint['empresas_sucesso']
            st.session_state.empresas_erro = checkpoint['empresas_erro']
            st.session_state.empresas_com_erro = checkpoint['empresas_com_erro']
            
            # Recupera a planilha associada
            if 'df_hash' in checkpoint:
                df_recuperado = carregar_planilha_sessao(checkpoint['df_hash'])
                if df_recuperado is not None:
                    st.session_state.df_atual = df_recuperado
                    st.session_state.df_hash = checkpoint['df_hash']
                    st.session_state.planilha_salva = True
                    
                    # LIMPA navegador e actions anteriores
                    st.session_state.browser = None
                    st.session_state.actions = None
                    
                    # Reinicia o processamento
                    st.session_state.processando = True
                    st.session_state.parar = False
                    st.session_state.fase = 'navegador'
                    
                    adicionar_log(f"{SIMBOLOS['sucesso']} Checkpoint carregado!")
                    adicionar_log(f"{SIMBOLOS['info']} Retomando da empresa {checkpoint['indice_atual'] + 1}")
                    st.rerun()
                else:
                    st.error("Planilha nao encontrada! Faca upload novamente.")
            else:
                st.error("Checkpoint antigo sem hash. Faca upload da planilha.")
    
    st.divider()
    
    # Estatisticas
    st.subheader("📊 Estatísticas")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("✅ Sucesso", st.session_state.empresas_sucesso, 
                 delta=f"{int(st.session_state.empresas_sucesso/max(1, st.session_state.empresas_processadas)*100)}%" if st.session_state.empresas_processadas > 0 else None)
    with col2:
        st.metric("❌ Erros", st.session_state.empresas_erro,
                 delta=f"{int(st.session_state.empresas_erro/max(1, st.session_state.empresas_processadas)*100)}%" if st.session_state.empresas_processadas > 0 else None,
                 delta_color="inverse")
    with col3:
        st.metric("🔄 Processadas", st.session_state.empresas_processadas)

# Conteudo principal
if arquivo is not None or st.session_state.planilha_salva:
    # Carrega planilha nova ou usa a ja carregada
    if arquivo is not None and not st.session_state.planilha_salva:
        df, file_hash = carregar_planilha(arquivo)
        st.session_state.df_atual = df
        st.session_state.df_hash = file_hash
        st.session_state.planilha_salva = True
    else:
        df = st.session_state.df_atual
    
    if df is not None:
        total_empresas = len(df)
        
        # Preview
        with st.expander("📋 Preview da Planilha", expanded=False):
            st.dataframe(df.head(20), use_container_width=True)
            st.caption(f"📊 Total: {total_empresas} empresas para processar")
        
        # Controles
        st.divider()
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if not st.session_state.processando:
                if st.button("▶️ Iniciar Processamento", type="primary", use_container_width=True):
                    # Reseta
                    st.session_state.log_messages = []
                    st.session_state.empresas_processadas = 0
                    st.session_state.empresas_sucesso = 0
                    st.session_state.empresas_erro = 0
                    st.session_state.empresas_com_erro = []
                    st.session_state.indice_atual = 0
                    st.session_state.processando = True
                    st.session_state.parar = False
                    st.session_state.fase = 'navegador'
                    st.rerun()
        
        with col2:
            if st.session_state.processando:
                if st.button("⏹️ Parar e Salvar", type="secondary", use_container_width=True):
                    st.session_state.parar = True
                    salvar_checkpoint()
                    adicionar_log(f"{SIMBOLOS['parar']} Parando...")
                    st.rerun()
        
        with col3:
            if st.session_state.log_messages:
                log_text = "\n".join(st.session_state.log_messages)
                st.download_button(
                    label="💾 Download Log",
                    data=log_text,
                    file_name=f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
        
        # Progresso
        if st.session_state.empresas_processadas > 0 or st.session_state.processando:
            st.divider()
            progresso = st.session_state.empresas_processadas / total_empresas if total_empresas > 0 else 0
            st.progress(progresso, text=f"Progresso: {st.session_state.empresas_processadas}/{total_empresas} empresas")
            
            # Status
            if st.session_state.processando:
                st.info(f"{SIMBOLOS['processando']} Processando empresa {st.session_state.empresas_processadas + 1}/{total_empresas}...")
            elif st.session_state.parar:
                st.warning(f"{SIMBOLOS['parar']} Processamento INTERROMPIDO - Checkpoint salvo")
            else:
                if st.session_state.empresas_erro == 0:
                    st.success(f"{SIMBOLOS['concluido']} Processamento CONCLUIDO com sucesso!")
                    st.balloons()
                else:
                    st.warning(f"{SIMBOLOS['concluido']} Processamento concluido com {st.session_state.empresas_erro} erros")
        
        # Log em tempo real
        st.divider()
        st.subheader("📝 Log em Tempo Real")
        
        log_container = st.container()
        with log_container:
            if st.session_state.log_messages:
                st.markdown("##### 🔄 Últimas Atividades")
                log_text = "\n".join(st.session_state.log_messages[-50:])
                st.markdown('<div class="log-container">', unsafe_allow_html=True)
                st.text_area("Log Output", value=log_text, height=300, label_visibility="collapsed", key=f"log_{len(st.session_state.log_messages)}")
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("⏳ Aguardando início do processamento...")
        
        # PROCESSAMENTO INCREMENTAL
        if st.session_state.processando and not st.session_state.parar:
            
            # Fase: Inicializar Navegador
            if st.session_state.fase == 'navegador':
                if st.session_state.browser is None:
                    # Usa configuracao da interface ou do .env
                    headless_mode = st.session_state.get('headless_override', HEADLESS_MODE)
                    adicionar_log(f"{SIMBOLOS['navegador']} Inicializando navegador...")
                    adicionar_log(f"{SIMBOLOS['info']} Modo headless: {'Sim' if headless_mode else 'Nao'}")
                    
                    try:
                        st.session_state.browser = SefazBrowser(headless=headless_mode)
                        adicionar_log(f"{SIMBOLOS['sucesso']} Navegador criado!")
                        time.sleep(2)
                        st.session_state.fase = 'login'
                        st.rerun()
                    except Exception as e:
                        adicionar_log(f"{SIMBOLOS['erro']} Erro ao inicializar: {e}")
                        st.session_state.processando = False
                        st.rerun()
                else:
                    # Navegador ja existe, vai para login
                    st.session_state.fase = 'login'
                    st.rerun()
            
            # Fase: Login
            elif st.session_state.fase == 'login':
                # Usa credenciais da interface ou do .env
                usuario_login = st.session_state.get('usuario_override', USUARIO_SEFAZ)
                senha_login = st.session_state.get('senha_override', SENHA_SEFAZ)
                
                if not usuario_login or not senha_login:
                    adicionar_log(f"{SIMBOLOS['erro']} Credenciais nao configuradas!")
                    st.error("Configure credenciais no .env ou na interface!")
                    st.session_state.processando = False
                    st.rerun()
                
                adicionar_log(f"{SIMBOLOS['login']} Realizando login com usuario: {usuario_login[:2]}***...")
                try:
                    if st.session_state.browser.fazer_login(usuario_login, senha_login):
                        adicionar_log(f"{SIMBOLOS['sucesso']} Login OK!")
                        time.sleep(2)
                        st.session_state.fase = 'menu'
                        st.rerun()
                    else:
                        adicionar_log(f"{SIMBOLOS['erro']} Falha no login!")
                        st.error("Falha no login! Verifique credenciais")
                        st.session_state.processando = False
                        st.rerun()
                except Exception as e:
                    adicionar_log(f"{SIMBOLOS['erro']} Erro no login: {e}")
                    st.session_state.processando = False
                    st.rerun()
            
            # Fase: Navegar para Menu
            elif st.session_state.fase == 'menu':
                adicionar_log(f"{SIMBOLOS['menu']} Navegando para menu...")
                try:
                    if st.session_state.browser.navegar_para_menu_xml():
                        adicionar_log(f"{SIMBOLOS['sucesso']} Menu OK!")
                        # Reinicializa actions com navegador atual
                        st.session_state.actions = SefazActions(st.session_state.browser)
                        adicionar_log(f"{SIMBOLOS['info']} Sistema pronto para processar!")
                        time.sleep(1)
                        st.session_state.fase = 'processando'
                        st.rerun()
                    else:
                        adicionar_log(f"{SIMBOLOS['erro']} Falha ao navegar!")
                        st.session_state.processando = False
                        st.rerun()
                except Exception as e:
                    adicionar_log(f"{SIMBOLOS['erro']} Erro ao navegar: {e}")
                    st.session_state.processando = False
                    st.rerun()
            
            # Fase: Processando Empresas
            elif st.session_state.fase == 'processando':
                # Verifica se actions está inicializado
                if st.session_state.actions is None:
                    adicionar_log(f"{SIMBOLOS['aviso']} Actions nao inicializado, reiniciando...")
                    st.session_state.fase = 'menu'
                    st.rerun()
                
                if st.session_state.indice_atual < total_empresas:
                    idx = st.session_state.indice_atual
                    row = df.iloc[idx]
                    
                    adicionar_log(f"{SIMBOLOS['processando']} Empresa {idx+1}/{total_empresas}")
                    
                    params = preparar_parametros(row)
                    inscricao = params["inscricao_municipal"]
                    
                    if not inscricao:
                        adicionar_log(f"{SIMBOLOS['aviso']} Inscricao ausente")
                        st.session_state.empresas_erro += 1
                    else:
                        adicionar_log(f"{SIMBOLOS['empresa']} {inscricao} | {params['tipo_arquivo']}")
                        
                        try:
                            tipo = params["tipo_arquivo"].upper()
                            
                            # Detecta se navegador está vivo
                            try:
                                st.session_state.browser.get_driver().title
                            except:
                                adicionar_log(f"{SIMBOLOS['erro']} Navegador desconectado!")
                                salvar_checkpoint()
                                st.session_state.processando = False
                                st.session_state.fase = 'concluido'
                                st.error(f"{SIMBOLOS['erro']} Navegador fechou! Checkpoint salvo. Use 'Retomar Checkpoint'")
                                st.rerun()
                            
                            if tipo in ["NFE", "NFC"]:
                                sucesso, msg = st.session_state.actions.processar_solicitacao_nfe_nfc(params)
                            elif tipo == "CTE":
                                sucesso, msg = st.session_state.actions.processar_solicitacao_cte(params)
                            else:
                                sucesso = False
                                msg = f"Tipo desconhecido: {tipo}"
                            
                            if sucesso:
                                adicionar_log(f"{SIMBOLOS['sucesso']} OK")
                                st.session_state.empresas_sucesso += 1
                                if idx + 1 < total_empresas:
                                    try:
                                        st.session_state.browser.voltar_para_nova_solicitacao()
                                    except:
                                        adicionar_log(f"{SIMBOLOS['aviso']} Erro ao voltar para nova solicitacao")
                                        salvar_checkpoint()
                                        st.session_state.processando = False
                                        st.rerun()
                            else:
                                adicionar_log(f"{SIMBOLOS['erro']} {msg}")
                                st.session_state.empresas_erro += 1
                                st.session_state.empresas_com_erro.append({
                                    'index': idx,
                                    'inscricao': inscricao,
                                    'tipo': tipo,
                                    'motivo': msg
                                })
                        except Exception as e:
                            erro_msg = str(e)
                            adicionar_log(f"{SIMBOLOS['erro']} Erro: {erro_msg}")
                            st.session_state.empresas_erro += 1
                            
                            # Se é erro de sessão, salva checkpoint e para
                            if 'invalid session' in erro_msg.lower() or 'disconnected' in erro_msg.lower():
                                adicionar_log(f"{SIMBOLOS['parar']} Navegador desconectado! Salvando checkpoint...")
                                salvar_checkpoint()
                                st.session_state.processando = False
                                st.session_state.fase = 'concluido'
                                st.error(f"{SIMBOLOS['erro']} Navegador desconectou! Use 'Retomar Checkpoint'")
                                
                                # Tenta fechar navegador
                                try:
                                    if st.session_state.browser:
                                        st.session_state.browser.fechar()
                                except:
                                    pass
                                st.session_state.browser = None
                                st.rerun()
                    
                    st.session_state.empresas_processadas = idx + 1
                    st.session_state.indice_atual += 1
                    
                    # Checkpoint a cada 10
                    if st.session_state.empresas_processadas % 10 == 0:
                        salvar_checkpoint()
                    
                    time.sleep(0.3)
                    st.rerun()
                else:
                    # Concluido
                    adicionar_log(f"{SIMBOLOS['concluido']} Concluido!")
                    adicionar_log(f"{SIMBOLOS['estatistica']} Sucesso: {st.session_state.empresas_sucesso} | Erros: {st.session_state.empresas_erro}")
                    st.session_state.processando = False
                    st.session_state.fase = 'concluido'
                    limpar_checkpoint()
                    
                    # Fecha navegador
                    if st.session_state.browser:
                        try:
                            st.session_state.browser.fechar()
                        except:
                            pass
                        st.session_state.browser = None
                    
                    st.rerun()
        
        # Parar solicitado
        if st.session_state.parar:
            adicionar_log(f"{SIMBOLOS['parar']} Interrompido!")
            salvar_checkpoint()
            st.session_state.processando = False
            st.session_state.parar = False
            
            if st.session_state.browser:
                try:
                    st.session_state.browser.fechar()
                except:
                    pass
                st.session_state.browser = None
            
            st.rerun()
        
        # Empresas com erro
        if st.session_state.empresas_com_erro:
            st.divider()
            st.subheader("Empresas com Erro")
            df_erros = pd.DataFrame(st.session_state.empresas_com_erro)
            st.dataframe(df_erros, use_container_width=True)
            
            csv = df_erros.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                "📥 Exportar Erros",
                csv,
                f"erros_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "text/csv"
            )

else:
    st.markdown("""
    <div class="instruction-box">
        <h3 style="margin-top:0">📋 Guia de Utilização</h3>
        <p>Siga os passos abaixo para começar:</p>
        <ol style="margin-bottom:1.5rem">
            <li>Configure suas credenciais no arquivo <code>.env</code></li>
            <li>Faça upload da planilha de dados pela barra lateral</li>
            <li>Inicie o processamento</li>
            <li>Monitore o progresso em tempo real</li>
        </ol>
    </div>
    
    <div class="controls-list">
        <h4 style="margin-top:0">🎮 Controles Disponíveis</h4>
        <ul>
            <li><strong>▶️ Iniciar</strong> - Inicia o processamento automatizado</li>
            <li><strong>⏹️ Parar</strong> - Interrompe o processo e salva o progresso atual</li>
            <li><strong>💾 Download</strong> - Exporta o registro completo de atividades</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("Exemplo"):
        exemplo = pd.DataFrame({
            'Inscricao Municipal': ['12345678', '87654321'],
            'Tipo de Arquivo': ['NFE', 'NFC'],
            'Pesquisar Por': ['Emitente', 'Destinatario'],
            'Data Inicial': ['01/09/2024', '01/09/2024'],
            'Data Final': ['30/09/2024', '30/09/2024']
        })
        st.dataframe(exemplo, use_container_width=True)

# Rodape
st.divider()
st.caption("🏢 Sistema de Consulta SEFAZ v8.0.2 | 🚀 Powered by Streamlit | 📜 MIT License")
