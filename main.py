import copy
import numpy as np

class Par: # 入力値や各種パラメータを扱うクラス
  # 入力値以外のパラメータ
  trend = -1 # スケジューリングの時の指向


  # ヘッダパラメータの入力受付
  def input_header(self):
    self.M,self.I,self.P,self.R,self.BL = map(int,input().split()[1:])

  # 評価用パラメータの入力受付
  def input_eva(self):
    self.A1,self.A2,self.A3,self.B1,self.B2,self.B3 = map(float,input().split()[1:])


  # MACHINE情報の入力受付
  # [マシン番号, 製造時間係数, 段取り時間係数]でまとめておく
  def input_machine(self):
    self.MACHINE = np.empty((0,3),int)
    c = list(map(int,input().split()[1:]))
    d = list(map(int,input().split()[1:]))
    for i in range(self.M):
      self.MACHINE = np.append(self.MACHINE, np.array([[i+1,c[i],d[i]]]), axis=0)

  # BOMの入力受付
  def input_bom(self):
    self.BOM = np.empty((0,4),int)
    for i in range(self.BL):
      self.BOM = np.append(self.BOM,np.array([list(map(int,input().split()[1:]))]),axis=0)
      
  # ORDERの入力受付
  def input_order(self):
    self.ORDER = np.empty((0,5),int)
    for i in range(self.R):
      self.ORDER = np.append(self.ORDER,np.array([list(map(int,input().split()[1:]))]),axis=0)

  # 傾向の決定
  def trend(self):
    if(self.A2 == max(self.A1,self.A2,self.A3)):
      self.trend = 2
    elif(self.A1 == max(self.A1,self.A3)):
     self.trend = 1
    else:
      self.trend = 3


  # 全ての初期入力を受け付ける
  def __init__(self):
    self.input_header()
    self.input_eva()
    self.input_machine()
    self.input_bom()
    self.input_order()
    self.trend()

#役にたつかもしれない
#def aa(self):
#  print(self.M)

def main(): #メイン関数
  par = Par() # 入力受付
  print(par.trend)


if __name__ == "__main__":
  main()
