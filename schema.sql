DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS calendar;
DROP TABLE IF EXISTS appointment;
DROP TABLE IF EXISTS answer;

CREATE TABLE user (
    id INTEGER PRIMARY KEY, 
    firstname TEXT NOT NULL,
    lastname TEXT NOT NULL,
    email TEXT NOT NULL,
    password_hash TEXT NOT NULL, 
    username TEXT NOT NULL
    );
CREATE TABLE calendar (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    owner_id INTEGER NOT NULL,
    additional_info TEXT,
    FOREIGN KEY (owner_id)
        REFERENCES user(id)     
    );
    CREATE TABLE appointment (
    id INTEGER PRIMARY KEY,
    calendar_id INT NOT NULL,
    starting_time TEXT NOT NULL,
    ending_time TEXT NOT NULL,
    available BOOLEAN NOT NULL,
    FOREIGN KEY (calendar_id)
        REFERENCES calendar(id) CHECK (available IN(0, 1))
    );
CREATE TABLE answer (
    id INT PRIMARY KEY,
    appointment_id ID INT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    participant_name TEXT NOT NULL,
    participant_email TEXT NOT NULL,
    FOREIGN KEY (appointment_id)
        REFERENCES appointment(id)
    );
