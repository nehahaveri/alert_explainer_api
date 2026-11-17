from fastapi import FastAPI

import models
from database import Base, engine
from routers.alerts import router as alerts_router


app = FastAPI(title="AI Intelligence Layer -- Alert Explainer API")

Base.metadata.create_all(bind=engine)
app.include_router(alerts_router)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"status": "AI Intelligence Layer is ready"}