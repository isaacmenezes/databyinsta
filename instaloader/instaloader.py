import logging
import os
import time
import random
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime

import pandas as pd
import instaloader
from dotenv import load_dotenv


# Configuração logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bulk_scraper.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Carregamento de variáveis
load_dotenv()

IG_USERNAME = os.getenv("IG_USERNAME", "").strip()
IG_PASSWORD = os.getenv("IG_PASSWORD", "").strip()
TARGET_PROFILES = os.getenv("TARGET_PROFILES", "perfil1,perfil2").split(",")
POSTS_PER_PROFILE = int(os.getenv("POSTS_PER_PROFILE", "30"))
REQUEST_DELAY_MIN = int(os.getenv("REQUEST_DELAY_MIN", "2"))
REQUEST_DELAY_MAX = int(os.getenv("REQUEST_DELAY_MAX", "5"))
PROFILE_DELAY_MIN = int(os.getenv("PROFILE_DELAY_MIN", "5"))
PROFILE_DELAY_MAX = int(os.getenv("PROFILE_DELAY_MAX", "10"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

if not IG_USERNAME or not IG_PASSWORD:
    raise ValueError("Credenciais não configuradas no arquivo .env")
@dataclass

class PostRecord:
    profile: str
    post_id: str
    likes: int
    comments: int
    caption: str
    is_video: bool
    date: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "profile": self.profile,
            "post_id": self.post_id,
            "likes": self.likes,
            "comments": self.comments,
            "caption": self.caption,
            "is_video": self.is_video,
            "date": self.date.isoformat() if self.date else None
        }

# ============================================================================
# LOADER
# ============================================================================

def create_loader() -> instaloader.Instaloader:
    """
    Cria instância do Instaloader com configurações otimizadas.
    
    Returns:
        Instaloader configurado para coleta sem download de mídia.
    """
    loader = instaloader.Instaloader(
        download_pictures=False,
        download_videos=False,
        download_comments=False,
        save_metadata=False,
        quiet=True
    )
    logger.debug("Instaloader criado com sucesso")
    return loader


def authenticate(loader: instaloader.Instaloader, username: str, password: str) -> bool:
    """
    Autentica no Instagram usando credenciais ou sessão salva.
    
    Args:
        loader: Instância do Instaloader.
        username: Usuário do Instagram.
        password: Senha do Instagram.
        
    Returns:
        bool: True se autenticado, False caso contrário.
    """
    try:
        loader.load_session_from_file(username)
        logger.info("✓ Sessão carregada com sucesso")
        return True
    except Exception as e:
        logger.warning(f"Sessão não encontrada ({e}), fazendo login...")
        try:
            loader.login(username, password)
            loader.save_session_to_file()
            logger.info("✓ Login realizado e sessão salva")
            return True
        except Exception as auth_error:
            logger.error(f"Falha na autenticação: {auth_error}")
            return False

# ============================================================================
# COLETA
# ============================================================================

def collect_profile_posts(
    loader: instaloader.Instaloader,
    profile_name: str,
    posts_limit: int,
    max_retries: int = MAX_RETRIES
) -> List[PostRecord]:
    """
    Coleta posts de um perfil com retry automático.
    
    Args:
        loader: Instância do Instaloader.
        profile_name: Nome do perfil.
        posts_limit: Quantidade máxima de posts a coletar.
        max_retries: Número máximo de tentativas.
        
    Returns:
        Lista com PostRecord dos posts coletados.
    """
    posts_data: List[PostRecord] = []
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Coletando @{profile_name} (tentativa {attempt + 1}/{max_retries})")
            
            profile = instaloader.Profile.from_username(loader.context, profile_name)
            posts_collected = 0
            
            for post in profile.get_posts():
                if posts_collected >= posts_limit:
                    break
                
                try:
                    post_record = PostRecord(
                        profile=profile_name,
                        post_id=post.shortcode,
                        likes=post.likes,
                        comments=post.comments,
                        caption=post.caption or "",
                        is_video=post.is_video,
                        date=post.date
                    )
                    posts_data.append(post_record)
                    posts_collected += 1
                    logger.debug(f"Post coletado: {post.shortcode}")
                    
                    # Delay entre requisições
                    time.sleep(random.uniform(REQUEST_DELAY_MIN, REQUEST_DELAY_MAX))
                    
                except Exception as post_error:
                    logger.warning(f"Erro ao processar post {post.shortcode}: {post_error}")
                    continue
            
            logger.info(f"✓ {posts_collected} posts coletados de @{profile_name}")
            return posts_data
            
        except instaloader.exceptions.ProfileNotExistsException:
            logger.error(f"Perfil @{profile_name} não encontrado")
            return []
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 10 * (attempt + 1)
                logger.warning(f"Erro na tentativa {attempt + 1}: {e}. Aguardando {wait_time}s...")
                time.sleep(wait_time)
            else:
                logger.error(f"Falha definitiva ao coletar @{profile_name}: {e}")
                return []
    
    return posts_data

# ============================================================================
# MAIN
# ============================================================================

def main() -> None:
    """Função principal: autentica e coleta múltiplos perfis."""
    try:
        logger.info("Iniciando coleta em massa...")
        
        loader = create_loader()
        
        if not authenticate(loader, IG_USERNAME, IG_PASSWORD):
            logger.error("Falha na autenticação, encerrando")
            return
        
        all_posts: List[PostRecord] = []
        profiles = [p.strip() for p in TARGET_PROFILES if p.strip()]
        
        logger.info(f"Coletando {len(profiles)} perfil(is)")
        
        for i, profile in enumerate(profiles, 1):
            logger.info(f"[{i}/{len(profiles)}] Processando @{profile}")
            
            posts = collect_profile_posts(loader, profile, POSTS_PER_PROFILE, MAX_RETRIES)
            all_posts.extend(posts)
            
            if i < len(profiles):
                delay = random.uniform(PROFILE_DELAY_MIN, PROFILE_DELAY_MAX)
                logger.debug(f"Aguardando {delay:.1f}s antes do próximo perfil...")
                time.sleep(delay)
        
        # Salvar dados
        if all_posts:
            records = [post.to_dict() for post in all_posts]
            df = pd.DataFrame(records)
            
            output_file = "dados_brutos.csv"
            df.to_csv(output_file, index=False, encoding="utf-8")
            
            logger.info(f"✓ Coleta concluída: {len(all_posts)} posts salvos em {output_file}")
            logger.info(f"   - Arquivo: {output_file}")
            logger.info(f"   - Tamanho: {len(df)} linhas")
        else:
            logger.warning("Nenhum post foi coletado")
            
    except Exception as e:
        logger.critical(f"Erro fatal: {e}", exc_info=True)


if __name__ == "__main__":
    main()