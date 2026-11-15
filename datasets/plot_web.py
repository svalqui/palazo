# streamlit run plot_web.py
# http://localhost:8501

from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Historical share prices", layout="wide")
st.title("Historical share prices")

directory = st.text_input("Folder containing CSV files", value="./prices")

date_options = ["Date", "date", ]
#price_options = ["Close", "close", "Adj Close", "adj_close"]
price_options = ["Adj Close",]

folder = Path(directory).expanduser()

if st.button("Load charts"):
    if not folder.is_dir():
        st.error(f"Folder not found: {folder}")
    else:
        files = sorted(folder.glob("*.csv"))

        if not files:
            st.warning("No CSV files found in that folder.")
        else:
            for file in files:
                try:
                    df = pd.read_csv(file)

                    date_col = next((c for c in date_options if c in df.columns), None)
                    price_col = next((c for c in price_options if c in df.columns), None)

                    if not date_col or not price_col:
                        st.warning(
                            f"{file.name}: couldn't find a date column and a closing-price "
                            f"column. Columns found: {', '.join(df.columns)}"
                        )
                        continue

                    chart_data = df[[date_col, price_col]].copy()
                    chart_data[date_col] = pd.to_datetime(chart_data[date_col], errors="coerce")
                    chart_data[price_col] = pd.to_numeric(chart_data[price_col], errors="coerce")
                    
                    chart_data = (
                        chart_data.dropna()
                        .sort_values(date_col)
                        .set_index(date_col)
                    )
                    
                    # Use the closing-price column for the rolling average.
                    chart_data["MA 20"] = chart_data[price_col].rolling(window=20).mean()
                    
                    # Rename the price series so the chart legend is clear.
                    chart_data = chart_data.rename(columns={price_col: "Closing price"})
                    
                    st.subheader(file.stem)
                    st.line_chart(chart_data[["Closing price", "MA 20"]])


                except Exception as exc:
                    st.error(f"Couldn't read {file.name}: {exc}")
