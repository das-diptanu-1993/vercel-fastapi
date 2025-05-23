from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse, FileResponse
from typing import Annotated
from util.gantt import file2row, plot_gantt, save_plot, FIG_LOCATION
import matplotlib
matplotlib.use('TkAgg')

app = FastAPI()

# APIs/Services

@app.get("/api/health_check")
async def health_check():
    return {"status": "success", \
            "message": "health checked successfully;"}

@app.post("/api/upload_csv")
async def upload_csv(file: Annotated[UploadFile, File()]):
    try:
        file_location = f"/tmp/{file.filename}"
        with open(file_location, "wb+") as file_object:
            file_object.write(file.file.read())
        return {"status": "success", \
                "message": f"`{file.filename}` file saved at `{file_location}` location;"}
    except Exception as e:
        return {"status": "error", \
                "message": f"`{file.filename}` file was not saved; error: {str(e)};"}
    
@app.get("/api/download_csv")
async def download_csv(file_name: str):
    try:
        file_location = f"/tmp/{file_name}"
        with open(file_location, "rb") as file_object:
            content = file_object.read()
        if content is None:
            return {"status": "error", \
                    "message": f"'{file_name}' file was not found."}
        headers = {'Content-Disposition': f'attachment; filename="{file_name}"'}
        file_response = FileResponse(file_location, headers=headers, media_type='text/csv')
        return file_response
    except Exception as e:
        return {"status": "error", \
                "message": f"`{file_location}` file was not downloaded; error: {str(e)};"}
    
@app.get("/api/create_gantt")
async def create_gantt(file_name: str):
    try:
        file_location = f"/tmp/{file_name}"
        row_data = file2row(file_location)
        print(row_data)
        plot_gantt("GANTT CHART", row_data)
        save_plot()
        headers = {'Content-Disposition': f'attachment; filename="gantt.png"'}
        file_response = FileResponse(FIG_LOCATION, headers=headers, media_type='image/png')
        return file_response
    except Exception as e:
        return {"status": "error", \
                "message": f"`{file_location}` file was not processed to create gantt; error: {str(e)};"}

# HTML-views

@app.get("/html/upload_csv", response_class=HTMLResponse)
async def html_upload_csv():
    with open('html/upload_csv.html', 'r') as file:
        html_response = file.read()
    return html_response