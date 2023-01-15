import socket
import threading
import pyautogui
import time
from rich.console import Console
from pynput import keyboard


console = Console()
exit_event = threading.Event()
stop_listening = False

choice = input('Do you want to host (1) or to connect (2):')

if choice == '1':
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#    hostname = socket.gethostname()
#    ip_addr = socket.gethostbyname(hostname)
    ip_addr = input('Enter your IPv4: ')
    server.bind((ip_addr, 9999))
    console.print(f'[yellow]Waiting for other machine to connect...[/yellow]')
    server.listen()

    client, _ = server.accept()
    console.print(f'[green]A connection has been established.[/green]')

elif choice == '2':
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ip_addr = input('Enter the IPv4 of the other machine: ')
    client.connect((ip_addr, 9999))
    console.print(f'[green]A connection has been established.[/green]')

else:
    exit()
  
  
def sending_messages(c):
    while True:
        message = input('')
        c.send(message.encode())


def receiving_message(c):
    def press(command):
        global stop_listening
        stop_listening = True
        pyautogui.press(command)
        stop_listening = False
                
    while True:
        message = str(c.recv(1024).decode())
        if message:
            console.print(f'[blue]<SENDER>[/blue] : {message}')
            if message == str(keyboard.Key.space):
                press("space")
            elif message == str(keyboard.Key.right):
                press("right")
            elif message == str(keyboard.Key.left):
                press("left")
        else:
            exit_event.set()
            console.print(f'[red]The connection has been disconnected.[/red]')
            pyautogui.press("space")
            exit()


def on_press(key):
    if exit_event.is_set():
        return False

    global stop_listening
    
    if not stop_listening and key in [keyboard.Key.space, keyboard.Key.right, keyboard.Key.left]:
        console.print(f'[red]<YOU>[/red] : {key}')
        client.send(str(key).encode())
        time.sleep(0.7) #FIXME
        return False
        
    elif key in [keyboard.Key.shift_r, keyboard.Key.shift] and not stop_listening:
            stop_listening = True
            console.print(f'[yellow]STOP[/yellow]')
    elif key == keyboard.Key.enter and stop_listening:
            stop_listening = False
            console.print(f'[yellow]RESUME[/yellow]')
        

#threading.Thread(target=sending_messages, args=(client,)).start()
threading.Thread(target=receiving_message, args=(client,), daemon=True).start()

while True:
    listener = keyboard.Listener(on_press=on_press)
    listener.daemon = True
    listener.start()
    listener.join()
    
    if exit_event.is_set():
        if choice == '1':
            server.close()
        client.close()
        exit()

