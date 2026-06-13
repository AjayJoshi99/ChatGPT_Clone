from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager

from database.connection import Base, engine
from api.auth_api import auth_router
from api.chat_with_llm_api import router




@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")
    async with engine.begin() as conn:
        print("Creating database tables...")
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Hello World"}


app.include_router(auth_router) 
app.include_router(router)