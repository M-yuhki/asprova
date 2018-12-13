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

  def __init__(self):
    self.input_header()
    self.input_eva()


class Machine(object): # マシン情報を扱うクラス
  def __init__(self,num,c,d):
    self.num = num
    self.c = c
    self.d = d


class Bom(object): # BOM情報を扱うクラス
  def __init__(self,i,p,m,t):
    self.i = i
    self.p = p
    self.m = m
    self.t = t
      
  # ORDERの入力受付
class Order(object): # ORDER情報を扱うクラス
  def __init__(self,r,i,e,d,p):
    self.r = r
    self.i = i
    self.e = e
    self.d = d
    self.p = p

#役にたつかもしれない
#def aa(self):
#  print(self.M)

def main(): #メイン関数
  par = Par() # 入力受付

  
  machine = [[] for i in range(par.M)]
  c = list(map(int,input().split()[1:]))
  d = list(map(int,input().split()[1:]))
  for i in range(par.M):
    machine[i] = Machine(i+1,c[i],d[i])

  bom = [[] for i in range(par.BL)]
  for j in range(par.BL):
    i,p,m,t = map(int,input().split()[1:])
    bom[j] = Bom(i,p,m,t)

  order = [[] for i in range(par.R)]
  for j in range(par.R):
    r,i,e,d,p = list(map(int,input().split()[1:]))
    order[j] = Order(r,i,e,d,p)

if __name__ == "__main__":
  main()
