from ..contracts.contractsETL import Transformer
import pdfplumber
import pandas as pd
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
import logging

logging.basicConfig(
    level=logging.INFO,              # Nivel mínimo de logs a mostrar
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='app.log',             # Opcional: guarda los logs en un archivo
    filemode='a'                    # 'a' append, 'w' overwrite
)

class PDFTransformer(Transformer):
    @classmethod
    def transform(cls, pdf_path: str, parquet_folder: str) -> str:
        try:
            # Crear carpeta si no existe
            Path(parquet_folder).mkdir(parents=True, exist_ok=True)

            # Generar nombre del parquet basado en el PDF
            parquet_file = os.path.basename(pdf_path).replace(".pdf", ".parquet")
            parquet_path = os.path.join(parquet_folder, parquet_file)

            # Extraer texto del PDF
            text_content = []
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text_content.append(page.extract_text() or "")
            full_text = "\n".join(text_content)

            # Dividir en chunks
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=50
            )
            chunks = splitter.split_text(full_text)

            # Guardar chunks en Parquet
            df = pd.DataFrame({"chunk_text": chunks, "source_pdf": pdf_path})
            df.to_parquet(parquet_path, index=False)

            logging.info(f"✅ PDF transformado y guardado en Parquet: {parquet_path}")
            return parquet_path

        except Exception as e:
            logging.error(f"❌ Error al transformar PDF {pdf_path}: {e}", exc_info=True)
            return None
