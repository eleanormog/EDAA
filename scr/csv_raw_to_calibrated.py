### csv_raw_to_calibrated.py ###

# python script to convert a csv file from the CO2 monitor website
# into calibrated CO2 data using set gain and offset
# can be used in another script or to simply create new csv file

# from the calibration.py file we have (raw CO2 = 0.8045841562 * ref + (49.7375292170))
gain = 0.9880977888
offset = 42.1695228756

import pandas as pd

def apply_calibration(
    df: pd.DataFrame,
    gain: float = gain,
    offset: float = offset,
) -> pd.DataFrame:
    """Applies sensor calibration parameters to a DataFrame containing 'CO2 (ppm) raw'.
    Formula: Calibrated = (Raw - Offset) / Gain
    """
    calibrated_df = df.copy()
    if "CO2 (ppm) raw" in calibrated_df.columns:
        calibrated_df["CO2 (ppm) calibrated"] = (
            calibrated_df["CO2 (ppm) raw"] - offset
        ) / gain

    return calibrated_df

def calibrate_sensor_file(
    input_filepath: str,
    output_filepath: str,
    gain: float = gain,
    offset: float = offset,
):
    """Reads a sensor CSV file, computes calibrated CO2, and writes output to CSV."""
    df = pd.read_csv(input_filepath)
    calibrated_df = apply_calibration(df, gain, offset)
    calibrated_df.to_csv(output_filepath, index=False)
    print(f"Saved calibrated file to: {output_filepath}")