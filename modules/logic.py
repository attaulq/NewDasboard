def hitung_estimasi(total, target, minggu):
    progress_week = minggu / 4

    actual = total * progress_week
    target_minggu = target * progress_week

    progress = actual / target_minggu if target_minggu > 0 else 0

    # STATUS
    if progress >= 1:
        status = "🟢 Tercapai"
    elif progress >= 0.8:
        status = "🟡 Hampir"
    else:
        status = "🔴 Risiko"

    # 🔥 TAMBAHKAN INI
    prediksi = total  # estimasi akhir bulan (pakai total aktual)

    forecast = "Akan tercapai" if total >= target else "Tidak tercapai"

    return {
        "actual": int(actual),
        "target": int(target_minggu),
        "gap": int(actual - target_minggu),
        "progress": progress,
        "status": status,
        "forecast": forecast,
        "prediksi": int(prediksi)  # ← WAJIB ADA
    }