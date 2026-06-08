import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import (
    silhouette_score,
    davies_bouldin_score,
    calinski_harabasz_score,
)
import skfuzzy as fuzz


# ─────────────────────────────────────────────
# Label helper
# ─────────────────────────────────────────────

def assign_labels(df: pd.DataFrame, cluster_col: str, sesi_col: str = "Sesi Foto") -> pd.DataFrame:
    """
    Menetapkan label Sepi / Normal / Padat berdasarkan rata-rata Sesi Foto
    tiap cluster, lalu menambahkan kolom Label_Cluster dan Rekomendasi_Fotografer.
    """
    df = df.copy()
    cluster_mean = df.groupby(cluster_col)[sesi_col].mean()

    # Urutan: cluster dengan mean terendah → Sepi, tengah → Normal, tertinggi → Padat
    sorted_clusters = cluster_mean.sort_values().index.tolist()
    label_map = {}
    rec_map = {}
    labels = ["Sepi", "Normal", "Padat"]
    recs = [1, 3, 5]
    for i, cl in enumerate(sorted_clusters):
        label_map[cl] = labels[i]
        rec_map[cl] = recs[i]

    df["Label_Cluster"] = df[cluster_col].map(label_map)
    df["Rekomendasi_Fotografer"] = df[cluster_col].map(rec_map)
    return df, label_map, rec_map


# ─────────────────────────────────────────────
# K-Means
# ─────────────────────────────────────────────

def run_kmeans(df_scaled: pd.DataFrame, scaled_array: np.ndarray, n_clusters: int = 3):
    """
    Menjalankan K-Means Clustering.

    Returns
    -------
    result_df   : DataFrame dengan kolom Cluster_KMeans, Label_Cluster, Rekomendasi_Fotografer
    eval_metrics: dict berisi Silhouette, DBI, CHI
    label_map   : mapping cluster → label
    centers     : array cluster centers
    inertias    : list inertia untuk Elbow Method
    """
    km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = km.fit_predict(scaled_array)

    result_df = df_scaled.copy()
    result_df["Cluster_KMeans"] = labels

    result_df, label_map, rec_map = assign_labels(result_df, "Cluster_KMeans")

    sil = silhouette_score(scaled_array, labels)
    dbi = davies_bouldin_score(scaled_array, labels)
    chi = calinski_harabasz_score(scaled_array, labels)

    eval_metrics = {
        "silhouette": round(float(sil), 4),
        "dbi": round(float(dbi), 4),
        "chi": round(float(chi), 4),
    }

    # Elbow Method: k=2..8
    inertias = []
    k_range = range(2, 9)
    for k in k_range:
        km_tmp = KMeans(n_clusters=k, random_state=42, n_init=10)
        km_tmp.fit(scaled_array)
        inertias.append(km_tmp.inertia_)

    return result_df, eval_metrics, label_map, km.cluster_centers_, list(k_range), inertias


# ─────────────────────────────────────────────
# Fuzzy C-Means
# ─────────────────────────────────────────────

def run_fcm(df_scaled: pd.DataFrame, scaled_array: np.ndarray, n_clusters: int = 3):
    """
    Menjalankan Fuzzy C-Means Clustering menggunakan scikit-fuzzy.

    Returns
    -------
    result_df   : DataFrame dengan Cluster_FCM, Membership_*, Label_Cluster, Rekomendasi_Fotografer
    eval_metrics: dict berisi Silhouette, DBI, CHI, FPC
    label_map   : mapping cluster → label
    centers     : array cluster centers
    u           : matriks keanggotaan (membership)
    """
    data_T = scaled_array.T  # skfuzzy butuh shape (n_features, n_samples)

    cntr, u, u0, d, jm, p, fpc = fuzz.cluster.cmeans(
        data_T,
        c=n_clusters,
        m=2.0,
        error=0.005,
        maxiter=1000,
        init=None,
        seed=42,
    )

    # Hard label: cluster dengan membership tertinggi
    labels = np.argmax(u, axis=0)

    result_df = df_scaled.copy()
    result_df["Cluster_FCM"] = labels

    # Tambahkan kolom membership
    for i in range(n_clusters):
        result_df[f"Membership_C{i}"] = u[i]

    result_df, label_map, rec_map = assign_labels(result_df, "Cluster_FCM")

    sil = silhouette_score(scaled_array, labels)
    dbi = davies_bouldin_score(scaled_array, labels)
    chi = calinski_harabasz_score(scaled_array, labels)

    eval_metrics = {
        "silhouette": round(float(sil), 4),
        "dbi": round(float(dbi), 4),
        "chi": round(float(chi), 4),
        "fpc": round(float(fpc), 4),
    }

    return result_df, eval_metrics, label_map, cntr, u


