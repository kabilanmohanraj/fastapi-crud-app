from fastapi import FastAPI
from backend.app.api.routes import login, books, events
from backend.app.core.db import init_db

def create_application() -> FastAPI:
    application = FastAPI(title="Library Management Application")
    application.include_router(login.router)
    application.include_router(books.router)
    # application.include_router(users.router)
    application.include_router(events.router)
    return application

library_app = create_application()

@library_app.on_event("startup")
def on_startup():
    init_db()

@library_app.get("/")
async def root():
    return {"message": "Welcome to the Library Management Application!"}

# Only execute this if the file is run directly
if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("backend.app.main:library_app", host="0.0.0.0", port=port, reload=True)