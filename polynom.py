import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures


dataset = pd.read_csv('dataset-polynomial-regression-master/Position_Salaries.csv')

x = dataset.iloc[:,1:2].values  
y = dataset.iloc[:,2].values

lin_reg = LinearRegression()
lin_reg.fit(x,y)

plt.scatter(x, y, color='red')
plt.plot(x, lin_reg.predict(x),color='blue')
plt.title("Truth or Bluff(Linear)")
plt.xlabel('Position level')
plt.ylabel('Salary')
# plt.show()


# visualising polynomial regression

poly_reg = PolynomialFeatures(degree=4)
x_poly = poly_reg.fit_transform(x)
lin_reg2 = LinearRegression()
lin_reg2.fit(x_poly,y)
 
x_grid = np.arange(min(x),max(x),0.1)
x_grid = x_grid.reshape(len(x_grid),1) 
plt.scatter(x,y, color='red') 
 
plt.plot(x_grid, lin_reg2.predict(poly_reg.fit_transform(x_grid)),color='blue') 
 
plt.title("Truth or Bluff(Polynomial)")
plt.xlabel('Position level')
plt.ylabel('Salary')
plt.show()

