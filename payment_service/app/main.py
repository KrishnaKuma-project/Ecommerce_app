from fastapi import FastAPI, Depends, HTTPException

app = FastAPI()

@app.get("/")
def summa ():
    return {"Message":"Working."}