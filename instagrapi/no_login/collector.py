import csv
import logging
import os
from dataclasses import dataclass
from enum import Enum
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from instagrapi import Client
from instagrapi.exceptions import LoginRequired

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("collector.log", encoding="utf-8"),
        logging.StreamHandler(stream=open(sys.stdout.fileno(), mode="w", encoding="utf-8", closefd=False))
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()

IG_SESSION_ID = os.getenv("IG_SESSION_ID", "").strip()

if not IG_SESSION_ID:
    raise ValueError("IG_SESSION_ID não configurado no arquivo .env")


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

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Seq": self.position,
            "URL": self.url,
            "Tipo": self.type,
            "Likes": self.likes,
            "Comentários": self.comments,
            "Visualizações": self.views if self.views is not None else "N/A"
        }


@dataclass
class ProfileData:
    username: str
    followers: int
    posts: List[PostData]


def authenticate() -> Optional[Client]:
    try:
        logger.info("Autenticando via session ID...")
        client = Client()
        client.login_by_sessionid(IG_SESSION_ID)
        logger.info("✓ Sessão válida")
        return client
    except LoginRequired:
        logger.error("Session ID expirado ou inválido.")
        return None
    except Exception as e:
        logger.error(f"Erro ao autenticar: {e}")
        return None


def fetch_profile_posts(client: Client, username: str, post_limit: int = 10) -> Optional[ProfileData]:
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
            views = getattr(media, "play_count", None) if media.media_type == 2 else None

            post_data = PostData(
                position=position,
                url=f"https://www.instagram.com/p/{media.code}/",
                type=media_type.label,
                likes=media.like_count,
                comments=media.comment_count,
                views=views
            )
            posts.append(post_data)
            logger.debug(f"Post {position}: likes={post_data.likes}, comments={post_data.comments}, type={post_data.type}")

        logger.info(f"✓ {len(posts)} posts coletados com sucesso")
        return ProfileData(username=user_info.username, followers=user_info.follower_count, posts=posts)

    except Exception as e:
        logger.error(f"Erro ao coletar perfil @{username}: {e}")
        return None


def save_to_csv(data: ProfileData, output_dir: str = "output") -> str:
    Path(output_dir).mkdir(exist_ok=True)
    filepath = Path(output_dir) / f"{data.username}_posts.csv"

    rows = [p.to_dict() for p in data.posts]
    if not rows:
        logger.warning("Nenhum post para salvar")
        return ""

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    logger.info(f"✓ CSV salvo em: {filepath}")
    return str(filepath)


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
        if post.views is not None:
            print(f"    Visualizações: {post.views:,}")

    print("\n" + "=" * 50 + "\n")


def main() -> None:
    try:
        client = authenticate()
        if not client:
            logger.error("Impossível continuar sem autenticação")
            return

        target_profile = os.getenv("TARGET_PROFILE", "neymarjr").strip()

        try:
            post_limit = int(os.getenv("POST_LIMIT", "10"))
        except ValueError:
            logger.warning("POST_LIMIT inválido, usando valor padrão de 10")
            post_limit = 10

        profile_data = fetch_profile_posts(client, target_profile, post_limit)

        if profile_data:
            display_profile_data(profile_data)
            save_to_csv(profile_data)
            logger.info("Coleta concluída com sucesso")
        else:
            logger.error("Falha ao coletar dados do perfil")

    except Exception as e:
        logger.critical(f"Erro fatal: {e}", exc_info=True)


if __name__ == "__main__":
    main()