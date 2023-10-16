from fastapi import FastAPI
import uvicorn
from mapx_new_config import main

app = FastAPI()

@app.get("/mapx/v1")
def mapx(account,pdf,pages):
    print(account,pdf,pages)
    pages = pages.split(",")
    account = account
    pdf = pdf
    final_json = {}
    for page in pages:
        _,final_response = main(account=account,input_pdf=pdf,page=page)
        final_json[str(page)] = final_response
    return final_json


if __name__ == "__main__":
    uvicorn.run("app:app",port=8000,debug=True)
