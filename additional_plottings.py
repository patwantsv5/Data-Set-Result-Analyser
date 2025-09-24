import os
import altair as alt
import pandas as pd
from params import Nugget

def scatter_plot_x_y(df, x, y, title, file_name, additionals1):
    df = df.to_pandas()
    # For Handling Total Operation I
    if additionals1 is not None:
        # Histogram Plotting
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
        new_df = pd.DataFrame({x: df[x],
            "percent": additionals1,
            "Ranges" : range_label})
        points = alt.Chart(new_df).mark_circle(size=80).encode(
            alt.X(x, title=x),
            alt.Y("percent", title=y),
            color=alt.Color("Ranges", title="Bins")
        ).properties(
            width=700,
            height=500,
            title=title
        )
        threshold_line = alt.Chart(pd.DataFrame({'y':[80]})).mark_rule(color="red", strokeWidth=2).encode(y='y')
        chart = points + threshold_line

        # Split Date Chart
        Date = []
        for deeze in df[Nugget.FILE_NAME_CSV]:
            for date in Nugget.MONTHS_DATA:
                if date in deeze:
                    Date.append(date)
        new_df = pd.DataFrame({x: df[x],
            "percent": additionals1,
            "Ranges" : range_label,
            "Date" : Date})
        points = alt.Chart(new_df).mark_circle(size=80).encode(
            alt.X(x,title=x),
            alt.Y("percent",title=y),
            color=alt.Color("Date", title="Bins")
        ).properties(
            width=700,
            height=500,
            title=f"{title} Split by Date"
        )
        chart2 = points + threshold_line
        chart2.save(os.path.join("outputs", f"{file_name}_Split_By_Date.png"),"png")  # saves as interactive HTML

        # Sort by Date Chart
        # Convert your Date column to datetime (if not already)
        # Create the chart
        points = alt.Chart(new_df).mark_circle(size=80).encode(
            x=alt.X("Date:T", title="Date"),   # <- temporal axis
            y=alt.Y("percent", title=y),
            color=alt.Color("Date:T", title="Date")  # optional, keeps colors consistent
        ).properties(
            width=700,
            height=500,
            title=f"{title} Split by Date"
        )

        chart2 = points + threshold_line

        # Save chart
        chart2.save(os.path.join("outputs", f"{file_name}_Sort_By_Date.png"), "png")
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

    chart.save(os.path.join("outputs", f"{file_name}.png"),"png")  # saves as interactive HTML