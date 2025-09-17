# Macro Flow / Flujo de Procesamiento de PDFs  

**ES / Español 🇪🇸**  

`macro_flow` es una librería modular en Python diseñada para pipelines de **ETL sobre documentos PDF**. Permite extraer un PDF desde una URL, transformarlo en chunks de texto y almacenarlo en un formato optimizado para su posterior uso en embeddings o flujos de RAG (Retrieval Augmented Generation).  

---

## 🚀 Características  

- Descarga de **PDFs desde URLs externas**.  
- Transformación de PDFs en **chunks de texto estructurados**.  
- Exportación en **Parquet** para análisis eficiente o entrenamiento de modelos.  
- Carga opcional en **Amazon S3** u otros destinos.  
- Configuración flexible mediante `.env`.  
- Uso como **librería Python** o desde **línea de comandos**.  

---

## ⚙️ Variables de entorno necesarias  

Debes definir un archivo `.env` en la raíz de tu proyecto con las siguientes variables:  

```env
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_DEFAULT_REGION=us-east-1 
AWS_BUCKET_NAME=chunks-data-parquet-2025
AWS_S3_PREFIX=chunks-s3
```


## macroflow --url https://example.com/documento.pdf

from macro_flow.main import MacroEtl

etl = MacroEtl(url="https://example.com/documento.pdf")
etl.run()


##🧠 Requirements

Python >= 3.9

Configured .env file

Internet connection to download PDFs

Valid AWS credentials (if using S3)

##🔮 Use cases

Preprocessing documents for embeddings.

Building RAG pipelines from PDF corpora.

Integration with cloud storage systems.

##🪪 License

MIT © Facu Vega
https://github.com/facuvegaingenieer