import pytest
from macro_flow_chunks.main import MacroEtl
def test_macro_etl(monkeypatch):
    # Patch extractPDF para que no descargue realmente
    monkeypatch.setattr("macro_flow_chunks.extract.extract.extract.extractPDF", lambda url, dest: "dummy.pdf")
    monkeypatch.setattr("macro_flow_chunks.transform.transform.PDFTransformer.transform", lambda f, dest: ["chunk1.parquet"])
    monkeypatch.setattr("macro_flow_chunks.load.load.Loaderpdf.save_and_upload_chunks", lambda chunks: ["s3://bucket/chunk1.parquet"])
    
    urls3 = MacroEtl("http://fakeurl.com/fake.pdf")
    assert urls3 == ["s3://bucket/chunk1.parquet"]