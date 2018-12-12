#input
#HEADER M I P R BL
#EVALUATIONFACTOR A A A B B B
#PRODUCTIONFACTOR C C … C
#SETUPFACTOR D D … D
#BOM i p m t
#:
#ORDER r i e d q

import copy
import numpy as np
#main
class Par: #変数を扱ったりするクラス
  M = -1 #設備数(1..20,整数)
  I = -1 #品目数(1..20,整数)
  P = -1 #最大工程数(1..5,整数)
  R = -1 #オーダ数(1..200,整数)
  BL = -1 #BOM行数(1,2..,整数)
  A1 = -1.0 #段取り時間ペナルティ係数(0≤A1≤100,実数)
  A2 = -1.0 #納期遅れペナルティ係数(0≤A2≤100,実数)
  A3 = -1.0 #着手遅延ポイント係数(0≤A3≤100,実数)
  B1 = -1.0 #段取り時間べき乗数(0<B1≤2,実数)
  B2 = -1.0 #納期遅れべき乗数(0<B2≤2,実数)
  B3 = -1.0 #着手遅延べき乗数(0<B3≤2,実数)

  def input_header(self):
    self.M,self.I,self.P,self.R,self.BL = map(int,input().split()[1:])

  def input_eva(self):
    self.A1,self.A2,self.A3,self.B1,self.B2,self.B3 = map(float,input().split()[1:])

  def input_machine(self):
    self.MACHINE = np.empty((0,3),int)
    c = list(map(int,input().split()[1:]))
    d = list(map(int,input().split()[1:]))
    for i in range(self.M):
      self.MACHINE = np.append(self.MACHINE, np.array([[i+1,c[i],d[i]]]), axis=0)

  def input_bom(self):
    self.BOM = np.empty((0,4),int)
    for i in range(self.BL):
      self.BOM = np.append(self.BOM,np.array([list(map(int,input().split()[1:]))]),axis=0)
      
  def input_order(self):
    self.ORDER = np.empty((0,5),int)
    for i in range(self.R):
      self.ORDER = np.append(self.ORDER,np.array([list(map(int,input().split()[1:]))]),axis=0)

  def __init__(self):
    self.input_header()
    self.input_eva()
    self.input_machine()
    self.input_bom()
    self.input_order()


p = Par()

print(p.M)
print(p.MACHINE)
print(p.BOM)
print(p.BOM[2,2:])
