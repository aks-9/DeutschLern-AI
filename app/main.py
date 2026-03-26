from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from app.routers import auth, theory, exercises, vocabulary, coach

app = FastAPI(title="DeutschLern AI")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(auth.router)
app.include_router(theory.router)
app.include_router(exercises.router)
app.include_router(vocabulary.router)
app.include_router(coach.router)


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/dashboard")
