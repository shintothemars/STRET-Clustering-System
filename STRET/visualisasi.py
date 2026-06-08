import io
import os
import base64

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import numpy as np
import pandas as pd


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def _fig_to_base64(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=120, facecolor=fig.get_facecolor())
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return img_str


CLUSTER_COLORS = {
    "Sepi": "#4A90D9",
    "Normal": "#27AE60",
    "Padat": "#E74C3C",
}

PALETTE = ["#4A90D9", "#27AE60", "#E74C3C"]
BG = "#1E2130"
CARD_BG = "#252A3B"
TEXT = "#E0E6F1"


def _setup_fig(w=8, h=5):
    fig, ax = plt.subplots(figsize=(w, h), facecolor=BG)
    ax.set_facecolor(CARD_BG)
    ax.tick_params(colors=TEXT)
    ax.xaxis.label.set_color(TEXT)
    ax.yaxis.label.set_color(TEXT)
    ax.title.set_color(TEXT)
    for spine in ax.spines.values():
        spine.set_edgecolor("#3A4060")
    return fig, ax


# ─────────────────────────────────────────────
# 1. Histogram Sesi Foto
# ─────────────────────────────────────────────

def plot_histogram(df: pd.DataFrame) -> str:
    fig, ax = _setup_fig(8, 5)
    n, bins, patches = ax.hist(df["Sesi Foto"], bins=15, color="#4A90D9",
                                edgecolor="#1E2130", alpha=0.9)
    ax.set_xlabel("Jumlah Sesi Foto", fontsize=11)
    ax.set_ylabel("Frekuensi", fontsize=11)
    ax.set_title("Histogram Distribusi Sesi Foto", fontsize=13, fontweight="bold")
    ax.grid(axis="y", linestyle="--", alpha=0.3, color=TEXT)
    return _fig_to_base64(fig)


# ─────────────────────────────────────────────
# 2. Boxplot Sesi Foto per Lokasi
# ─────────────────────────────────────────────

def plot_boxplot(df: pd.DataFrame) -> str:
    fig, ax = _setup_fig(8, 5)
    lokasi_list = df["Lokasi"].unique().tolist()
    data_bp = [df[df["Lokasi"] == l]["Sesi Foto"].values for l in lokasi_list]
    bp = ax.boxplot(data_bp, patch_artist=True, notch=False,
                    medianprops=dict(color="white", linewidth=2))
    colors = PALETTE[:len(lokasi_list)]
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.8)
    for element in ["whiskers", "caps", "fliers"]:
        for item in bp[element]:
            item.set_color(TEXT)
    ax.set_xticklabels(lokasi_list, color=TEXT)
    ax.set_xlabel("Lokasi", fontsize=11)
    ax.set_ylabel("Sesi Foto", fontsize=11)
    ax.set_title("Boxplot Sesi Foto per Lokasi", fontsize=13, fontweight="bold")
    ax.grid(axis="y", linestyle="--", alpha=0.3, color=TEXT)
    return _fig_to_base64(fig)


# ─────────────────────────────────────────────
# 3. Elbow Method
# ─────────────────────────────────────────────

def plot_elbow(k_range: list, inertias: list) -> str:
    fig, ax = _setup_fig(8, 5)
    ax.plot(k_range, inertias, marker="o", color="#4A90D9",
            linewidth=2, markersize=8, markerfacecolor="#E74C3C")
    ax.fill_between(k_range, inertias, alpha=0.1, color="#4A90D9")
    ax.set_xlabel("Jumlah Cluster (k)", fontsize=11)
    ax.set_ylabel("Inertia (SSE)", fontsize=11)
    ax.set_title("Elbow Method — Penentuan Jumlah Cluster Optimal", fontsize=13, fontweight="bold")
    ax.grid(linestyle="--", alpha=0.3, color=TEXT)
    ax.axvline(x=3, color="#E74C3C", linestyle="--", alpha=0.7, label="k=3 (dipilih)")
    ax.legend(facecolor=CARD_BG, labelcolor=TEXT)
    return _fig_to_base64(fig)


# ─────────────────────────────────────────────
# 4. Scatter Plot K-Means
# ─────────────────────────────────────────────

def plot_scatter_kmeans(df: pd.DataFrame, label_map: dict) -> str:
    fig, ax = _setup_fig(8, 5)
    inv_map = {v: k for k, v in label_map.items()}
    color_list = [CLUSTER_COLORS.get(df.loc[i, "Label_Cluster"], "#888") for i in df.index]
    ax.scatter(df["Sesi Foto"], df["Lokasi_enc"],
               c=color_list, alpha=0.75, s=60, edgecolors="none")
    patches = [mpatches.Patch(color=CLUSTER_COLORS[l], label=l)
               for l in ["Sepi", "Normal", "Padat"] if l in df["Label_Cluster"].values]
    ax.legend(handles=patches, facecolor=CARD_BG, labelcolor=TEXT, title="Cluster",
              title_fontsize=9, fontsize=9)
    ax.set_xlabel("Sesi Foto", fontsize=11)
    ax.set_ylabel("Lokasi (encoded)", fontsize=11)
    ax.set_title("Scatter Plot — K-Means Clustering", fontsize=13, fontweight="bold")
    ax.grid(linestyle="--", alpha=0.3, color=TEXT)
    return _fig_to_base64(fig)


# ─────────────────────────────────────────────
# 5. Scatter Plot FCM
# ─────────────────────────────────────────────

