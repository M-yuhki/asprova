#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
import sys
import fileinput
import operator
from operator import itemgetter, attrgetter

class Order:
    def __init__(self, r, i, e, d, q):
        # オーダ番号    : Order number
        self.r=r
        # 品目番号      : Item number
        self.i=i
        # 最早開始時刻  : Earliest start time
        self.e=e
        # 納期          : Deadline
        self.d=d
        # 製造数量      : Manufacturing quanity
        self.q=q

class Bom:
    def __init__(self, i, p, m, t):
        # 品目番号             : Item number
        self.i = i
        # 工程番号             : Process number
        self.p = p
        # 設備番号             : Machine number
        self.m = m
        # 1個当たりの製造時間  : Manufacturing time per piece
        self.t = t

class Operation:
    def __init__(self, m, r, p, t1, t2, t3):
        # 設備番号           : Machine number
        self.m = m
        # オーダ番号         : Order number
        self.r = r
        # 工程番号           : Process number
        self.p = p
        # 段取り開始時刻     : Setup start time
        self.t1 = t1
        # 製造開始時刻       : Manufacturing start time
        self.t2 = t2
        # 製造終了時刻      : Manufacturing end time
        self.t3 = t3

class Asprova2:
    def __init__(self):
        # 設備数                   : Number of machines
        self.M=0
        # 品目数                   : Number of items
        self.I=0
        # 最大工程数               : Max number of processes
        self.P=0
        # 注文数                   : Number of Processes
        self.R=0
        # BOM行数                  : Number of BOM line
        self.BL=0
        # 段取り時間ペナルティ係数 : Setup time penalty
        self.A1=0
        # 納期遅れペナルティ係数   : Missed deadline penalty
        self.A2=0
        # 着手遅延ポイント係数     : Assignment lateness bonus
        self.A3=0
        # 段取り時間べき乗数       : Setup time exponent
        self.B1=0
        # 納期遅れべき乗数         : Missed deadline exponent
        self.B2=0
        # 着手遅延べき乗数         : Late assignment exponent
        self.B3=0
        # 設備mの製造時間係数   : Machine manufacturing time multiplier
        self.C=[]
        # 設備mの段取り時間係数 : Machine setup time multiplier
        self.D=[]
        self.boms = []
        self.orders = []
        self.operations = []

    def readProblem(self):
        n = 0
        for line in fileinput.input():
            split = line.strip().split()
            if n == 0:
                self.M = int(split[1])
                self.I = int(split[2])
                self.P = int(split[3])
                self.R = int(split[4])
                self.BL = int(split[5])
            elif n == 1:
                self.A1 = float(split[1])
                self.A2 = float(split[2])
                self.A3 = float(split[3])
                self.B1 = float(split[4])
                self.B2 = float(split[5])
                self.B3 = float(split[6])
            elif n == 2:
                self.C = [int(split[1+m]) for m in range(self.M)]
            elif n == 3:
                self.D = [int(split[1+m]) for m in range(self.M)]
            elif split[0] == "BOM":
                i = int(split[1]) - 1
                p = int(split[2]) - 1
                m = int(split[3]) - 1
                t = int(split[4])
                self.boms.append(Bom(i, p, m, t))
            elif split[0] == "ORDER":
                r = int(split[1]) - 1
                i = int(split[2]) - 1
                e = int(split[3])
                d = int(split[4])
                q = int(split[5])
                self.orders.append(Order(r, i, e, d, q))

            n = n + 1

        # 各品目の工程数 : Number of processes by each item
        self.iToP = [0 for i in range(self.I)]
        for bom in self.boms:
            self.iToP[bom.i] = max(self.iToP[bom.i], bom.p + 1)

        self.P = 0;
        for i in range(self.I):
            self.P = max(self.P, self.iToP[i]);

    def time(self, m, i, p):
        for bom in self.boms:
            if bom.i == i and bom.p == p and bom.m == m:
                return bom.t
        return -1

    def canMake(self, m, i, p):
        for bom in self.boms:
            if bom.i == i and bom.p == p and bom.m == m:
                return True
        return False

    def solve(self):
        # 各設備の前回の製造終了時刻 : Previous manufacturing end time of each machine
        mToPreviousT3 = [0 for m in range(self.M)]
        # 各設備の前回の品目 : Previous item of each machine
        mToPreviousI = [-1 for m in range(self.M)]
        # 各注文の各工程の製造終了時刻 : Manufacturing end time of each process of each order 
        t3rp = [[-1 for p in range(self.iToP[self.orders[r].i])] for r in range(self.R)]

        # 注文を最早開始時刻が早い順に並べ替える : Sort orders by earliest start time
        self.orders = sorted(self.orders, key=attrgetter('e', 'r'))

        for j in range(self.R):
            order = self.orders[j]
            r = order.r;
            i = order.i;
            e = order.e;
            d = order.d;
            q = order.q;
            # 各注文の最初の工程から設備と時間を割り付けていく : Assign operation from the first of each order to machine and time
            for p in range(self.iToP[i]):
                # 利用可能な設備を見つける : Find assignable resource
                m = -1;
                for m2 in range(self.M):
                    if self.canMake(m2, i, p):
                        m = m2
                        break
                if m == -1:
                    continue

                # 段取り開始時刻は、｛この注文の最早開始時刻、この工程の前の工程の製造終了時刻、この設備の前回の製造終了時刻｝の最大値
    	        # Setup start time is max number of { Earliest start time of this order, 
          	    #                                  	  Manufacturing end time of the operation of previous process, 
            	#                                     Manufacturing end time of last assigend operation to this machine }
                t1 = max(e, t3rp[r][p - 1] if p - 1 >= 0 else 0, mToPreviousT3[m])
                t2 = t1
                if mToPreviousI[m] != -1:
                    # この設備を使うのが２回目以降なら、段取り時間を足す。 : Add setup time if this operation is not the first operation assigned to this machine. 
                    t2 += self.D[m] * (abs(i - mToPreviousI[m]) % 3)
                t3 = t2 + self.C[m] * self.time(m, i, p) * q

                self.operations.append(Operation(m, r, p, t1, t2, t3))

                mToPreviousI[m] = i
                mToPreviousT3[m] = t3
                t3rp[r][p] = t3

    def writeSolution(self):
        print("{}".format(len(self.operations)))
        for operation in self.operations:
            print("{} {} {} {} {} {}".format((operation.m + 1), (operation.r + 1), (operation.p + 1), operation.t1, operation.t2, operation.t3))

    def run(self):
        self.readProblem()
        self.solve()
        self.writeSolution()

if __name__ == '__main__':
    asprova2 = Asprova2()
    asprova2.run()
