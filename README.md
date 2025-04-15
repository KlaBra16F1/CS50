# _Test_**Forge**
### Video Demo:  <URL HERE>
### Description:
_Test_**Forge** is a multiple choice test-generator with a variety of options, depending on a users role.

#### Visitors:
As a unregistered guest you can create a test from available topics, subtopics (multiple selection) or a random set across all topics. After finnishing your test, you get your test-results along with - if available - some helpful comments on wrong answers. If a questions has multiple right answers and you missed one, there might be a comment, too. Visitors can also register as users.

#### Users:
Registered users have the option to save a finnished test, in case they want to repeat it later. Saved tests can be found on the users profile page, where you can find some statistics, track your progress and compare against other users. Here you also can change your password or delete your account.

#### Maintainer:
If you're promoted to maintaier, you can create new topics and suptopics, add questions and answers or delete a bunch of them. Of course there's also the option to edit all the items from the database. Sortable and searchable tables will be of great assistance when dealing with lots of entries. You also have acces to the site statistics, where you can track the test activity and if you have enough questions for your users demands.

#### Admin:
As an admin you have acces to the users management. You can easily generate new accounts and are privileged to hand out _unsafe_ passwords (i.e. for test-accounts). You also can promote users to maintainer or admin and - if neccessary - delete user-accounts.

### Usage 

#### Run with Python

1. Clone the repository and `cd` into the `CS50-Final_Project/app` directory
```bash
git clone https://github.com/KlaBra16F1/CS50-Final_Project.git
```
2. Install requrirements (venv or conda reccomended)
```bash
pip install -r requirements.txt
```
3. Generate a secret
```
# Linux
EXPORT FLASK_SECRET_KEY="$(openssl rand -base64 32)"
# WINDOWS
$env:FLASK_SECRET_KEY = -join([char[]](33..122) | Get-Random -Count 32)
```
4. Run the app
```bash
# localhost only
flask run
# or in your local network
flask run --host=0.0.0.0
```
5. Open your browser and go to `http://localhost:5000`

6. Login as user: `admin` password: `admin`

7. Enjoy

#### Run with Docker

1. Clone the repository and `cd` into the `CS50-Final_Project` directory
```bash
git clone https://github.com/KlaBra16F1/CS50-Final_Project.git
```
2. Build the docker image
```bash
docker build -t TestForge/testforge:v1.0.0 -f docker/Dockerfile app
```
3. Run the docker image
```bash
docker run -p 8080:5000  --name TestForge TestForge/testforge:v1.0.0
```
4. Open your browser and go to `http://localhost:5000`

5. Login as user: `admin` password: `admin`

6. Enjoy

> [!CAUTION]
> This app is **NOT FOR PRODUCTION!!!**
>
> There is only minimal security and no HTTPS encryption, so it is strongly advised to use it only in your local network.

### Stack
- Backend
  - [Python](https://www.python.org)
  - [SQLite3](https://sqlite.org)
  - [Flask](https://github.com/pallets/flask)
  - [Jinja](https://github.com/pallets/jinja)
  - [Werkzeug](https://github.com/pallets/werkzeug/)
  - [CS50](https://github.com/cs50/python-cs50)
  - [Markdow](https://github.com/Python-Markdown/markdown)
- Frontend
  - HTML
  - CSS
  - JavaScript
  - [Metro_UI](https://github.com/olton/metroui)
  - [CanvasJS](https://canvasjs.com)


