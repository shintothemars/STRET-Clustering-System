import os
import io

import pandas as pd
from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, send_file, jsonify
)
from werkzeug.utils import secure_filename

from preprocessing import run_preprocessing
from clustering import run_kmeans, run_fcm, compare_algorithms
from visualisasi import generate_all_charts

# ──────────────────────────────────────────────────────────────────────────────
# Konfigurasi Flask
# ──────────────────────────────────────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.secret_key = "stret_secret_key_2024"

# Expose Python builtins to Jinja2
app.jinja_env.globals.update(enumerate=enumerate, zip=zip, len=len, round=round)
app.config["UPLOAD_FOLDER"] = os.path.join(BASE_DIR, "uploads")
app.config["OUTPUT_FOLDER"] = os.path.join(BASE_DIR, "outputs")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB
ALLOWED_EXTENSIONS = {"xlsx", "xls"}

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(app.config["OUTPUT_FOLDER"], exist_ok=True)


# ──────────────────────────────────────────────────────────────────────────────
# In-memory cache (satu dataset aktif per server run)
# ──────────────────────────────────────────────────────────────────────────────

_cache = {}


def get_cache(key, default=None):
    return _cache.get(key, default)


def set_cache(key, value):
    _cache[key] = value


def cache_ready() -> bool:
    return "prep_result" in _cache


def clustering_ready() -> bool:
    return "km_result" in _cache and "fcm_result" in _cache


# ──────────────────────────────────────────────────────────────────────────────
# Helper
# ──────────────────────────────────────────────────────────────────────────────

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ──────────────────────────────────────────────────────────────────────────────
# Context Processor — kirim status ke semua template
# ──────────────────────────────────────────────────────────────────────────────

@app.context_processor
def inject_status():
    filename = session.get("filename", None)
    return {
        "filename": filename,
        "cache_ready": cache_ready(),
        "clustering_ready": clustering_ready(),
        "best_algo": get_cache("best_algo"),
    }


# ──────────────────────────────────────────────────────────────────────────────
# 1. Dashboard
# ──────────────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    stats = {}
    if cache_ready():
        prep = get_cache("prep_result")
        stats["total_data"] = prep["shape_raw"][0]
        stats["total_kolom"] = prep["shape_raw"][1]
        stats["lokasi"] = 3  # Marba, Pringsewu, Distrik
        stats["cluster"] = 3
        if clustering_ready():
            stats["best_algo"] = get_cache("best_algo", "-")
            km_r = get_cache("km_result")
            stats["dist_km"] = km_r["df"]["Label_Cluster"].value_counts().to_dict()
    return render_template("index.html", stats=stats)


# ──────────────────────────────────────────────────────────────────────────────
# 2. Upload Dataset
# ──────────────────────────────────────────────────────────────────────────────

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        if "file" not in request.files:
            flash("Tidak ada file yang dipilih.", "danger")
            return redirect(request.url)

        file = request.files["file"]
        if file.filename == "":
            flash("Nama file kosong.", "danger")
            return redirect(request.url)

        if not allowed_file(file.filename):
            flash("Format file tidak didukung. Gunakan .xlsx atau .xls", "warning")
            return redirect(request.url)

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        session["filename"] = filename
        session["filepath"] = filepath

        # Reset cache
        _cache.clear()

        flash(f"File '{filename}' berhasil diupload!", "success")
        return redirect(url_for("data_understanding"))

    return render_template("upload.html")


# ──────────────────────────────────────────────────────────────────────────────
# 3. Data Understanding
# ──────────────────────────────────────────────────────────────────────────────

@app.route("/data-understanding")
def data_understanding():
    if not session.get("filepath"):
        flash("Silakan upload dataset terlebih dahulu.", "warning")
        return redirect(url_for("upload"))

    if not cache_ready():
        try:
            prep = run_preprocessing(session["filepath"])
            set_cache("prep_result", prep)
        except Exception as e:
            flash(f"Error saat membaca dataset: {e}", "danger")
            return redirect(url_for("upload"))

    prep = get_cache("prep_result")
    return render_template("data_understanding.html", prep=prep)


# ──────────────────────────────────────────────────────────────────────────────
# 4. Preprocessing
# ──────────────────────────────────────────────────────────────────────────────

