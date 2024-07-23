__Installation:__

requires python3.10+

```
cd fast_api_server
source venv/bin/activate (activate virtualenv)
pip install -r requirements.txt
// TODO should not need to manually install psycopg2-binary
pip install psycopg2-binary
cd client
npm install
```

__Run:__
in root dir (ensure venv is activated)
server `./startserver.sh`

client `npm start`

go to `http://localhost:3000/`
