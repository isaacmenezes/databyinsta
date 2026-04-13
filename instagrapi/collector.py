import csv
import logging
import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, PleaseLoginAgain

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("collector.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()

IG_USERNAME = os.getenv("IG_USERNAME", "").strip()
IG_PASSWORD = os.getenv("IG_PASSWORD", "").strip()
SESSION_FILE = os.getenv("SESSION_FILE", "session.json")

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


def authenticate(username: str, password: str) -> Optional[Client]:
    try:
        client = Client()

        if Path(SESSION_FILE).exists():
            logger.info("Carregando sessão salva...")
            client.load_settings(SESSION_FILE)
            client.login(username, password)
            logger.info("✓ Sessão restaurada com sucesso")
        else:
            logger.info("Nenhuma sessão encontrada, autenticando...")
            client.login(username, password)
            client.dump_settings(SESSION_FILE)
            logger.info(f"✓ Autenticação bem-sucedida, sessão salva em '{SESSION_FILE}'")

        return client

    except (LoginRequired, PleaseLoginAgain):
        logger.warning("Sessão expirada, refazendo login...")
        try:
            client = Client()
            client.login(username, password)
            client.dump_settings(SESSION_FILE)
            logger.info("✓ Reautenticação bem-sucedida")
            return client
        except Exception as e:
            logger.error(f"Falha ao reautenticar: {e}")
            return None
    except Exception as e:
        logger.error(f"Erro durante autenticação: {e}")
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
        client = authenticate(IG_USERNAME, IG_PASSWORD)
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