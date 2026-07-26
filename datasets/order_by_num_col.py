#!/usr/bin/env python3
import pandas as pd

df = pd.read_csv("my.csv")
# or read_csv("file.csv", encoding="utf-8")
#df_sorted = df.sort_values(by="Market Cap", ascending=True)  # or False

#df["Market Cap"] = pd.to_numeric(df["Market Cap"], errors="coerce")  # converts; bad values -> NaN
#df_sorted = df.sort_values(by="Market Cap", ascending=True)

#print(df_sorted.head())
#print(df_sorted)
#print(df_sorted["Market Cap"].map("{:,.2f}".format).to_string(index=False))


pd.set_option('display.max_rows', None)

col_sort = "Market Cap"  # the column that looks like text but contains numbers

# 1) convert for sorting
df[col_sort] = pd.to_numeric(df[col_sort], errors="coerce")  # bad values -> NaN

# 2) sort
#df_sorted = df.sort_values(by=col_sort, ascending=True, na_position="last")
df_sorted = df.sort_values(by=col_sort, ascending=False, na_position="last")

# after you computed df_sorted
df_sorted = df_sorted.reset_index(drop=True)
df_sorted["counter"] = df_sorted.index + 1


# 3) create a decimal-formatted display column (as string)
df_sorted["num_col_fmt"] = df_sorted[col_sort].map(lambda x: f"{x:,.2f}" if pd.notna(x) else "")

# 4) display (choose which columns you want)
cols_to_show = ["text_col1", "text_col2", col_sort, "num_col_fmt"]  # edit as needed

print(df_sorted)
#print(df_sorted[cols_to_show].to_string(index=False))
