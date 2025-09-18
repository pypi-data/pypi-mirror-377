from .estructuras import ListaEnlazada, Producto

def calcular_valor_total(inventario: ListaEnlazada) -> float:
    """
    Calcula el valor total del inventario.

    Args:
        inventario: La lista enlazada con los productos.

    Returns:
        El valor total del inventario.
    """
    valor_total = 0.0
    actual = inventario.cabeza
    while actual:
        valor_total += actual.producto.cantidad * actual.producto.precio
        actual = actual.siguiente
    return valor_total

def obtener_stock_bajo(inventario: ListaEnlazada, umbral: int) -> list[Producto]:
    """
    Obtiene una lista de productos con un stock por debajo de un umbral dado.

    Args:
        inventario: La lista enlazada con los productos.
        umbral: El valor umbral para considerar el stock como bajo.

    Returns:
        Una lista de objetos Producto.
    """
    productos_bajos = []
    actual = inventario.cabeza
    while actual:
        if actual.producto.cantidad < umbral:
            productos_bajos.append(actual.producto)
        actual = actual.siguiente
    return productos_bajos

def obtener_productos_mas_caros(inventario: ListaEnlazada, n: int) -> list[Producto]:
    """
    Obtiene los N productos más caros del inventario.

    Args:
        inventario: La lista enlazada con los productos.
        n: El número de productos más caros a retornar.

    Returns:
        Una lista de los N objetos Producto más caros.
    """
    productos = []
    actual = inventario.cabeza
    while actual:
        productos.append(actual.producto)
        actual = actual.siguiente
    
    productos.sort(key=lambda p: p.precio, reverse=True)
    return productos[:n]

def obtener_productos_mas_vendidos(inventario: ListaEnlazada, n: int) -> list[Producto]:
    """
    Obtiene los N productos más vendidos del inventario.

    Args:
        inventario: La lista enlazada con los productos.
        n: El número de productos más vendidos a retornar.

    Returns:
        Una lista de los N objetos Producto más vendidos.
    """
    productos = []
    actual = inventario.cabeza
    while actual:
        productos.append(actual.producto)
        actual = actual.siguiente
    
    productos.sort(key=lambda p: p.veces_vendido, reverse=True)
    return productos[:n]