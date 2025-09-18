class Producto:
    """Clase que representa un producto en el inventario."""
    def __init__(self, nombre: str, cantidad: int, precio: float, veces_vendido: int = 0):
        self.nombre = nombre
        self.cantidad = cantidad
        self.precio = precio
        self.veces_vendido = veces_vendido

class Nodo:
    """Clase que representa un nodo en la lista enlazada."""
    def __init__(self, producto: Producto):
        self.producto = producto
        self.siguiente = None

class ListaEnlazada:
    """
    Clase que implementa una lista enlazada para gestionar productos.
    Permite agregar productos de manera eficiente.
    """
    def __init__(self):
        self.cabeza = None

    def agregar_producto(self, producto: Producto):
        """
        Agrega un producto al final de la lista enlazada.

        Args:
            producto: El objeto Producto a agregar.
        """
        nuevo_nodo = Nodo(producto)
        if not self.cabeza:
            self.cabeza = nuevo_nodo
            return
        actual = self.cabeza
        while actual.siguiente:
            actual = actual.siguiente
        actual.siguiente = nuevo_nodo