from ..contracts.contractsETL import Loader
import logging
import boto3
import json
from pathlib import Path
import os

logging.basicConfig(
    level=logging.INFO,              # Nivel mínimo de logs a mostrar
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='app.log',             # Opcional: guarda los logs en un archivo
    filemode='a'                    # 'a' append, 'w' overwrite
)

class Loaderpdf(Loader):
    @classmethod
    def save_and_upload_chunks(cls, parquet_path: str):
        """
        Sube el archivo Parquet local a S3 usando variables de entorno:
        - AWS_BUCKET
        - AWS_S3_PREFIX (opcional)
        """
        try:
            if not Path(parquet_path).exists():
                logging.error(f"❌ El archivo parquet no existe: {parquet_path}")
                return None

            s3_bucket = os.environ.get("AWS_BUCKET")
            s3_prefix = os.environ.get("AWS_S3_PREFIX", "")

            if not s3_bucket:
                logging.error("❌ No se encontró la variable de entorno AWS_BUCKET")
                return None

            # Crear cliente S3
            s3 = boto3.client(
                "s3",
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                region_name=os.getenv("AWS_DEFAULT_REGION"),
            )

            # Generar key en S3
            file_name = Path(parquet_path).name
            s3_key = f"{s3_prefix}/{file_name}" if s3_prefix else file_name

            # Subir archivo
            s3.upload_file(parquet_path, s3_bucket, s3_key)
            logging.info(f"☁️ Parquet subido a S3: s3://{s3_bucket}/{s3_key}")

            return f"s3://{s3_bucket}/{s3_key}"

        except Exception as e:
            logging.error(f"❌ Error subiendo parquet a S3: {e}", exc_info=True)
            return None
