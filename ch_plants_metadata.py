from pathlib import Path
import pandas as pd

class PlantsMetaCH():
    def __init__(self, file_metadata:Path='./data/pv_data_merged.csv'):
        """ Reads all Switzerland plants metadata file. The metadata file used 
        is the output of the combine-ch-pv-systems-meta function.

        Args:
            file_metadata (Path, optional): Path to the plants metadata file. 
                Defaults to './data/all.csv'.
        """
        self.file_metadata = file_metadata
        self.run_pipeline()
    
    def run_pipeline(self):
        """ Standard data pipeline
        """
        self.read_metadatafile()
        self.standardize_columns()
        self.convert_orientation()
        self.convert_lv95_to_wgs84()
    
    def read_metadatafile(self):
        """ Reads input meta data file
        """
        self.raw_medatada = pd.read_csv(self.file_metadata)
        self.metadata = self.raw_medatada.copy()
        
    def standardize_columns(self):
        """ Rename column names to english names with lower capitals
        """
        self.metadata.rename(columns={
            'Anlagen-ID': 'plant_id',
            'ID der Erw.': 'plant_extension_id',
            'Anlagenkategorie': 'plant_category',
            'Ausrichtung': 'orientation_deg',
            'Neigungswinkel [°] Winkel gegen die Horizontale': 'slope_deg',
            'Leistung pro Anlagenteil': 'power_plantpart_kwp',
            'Realisierte Leistung': 'power_totalplant_kwp',
            'Address': 'address',
            'PostCode': 'postcode', 
            'Municipality': 'municipality', 
            'Canton': 'canton', 
            '_x': 'lv95_x',
            '_y': 'lv95_y'
        }, inplace=True)
        self.metadata = self.metadata[[
            'plant_id', 'plant_extension_id', 'plant_category', 
            'orientation_deg', 'slope_deg', 'power_plantpart_kwp',
            'power_totalplant_kwp', 'address', 'postcode', 'municipality',
            'canton', 'lv95_x', 'lv95_y']]
        self.metadata['postcode'] = self.metadata['postcode'].astype(int)
    
    def convert_orientation(self):
        """ Transform pv module orientation to numerical values
        """
        orientation_mapping = {
            'Nord': -180,
            'Nordost': -135,
            'Ost': -90,
            'Südost': -45,
            'Süd': 0,
            'Südwest': 45,
            'West': 90,
            'Nordwest': 135,
            'Sonstige': 0,
            'ohne Neigung montiert': 0,
            'Nachführsystem': 0
        }
        self.metadata['orientation_deg'] = self.metadata['orientation_deg'].map(
            orientation_mapping
        ).astype(int)
    
    def convert_lv95_to_wgs84(self):
        """
        Convert swiss coordinates (LV03) to latitude, longitude values (WGS84)
        https://www.swisstopo.admin.ch › ch1903wgs84_d
        """
        x = self.metadata['lv95_x']
        y = self.metadata['lv95_y']
        ys = (x - 2600000) / 1000000
        xs = (y - 1200000) / 1000000
        lon = 2.6779094\
            + 4.728982 * ys\
            + 0.791484 * ys * xs\
            + 0.1306 * ys * xs * xs\
            - 0.0436 * ys * ys * ys
        lat = 16.9023892\
            + 3.238272 * xs\
            - 0.270978 * ys * ys\
            - 0.002528 * xs * xs\
            - 0.0447 * ys * ys * xs\
            - 0.0140 * xs * xs * xs
        lon = lon * 100 / 36
        lat = lat * 100 / 36

        self.metadata['longitude'] = lon
        self.metadata['latitude'] = lat
    
    def get_output_metadata(self):
        """ Returns the plant metadata list in the desired output format
        """
        return(self.metadata)

if __name__ == "__main__":
    pl = PlantsMetaCH()
    print(pl.get_output_metadata().head(10))
