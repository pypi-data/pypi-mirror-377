import os, time, math, datetime
os.system('cls')

from matplotlib import pyplot
ages = [9,21.5,27.5,32.5,42.5,47.5,52.5,57.5,79.5]

coefs = {'1': 8.730887896085287, 'age_group2': -0.3161219010603968, 'age_group': 38.94666767730002}
incomes = [coefs['1']+coefs['age_group']*age+coefs['age_group2']*age**2 for age in ages]
pyplot.plot(ages, incomes, label='1')

coefs = {'1': -305.13066728256337, 'age_group': 60.53173639234256, 'age_group2': -0.47819069065097364}
incomes = [coefs['1']+coefs['age_group']*age+coefs['age_group2']*age**2 for age in ages]
pyplot.plot(ages, incomes, label='2')



pyplot.legend()
pyplot.show()
