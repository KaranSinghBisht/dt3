import socket
import threading
import hashlib
import sqlite3

# Database connection


def get_db_connection():
    conn = sqlite3.connect('quiz.db', check_same_thread=False)
    return conn

# Create tables if they do not exist


def setup_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS questions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        creator_id INTEGER,
                        question TEXT NOT NULL,
                        option1 TEXT NOT NULL,
                        option2 TEXT NOT NULL,
                        option3 TEXT NOT NULL,
                        option4 TEXT NOT NULL,
                        correct_option INTEGER NOT NULL,
                        FOREIGN KEY (creator_id) REFERENCES users(id))''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS leaderboard (
                        user_id INTEGER PRIMARY KEY,
                        score INTEGER DEFAULT 0,
                        FOREIGN KEY (user_id) REFERENCES users(id))''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS answers (
                        user_id INTEGER,
                        question_id INTEGER,
                        FOREIGN KEY (user_id) REFERENCES users(id),
                        FOREIGN KEY (question_id) REFERENCES questions(id),
                        PRIMARY KEY (user_id, question_id))''')
    conn.commit()
    conn.close()


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def register_user(cursor, username, password):
    password_hash = hash_password(password)
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
        cursor.execute(
            "INSERT INTO leaderboard (user_id) VALUES (LAST_INSERT_ROWID())")
        return "registration successful."
    except sqlite3.IntegrityError:
        return "username already exists."


def login_user(cursor, username, password):
    cursor.execute(
        "SELECT id, password_hash FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    if not result:
        return None, "username not found."
    elif result[1] != hash_password(password):
        return None, "incorrect password."
    else:
        return result[0], "login successful."


def add_quiz(cursor, user_id, question_data):
    question, option1, option2, option3, option4, correct_option = question_data.split(
        '~')
    cursor.execute("INSERT INTO questions (creator_id, question, option1, option2, option3, option4, correct_option) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (user_id, question, option1, option2, option3, option4, correct_option))
    return "quiz question added."


def get_unanswered_question(cursor, user_id):
    cursor.execute("""
        SELECT q.id, q.question, q.option1, q.option2, q.option3, q.option4 
        FROM questions q
        LEFT JOIN answers a ON q.id = a.question_id AND a.user_id = ?
        WHERE q.creator_id != ? AND a.user_id IS NULL
        LIMIT 1
    """, (user_id, user_id))
    return cursor.fetchone()


def check_answer(cursor, user_id, question_id, answer):
    cursor.execute(
        "SELECT correct_option FROM questions WHERE id = ?", (question_id,))
    correct_option = cursor.fetchone()
    if correct_option and int(answer) == correct_option[0]:
        cursor.execute(
            "UPDATE leaderboard SET score = score + 1 WHERE user_id = ?", (user_id,))
        cursor.execute(
            "INSERT INTO answers (user_id, question_id) VALUES (?, ?)", (user_id, question_id))
        return "correct answer!"
    else:
        cursor.execute(
            "INSERT INTO answers (user_id, question_id) VALUES (?, ?)", (user_id, question_id))
        return "incorrect answer."


def get_leaderboard(cursor):
    cursor.execute(
        "SELECT u.username, l.score FROM leaderboard l JOIN users u ON l.user_id = u.id ORDER BY l.score DESC")
    return cursor.fetchall()


def handle_client(client_socket, addr):
    print(f"Accepted connection from {addr}")
    user_id = None
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                command, *params = message.lower().split(' ', 1)
                if command == "register" and len(params) == 1:
                    username, password = params[0].split()
                    response = register_user(cursor, username, password)
                    conn.commit()
                    client_socket.send(response.encode('utf-8'))
                elif command == "login" and len(params) == 1:
                    username, password = params[0].split()
                    user_id, response = login_user(cursor, username, password)
                    client_socket.send(response.encode('utf-8'))
                elif user_id:
                    if command == "add_quiz" and len(params) == 1:
                        response = add_quiz(cursor, user_id, params[0])
                        conn.commit()
                        client_socket.send(response.encode('utf-8'))
                    elif command == "answer_quiz":
                        while True:
                            question = get_unanswered_question(cursor, user_id)
                            if question:
                                question_id, question_text, option1, option2, option3, option4 = question
                                formatted_question = (
                                    f"Question ID: {question_id}\n"
                                    f"{question_text}\n"
                                    f"1. {option1}\n"
                                    f"2. {option2}\n"
                                    f"3. {option3}\n"
                                    f"4. {option4}\n"
                                    f"Enter the number of your answer: "
                                )
                                client_socket.send(
                                    formatted_question.encode('utf-8'))
                                answer = client_socket.recv(
                                    1024).decode('utf-8')
                                response = check_answer(
                                    cursor, user_id, question_id, answer)
                                conn.commit()
                                client_socket.send(response.encode('utf-8'))

                                # Ask if the user wants to continue answering questions
                                client_socket.send(
                                    "Do you want to answer more questions? (y/n): ".encode('utf-8'))
                                continue_response = client_socket.recv(
                                    1024).decode('utf-8').strip().lower()
                                if continue_response != 'y':
                                    break
                            else:
                                client_socket.send(
                                    "No more questions available.".encode('utf-8'))
                                break
                    elif command == "view_leaderboard":
                        leaderboard = get_leaderboard(cursor)
                        leaderboard_str = "\n".join(
                            [f"{username}: {score}" for username, score in leaderboard])
                        client_socket.send(leaderboard_str.encode('utf-8'))
                    else:
                        client_socket.send("invalid command.".encode('utf-8'))
                else:
                    client_socket.send("please login first.".encode('utf-8'))
            else:
                break
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()
        client_socket.close()


def main():
    setup_db()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 9999))
    server.listen(5)
    print("Server started on port 9999...")

    while True:
        client_socket, addr = server.accept()
        client_handler = threading.Thread(
            target=handle_client, args=(client_socket, addr))
        client_handler.start()


if __name__ == "__main__":
    main()
