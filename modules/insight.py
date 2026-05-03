def generate_insight(actual_total, target_total, minggu):
    progress_week = minggu / 4

    actual = actual_total * progress_week
    target = target_total * progress_week

    progress = actual / target if target > 0 else 0

    # STATUS
    if progress >= 1:
        status = "🟢 On Track / Tercapai"
    elif progress >= 0.8:
        status = "🟡 Perlu percepatan"
    else:
        status = "🔴 Risiko tidak tercapai"

    # FORECAST (pakai total aktual)
    forecast = actual_total

    if forecast >= target_total:
        prediksi = "Akan tercapai"
    else:
        prediksi = "Berpotensi tidak tercapai"

    return {
        "actual": int(actual),
        "target": int(target),
        "progress": progress,
        "status": status,
        "forecast": prediksi
    }