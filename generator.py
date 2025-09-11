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

def Apply_File_Name(df):
    # Apply File Name to dataset, if dataset has additional column with filenames.
    name = list(dict.fromkeys(df[Nugget.FILE_NAME_CSV]))
    return name

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

    try:
        name = Apply_File_Name(df=df)
    except Exception as e:
        print("File name for each operation not found. Skipping.")

    # Create New Polars DataFrame
    if "name" in locals():
        csv_new = pl.DataFrame({
        Nugget.OPERATION_ID : list(range(1,num_ops+1)),
        Nugget.AVERAGE_MAE : avg_mae_list,
        Nugget.ERROR_FLAG : alerts,
        Nugget.UP_TIME_ACCURACY: up_time,
        Nugget.FILE_NAME_CSV : name
    })
    else:
        csv_new = pl.DataFrame({
        Nugget.OPERATION_ID : list(range(1,num_ops+1)),
        Nugget.AVERAGE_MAE : avg_mae_list,
        Nugget.ERROR_FLAG : alerts,
        Nugget.UP_TIME_ACCURACY: up_time
    })
    csv_new.write_csv(os.path.join("outputs", f"{Nugget.FILE_NAME}_Operation_And_Accuracy.csv"))

    return csv_new

def histogram_accuracy_grouping(pl_df):
    # Nested dictionary: one per group, each with bins
    histogram = {"All": {"UnLabelled": [], "80+": [], "85+": [], "90+": [], "95+": []}}
    for i in Nugget.MONTHS_DATA:
        histogram[i] = {"UnLabelled": [], "80+": [], "85+": [], "90+": [], "95+": []}

    # Loop through rows with enumerate to get index
    for idx, val_str in enumerate(pl_df[Nugget.UP_TIME_ACCURACY]):
        # Convert "90%" → float
        val = float(val_str.replace("%", ""))

        # Determine which groups this row belongs to
        filename = pl_df[Nugget.FILE_NAME_CSV][idx]
        groups = ["All"]
        
        for date in Nugget.MONTHS_DATA:
            if date in filename:
                groups.append(date)

        # Append to bins for each group
        for group in groups:
            if val < 80:
                histogram[group]["UnLabelled"].append(val)
            if val >= 80:
                histogram[group]["80+"].append(val)
            if val >= 85:
                histogram[group]["85+"].append(val)
            if val >= 90:
                histogram[group]["90+"].append(val)
            if val >= 95:
                histogram[group]["95+"].append(val)

    # Flatten nested dict into table for CSV
    rows = []
    for group_name, bins in histogram.items():
        row = {"Date": group_name}
        for bin_name, values in bins.items():
            row[bin_name] = len(values)
        rows.append(row)

    histo_df = pl.DataFrame(rows)
    histo_df.write_csv(os.path.join("outputs", f"{Nugget.FILE_NAME}_Histogram.csv"))

    return histogram

if __name__ == "__main__":
    df = pl.read_csv(os.path.join("inputs", Nugget.FILE_NAME))
    df = df.to_pandas()

    # Split Indices #
    split_indices = df.index[(df[Nugget.ACTUALS] == 0) & (df[Nugget.ACTUALS].shift(1) > 0)].tolist()
    split_indices.insert(0, 0) 
    split_indices.append(len(df))
    # ============= #

    mae_data = accumulate_and_flag(df, split_indices)
    csv_new = make_new_average_csv(df, split_indices, mae_data)
    isolated_ranges_groupings = histogram_accuracy_grouping(csv_new)
    mae_data.to_csv(os.path.join("outputs", f"{Nugget.FILE_NAME}_Individual_MAE.csv"), index=False)

    # Plottings, Additionals.
    # try:
    # Plot Operation ID to Up Time Accuracy
    percent_float = [float(i.replace("%","")) for i in csv_new[Nugget.UP_TIME_ACCURACY]]
    scatter_plot_x_y(df=csv_new, x=Nugget.OPERATION_ID, y=Nugget.UP_TIME_ACCURACY,
                    title="Plot Operation ID to Up Time Accuracy",
                    file_name="Up_Time_To_Operation_ID",
                    additionals1=percent_float)
    # except Exception as e:
    #     print(f"Failed to generate plot: {e}")