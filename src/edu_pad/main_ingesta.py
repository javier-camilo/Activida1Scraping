import pandas as pd
import os
from src.edu_pad.database import Database

def main():
    db = Database()
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_csv = os.path.join(current_dir, "static", "csv", "data_extractora.csv")
    output_csv = os.path.join(current_dir, "static", "csv", "data_bd.csv")
    
    if not os.path.exists(input_csv):
        print("El archivo {} no existe. Ejecuta primero el scraping.".format(input_csv))
        return
    
    df = pd.read_csv(input_csv)
    df_bd = db.guardar_df(df)
    df_bd2 = db.obtener_datos()
    df_bd2.to_csv(output_csv, index=False)
    
if __name__ == "__main__":
    main()