@app.route("/preprocessing")
def preprocessing():
    if not session.get("filepath"):
        flash("Silakan upload dataset terlebih dahulu.", "warning")
        return redirect(url_for("upload"))

    if not cache_ready():
        try:
            prep = run_preprocessing(session["filepath"])
            set_cache("prep_result", prep)
        except Exception as e:
            flash(f"Error saat preprocessing: {e}", "danger")
            return redirect(url_for("upload"))

    prep = get_cache("prep_result")
    return render_template("preprocessing.html", prep=prep)


# ──────────────────────────────────────────────────────────────────────────────
# 5. K-Means
# ──────────────────────────────────────────────────────────────────────────────

@app.route("/kmeans", methods=["GET", "POST"])
def kmeans():
    if not cache_ready():
        flash("Silakan lakukan preprocessing terlebih dahulu.", "warning")
        return redirect(url_for("upload"))

    prep = get_cache("prep_result")
    n_clusters = 3

    if request.method == "POST":
        try:
            n_clusters = int(request.form.get("n_clusters", 3))
        except ValueError:
            n_clusters = 3

    try:
        df_scaled = prep["df_scaled"]
        scaled_array = prep["scaled_array"]
        result_df, eval_metrics, label_map, centers, k_range, inertias = \
            run_kmeans(df_scaled, scaled_array, n_clusters)

        # Gabungkan dengan data asli — hapus kolom overlap jika ada
        df_raw = prep["df_raw"].copy().reset_index(drop=True)
        km_cols = ["Cluster_KMeans", "Label_Cluster", "Rekomendasi_Fotografer"]
        df_raw_clean = df_raw.drop(columns=[c for c in km_cols + ["Cluster_FCM", "Label_FCM", "Rek_Fotografer_KMeans", "Rek_Fotografer_FCM"] if c in df_raw.columns], errors="ignore")
        result_combined = df_raw_clean.join(result_df[km_cols].reset_index(drop=True))

        set_cache("km_result", {
            "df": result_combined,
            "eval": eval_metrics,
            "label_map": label_map,
            "k_range": k_range,
            "inertias": inertias,
            "n_clusters": n_clusters,
            "df_scaled_km": result_df,
        })

        # Hitung distribusi
        dist = result_combined["Label_Cluster"].value_counts().to_dict()

    except Exception as e:
        flash(f"Error saat K-Means: {e}", "danger")
        return redirect(url_for("preprocessing"))

    km_result = get_cache("km_result")
    table_data = km_result["df"].head(50).to_dict(orient="records")

    return render_template("kmeans.html",
                           eval_metrics=km_result["eval"],
                           table_data=table_data,
                           label_map=km_result["label_map"],
                           dist=km_result["df"]["Label_Cluster"].value_counts().to_dict(),
                           n_clusters=km_result["n_clusters"],
                           total=len(km_result["df"]))


# ──────────────────────────────────────────────────────────────────────────────
# 6. Fuzzy C-Means
# ──────────────────────────────────────────────────────────────────────────────

@app.route("/fcm", methods=["GET", "POST"])
def fcm():
    if not cache_ready():
        flash("Silakan lakukan preprocessing terlebih dahulu.", "warning")
        return redirect(url_for("upload"))

    prep = get_cache("prep_result")
    n_clusters = 3

    if request.method == "POST":
        try:
            n_clusters = int(request.form.get("n_clusters", 3))
        except ValueError:
            n_clusters = 3

    try:
        df_scaled = prep["df_scaled"]
        scaled_array = prep["scaled_array"]
        result_df, eval_metrics, label_map, centers, u = \
            run_fcm(df_scaled, scaled_array, n_clusters)

        df_raw = prep["df_raw"].copy().reset_index(drop=True)
        membership_cols = [c for c in result_df.columns if c.startswith("Membership_")]
        fcm_join_cols = ["Cluster_FCM", "Label_Cluster", "Rekomendasi_Fotografer"] + membership_cols
        # Hapus kolom overlap jika sudah ada di df_raw
        df_raw_clean = df_raw.drop(columns=[c for c in fcm_join_cols + ["Cluster_KMeans", "Label_KMeans", "Rek_Fotografer_KMeans", "Rek_Fotografer_FCM"] if c in df_raw.columns], errors="ignore")
        result_combined = df_raw_clean.join(
            result_df[fcm_join_cols].reset_index(drop=True)
        )

        set_cache("fcm_result", {
            "df": result_combined,
            "eval": eval_metrics,
            "label_map": label_map,
            "n_clusters": n_clusters,
            "df_scaled_fcm": result_df,
            "membership_cols": membership_cols,
        })

    except Exception as e:
        flash(f"Error saat Fuzzy C-Means: {e}", "danger")
        return redirect(url_for("preprocessing"))

    # Auto run comparison
    if get_cache("km_result"):
        try:
            comp = compare_algorithms(
                get_cache("km_result")["eval"],
                get_cache("fcm_result")["eval"]
            )
            set_cache("comparison", comp)
            set_cache("best_algo", comp["best"])
        except Exception:
            pass

    fcm_result = get_cache("fcm_result")
    table_data = fcm_result["df"].head(50).to_dict(orient="records")
    membership_cols = fcm_result["membership_cols"]

    return render_template("fcm.html",
                           eval_metrics=fcm_result["eval"],
                           table_data=table_data,
                           label_map=fcm_result["label_map"],
                           dist=fcm_result["df"]["Label_Cluster"].value_counts().to_dict(),
                           n_clusters=fcm_result["n_clusters"],
                           membership_cols=membership_cols,
                           total=len(fcm_result["df"]))


