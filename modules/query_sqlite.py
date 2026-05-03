import pandas as pd
from modules.koneksi_sqlite import get_conn

conn = get_conn()

# =========================
# IURAN
# =========================
def get_iuran_pu(bulan, tahun):
    q = f"""SELECT SUM(TOTAL_IURAN) as total
            FROM "DATA_MONITORING_IURAN_PU"
            WHERE BLN={bulan} AND TAHUN={tahun}"""
    return pd.read_sql(q, conn)["total"][0] or 0

def get_iuran_bpu(bulan, tahun):
    q = f"""SELECT SUM(TOTAL_IURAN) as total
            FROM DATA_MONITORING_IURAN_PU_BARU
            WHERE BLN={bulan} AND TAHUN={tahun}"""
    return pd.read_sql(q, conn)["total"][0] or 0

def get_iuran_jakon(bulan, tahun):
    q = f"""SELECT SUM(TOTAL_IURAN) as total
            FROM DATA_IURAN_JAKON_HISTORY
            WHERE BLN={bulan} AND TAHUN={tahun}"""
    return pd.read_sql(q, conn)["total"][0] or 0


# =========================
# TK
# =========================
def get_tk_pu(bulan, tahun):
    q = f"""SELECT SUM(TOTAL_TK_PU) as total
            FROM "DATA_TK_PU_HISTORY"
            WHERE BLN={bulan} AND TAHUN={tahun}"""
    return pd.read_sql(q, conn)["total"][0] or 0

def get_tk_bpu(bulan, tahun):
    q = f"""SELECT SUM(TOTAL_TK_BPU) as total
            FROM DATA_TK_BPU_HISTORY
            WHERE BLN={bulan} AND TAHUN={tahun}"""
    return pd.read_sql(q, conn)["total"][0] or 0

def get_tk_jakon(bulan, tahun):
    q = f"""SELECT SUM(TOTAL_TK_JAKON) as total
            FROM DATA_TK_JAKON_HISTORY
            WHERE BLN={bulan} AND TAHUN={tahun}"""
    return pd.read_sql(q, conn)["total"][0] or 0


# =========================
# PERUSAHAAN
# =========================
def get_perusahaan(bulan, tahun):
    q = f"""SELECT SUM(TOTAL_PRS) as total
            FROM "DATA_MONITORING_IURAN_PU"
            WHERE BLN={bulan} AND TAHUN={tahun}"""
    return pd.read_sql(q, conn)["total"][0] or 0


# =========================
# TARGET
# =========================
def get_target():
    q = "SELECT * FROM DATA_TARGET_SETUP_KANTOR LIMIT 1"
    return pd.read_sql(q, conn).iloc[0]



def get_tren_iuran_pu(tahun):
    query = f"""
    SELECT BLN, SUM(TOTAL_IURAN) as total
    FROM DATA_MONITORING_IURAN_PU
    WHERE TAHUN = {tahun}
    GROUP BY BLN
    ORDER BY BLN
    """
    df = pd.read_sql(query, conn)
    return df


def get_tren_iuran_bpu(tahun):
    query = f"""
    SELECT BLN, SUM(TOTAL_IURAN) as total
    FROM DATA_MONITORING_IURAN_PU_BARU
    WHERE TAHUN = {tahun}
    GROUP BY BLN
    ORDER BY BLN
    """
    df = pd.read_sql(query, conn)
    return df

def get_tren_iuran_jakon(tahun):
    query = f"""
    SELECT BLN, SUM(TOTAL_IURAN) as total
    FROM DATA_IURAN_JAKON_HISTORY
    WHERE TAHUN = {tahun}
    GROUP BY BLN
    ORDER BY BLN
    """
    return pd.read_sql(query, conn)

def get_target_kantor():
    import pandas as pd
    
    query = """
    SELECT 
        TARGET_IUR_PU_BLN,
        TARGET_IUR_BPU_BLN,
        TARGET_IUR_JAKON_BLN,
        TARGET_TK_PU_BLN,
        TARGET_TK_BPU_BLN,
        TARGET_TK_JAKON_BLN,
        TARGET_PRS_PU_BLN,
        TARGET_PRS_BPU_BLN,
        TARGET_PRS_JAKON_BLN
    FROM DATA_TARGET_SETUP_KANTOR
    LIMIT 1
    """
    df = pd.read_sql("SELECT * FROM DATA_TARGET_SETUP_KANTOR", conn)

    if df.empty:
        return {
            "TARGET_IURAN_PU_BLN": 0,
            "TARGET_IURAN_BPU_BLN": 0,
            "TARGET_IURAN_JAKON_BLN": 0,
            "TARGET_TK_BLN": 0,
            "TARGET_PRS_BLN": 0
        }
    
    return df.iloc[0]    

