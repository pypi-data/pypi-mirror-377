from macro_flow_chunks.extract.extract import extract
from macro_flow_chunks.transform.transform import PDFTransformer
from macro_flow_chunks.load.load import Loaderpdf
import logging

logging.basicConfig(
    level=logging.INFO,              # Nivel mínimo de logs a mostrar
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='appMain.log',             # Opcional: guarda los logs en un archivo
    filemode='a'                    # 'a' append, 'w' overwrite
)


def MacroEtl(url: str) -> str | None:
    """
    Descarga un PDF desde `url`, lo transforma en parquet y lo sube a S3.
    Devuelve la URL en S3 si todo sale bien, None si falla.
    """
    destino_local = "downloads"
    destino_parquet = "parquet_chunks"

    # 1️⃣ Extraer
    archivo = extract.extractPDF(url, destino_local)
    if not archivo:
        logging.error(f"Error al descargar el PDF desde {url}")
        return None

    # 2️⃣ Transformar
    parquet_chunks = PDFTransformer.transform(archivo, destino_parquet)
    if not parquet_chunks:
        logging.error(f"Error al transformar PDF desde {url}")
        return None

    # 3️⃣ Cargar a S3
    s3_urls = Loaderpdf.save_and_upload_chunks(parquet_chunks)
    if not s3_urls:
        logging.error(f"Error al subir chunks a S3 desde {url}")
        return None

    # 4️⃣ Retornar URLs de S3
    return s3_urls