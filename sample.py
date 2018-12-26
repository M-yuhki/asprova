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
        # 納期までの時間
        self.lim = d - e
        # このオーダの工数
        self.p = -1
        # このオーダにおける残り工数
        self.prest = -1
        # 既に割り当てた工数分の時間を差し引いた納期
        self.drest = d
        # 順方向割り当て用
        self.erest = e
        # 直前の工程の段取り時間が確定しているか否か
        self.dflg = True

class Bom:
    def __init__(self, i, p, m, t,c,d):
        # 品目番号             : Item number
        self.i = i
        # 工程番号             : Process number
        self.p = p
        # 設備番号             : Machine number
        self.m = m
        # 1個当たりの製造時間  : Manufacturing time per piece
        self.t = t
        # そのBOMに対応するマシンのcとdの値
        self.c = c
        self.d = d
        # cとdを掛け合わせた評価値
        self.cd = c*d

class Operation:
    def __init__(self, m, r, p, t1, t2, t3, i, order):
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
        # 品目番号
        self.i = i
        # オーダそのもの
        self.order = order
        # 依存関係が発生するopeの情報を登録しておく
        # そのマシンの直後のオーダと、自分の次の工程
        self.depend_before = []
        self.depend_after = []

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
        
        # スケジューリングで重視する傾向
        self.Trend = -1
        

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
                c = self.C[m]
                d = self.D[m]
                self.boms.append(Bom(i, p, m, t, c, d))
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
        
        # ORDER毎に工程数を登録しておく
        for i in range(self.R):
            self.orders[i].p = self.iToP[self.orders[i].i] -1
            self.orders[i].prest = self.iToP[self.orders[i].i] -1
        
        self.P = 0;
        for i in range(self.I):
            self.P = max(self.P, self.iToP[i]);
            
        # シミュレーションの際に考慮する傾向
        # 遅延のおよその平均値を10000としておく
        ave_delay = 30000
        AB1 = self.A1*pow(ave_delay,self.B1)
        AB2 = self.A2*pow(ave_delay,self.B2)
        AB3 = self.A3*pow(ave_delay,self.B3)
        
        if(AB2 == max(AB1,AB2,AB3)):
            self.Trend = 2 # 遅延解消傾向
        elif(AB1 == max(AB1,AB3)):
            self.Trend = 1 # 段取り解消傾向
        else:
            self.Trend = 3 # ボーナス最大化傾向

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
    
    def selectMachine(self,i,p,num,ope):
        
        minm0 = -1
        
        minm1 = -1
        minnum1 = 99999999999
        
        minm2 = -1
        minnum2 = 99999999999
        
        minm3 = -1
        minnum3 = 99999999999

        # BOMを順番に見ていく
        for bom in self.boms:
            if (bom.i == i and bom.p == p): # 対応できるBOMである
                
                if(num[bom.m] == 0): # そのマシンにまだ一つのオーダも割り当てられていなものを優先
                    return bom.m
                    
                elif(abs(i - ope[bom.m].i)%3 == 0 and num[bom.m] < minnum1): # 割り当てられている場合、段取り時間が発生せず、なるべく少ないマシンを選択
                    minnum1 = num[bom.m]
                    minm1 = bom.m
                    
                elif(abs(i - ope[bom.m].i)%3 == 1 and  num[bom.m] < minnum2):
                    minnum2 = num[bom.m]
                    minm2 = bom.m
                    
                elif(num[bom.m] < minnum3):
                    minnum3 = num[bom.m]
                    minm3 = bom.m
        
        if(minm1 != -1):
            return minm1
        elif(minm2 != -1):
            return minm2
        else:
            return minm3
    
    def selectOrder(self):
        
        # orderは更新されるのでsortし直す
        self.orders = sorted(self.orders, key=attrgetter('lim'))
        self.orders = sorted(self.orders, key=attrgetter('drest','e', 'r'),reverse = True)
        
        # 現在までに割り当てた工程の開始時間より
        # 後に終わりうるものから選択する
        
        
        for order in self.orders: # orderをsortした順に見ていく
            if(order.prest == -1): # prestが0のオーダは完了済みなので割り付けない
                continue
            
            if(order.dflg): # dflgがTrueのものから優先的に使用
                return order
        
        # dflgが全てFalseならprestが0でない先頭のorderを使用
        for order in self.orders:
            if(order.prest != -1):
                return order
    
    
    def searchOpe(self,r,p):
        
        for operation in self.operations:
            if(operation.r == r and operation.p == p):
                return operation
    

    def solve(self):
        # 各設備の直後の製造開始時刻 : Previous manufacturing end time of each machine
        #mToPreviousT3 = [0 for m in range(self.M)]
        mToPreviousT1 = [0 for m in range(self.M)]
        mToPreviousT3 = [0 for m in range(self.M)]
        # 各設備の直後の品目: Previous item of each machine
        mToPreviousI = [-1 for m in range(self.M)]
        # 各設備の直後のジョブを参照するために登録
        mToPreviousOpe = [-1 for m in range(self.M)]
        # 各注文の各工程の製造終了時刻 : Manufacturing end time of each process of each order
        t3rp = [[-1 for p in range(self.iToP[self.orders[r].i])] for r in range(self.R)]
        # 各設備に割り当てられたオーダの数
        mToNumorder = [0 for m in range(self.M)]
        
        
        # 工程の総数
        ol = 0
        for i in t3rp:
            ol += len(i)

        # 注文を納期が遅い順に並べ替える : Sort orders by earliest start time
        # 納期が遅い→limitが少ないの順
        self.orders = sorted(self.orders, key=attrgetter('lim'))
        self.orders = sorted(self.orders, key=attrgetter('drest','e', 'r'),reverse = True)
        
        # BOMをsortする
        # 段取り時間ペナルティ係数が遅延ペナルティ係数より大きい場合,dを優先的に見る
        """
        if(self.A1 == max(self.A1,self.A2,self.A3)):
            self.boms = sorted(self.boms, key = attrgetter("d","cd","c"))
        # それ以外の場合はcdを優先し、第二項目は平均が大きい項目を考慮
        else:
            if(sum(self.C) >= sum(self.D) ):
                sortkey = "c"
            else:
                sortkey = "d"
            self.boms = sorted(self.boms, key = attrgetter("cd",sortkey))
        """
        # Trendを元にsort
        # 段取りは解消できるからcだけでsortする
        self.boms = sorted(self.boms, key = attrgetter("c","d"))
        
        # オーダを1つずつ処理していくのではなく各工程毎に処理
        while True:
            # selectOrder関数を新たに作成
            #order = self.orders[j]
            
            order = self.selectOrder()
            r = order.r;
            i = order.i;
            e = order.e;
            d = order.d;
            q = order.q;
            p = order.p;
            prest = order.prest;
            drest = order.drest;
            erest = order.erest;
            
            #選ばれた注文の最後の工程から設備と時間を割り付けていく
            # 利用可能な設備を見つける
            m = -1;
            
            # マシンごとに見ていくのではなく、すべてのマシンを総当たりして
            # 望ましいマシンを探す
            """
            # 前から探す場合ここから
            m = self.selectMachine(i,prest,mToNumorder,mToPreviousOpe)
            
            if m == -1:
                continue

            # 段取り開始時刻は、｛この注文の最早開始時刻、この工程の前の工程の製造終了時刻、この設備の前回の製造終了時刻｝の最大値
    	    # Setup start time is max number of { Earliest start time of this order,
         	#                                  	  Manufacturing end time of the operation of previous process,
            #                                     Manufacturing end time of last assigend operation to this machine }
            if(mToPreviousI[m] == -1):
                t1 = order.erest
                t2 = t1
            else:
                t1 = max(erest, t3rp[r][p - 1] if p - 1 >= 0 else 0,  mToPreviousT3[m])
                t2 = t1 + self.D[m] * (abs(i - mToPreviousI[m]) % 3)
            
            t3 = t2 + self.C[m] * self.time(m, i, (p-prest)) * q

            ope = Operation(m, r, (p-prest), t1, t2, t3, i, order)
            self.operations.append(ope)
            
            # 依存関係の登録
            # その品目の次の工程
            if((p - prest) != 0):
                x = self.searchOpe(r,(p - prest - 1))
                x.depend_after.append(ope)
            if(mToPreviousI[m] != -1):
                mToPreviousOpe[m].depend_after.append(ope)

            # NumOrderの更新
            mToNumorder[m] += 1

            
            # 対象としたオーダのdrestとdflgを更新
            order.erest = t3
            order.prest -= 1
            
            # Previous系のパラメータを更新
            mToPreviousT3[m] = t3
            t3rp[r][p] = t3
            mToPreviousI[m] = i
            mToPreviousOpe[m] = ope
            

            # olを更新して、ループから抜ける判定
            
            ol -= 1
            if(ol == 0):
                break
            
            # 前から探す場合ここまで
            
            """
            # 後ろからわりつける場合はここから
            m = self.selectMachine(i,prest,mToNumorder,mToPreviousOpe)
            
            if m == -1:
                continue
            
            if(mToPreviousI[m] == -1): #そのマシンにオーダが割り付けられていない場合
                t3 = order.drest
                dantime = 0
            
            else: # そのマシンにオーダが割り付けられている場合
                #発生しうる段取り時間
                dantime = self.D[m] * (abs(i - mToPreviousI[m])%3)
            
                # 段取り終了時刻は{そのオーダの納期、直後の工程の製造開始時刻+段取り時間}の最小値
                t3 = min(order.drest, mToPreviousT1[m]-dantime)
            
            # t2はt3から実行時間を引いたもの
            t2 = t3 - self.C[m] * self.time(m, i, order.prest) * q
            
            # 段取り開始時刻はあとから計算するためt1=t2
            t1 = t2
            
            # orderを追加
            ope = Operation(m, r, order.prest, t1, t2, t3, i, order)
            self.operations.append(ope)
            
            # 既にそのマシンに工程がわりあてられていたら、そのオーダのパラメータを更新
            if(mToPreviousI[m] != -1):
                mToPreviousOpe[m].t1 -= dantime # t1に段取り時間を追加
                mToPreviousOpe[m].order.drest  -= dantime # drestから段取り時間を引く
                mToPreviousOpe[m].order.dflg = True # dflgをTrueにする
                
                # 依存関係の登録
                # そのマシンの次のオーダ
                ope.depend_after.append(mToPreviousOpe[m])
            
            # 依存関係の登録
            # その品目の次の工程
            if(order.prest != order.p):
                ope.depend_after.append(self.searchOpe(r,order.prest+1))
            
            
            # NumOrderの更新
            mToNumorder[m] += 1

            
            # 対象としたオーダのdrestとdflgを更新
            order.drest = t1
            order.dflg = False
            order.prest -= 1
            
            # Previous系のパラメータを更新
            mToPreviousT1[m] = t1
            mToPreviousI[m] = i
            mToPreviousOpe[m] = ope
            

            # olを更新して、ループから抜ける判定
            
            ol -= 1
            if(ol == 0):
                break
            # 後ろから探す場合ここまで
            
            
        
        #print(checkOrder)
     
        """
            # 各注文の最初の工程から設備と時間を割り付けていく : Assign operation from the first of each order to machine and time
            for p in range(self.iToP[i]):
                # 利用可能な設備を見つける : Find assignable resource
                m = -1;
                for m2 in range(self.M):
                    # マシンを選択
                    # BOMをsortしているので望ましいものから選ばれる
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

                self.operations.append(Operation(m, r, p, t1, t2, t3, i, order))

                mToPreviousI[m] = i
                mToPreviousT3[m] = t3
                t3rp[r][p] = t3
        """
    
    def checkOver(self,ope,pret3):
        if(ope.p == 0): # そのオーダの最初の工程なら最早時間も考慮する
            if(ope.t1 < ope.order.e or ope.t1 < pret3):# 段取り開始時刻が最早時間よりも早い
                over = max(ope.order.e - ope.t1, pret3 - ope.t1)
                ope.t1 += over
                ope.t2 += over
                ope.t3 += over
                for j in ope.depend_after:
                    self.checkOver(j,ope.t3)
        
        else: # 最初の工程でなけれ依存関係のあるt3から判断
            if(ope.t1 < pret3):
                over = pret3 - ope.t1
                ope.t1 += over
                ope.t2 += over
                ope.t3 += over
                for j in ope.depend_after:
                    self.checkOver(j,ope.t3)
        return True
    
    # 隙間を埋めて遅延を解消する関数
    def adjustDelay(self,ope,time):
        # timeは、解消したい遅延時間
        # 早めることができるtimeの時間を更新
        if(ope.p == 0):
            time = min(time, ope.t1 - ope.order.e)
        
        for before in ope.depend_before:
            time = min(time, ope.t1 - before.t3)
        if(time < 0):
            time = 0
        
        """    
        # 最後の工程にたどり着くまで再帰的に呼び出す    
        if(ope.order.p != ope.p):
            for after in ope.depend_after:
                if(after.r == ope.r):
                    time = self.adjustDelay(after,time) # 同じオーダについて再帰的に呼び出す
        """    
        ope.t1 -= time
        ope.t2 -= time
        ope.t3 -= time
        return time 

    # 隙間を埋めて開始を遅らせる関数
    def adjustStart(self,ope,time):
        # timeは、解消したい遅延時間
        # 早めることができるtimeの時間を更新
        if(ope.p == ope.order.p):
            time = min(time, ope.order.d - ope.t3)
        
        for after in ope.depend_after:
            time = min(time, after.t1 - ope.t3)
            
        if(time < 0):
            time = 0
        
        """    
        # 最後の工程にたどり着くまで再帰的に呼び出す    
        if(ope.order.p != ope.p):
            for after in ope.depend_after:
                if(after.r == ope.r):
                    time = self.adjustDelay(after,time) # 同じオーダについて再帰的に呼び出す
        """    
        ope.t1 += time
        ope.t2 += time
        ope.t3 += time
        return time 
            
    
    def checkResult(self): #依存関係を元に時間を調整する
    
        # 各オーダの「これだけ早くできる」を登録
        stend = [-1 for i in range(self.R)]
        
        # 工程順にsort
        # こうすることによって2工程目以降のcheckの必要がなくなる
        self.operations = sorted(self.operations, key= attrgetter("p","r"))
        for ope in self.operations:
            # まずはbefore方向の依存関係を登録しておく
            for j in ope.depend_after:
                j.depend_before.append(ope)
            
            # 実質的な操作はcheckOver関数で対応
            # 最早開始時間に対して頭が出ている場合、下げる
            self.checkOver(ope,0)
        
        # stendを更新する    
        for ope in self.operations:
            if(ope.p == 0):
                stend[ope.r] = ope.t1 - ope.order.e # そのオーダを前に動かせるだけの時間
            if(ope.order.p == ope.p):
                # (ope.t3 - ope.order.d)は、遅延している時間
                # そのためstendの値は"遅延を解消するために動かせる値の限界値"である
                # 負の値を示すなら遅延は発生していない
                stend[ope.r] = min(stend[ope.r],(ope.t3 - ope.order.d))
        
        
        # 工程を前に詰める再構成と、後ろに下げる再構成を繰り返す
        
        
        #while True: #解消できる限り解消を試みる
        for c in range(30):
            # 前に詰める
            maxtime = 0 # そのターンでもっとも短縮できた時間
            self.operations = sorted(self.operations, key = attrgetter("p"),reverse = True)
            
            for ope in self.operations:
                if(ope.p != 0): # 1工程目以外を対象にする
                    time = self.adjustDelay(ope,9999999)
                    if(time > 0):
                        maxtime = max(maxtime,time) 
            
            if(c > 0): # たまに入る
                self.operations = sorted(self.operations, key = attrgetter("p"))
                for ope in self.operations:
                    if(ope.p != ope.order.p): #最終工程以外を対象にする
                        time = self.adjustStart(ope,999999)
                        if(time != 0):
                            maxtime = max(maxtime,time)
            
            if(maxtime == 0): # そのターンで少しも短縮できなければループを出る
                break
            
        
    def writeSolution(self):
        print("{}".format(len(self.operations)))
        
        self.operations = sorted(self.operations, key = attrgetter("r","p"))
        
        
        for operation in self.operations:
            print("{} {} {} {} {} {}".format((operation.m + 1), (operation.r + 1), (operation.p + 1), operation.t1, operation.t2, operation.t3))
        
        """    
        print("****************************************************************")
        
        # 総遅延時間のチェック
        j = 0
        k = 0
        for operation in self.operations:
            if(operation.p == 0):
                j += max(0, operation.t1 - operation.order.e)
            if(operation.order.p == operation.p):
                k += max(0, operation.t3 - operation.order.d)
        print("多い方が良い {}".format(j))
        print("少ない方が良い {}".format(k))
        # 各オーダ内でのエラーチェック
        self.operations = sorted(self.operations, key = attrgetter("r","p"))
        
        for operation in self.operations:
            if(operation.p == 0):
                s = operation.t3
            else:
                if(operation.t1 - s < 0):
                    print("ERROR!")
                s = operation.t3
        
        # 各マシン内でのエラーチェック
        self.operations = sorted(self.operations, key = attrgetter("m","t1"))
        mnow = -1
        for operation in self.operations:
            if(operation.m != mnow):
                mnow = operation.m
                s = operation.t3
            else:
                if(operation.t1 - s < 0):
                    print("ERROR!")
                s = operation.t3
                
        #    print(operation.t1 - s)
        #    s = operation.t3

        
        print("********")
        k = 0
        for operation in self.operations:
            if(operation.p == 0):
                k += max(0, operation.t1 - operation.order.e)
        print(k)
        
        print("********")
        k = 0
        for operation in self.operations:
            if(operation.order.p == operation.p):
                k += max(0, operation.t3 - operation.order.d)
        print(k)
        """

    def run(self):
        self.readProblem()
        self.solve()
        self.checkResult()
        self.writeSolution()

if __name__ == '__main__':
    asprova2 = Asprova2()
    asprova2.run()
