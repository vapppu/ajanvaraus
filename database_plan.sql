
CREATE TABLE user (
    id INTEGER PRIMARY KEY, 
    email TEXT NOT NULL,
    passw TEXT NOT NULL
    );

CREATE TABLE calendar (
    id INT PRIMARY KEY,
    name TEXT NOT NULL,
    owner_id INT NOT NULL,
    additional_info TEXT,
    FOREIGN KEY (owner_id)
        REFERENCES user(id)     
    );


CREATE TABLE appointment (
    id INT PRIMARY KEY,
    calendar_id INT NOT NULL,
    starting_time TEXT NOT NULL,
    ending_time TEXT NOT NULL,
    available BOOL NOT NULL,
    description TEXT NOT NULL, (<- on kellonajat tekstinä)
    FOREIGN KEY (calendar_id)
        REFERENCES calendar(id)
    );

CREATE TABLE answer (
    id INT PRIMARY KEY,
    appointment_id ID INT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    type TEXT NOT NULL,
    participant_id INT NOT NULL,
    FOREIGN KEY (appointment_id)
        REFERENCES appointment(id),
    FOREIGN KEY (participant_id)
        REFERENCES user(id)
    );



from werkzeug.security import check_password_hash, generate_password_hash



def register_user():

    username = input("Username: ")
    passw = generate_password_hash(input("Password: "))

    try:

        connect = sqlite3.connect('database.db')
        cursor = connect.cursor()
        print("Connection to SQLite DB successful")

    except sql.Error as e:
        print(f"The error '{e}' occurred")
    
    cursor.execute("""INSERT INTO user(email,passw) VALUES (?,?)""", (username, passw))

    connect.commit()

    connect.close()




def main():

    register_user()


if __name__ == "__main__":
    main()



