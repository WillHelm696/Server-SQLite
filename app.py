from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS  # Importar CORS
import os

# Obtener el directorio actual del script
basedir = os.path.abspath(os.path.dirname(__file__))

# Configuración de la aplicación Flask
app = Flask(__name__)

# Habilitar CORS para todas las rutas (permite solicitudes desde el navegador)
CORS(app)

# Configurar la base de datos SQLite en el directorio raíz del proyecto
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'items.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicialización de SQLAlchemy
db = SQLAlchemy(app)


# Modelo de la tabla Item
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(200), nullable=False)

    def to_dict(self):
        return {"id": self.id, "nombre": self.nombre, "descripcion": self.descripcion}


# Crear la base de datos y la tabla al iniciar la aplicación
with app.app_context():
    db.create_all()


# Rutas para las operaciones CRUD

# Crear un nuevo elemento (POST)
@app.route('/items', methods=['POST'])
def create_item():
    print("Recibida solicitud POST en /items")  # Log para depuración
    data = request.get_json()
    print(f"Datos recibidos: {data}")  # Log para depuración

    if not data or 'nombre' not in data or 'descripcion' not in data:
        print("Error: Faltan campos obligatorios")  # Log para depuración
        return jsonify({"error": "Faltan campos obligatorios: nombre y descripción"}), 400

    try:
        new_item = Item(nombre=data['nombre'], descripcion=data['descripcion'])
        db.session.add(new_item)
        db.session.commit()
        print(f"Ítem creado: {new_item.to_dict()}")  # Log para depuración
        return jsonify(new_item.to_dict()), 201
    except Exception as e:
        print(f"Error al crear el ítem: {e}")  # Log para depuración
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# Obtener todos los elementos (GET)
@app.route('/items', methods=['GET'])
def get_items():
    print("Recibida solicitud GET en /items")  # Log para depuración
    items = Item.query.all()
    print(f"Ítems obtenidos: {[item.to_dict() for item in items]}")  # Log para depuración
    return jsonify([item.to_dict() for item in items])


# Obtener un elemento por su ID (GET)
@app.route('/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    print(f"Recibida solicitud GET en /items/{item_id}")  # Log para depuración
    item = Item.query.get(item_id)
    if not item:
        print(f"Error: Ítem con ID {item_id} no encontrado")  # Log para depuración
        return jsonify({"error": "Elemento no encontrado"}), 404
    return jsonify(item.to_dict())


# Actualizar un elemento (PUT)
@app.route('/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    print(f"Recibida solicitud PUT en /items/{item_id}")  # Log para depuración
    item = Item.query.get(item_id)
    if not item:
        print(f"Error: Ítem con ID {item_id} no encontrado")  # Log para depuración
        return jsonify({"error": "Elemento no encontrado"}), 404

    data = request.get_json()
    print(f"Datos recibidos para actualizar: {data}")  # Log para depuración

    if 'nombre' in data:
        item.nombre = data['nombre']
    if 'descripcion' in data:
        item.descripcion = data['descripcion']

    try:
        db.session.commit()
        print(f"Ítem actualizado: {item.to_dict()}")  # Log para depuración
        return jsonify(item.to_dict())
    except Exception as e:
        print(f"Error al actualizar el ítem: {e}")  # Log para depuración
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# Eliminar un elemento (DELETE)
@app.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    print(f"Recibida solicitud DELETE en /items/{item_id}")  # Log para depuración
    item = Item.query.get(item_id)
    if not item:
        print(f"Error: Ítem con ID {item_id} no encontrado")  # Log para depuración
        return jsonify({"error": "Elemento no encontrado"}), 404

    try:
        db.session.delete(item)
        db.session.commit()
        print(f"Ítem con ID {item_id} eliminado")  # Log para depuración
        return jsonify({"message": "Elemento eliminado correctamente"}), 200
    except Exception as e:
        print(f"Error al eliminar el ítem: {e}")  # Log para depuración
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# Ruta para servir la página interactiva
@app.route('/')
def index():
    return render_template('index.html')


# Iniciar el servidor
if __name__ == '__main__':
    app.run(debug=True)