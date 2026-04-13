"""
Instagram Web Scraper - Coleta de dados de perfis usando Selenium.

Dependências: selenium, pandas, python-dotenv, webdriver-manager

Uso:
    python complete_version.py
"""

import logging
import os
import time
import random
from typing import Optional, Set, List, Dict, Any
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


# Configuração logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("scraper.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Carregamento de variáveis ambiente
load_dotenv()

# Configurações
IG_USERNAME = os.getenv("IG_USERNAME", "").strip()
IG_PASSWORD = os.getenv("IG_PASSWORD", "").strip()
TARGET_PROFILES = os.getenv("TARGET_PROFILES", "kalyton.psi").split(",")
POSTS_PER_PROFILE = int(os.getenv("POSTS_PER_PROFILE", "10"))
DRIVER_TIMEOUT = int(os.getenv("DRIVER_TIMEOUT", "15"))
LOGIN_WAIT = int(os.getenv("LOGIN_WAIT_TIME", "8"))

# Validação de credenciais
if not IG_USERNAME or not IG_PASSWORD:
    raise ValueError("Credenciais não configuradas no arquivo .env")

# ============================================================================
# DRIVER
# ============================================================================

def setup_driver() -> webdriver.Chrome:
    """
    Configura e retorna uma instância do Chrome Driver com otimizações.
    
    Returns:
        webdriver.Chrome: Driver configurado e pronto para uso.
    """
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    
    # Otimizações para evitar bloqueios
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--start-maximized")
    
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(DRIVER_TIMEOUT)
    
    logger.info("Driver inicializado com sucesso")
    return driver


# ============================================================================
# AUTENTICAÇÃO
# ============================================================================

def close_popups(driver: webdriver.Chrome) -> None:
    """
    Fecha popups e modais comuns após login (notificações, cookies, etc).
    
    Args:
        driver: Instância do Chrome Driver.
    """
    try:
        buttons = driver.find_elements(By.XPATH, "//button")
        dismiss_texts = ["agora não", "not now", "ignore", "close"]
        
        for button in buttons:
            text = button.text.lower().strip()
            if any(dismiss in text for dismiss in dismiss_texts):
                try:
                    button.click()
                    time.sleep(1)
                except Exception:
                    pass
    except Exception as e:
        logger.debug(f"Erro ao fechar popups: {e}")


def perform_login(driver: webdriver.Chrome, username: str, password: str) -> bool:
    """
    Realiza login no Instagram.
    
    Args:
        driver: Instância do Chrome Driver.
        username: Usuário do Instagram.
        password: Senha do Instagram.
        
    Returns:
        bool: True se login foi bem-sucedido, False caso contrário.
    """
    try:
        logger.info("Iniciando login...")
        driver.get("https://www.instagram.com/")
        
        # Aguardar campos de entrada
        WebDriverWait(driver, DRIVER_TIMEOUT).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "input"))
        )
        
        inputs = driver.find_elements(By.TAG_NAME, "input")
        if len(inputs) < 2:
            logger.error("Campos de login não encontrados")
            return False
        
        inputs[0].send_keys(username)
        inputs[1].send_keys(password)
        inputs[1].send_keys(Keys.ENTER)
        
        logger.info("Credenciais enviadas, aguardando confirmação...")
        time.sleep(LOGIN_WAIT)
        close_popups(driver)
        
        logger.info("✓ Login realizado com sucesso")
        return True
        
    except Exception as e:
        logger.error(f"Erro durante login: {e}")
        return False

# ============================================================================
# COLETA DE POSTS
# ============================================================================

def collect_post_links(driver: webdriver.Chrome, profile: str, limit: int) -> List[str]:
    """
    Coleta links de posts de um perfil fazendo scroll.
    
    Args:
        driver: Instância do Chrome Driver.
        profile: Nome do perfil do Instagram.
        limit: Quantidade máxima de posts a coletar.
        
    Returns:
        Lista com URLs dos posts encontrados.
    """
    try:
        logger.info(f"Coletando posts do perfil: {profile}")
        driver.get(f"https://www.instagram.com/{profile}/")
        time.sleep(3)
        
        WebDriverWait(driver, DRIVER_TIMEOUT).until(
            EC.presence_of_element_located((By.XPATH, "//article"))
        )
    except Exception as e:
        logger.warning(f"Perfil {profile} não carregou completamente: {e}")
    
    post_links: Set[str] = set()
    scroll_attempts = 5
    
    for scroll_i in range(scroll_attempts):
        try:
            # Executar script para coletar links de posts
            script = """
            const posts = new Set();
            const links = document.querySelectorAll('a[href*="/p/"]');
            for (let link of links) {
                const href = link.getAttribute('href');
                if (href && href.includes('/p/')) {
                    posts.add(href);
                }
            }
            return Array.from(posts);
            """
            
            links = driver.execute_script(script)
            post_links.update(links)
            
            if len(post_links) >= limit:
                break
            
            logger.debug(f"Scroll {scroll_i + 1}: {len(post_links)} posts encontrados")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(2, 4))
            
        except Exception as e:
            logger.debug(f"Erro durante scroll: {e}")
            continue
    
    result = list(post_links)[:limit]
    logger.info(f"Total de posts coletados: {len(result)}")
    return result

