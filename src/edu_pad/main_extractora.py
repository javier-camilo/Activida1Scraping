import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", "..")) 
sys.path.append(project_root)

from src.edu_pad.dataweb import DataWeb

def main_1():
    dw = DataWeb()
    df = dw.obtener_datos()
    
    output_dir = os.path.join(current_dir, "static", "csv")
    os.makedirs(output_dir, exist_ok=True)
    
    if not df.empty:
        df.to_csv(os.path.join(output_dir, "data_extractora.csv"), index=False)
    else:
        print("No se encontraron datos para guardar.")

if __name__ == "__main__":
    main_1()
