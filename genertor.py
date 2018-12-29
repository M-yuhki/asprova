import random

print("input number(1 or 2 or 3)")
n = int(input())

eva = ""
pro = ""
setup = ""
a = ""
b = ""

a1 = random.randint(0,100)
b1 = random.uniform(0.1,2.0)
a2 = random.randint(0,100)
b2 = random.uniform(0.1,2.0)
a3 = random.randint(0,min(a1,a2))
b3 = random.uniform(0.1,min(b1,b2))

eva = "{}\t{}\t{}\t{}\t{}\t{}".format(a1,a2,a3,b1,b2,b3)

print(n)
if(n == 1):
  k = 4

elif(n == 2):
  k = 10

elif(n == 3):
  k = 20 

else:
  k = 0
print(k)

for i in range(k):
  pro += str(random.randint(1,10000))
  setup += str(random.randint(1,10000))
  if(i != -1):
    pro += "\t"
    setup += "\t"

print("EVALUATIONFACTOR\t{}".format(eva))
print("PRODUCTIONFACTOR\t{}".format(pro))
print("SETUPFACTOR\t{}".format(setup))
