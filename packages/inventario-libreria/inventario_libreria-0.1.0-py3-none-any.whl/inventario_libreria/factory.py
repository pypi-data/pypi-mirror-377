from .estructuras import Producto

def crear_producto(tipo_producto, nombre, cantidad, precio, veces_vendido=0):
    if tipo_producto == 'ropa':
        return Producto(nombre, cantidad, precio, veces_vendido)
    elif tipo_producto == 'electronico':
        return Producto(nombre, cantidad, precio, veces_vendido)
    else:
        raise ValueError("Tipo de producto no reconocido")