# ──────────────────────────────────────────────────────────────────────────────
# 7. Perbandingan Algoritma
# ──────────────────────────────────────────────────────────────────────────────

@app.route("/comparison")
def comparison():
    if not clustering_ready():
        flash("Jalankan K-Means dan FCM terlebih dahulu.", "warning")
        return redirect(url_for("kmeans"))

    comp = get_cache("comparison")
    if comp is None:
        comp = compare_algorithms(
            get_cache("km_result")["eval"],
            get_cache("fcm_result")["eval"]
        )
        set_cache("comparison", comp)
        set_cache("best_algo", comp["best"])

    return render_template("comparison.html",
                           comp=comp,
                           km_eval=get_cache("km_result")["eval"],
                           fcm_eval=get_cache("fcm_result")["eval"])


# ──────────────────────────────────────────────────────────────────────────────
# 8. Visualisasi
# ──────────────────────────────────────────────────────────────────────────────

@app.route("/visualisasi")
def visualisasi():
    if not clustering_ready():
        flash("Jalankan K-Means dan FCM terlebih dahulu.", "warning")
        return redirect(url_for("kmeans"))

    prep = get_cache("prep_result")
    km_r = get_cache("km_result")
    fcm_r = get_cache("fcm_result")

    charts = generate_all_charts(
        df_raw=prep["df_raw"],
        df_km=km_r["df_scaled_km"],
        df_fcm=fcm_r["df_scaled_fcm"],
        km_label_map=km_r["label_map"],
        fcm_label_map=fcm_r["label_map"],
        k_range=km_r["k_range"],
        inertias=km_r["inertias"],
    )

    return render_template("visualisasi.html", charts=charts)


# ──────────────────────────────────────────────────────────────────────────────
# 9. Download Hasil
# ──────────────────────────────────────────────────────────────────────────────

@app.route("/download")
def download():
    return render_template("download.html",
                           clustering_ready=clustering_ready())


@app.route("/download/excel")
def download_excel():
    if not clustering_ready():
        flash("Jalankan clustering terlebih dahulu.", "warning")
        return redirect(url_for("download"))

    prep = get_cache("prep_result")
    km_r = get_cache("km_result")
    fcm_r = get_cache("fcm_result")

    df_raw = prep["df_raw"].copy().reset_index(drop=True)
    km_df = km_r["df"][["Cluster_KMeans", "Label_Cluster", "Rekomendasi_Fotografer"]].copy()
    km_df.columns = ["Cluster_KMeans", "Label_KMeans", "Rek_Fotografer_KMeans"]

    fcm_cols = ["Cluster_FCM", "Label_Cluster", "Rekomendasi_Fotografer"]
    fcm_df = fcm_r["df"][fcm_cols].copy()
    fcm_df.columns = ["Cluster_FCM", "Label_FCM", "Rek_Fotografer_FCM"]

    final_df = pd.concat([df_raw, km_df, fcm_df], axis=1)

    output_path = os.path.join(app.config["OUTPUT_FOLDER"], "Hasil_Clustering_STRET.xlsx")

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        final_df.to_excel(writer, sheet_name="Hasil Clustering", index=False)
        km_r["df"].to_excel(writer, sheet_name="K-Means Detail", index=False)
        fcm_r["df"].to_excel(writer, sheet_name="FCM Detail", index=False)

    return send_file(output_path,
                     as_attachment=True,
                     download_name="Hasil_Clustering_STRET.xlsx",
                     mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


# ──────────────────────────────────────────────────────────────────────────────
# Run
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
