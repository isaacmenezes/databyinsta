from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

import pandas as pd
import time
import random
import json

USUARIO = "poorgalinda"
SENHA = "pe@rlofS3a"

PERFIS = [
    "kalyton.psi"
]

POSTS_POR_PERFIL = 10


def iniciar_driver():
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--start-maximized")
    
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def login(driver):
    driver.get("https://www.instagram.com/")
    
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.TAG_NAME, "input"))
    )

    inputs = driver.find_elements(By.TAG_NAME, "input")
    inputs[0].send_keys(USUARIO)
    inputs[1].send_keys(SENHA)
    inputs[1].send_keys(Keys.ENTER)

    time.sleep(8)

    # Fechar popups
    try:
        botoes = driver.find_elements(By.XPATH, "//button")
        for botao in botoes:
            texto = botao.text.lower()
            if "agora não" in texto or "not now" in texto:
                botao.click()
                time.sleep(1)
    except:
        pass


def extrair_dados_feed(driver, perfil):
    """Extrai dados dos posts visíveis no feed do perfil (sem abrir cada um)"""
    driver.get(f"https://www.instagram.com/{perfil}/")
    time.sleep(3)

    dados = []
    links_vistos = set()

    # Fazer scroll para carregar mais posts
    for scroll_i in range(5):
        print(f"  Scroll {scroll_i+1}/5...")
        
        # Executar JavaScript para extrair dados
        script = """
        const posts = [];
        const articles = document.querySelectorAll('a[href*="/p/"]');
        
        for (let link of articles) {
            const href = link.getAttribute('href');
            if (href && href.includes('/p/')) {
                posts.push(href);
            }
        }
        
        return posts;
        """
        
        links = driver.execute_script(script)
        
        # Remover duplicatas
        novos_links = [l for l in links if l not in links_vistos]
        links_vistos.update(links)
        
        print(f"     Links encontrados até agora: {len(links_vistos)}")
        
        if len(links_vistos) >= POSTS_POR_PERFIL:
            break
        
        # Scroll
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

    # Pegar os primeiros N links
    links_finais = list(links_vistos)[:POSTS_POR_PERFIL]
    
    print(f"\n✓ Total de posts para coletar: {len(links_finais)}")
    
    # Para cada post, abrir em uma nova aba e extrair dados básicos
    for i, link in enumerate(links_finais, 1):
        try:
            print(f"  [{i}/{len(links_finais)}] Abrindo: {link}")
            
            # Abrir post em nova aba
            driver.execute_script(f"window.open('{link}', '_blank');")
            time.sleep(1)
            
            # Mudar para a nova aba
            driver.switch_to.window(driver.window_handles[-1])
            time.sleep(2)
            
            # Tentar extrair dados da página
            try:
                # Tentar pegar likes
                likes_text = "0"
                likes_elements = driver.find_elements(By.XPATH, "//button[contains(., 'gosto')]")
                if not likes_elements:
                    likes_elements = driver.find_elements(By.XPATH, "//a[contains(@href, '/like')]")
                
                if likes_elements:
                    likes_text = likes_elements[0].text.split()[0]
                
                # Tentar pegar comentários
                comments_text = "0"
                comment_elements = driver.find_elements(By.XPATH, "//button[contains(., 'comentário')]")
                if comment_elements:
                    comments_text = comment_elements[0].text.split()[0]
                
                # Caption
                caption = ""
                try:
                    caption_el = driver.find_element(By.XPATH, "//div[@role='dialog']//div[@data-testid='post-caption']")
                    caption = caption_el.text[:100]
                except:
                    pass
                
                dados.append({
                    "profile": perfil,
                    "link": link,
                    "likes": likes_text,
                    "comments": comments_text,
                    "caption": caption
                })
                
                print(f"     ✓ Likes: {likes_text}, Comentários: {comments_text}")
                
            except Exception as e:
                print(f"     ⚠️ Erro extraindo dados: {str(e)[:50]}")
                dados.append({
                    "profile": perfil,
                    "link": link,
                    "likes": "N/A",
                    "comments": "N/A",
                    "caption": ""
                })
            
            # Fechar aba
            driver.close()
            time.sleep(1)
            
            # Voltar para a aba original
            driver.switch_to.window(driver.window_handles[0])
            
            time.sleep(random.uniform(1, 2))
            
        except Exception as e:
            print(f"     ❌ Erro ao processar post: {e}")
            # Tentar voltar para aba original
            try:
                driver.switch_to.window(driver.window_handles[0])
            except:
                pass

    return dados


def main():
    driver = iniciar_driver()
    
    try:
        print("Fazendo login...")
        login(driver)
        print("✅ Login realizado!\n")
        
        todos_dados = []
        
        for perfil in PERFIS:
            print(f"Coletando perfil: {perfil}")
            dados = extrair_dados_feed(driver, perfil)
            todos_dados.extend(dados)
            
            time.sleep(random.uniform(3, 5))
        
        # Salvar dados
        if todos_dados:
            df = pd.DataFrame(todos_dados)
            df.to_csv("dados_instagram.csv", index=False)
            print(f"\n✅ Sucesso! {len(todos_dados)} posts salvos em 'dados_instagram.csv'")
        else:
            print("\n❌ Nenhum dado foi coletado")
    
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
