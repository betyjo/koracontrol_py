from fastapi import FastAPI
from api import router
from simulator import Simulator

app = FastAPI()
app.include_router(router)

sim = Simulator()
sim.start()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)