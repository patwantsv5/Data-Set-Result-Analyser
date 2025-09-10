import os
import altair as alt
import pandas as pd

def scatter_plot_x_y(df, x, y, title, file_name, additionals1):
    df = df.to_pandas()
    if additionals1 is not None:
        range_label = []
        for val in additionals1:
            if 80 <= val < 85:
                range_label.append("80-85")
            elif 85 <= val < 90:
                range_label.append("85-90")
            elif 90 <= val < 95:
                range_label.append("90-95")
            elif 95 <= val < 100:
                range_label.append("95-100")
            else:
                range_label.append("UnLabelled")
        df = pd.DataFrame({x: df[x],
            "percent": additionals1,
            "Ranges" : range_label})
        # Histogram
        chart = alt.Chart(df).mark_circle(size=80).encode(
            alt.X(x, title=x),
            alt.Y("percent", title=y),
            color=alt.Color("Ranges", title="Bins")
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