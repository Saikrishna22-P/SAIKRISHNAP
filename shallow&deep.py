import copy
l=[1,2,[3,4]]
sh_l=copy.copy(l)
sh_l[2][0]=33
print(l)
dc_l=copy.deepcopy(l)
dc_l[2][0]=44
print(l)
