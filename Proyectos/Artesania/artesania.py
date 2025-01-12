from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Lista de productos de artesanía
productos = [
    {'id': 1, 'nombre': 'Cuenco de Cerámica', 'precio': 25},
    {'id': 2, 'nombre': 'Jarrón de Vidrio', 'precio': 40},
    {'id': 3, 'nombre': 'Cesto de Mimbre', 'precio': 30}
]

@app.route('/')
def tienda():
    return render_template('tienda.html', productos=productos)

@app.route('/producto/<int:producto_id>')
def producto(producto_id):
    producto = next((p for p in productos if p['id'] == producto_id), None)
    if producto:
        return render_template('producto.html', producto=producto)
    return 'Producto no encontrado', 404

@app.route('/comprar/<int:producto_id>', methods=['POST'])
def comprar(producto_id):
    producto = next((p for p in productos if p['id'] == producto_id), None)
    if producto:
        # Aquí iría el código para procesar la compra
        return redirect(url_for('tienda'))
    return 'Producto no encontrado', 404

if __name__ == '__main__':
    app.run(debug=True)