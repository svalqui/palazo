# streamlit run plot_web.py
# http://localhost:8501

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import streamlit as st

st.set_page_config(page_title="Historical share prices", layout="wide")
st.title("Historical share prices")

HIST = os.environ["HIST"]

directory = st.text_input("Folder containing CSV files", value=HIST)

date_options = ["Date", "date", ]
price_options = ["Adj Close",]
volume_options = ["Volume", "volume"]


folder = Path(directory).expanduser()

if st.button("Load charts"):
    st.session_state["load_charts"] = True

if st.session_state.get("load_charts", False):

    if not folder.is_dir():
        st.error(f"Folder not found: {folder}")
    else:
        files = sorted(folder.glob("*.AX"))

        if not files:
            st.warning("No CSV files found in that folder.")
        else:
            for file in files:
                try:
                    df = pd.read_csv(file)

                    date_col = next((c for c in date_options if c in df.columns), None)
                    price_col = next((c for c in price_options if c in df.columns), None)
                    volume_col = next((c for c in volume_options if c in df.columns), None)


                    if not date_col or not price_col or not volume_col:
                        st.warning(
                            f"{file.name}: expected date, closing-price, and volume columns. "
                            f"Found: {', '.join(df.columns)}"
                        )
                        continue


                    chart_data = df[[date_col, price_col, volume_col]].copy()
                    chart_data[date_col] = pd.to_datetime(chart_data[date_col], errors="coerce", utc=True)
                    chart_data[price_col] = pd.to_numeric(chart_data[price_col], errors="coerce")
                    chart_data[volume_col] = pd.to_numeric(chart_data[volume_col], errors="coerce")
                    chart_data = chart_data.dropna().sort_values(date_col)
                    
                    # Calculate rolling averages over trading-day rows.
                    for days in (5, 20, 50):
                        chart_data[f"MA {days}"] = chart_data[price_col].rolling(window=days).mean()

                    range_label = st.selectbox(
                        "Show",
                        ["All history", "1 year", "6 months", "3 months"],
                        key=f"range_{file.stem}",  # unique control for each ticker
                    )

                    periods = {
                        "1 year": pd.DateOffset(years=1),
                        "6 months": pd.DateOffset(months=6),
                        "3 months": pd.DateOffset(months=3),
                    }

                    if range_label == "All history":
                        plot_data = chart_data
                    else:
                        latest_date = chart_data[date_col].max()
                        cutoff = latest_date - periods[range_label]
                        plot_data = chart_data.loc[chart_data[date_col] >= cutoff]

                    fig = make_subplots(
                        rows=2,
                        cols=1,
                        shared_xaxes=True,
                        vertical_spacing=0.06,
                        row_heights=[0.75, 0.25],
                    )
                    
                    fig.add_trace(
                        go.Scatter(
                            x=plot_data[date_col],
                            y=plot_data[price_col],
                            name="Closing price",
                        ),
                        row=1,
                        col=1,
                    )
                    
                    for days in (5, 20, 50):
                        fig.add_trace(
                            go.Scatter(
                                x=plot_data[date_col],
                                y=plot_data[f"MA {days}"],
                                name=f"{days}-day MA",
                            ),
                            row=1,
                            col=1,
                        )
                    
                    fig.add_trace(
                        go.Bar(
                            x=plot_data[date_col],
                            y=plot_data[volume_col],
                            name="Volume",
                        ),
                        row=2,
                        col=1,
                    )
                    
                    fig.update_layout(
                        title=file.stem,
                        height=650,
                        xaxis2_title="Date",
                        yaxis_title="Price",
                        yaxis2_title="Volume",
                        legend=dict(orientation="h"),
                    )

                    
                    st.plotly_chart(fig, use_container_width=True)


                except Exception as exc:
                    st.error(f"Couldn't read {file.name}: {exc}")
