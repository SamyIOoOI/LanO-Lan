from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status, File, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
import os
import json
import bcrypt
import aiofiles
import time
import subprocess
import asyncio


app = FastAPI()
BASE_DIR = os.path.dirname(__file__)
TEMP_DIR = os.path.join(os.getcwd(), "temp")
SETTING_DIR = os.path.join(os.getcwd(), "Settings")
Requests = []
Halts = []
Devices = []
online_users = []
ipv4port = ["192.168.1.4", "8000"] ## Will be later changed by the Registery App.
upload_status = "green"
os.makedirs(TEMP_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")
app.mount("/Settings", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "Settings")), name="Settings")

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)
manager = ConnectionManager()
## Security
with open(os.path.join(SETTING_DIR, "users_db.json")) as f:
    users_db = json.load(f)
def real_hash_password(password: str):
    hashedpassword = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashedpassword
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
class User(BaseModel):
    username: str

class UserInDB(User):
    hashed_password: str


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def fake_decode_token(token):
    user = get_user(users_db, token)
    return user


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_dict = users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = UserInDB(**user_dict)
    if not bcrypt.checkpw(form_data.password.encode('utf-8'), user.hashed_password.encode('utf-8')):
         raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user.username, "token_type": "bearer"}


@app.get("/info")
async def get_ipnport():
    return {"ipv4": ipv4port[0], "port": ipv4port[1]}
@app.get("/users/me")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user
@app.get("/")
async def get_login():
    return FileResponse(os.path.join(BASE_DIR, "static/login.html"))
@app.get("/chat")   
async def get_chat():
    return FileResponse(os.path.join(BASE_DIR, "static/chat.html"))
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str, token: str):
    user = fake_decode_token(token)
    if not user:
        await websocket.close(code=1008)
        return
    await manager.connect(websocket)
    online_users.append(user.username)
    await manager.broadcast(f"User_List:{json.dumps(online_users)}")
    try:
        while True:
            data = await websocket.receive_text()
            coded_message = f'<span style="color: lightgreen;">{user.username}:</span> {data}'
            await manager.broadcast(coded_message)
    except WebSocketDisconnect: 
        manager.disconnect(websocket)
        online_users.remove(user.username)
        await manager.broadcast(f"User_List:{json.dumps(online_users)}")
        await manager.broadcast(f"{user.username} has left the chat")
@app.post("/uploadfiles/")
async def create_upload_files(file: list[UploadFile]):
    global upload_status
    for f in file:
        path = os.path.join(TEMP_DIR, f.filename)
        async with aiofiles.open(path, 'wb') as out:
            upload_status = "yellow"
            await manager.broadcast(f"Upload_Status:{upload_status}")
            while chunk := await f.read(1024 * 1024):
                await out.write(chunk)
        await manager.broadcast(f"FILE_ADD:{f.filename}")
        upload_status = "red"
        await manager.broadcast(f"Upload_Status:{upload_status}")
        await asyncio.sleep(2)
        upload_status = "green"
        await manager.broadcast(f"Upload_Status:{upload_status}")
    return {"filenames": [f.filename for f in file]}
@app.get("/download/{filename}")
async def download_file(filename: str):
    path = os.path.join(TEMP_DIR, filename)
    return FileResponse(path, filename=filename)
@app.get("/files")
async def available_files():
    files = os.listdir(TEMP_DIR)
    return {"files": files}
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)