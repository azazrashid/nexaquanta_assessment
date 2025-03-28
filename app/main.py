import uvicorn

from app.core.config import config

if __name__ == "__main__":
    uvicorn.run(
        app="app.core.server:app",
        host="0.0.0.0",  # Important for Docker to bind to all interfaces
        port=8000,
        reload=True if config.ENVIRONMENT == "development" else False,
    )
