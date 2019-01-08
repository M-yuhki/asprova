#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 初マラソン楽しかったです、ありがとうございました

import sys
import fileinput
import statistics
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
        # 遅延している時間
        self.delay = -1
        
        # 対応するマシンを入れておく配列
        self.machine_list = []
        
        # 対象となる工程を取り扱えるマシンの数
        self.machine_num = -1

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
        # 該当するマシンで取り扱えるBOMの数
        self.mworth = -1

class Operation:
    def __init__(self, m, r, p, t1, t2, t3, i, order, c,d,mworth):
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
        # 製造時間
        self.run = t3 - t2
        # 段取り時間
        self.dan = t2 - t1
        
        # 品目番号
        self.i = i
        # オーダそのもの
        self.order = order
        # 依存関係が発生するopeの情報を登録しておく
        self.machine_before = None
        self.machine_after = None
        self.order_before = None
        self.order_after = None
        
        # backfillがその回で適用されたかの判定
        self.backflg = False
        self.forwardflg = False
        
        # 使用したマシンの価値
        self.mworth = mworth
        
        # 使用したマシンのcとd
        self.c = c
        self.d = d

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
        
        self.AB1 = 0
        self.AB2 = 0
        self.AB3 = 0
        
        self.bunsan_c = 0
        self.bunsan_d = 0
        
        self.ave_c = 0
        self.ave_d = 0
        
        self.ave_q = 0

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

        iPtoMachine = []
        # 品目iの工程pに対応するマシンを登録するリストを作る
        for i in range(self.I):
            iPtoMachine.append([ [] for j in range(self.iToP[i]) ])
        
        for bom in self.boms:
            iPtoMachine[bom.i][bom.p].append(bom.m)
        
        for order in self.orders:
            order.machine_list = iPtoMachine[order.i]
            order.machine_num = len(order.machine_list[order.p])
        self.P = 0;
        for i in range(self.I):
            self.P = max(self.P, self.iToP[i]);
        
        # マシンごとに対応するBOMの数    
        self.mnum = [0 for i in range(self.M)]
        for bom in self.boms:
            self.mnum[bom.m] += 1
        
        for bom in self.boms:
            bom.mworth = self.mnum[bom.m]
            
        # マシンごとの利用時刻
        self.machinetime = [-1 for i in range(self.M)]
            
        # シミュレーションの際に考慮する傾向
        # 遅延のおよその平均値を10000としておく
        ave_delay = 30000
        self.AB1 = self.A1*pow(ave_delay,self.B1)
        self.AB2 = self.A2*pow(ave_delay,self.B2)
        self.AB3 = self.A3*pow(ave_delay,self.B3)
        
        if(self.AB2 == max(self.AB1,self.AB2,self.AB3)):
            self.Trend = 2 # 遅延解消傾向
        elif(self.AB1 == max(self.AB1,self.AB3)):
            self.Trend = 1 # 段取り解消傾向
        else:
            self.Trend = 3 # ボーナス最大化傾向
            
        # cとdの分散を計算
        self.ave_c = int(sum(self.C)/self.M)
        
        total_c = 0
        for c in self.C:
            total_c += (c - self.ave_c)*(c - self.ave_c)
        self.bunsan_c = int(total_c/self.M)
        
        # cとdの分散を計算
        self.ave_d = int(sum(self.D)/self.M)
        
        total_d = 0
        for d in self.D:
            total_d += (d - self.ave_d)*(d - self.ave_d)
        self.bunsan_d = int(total_d/self.M)
        
        # 各オーダの製造個数の平均値
        total_q = 0
        for order in self.orders:
            total_q += order.q
        self.ave_q = int(total_q/self.R)
        

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
    
    def selectMachine(self,i,p,num,before,ope):
        
        maxm0 = -1
        maxtime0 = -99999999999
        maxtime1 = -99999999999
        maxtime2 = -99999999999
        maxtime3 = -99999999999
        
        minm1 = -1
        minnum1 = 99999999999
        
        minm2 = -1
        minnum2 = 99999999999
        
        minm3 = -1
        minnum3 = 99999999999
        
        # bomをsortする
        # 製造個数が多ければCが小さめ、製造個数が少なければCが大きめのマシンを選びやすくする
        self.boms = sorted(self.boms, key = attrgetter("mworth"))
        
        if(ope.q > self.ave_q): # 要求数が多め
            self.boms = sorted(self.boms, key = attrgetter("c"))
        
        else: # 少なめ
            self.boms = sorted(self.boms, key = attrgetter("c"),reverse = True)
        
        esp_d2 = pow(self.ave_d * 2,self.B1) * self.A1
        esp_d1 = pow(self.ave_d,self.B1) * self.A1
        esp_c = pow(self.ave_c * self.ave_q,self.B2) * self.A2

        # BOMを順番に見ていく
        for bom in self.boms:
            if (bom.i == i and bom.p == p): # 対応できるBOMである
                
                
                if(num[bom.m] == 0): # そのマシンにまだ一つのオーダも割り当てられていなものを優先
                    return bom.m
                 
                # 発生しうる段取り時間が予測されるrun時間に比べて大きい
                # 段取り時間は極力発生させない
                if(esp_d1 > esp_c): 
                    if((abs(i - before[bom.m].i)%3 == 0 or bom.d == 0) and maxtime1 < self.machinetime[bom.m]): # 割り当てられている場合、段取り時間が発生せず、なるべく少ないマシンを選択
                        maxtime1 = self.machinetime[bom.m]
                        minm1 = bom.m
                    
                    elif(abs(i - before[bom.m].i)%3 == 1 and maxtime2 < self.machinetime[bom.m]):
                        maxtime2 = self.machinetime[bom.m]
                        minm2 = bom.m
                    
                    elif(maxtime3 < self.machinetime[bom.m]):
                        maxtime3 = self.machinetime[bom.m]
                        minm3 = bom.m
        
                # 2段階の発生は抑えたい
                elif(esp_d2 > esp_c):
                    if((abs(i - before[bom.m].i)%3 != 2 or bom.d == 0) and maxtime1 < self.machinetime[bom.m]): # 割り当てられている場合、段取り時間が発生せず、なるべく少ないマシンを選択
                        maxtime1 = self.machinetime[bom.m]
                        minm1 = bom.m
                    
                    elif(maxtime2 < self.machinetime[bom.m]):
                        maxtime2 = self.machinetime[bom.m]
                        minm2 = bom.m
                
                # 2段階とも発生してOK
                else:
                    if(maxtime1 < self.machinetime[bom.m]): # 割り当てられている場合、段取り時間が発生せず、なるべく少ないマシンを選択
                        maxtime1 = self.machinetime[bom.m]
                        minm1 = bom.m
                    
                
        if(minm1 != -1):
            return minm1
        elif(minm2 != -1):
            return minm2
        else:
            return minm3
    
    def selectOrder(self):
        
        # orderは更新されるのでsortし直す

        self.orders = sorted(self.orders, key=attrgetter('prest','drest','d'),reverse = True)
        
        best_order = None
        
        for order in self.orders: # orderをsortした順に見ていく
            if(order.prest == -1): # prestが0のオーダは完了済みなので割り付けない
                continue
            
            if(order.dflg): # dflgがTrueのものから優先的に使用
             
                
                if(best_order == None):
                    best_order = order
                    
                elif(order.prest > best_order.prest):
                    best_order = order

                elif(order.drest > best_order.drest):
                    best_order = order

                    
        
        # dflgが全てFalseならprestが0でない先頭のorderを使用
        if(best_order == None):
            for order in self.orders:
                if(order.prest != -1):
                    if(best_order == None):
                        best_order = order
                        
                    elif(order.prest > best_order.prest):
                        best_order = order
                        
                    elif(order.drest > best_order.drest):
                        best_order = order

        return best_order
    
    
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
        self.orders = sorted(self.orders, key=attrgetter('e'))
        self.orders = sorted(self.orders, key=attrgetter('drest','e', 'r'),reverse = True)
        
        #self.boms = sorted(self.boms, key = attrgetter("c","d"))
        self.boms = sorted(self.boms, key = attrgetter("mworth"))
        
        
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

            m = self.selectMachine(i,prest,mToNumorder,mToPreviousOpe,order)

            
            if (m == -1):
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
            ope = Operation(m, r, order.prest, t1, t2, t3, i, order,self.C[m],self.D[m], self.mnum[m])
            self.operations.append(ope)
            
            # 既にそのマシンに工程がわりあてられていたら、そのオーダのパラメータを更新
            if(mToPreviousI[m] != -1):
                mToPreviousOpe[m].t1 -= dantime # t1に段取り時間を追加
                mToPreviousOpe[m].order.drest  -= dantime # drestから段取り時間を引く

                mToPreviousOpe[m].dan = dantime
                mToPreviousOpe[m].order.dflg = True # dflgをTrueにする
                
                # 依存関係の登録
                # そのマシンの次のオーダ
                ope.machine_after = mToPreviousOpe[m]
                mToPreviousOpe[m].machine_before = ope
            
            # 依存関係の登録
            # その品目の次の工程
            if(order.prest != order.p):
                tar = self.searchOpe(r,order.prest+1)
                ope.order_after = tar
                tar.order_before = ope
            
            
            # NumOrderとmachineTImeの更新
            mToNumorder[m] += 1
            self.machinetime[m] = t1
            

            
            # 対象としたオーダのdrestとdflgを更新
            order.drest = t1
            order.lim = drest - e
            order.prest -= 1
            if(order.prest >= 0):
                order.machine_num = len(order.machine_list[prest])
            
            
            order.dflg = False
            
            
            # Previous系のパラメータを更新
            mToPreviousT1[m] = t1
            mToPreviousI[m] = i
            mToPreviousOpe[m] = ope
            

            # olを更新して、ループから抜ける判定
            
            ol -= 1
            if(ol == 0):
                break
            # 後ろから探す場合ここまで

    
    def checkOver(self,ope,pret3):
        if(ope.p == 0): # そのオーダの最初の工程なら最早時間も考慮する
            if(ope.t1 < ope.order.e or ope.t1 < pret3):# 段取り開始時刻が最早時間よりも早い
                over = max(ope.order.e - ope.t1, pret3 - ope.t1)
                ope.t1 += over
                ope.t2 += over
                ope.t3 += over
                if(ope.machine_after != None):
                    self.checkOver(ope.machine_after,ope.t3)
                if(ope.order_after != None):
                    self.checkOver(ope.order_after,ope.t3)
        
        else: # 最初の工程でなけれ依存関係のある工程のt3から判断
            if(ope.t1 < pret3):
                over = pret3 - ope.t1
                ope.t1 += over
                ope.t2 += over
                ope.t3 += over
                if(ope.machine_after != None):
                    self.checkOver(ope.machine_after,ope.t3)
                if(ope.order_after != None):
                    self.checkOver(ope.order_after,ope.t3)
                
        return True
 
    # 隙間を埋めて遅延を解消する関数
    def adjustDelay(self,ope,time):

        # 確認用の表示
        # timeは、解消したい遅延時間
        # 早めることができるtimeの時間を更新
        if(ope.p == 0):
            
            if(self.A3 >= self.A2*1.1 and self.B3 >= self.B2):
            #time = 0
                time = 0
            else:
                time = min(time, ope.t1 - ope.order.e)
            
        if(ope.machine_before != None):
            time = min(time, ope.t1 - ope.machine_before.t3)
        if(ope.order_before != None):
            time = min(time, ope.t1 - ope.order_before.t3)
        
        if(time <= 0):
            time = 0

        ope.t1 -= time
        ope.t2 -= time
        ope.t3 -= time
            
        return time

    # 隙間を埋めて開始を遅らせる関数
    def adjustStart(self,ope,time):
        # timeは、遅らせることができる時間
        # 早めることができるtimeの時間を更新
        if(ope.p == ope.order.p):
        #if(ope.p != 0):
            time = min(time, ope.order.d - ope.t3)
            #time = 0
        
        if(ope.machine_after != None):
            time = min(time, ope.machine_after.t1 - ope.t3)
        if(ope.order_after != None):
            time = min(time, ope.order_after.t1 - ope.t3)
            
        if(time < 0):
            time = 0
        
        #適当な確率で埋めない
        ope.t1 += time
        ope.t2 += time
        ope.t3 += time

            
        return time 

    # backfillで間を埋める関数
    def backfill(self):    
        
        self.operations = sorted(self.operations, key = attrgetter("t1","c"))
        self.operations = sorted(self.operations, key = attrgetter("mworth","m"),reverse = True)
        
        # フラグの初期化
        for ope in self.operations:
            ope.backflg = False
        
        before_t3 = -1 # 直前の工程の完了時間
        now_m = -1 # 現在のマシンの番号
        mfound = False # そのマシンで一度でも見つかったか
        # backfillないの判定を容易にするためにjでループ回す
        # 一番最後のオーダはspaceが発生することはないので無視
        for j in range(len(self.operations)): # backfill内部の処理をしやすくするためにjでループ回す
            ope = self.operations[j]
            # 別のマシン部分に入るor最初の処理
            # パラメータをリセット
            if(ope.m != now_m or before_t3 == -1):
                now_m = ope.m
                mfound = False
                before_t3 = ope.t3
                before_i = ope.i
            
            
            elif(not(mfound)):
                space = ope.t1 - before_t3 # 現在の工程と一つ前の工程の間の時間
                p = j #これから見るジョブのindex

                bestfit = None # もっとも好条件なものを選ぶ
                
                while(space > 0): # スペースがある程度あるならbackfillを試みる
                    p += 1 # continueの影響を受けないように冒頭でインクリメント
                    
                    if(p >= len(self.operations)): # 最終マシン用の終了判定
                        break
                    
                    #ターゲットとなるオーダの情報を登録
                    
                    tar_b = self.operations[p-1] # ターゲットの1つ前のオーダ
                    tar = self.operations[p] # ターゲットのオーダ
                    
                
                    # ターゲットの1つ次のオーダ
                    # 各マシンの最後のオーダの場合はそれ自身を登録しておく
                    # tar_aは段取り時間の影響をみるだけなのでtar_a=tarでも問題ない
                    
                    if(p >= len(self.operations) - 1):
                        tar_a = tar
                    elif(self.operations[p+1].m != now_m):
                        tar_a = tar
                    else:
                        tar_a = self.operations[p+1]
                    
                    
                    if(tar.m != now_m): # 別のマシン部分まで到達したら終了
                        break
                    
                    
                    if( abs(tar.i - tar_b.i)%3 != 0 or abs(tar_a.i - tar.i)%3 != 0):
                    #if(not(tar_b.i == tar.i == tar_a.i)): #段取り時間に変更が出る場合は（面倒なので）スルー
                        continue
                    
                    if(tar.backflg or tar_a.backflg): #一度backfillされている場合もスルー
                        continue
                    # 各オーダの最初の工程の場合
                    # 1工程目は、その品目の工程数が3以上であれば対象外とする
                    if(tar.p == 0 and tar.order.p >= 3):
                        continue
                        
                    # 間を埋める条件は基本的には"オーダの依存関係が問題ない","実行時間がspaceより短い","段取り時間に変化がない"
                    # 判定はもう少し複雑にできるけどとりあえずシンプルに
                    # 段取り時間の部分は、opeでなくbeforeと判定すればOk
                    if(tar.order_before != None): # 2工程目以降
                        if(tar.order_before.t3 <= before_t3 and tar.run < space and abs(tar.i - before_i)%3 == 0):
                            
                            # 最初に見つけたものを登録しておく
                            if(bestfit == None):
                                bestfit = tar
                            
                            else: # spaceになるべくfitするものを選ぶ
                                
                                if(bestfit.run <= tar.run):
                                    bestfit = tar
                    
                    else: # 1工程目
                        #if(tar.order.e <= before_t3 and tar.run < space and ope.i == tar.i == tar_a.i):
                        if(tar.order.e <= before_t3 and tar.run < space and abs(tar.i - before_i)%3 == 0):
                            if(bestfit == None):
                                bestfit = tar
                            
                            else: # spaceになるべくfitするものを選ぶ
                                if(bestfit.run <= tar.run):
                                    bestfit = tar

                
                # bestfitがNoneでない、つまりbackfillできるものが見つかっていればbackfillを適用
                if(bestfit != None):
                       
                    # 時間の更新
                    bestfit.t1 = before_t3
                    bestfit.t2 = bestfit.t1
                    bestfit.t3 = bestfit.t2 + bestfit.run
                    
                    # 前後関係の更新
                    tmp_before = bestfit.machine_before
                    tmp_after = bestfit.machine_after
                    ope_before = ope.machine_before
                    
                    ope.machine_before.machine_after = bestfit
                    ope.machine_before = bestfit
                    
                    if(bestfit.machine_before != None):
                        bestfit.machine_before.machine_after = tmp_after
                    if(bestfit.machine_after != None):
                        bestfit.machine_after.machine_before = tmp_before
                    
                    bestfit.machine_before = ope_before
                    bestfit.machine_after = ope
                    
                    # フラグの更新
                    bestfit.backflg = True
                    mfound = True
                       
                #before値の更新       
                before_t3 = ope.t3
                before_i = ope.i
    
               
    def lco(self): # 局所クラスタリング組織化法
        count = 0
        # ope自身と前後の割り付けとの入れ替えを考える
        #for ope in self.operations:
        for j in range(len(self.operations)):
            ope = self.operations[j]
            
            # 同一マシンの前後に割り付けられていなければ対象外
            if(ope.machine_before == None or ope.machine_after == None):
                continue
            
            before = ope.machine_before
            after = ope.machine_after
            
            # 段取り時間が変化しうる場合は対象外
            if(ope.dan != 0 or before.dan != 0 or after.dan != 0):
                continue
                
            # ここから、opeとbeforeの交換の評価値
            
            # それぞれの制限時間を、条件に基づき登録
            # opeの交換後の開始すべき時刻
            if(ope.order_before != None):
                ope_start = ope.order_before.t3
            else:
                ope_start = ope.order.e
                
            # beforeの交換後の終了すべき時刻
            if(before.order_after != None):
                before_end = before.order_after.t1
            else:
                before_end = before.order.d
            
            # beforeと交換した時の評価値
            before_excvalue = (ope.order.d - (before.t1 + ope.run) ) + (before.order.d - (ope.t3) )
            # 交換しない場合の評価値
            before_value = (ope.order.d - ope.t3) + (before.order.d - before.t3)
            
            # before_valueが0ならexcvalueの値にしたがって更新
            if(before_value == 0 and before_excvalue == 0):
                before_excvalue = 10
                before_value = 10
            elif(before_value == 0 or before_excvalue == 0):
                diff = max(abs(before_excvalue),abs(before_value))*2
                before_excvalue += diff
                before_value += diff
                
                    
            
            # continueの代わりに、excvalueを極めて小さくしておく
            # 交換後、それぞれの前後の時刻に干渉してしまうなら対象外
            if(before.t1 < ope_start or ope.t3 > before_end):
                before_excvalue = abs(before_value)*(-100000)
 
            # beforeのみ最終工程、あるいはopeのみ1だと対象外
            if((ope.p != ope.order.p and before.p == before.order.p) or (ope.p == 0 and before.p != 0) ):
                before_excvalue = abs(before_value)*(-100000)
            
            # どちらかが第一工程であれば対象外
            if(ope.p == 0 or before.p == 0):
                before_excvalue = abs(before_value)*(-100000)
                
            # 同一オーダだと対象外
            if(ope.r == before.r):
                before_excvalue = abs(before_value)*(-100000)
            
            # 双方とも遅延していない場合は対象外
            if(ope.order.delay <= 0 and before.order.delay <= 0):
                before_excvalue = abs(before_value)*(-100000)

    
            # ここから、opeとafter交換の評価値
            
            # それぞれの制限時間を、条件に基づき登録
            # afterの交換後の開始すべき時刻
            if(after.order_before != None):
                after_start = after.order_before.t3
            else:
                after_start = after.order.e
 
            # opeの交換後の終了すべき時刻
            if(ope.order_after != None):
                ope_end = ope.order_after.t1
            else:
                ope_end = ope.order.d
                
            # afterと交換した時の評価値
            after_excvalue = (after.order.d - (ope.t1 + after.run) ) + (ope.order.d - (after.t3) )
            # 交換しない場合の評価値
            after_value = (after.order.d - after.t3) + (ope.order.d - ope.t3)
            
            if(after_value == 0 and after_excvalue == 0):
                after_excvalue = 10
                after_value = 10
            elif(after_value == 0 or after_excvalue == 0):
                diff = max(abs(before_excvalue),abs(before_value))*2
                after_excvalue += diff
                after_value += diff
            
            # 交換後、それぞれの前後の時刻に干渉してしまうなら対象外
            if(ope.t1 < after_start or after.t3 > ope_end):
                after_excvalue = abs(after_value)*(-100000)
 
            # opeのみ最終工程、あるいはafterのみ1だと対象外
            if((after.p != after.order.p and ope.p == ope.order.p) or (after.p == 0 and ope.p != 0) ):
                after_excvalue = abs(after_value)*(-100000)
            
            # どちらかが第一工程であれば対象外
            if(after.p == 0 or ope.p == 0):
                after_excvalue = abs(after_value)*(-100000)
            
            # 同一オーダだと対象外
            if(after.r == ope.p):
                after_excvalue = abs(after_value)*(-100000)
            
            
            # 双方とも遅延していない場合は対象外
            if(after.order.delay <= 0 and ope.order.delay <= 0):
                after_excvalue = abs(after_value)*(-100000)

            
            # いずれとも交換しない方が価値が良いならば、交換しない
            if(before_value >= before_excvalue and after_value >= after_excvalue):
                continue

            
            # beforeと交換する
            elif( (before_excvalue - before_value) >= (after_excvalue - after_value) ):
                
                
                tmp_t3 = ope.t3
                
                ope.t1 = before.t1
                ope.t2 = ope.t1
                ope.t3 = ope.t2 + ope.run
                
                before.t3 = tmp_t3
                before.t2 = tmp_t3 - before.run
                before.t1 = before.t2
                
                
                # ポインタのつなぎ変え
                if(ope.machine_after != None):
                    ope.machine_after.machine_before = before
                    before.machine_after = ope.machine_after
                else:
                    before.machine_after = None
                
                if(before.machine_before != None):
                    before.machine_before.machine_after = ope
                    ope.machine_before = before.machine_before
                else:
                    ope.machine_before = None
            
                ope.machine_after = before
                before.machine_before = ope
            
            
            # afterと交換する
            
            elif( (before_excvalue - before_value) < (after_excvalue - after_value) ):
                  
                tmp_t3 = after.t3
                
                after.t1 = ope.t1
                after.t2 = after.t1
                after.t3 = after.t2 + after.run
                
                ope.t3 = tmp_t3
                ope.t2 = tmp_t3 - ope.run
                ope.t1 = ope.t2
                
                
                # ポインタのつなぎ変え
                if(after.machine_after != None):
                    after.machine_after.machine_before = ope
                    ope.machine_after = after.machine_after
                else:
                    ope.machine_after = None
                
                if(ope.machine_before != None):
                    ope.machine_before.machine_after = after
                    after.machine_before = ope.machine_before
                else:
                    after.machine_before = None
            
                after.machine_after = ope
                ope.machine_before = after
                
        
    def checkResult(self): #依存関係を元に時間を調整する
    
        # 各オーダの「これだけ早くできる」を登録
        stend = [-1 for i in range(self.R)]
        
        # 工程順にsort
        self.operations = sorted(self.operations, key= attrgetter("p","r"))


        for ope in self.operations:

            self.checkOver(ope,0)

        # stendを更新する 
        # stendはオーダごとの値なので相関を見ていなかった
        
        for ope in self.operations:
            if(ope.p == 0):
                stend[ope.r] = ope.t1 - ope.order.e # そのオーダを前に動かせるだけの時間
            if(ope.order.p == ope.p):
                # (ope.t3 - ope.order.d)は、遅延している時間
                # そのためstendの値は"遅延を解消するために動かせる値の限界値"である
                # 負の値を示すなら遅延は発生していない
                stend[ope.r] = min(stend[ope.r],(ope.t3 - ope.order.d))
        
        # 工程を前に詰める再構成と、後ろに下げる再構成を繰り返す
        
        # ここのループをたくさんやれば良いのでは？
       
        for i in range(10):
            self.operations = sorted(self.operations, key = attrgetter("t3","m"),reverse = True)
            for ope in self.operations:
                if(stend[ope.r] > 0):
                    self.adjustDelay(ope,stend[ope.r])
        
        
        # 遅延時間を登録
        for ope in self.operations:
            if(ope.p == ope.order.p):
                ope.order.delay = ope.t3 - ope.order.d
        
        #backfillで間を埋める
        # backfillは、後ろのジョブを前に出す

        for i in range(50):
            
            self.backfill()
            self.lco()
            self.operations = sorted(self.operations, key = attrgetter("t3"))
            for ope in self.operations:
                time = self.adjustDelay(ope,999999)
        
        self.lco()
        
        for i in range(10):
            self.operations = sorted(self.operations, key = attrgetter("t3"), reverse = True)
            for ope in self.operations:
                time = self.adjustStart(ope,999999)
                
    def writeSolution(self):
        print("{}".format(len(self.operations)))
        
        self.operations = sorted(self.operations, key = attrgetter("m","t1"))

        
        for operation in self.operations:
            print("{} {} {} {} {} {}".format((operation.m + 1), (operation.r + 1), (operation.p + 1), operation.t1, operation.t2, operation.t3))

        
    def run(self):
        self.readProblem()
        self.solve()
        self.checkResult()
        self.writeSolution()

if __name__ == '__main__':
    asprova2 = Asprova2()
    asprova2.run()

