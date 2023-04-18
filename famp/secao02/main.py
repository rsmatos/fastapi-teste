from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"Hello": "world"}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="localhost", port=8000, log_level="info", reload=True)