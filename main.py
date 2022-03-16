from msilib.schema import Directory
from fastapi import FastAPI, Depends, status
import models
from database import engine

from routers import auth, todos
from company import companyapis, dependencies
from starlette.staticfiles import StaticFiles
from starlette.responses import RedirectResponse
# Creates all database schema
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Static Files mounting
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(
    companyapis.router,
    prefix="/company",
    tags=['company'],
    dependencies=[Depends(dependencies.get_dependencies)],
    responses={
        400: {'response': 'Bad request'}
    }
)

# DEFAULT URL REDIRECTION


@app.get("/")
async def default_redirect():
    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)
