from fastapi import FastAPI, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from app.models import User
from app.dependencies import get_current_user
from fastapi.templating import Jinja2Templates
from app.routers import auth, theory, exercises, vocabulary, coach

app = FastAPI(title="DeutschLern AI")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

app.include_router(auth.router)
app.include_router(theory.router)
app.include_router(exercises.router)
app.include_router(vocabulary.router)
app.include_router(coach.router)


@app.get("/", include_in_schema=False)
async def root():
    """Redirect the root URL to the dashboard."""
    return RedirectResponse(url="/dashboard")


@app.get("/dashboard", include_in_schema=False)
async def dashboard(request: Request, current_user: User = Depends(get_current_user)):
    """
    Render the user dashboard

    :param request: The incoming FastAPI request.
    :param current_user: The authenticated user from the JWT cookie
    :return: TemplateResponse rendering dashboard.html with basic user data
    """
    return templates.TemplateResponse(
        request, "dashboard.html", {"user": current_user}
    )

