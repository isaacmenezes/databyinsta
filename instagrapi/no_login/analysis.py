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


# ============================================================================
# CARREGAMENTO E PREPARO
# ============================================================================

def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)

    df["Visualizações"] = pd.to_numeric(df["Visualizações"], errors="coerce")
    df["Engajamento"] = df["Likes"] + df["Comentários"]
    df["Taxa de Engajamento (%)"] = (df["Engajamento"] / df["Seguidores"] * 100).round(4)

    logger.info(f"✓ {len(df)} posts carregados de {df['Perfil'].nunique()} perfil(is)")
    return df


# ============================================================================
# 1. MÉDIA DE ENGAJAMENTO POR PERFIL
# ============================================================================

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


# ============================================================================
# 2. DISTRIBUIÇÃO DE ENGAJAMENTO (HISTOGRAMA)
# ============================================================================

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


# ============================================================================
# 3. HASHTAGS VS ENGAJAMENTO
# ============================================================================

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


# ============================================================================
# 4. TAMANHO DA LEGENDA VS ENGAJAMENTO
# ============================================================================

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


# ============================================================================
# 5. TIPO DE POST VS ENGAJAMENTO
# ============================================================================

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



# ============================================================================
# RELATÓRIO EM TEXTO
# ============================================================================

def generate_text_report(df: pd.DataFrame) -> None:
    lines = []

    def section(title: str) -> None:
        lines.append("\n" + "=" * 60)
        lines.append(f"  {title}")
        lines.append("=" * 60)

    def row(label: str, value: str) -> None:
        lines.append(f"  {label:<35} {value}")

    lines.append("=" * 60)
    lines.append("  RELATÓRIO DE ANÁLISE DE ENGAJAMENTO")
    lines.append(f"  Perfis: {', '.join(f'@{p}' for p in df['Perfil'].unique())}")
    lines.append(f"  Total de posts analisados: {len(df)}")
    lines.append("=" * 60)

    # 0. Geral
    section("0. VISÃO GERAL (TODOS OS PERFIS)")
    row("Total de posts:", f"{len(df)}")
    row("Likes médios:", f"{df['Likes'].mean():,.0f}")
    row("Comentários médios:", f"{df['Comentários'].mean():,.0f}")
    row("Engajamento médio:", f"{df['Engajamento'].mean():,.0f}")
    row("Taxa de engajamento média:", f"{df['Taxa de Engajamento (%)'].mean():.4f}%")
    row("Mediana de engajamento:", f"{df['Engajamento'].median():,.0f}")
    row("Maior engajamento:", f"{df['Engajamento'].max():,.0f}  ({df.loc[df['Engajamento'].idxmax(), 'Perfil']})")
    row("Menor engajamento:", f"{df['Engajamento'].min():,.0f}  ({df.loc[df['Engajamento'].idxmin(), 'Perfil']})")
    lines.append("")
    tipo_mais_comum = df["Tipo"].value_counts().idxmax()
    row("Tipo de post mais comum:", f"{tipo_mais_comum} ({df['Tipo'].value_counts()[tipo_mais_comum]} posts)")
    row("Hashtags médias por post:", f"{df['Hashtags'].mean():.1f}")
    row("Tamanho médio da legenda:", f"{df['Tamanho Legenda'].mean():.0f} caracteres")

    # 1. Média por perfil
    section("1. MÉDIA DE ENGAJAMENTO POR PERFIL")
    for perfil, g in df.groupby("Perfil"):
        lines.append(f"\n  @{perfil} ({g['Seguidores'].iloc[0]:,} seguidores | {len(g)} posts)")
        row("Likes médios:", f"{g['Likes'].mean():,.0f}")
        row("Comentários médios:", f"{g['Comentários'].mean():,.0f}")
        row("Engajamento médio:", f"{g['Engajamento'].mean():,.0f}")
        row("Taxa de engajamento média:", f"{g['Taxa de Engajamento (%)'].mean():.4f}%")
        row("Post com mais engajamento:", f"{g.loc[g['Engajamento'].idxmax(), 'URL']}")
        row("Post com menos engajamento:", f"{g.loc[g['Engajamento'].idxmin(), 'URL']}")

    # 2. Distribuição
    section("2. DISTRIBUIÇÃO DE ENGAJAMENTO")
    for perfil, g in df.groupby("Perfil"):
        lines.append(f"\n  @{perfil}")
        row("Mínimo:", f"{g['Engajamento'].min():,.0f}")
        row("Mediana:", f"{g['Engajamento'].median():,.0f}")
        row("Máximo:", f"{g['Engajamento'].max():,.0f}")
        row("Desvio padrão:", f"{g['Engajamento'].std():,.0f}")

    # 3. Hashtags vs engajamento
    section("3. HASHTAGS VS ENGAJAMENTO")
    corr_ht = df["Hashtags"].corr(df["Taxa de Engajamento (%)"])
    row("Correlação hashtags x taxa (%):", f"{corr_ht:.4f}")
    lines.append("")
    avg_ht = df.groupby("Hashtags")["Taxa de Engajamento (%)"].mean().sort_values(ascending=False)
    lines.append("  Taxa média por nº de hashtags (top 5):")
    for n_ht, taxa in avg_ht.head(5).items():
        lines.append(f"    {n_ht} hashtag(s) → {taxa:.4f}%")

    # 4. Legenda vs engajamento
    section("4. TAMANHO DA LEGENDA VS ENGAJAMENTO")
    corr_cap = df["Tamanho Legenda"].corr(df["Taxa de Engajamento (%)"])
    row("Correlação legenda x taxa (%):", f"{corr_cap:.4f}")
    lines.append("")
    bins = pd.cut(df["Tamanho Legenda"], bins=5)
    avg_cap = df.groupby(bins, observed=True)["Taxa de Engajamento (%)"].mean()
    lines.append("  Taxa média por faixa de tamanho:")
    for faixa, taxa in avg_cap.items():
        lines.append(f"    {str(faixa):<25} → {taxa:.4f}%")

    # 5. Tipo de post vs engajamento
    section("5. TIPO DE POST VS ENGAJAMENTO")
    avg_tipo = df.groupby("Tipo")["Taxa de Engajamento (%)"].mean().sort_values(ascending=False)
    lines.append("")
    for tipo, taxa in avg_tipo.items():
        count = len(df[df["Tipo"] == tipo])
        lines.append(f"  {tipo:<15} → {taxa:.4f}%  ({count} posts)")

    lines.append("\n" + "=" * 60 + "\n")

    report = "\n".join(lines)
    print(report)

    path = OUTPUT_DIR / "relatorio.txt"
    path.write_text(report, encoding="utf-8")
    logger.info(f"✓ Relatório salvo em: {path}")



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
    generate_text_report(df)

    logger.info(f"✓ Análise concluída. Resultados salvos em '{OUTPUT_DIR}'")


if __name__ == "__main__":
    main()