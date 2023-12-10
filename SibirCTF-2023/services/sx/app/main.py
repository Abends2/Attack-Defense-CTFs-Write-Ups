from fastapi import FastAPI
from sqlalchemy.schema import CreateTable

from app.routes import router
from app.db import get_async_session, BaseModel


app = FastAPI(title="South X", docs_url="/")
app.include_router(router)


@app.on_event("startup")
async def startup_event():
    async_session = get_async_session()
    async with async_session() as session:
        for table in BaseModel.metadata.sorted_tables:
            create_expression = CreateTable(table, if_not_exists=True)
            await session.execute(create_expression)
