// URL base del servidor Flask (usa el mismo puerto y host)
const API_URL = window.location.origin || 'http://localhost:5000';

// Función para agregar logs de depuración
function log(message) {
    const debugLog = document.getElementById('debug-log');
    const logEntry = document.createElement('div');
    logEntry.textContent = message;
    debugLog.appendChild(logEntry);
    debugLog.scrollTop = debugLog.scrollHeight;
}

// Mostrar/ocultar logs
function toggleDebug() {
    const debugLog = document.getElementById('debug-log');
    debugLog.style.display = debugLog.style.display === 'none' ? 'block' : 'none';
}

// ============================================
// FUNCIONES PARA MOSTRAR MENSAJES
// ============================================
function showMessage(message, isSuccess) {
    const messageDiv = document.getElementById('message');
    messageDiv.textContent = message;
    messageDiv.className = `message ${isSuccess ? 'success' : 'error'}`;
    messageDiv.style.display = 'block';

    setTimeout(() => {
        messageDiv.style.display = 'none';
    }, 3000);
}

// ============================================
// FUNCIONES PARA CARGAR Y RENDERIZAR ÍTEMS
// ============================================

// Cargar todos los ítems desde el servidor
async function loadItems() {
    log(`Cargando ítems desde ${API_URL}/items`);
    try {
        const response = await fetch(`${API_URL}/items`);
        log(`Respuesta del servidor: ${response.status} ${response.statusText}`);

        if (!response.ok) {
            throw new Error('Error al cargar los ítems: ' + response.statusText);
        }

        const items = await response.json();
        log(`Ítems recibidos: ${JSON.stringify(items)}`);
        renderItems(items);
    } catch (error) {
        log(`Error al cargar ítems: ${error.message}`);
        showMessage('Error al cargar los ítems: ' + error.message, false);
        console.error('Error:', error);
    }
}

// Renderizar los ítems en la tabla
function renderItems(items) {
    const itemsList = document.getElementById('items-list');
    itemsList.innerHTML = '';

    if (items.length === 0) {
        itemsList.innerHTML = '<tr><td colspan="4" class="no-items">No hay ítems registrados. ¡Crea uno nuevo!</td></tr>';
        return;
    }

    items.forEach(item => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${item.id}</td>
            <td>${escapeHtml(item.nombre)}</td>
            <td>${escapeHtml(item.descripcion)}</td>
            <td class="action-buttons">
                <button class="btn-success" onclick="editItem(${item.id})">✏️ Editar</button>
                <button class="btn-danger" onclick="deleteItem(${item.id})">🗑️ Eliminar</button>
            </td>
        `;
        itemsList.appendChild(row);
    });
}

// Función para escapar HTML y evitar XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ============================================
// FUNCIONES PARA OPERACIONES CRUD
// ============================================

// Crear un nuevo ítem
async function createItem(item) {
    log(`Creando ítem: ${JSON.stringify(item)}`);
    try {
        const response = await fetch(`${API_URL}/items`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(item),
        });

        log(`Respuesta del servidor: ${response.status} ${response.statusText}`);

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Error al crear el ítem');
        }

        const newItem = await response.json();
        log(`Ítem creado: ${JSON.stringify(newItem)}`);
        showMessage(`✅ Ítem "${newItem.nombre}" creado correctamente`, true);

        // Recargar la tabla después de crear
        await loadItems();
        resetForm();
    } catch (error) {
        log(`Error al crear ítem: ${error.message}`);
        showMessage('❌ Error al crear el ítem: ' + error.message, false);
        console.error('Error:', error);
    }
}

// Obtener un ítem por su ID
async function getItem(itemId) {
    log(`Obteniendo ítem con ID ${itemId}`);
    try {
        const response = await fetch(`${API_URL}/items/${itemId}`);
        log(`Respuesta del servidor: ${response.status} ${response.statusText}`);

        if (!response.ok) {
            throw new Error('Error al obtener el ítem');
        }

        const item = await response.json();
        log(`Ítem obtenido: ${JSON.stringify(item)}`);
        return item;
    } catch (error) {
        log(`Error al obtener ítem: ${error.message}`);
        showMessage('❌ Error al obtener el ítem: ' + error.message, false);
        console.error('Error:', error);
        return null;
    }
}

// Actualizar un ítem
async function updateItem(itemId, item) {
    log(`Actualizando ítem con ID ${itemId}: ${JSON.stringify(item)}`);
    try {
        const response = await fetch(`${API_URL}/items/${itemId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(item),
        });

        log(`Respuesta del servidor: ${response.status} ${response.statusText}`);

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Error al actualizar el ítem');
        }

        const updatedItem = await response.json();
        log(`Ítem actualizado: ${JSON.stringify(updatedItem)}`);
        showMessage(`✅ Ítem "${updatedItem.nombre}" actualizado correctamente`, true);

        // Recargar la tabla después de actualizar
        await loadItems();
        resetForm();
    } catch (error) {
        log(`Error al actualizar ítem: ${error.message}`);
        showMessage('❌ Error al actualizar el ítem: ' + error.message, false);
        console.error('Error:', error);
    }
}

