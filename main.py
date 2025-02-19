from fastapi import FastAPI
from tasks import process_document_task

app = FastAPI()

@app.post("/process/")
async def process_document(pdf_path: str):
    task = process_document_task.apply_async(args=[pdf_path])
    result = task.get(timeout=300)

    return {"task_id": task.id, "result": result}

@app.get("/status/{task_id}")
async def get_status(task_id: str):
    task = process_document_task.AsyncResult(task_id)
    return {
        "task_id": task.id,
        "status": task.status,
        "result": task.result if task.ready() else None
    }
