import csv
import networkx as nx
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import json
import os.path
import random

'''
MyJamArtist: Clase que construye 2 tipos de grafos: La red entre los usuarios  y la red de artistas por géneros. La clase hace la unión entre estos dos grafos
y aplica el filtrado colaborativo para generar la recomendación.
Input: doc, el path del archivo .csv en donde cada fila representa a un usuario y cada columna representa el top de los usuarios en orden descendente
Output: un diccionario con los artistas recomendados y su puntaje para un usuario en específico.
'''
class MyJamArtist():

    def __init__(self, doc) -> None:
        self.doc = doc
        self.artistas = {} #Aquí se van a guardar un diccionario con llave el nombre del artista en mayúsculas y sus géneros.
        self.usuarios = [] #Aquí se guardan los usuarios con su top 10 asociado a ellos en un diccionario. Es una lista de diccionarios.
        self.grafo_usuarios = self.crear_grafo_usuarios()
        self.grafo_artistas = self.crear_grafo_artistas()
        self.grafo_recommend = self.crear_grafo_recommend()

    def crear_usuarios(self): #Método que lee el CSV de la base de datos y construye la lista de diccionarios correspondientes a cada usuario.
        with open(self.doc) as d:
            reader = csv.reader(d, delimiter=';')
            for u in reader:
                usuario = {}
                for i,a in enumerate(u):
                    usuario[i+1] = a
                    self.artistas[a]=[]
                self.usuarios.append(usuario)

    def get_artist_genres(self,artist_name): #Consulta el API de spotify para obtener los géneros de un artista.
        # Credenciales de Spotipy
        client_id = '4417bca2fc0f405aa211b519e067bbaf'
        client_secret = '9d53090efda44e968a6d4d5f5166ca36'
        client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        # Busca el Artista
        results = sp.search(q=artist_name, type='artist', limit=1)
        if 'artists' in results and 'items' in results['artists'] and len(results['artists']['items']) > 0:
            artist = results['artists']['items'][0]
            return artist['genres']
        else:
            return []

    def fetch_genero_artistas(self): #Llama a get_artist_genres() para obtener los géneros de todos los artistas. Crea el archivo JSON con esta información. Si el archivo ya está creado lo lee y lo transforma a un diccionario de Python
        if not os.path.isfile('./info_artists.txt'):
            for artista in self.artistas.keys():
                self.artistas[artista]=self.get_artist_genres(artista)
            jason = json.dumps(self.artistas)
            with open('info_artists.txt', 'w') as f:
                f.write(jason)
        else:
            with open('./info_artists.txt', 'r') as f:
                self.artistas = json.load(f)

    def crear_grafo_usuarios(self): #Construye el grafo de usuarios donde un usuario está relacionado con otro en tanto comparten gustos musicales.
        self.crear_usuarios()
        self.fetch_genero_artistas()
        G = nx.Graph()
        #Crea los nodos numerados y con atributo dict con el top de artistas.
        for i,u in enumerate(self.usuarios):
            G.add_node(i,top = u)
        #Crea las aristas entre usuario según la métrica de afinidad entre usuarios.
        for u1 in range(len(self.usuarios)):
            u1_min = {}
            for u2 in range(len(self.usuarios)):
                if u1 != u2:
                    #Calcula el common artists entre u1 y u2.
                    artists_u1 = G.nodes[u1]['top'].values()
                    artists_u2 = G.nodes[u2]['top'].values()
                    a_u1 = set([i for i in artists_u1])
                    a_u2 = set([i for i in artists_u2])
                    CA = len(a_u1.intersection(a_u2))
                    if CA >= 2: #No es necesario buscar el common position cuando no comparten artistas. Además, se restringe a que compartan mínimo dos artistas.
                        CP = 0
                        for u1_a, u2_a in zip(artists_u1,artists_u2):
                            if u2_a == u1_a:
                                CP +=1
                        puntaje_u1_u2 = 1/(4*CA + 6*CP)
                    else:
                        puntaje_u1_u2 = 2 #No comparten artistas

                    #Guarda el usuario y el peso si es de los 6 con menor afinidad
                    if puntaje_u1_u2 !=2:
                        if len(u1_min) < 6: 
                            u1_min[u2] = puntaje_u1_u2
                        else:
                            if puntaje_u1_u2 < min(u1_min.values()):
                                mx = max(u1_min, key = u1_min.get)
                                del u1_min[mx]
                                u1_min[u2] = puntaje_u1_u2
            #Crea las aristas con los nodos con afinidad mínima
            for user in u1_min:
                G.add_edge(u1, user, weight=u1_min[user])
        return G
    
    def crear_grafo_artistas(self):
        G = nx.Graph()
        #Crear los nodos numerados y con atributo el dict con el top de artistas
        for i in self.artistas.keys():
            G.add_node(i, genres = self.artistas[i])
        #Crear las aristas entre usuario según la métrica de afinidad entre usuarios
        for a1 in self.artistas:
            a1_min = {}
            for a2 in self.artistas:
                if a1 != a2:
                    #Calcula el common artists entre u1 y u2
                    g_a1 = set(G.nodes[a1]['genres'])
                    g_a2 = set(G.nodes[a2]['genres'])
                    CG = len(g_a1.intersection(g_a2)) #cantidad de géneros que comparten
                    if CG!=0:
                        puntaje_a1_a2=1/CG
                    else:
                        puntaje_a1_a2=2
                    #Guarda el usuario y el peso si es de los 6 con menor afinidad
                    if puntaje_a1_a2 !=2:
                        if len(a1_min) < 6: 
                            a1_min[a2] = puntaje_a1_a2
                        else:
                            if puntaje_a1_a2 < min(a1_min.values()):
                                mx = max(a1_min, key = a1_min.get)
                                del a1_min[mx]
                                a1_min[a2] = puntaje_a1_a2

            #Crea las aristas con los nodos con afinidad mínima
            for artist in a1_min:
                G.add_edge(a1, artist, weight=a1_min[artist])
        return G
    
    def crear_grafo_recommend(self): #Hace la unión entre los grafos de artistas y usuarios, relacionando cada usuario con los artistas de su top 10.
        G=nx.union(self.grafo_artistas, self.grafo_usuarios)
        for u in range(len(self.usuarios)):
            artists_u=G.nodes[u]['top'].values()
            cont=1
            for a in artists_u:
                G.add_edge(u,a, weight=cont)
                cont+=1
        return G

    def filtrado_lcd(self, u1):#Algoritmo de filtrado colaborativo. Nombrado en honor a los creadores uwu.
        recommends={}
        artistas_u1=set(self.grafo_usuarios.nodes[u1]['top'].values())
        #Algoritmo de recomendación
        for c in self.grafo_usuarios.nodes:
            w_min=10000
            if c != u1:
                artistas_c= set(self.grafo_usuarios.nodes[c]['top'].values())
                #Se filtran los artistas que pueden estar repetidos en los tops.
                diff_sim=artistas_c.symmetric_difference(artistas_u1)
                artistas_u1_sim= artistas_u1.intersection(diff_sim)
                artistas_c_sim= artistas_c.intersection(diff_sim)
                for a in artistas_c_sim:
                    for b in artistas_u1_sim:
                        w_rec, path = nx.single_source_dijkstra(self.grafo_recommend, a, b, None, 'weight')
                        if w_rec<w_min:
                            w_min=w_rec
                            recommends[a]=w_min
        #Escoge las 30 mejores recomendaciones
        recommends_final={}
        for r in recommends:
            if len(recommends_final) < 30: 
                recommends_final[r] = recommends[r]
            else:
                if recommends[r] < max(recommends_final.values()):
                    mx = max(recommends_final, key = recommends_final.get)
                    del recommends_final[mx]
                    recommends_final[r]=recommends[r]
        rands=[]
        generos_u1 = set()
        recommends_final_final={}

        #Busca los artistas que comparten géneros con el usuario para mejorar la recomendación
        for a in artistas_u1:
            generos_A = self.artistas[a]
            generos_u1.update(generos_A)
        
        for r in recommends_final:
            g_r = set(self.artistas[r])
            inter = g_r.intersection(generos_u1)
            if len(inter) != 0 and len(recommends_final_final) <= 8:
                recommends_final_final[r] = recommends_final[r]
        
        #Rellena la lista con aleatorios hasta tener 8 recomendaciones
        while len(recommends_final_final) <= 8:
            rand_artist, rand_w = random.choice(list(recommends_final.items()))
            while((rand_artist, rand_w) in rands):
              rand_artist, rand_w = random.choice(list(recommends_final.items())) 
            rands.append((rand_artist,rand_w))
            recommends_final_final[rand_artist]=rand_w

        return artistas_u1, recommends_final_final