from fastapi import FastAPI

app=FastAPI()

@app.get("/")
def summa ():
    return {"Message":"admin panel working"}