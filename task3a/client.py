import socket


def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('127.0.0.1', 9999))
    logged_in = False

    while True:
        if not logged_in:
            command = input("Enter command (register, login): ").lower()
        else:
            command = input(
                "Enter command (add_quiz, answer_quiz, view_leaderboard, exit): ").lower()

        if command == "exit":
            break

        if command in ["register", "login"]:
            username = input("Enter username: ").lower()
            password = input("Enter password: ")
            message = f"{command} {username} {password}"
        elif command == "add_quiz":
            question = input("Enter question: ")
            options = [input(f"Option {i+1}: ") for i in range(4)]
            correct_option = input("Enter correct option number (1-4): ")
            message = f"{command} {question}~{options[0]}~{
                options[1]}~{options[2]}~{options[3]}~{correct_option}"
        elif command == "answer_quiz":
            message = command
        elif command == "view_leaderboard":
            message = command
        else:
            print("Invalid command.")
            continue

        try:
            client.send(message.encode('utf-8'))
            response = client.recv(4096).decode('utf-8')
            print(f"Received: {response}")

            if command == "login" and "login successful" in response.lower():
                logged_in = True

            if command == "answer_quiz" and "no more questions available" not in response.lower():
                answer = input("Enter your answer: ")
                client.send(answer.encode('utf-8'))
                response = client.recv(4096).decode('utf-8')
                print(f"Received: {response}")

                # Continue answering questions if available
                while True:
                    continue_response = input(
                        "Do you want to answer more questions? (y/n): ").strip().lower()
                    client.send(continue_response.encode('utf-8'))
                    if continue_response != 'y':
                        break
                    response = client.recv(4096).decode('utf-8')
                    print(f"Received: {response}")
                    if "no more questions available" in response.lower():
                        break
                    answer = input("Enter your answer: ")
                    client.send(answer.encode('utf-8'))
                    response = client.recv(4096).decode('utf-8')
                    print(f"Received: {response}")

        except BrokenPipeError:
            print("Connection to server lost. Please restart the client.")
            break


if __name__ == "__main__":
    main()
