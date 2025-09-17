from ..contracts.contractsETL import Extractor
import logging
import requests
from pathlib import Path
import os

logging.basicConfig(
    level=logging.INFO,              # Nivel mínimo de logs a mostrar
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='app.log',             # Opcional: guarda los logs en un archivo
    filemode='a'                    # 'a' append, 'w' overwrite
)

class extract(Extractor):
    @classmethod
    def extractPDF(cls, source: str, destination_folder: str) -> str:
        try:
            # Crear carpeta si no existe
            Path(destination_folder).mkdir(parents=True, exist_ok=True)

            # Generar nombre de archivo a partir de la URL
            filename = source.split("/")[-1]  # toma lo último de la URL
            if not filename.endswith(".pdf"):
                filename += ".pdf"

            destination = os.path.join(destination_folder, filename)

            # Descargar PDF
            response = requests.get(source)
            response = requests.get(source)
            if response.status_code == 404:
                logging.error(f"❌ PDF no encontrado (404): {source}")
                return None
            response.raise_for_status()

            # Guardar PDF
            with open(destination, "wb") as f:
                f.write(response.content)

            logging.info(f"✅ PDF descargado: {destination}")
            return destination

        except Exception as e:
            logging.error(f"❌ Error al descargar {source}: {e}", exc_info=True)
            return None
