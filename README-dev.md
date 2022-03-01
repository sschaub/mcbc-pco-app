# README

## Development Setup: Windows

### Python setup

Setup a Python virtual environment:
```
pip install virtualenv
virtualenv .venv
.venv\Scripts\activate
pip install -r api\requirements.txt
```

Create .env in root folder of this project:
```
PCO_APP_ID=...put PCO App ID here...
PCO_SECRET=...
PCO_WEBAPP_LOGIN_USERNAME=...
PCO_WEBAPP_LOGIN_PASSWORD=...
DB_PATH=/dev/mcbc-pco-app/db/mcbcmusic.sqlite3
SENDGRID_API_KEY=...SENDGRID API KEY HERE...
FLASK_SECRET_KEY=...FLASK SECRET KEY HERE...
INITIAL_EMAIL_LIST=...comma-delimited list of email addresses to receive initial special title submissions...
ALL_EMAIL_LIST=...comma-delimited list of email addresses to receive special info submissions...
LOG_LEVEL=DEBUG
```

### NodeJS setup

Install NodeJS. Then:
```
cd ui
npm install
```

## Start Debugging

To start UI module:
```
cd ui
npm run dev
```

To start API module: In VSCode, in the debug tab, pick Python: Flask and choose Run > Start Debugging. This will import environment variables
from .env and start server.py.


## Development Setup: Docker

On Windows:

1. Install WSL
2. Install Docker Desktop
3. Checkout project to WSL home directory (~)
4. Create a file named ~/mcbc-pco-app/.env containing the following:

   ```
   PCO_APP_ID=...put PCO App ID here...
   PCO_SECRET=...
   PCO_WEBAPP_LOGIN_USERNAME=...
   PCO_WEBAPP_LOGIN_PASSWORD=...
   ```

To start:

```
cd ~/mcbc-pco-app
./devrun
```

With VSCode:

1. Open VSCode:
   ```
   cd ~/mcbc-pco-app
   mkdir ~/mcbc-pco-app/ui/node_modules
   code .
   ```
2. In VSCode, Remote-Containers: Reopen Folder in Container
3. Install modules:
   ```
   cd /workspace/ui
   sudo -u node npm install
   ```
4. Install VSCode Vetur extension for intellisense and syntax highlighting
5. Start UI app:
   ```
   cd ui
   npm run serve
   ```

Test URL's:
* Application UI: http://localhost:8080
* Application API: http://localhost:9091
