import logging
import os
from typing import Optional, Dict, List, Any
from enum import Enum
from dataclasses import dataclass

from dotenv import load_dotenv
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, PleaseLoginAgain


# Configuração logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("collector.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Carregamento de variáveis
load_dotenv()

IG_USERNAME = os.getenv("IG_USERNAME", "").strip()
IG_PASSWORD = os.getenv("IG_PASSWORD", "").strip()

if not IG_USERNAME or not IG_PASSWORD:
    raise ValueError("Credenciais não configuradas no arquivo .env")


class MediaType(Enum):
    PHOTO = (1, "Foto")
    VIDEO = (2, "Vídeo/Reel")
    CAROUSEL = (8, "Carrossel")
    UNKNOWN = (-1, "Desconhecido")
    
    def __init__(self, code: int, label: str):
        self.code = code
        self.label = label
    
    @classmethod
    def from_code(cls, code: int) -> "MediaType":
        for media_type in cls:
            if media_type.code == code:
                return media_type
        return cls.UNKNOWN


@dataclass
class PostData:
    position: int
    url: str
    type: str
    likes: int
    comments: int
    views: Any

    # conversao -> dicionario
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "Seq": self.position,
            "URL": self.url,
            "Tipo": self.type,
            "Likes": self.likes,
            "Comentários": self.comments,
            "Visualizações": self.views or "N/A"
        }


@dataclass
class ProfileData:
    username: str
    followers: int
    posts: List[PostData]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "Conta": self.username,
            "Seguidores": self.followers,
            "Posts": [p.to_dict() for p in self.posts]
        }

def authenticate(username: str, password: str) -> Optional[Client]:
    try:
        logger.info("Iniciando autenticação...")
        client = Client()
        client.login(username, password)
        logger.info("✓ Autenticação bem-sucedida")
        return client
    except (LoginRequired, PleaseLoginAgain) as e:
        logger.error(f"Falha de autenticação: {e}")
        return None
    except Exception as e:
        logger.error(f"Erro durante autenticação: {e}")
        return None


def fetch_profile_posts(
    client: Client, 
    username: str, 
    post_limit: int = 10
) -> Optional[ProfileData]:
    try:
        logger.info(f"Coletando perfil: @{username}")
        
        user_id = client.user_id_from_username(username)
        user_info = client.user_info(user_id)
        logger.info(f"Perfil encontrado: @{user_info.username} ({user_info.follower_count} seguidores)")
        
        logger.info(f"Coletando {post_limit} posts...")
        medias = client.user_medias(user_id, amount=post_limit)
        
        posts: List[PostData] = []
        for position, media in enumerate(medias, start=1):
            media_type = MediaType.from_code(media.media_type)
            
            # Extrai visualizações apenas para vídeos
            views = getattr(media, "play_count", 0) if media.media_type == 2 else None
            
            post_url = f"https://www.instagram.com/p/{media.code}/"
            post_data = PostData(
                position=position,
                url=post_url,
                type=media_type.label,
                likes=media.like_count,
                comments=media.comment_count,
                views=views
            )
            posts.append(post_data)
            logger.debug(f"Post {position}: likes={post_data.likes}, comments={post_data.comments}, type={post_data.type}")
        
        profile_data = ProfileData(
            username=user_info.username,
            followers=user_info.follower_count,
            posts=posts
        )
        
        logger.info(f"✓ {len(posts)} posts coletados com sucesso")
        return profile_data
        
    except Exception as e:
        logger.error(f"Erro ao coletar perfil @{username}: {e}")
        return None


def display_profile_data(data: ProfileData) -> None:
    print("\n" + "=" * 50)
    print(f"  PERFIL: @{data.username}")
    print(f"  SEGUIDORES: {data.followers:,}")
    print("=" * 50)
    
    for post in data.posts:
        print(f"\n  Post #{post.position}")
        print(f"    URL: {post.url}")
        print(f"    Tipo: {post.type}")
        print(f"    Likes: {post.likes:,}")
        print(f"    Comentários: {post.comments:,}")
        if post.views:
            print(f"    Visualizações: {post.views:,}")
    
    print("\n" + "=" * 50 + "\n")

def main() -> None:
    """Função principal: autentica e coleta perfil."""
    try:
        client = authenticate(IG_USERNAME, IG_PASSWORD)
        if not client:
            logger.error("Impossível continuar sem autenticação")
            return
        
        target_profile = os.getenv("TARGET_PROFILE", "neymarjr").strip()
        post_limit = int(os.getenv("POST_LIMIT", "10"))
        
        profile_data = fetch_profile_posts(client, target_profile, post_limit)
        
        if profile_data:
            display_profile_data(profile_data)
            logger.info("Coleta concluída com sucesso")
        else:
            logger.error("Falha ao coletar dados do perfil")
            
    except Exception as e:
        logger.critical(f"Erro fatal: {e}", exc_info=True)


if __name__ == "__main__":
    main()