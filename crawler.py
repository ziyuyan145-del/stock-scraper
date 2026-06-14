import os
import yfinance as yf


def fetch_stock_data(ticker="2330.TW", period="5d"):
    print(f"[*] 開始抓取股票資料: {ticker} (期間: {period})...")

    # 抓取資料
    df = yf.download(ticker, period=period)

    if df.empty:
        print("[!] 抓取失敗，請檢查網路或股票代碼。")
        return False

    # 把欄位名稱做重置
    df = df.reset_index()

    # 將資料儲存為 CSV 檔
    csv_filename = "stock_data.csv"
    df.to_csv(csv_filename, index=False)
    print(f"[+] 資料抓取成功！已儲存至 {csv_filename}")
    print(df.tail())  # 在終端機印出最後幾筆測試
    return True


if __name__ == "__main__":
    fetch_stock_data()