# -*- coding: utf-8 -*-
import yfinance as yf
import pandas as pd
from datetime import datetime

# =====================
# パラメータ
# =====================
START_DATE = "2018-08-01"
END_DATE = datetime.today().strftime("%Y-%m-%d")

TICKERS = {
    "USDJPY": "JPY=X",

    "Gold_F": "GC=F",
    "Gold_ETF": "1672.T",

    "Silver_F": "SI=F",
    "Silver_ETF": "1673.T",

    "Platinum_F": "PL=F",
    "Platinum_ETF": "1674.T",

    "Palladium_F": "PA=F",
    "Palladium_ETF": "1675.T",

    "NobleMetal_ETF": "1676.T"
}

# 先物→ETF換算係数（あなたの定義を踏襲）
OZ = {
    "Gold": 0.1,
    "Silver": 1.0,
    "Platinum": 0.1,
    "Palladium": 0.1,
}

# =====================
# データ取得（Open & Close）
# =====================
dfs = []

for name, ticker in TICKERS.items():
    df = yf.Ticker(ticker).history(
        start=START_DATE,
        end=END_DATE,
        auto_adjust=False
    )
    if df.empty:
        continue

    df = df[["Open", "Close"]].rename(
        columns={
            "Open": f"{name}_Open",
            "Close": f"{name}_Close",
        }
    )
    dfs.append(df)

df_all = pd.concat(dfs, axis=1)

# 日付をDateに正規化（UTC → 日次）
df_all.index = pd.to_datetime(df_all.index, utc=True)
df = df_all.groupby(df_all.index.date).last()
df.index = pd.to_datetime(df.index)
df.index.name = "Date"

# 欠損補完（市場休場差を吸収）
df = df.ffill()

# =====================
# 円換算先物（Close / Open）
# =====================
df["Gold_F_JPY_Close"] = df["Gold_F_Close"] * df["USDJPY_Close"] * OZ["Gold"]
df["Silver_F_JPY_Close"] = df["Silver_F_Close"] * df["USDJPY_Close"] * OZ["Silver"]
df["Platinum_F_JPY_Close"] = df["Platinum_F_Close"] * df["USDJPY_Close"] * OZ["Platinum"]
df["Palladium_F_JPY_Close"] = df["Palladium_F_Close"] * df["USDJPY_Close"] * OZ["Palladium"]

df["Gold_F_JPY_Open"] = df["Gold_F_Open"] * df["USDJPY_Open"] * OZ["Gold"]
df["Silver_F_JPY_Open"] = df["Silver_F_Open"] * df["USDJPY_Open"] * OZ["Silver"]
df["Platinum_F_JPY_Open"] = df["Platinum_F_Open"] * df["USDJPY_Open"] * OZ["Platinum"]
df["Palladium_F_JPY_Open"] = df["Palladium_F_Open"] * df["USDJPY_Open"] * OZ["Palladium"]

# =====================
# 乖離率
# =====================
# 前日Close（判断用）
df["Gold_dev_Close"] = (df["Gold_ETF_Close"] - df["Gold_F_JPY_Close"]) / df["Gold_F_JPY_Close"] * 100
df["Silver_dev_Close"] = (df["Silver_ETF_Close"] - df["Silver_F_JPY_Close"]) / df["Silver_F_JPY_Close"] * 100
df["Platinum_dev_Close"] = (df["Platinum_ETF_Close"] - df["Platinum_F_JPY_Close"]) / df["Platinum_F_JPY_Close"] * 100
df["Palladium_dev_Close"] = (df["Palladium_ETF_Close"] - df["Palladium_F_JPY_Close"]) / df["Palladium_F_JPY_Close"] * 100

# 当日Open（参考・他作戦用）
df["Gold_dev_Open"] = (df["Gold_ETF_Open"] - df["Gold_F_JPY_Open"]) / df["Gold_F_JPY_Open"] * 100
df["Silver_dev_Open"] = (df["Silver_ETF_Open"] - df["Silver_F_JPY_Open"]) / df["Silver_F_JPY_Open"] * 100
df["Platinum_dev_Open"] = (df["Platinum_ETF_Open"] - df["Platinum_F_JPY_Open"]) / df["Platinum_F_JPY_Open"] * 100
df["Palladium_dev_Open"] = (df["Palladium_ETF_Open"] - df["Palladium_F_JPY_Open"]) / df["Palladium_F_JPY_Open"] * 100

# =====================
# 列順整理
# =====================
df = df[
    [
        # FX
        "USDJPY_Open", "USDJPY_Close",

        # Gold
        "Gold_F_Open", "Gold_F_Close",
        "Gold_ETF_Open", "Gold_ETF_Close",
        "Gold_dev_Open", "Gold_dev_Close",

        # Silver
        "Silver_F_Open", "Silver_F_Close",
        "Silver_ETF_Open", "Silver_ETF_Close",
        "Silver_dev_Open", "Silver_dev_Close",

        # Platinum
        "Platinum_F_Open", "Platinum_F_Close",
        "Platinum_ETF_Open", "Platinum_ETF_Close",
        "Platinum_dev_Open", "Platinum_dev_Close",

        # Palladium
        "Palladium_F_Open", "Palladium_F_Close",
        "Palladium_ETF_Open", "Palladium_ETF_Close",
        "Palladium_dev_Open", "Palladium_dev_Close",
    ]
]

# =====================
# CSV出力
# =====================
df.to_csv(
    "1676_market_prices_and_dev_20180801_to_now.csv",
    encoding="utf-8-sig",
    float_format="%.4f"
)

print(df.head())
print(df.tail())
