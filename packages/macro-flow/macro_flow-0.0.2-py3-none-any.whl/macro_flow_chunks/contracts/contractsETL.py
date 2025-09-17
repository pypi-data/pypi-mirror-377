from abc import ABC, abstractmethod

class Extractor(ABC):
    @abstractmethod
    def extract(self) -> bytes:
        """Descargar o recibir el PDF en bytes"""
        pass

# Contrato para transformación
class Transformer(ABC):
    @abstractmethod
    def transform(self, pdf_path: str, parquet_path: str) -> str:
        """
        Procesa un PDF y guarda los chunks en un archivo Parquet.
        Devuelve la ruta al archivo Parquet generado.
        """
        pass

# Contrato para carga (load)
class Loader(ABC):
    @abstractmethod
    def load(self, texts: list[str], embeddings: list):
        """Guardar texto + embeddings en DB, S3 o vector DB"""
        pass