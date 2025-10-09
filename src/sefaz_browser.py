"""
Módulo para gerenciamento do navegador e autenticação no SEFAZ
Responsável por inicializar o navegador e fazer login uma única vez
"""
import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class SefazBrowser:
    """Classe para gerenciar a sessão do navegador no portal SEFAZ"""
    
    def __init__(self, headless=False):
        """
        Inicializa o navegador com as configurações necessárias
        
        Args:
            headless (bool): Se True, executa o navegador em modo headless
        """
        self.navegador = None
        self.wait = None
        self.headless = headless
        self._inicializar_navegador()
        
    def _inicializar_navegador(self):
        """Configura e inicializa o navegador Chrome"""
        options = Options()
        options.add_argument("--disable-gpu")
        if self.headless:
            options.add_argument("--headless=new")
        options.add_argument("--mute-audio")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("useAutomationExtension", False)
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        
        servico = Service(ChromeDriverManager().install())
        self.navegador = webdriver.Chrome(service=servico, options=options)
        # Wait reduzido para 10s (mais rápido, mas ainda seguro)
        self.wait = WebDriverWait(self.navegador, 10, poll_frequency=0.5)
        print("[OK] Navegador inicializado com sucesso!")
    
    def fazer_login(self, usuario, senha):
        """
        Realiza o login no portal SEFAZ
        
        Args:
            usuario (str): Nome de usuário
            senha (str): Senha do usuário
            
        Returns:
            bool: True se login bem-sucedido, False caso contrário
        """
        try:
            print("[LOGIN] Iniciando processo de login...")
            self.navegador.get("https://www.sefaz.se.gov.br/SitePages/acesso_usuario.aspx")
            time.sleep(2)  # Aguarda página carregar completamente
            
            # Aceitar cookies, se houver
            try:
                accept_button = WebDriverWait(self.navegador, 3).until(
                    EC.element_to_be_clickable((By.ID, 'accept-button'))
                )
                accept_button.click()
            except Exception:
                pass
            
            time.sleep(0.3)
            
            # Entrar no primeiro iframe
            iframes = self.navegador.find_elements(By.TAG_NAME, "iframe")
            if not iframes:
                print("[ERRO] Nenhum iframe encontrado na tela de acesso!")
                return False
            self.navegador.switch_to.frame(iframes[0])
            time.sleep(0.5)
            
            # Dropdown de acesso rápido
            dropdown = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'acessoRapido')))
            dropdown.click()
            time.sleep(0.2)
            
            # Seleciona Contabilista
            option_contabilista = self.wait.until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    "//option[@value='https://security.sefaz.se.gov.br/internet/portal/contabilista/atoAcessoContabilista.jsp']"
                ))
            )
            option_contabilista.click()
            time.sleep(0.2)
            
            # Click no body para desencadear evento
            try:
                body_tmp = self.navegador.find_element(By.TAG_NAME, "body")
                body_tmp.click()
                time.sleep(0.2)
            except Exception:
                pass
            
            # Entrar no iframe de login
            try:
                iframe_login = self.wait.until(
                    EC.presence_of_element_located((By.XPATH, "//iframe[contains(@src, 'atoAcessoContribuinte.jsp') or contains(@src, 'atoAcessoContabilista.jsp')]"))
                )
                self.navegador.switch_to.frame(iframe_login)
                time.sleep(0.5)
            except Exception as e:
                print(f"[ERRO] O iframe do login NAO foi encontrado! {e}")
                return False
            
            # Localiza a tabela de login
            tabela_login = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "tabelaVerde")))
            
            # Preenche campos de login
            campo_usuario = tabela_login.find_element(By.NAME, "UserName")
            campo_senha = tabela_login.find_element(By.NAME, "Password")
            botao_login = tabela_login.find_element(By.NAME, "submit")
            
            campo_usuario.click()
            campo_usuario.send_keys(usuario)
            campo_senha.click()
            campo_senha.send_keys(senha)
            botao_login.click()
            
            print("[OK] Login realizado com sucesso!")
            return True
            
        except Exception as e:
            print(f"[ERRO] Erro ao fazer login: {e}")
            return False
    
    def navegar_para_menu_xml(self):
        """
        Navega até o menu de solicitação de XML após o login
        
        Returns:
            bool: True se navegação bem-sucedida, False caso contrário
        """
        try:
            # Volta ao contexto principal
            self.navegador.switch_to.default_content()
            
            # Alterna para nova aba se houver
            for _ in range(30):
                if len(self.navegador.window_handles) > 1:
                    self.navegador.switch_to.window(self.navegador.window_handles[-1])
                    break
                time.sleep(0.1)
            
            # Aguarda a página ficar pronta
            WebDriverWait(self.navegador, 15).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            
            # Aguarda o body
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # Acessa o menu NFE
            menu_nfe = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(., 'NFE/DOCUMENTOS ELETRONICOS')]"))
            )
            menu_nfe.click()
            print("[OK] 'NFE/DOCUMENTOS ELETRONICOS' acessada com sucesso!")
            
            # Entrar em 'Solicitar Arquivos XML'
            solicitar_xml = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(., 'Solicitar Arquivos XML')]"))
            )
            solicitar_xml.click()
            time.sleep(0.2)
            
            # Garante que o body foi renderizado
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # Clica no botão "Novo"
            novo_elemento = self.wait.until(EC.presence_of_element_located((
                By.CSS_SELECTOR,
                "body > table > tbody > tr:nth-child(2) > td:nth-child(2) > table > tbody > tr > td > table:nth-child(6) > tbody > tr > td:nth-child(1) > a"
            )))
            
            # Scroll até o link
            self.navegador.execute_script("arguments[0].scrollIntoView({block: 'center'});", novo_elemento)
            time.sleep(0.1)
            
            # Clica no elemento
            try:
                novo_elemento.click()
            except Exception:
                self.navegador.execute_script("arguments[0].click();", novo_elemento)
            
            print("[OK] Menu de solicitacao XML acessado com sucesso!")
            return True
            
        except Exception as e:
            print(f"[ERRO] Erro ao navegar para menu XML: {e}")
            return False
    
    def voltar_para_nova_solicitacao(self):
        """
        Volta para a página de nova solicitação XML após concluir uma solicitação
        
        Returns:
            bool: True se navegação bem-sucedida, False caso contrário
        """
        try:
            # Aguarda um pouco para a página processar (reduzido para otimização)
            time.sleep(0.2)
            
            # Tenta localizar e clicar no botão "Novo" ou voltar para o menu
            novo_elemento = self.wait.until(EC.presence_of_element_located((
                By.CSS_SELECTOR,
                "body > table > tbody > tr:nth-child(2) > td:nth-child(2) > table > tbody > tr > td > table:nth-child(6) > tbody > tr > td:nth-child(1) > a"
            )))
            
            self.navegador.execute_script("arguments[0].scrollIntoView({block: 'center'});", novo_elemento)
            time.sleep(0.1)
            
            try:
                novo_elemento.click()
            except Exception:
                self.navegador.execute_script("arguments[0].click();", novo_elemento)
            
            print("[OK] Navegado para nova solicitacao!")
            return True
            
        except Exception as e:
            print(f"[AVISO] Nao foi possivel voltar automaticamente. Tentando recarregar... {e}")
            # Se falhar, tenta navegar pelo menu novamente
            return self.navegar_para_menu_xml()
    
    def fechar(self):
        """Fecha o navegador"""
        if self.navegador:
            try:
                self.navegador.quit()
                print("[OK] Navegador fechado com sucesso!")
            except Exception as e:
                print(f"[AVISO] Erro ao fechar navegador: {e}")
    
    def get_driver(self):
        """Retorna o driver do Selenium"""
        return self.navegador
    
    def get_wait(self):
        """Retorna o objeto WebDriverWait"""
        return self.wait
