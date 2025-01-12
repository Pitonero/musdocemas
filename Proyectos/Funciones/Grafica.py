import matplotlib.pyplot as plt

x = [1, 2, 3, 4, 5]
y = [2, 3, 4, 5, 6]

plt.plot(x, y)
plt.xlabel('Eje X')
plt.ylabel('Eje Y')
plt.title('Gráfico de Líneas')
plt.show()

import pandas as pd
import seaborn as sns

data = {'Ciudad': ['Nueva York', 'Chicago', 'San Francisco', 'Los Ángeles'],
        'Población': [8623000, 2716000, 883305, 3976000]}

df = pd.DataFrame(data)

sns.barplot(x='Ciudad', y='Población', data=df)
plt.xlabel('Ciudad')
plt.ylabel('Población')
plt.title('Población de las Ciudades')
plt.show()

import plotly.express as px

df = px.data.iris()

fig = px.scatter_3d(df, x='sepal_length', y='sepal_width', z='petal_length', color='species')
fig.show()
