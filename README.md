------------------------------------


![alt text](<LanO'Lan Banner.gif>)
-------------------------------------------
<div align="center"><h1>Lan O' Lan</h1>
</div>


***Need a Lan-Based messaging and file sharing utility but they're all a decade old and barely work? Got tired of searching in overly outdated websites? I've been there. LanO'Lan was my solution, available for anyone, available everywhere. Open-Source for all of us.***

---------------------------------------------

<h2>How does it work?</h2>

* The main host "server" device broadcasts the application and website through websocket.
* The Websocket connection doesn't require any internet bandwidth as it relies on lan-to-lan connection between devices on the same network.
* The host device generates local certificates to allow for https connections needed for Video/Audio connections via WebRTC
* Clients access the app through the link provided to the host from the controller application.
* The local certificates will prompt a "danger" warning when clients access via website, ignore it and continue, just like your router's settings.
* Each client has a username and password, with the password only stored as a hash.
----------------
<h2>Features</h2>

* Clients have access (as of version 1.0.1) to the following: 

* Global text chat.

* Voice Chat (P2P).
  
* Video chat (P2P).

* Call Acceptance/Rejection Handling
  
* End Call Functionality (Automatically clears video input/output)

* File Upload/Download.

* File Upload/Download Status Indicator (green: free, yellow: uploading, red: uploaded)

* Automatic Server Storage Optimization (with an override option extended via /Settings).

* Automatic SSL Certificate Generation

* Automatic IPV4 Discovery

* Customizable Font, SoundEffects and Port via /Settings/

* Global Server Broadcasts for Joins/Leaves/Uploads/Deletions

*Note: Mobile clients get "upload pictures or videos" prompt, ignore it, any type of file can be uploaded via your files application.*

--------------
<h3>Does it need internet bandwidth to work?</h3>

--------------------------------------------------

*Nope, that defeats the whole purpose of LanO'Lan,
all you need is a LAN connection, a mobile hotspot without internet worked perfectly as shown in the video.*

----
<h2>Deployment<h2>

> For Windows users, download the latest release .zip file, extract and run LanO'Lan.exe for GUI, or LoLServer.exe to directly start the server.

> For Linux users, download the latest release .zip file, open terminal, cd [path to folder extracted], ./LanO'Lan (if it returns an error rename the file to LanOLan and retry) for GUI, and the same for LoLServer.

> For Source-Code deployment, clone repository, pip install -r requirements.txt. Afterwards simply run register.py for GUI, and main.py for server only.

> For users running debian-based distributions that may separate tkinter as its own package or may have errors with the package, install it with the following command. sudo apt install python3-tk && sudo apt install python3-ttkthemes
 (debian), sudo dnf install python3-tkinter && sudo dnf install python3-ttkthemes (Fedora/RHEL), sudo pacman -S tk && yay -S ttk-themes-chooser (Arch)

> In case you cannot launch the server due to the port being used, check for LoLServer process using taskmanager or terminal commands and terminate it. If the port is used by another application you can modify it in Settings/settings.json.

<h2>Mind Map</h2>  

***These are candidates for next updates or new features not yet implemented.***

* Pypi deployment (check the banner GIF)
* CLI // Headless version for clients and hosts (I know your kind)
* MAC-Based blocking (To keep unwanted devices away)
* Dark Mode (self explanatory)
* Simple games such as tic tac toe (P2P)
* Private direct messages


<h2>Notice</h2>

***Do not share sensitive information in public networks such as schools or internet-exposed LANs. LanO'Lan does not offer protection against man-in-the-middle attacks due to local SSL certificates.***

---------------
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

-----------------

Made by Samy0_o (SamyIOoOI) on github (2026-2027) Under MIT Licence.
