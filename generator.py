import os
from sklearn.metrics import mean_absolute_error
import polars as pl
# import matplotlib.pyplot as plt
from params import Nugget
# import altair as alt
from additional_plottings import scatter_plot_x_y

# 2025/09/04 - make it so that each operation has its own resultTFT.csv file, 
# respective to their own operation_id, 
# with individual MAE per time step and total average MAE for the whole operation.

def accumulate_and_flag(df, split_indices):
    mae_data = df.copy()

    # Generate a new row to differentiate new operations.
    mae_data[Nugget.OPERATION_ID] = 0
    for i in range(1,len(split_indices)):
        start = split_indices[i-1]
        end = split_indices[i]
        mae_data.loc[start:end-1, Nugget.OPERATION_ID] = i

    # # Generate Accumulated MAE for each operation
    # mae_data[Nugget.ACCUM_MAE_PER_OP] = 0.0
    # for i in range(1, len(split_indices)):
    #     start = split_indices[i-1] 
    #     end = split_indices[i] 
    #     for x in range(start,end): 
    #         y_actuals = df[Nugget.ACTUALS][start:x+1]
    #         y_predictions = df[Nugget.PREDICTIONS][start:x+1]
    #         mae = mean_absolute_error(y_actuals, y_predictions) 
    #         mae_data.at[x, Nugget.ACCUM_MAE_PER_OP] = mae

    # Calculate MAE for EACH individual row.
    mae_data[Nugget.MAE_PER_ROW] = 0.0
    for i in range(0, len(mae_data)):           # Get Absolute value of pred - actuals.
        mmae = abs(df[Nugget.PREDICTIONS][i] - df[Nugget.ACTUALS][i])
        mae_data.at[i, Nugget.MAE_PER_ROW] = mmae

    # Generate Error Flag if MAE of each individual reaches threshold
    mae_data[Nugget.ERROR_FLAG] = 0.0
    for i in range(0, len(mae_data)):
        if mae_data[Nugget.MAE_PER_ROW][i] > Nugget.THRESHOLD:
            mae_data.loc[i, Nugget.ERROR_FLAG] = 1
        else:
            mae_data.loc[i, Nugget.ERROR_FLAG] = 0
    return mae_data

def make_new_average_csv(df, split_indices, mae_data):
    num_ops = len(split_indices) -1
    avg_mae_list = []
    # Calculate Segment MAE
    for i in range(len(split_indices) -1):
        segment = df[split_indices[i]:split_indices[i+1]] 
        segment = segment.reset_index(drop=True)
        segment_mae = mean_absolute_error(segment[Nugget.ACTUALS],segment[Nugget.PREDICTIONS])
        avg_mae_list.append(segment_mae)

    # Add Alerts just in case.
    # Generate Error Flag if MAE of each individual reaches threshold
    alerts = []
    for i in range(0, len(split_indices)-1):
        if avg_mae_list[i] > Nugget.THRESHOLD:
            alerts.append(1)
        else:
            alerts.append(0)

    error_numbers = []
    up_time = []
    # Find Accuracy of Prediction, by finding the uptime of alert 1 and 0 from df dataset. (some kind of uptime for how long 0 is on)
    for i in range(1, len(split_indices)):
        start = split_indices[i-1] 
        end = split_indices[i]
        for x in range(start,end):
            if mae_data[Nugget.ERROR_FLAG][x] == 1:
                error_numbers.append(1)
            else:
                error_numbers.append(0)
        up_time.append(f"{((1.0 - (mae_data[Nugget.ERROR_FLAG][start:end].mean())) *100)}%")
        error_numbers = []

    # Create New Polars DataFrame
    csv_new = pl.DataFrame({
        Nugget.OPERATION_ID : list(range(1,num_ops+1)),
        Nugget.AVERAGE_MAE : avg_mae_list,
        Nugget.ERROR_FLAG : alerts,
        Nugget.UP_TIME_ACCURACY: up_time
    })
    csv_new.write_csv(os.path.join("outputs", Nugget.FILE_NAME))

    return csv_new

def histogram_accuracy_grouping(pl_df):
    isolated_ranges_groups = {
        "UnLabelled": [],
        "80+":[],
        "85+":[],
        "90+":[],
        "95+":[],
        "Unique Operation ID":[]
    }
    percent = []
    for i in pl_df[Nugget.UP_TIME_ACCURACY]:
        k = i.replace("%","")
        percent.append(float(k))
    percent = pl.Series(percent)
    # categorized_percentage = percent.filter((percent >= 80) & (percent <=100)) # FILTERED

    for val in percent:
        if 80 <= val:
            isolated_ranges_groups["80+"].append(val)
        if 85 <= val:
            isolated_ranges_groups["85+"].append(val)
        if 90 <= val:
            isolated_ranges_groups["90+"].append(val)
        if 95 <= val:
            isolated_ranges_groups["95+"].append(val)
        if val < 80:
            isolated_ranges_groups["UnLabelled"].append(val)
        isolated_ranges_groups["Unique Operation ID"].append(val)
    histo = pl.DataFrame({
        label: [len(vals)] for label, vals in isolated_ranges_groups.items()
    })
    histo.write_csv(os.path.join("outputs", "Histogram.csv"))
    return isolated_ranges_groups

if __name__ == "__main__":
    df = pl.read_csv(os.path.join("inputs", Nugget.DATA_FRAME))
    df = df.to_pandas()

    # Split Indices #
    split_indices = df.index[(df[Nugget.ACTUALS] == 0) & (df[Nugget.ACTUALS].shift(1) > 0)].tolist()
    split_indices.insert(0, 0) 
    split_indices.append(len(df))
    # ============= #

    mae_data = accumulate_and_flag(df, split_indices)
    csv_new = make_new_average_csv(df, split_indices, mae_data)
    isolated_ranges_groupings = histogram_accuracy_grouping(csv_new)
    mae_data.to_csv("outputs/output.csv")

    # Plottings, Additionals.
    # try:
    # Plot Operation ID to Up Time Accuracy
    percent_float = [float(i.replace("%","")) for i in csv_new[Nugget.UP_TIME_ACCURACY]]
    scatter_plot_x_y(df=csv_new, x=Nugget.OPERATION_ID, y=Nugget.UP_TIME_ACCURACY,
                    title="Plot Operation ID to Up Time Accuracy",
                    file_name="Up_Time_To_Operation_ID.png",
                    additionals1=percent_float)
    # except Exception as e:
    #     print(f"Failed to generate plot: {e}")