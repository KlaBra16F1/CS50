# Documentaation

## Use cases
```plantuml
@startuml
left to right direction
actor Admin as a
actor Maintainer as m
actor User as u
actor Guest as g
package Website {
    usecase "register" as uc0
    usecase "Create test from topics/subtopics" as uc1
    usecase "Take test" as uc2
    usecase "Store statistics from tests" as uc3
    usecase "View personal statistics" as uc4
    usecase "CRUD topics/subtopics" as uc5
    usecase "CRUD questions/answers" as uc6
    usecase "See all statistics" as uc7
    usecase "CRUD users" as uc8
    (login)
}
g --> uc0
g --> uc1
g --> uc2
g <|-- u
u --> (login)
u --> uc3 
u --> uc4 
u <|-- m 
m --> uc5
m --> uc6
m --> uc7
m <|-- a 
a --> uc8
@enduml
```

## Database
```sql
-- static tables
CREATE TABLE users (u_id INTEGER PRIMARY KEY NOT NULL DEFAULT rowid, name TEXT NOT NULL, hash TEXT NOT NULL,role TEXT NOT NULL DEFAULT 'user');

CREATE TABLE topics (t_id INTEGER PRIMARY KEY NOT NULL DEFAULT rowid, topic TEXT NOT NULL);

CREATE TABLE subtopics (s_id INTEGER PRIMARY KEY NOT NULL DEFAULT rowid, t_id INTEGER, subtopic TEXT NOT NULL, FOREIGN KEY (t_id) REFERENCES topics(t_id));

CREATE TABLE questions (q_id INTEGER PRIMARY KEY NOT NULL DEFAULT rowid, s_id INTEGER NOT NULL, question TEXT NOT NULL, difficulty INTEGER DEFAULT 0, isMultipleChoice NUMERIC DEFAULT 0, FOREIGN KEY (s_id) REFERENCES subtopics(s_id));

CREATE TABLE answers (a_id INTEGER PRIMARY KEY NOT NULL DEFAULT rowid, q_id INTEGER NOT NULL, answer TEXT NOT NULL, comment TEXT, is_true NUMERIC NOT NULL DEFAULT 0, FOREIGN KEY (q_id) REFERENCES questions(q_id));

CREATE TABLE user_questions (u_id INTEGER NOT NULL, q_id INTEGER NOT NULL, timesDone INTEGER NOT NULL, timesRight INTEGER NOT NULL, 
    accuracy REAL GENERATED ALWAYS AS (ROUND(CAST(timesRight AS REAL) / CAST(timesDone AS REAL),2)),lastDate TEXT);

CREATE TABLE user_tests (ut_id INTEGER PRIMARY KEY NOT NULL DEFAULT rowid, u_id INTEGER NOT NULL, test_name TEXT NOT NULL ,questions TEXT NOT NULL, FOREIGN KEY (u_id) REFERENCES users(u_id));

CREATE TABLE teststats (testsMade integer, forUser integer); INSERT INTO teststats VALUES(0,0);

-- index

CREATE INDEX idx_uq ON user_questions (u_id, q_id);


select * from sqlite_master where type = 'index';
```

```mermaid
erDiagram

topics {
    int t_id
    text topic
}
subtopics {
    int s_id
    int t_id
    text subtopic
}
questions {
    int q_id
    int s_id
    text question
    int difficulty
    int isMultipleChoice
}
answers {
    int a_id
    int q_id
    text answer
    text comment
    int true
}
users {
    int u_id
    text name
    text hash
    text role
}
user_questions {
    int u_id
    int q_id
    int timesDone
    int timesRight
    real accuracy
    text lastDate
}
user_tests {
    int ut_id
    int u_id
    text test_name
    text questions
}


topics ||--o{ subtopics : has
subtopics ||--o{ questions : has
questions ||--o{ answers : has
users ||--o{ user_questions : n
questions ||--o{ user_questions : n
users ||--o{ user_tests : n
user_tests ||--o{ questions : n
```