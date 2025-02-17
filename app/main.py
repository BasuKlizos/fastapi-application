from fastapi import FastAPI, status

from app.routes import auths

app = FastAPI()

app.include_router(auths.auth_routes)


@app.get("/", status_code=status.HTTP_200_OK)
def index():
    return {"msg": "I am healthy."}
