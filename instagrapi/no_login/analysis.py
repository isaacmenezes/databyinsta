import logging
import sys
import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
import seaborn as sns

warnings.filterwarnings("ignore")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(stream=open(sys.stdout.fileno(), mode="w", encoding="utf-8", closefd=False))
    ]
)
logger = logging.getLogger(__name__)

CSV_PATH = "output/posts.csv"
OUTPUT_DIR = Path("output/analysis")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PALETTE = "Set2"
FIGSIZE = (10, 6)

sns.set_theme(style="whitegrid", palette=PALETTE)

def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)

    df["Visualizações"] = pd.to_numeric(df["Visualizações"], errors="coerce")
    df["Engajamento"] = df["Likes"] + df["Comentários"]
    df["Taxa de Engajamento (%)"] = (df["Engajamento"] / df["Seguidores"] * 100).round(4)

    logger.info(f"✓ {len(df)} posts carregados de {df['Perfil'].nunique()} perfil(is)")
    return df


# media de engajamento por perfil (barplot) e taxa média de engajamento (%) por perfil (barplot)

def plot_avg_engagement(df: pd.DataFrame) -> None:
    summary = (
        df.groupby("Perfil")
        .agg(
            Posts=("Engajamento", "count"),
            Likes_Medio=("Likes", "mean"),
            Comentarios_Medio=("Comentários", "mean"),
            Engajamento_Medio=("Engajamento", "mean"),
            Taxa_Media=("Taxa de Engajamento (%)", "mean"),
        )
        .round(2)
        .reset_index()
    )

    print("\n" + "=" * 60)
    print("  MÉDIA DE ENGAJAMENTO POR PERFIL")
    print("=" * 60)
    print(summary.to_string(index=False))
    print("=" * 60 + "\n")

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle("Média de Engajamento por Perfil", fontsize=14, fontweight="bold")

    sns.barplot(data=summary, x="Perfil", y="Engajamento_Medio", ax=axes[0], palette=PALETTE)
    axes[0].set_title("Engajamento Médio (Likes + Comentários)")
    axes[0].set_xlabel("Perfil")
    axes[0].set_ylabel("Engajamento Médio")
    axes[0].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    for bar in axes[0].patches:
        axes[0].text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + bar.get_height() * 0.01,
            f"{bar.get_height():,.0f}",
            ha="center", va="bottom", fontsize=9
        )

    sns.barplot(data=summary, x="Perfil", y="Taxa_Media", ax=axes[1], palette=PALETTE)
    axes[1].set_title("Taxa de Engajamento Média (%)")
    axes[1].set_xlabel("Perfil")
    axes[1].set_ylabel("Taxa (%)")
    for bar in axes[1].patches:
        axes[1].text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + bar.get_height() * 0.01,
            f"{bar.get_height():.4f}%",
            ha="center", va="bottom", fontsize=9
        )

    plt.tight_layout()
    path = OUTPUT_DIR / "1_engajamento_por_perfil.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    logger.info(f"✓ Salvo: {path}")


# distribuição de engajamento (histograma) por perfil, para engajamento absoluto e taxa de engajamento (%)

def plot_engagement_distribution(df: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle("Distribuição de Engajamento", fontsize=14, fontweight="bold")

    profiles = df["Perfil"].unique()
    colors = sns.color_palette(PALETTE, len(profiles))

    for profile, color in zip(profiles, colors):
        subset = df[df["Perfil"] == profile]
        sns.histplot(subset["Engajamento"], ax=axes[0], label=profile, color=color, kde=True, alpha=0.5, bins=15)

    axes[0].set_title("Engajamento Absoluto (Likes + Comentários)")
    axes[0].set_xlabel("Engajamento")
    axes[0].set_ylabel("Frequência")
    axes[0].xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    axes[0].legend(title="Perfil")

    for profile, color in zip(profiles, colors):
        subset = df[df["Perfil"] == profile]
        sns.histplot(subset["Taxa de Engajamento (%)"], ax=axes[1], label=profile, color=color, kde=True, alpha=0.5, bins=15)

    axes[1].set_title("Taxa de Engajamento (%)")
    axes[1].set_xlabel("Taxa (%)")
    axes[1].set_ylabel("Frequência")
    axes[1].legend(title="Perfil")

    plt.tight_layout()
    path = OUTPUT_DIR / "2_distribuicao_engajamento.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    logger.info(f"✓ Salvo: {path}")


# hashtags vs engajamento absoluto (scatter) e taxa média (lineplot)

def plot_hashtags_vs_engagement(df: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle("Hashtags vs Engajamento", fontsize=14, fontweight="bold")

    sns.scatterplot(
        data=df, x="Hashtags", y="Engajamento",
        hue="Perfil", palette=PALETTE, alpha=0.7, ax=axes[0]
    )
    axes[0].set_title("Nº de Hashtags vs Engajamento")
    axes[0].set_xlabel("Nº de Hashtags")
    axes[0].set_ylabel("Engajamento")
    axes[0].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))

    avg = df.groupby("Hashtags")["Taxa de Engajamento (%)"].mean().reset_index()
    sns.lineplot(data=avg, x="Hashtags", y="Taxa de Engajamento (%)", ax=axes[1], marker="o", color="steelblue")
    axes[1].set_title("Nº de Hashtags vs Taxa de Engajamento Média (%)")
    axes[1].set_xlabel("Nº de Hashtags")
    axes[1].set_ylabel("Taxa Média (%)")

    plt.tight_layout()
    path = OUTPUT_DIR / "3_hashtags_vs_engajamento.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    logger.info(f"✓ Salvo: {path}")


