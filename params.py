from dataclasses import dataclass

@dataclass
class Nugget:
        # DataFrame File to Load, or just leave empty if just calling function #
    FILE_NAME: str = '9_11.csv' # file name for input
        # Base Parameters in DataFrame #
    PREDICTIONS: str = 'predictions'
    ACTUALS: str = 'actuals'

        # Generate a new row to differentiate new operations. #
    OPERATION_ID: str = 'Operation ID'

    ACCUM_MAE_PER_OP: str = 'Accumulated MAE per operation'

        # Invididual MAE for each row #
    MAE_PER_ROW: str = 'Individual MAE per Row'

    FILE_NAME_CSV: str = 'file_name' # FILE NAME FOR INDIVIDUAL CSV, IF HAVE
        # Flag for ERROR if value above threashold #
    THRESHOLD: int = 3
    ERROR_FLAG: str = 'Error Flag'

        # Calculate Average MAE for each Operation #
    AVERAGE_MAE: str = 'Average MAE'

    MONTHS_DATA: list = ("2507","2508")

        # Accuracy and Uptime of MAE being under threshold. #
    UP_TIME_ACCURACY: str = 'Accuracy Up-time'