import pandas as pd
import matplotlib.pyplot as plt

def plot_value_basic(csv_path, date_col="Date", price_col="Close"):
    df = pd.read_csv(csv_path, parse_dates=[date_col])
    df = df.sort_values(date_col)

    fig, ax = plt.subplots()
    ax.plot(df[date_col], df[price_col])
    ax.set(xlabel="Date", ylabel="Value", title="Historical Value")
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig("historical_value.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    return ax
