
# -*- coding: utf-8 -*-

import numpy as np
from numpy import inf
import pandas as pd
from threading import Thread, Timer
import os
import time
import pandas as pd
import threading
from pynput import mouse
import winsound

os.system('python movements.py')

def generate_features(mouse_raw):
  
  horiz_spd = mouse_raw['x'].diff()/mouse_raw['client timestamp'].diff()
  vert_spd = mouse_raw['y'].diff()/mouse_raw['client timestamp'].diff()
  tang_spd = np.sqrt((horiz_spd**2)+(vert_spd**2))
  horiz_spd_ag_dist = (mouse_raw['x'] - mouse_raw['x'][0])/(mouse_raw['client timestamp']-mouse_raw['client timestamp'][0])
  vert_spd_ag_dist = (mouse_raw['y'] - mouse_raw['y'][0])/(mouse_raw['client timestamp']-mouse_raw['client timestamp'][0])
  avrge_spd_ag_dist = np.sqrt((mouse_raw['x'].diff()**2)+(mouse_raw['y'].diff()**2)).sum()/(mouse_raw['client timestamp']-mouse_raw['client timestamp'][0])
 
  return {'horiz_spd':horiz_spd, 'vert_spd':vert_spd, 'tang_spd':tang_spd,'horiz_spd_ag_dist':horiz_spd_ag_dist, 'vert_spd_ag_dist':vert_spd_ag_dist, 'avrge_spd_ag_dist':avrge_spd_ag_dist}
        
def generate_features_2(mouse_raw, mouse_raw_1):  
  
  horiz_acc = mouse_raw_1['horiz_spd'].diff()/mouse_raw['client timestamp'].diff()
  vert_acc = mouse_raw_1['vert_spd'].diff()/mouse_raw['client timestamp'].diff()
  tang_acc = np.sqrt((horiz_acc**2)+(vert_acc**2))
  horiz_acc_ag_dist = (mouse_raw_1['horiz_spd_ag_dist'] - mouse_raw_1['horiz_spd_ag_dist'][0])/(mouse_raw['client timestamp']-mouse_raw['client timestamp'][0])
  vert_acc_ag_dist= (mouse_raw_1['vert_spd_ag_dist'] - mouse_raw_1['vert_spd_ag_dist'][0])/(mouse_raw['client timestamp']-mouse_raw['client timestamp'][0])
  avrge_acc_ag_dist = (mouse_raw_1['avrge_spd_ag_dist'] - mouse_raw_1['avrge_spd_ag_dist'][0])/(mouse_raw['client timestamp']-mouse_raw['client timestamp'][0])
 
  return {'horiz_acc':horiz_acc, 'vert_acc':vert_acc, 'tang_acc':tang_acc, 'horiz_acc_ag_dist':horiz_acc_ag_dist, 'vert_acc_ag_dist':vert_acc_ag_dist, 'avrge_acc_ag_dist':avrge_acc_ag_dist}

def features_mouse(mouse_training):

  mouse_train_1 = pd.DataFrame(generate_features(mouse_training)).fillna(0)

  mouse_train_1[mouse_train_1 == inf] = 0
  mouse_train_1[mouse_train_1 == -inf] = 0

  mouse_train_2 = pd.DataFrame(generate_features_2(mouse_training, mouse_train_1)).fillna(0)
  mouse_train_2[mouse_train_2 == inf] = 0
  mouse_train_2[mouse_train_2 == -inf] = 0

  mouse_train_feat = pd.concat([mouse_train_1,mouse_train_2],axis=1)

  return mouse_train_feat

mouse_train = pd.read_csv('mouse_data.csv')
mouse_train_features = features_mouse(mouse_train)
mouse_train_features.to_csv('mouse_features.csv')

os.system('cls')

from sklearn import svm

svmclassifier = svm.OneClassSVM(nu=0.07, kernel="linear")
svmclassifier.fit(mouse_train_features)

import pickle

s = pickle.dumps(svmclassifier)

print("Iniciar Autenticação!")
confidence = float(input("Indique o grau de confiança alvo entre 0.00(mínimo) e 100.00(máximo) e aperte Enter: "))
if confidence == ' ':
  confidence = '70'

class Recorder():

  def __init__(self):
    self.max_time = 600 #segundos (10 min)
    self.df = pd.DataFrame(columns=['client timestamp', 'button', 'state', 'x', 'y'])
    self.check_drag = False
    self.last_move = None
    self.info = pd.DataFrame()

  def start(self):
    self.time0 = time.time()
    self.mouse_listener = mouse.Listener(on_move=self.on_move, on_click=self.on_click, on_scroll=self.on_scroll)
    self.mouse_listener.start()

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


  def register_action(self, x, y, button, state):
    self.df = self.df.append({
              'client timestamp': time.time() - self.time0, 
              'button': button, 
              'state': state, 
              'x': int(x), 
              'y': int(y)
          }, ignore_index=True)
    self.df['client timestamp'] = self.df['client timestamp'] - self.df['client timestamp'][0]
    self.df.to_csv('mouse_data_intruder.csv', index=False)
    global info
    info = pd.read_csv('mouse_data_intruder.csv')

  def stop(self):
      self.mouse_listener.stop()

def autenticador():

  svmclassifier = pickle.loads(s)
  
  def obter_dados_autenticar():

    def show_menu():
    
      return '1'

    def stop_recording(recorder):
      recorder.stop()
      os._exit(1)

    def start_recording(recorder):
      recorder.start()
      t = threading.Timer(600, stop_recording, [recorder])
      t.daemon = True
      t.start()

    if __name__ == '__main__':
      choice = '1'
      rec = Recorder()
      while choice != '1':
        choice = show_menu()

      start_recording(rec)

      while choice != '2':
        choice = input('\nPara terminar antes pressione 2:')
        stop_recording(rec)

  def autenticar():
    time.sleep(5)
    t = Timer(600, autenticar)
    t.daemon = True
    t.start()
    ciclo = 1

    while True:
    
      mouse_intruder = info.copy()
      mouse_intruder_feat = features_mouse(mouse_intruder)
      mouse_intruder_feat.to_csv('mouse_features.csv')
      
      y_pred_intruder = svmclassifier.predict(mouse_intruder_feat)
      #print(y_pred_intruder)
      n_error_intruder = y_pred_intruder[y_pred_intruder == -1].size
      confianca = 100 - n_error_intruder/y_pred_intruder.size*100

      print('Índice de Confiaça: {0:.2f}%'.format(confianca))

      if ciclo <= 3:
        print('analisando perfil de movimentação do mouse')
        ciclo += 1
      else:
        if confianca <= confidence:
          print('Intruso! Intruso!')
          winsound.PlaySound('Red Alert.wav', winsound.SND_FILENAME)
        else:
          print('Usunário Autenticado!')
      time.sleep(5)

  if __name__ == '__main__':
    Thread(target = obter_dados_autenticar).start()
    Thread(target = autenticar).start()   

auth = autenticador()
