#fastapi app
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from main import Database

app = FastAPI()

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Create a Database instance
db = Database('entities.db')

@app.get("/data")
async def get_data():
    # Return entities and edges as JSON
    content = db.get_entities_and_edges()
    print(content)
    return JSONResponse(content=content)

@app.get("/")
async def read_root(request: Request):
    # Render the index.html template
    return templates.TemplateResponse("index.html", {"request": request})
