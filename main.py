from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status, UploadFile, Form
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from contextlib import asynccontextmanager
import os
import json
import bcrypt
import aiofiles
import asyncio

BASE_DIR = os.path.dirname(__file__)
TEMP_DIR = os.path.join(os.getcwd(), "temp")
SETTING_DIR = os.path.join(os.getcwd(), "Settings")
online_users = []
ipv4port = ["192.168.1.4", "8000"] ## Will be later changed by the Registery App.
upload_status = "green" ## Default upload status.

@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(TEMP_DIR, exist_ok=True)
    asyncio.ensure_future(cleanup_chore())
    yield
app = FastAPI(lifespan=lifespan)
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
    await manager.broadcast("Uploaded files will be automatically removed from the server storage based on their size and uploader's prompt response.")
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
async def create_upload_files(file: list[UploadFile], special: bool = Form(False)):
    global upload_status
    for f in file:
        path = os.path.join(TEMP_DIR, f.filename)
        async with aiofiles.open(path, 'wb') as out:
            upload_status = "yellow"
            await manager.broadcast(f"Upload_Status:{upload_status}")
            while chunk := await f.read(1024 * 1024):
                await out.write(chunk)
        await manager.broadcast(f"FILE_ADD:{f.filename}")
        await asyncio.sleep(2)
        upload_status = "red"
        await manager.broadcast(f"Upload_Status:{upload_status}")
        await asyncio.sleep(2)
        upload_status = "green"
        await manager.broadcast(f"Upload_Status:{upload_status}")
        asyncio.create_task(upload_tick(f.filename, special))
    return {"filenames": [f.filename for f in file]}
@app.get("/download/{filename}")
async def download_file(filename: str):
    path = os.path.join(TEMP_DIR, filename)
    if filename in os.listdir(TEMP_DIR):
        return FileResponse(path, filename=filename)
    else:
        raise HTTPException(status_code=404, detail="File not found")
@app.get("/files")
async def available_files():
    files = os.listdir(TEMP_DIR)
    return {"files": files}

async def upload_tick(name: str, special: bool): ## Cleans up the temp directory
    files = os.listdir(TEMP_DIR)
    if name in files:
        path = os.path.join(TEMP_DIR, name)
        weight = os.path.getsize(path)
        if not special:
            if weight <= 1024 * 1024 * 20:
                await manager.broadcast(f"File {name} will be removed from server storage in 10 minutes.")
                await asyncio.sleep(600)
                os.remove(path)
                await manager.broadcast(f"File {name} has been removed from server storage.")
            elif weight <= 1024 * 1024 * 100:
                await manager.broadcast(f"File {name} will be removed from server storage in 20 minutes.")
                await asyncio.sleep(1200)
                os.remove(path)
                await manager.broadcast(f"File {name} has been removed from server storage.")
            elif weight <= 1024 * 1024 * 500:
                await manager.broadcast(f"File {name} will be removed from server storage in 30 minutes.")
                await asyncio.sleep(1800)
                os.remove(path)
                await manager.broadcast(f"File {name} has been removed from server storage.")
            elif weight <= 1024 * 1024 * 1024:
                await manager.broadcast(f"File {name} will be removed from server storage in 60 minutes.")
                await asyncio.sleep(3600)
                os.remove(path)
                await manager.broadcast(f"File {name} has been removed from server storage.")
            else:
                await manager.broadcast(f"File {name} will be removed from server storage in 120 minutes.")
                await asyncio.sleep(7200)
                os.remove(path)
                await manager.broadcast(f"File {name} has been removed from server storage.")
        elif special:
            await manager.broadcast(f"File {name} will be removed from server storage in 7 hours.")
            await asyncio.sleep(25200)
            os.remove(path)
            await manager.broadcast(f"File {name} has been removed from server storage.")
    else:
        pass
async def reverse_upload_tick(name: str, special: bool):
    files = os.listdir(TEMP_DIR)
    if name in files:
        path = os.path.join(TEMP_DIR, name)
        weight = os.path.getsize(path)
        if not special:
            if weight <= 1024 * 1024 * 20:
                await asyncio.sleep(25200)
                os.remove(path)
                await manager.broadcast(f"File {name} has been removed from server storage.")
            elif weight <= 1024 * 1024 * 100:
                await asyncio.sleep(25200)
                os.remove(path)
                await manager.broadcast(f"File {name} has been removed from server storage.")
            elif weight <= 1024 * 1024 * 500:
                await asyncio.sleep(3600)
                os.remove(path)
                await manager.broadcast(f"File {name} has been removed from server storage.")
            elif weight <= 1024 * 1024 * 1024:
                await asyncio.sleep(1800)
                os.remove(path)
                await manager.broadcast(f"File {name} has been removed from server storage.")
            else:
                await asyncio.sleep(1200)
                os.remove(path)
                await manager.broadcast(f"File {name} has been removed from server storage.")
    else:
        pass
async def cleanup_chore():
    if TEMP_DIR:
        files = os.listdir(TEMP_DIR)
        if files:
            for file in files:
                await reverse_upload_tick(file, False)
        else:
            pass
    else:
        pass
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)