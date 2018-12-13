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
    self.cd = c*d # CとDを双方評価した値
    self.inum = [] # 取り扱える品目番号を加えておく


class Bom(object): # BOM情報を扱うクラス
  def __init__(self,i,p,m,t):
    self.i = i
    self.p = p
    self.m = m
    self.t = t
      
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
  
  # パラメータの受け取り 
  par = Par()

  # マシンの番号と配列の番号は1ずれていることに注意
  machine = [[] for j in range(par.M)]
  c = list(map(int,input().split()[1:]))
  d = list(map(int,input().split()[1:]))
  for j in range(par.M):
    machine[j] = Machine(j+1,c[j],d[j])

  bom = [[] for j in range(par.BL)]
  for j in range(par.BL):
    i,p,m,t = map(int,input().split()[1:])
    bom[j] = Bom(i,p,m,t)

  order = [[] for j in range(par.R)]
  for j in range(par.R):
    r,i,e,d,p = list(map(int,input().split()[1:]))
    order[j] = Order(r,i,e,d,p)

  # マシンごとに取り扱える品目を登録
  for j in bom:
    machine[j.m-1].inum.append(j.i)

  # 品目ごとに工程の数を登録
  # 品目の番号と配列の番号は1ずれていることに注意
  step = [-1 for j in range(par.I)]
  for j in bom:
    if(step[j.i - 1] < j.p):
      step[j.i - 1] = j.p

  #machineをcd値順にsort
  for j in machine:
    print(vars(j))
  machine.sort(key = lambda x:x.cd)
  for j in machine:
    print(vars(j))


if __name__ == "__main__":
  main()
