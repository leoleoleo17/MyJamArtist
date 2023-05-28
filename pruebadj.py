import networkx as nx

G = nx.cycle_graph(5)
G[0][1]['weight']=1
G[1][2]['weight']=2
G[2][3]['weight']=3
G[3][4]['weight']=9
G[4][0]['weight']=1

length, path = nx.single_source_dijkstra(G, 3, 4, None, 'weight')
print(length,path)