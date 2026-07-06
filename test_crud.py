from flask_sqlalchemy import SQLAlchemy
from flask import Flask
import os

# Configuración mínima de Flask para usar SQLAlchemy
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'items.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar SQLAlchemy
db = SQLAlchemy(app)


# Modelo de la tabla Item (debe coincidir con app.py)
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(200), nullable=False)

    def to_dict(self):
        return {"id": self.id, "nombre": self.nombre, "descripcion": self.descripcion}


# ============================================
# FUNCIONES PARA OPERACIONES CRUD (LOCAL)
# ============================================

def crear_item(nombre, descripcion):
    """Crea un nuevo ítem en la base de datos."""
    with app.app_context():
        new_item = Item(nombre=nombre, descripcion=descripcion)
        db.session.add(new_item)
        db.session.commit()
        print(f"✅ Ítem creado: ID={new_item.id}, Nombre='{new_item.nombre}'")
        return new_item


def obtener_todos_los_items():
    """Obtiene todos los ítems de la base de datos."""
    with app.app_context():
        items = Item.query.all()
        return [item.to_dict() for item in items]


def obtener_item_por_id(item_id):
    """Obtiene un ítem por su ID."""
    with app.app_context():
        item = Item.query.get(item_id)
        return item.to_dict() if item else None


def actualizar_item(item_id, nombre=None, descripcion=None):
    """Actualiza un ítem existente."""
    with app.app_context():
        item = Item.query.get(item_id)
        if not item:
            print(f"❌ Error: No se encontró el ítem con ID {item_id}")
            return False

        if nombre:
            item.nombre = nombre
        if descripcion:
            item.descripcion = descripcion

        db.session.commit()
        print(f"✅ Ítem actualizado: ID={item.id}, Nombre='{item.nombre}'")
        return True


def eliminar_item(item_id):
    """Elimina un ítem por su ID."""
    with app.app_context():
        item = Item.query.get(item_id)
        if not item:
            print(f"❌ Error: No se encontró el ítem con ID {item_id}")
            return False

        db.session.delete(item)
        db.session.commit()
        print(f"✅ Ítem eliminado: ID={item_id}")
        return True


# ============================================
# FUNCIÓN PARA MOSTRAR LA TABLA EN CONSOLA
# ============================================

def mostrar_tabla(items):
    """Muestra los ítems en formato de tabla en la consola."""
    if not items:
        print("\n📊 Tabla de Ítems: (vacía)")
        return

    print("\n📊 Tabla de Ítems:")
    print("-" * 80)
    print(f"{'ID':<5} | {'Nombre':<20} | {'Descripción':<40}")
    print("-" * 80)
    for item in items:
        # Truncar descripción si es muy larga
        desc = item['descripcion'][:37] + "..." if len(item['descripcion']) > 40 else item['descripcion']
        print(f"{item['id']:<5} | {item['nombre']:<20} | {desc:<40}")
    print("-" * 80)


# ============================================
# MENÚ INTERACTIVO
# ============================================

def menu():
    """Menú interactivo para probar las operaciones CRUD."""
    while True:
        print("\n" + "=" * 50)
        print("📌 MENÚ INTERACTIVO - PRUEBAS CRUD")
        print("=" * 50)
        print("1. 📝 Crear nuevo ítem")
        print("2. 📊 Mostrar todos los ítems")
        print("3. 🔍 Buscar ítem por ID")
        print("4. ✏️ Actualizar ítem")
        print("5. 🗑️ Eliminar ítem")
        print("6. 🚪 Salir")
        print("=" * 50)

        opcion = input("Selecciona una opción (1-6): ").strip()

        if opcion == '1':
            # Crear ítem
            print("\n📝 CREAR NUEVO ÍTEM")
            nombre = input("Nombre: ").strip()
            descripcion = input("Descripción: ").strip()
            if nombre and descripcion:
                crear_item(nombre, descripcion)
            else:
                print("❌ Error: Nombre y descripción son obligatorios.")

        elif opcion == '2':
            # Mostrar todos los ítems
            items = obtener_todos_los_items()
            mostrar_tabla(items)

        elif opcion == '3':
            # Buscar ítem por ID
            print("\n🔍 BUSCAR ÍTEM POR ID")
            try:
                item_id = int(input("ID del ítem: "))
                item = obtener_item_por_id(item_id)
                if item:
                    print(f"\n📌 Ítem encontrado:")
                    print(f"ID: {item['id']}")
                    print(f"Nombre: {item['nombre']}")
                    print(f"Descripción: {item['descripcion']}")
                else:
                    print(f"❌ No se encontró ningún ítem con ID {item_id}")
            except ValueError:
                print("❌ Error: El ID debe ser un número entero.")

        elif opcion == '4':
            # Actualizar ítem
            print("\n✏️ ACTUALIZAR ÍTEM")
            try:
                item_id = int(input("ID del ítem a actualizar: "))
                item = obtener_item_por_id(item_id)
                if item:
                    print(f"📌 Ítem actual: Nombre='{item['nombre']}', Descripción='{item['descripcion']}'")
                    nombre = input("Nuevo nombre (dejar vacío para no cambiar): ").strip()
                    descripcion = input("Nueva descripción (dejar vacío para no cambiar): ").strip()

                    # Solo actualizar si se proporcionó un valor
                    nuevo_nombre = nombre if nombre else None
                    nueva_descripcion = descripcion if descripcion else None

                    actualizar_item(item_id, nuevo_nombre, nueva_descripcion)
                else:
                    print(f"❌ No se encontró ningún ítem con ID {item_id}")
            except ValueError:
                print("❌ Error: El ID debe ser un número entero.")

        elif opcion == '5':
            # Eliminar ítem
            print("\n🗑️ ELIMINAR ÍTEM")
            try:
                item_id = int(input("ID del ítem a eliminar: "))
                confirmar = input(f"¿Estás seguro de eliminar el ítem con ID {item_id}? (s/n): ").strip().lower()
                if confirmar == 's':
                    eliminar_item(item_id)
                else:
                    print("❌ Operación cancelada.")
            except ValueError:
                print("❌ Error: El ID debe ser un número entero.")

        elif opcion == '6':
            # Salir
            print("\n👋 Saliendo del menú... ¡Hasta luego!")
            break

        else:
            print("❌ Opción no válida. Por favor, selecciona una opción del 1 al 6.")


# ============================================
# INICIO DEL PROGRAMA
# ============================================

if __name__ == '__main__':
    print("🚀 Iniciando menú interactivo para pruebas CRUD...")
    print("📁 Base de datos: items.db (en el directorio actual)")
    menu()