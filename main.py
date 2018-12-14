import copy
import numpy as np

class Par: # 入力値や各種パラメータを扱うクラス
  # 入力値以外のパラメータ
  trend = -1 # スケジューリングの時の指向
  OL = 0 # 最終出力用の割り当ての数

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
  def __init__(self,m,c,d):
    self.m = m
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
    self.lim = d - e #納期までの時間
    self.prest = -1# そのオーダの残り工程数 (i,prest)で工程特定可能
    self.drest = d # すでに割り当てたプロセスを差し引いた納期


# 品目ごとの情報を扱うクラス
# 他の情報で補えるのだが参照しやすいように
class Item(object):
  def __init__(self,i,p,mlist):
    self.i = i
    self.p = p # その品目の工程数
    self.mlist = mlist # その品目を扱うことができるマシン番号
    self.gid = i%3 # グループid:これが同じだと工程依存が発生しない

# マシンの割り当て状況
class Mlog(object):
  def __init__(self,m,r,p,t1,t2,t3,i):
    self.m = m
    self.r = r
    self.p = p
    self.t1 = t1
    self.t2 = t2
    self.t3 = t3
    self.i = i #品目番号を登録しておく 
    self.gid = i%3

# 回答
class Log(object):
  def __init__(self):
    self.m = -1



def test(machine):
  print(machine)
  print(vars(machine[1]))


#傾向を判断する
#Bも判断してきちんとやりたい
def check_trend(self):
  if(self.A2 == max(self.A1,self.A2,self.A3)):
    return 2
  elif(self.A1 == max(self.A1,self.A3)):
    return 1
  else:
    return 3


#スケジュールの対象とするジョブを選択する
#今は単純な判定だがgnumとかをちゃんと使う
def select_job(trend,order,gnum):
  p = -1
  j = 999999
  for i in range(len(order)):
    if(order[i].lim < j):
      p = i
      j = order[i].lim
  return p

#スケジューリングアルゴリズムの部分
def select_bom(par,bom,tar_order,mlog):
  first = -1 # 最初に見つけたもの
  b = -1
  for j in range(par.BL):
    # 取り扱えるマシンを抽出
    # sortしているのでとりあえず先頭から見る
    if(tar_order.i == bom[j].i and tar_order.prest == bom[j].p):
      if(first == -1):
        first = j
      
      # 割り当て状況を確認
      # mlogが空なら確定
      if(len(mlog[bom[j].m]) == 0):
        b =  j
      # ざっくりと時間を計算して割り当てられるか判定
      else:
        mlog[bom[j].m].sort(key = lambda x:x.t1)
        
        if(mlog[bom[j].m][0].t1 -1 - (bom.t * tar_order.q * mlog[bom[j].m][0].c) - (abs((mlog_tl[0].i-tar_order.i)%3)*mlog[bom[j].m][0].d)  > 0):

        #if(abs(mlog[bom[j].m][0].i-tar_order.i)%3):
          b = j
    
    if(b != -1):
      break
  
  if(b != 1):
    return b
  else:
    return first 

  

def pick_machine(machine,m):
  for j in range(len(machine)):
    if(machine[j].m == m):
      return j
  return -1

    
def batch_job(par,machine,bom,tar_order,mlog_tl):
  # mlog_tl はそのマシンの配列
  
  # m,r,p,t1,t2,t3
  
  gid = (tar_order.i)%3

  # 実行
  runtime = bom.t * tar_order.q * machine.c

  if(len(mlog_tl) == 0):
    batch = Mlog(machine.m, tar_order.r, bom.p, tar_order.drest-runtime, tar_order.drest-runtime, tar_order.drest, tar_order.i) 
  else:
    mlog_tl.sort(key = lambda x:x.t1)
    pena = abs((mlog_tl[0].i-tar_order.i)%3)*machine.d
    batch = Mlog(machine.m, tar_order.r, bom.p, mlog_tl[0].t1 -1 -runtime - pena,mlog_tl[0].t1 - 1 - runtime , mlog_tl[0].t1 - 1,  tar_order.i)

  return batch


def scheduler(trend,par,machine,bom,order,item):
  mlog = [[] for i in range(par.M + 1)] # マシンの割り当て状況 0は空列
  gnum = -1 # 直前に選択したジョブのグループ
  while True:
    # スケジュールの対象とするジョブを選択
    a = select_job(trend,order,gnum)
    
    if(a == -1): # a = -1はジョブがないこと意味する
      break
    
    tar_order = order[a]
    
    # 作る品目と工程
    # 品目番号tar_order.i,工程tar_order.prest
    
    # 使用するBOM/割り当てるマシンを選択
    tar_bom = bom[select_bom(par,bom,tar_order,mlog)]
    tar_machine = machine[pick_machine(machine,tar_bom.m)]
    
    # マシンに割り当て
    result =  batch_job(par,tar_machine,tar_bom,tar_order,mlog[tar_machine.m])
    

    mlog[tar_machine.m].append(result)

    par.OL += 1

    tar_order.prest -= 1

    if(tar_order.prest == 0):
      order.pop(a)


  return mlog


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
  machine.sort(key = lambda x:x.cd)
  
  bom = []
  for j in range(par.BL):
    i,p,m,t = map(int,input().split()[1:])
    bom.append(Bom(i,p,m,t))

  order = []
  for j in range(par.R):
    r,i,e,d,q = list(map(int,input().split()[1:]))
    order.append( Order(r,i,e,d,q) )

  #orderを納期までの期限が短い順にsort
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
  
  # itemを元にprestを登録
  for j in order:
    j.prest = item[j.i - 1].p

  
  # 入力受付だいたいここまで

  # 重視すべき要素を判断
  trend = check_trend(par)

  
  # trendに合わせて配列をsortする
  if(trend == 1): #段取り最適化重視
    machine.sort(key = lambda x:(x.d,x.cd,x.c))
    order.sort(key = lambda x:x.lim)
    item.sort(key = lambda x:(x.p,len(x.mlist)))

  elif(trend == 2): #納期遵守重視
    machine.sort(key = lambda x:(x.cd,x.c,x.d))
    order.sort(key = lambda x:(x.lim,-x.d))
    item.sort(key = lambda x:len(x.mlist))

  else: #着手遅延ボーナス最大化重視
    machine.sort(key = lambda x:(x.c,x.cd,x.d))
    order.sort(key = lambda x:(x.lim,-x.d))
    item.sort(key = lambda x:len(x.mlist))


  # ここからスケジューリング
  result = scheduler(trend,par,machine,bom,order,item)


  # 最終的な出力

  print(par.OL)
  for s in result:
    for t in s:
      print("{} {} {} {} {} {}".format(t.m,t.r,t.p,t.t1,t.t2,t.t3))


  
  # 動作確認用のprint
  #print("****machine****")
  #for j in machine:
  #  print(vars(j))
  #print("******bom******")
  #for j in bom:
  #  print(vars(j))
  #print("*****order*****")
  #for j in order:
  #  print(vars(j))
  #print("*****item******")
  #for j in item:
  #  print(vars(j))


if __name__ == "__main__":
  main()
