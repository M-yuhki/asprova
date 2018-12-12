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

#入力の受付
M,I,P,R,BL = map(int,input().split()[1:])
A1,A2,A3,B1,B2,B3 = map(float,input().split()[1:])
MACHINE = np.array(np.array([]) for i in range(M))
print(MACHINE)
c = list(map(int,input().split()[1:]))
d = list(map(int,input().split()[1:]))
for i in range(M):
  np.array([MACHINE,[i+1,c[i],d[i]]])
BOM=np.array([])
for i in range(BL):
  np.append(BOM,list(map(int,input().split()[1:])))
ORDER=np.array([])
for i in range(R):
  np.append(ORDER,list(map(int,input().split()[1:])))

tar = 2 #スケジューリングの際に重視する指向
#まずは納期指向
"""
if(A2 == max(A1,A2,A3)):
  tar = 2 #納期を優先する
elif(A1 == max(A1,A2,A3)):
  tar = 1 #段取りを優先する
else:
  tar = 3 #着手遅延を優先する
"""

#MACHINEを並び替え
#製造時間係数が小さい→段取り時間係数が短い
#MACHINE.sort(key = lambda x:(x[1],x[2]))
print(MACHINE)

#ORDERを並び替え
#最早開始時刻が遅い→納期が遅い
#np.argsort(ORDER,axis=2)
#np.argsort(ORDER,axis=3)

#print(ORDER)

#一番遅い納期

