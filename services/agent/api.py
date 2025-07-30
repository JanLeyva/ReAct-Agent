# internal libs
from src.shared.api import generate, search, upload

# 3rd party
import uvicorn
from fastapi import FastAPI, APIRouter

app = FastAPI()
router_v1 = APIRouter(prefix="/v1")

router_v1.include_router(generate.router)
router_v1.include_router(search.router)
router_v1.include_router(upload.router)

app.include_router(router_v1)


@app.get("/")
def health():
    return {"message": "OK"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80, log_level="debug")
