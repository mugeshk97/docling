from app.routes import document
from fastapi import FastAPI

app = FastAPI()

# Include the router
app.include_router(document.router, prefix="/parse")


@app.on_event("startup")
async def startup_event():
    print("Application startup complete")


@app.get("/health")
def health_check():
    return {"status": "OK"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
