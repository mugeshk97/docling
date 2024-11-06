from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (EasyOcrOptions,
                                                PdfPipelineOptions,
                                                TableFormerMode)
from docling.document_converter import DocumentConverter, PdfFormatOption

# Initialize the document converter once
pipeline_options = PdfPipelineOptions(do_table_structure=True)
pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE
pipeline_options.do_ocr = True
pipeline_options.ocr_options = EasyOcrOptions(use_gpu=False)
pipeline_options.artifacts_path= "/home/mugesh/Project/doc-intelligence/docling-models"


doc_converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)