# tamanho da legenda (nº de caracteres) vs engajamento absoluto (scatter) e taxa média (barplot)

def plot_caption_vs_engagement(df: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle("Tamanho da Legenda vs Engajamento", fontsize=14, fontweight="bold")

    sns.scatterplot(
        data=df, x="Tamanho Legenda", y="Engajamento",
        hue="Perfil", palette=PALETTE, alpha=0.7, ax=axes[0]
    )
    axes[0].set_title("Tamanho da Legenda vs Engajamento")
    axes[0].set_xlabel("Caracteres na Legenda")
    axes[0].set_ylabel("Engajamento")
    axes[0].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))

    bins = pd.cut(df["Tamanho Legenda"], bins=5)
    avg = df.groupby(bins, observed=True)["Taxa de Engajamento (%)"].mean().reset_index()
    avg["Tamanho Legenda"] = avg["Tamanho Legenda"].astype(str)
    sns.barplot(data=avg, x="Tamanho Legenda", y="Taxa de Engajamento (%)", ax=axes[1], palette=PALETTE)
    axes[1].set_title("Faixas de Legenda vs Taxa de Engajamento Média (%)")
    axes[1].set_xlabel("Tamanho da Legenda (faixas)")
    axes[1].set_ylabel("Taxa Média (%)")
    axes[1].tick_params(axis="x", rotation=20)

    plt.tight_layout()
    path = OUTPUT_DIR / "4_legenda_vs_engajamento.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    logger.info(f"✓ Salvo: {path}")


# tipo de post vs engajamento absoluto (boxplot) e taxa média (barplot)

def plot_post_type_vs_engagement(df: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle("Tipo de Post vs Engajamento", fontsize=14, fontweight="bold")

    sns.boxplot(data=df, x="Tipo", y="Engajamento", palette=PALETTE, ax=axes[0])
    axes[0].set_title("Distribuição de Engajamento por Tipo")
    axes[0].set_xlabel("Tipo de Post")
    axes[0].set_ylabel("Engajamento")
    axes[0].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))

    avg = df.groupby("Tipo")["Taxa de Engajamento (%)"].mean().reset_index().sort_values("Taxa de Engajamento (%)", ascending=False)
    sns.barplot(data=avg, x="Tipo", y="Taxa de Engajamento (%)", palette=PALETTE, ax=axes[1])
    axes[1].set_title("Taxa de Engajamento Média (%) por Tipo")
    axes[1].set_xlabel("Tipo de Post")
    axes[1].set_ylabel("Taxa Média (%)")
    for bar in axes[1].patches:
        axes[1].text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + bar.get_height() * 0.01,
            f"{bar.get_height():.4f}%",
            ha="center", va="bottom", fontsize=9
        )

    plt.tight_layout()
    path = OUTPUT_DIR / "5_tipo_post_vs_engajamento.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    logger.info(f"✓ Salvo: {path}")


# main

def main() -> None:
    if not Path(CSV_PATH).exists():
        logger.error(f"CSV não encontrado em '{CSV_PATH}'. Rode o collector.py primeiro.")
        return

    df = load_data(CSV_PATH)

    plot_avg_engagement(df)
    plot_engagement_distribution(df)
    plot_hashtags_vs_engagement(df)
    plot_caption_vs_engagement(df)
    plot_post_type_vs_engagement(df)

    logger.info(f"✓ Análise concluída. Gráficos salvos em '{OUTPUT_DIR}'")


if __name__ == "__main__":
    main()