import pandas as pd

if __name__ == "__main__":
    df_pv_anlagen = pd.read_csv("data/20220822_Ausrichtung_Neigung_Report_Mengengerüst.csv", header=0)
    df_all_anlagen_locations = pd.read_csv("data/ElectricityProductionPlant.csv", header=0)

    df_pv_anlagen_locations = df_all_anlagen_locations[df_all_anlagen_locations['SubCategory'] == 'subcat_2']

    df_all = pd.merge(
        left=df_pv_anlagen,
        right=df_pv_anlagen_locations,
        left_on='Anlagen-ID',
        right_on='xtf_id',
        how='left'
    )

    df_all.to_csv("data/all.csv")
