"""Allow running the app as a module: python -m app"""

import uvicorn


def main():
    uvicorn.run("app_server:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
