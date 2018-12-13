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


class Bom(object): # BOM情報を扱うクラス
  def __init__(self,i,p,m,t):
    self.i = i
    self.p = p
    self.m = m
    self.t = t
      
class Order(object): # ORDER情報を扱うクラス
  def __init__(self,r,i,e,d,q):
    self.r = r
    self.i = i
    self.e = e
    self.d = d
    self.q = q

# 品目ごとの情報を扱うクラス
# 他の情報で補えるのだが参照しやすいように
class Item(object):
  def __init__(self,i,p,mlist):
    self.i = i
    self.p = p # その品目の工程数
    self.mlist = mlist # その品目を扱うことができるマシン番号
    self.gid = i%3 # グループid:これが同じだと工程依存が発生しない

#役にたつかもしれない
#def aa(self):
#  print(self.M)

def main(): #メイン関数
  
  # パラメータの受け取り 
  par = Par()

  # マシンの番号と配列の番号は1ずれていることに注意
  machine = []
  c = list(map(int,input().split()[1:]))
  d = list(map(int,input().split()[1:]))
  for j in range(par.M):
    machine.append( Machine(j+1,c[j],d[j]) )

  #machineをcd値順にsortしておく
  #のぞまいしマシンから優先的に探索しやすくなる
  machine.sort(key = lambda x:x.cd)
  
  bom = []
  for j in range(par.BL):
    i,p,m,t = map(int,input().split()[1:])
    bom.append(Bom(i,p,m,t))

  order = []
  for j in range(par.R):
    r,i,e,d,q = list(map(int,input().split()[1:]))
    order.append( Order(r,i,e,d,q) )

  #orderを納期が遅い順にsort
  order.sort(key = lambda x:-x.d)
  
  # 入力値を整形して品目ごとにアクセスしやすくする
  item = []
  item_p = [-1 for i in range(par.I)]
  item_machine = [[] for i in range(par.I)]
  for j in bom:
    item_machine[j.i-1].append(j.m) # 対応するマシンの登録
    if(j.p > item_p[j.i-1]): # マシンの工程数を更新
      item_p[j.i-1] = j.p

  for j in range(par.I):
    item.append( Item(j+1,item_p[j],item_machine[j]) )
  
  # 動作確認用のprint
  print("machine")
  for j in machine:
    print(vars(j))
  print("bom")
  for j in bom:
    print(vars(j))
  print("order")
  for j in order:
    print(vars(j))
  print("item")
  for j in item:
    print(vars(j))

if __name__ == "__main__":
  main()
