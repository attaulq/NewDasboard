import calendar

def get_range_kumulatif(minggu, tahun, bulan):
    last_day = calendar.monthrange(tahun, bulan)[1]

    if minggu == 1:
        end_day = 7
    elif minggu == 2:
        end_day = 14
    elif minggu == 3:
        end_day = 21
    else:
        end_day = last_day

    start = f"{tahun}-{bulan:02d}-01"
    end = f"{tahun}-{bulan:02d}-{end_day}"

    return start, end

def get_progress_minggu(minggu):
    return minggu / 4

def get_target_kumulatif(target_bulanan, minggu):
    return target_bulanan * (minggu / 4)