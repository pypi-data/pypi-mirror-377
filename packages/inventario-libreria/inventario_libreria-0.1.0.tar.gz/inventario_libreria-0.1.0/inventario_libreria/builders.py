import json
from .estructuras import ListaEnlazada, Producto

class InventarioBuilder:
    """
    Patrón de diseño Builder para construir un inventario de forma encadenada.
    """
    def __init__(self):
        self._inventario = ListaEnlazada()

    def agregar_producto(self, nombre: str, cantidad: int, precio: float, veces_vendido: int = 0):
        """
        Agrega un producto al inventario que se está construyendo.
        
        Args:
            nombre: El nombre del producto.
            cantidad: La cantidad en stock.
            precio: El precio unitario.
            veces_vendido: La cantidad de veces que se ha vendido el producto.
            
        Returns:
            La instancia del builder para encadenar más llamadas.
        """
        producto = Producto(nombre, cantidad, precio, veces_vendido)
        self._inventario.agregar_producto(producto)
        return self

    def construir(self) -> ListaEnlazada:
        """
        Retorna el inventario construido.
        
        Returns:
            Una instancia de ListaEnlazada con los productos.
        """
        return self._inventario

def construir_desde_json(ruta_archivo: str) -> ListaEnlazada:
    """
    Crea un inventario a partir de un archivo JSON.
    
    Args:
        ruta_archivo: La ruta al archivo JSON con los datos del inventario.
        
    Returns:
        Una instancia de ListaEnlazada o None si hay un error.
    """
    inventario = ListaEnlazada()
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
            datos = json.load(archivo)
            for item in datos:
                producto = Producto(item['nombre'], item['cantidad'], item['precio'], item.get('veces_vendido', 0))
                inventario.agregar_producto(producto)
    except FileNotFoundError:
        print(f"Error: El archivo '{ruta_archivo}' no fue encontrado.")
        return None
    except Exception as e:
        print(f"Ocurrió un error al leer el archivo JSON: {e}")
        return None
    return inventario