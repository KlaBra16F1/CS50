# _Test_**Forge**

### Video Demo:  <URL HERE>
### Description:
_Test_**Forge** is a multiple choice test-generator with a variety of options, depending on the role of the user.

#### Visitors:
As a unregistered guest you can create a test from available topics, subtopics (multiple selection) or a random set across all topics. After finishing your test, you get your results along with - if available - some helpful comments on wrong answers. If a question has multiple right answers and you missed one, there might be a comment, too. Visitors can also register as users.

#### Users:
For registered users the test results are stored per question the database. This way your next test will consist of questions you haven't answered, you haven't answered recently or you haven't answered right. You also have the option to save a finished test, in case you want to repeat it later. Saved tests can be found on the users profile page, where you can find some statistics, track your progress and compare against other users. Here you can also change your password or delete your account.

#### Maintainer:
If you're promoted to maintainer, you can create new topics and suptopics, add questions, answers and helpful comments. Of course you can edit or delete each item from the database, too. There's even markdown support so you can write __bold__, _italics_ and `code`. Sortable and searchable tables will be of great assistance when dealing with lots of entries. You also have access to the site statistics, where you can track the test activity and if you have enough questions for your users demands.

#### Admin:
As an admin you have access to user management. You can easily generate new accounts and are privileged to hand out _unsafe_ passwords (i.e. for test accounts). You can also promote users to maintainer or admin and - if neccessary - delete user accounts.

> [!TIP]
> 
> To get you started, the database is filled with a bunch of questions from categories like 'Programming Languages' or 'Web Design'. Of course it's easy to delete whole topics, so a clean start is only six clicks away.

### Usage 

#### Run with Python

1. Clone the repository and `cd` into the `CS50-Final_Project/app` directory
```bash
git clone https://github.com/KlaBra16F1/CS50-Final_Project.git
```
2. Install requrirements (Consider a virtual environment like Venv or Conda)
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
# Everything inside docker
docker run -p 8080:5000  --name TestForge TestForge/testforge:v1.0.0
# Persistent database in your host-folder (Reccomended)
docker run -p 8080:5000  -v /your/desired/path:/app/database --name TestForge TestForge/testforge:v1.0.0
```
4. Open your browser and go to `http://localhost:5000`

5. Login as user: `admin` password: `admin`

6. Enjoy

> [!WARNING]
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

### Docs

Visit the [Documentation](/docs/documentation.md) for more information about the app.


