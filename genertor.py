import random

print("input number(1 or 2 or 3)")
n = input()

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


if(n == 1):
  for i in range(4):
    pro += str(random.randint(1,))

else:
  print("ERROR")


print("EVALUATIONFACTOR\t{}".format(eva))
print("PRODUCTIONFACTOR")
print("SETUPFACTOR")
