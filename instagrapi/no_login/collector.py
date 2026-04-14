import csv
import logging
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
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


WEEKDAYS = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]


def resolve_post_type(media_type: int, product_type: str) -> str:
    if media_type == 1:
        return "Imagem"
    if media_type == 8:
        return "Carrossel"
    if media_type == 2:
        return "Reel" if product_type == "clips" else "Vídeo"
    return "Desconhecido"


@dataclass
class PostData:
    position: int
    url: str
    post_type: str
    likes: int
    comments: int
    views: Any
    caption_length: int
    hashtags_count: int
    mentions_count: int
    hour_posted: str
    weekday: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Seq": self.position,
            "URL": self.url,
            "Tipo": self.post_type,
            "Likes": self.likes,
            "Comentários": self.comments,
            "Visualizações": self.views if self.views is not None else "N/A",
            "Tamanho Legenda": self.caption_length,
            "Hashtags": self.hashtags_count,
            "Menções": self.mentions_count,
            "Hora": self.hour_posted,
            "Dia da Semana": self.weekday,
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
            caption = media.caption_text or ""
            product_type = getattr(media, "product_type", "") or ""
            taken_at: datetime = media.taken_at

            post_data = PostData(
                position=position,
                url=f"https://www.instagram.com/p/{media.code}/",
                post_type=resolve_post_type(media.media_type, product_type),
                likes=media.like_count,
                comments=media.comment_count,
                views=getattr(media, "play_count", None) if media.media_type == 2 else None,
                caption_length=len(caption),
                hashtags_count=len(re.findall(r"#\w+", caption)),
                mentions_count=len(re.findall(r"@\w+", caption)),
                hour_posted=taken_at.strftime("%H:%M") if taken_at else "N/A",
                weekday=WEEKDAYS[taken_at.weekday()] if taken_at else "N/A",
            )
            posts.append(post_data)
            logger.debug(f"Post {position}: likes={post_data.likes}, type={post_data.post_type}")

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
        print(f"    Tipo: {post.post_type}")
        print(f"    Likes: {post.likes:,}")
        print(f"    Comentários: {post.comments:,}")
        if post.views is not None:
            print(f"    Visualizações: {post.views:,}")
        print(f"    Tamanho Legenda: {post.caption_length}")
        print(f"    Hashtags: {post.hashtags_count}")
        print(f"    Menções: {post.mentions_count}")
        print(f"    Hora: {post.hour_posted}")
        print(f"    Dia da Semana: {post.weekday}")

    print("\n" + "=" * 50 + "\n")


def main() -> None:
    try:
        client = authenticate()
        if not client:
            logger.error("Impossível continuar sem autenticação")
            return

        raw_profiles = os.getenv("TARGET_PROFILES", os.getenv("TARGET_PROFILE", "neymarjr"))
        target_profiles = [p.strip() for p in raw_profiles.split(",") if p.strip()]

        try:
            post_limit = int(os.getenv("POST_LIMIT", "10"))
        except ValueError:
            logger.warning("POST_LIMIT inválido, usando valor padrão de 10")
            post_limit = 10

        logger.info(f"Perfis na fila: {target_profiles}")

        for username in target_profiles:
            logger.info(f"--- Iniciando coleta: @{username} ---")
            profile_data = fetch_profile_posts(client, username, post_limit)

            if profile_data:
                display_profile_data(profile_data)
                save_to_csv(profile_data)
            else:
                logger.error(f"Falha ao coletar @{username}, pulando...")

        logger.info("Todas as coletas concluídas")

    except Exception as e:
        logger.critical(f"Erro fatal: {e}", exc_info=True)


if __name__ == "__main__":
    main()