def plot_scatter_fcm(df: pd.DataFrame, label_map: dict) -> str:
    fig, ax = _setup_fig(8, 5)
    color_list = [CLUSTER_COLORS.get(df.loc[i, "Label_Cluster"], "#888") for i in df.index]
    ax.scatter(df["Sesi Foto"], df["Lokasi_enc"],
               c=color_list, alpha=0.75, s=60, edgecolors="none")
    patches = [mpatches.Patch(color=CLUSTER_COLORS[l], label=l)
               for l in ["Sepi", "Normal", "Padat"] if l in df["Label_Cluster"].values]
    ax.legend(handles=patches, facecolor=CARD_BG, labelcolor=TEXT, title="Cluster",
              title_fontsize=9, fontsize=9)
    ax.set_xlabel("Sesi Foto", fontsize=11)
    ax.set_ylabel("Lokasi (encoded)", fontsize=11)
    ax.set_title("Scatter Plot — Fuzzy C-Means Clustering", fontsize=13, fontweight="bold")
    ax.grid(linestyle="--", alpha=0.3, color=TEXT)
    return _fig_to_base64(fig)


# ─────────────────────────────────────────────
# 6. Bar Chart Rata-rata Sesi Foto per Cluster
# ─────────────────────────────────────────────

def plot_bar_cluster(df_km: pd.DataFrame, df_fcm: pd.DataFrame) -> str:
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), facecolor=BG)

    for ax, (df, title) in zip(axes, [(df_km, "K-Means"), (df_fcm, "FCM")]):
        ax.set_facecolor(CARD_BG)
        mean_sesi = df.groupby("Label_Cluster")["Sesi Foto"].mean().reindex(
            ["Sepi", "Normal", "Padat"])
        bars = ax.bar(mean_sesi.index, mean_sesi.values,
                      color=[CLUSTER_COLORS[l] for l in mean_sesi.index],
                      edgecolor=BG, width=0.5)
        for bar, val in zip(bars, mean_sesi.values):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                    f"{val:.1f}", ha="center", va="bottom", color=TEXT, fontsize=10)
        ax.set_title(f"Rata-rata Sesi Foto per Cluster ({title})", color=TEXT, fontsize=11,
                     fontweight="bold")
        ax.set_xlabel("Kategori Cluster", color=TEXT)
        ax.set_ylabel("Rata-rata Sesi Foto", color=TEXT)
        ax.tick_params(colors=TEXT)
        for spine in ax.spines.values():
            spine.set_edgecolor("#3A4060")
        ax.grid(axis="y", linestyle="--", alpha=0.3, color=TEXT)

    plt.tight_layout()
    return _fig_to_base64(fig)


# ─────────────────────────────────────────────
# 7. Pie Chart Distribusi Cluster
# ─────────────────────────────────────────────

def plot_pie_cluster(df_km: pd.DataFrame, df_fcm: pd.DataFrame) -> str:
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), facecolor=BG)

    for ax, (df, title) in zip(axes, [(df_km, "K-Means"), (df_fcm, "FCM")]):
        ax.set_facecolor(BG)
        counts = df["Label_Cluster"].value_counts().reindex(["Sepi", "Normal", "Padat"], fill_value=0)
        colors = [CLUSTER_COLORS[l] for l in counts.index]
        wedges, texts, autotexts = ax.pie(
            counts.values, labels=counts.index,
            colors=colors, autopct="%1.1f%%",
            pctdistance=0.75, startangle=90,
            wedgeprops=dict(linewidth=2, edgecolor=BG)
        )
        for t in texts:
            t.set_color(TEXT)
        for at in autotexts:
            at.set_color("white")
            at.set_fontweight("bold")
        ax.set_title(f"Distribusi Cluster — {title}", color=TEXT, fontsize=12, fontweight="bold")

    plt.tight_layout()
    return _fig_to_base64(fig)


# ─────────────────────────────────────────────
# 8. Heatmap Korelasi
# ─────────────────────────────────────────────

def plot_heatmap(df: pd.DataFrame) -> str:
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    # Pilih kolom relevan
    relevant = ["Sesi Foto", "Jumlah Fotografer", "Weekend", "Hari Libur"]
    cols = [c for c in relevant if c in num_cols]
    if not cols:
        cols = num_cols[:6]

    corr = df[cols].corr()
    fig, ax = _setup_fig(8, 6)
    mask = np.zeros_like(corr, dtype=bool)
    mask[np.triu_indices_from(mask, k=1)] = False
    sns.heatmap(
        corr, ax=ax, annot=True, fmt=".2f", mask=mask,
        cmap=sns.diverging_palette(220, 20, as_cmap=True),
        linewidths=0.5, linecolor=BG,
        annot_kws={"size": 11, "color": "white"},
        cbar_kws={"shrink": 0.8}
    )
    ax.set_title("Heatmap Korelasi Fitur", fontsize=13, fontweight="bold")
    ax.tick_params(colors=TEXT, labelsize=10)
    cbar = ax.collections[0].colorbar
    cbar.ax.tick_params(colors=TEXT)
    return _fig_to_base64(fig)


# ─────────────────────────────────────────────
# Semua chart sekaligus
# ─────────────────────────────────────────────

def generate_all_charts(df_raw: pd.DataFrame,
                         df_km: pd.DataFrame,
                         df_fcm: pd.DataFrame,
                         km_label_map: dict,
                         fcm_label_map: dict,
                         k_range: list,
                         inertias: list) -> dict:
    return {
        "histogram": plot_histogram(df_raw),
        "boxplot": plot_boxplot(df_raw),
        "elbow": plot_elbow(k_range, inertias),
        "scatter_km": plot_scatter_kmeans(df_km, km_label_map),
        "scatter_fcm": plot_scatter_fcm(df_fcm, fcm_label_map),
        "bar_cluster": plot_bar_cluster(df_km, df_fcm),
        "pie_cluster": plot_pie_cluster(df_km, df_fcm),
        "heatmap": plot_heatmap(df_raw),
    }
