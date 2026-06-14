import os
from flask import Flask, jsonify, render_template, request
import numpy as np
import pandas as pd
import yfinance as yf

app = Flask(__name__)

def fetch_and_clean_stock(ticker):
    print(f"[*] 數據流水線啟動：自雲端採集 {ticker} 時間序列...")

    # 利用官方參數強制關閉多層索引 (multi_level_index=False)
    df = yf.download(ticker, period="1mo", multi_level_index=False)

    if df.empty:
        print(f"[-] 核心錯誤：{ticker} 數據採集結果為空")
        return None

    # 將時間索引 Date 提取為一般欄位
    df = df.reset_index()

    # 統一套用標準小寫，防止前後端大小寫對不上
    df.columns = [str(col).strip().lower() for col in df.columns]

    # 確保主要鍵存在（date/datetime）
    if "date" not in df.columns:
        df.rename(columns={df.columns[0]: "date"}, inplace=True)

    # 確保日期型態為乾淨的 YYYY-MM-DD
    df["date"] = df["date"].astype(str).str.strip().str.slice(0, 10)

    # 過濾非標準日期的雜訊行
    df = df[df["date"].str.match(r"^\d{4}-\d{2}-\d{2}$", na=False)]

    # 欄位型態強制型轉，防止髒資料
    num_cols = ["open", "high", "low", "close", "volume"]
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # 處理缺失值
    df = df.replace({np.nan: 0})

    return df


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/stock")
def get_stock_data():
    ticker = request.args.get("ticker", "2330.TW").upper().strip()

    # 直接調用高效清洗模組
    df = fetch_and_clean_stock(ticker)

    if df is None or df.empty:
        return (
            jsonify({"error": f"股票代碼 {ticker} 清洗後無有效時序數據"}),
            404,
        )

    # 轉成標準序列字典格式回傳
    return jsonify(df.to_dict(orient="records"))


if __name__ == "__main__":
    # 讀取雲端環境指定的 Port，若沒有則預設 5000
    port = int(os.environ.get("臨特定Port", 5000)) 
    app.run(host="0.0.0.0", port=port)
