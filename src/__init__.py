"""
SEFAZ Query Automator
Automated system for querying and requesting XML files from the SEFAZ portal.
"""

__version__ = "1.0.0"
__author__ = "Adrian Haelisson"
__license__ = "MIT"

from .config import (
    USUARIO_SEFAZ,
    SENHA_SEFAZ,
    SIMBOLOS,
    HEADLESS_MODE,
    MAX_TENTATIVAS_RETRY,
    USAR_EMOJIS,
    validar_configuracoes
)

from .sefaz_browser import SefazBrowser
from .sefaz_actions import SefazActions
from .utils import formatar_data, preparar_parametros, timestamp

__all__ = [
    'SefazBrowser',
    'SefazActions',
    'formatar_data',
    'preparar_parametros',
    'timestamp',
    'USUARIO_SEFAZ',
    'SENHA_SEFAZ',
    'SIMBOLOS',
    'HEADLESS_MODE',
    'MAX_TENTATIVAS_RETRY',
    'USAR_EMOJIS',
    'validar_configuracoes',
]
