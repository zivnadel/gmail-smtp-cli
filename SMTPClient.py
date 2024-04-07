from socket import *
from colorama import Fore, Style
from getpass import getpass
import ssl, base64, atexit, re

def send(command, code, cs, error=""):
    cs.sendall((command + '\r\n').encode())
    res = cs.recv(1024).decode()

    if res[:3] != str(code):
        print(Fore.RED +
              "\n" + 
              (error if error else "Unknown error occured!") + 
              f"\nExpected reply code: {code}\nExiting!")
        exit()

def connect(server, port, email, password):
    cs = socket(AF_INET, SOCK_STREAM)
    cs.connect((server, port))
    res = cs.recv(1024).decode()

    if res[:3] != "220":
        print(Fore.RED + "\nConnection failed! Please try again.")
        exit()

    send("HELO gmail.com", 250, cs)

    send("STARTTLS", 220, cs)

    context = ssl.create_default_context()
    cs = context.wrap_socket(cs, server_hostname=server)

    send("AUTH LOGIN", 334, cs)
    send(base64.b64encode(email.encode()).decode(), 334, cs, "Incorrect credentials!")
    send(base64.b64encode(password.encode()).decode(), 235, cs, "Incorrect credentials!")

    return cs

def mailto(sender, recipient, subject, body, cs):
    send(f'MAIL FROM: <{sender}>', 250, cs, "Corrupted sender/recipient address!")
    send(f'RCPT TO: <{recipient}>', 250, cs, "Corrupted sender/recipient address!")
    send('DATA', 354, cs)

    email_message = f'Subject: {subject}\r\n'
    email_message += f'From: {sender}\r\n'
    email_message += f'To: {recipient}\r\n'
    email_message += f'\r\n{body}\r\n.\r\n'

    send(email_message, 250, cs, "Corrupted mail content!")

def multiline_input(prompt):
    print(prompt)

    line, lines = input(), [] 
    while line != '.':  
        lines.append(line) 
        line = input()

    return '\n'.join(lines)

def close(cs):
    print(Fore.LIGHTRED_EX + "\nExiting...")
    send('QUIT', 221, cs, "Error terminating the session!")
    cs.close()
    exit()

if __name__ == "__main__":
    try:
        server, port = 'smtp.gmail.com', 587

        atexit.register(lambda: print(Style.RESET_ALL))

        print(Fore.CYAN + """
    _____ __  __          _____ _         _____ __  __ _______ _____  
    / ____|  \/  |   /\   |_   _| |       / ____|  \/  |__   __|  __ \ 
    | |  __| \  / |  /  \    | | | |      | (___ | \  / |  | |  | |__) |
    | | |_ | |\/| | / /\ \   | | | |       \___ \| |\/| |  | |  |  ___/ 
    | |__| | |  | |/ ____ \ _| |_| |____   ____) | |  | |  | |  | |     
    \_____|_|  |_/_/    \_\_____|______| |_____/|_|  |_|  |_|  |_| 
                        _____   _            _
                        / ____| (_)          | |                       
                        | |    | |_  ___ _ __ | |_                      
                        | |    | | |/ _ \ '_ \| __|                     
                        | |____| | |  __/ | | | |_                      
                        \_____|_|_|\___|_| |_|\__|                     
    \n\n""")
        
        print("Welcome the the Gmail SMTP Client!\n" + Style.RESET_ALL)

        email = input("Please enter your Gmail Address: ")
        while not re.match("^[a-zA-Z0-9]+@gmail\.com", email):
            email = input(f"{Fore.RED}Corrupted address!{Style.RESET_ALL} Please retry: ")
        
        print("Please enter you password below. The input will be hidden.\n(You will have to enable 2FA in order to create an App Password)")
        password = getpass()
        while password == "":
            password = getpass(f"{Fore.RED}You cannot enter an empty password!{Style.RESET_ALL} Please retype: ")

        cs = connect(server, port, email, password)

        print(Fore.GREEN + "\nSuccessfuly logged in!\n" + Style.RESET_ALL)

        ans = 'y'
        while ans == 'y':
            recipient = input(Fore.LIGHTBLUE_EX + "Enter recipient: " + Style.RESET_ALL)
            while not re.match("^[a-zA-Z0-9]+@[a-zA_Z0-9]+\.[a-zA_Z0-9]+", recipient):
                recipient = input(f"{Fore.RED}Corrupted recipient address!{Style.RESET_ALL} Please retry: ")
            
            subject = input(Fore.LIGHTBLUE_EX + "Enter subject: " + Style.RESET_ALL)
            while subject == "":
                subject = input(f"{Fore.RED}You cannot enter an empty subject!{Style.RESET_ALL} Please retype: ")

            body = multiline_input(Fore.LIGHTBLUE_EX + "Enter mail (enter '.' to finish): " + Style.RESET_ALL)

            mailto(email, recipient, subject, body, cs)

            print(Fore.GREEN + "\nEmail succesfuly sent!\n" + Style.RESET_ALL)
            ans = input(Fore.LIGHTBLUE_EX + "Do you want to send another? (y/N)\n " + Style.RESET_ALL)

        close(cs)
    
    except KeyboardInterrupt:
        print(Fore.LIGHTRED_EX + "\n\nExiting...")
        exit()