# ============================================================================
# EXTRAÇÃO DE DADOS
# ============================================================================

def extract_likes(driver: webdriver.Chrome) -> str:
    """
    Extrai quantidade de likes do post atual.
    
    Args:
        driver: Instância do Chrome Driver.
        
    Returns:
        str: Quantidade de likes ou "N/A" se não encontrado.
    """
    try:
        selectors = [
            "//button//span[contains(text(), 'gosto')]",
            "//button//span[contains(text(), 'like')]",
        ]
        
        for selector in selectors:
            try:
                element = driver.find_element(By.XPATH, selector)
                return element.text.strip()
            except Exception:
                continue
        
        return "N/A"
    except Exception as e:
        logger.debug(f"Erro ao extrair likes: {e}")
        return "N/A"


def extract_comments_count(driver: webdriver.Chrome) -> str:
    """
    Extrai quantidade de comentários do post atual.
    
    Args:
        driver: Instância do Chrome Driver.
        
    Returns:
        str: Quantidade de comentários ou "0" se não encontrado.
    """
    try:
        selector = "//button[contains(., 'comentário')]"
        element = driver.find_element(By.XPATH, selector)
        return element.text.split()[0] if element.text else "0"
    except Exception:
        return "0"


def extract_caption(driver: webdriver.Chrome) -> str:
    """
    Extrai caption (descrição) do post atual.
    
    Args:
        driver: Instância do Chrome Driver.
        
    Returns:
        str: Caption truncada em 200 caracteres ou string vazia.
    """
    try:
        selectors = [
            "//div[@role='dialog']//div[@data-testid='post-caption']",
            "//div[contains(@class, 'caption')]//span",
        ]
        
        for selector in selectors:
            try:
                element = driver.find_element(By.XPATH, selector)
                caption = element.text.strip()
                return caption[:200] if caption else ""
            except Exception:
                continue
        
        return ""
    except Exception as e:
        logger.debug(f"Erro ao extrair caption: {e}")
        return ""


def extract_post_data(driver: webdriver.Chrome, post_url: str, profile: str) -> Optional[Dict[str, Any]]:
    """
    Extrai dados completos de um post.
    
    Args:
        driver: Instância do Chrome Driver.
        post_url: URL do post.
        profile: Nome do perfil.
        
    Returns:
        Dict com dados do post ou None se houver erro.
    """
    max_attempts = 3
    
    for attempt in range(max_attempts):
        try:
            driver.get(post_url)
            WebDriverWait(driver, DRIVER_TIMEOUT).until(
                EC.presence_of_element_located((By.TAG_NAME, "article"))
            )
            time.sleep(2)
            
            post_data = {
                "profile": profile,
                "link": post_url,
                "likes": extract_likes(driver),
                "comments": extract_comments_count(driver),
                "caption": extract_caption(driver),
            }
            
            logger.debug(f"Post extraído: {post_data['likes']} likes, {post_data['comments']} comentários")
            return post_data
            
        except Exception as e:
            if attempt < max_attempts - 1:
                logger.debug(f"Tentativa {attempt + 1} falhou, retentando em 3s...")
                time.sleep(3)
            else:
                logger.warning(f"Falha ao extrair post {post_url}: {e}")
                return None
    
    return None


# ============================================================================
# MAIN
# ============================================================================

def main() -> None:
    """
    Função principal: realiza login e coleta posts de múltiplos perfis.
    """
    driver = None
    
    try:
        driver = setup_driver()
        
        if not perform_login(driver, IG_USERNAME, IG_PASSWORD):
            logger.error("Falha no login, encerrando...")
            return
        
        all_data: List[Dict[str, Any]] = []
        
        for profile in TARGET_PROFILES:
            profile = profile.strip()
            logger.info(f"Iniciando coleta do perfil: {profile}")
            
            try:
                post_links = collect_post_links(driver, profile, POSTS_PER_PROFILE)
                logger.info(f"Extraindo dados de {len(post_links)} posts...")
                
                for i, link in enumerate(post_links, 1):
                    logger.info(f"[{i}/{len(post_links)}] Processando: {link}")
                    
                    post_data = extract_post_data(driver, link, profile)
                    if post_data:
                        all_data.append(post_data)
                    
                    time.sleep(random.uniform(2, 4))
                
                time.sleep(random.uniform(5, 10))
                
            except Exception as e:
                logger.error(f"Erro ao processar perfil {profile}: {e}")
                continue
        
        # Salvar dados
        if all_data:
            df = pd.DataFrame(all_data)
            output_file = "dados_instagram.csv"
            df.to_csv(output_file, index=False, encoding="utf-8")
            logger.info(f"✓ {len(all_data)} registros salvos em {output_file}")
        else:
            logger.warning("Nenhum dado foi coletado")
            
    except Exception as e:
        logger.error(f"Erro fatal: {e}", exc_info=True)
        
    finally:
        if driver:
            driver.quit()
            logger.info("Driver finalizado")


if __name__ == "__main__":
    main()