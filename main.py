from random import choice
from algoritmos import MyJamArtist

g = MyJamArtist('./respuestas.csv')
u = choice(range(80))
a, info = g.filtrado_lcd(u)
print(f'El usuario {u} con top {a} se le recomienda escuchar {info}')