// Eliminar un ítem
async function deleteItem(itemId) {
    log(`Eliminando ítem con ID ${itemId}`);
    if (!confirm('¿Estás seguro de que quieres eliminar este ítem? Esta acción no se puede deshacer.')) {
        log('Eliminación cancelada por el usuario');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/items/${itemId}`, {
            method: 'DELETE',
        });

        log(`Respuesta del servidor: ${response.status} ${response.statusText}`);

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Error al eliminar el ítem');
        }

        showMessage('✅ Ítem eliminado correctamente', true);

        // Recargar la tabla después de eliminar
        await loadItems();
    } catch (error) {
        log(`Error al eliminar ítem: ${error.message}`);
        showMessage('❌ Error al eliminar el ítem: ' + error.message, false);
        console.error('Error:', error);
    }
}

// ============================================
// FUNCIONES PARA MANEJAR EL FORMULARIO
// ============================================

// Cargar los datos de un ítem en el formulario para editar
async function editItem(itemId) {
    log(`Editando ítem con ID ${itemId}`);
    const item = await getItem(itemId);
    if (item) {
        document.getElementById('item-id').value = item.id;
        document.getElementById('nombre').value = item.nombre;
        document.getElementById('descripcion').value = item.descripcion;
        document.getElementById('form-title').textContent = '✏️ Editar Ítem';
        document.getElementById('submit-btn').textContent = '🔄 Actualizar';
        document.getElementById('cancel-btn').style.display = 'inline-block';
    }
}

// Resetear el formulario
function resetForm() {
    log('Reseteando formulario');
    document.getElementById('item-form').reset();
    document.getElementById('item-id').value = '';
    document.getElementById('form-title').textContent = '➕ Crear Nuevo Ítem';
    document.getElementById('submit-btn').textContent = '💾 Guardar';
    document.getElementById('cancel-btn').style.display = 'none';
}

// ============================================
// EVENT LISTENERS
// ============================================

// Manejar el envío del formulario (Crear o Actualizar)
document.getElementById('item-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const itemId = document.getElementById('item-id').value;
    const nombre = document.getElementById('nombre').value.trim();
    const descripcion = document.getElementById('descripcion').value.trim();

    log(`Formulario enviado - ID: ${itemId}, Nombre: ${nombre}, Descripción: ${descripcion}`);

    if (!nombre || !descripcion) {
        showMessage('❌ Por favor, completa todos los campos.', false);
        return;
    }

    const item = { nombre, descripcion };

    if (itemId) {
        await updateItem(itemId, item);
    } else {
        await createItem(item);
    }
});

// Manejar el botón de cancelar
document.getElementById('cancel-btn').addEventListener('click', resetForm);

// ============================================
// INICIALIZACIÓN
// ============================================

// Cargar los ítems al iniciar la página
document.addEventListener('DOMContentLoaded', () => {
    log('Página cargada. Cargando ítems...');
    loadItems();
});