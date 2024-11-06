from app.models.request_model import DocumentUrlRequest
from app.services.document_service import process_document
from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.post("/process-url")
async def process_file_from_url(document_url: DocumentUrlRequest):
    url = document_url.url
    try:
        # Pass the pre-initialized model to the handler
        result = await process_document(url)
        return result  # Adjust output as needed
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))