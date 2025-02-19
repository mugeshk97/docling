import json
import logging

from celery import Celery

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (EasyOcrOptions,
                                                PdfPipelineOptions,
                                                TableFormerMode)
from docling.document_converter import DocumentConverter, PdfFormatOption

logging.basicConfig(level=logging.INFO)

# Configure pipeline options
pipeline_options = PdfPipelineOptions(do_table_structure=True)
pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE
pipeline_options.do_ocr = True
pipeline_options.ocr_options = EasyOcrOptions(use_gpu=True)

# Initialize Docling Converter
doc_converter = DocumentConverter(
    format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)}
)

# Configure Celery
celery_app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",  # Redis broker
    backend="redis://localhost:6379/0"  # Redis result backend
)

@celery_app.task(name="process_document_task")
def process_document_task(pdf_path: str):
    """Celery task for processing a PDF and converting it to Markdown."""
    try:
        logging.info(f"Processing document: {pdf_path}")
        result = doc_converter.convert(pdf_path, max_num_pages=100)
        result_data = result.document.export_to_markdown()  
        return json.dumps({"status": "success", "data": result_data})
    except Exception as e:
        logging.error(f"Error processing document: {str(e)}")
        return json.dumps({"status": "error", "message": str(e)})
