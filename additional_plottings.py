import os
import altair as alt
import pandas as pd

def scatter_plot_x_y(df, x, y, title, file_name, additionals1):
    df = df.to_pandas()
    if additionals1 is not None:
        df = pd.DataFrame({x: df[x],
            "percent": additionals1})
        # Histogram
        chart = alt.Chart(df).mark_circle(size=80).encode(
            alt.X(x, title=x),
            alt.Y("percent", title=y),
            color=alt.Color("percent", scale=alt.Scale(scheme="viridis"))
        ).properties(
            width=700,
            height=500,
            title=title
        )
    else:
        chart = alt.Chart(df).mark_circle(size=80).encode(
            alt.X(x, title=x),
            alt.Y(y, title=y),
            color=alt.Color(y, scale=alt.Scale(scheme="viridis"))
        ).properties(
            width=700,
            height=500,
            title=title
        )

    chart.save(os.path.join("outputs", file_name),"png")  # saves as interactive HTML