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
import subprocess
import re
import shutil
import sys
def the_base_dir_ugh():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))
BASE_DIR = the_base_dir_ugh()
TEMP_DIR = os.path.join(BASE_DIR, "temp")
SETTING_DIR = os.path.join(BASE_DIR, "Settings")
online_users = []
upload_status = "green" ## Default upload status.
max_wait_time = json.load(open(os.path.join(SETTING_DIR, "settings.json")))["max_wait_time"] ## Max wait time for file deletion, in seconds. Default is 7200 (2 hours).
ipv4 = json.load(open(os.path.join(SETTING_DIR, "settings.json")))["ipv4"] ## IPv4 address for the server.
port = json.load(open(os.path.join(SETTING_DIR, "settings.json")))["port"] 
ipv4port = [ipv4, port]  ## Will be later changed by the Registery App.
@asynccontextmanager
async def lifespan(app: FastAPI):
    global ipv4s
    os.makedirs(TEMP_DIR, exist_ok=True)
    asyncio.ensure_future(cleanup_chore())
    ipv4s = await get_ipv4s()
    yield
app = FastAPI(lifespan=lifespan)
os.makedirs(TEMP_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
app.mount("/Settings", StaticFiles(directory=os.path.join(BASE_DIR, "Settings")), name="Settings")
async def get_ipv4s(): ## Ignore it atp, I thought WebRTC would need it or something, I guess it can be later used to block certain ips? -- nah... , maybe (blocking with macs should be better)
    try:
        result = await asyncio.get_event_loop().run_in_executor(None, subprocess.check_output, ["arp", "-a"])
        result = result.decode('utf-8', errors='ignore')
        pattern = r"((?:\d{1,3}\.){3}\d{1,3})"
        ipv4ss = re.findall(pattern, result)
        ipv4s = set(ip for ip in ipv4ss if not ip.startswith(("224.", "239.", "255.")))
        return list(ipv4s)
    except Exception as e:
        pass
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, username: str):
        await websocket.accept()
        self.active_connections[username] = websocket

    def disconnect(self, username: str):
        self.active_connections.pop(username, None)

    async def broadcast(self, message: str):
        for ws in self.active_connections.values():
            await ws.send_text(message)
    async def send_private(self, username: str, message: str):
        ws = self.active_connections.get(username)
        if ws:
            await ws.send_text(message)
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
    with open(os.path.join(SETTING_DIR, "users_db.json")) as f:
        users_db = json.load(f)
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
    with open(os.path.join(SETTING_DIR, "users_db.json")) as f:
        users_db = json.load(f)
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
    await manager.connect(websocket, user.username)
    online_users.append(user.username)
    await manager.broadcast(f"User_List:{json.dumps(online_users)}")
    await manager.send_private(user.username, "Uploaded files will be automatically removed from the server storage based on their size and uploader's prompt response.")
    try:
        while True:
            data = await websocket.receive_text()
            if data.startswith("CALL_REQUEST:"):
                destination = data.split(":")[1]
                await manager.send_private(destination, f"CALL_REQUEST:{user.username}")
            elif data.startswith("CALL_ACCEPT:"):
                destination = data.split(":")[1]
                await manager.send_private(destination, f"CALL_ACCEPT:{user.username}")
            elif data.startswith("CALL_REJECT:"):
                destination = data.split(":")[1]
                await manager.send_private(destination, f"CALL_REJECT:{user.username}")
            elif data.startswith("OFFER:"):
                divided = data.split(":", 2)
                await manager.send_private(divided[1], f"OFFER:{user.username}:{divided[2]}")
            elif data.startswith("ANSWER:"):
                divided = data.split(":", 2)
                await manager.send_private(divided[1], f"ANSWER:{user.username}:{divided[2]}")
            elif data.startswith("ICE:"):
                divided = data.split(":", 2)
                await manager.send_private(divided[1], f"ICE:{user.username}:{divided[2]}")
            elif data.startswith("CALL_END:"):
                destination = data.split(":")[1]
                await manager.send_private(destination, f"CALL_END:{user.username}")
            else:
                coded_message = f'<span style="color: lightgreen;">{user.username}:</span> {data}'
                await manager.broadcast(coded_message)
    except WebSocketDisconnect: 
        manager.disconnect(user.username)
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
            await manager.broadcast(f"File {name} will be removed from server storage after {max_wait_time // 3600} hours.")
            await asyncio.sleep(max_wait_time)
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
                await asyncio.sleep(max_wait_time)
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
@app.get('/available')
async def check_space():
    total, used, free = shutil.disk_usage(TEMP_DIR)
    max_upload = int(free) // (1024 * 1024)
    return {'max_upload': max_upload}
@app.get('/favicon.ico')
async def favicon():
    return FileResponse(os.path.join(BASE_DIR, "static/favicon.ico"))
ssl_cert = os.path.join(SETTING_DIR, "Certificates", "cert.pem")
ssl_key = os.path.join(SETTING_DIR, "Certificates", "key.pem")
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=port, ssl_certfile=f"{ssl_cert}", ssl_keyfile=f"{ssl_key}")