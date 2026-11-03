import copy

import networkx as nx

from database.DAO import DAO

class Model:
    def __init__(self):
        self._graph = nx.DiGraph()
        self.idMap = {}
        self.bestPath = []
        self.bestScore = 0

    def getAllStores(self):
        return DAO.getAllStores()

    def buildGraph(self,store, n):
        self._graph.clear()

        nodes = DAO.getAllNodes(store)
        for node in nodes:
            self.idMap[node.order_id] = node

        self._graph.add_nodes_from(nodes)

        edges = DAO.getAllEdges(store, n)
        for edge in edges:
            u = self.idMap[edge[0]]
            v = self.idMap[edge[1]]
            self._graph.add_edge(u, v, weight=edge[2])


    def getGraphDetails(self):
        return len(self._graph.nodes), len(self._graph.edges)


    def getNodes(self):
        return list(self._graph.nodes)
    def getEdges(self):
        return list(self._graph.edges(data=True))


    # Tramite il pulsante “Cerca Percorso Massimo”, si visualizzi il cammino più lungo partendo da un nodo (si
    # scelga l’algoritmo di visita del grafo più opportuno fra visita in ampiezza ed in profondità). Il nodo è
    # selezionato dall’apposito menù a tendina.
    def getPercorsoMax(self, partenza):

        # questa soluzione è sbgaliata
        archi = nx.dfs_edges(self._graph, partenza)
        nodiDFS = [partenza]
        for u, v in archi:
            nodiDFS.append(v)
        # return nodiDFS

        # perchè:
        # nx.dfs_edges ti dà gli archi nell’ordine in cui la DFS li percorre. La DFS fa questo:
        #
        # Parte da A e va su B.
        # Da B va su D.
        # Da D va su E.
        # Da E non può andare avanti, quindi torna indietro fino ad A.
        # Da A va su C.
        #
        # Gli archi restituiti sono quindi (A,B), (B,D), (D,E), (A,C).
        # Il tuo codice prende solo il secondo elemento di ogni arco e ottiene la lista:
        #
        # [A, B, D, E, C]
        #
        # Leggendola come cammino direbbe A → B → D → E → C, ma l’arco E → C non esiste.
        # Tra E e C la DFS aveva fatto marcia indietro, e la tua lista non lo registra.
        #
        # Il tuo codice restituisce quindi l’ordine in cui i nodi vengono scoperti, non un cammino.
        # Il tuo output, in questo caso, ha anche 5 nodi invece di 4, e il cammino vero è più corto.



        # SOLUZIONE CORRETTA
        # L’idea è di non fidarsi dell’ordine di visita, ma di costruire l’albero della DFS e poi ricostruire i cammini veri.

        # ((((_tree, costruisce e ti restituisce un vero e proprio oggetto grafo (un sotto-grafo orientato)
        # che rappresenta l'albero di visita. Non è una semplice lista di coppie, ma un oggetto grafo a tutti gli effetti che possiede
        # già al suo interno tutti i nodi e tutti gli archi della visita.))))

        # Passo 1: tree = nx.dfs_tree(self._graph, source)
        # È un nuovo grafo che contiene solo gli archi che la DFS ha davvero usato per scoprire nuovi nodi. Nel nostro esempio sono tutti e 4: A→B, A→C, B→D, D→E.
        # In un albero ogni nodo ha un solo padre, quindi per ogni nodo esiste un solo percorso che parte dalla sorgente.
        # Passo 2: nodi = list(tree.nodes())
        # La lista dei nodi raggiunti: A, B, D, E, C.

        # Passo 3: per ogni nodo ricostruisce il suo percorso risalendo i padri

        #Prendi il nodo E:
        # e dobbiamo arrivare al primo nodo A (partenza)
        # (questa cosa la fa per ogni nodo, E,C,B, e A, e cerca un cammino per arrivare al nodo di partenza A)

        # costriamo lista tmp, dove iniziamo ad aggiungere E
        # tmp = [E]

        # tmp[0] è E, diverso da A, quindi cerca il padre di E, che è D, e lo mette davanti: [D, E]
        # tmp[0] è D, diverso da A, quindi padre di D = B: [B, D, E]
        # padre di B = A: [A, B, D, E]
        # tmp[0] è A, uguale alla sorgente, quindi il ciclo while si ferma
        # e abbiamo completato il percorso temp

        # nx.predecessor(tree, source, tmp[0]) serve proprio a trovare il padre di quel nodo,
        # e pred[0] ne prende il primo (e unico) elemento.
        # Questa funzione fa una visita in ampiezza (BFS) a partire da source e annota, per ogni nodo, da quale nodo è stato raggiunto.
        # Se come terzo argomento passi un nodo (qui tmp[0]), ti restituisce solo la lista dei predecessori di quel nodo.
        #
        # Nel nostro albero A→B, A→C, B→D, D→E:
        #
        # nx.predecessor(tree, A, E) restituisce [D]
        # nx.predecessor(tree, A, D) restituisce [B]
        # nx.predecessor(tree, A, B) restituisce [A]
        # Il risultato è una lista perché in un grafo generico un nodo può avere più predecessori. Nell’albero ne ha sempre uno solo, quindi pred[0] è il padre.

        # Passo 4: tiene il percorso più lungo
        # per ogni nodo, abbiamo ottenuto diversi tmp, teniamo il più lungo
        #
        # Nodo	Percorso ricostruito	Lunghezza
        # A	            [A]	                1
        # B	            [A, B]	            2
        # D	            [A, B, D]	        3
        # E	            [A, B, D, E]	    4
        # C	            [A, C]	            2


        lp = []


        tree = nx.dfs_tree(self._graph, partenza)
        nodi = list(tree.nodes())

        for node in nodi:
            tmp = [node]

            while tmp[0] != partenza:
                pred = nx.predecessor(tree, partenza, tmp[0])
                tmp.insert(0, pred[0])

            if len(tmp) > len(lp):
                 lp = copy.deepcopy(tmp)

        return lp


    def getBestPath(self, partenza):
        self.bestPath = []
        self.bestScore = 0

        parziale = [partenza]

        self.ricorsione(parziale)

        return self.bestPath, self.bestScore

    def ricorsione(self, parziale):
        # caso terminale
        score = self.calcolaScore(parziale)
        if score > self.bestScore:
            self.bestScore = score
            self.bestPath = copy.deepcopy(parziale)

        # caso ricorsivo
        for nodo in self._graph.successors(parziale[-1]):
            if nodo not in parziale:
                if self.condizione(nodo, parziale):
                    parziale.append(nodo)
                    self.ricorsione(parziale)
                    parziale.pop()


    def condizione(self, nodo, parziale):
        pesoAttuale  = self._graph[parziale[-1]][nodo]['weight']

        if len(parziale) > 2:
            pesoPrecedente = self._graph[parziale[-2]][parziale[-1]]['weight']
            if pesoAttuale < pesoPrecedente:
                return True
            else:
                return False

        return True


    def calcolaScore(self, parziale):
        score = 0
        for i in range(len(parziale) - 1):
            score += self._graph[parziale[i]][parziale[i + 1]]["weight"]
        return score


