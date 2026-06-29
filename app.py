import os
from flask import Flask, jsonify, render_template, request
import numpy as np
import pandas as pd
import yfinance as yf

app = Flask(__name__)


def fetch_and_clean_stock(ticker, period="1mo"):
    print(f"[*] 數據流水線啟動：自雲端採集 {ticker} ({period})...")

    # 下載股票資料
    df = yf.download(
        ticker,
        period=period,
        multi_level_index=False
    )

    if df.empty:
        print(f"[-] 核心錯誤：{ticker} 數據採集結果為空")
        return None

    # 將時間索引 Date 提取為一般欄位
    df = df.reset_index()

    # 欄位全部轉小寫
    df.columns = [str(col).strip().lower() for col in df.columns]

    # 確保 date 存在
    if "date" not in df.columns:
        df.rename(columns={df.columns[0]: "date"}, inplace=True)

    # 日期格式
    df["date"] = df["date"].astype(str).str.strip().str.slice(0, 10)

    # 過濾錯誤日期
    df = df[df["date"].str.match(r"^\d{4}-\d{2}-\d{2}$", na=False)]

    # 數值欄位
    num_cols = ["open", "high", "low", "close", "volume"]

    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # NaN -> 0
    df = df.replace({np.nan: 0})

    return df


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/stock")
def get_stock_data():

    ticker = request.args.get("ticker", "2330.TW").upper().strip()

    # 新增時間區間
    period = request.args.get("period", "1mo")

    # 只允許合法期間
    allow_period = [
        "1mo",
        "3mo",
        "6mo",
        "1y"
    ]

    if period not in allow_period:
        period = "1mo"

    df = fetch_and_clean_stock(ticker, period)

    if df is None or df.empty:
        return (
            jsonify(
                {
                    "error": f"股票代碼 {ticker} 清洗後無有效時序數據"
                }
            ),
            404,
        )

    return jsonify(df.to_dict(orient="records"))


if __name__ == "__main__":

    # Render / Railway
    port = int(os.environ.get("PORT", 5000))

    app.run(host="0.0.0.0", port=port)
