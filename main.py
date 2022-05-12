from fastapi import FastAPI, File, Form, UploadFile
from starlette.responses import FileResponse
from fastapi.responses import HTMLResponse
from translate_support import pdf2html2col
import uvicorn

app = FastAPI()

@app.get('/')
def read_root():
    return FileResponse('index.html')

@app.post('/upload/')
async def create_file(file: UploadFile = File(...)):
    html = pdf2html2col(file)
    
    # with open(path, 'w+b') as buffer:
    #     shutil.copyfileobj(file.file, buffer)
    
    return HTMLResponse(content=html, status_code=200)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)