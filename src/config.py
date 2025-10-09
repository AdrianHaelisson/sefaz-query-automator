"""
Arquivo de configuracao do Sistema de Consulta SEFAZ
Gerencia variaveis de ambiente e configuracoes do sistema
"""
import os
from decouple import config

# ============================
# Credenciais SEFAZ
# ============================
USUARIO_SEFAZ = config('SEFAZ_USUARIO', default='')
SENHA_SEFAZ = config('SEFAZ_SENHA', default='')

# ============================
# Configuracoes do Navegador
# ============================
HEADLESS_MODE = config('HEADLESS_MODE', default=False, cast=bool)

# ============================
# Configuracoes de Retry
# ============================
MAX_TENTATIVAS_RETRY = config('MAX_TENTATIVAS_RETRY', default=3, cast=int)

# ============================
# Configuracoes de Interface
# ============================
USAR_EMOJIS = config('USAR_EMOJIS', default=False, cast=bool)

# Mapeamento de simbolos (com e sem emojis)
SIMBOLOS = {
    'sucesso': '✅' if USAR_EMOJIS else '[OK]',
    'erro': '❌' if USAR_EMOJIS else '[ERRO]',
    'aviso': '⚠️' if USAR_EMOJIS else '[AVISO]',
    'info': 'ℹ️' if USAR_EMOJIS else '[INFO]',
    'processando': '▶️' if USAR_EMOJIS else '[>]',
    'concluido': '🎉' if USAR_EMOJIS else '[CONCLUIDO]',
    'navegador': '🌐' if USAR_EMOJIS else '[NAV]',
    'login': '🔐' if USAR_EMOJIS else '[LOGIN]',
    'menu': '📋' if USAR_EMOJIS else '[MENU]',
    'empresa': '🏢' if USAR_EMOJIS else '[EMP]',
    'arquivo': '📄' if USAR_EMOJIS else '[ARQ]',
    'calendario': '📅' if USAR_EMOJIS else '[DATA]',
    'estatistica': '📊' if USAR_EMOJIS else '[STATS]',
    'pasta': '📂' if USAR_EMOJIS else '[PASTA]',
    'busca': '🔍' if USAR_EMOJIS else '[BUSCA]',
    'envio': '📤' if USAR_EMOJIS else '[ENVIO]',
    'loop': '🔄' if USAR_EMOJIS else '[LOOP]',
    'parar': '⛔' if USAR_EMOJIS else '[PARAR]',
    'fechar': '🔒' if USAR_EMOJIS else '[FECHAR]',
}

# ============================
# Validacao de Configuracoes
# ============================
def validar_configuracoes():
    """
    Valida se as configuracoes essenciais estao definidas
    
    Returns:
        tuple: (bool, str) - (e_valido, mensagem_erro)
    """
    if not USUARIO_SEFAZ or not SENHA_SEFAZ:
        return False, (
            "Credenciais do SEFAZ nao configuradas!\n\n"
            "Por favor, configure as seguintes variaveis de ambiente:\n"
            "- SEFAZ_USUARIO\n"
            "- SEFAZ_SENHA\n\n"
            "Voce pode criar um arquivo .env baseado no env.example"
        )
    
    return True, "Configuracoes validas"
