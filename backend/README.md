# Clone the repo 

### With ssh:
```bash
git clone git@github.com:Shabbir-Anjum/TravelSpotter.git
```

### With https:
```bash
git clone https://github.com/Shabbir-Anjum/TravelSpotter.git
```
# Move to parent directory
```bash
cd TravelSpotter
```

# Set db connection settings in .env
```bash
cp .env.example .env
```
```bash
vi .env
```
### Set password for your mysql user in .env
### Do not change only the MYSQL_HOST

# Set another .env for frontend
```bash
cd frontend/
```
Set up the keys and `copy` the following code
```bash
NEXT_PUBLIC_FIREBASE_API_KEY=
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=
NEXT_PUBLIC_FIREBASE_PROJECT_ID=
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=
NEXT_PUBLIC_FIREBASE_APP_ID=
NEXT_PUBLIC_GOOGLE_CLIENT_ID=
NEXT_PUBLIC_GOOGLE_CLIENT_SECRET=
NEXT_PUBLIC_GOOGLE_API_KEY=
```
Paste the code in .env :
```bash
vi .env
```

# Now go to backend folder
```bash
cd ../backend/
```
```bash
cp .env.example .env
```
Open the `.env` file
```bash
vi .env
```

Change both keys (I need to remove the connection_uri key)

# Run Docker compose
```bash
docker compose build
```
```bash
docker compose up
```
You can use `up -d` or just `up`

# Your app is ready!!

# Port mapping :
`backend` : 5000

`frontend` : 3000

`mysql` : 3306

`phpmyadmin` : 8080

# Simple Docker commands : 
### List all containers for this compose file
```bash
docker compose ps
```
### Execute container
```bash
docker exec -it `container_name` bash
```
change container name

Example : 
* travelspotter-backend-1
* mysql
* travelspotter-frontend-1
....

# Connect to phpadmin on 
```address
http://localhost:8080
```
with your user and password from main .env file

# Insert data in base
> try by yourself on this

see the user on :
```address
http://localhost:5000/api/users/<id>
```

Currently just this route is working.

# Do not modify docker files

<p> Work on models.py, routes.py and app.py. Try to implement every model from main.py in
this three scripts, than remove main.py </p>

## Happy coding :)