# ─────────────────────────────────────────────
# Perbandingan Algoritma
# ─────────────────────────────────────────────

def compare_algorithms(km_eval: dict, fcm_eval: dict) -> dict:
    """
    Membandingkan K-Means dan FCM berdasarkan metrik evaluasi.

    Aturan:
    - Silhouette: semakin TINGGI semakin baik
    - DBI        : semakin RENDAH semakin baik
    - CHI        : semakin TINGGI semakin baik

    Returns dict dengan tabel perbandingan dan pemenang.
    """
    scores = {
        "KMeans": 0,
        "FCM": 0,
    }

    # Silhouette: lebih tinggi lebih baik
    if km_eval["silhouette"] >= fcm_eval["silhouette"]:
        scores["KMeans"] += 1
        sil_winner = "K-Means"
    else:
        scores["FCM"] += 1
        sil_winner = "Fuzzy C-Means"

    # DBI: lebih rendah lebih baik
    if km_eval["dbi"] <= fcm_eval["dbi"]:
        scores["KMeans"] += 1
        dbi_winner = "K-Means"
    else:
        scores["FCM"] += 1
        dbi_winner = "Fuzzy C-Means"

    # CHI: lebih tinggi lebih baik
    if km_eval["chi"] >= fcm_eval["chi"]:
        scores["KMeans"] += 1
        chi_winner = "K-Means"
    else:
        scores["FCM"] += 1
        chi_winner = "Fuzzy C-Means"

    best = "K-Means" if scores["KMeans"] >= scores["FCM"] else "Fuzzy C-Means"
    best_key = "KMeans" if best == "K-Means" else "FCM"

    alasan = []
    if sil_winner == best:
        alasan.append(f"Silhouette Score lebih tinggi ({km_eval['silhouette'] if best=='K-Means' else fcm_eval['silhouette']})")
    if dbi_winner == best:
        alasan.append(f"Davies-Bouldin Index lebih rendah ({km_eval['dbi'] if best=='K-Means' else fcm_eval['dbi']})")
    if chi_winner == best:
        alasan.append(f"Calinski-Harabasz Index lebih tinggi ({km_eval['chi'] if best=='K-Means' else fcm_eval['chi']})")

    return {
        "table": [
            {
                "metrik": "Silhouette Score ↑",
                "kmeans": km_eval["silhouette"],
                "fcm": fcm_eval["silhouette"],
                "pemenang": sil_winner,
                "keterangan": "Semakin tinggi semakin baik",
            },
            {
                "metrik": "Davies-Bouldin Index ↓",
                "kmeans": km_eval["dbi"],
                "fcm": fcm_eval["dbi"],
                "pemenang": dbi_winner,
                "keterangan": "Semakin rendah semakin baik",
            },
            {
                "metrik": "Calinski-Harabasz Index ↑",
                "kmeans": km_eval["chi"],
                "fcm": fcm_eval["chi"],
                "pemenang": chi_winner,
                "keterangan": "Semakin tinggi semakin baik",
            },
        ],
        "scores": scores,
        "best": best,
        "best_key": best_key,
        "alasan": alasan,
    }
