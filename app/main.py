from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

from app.api.v1 import auth, levels, tasks, courses, users, achievments
from app.internal.admin_views import setup_admin


app = FastAPI(title="CodeLingo API")


setup_admin(app)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(levels.router, prefix="/api/levels", tags=["levels"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(courses.router, prefix="/api/courses", tags=["courses"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(achievments.router, prefix="/api/achievments", tags=["achievments"])


@app.get("/")
async def get_root():
    return {"message": "Hello World"}

@app.api_route("/health", methods=["GET", "HEAD"])
async def get_health():
    return {"status": "ok"}

@app.get("/robots.txt", include_in_schema=False)
def robots():
    return PlainTextResponse("User-agent: *\nDisallow: /")
