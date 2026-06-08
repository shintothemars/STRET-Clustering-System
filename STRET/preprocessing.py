import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, MinMaxScaler


def load_data(filepath: str) -> pd.DataFrame:
    """Membaca file Excel dan mengembalikan DataFrame."""
    df = pd.read_excel(filepath)
    return df


def check_missing(df: pd.DataFrame) -> dict:
    """Mengembalikan info missing value."""
    missing = df.isnull().sum()
    missing_pct = (df.isnull().sum() / len(df) * 100).round(2)
    result = []
    for col in df.columns:
        result.append({
            "kolom": col,
            "jumlah_missing": int(missing[col]),
            "persentase": float(missing_pct[col])
        })
    total_missing = int(df.isnull().sum().sum())
    return {"detail": result, "total": total_missing}


def check_duplicates(df: pd.DataFrame) -> dict:
    """Mengembalikan jumlah data duplikat."""
    n_dup = int(df.duplicated().sum())
    return {"jumlah_duplikat": n_dup}


def encode_labels(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Melakukan Label Encoding pada kolom Hari dan Lokasi.
    Mengembalikan DataFrame hasil encoding dan mapping label.
    """
    df_enc = df.copy()
    mappings = {}

    le_hari = LabelEncoder()
    df_enc["Hari_enc"] = le_hari.fit_transform(df_enc["Hari"].astype(str))
    mappings["Hari"] = dict(zip(le_hari.classes_, le_hari.transform(le_hari.classes_)))

    le_lokasi = LabelEncoder()
    df_enc["Lokasi_enc"] = le_lokasi.fit_transform(df_enc["Lokasi"].astype(str))
    mappings["Lokasi"] = dict(zip(le_lokasi.classes_, le_lokasi.transform(le_lokasi.classes_)))

    return df_enc, mappings


def scale_features(df_enc: pd.DataFrame) -> tuple[pd.DataFrame, np.ndarray]:
    """
    Melakukan MinMaxScaler pada fitur clustering:
    Lokasi_enc, Weekend, Hari Libur, Sesi Foto.
    Mengembalikan DataFrame dengan kolom scaled dan array numpy.
    """
    features = ["Lokasi_enc", "Weekend", "Hari Libur", "Sesi Foto"]
    scaler = MinMaxScaler()
    scaled_values = scaler.fit_transform(df_enc[features])
    df_scaled = df_enc.copy()
    df_scaled[["Lokasi_sc", "Weekend_sc", "HariLibur_sc", "SesiFoto_sc"]] = scaled_values
    return df_scaled, scaled_values


def run_preprocessing(filepath: str) -> dict:
    """
    Pipeline preprocessing lengkap.
    Mengembalikan semua informasi hasil preprocessing sebagai dict.
    """
    df_raw = load_data(filepath)

    # Info missing & duplikat (sebelum cleaning)
    missing_info = check_missing(df_raw)
    dup_info = check_duplicates(df_raw)

    # Drop duplikat jika ada
    df_clean = df_raw.drop_duplicates().reset_index(drop=True)

    # Fill missing value dengan modus (jika ada)
    for col in df_clean.columns:
        if df_clean[col].isnull().sum() > 0:
            df_clean[col].fillna(df_clean[col].mode()[0], inplace=True)

    # Encoding
    df_enc, mappings = encode_labels(df_clean)

    # Scaling
    df_scaled, scaled_array = scale_features(df_enc)

    # Konversi untuk display (10 baris pertama) - pastikan semua nilai bisa di-render Jinja2
    head_raw_df = df_raw.head(10).copy()
    for col in head_raw_df.select_dtypes(include=["datetime64[ns]", "datetime64"]).columns:
        head_raw_df[col] = head_raw_df[col].dt.strftime("%Y-%m-%d")
    head_raw = head_raw_df.to_dict(orient="records")
    head_enc = df_enc[["Tanggal", "Hari", "Hari_enc", "Lokasi", "Lokasi_enc",
                        "Weekend", "Hari Libur", "Sesi Foto"]].head(10).to_dict(orient="records")
    head_scaled = df_scaled[["Lokasi_sc", "Weekend_sc", "HariLibur_sc", "SesiFoto_sc"]].head(10).to_dict(orient="records")

    columns_info = []
    for col in df_raw.columns:
        columns_info.append({
            "kolom": col,
            "tipe": str(df_raw[col].dtype),
            "unique": int(df_raw[col].nunique()),
            "contoh": str(df_raw[col].iloc[0]) if len(df_raw) > 0 else "-"
        })

    describe = df_raw.describe().round(2).to_dict()

    return {
        "shape_raw": df_raw.shape,
        "shape_clean": df_clean.shape,
        "missing_info": missing_info,
        "dup_info": dup_info,
        "mappings": mappings,
        "head_raw": head_raw,
        "head_enc": head_enc,
        "head_scaled": head_scaled,
        "columns_info": columns_info,
        "describe": describe,
        "df_scaled": df_scaled,
        "scaled_array": scaled_array,
        "df_raw": df_raw,
        "df_clean": df_clean,
    }
