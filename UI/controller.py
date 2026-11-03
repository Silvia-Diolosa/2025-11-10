import flet as ft


class Controller:
    def __init__(self, view, model):
        # the view, with the graphical elements of the UI
        self._view = view
        # the model, which implements the logic of the program and holds the data
        self._model = model
        self._choiceStore = None
        self._choiceOrder = None


    def fillDD(self):
        stores = self._model.getAllStores()
        for store in stores:
            self._view._ddStore.options.append(ft.dropdown.Option(data=store,
                                                                  key=store.store_name,
                                                                  on_click=self.handleChoice))

    def handleChoice(self, e):
        self._choiceStore = e.control.data


    def handleCreaGrafo(self, e):
        if self._choiceStore is None:
            self._view.txt_result.controls.clear()
            self._view.txt_result.controls.append(
                ft.Text("Selezionare un valore dal menu."))
            self._view.update_page()
            return

        txt = self._view._txtIntK.value

        if txt is None:
            self._view.txtResult.controls.clear()
            self._view.txtResult.controls.append(
                ft.Text("Inserire un valore."))
            self._view.update_page()
            return

        try:
            val = int(txt)
        except ValueError:
            self._view.txtResult.controls.clear()
            self._view.txtResult.controls.append(
                ft.Text("Inserire un valore intero."))
            self._view.update_page()
            return

        if val < 1 :
            self._view.txtResult.controls.clear()
            self._view.txtResult.controls.append(
                ft.Text("Inserire un valore maggiore di 1 "))
            self._view.update_page()
            return

        self._model.buildGraph(self._choiceStore, val)
        nNodi, nArchi = self._model.getGraphDetails()

        self._view.txt_result.controls.clear()
        self._view.txt_result.controls.append(
            ft.Text("Grafo correttamente creato.", color="green"))
        self._view.txt_result.controls.append(
            ft.Text(f"Nodi: {nNodi}, Archi: {nArchi}"))

        edges = self._model.getEdges()
        edges.sort(key=lambda x: x[2]["weight"], reverse=True)
        best5 = edges[0:5]
        self._view.txt_result.controls.append(ft.Text("cinque archi peso maggiore", color="green"))
        for edge in best5:
            self._view.txt_result.controls.append(ft.Text(f"arco: {edge[0]} --> {edge[1]}, peso: {edge[2]["weight"]}"))

        self._view._ddNode.disabled = False
        self.fillDDNodi()
        self._view._btnCerca.disabled = False
        self._view._btnRicorsione.disabled = False

        self._view.update_page()


    def fillDDNodi(self):
        nodes = self._model.getNodes()
        for node in nodes:
            self._view._ddNode.options.append(ft.dropdown.Option(data=node,
                                                                 key=node.order_id,
                                                                 on_click=self.handleChoiceNodo))

    def handleChoiceNodo(self, e):
        self._choiceOrder = e.control.data


    def handleCerca(self, e):
        self._view.txtResult.controls.clear()

        if self._choiceOrder is None:
            self._view.txt_result.controls.clear()
            self._view.txt_result.controls.append(
                ft.Text("Selezionare un valore dal menu."))
            self._view.update_page()
            return

        percorso = self._model.getPercorsoMax(self._choiceOrder)
        for nodo in percorso:
            self._view.txt_result.controls.append(
                ft.Text(f"{nodo}"))

        self._view.update_page()

    def handleRicorsione(self, e):
        self._view.txtResult.controls.clear()

        if self._choiceOrder is None:
            self._view.txt_result.controls.clear()
            self._view.txt_result.controls.append(
                ft.Text("Selezionare un valore dal menu."))
            self._view.update_page()
            return


        bestPath, bestScore = self._model.getBestPath(self._choiceOrder)

        self._view.txt_result.controls.append(ft.Text(f"il percorso migliore ha peso {bestScore} e i nodi soo i seguenti:"))
        for nodo in bestPath:
            self._view.txt_result.controls.append(ft.Text(f"{nodo}"))

        self._view.update_page()