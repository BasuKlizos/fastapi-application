from fastapi import FastAPI, status

from app.routes import auths, users
from app.redis.redis import lifespan

app = FastAPI(lifespan=lifespan)

app.include_router(auths.auth_routes)
app.include_router(users.users_route)


@app.get("/", status_code=status.HTTP_200_OK)
def index():
    return {"msg": "I am healthy."}
