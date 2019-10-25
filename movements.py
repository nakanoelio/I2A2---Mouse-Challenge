import os
import sys
import time
import pandas as pd
import threading
from pynput import mouse
from pynput import keyboard 
from pynput.keyboard import Key

class Recorder():
    def __init__(self):
        self.max_time = 3600 #segundos (1h)
        self.df = pd.DataFrame(columns=['client timestamp', 'button', 'state', 'x', 'y'])
        self.check_drag = False
        self.last_move = None

    def register_action(self, x, y, button, state):
        self.df = self.df.append({
            'client timestamp': time.time() - self.time0, 
            'button': button, 
            'state': state, 
            'x': int(x), 
            'y': int(y)
        }, ignore_index=True)

    def start(self):
        self.time0 = time.time()
        self.mouse_listener = mouse.Listener(on_move=self.on_move, on_click=self.on_click, on_scroll=self.on_scroll)
        self.mouse_listener.start()

    def stop(self):
        self.mouse_listener.stop()

    def save_csv(self):
        self.df['client timestamp'] = self.df['client timestamp'] - self.df['client timestamp'][0]
        self.df.to_csv('mouse_data.csv', index=False)

    def on_move(self, x, y):
        self.last_move = 'Move'
        if not self.check_drag:
            self.register_action(x, y, 'NoButton', 'Move')

    def on_click(self, x, y, button, pressed):
        if pressed:
            self.check_drag = True
            self.last_move = 'Pressed'
            self.register_action(x, y, str(button).split('.')[1].capitalize(), 'Pressed')
        else:
            self.check_drag = False
            if self.last_move != 'Pressed':
                self.register_action(x, y, 'NoButton', 'Drag')
            self.register_action(x, y, str(button).split('.')[1].capitalize(), 'Released')

    def on_scroll(self, x, y, dx, dy):
        self.register_action(0, 0, 'Scroll', 'Up' if dy>0 else 'Down')

def show_menu():
    text = \
    '''
        ================ Mouse Recorder ================

        Instruções Gerais:
        - Pressione 1 para iniciar a gravar os movimentos do mouse.
        - Pressione 2 para terminar a gravação e sair do programa.

        Obs.: O tempo máximo de gravação do programa é de 1 hora.

    '''
    return input(text + '\n\nEscolha uma opção: ')

def start_recording(recorder):
    recorder.start()
    t = threading.Timer(3600, stop_recording, [recorder])
    t.daemon = True
    t.start()

def stop_recording(recorder):
    recorder.save_csv()
    recorder.stop()
    print('\nArquivo salvo. Gravação terminada')
    os._exit(1)

if __name__ == '__main__':
    choice = ''
    rec = Recorder()
    while choice != '1':
        choice = show_menu()

    print('\nGravação iniciada.')
    start_recording(rec)

    while choice != '2':
        choice = input('\nGravação em andamento, para terminar antes de 1h pressione 2: ')
        stop_recording(rec)
