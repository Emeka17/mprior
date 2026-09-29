from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tiles.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Tile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    brand_name = db.Column(db.String(100), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    finish = db.Column(db.String(50), nullable=False)
    use = db.Column(db.String(50), nullable=False)
    size = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(100), nullable=True)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    tiles = Tile.query.all()
    return render_template('index.html', tiles=tiles)

@app.route('/a')
def old_admin_redirect():
    return redirect(url_for('admin'))

@app.route('/admin')
def admin():
    tiles = Tile.query.all()
    return render_template('admin.html', tiles=tiles)

@app.route('/admin/add', methods=['POST'])
def add_tile():
    brand_name = request.form.get('brand_name')
    name = request.form.get('name')
    finish = request.form.get('finish')
    use = request.form.get('use')
    size = request.form.get('size')
    price_val = request.form.get('price')
    file = request.files.get('image')

    price = float(price_val) if price_val else 0.0
    image_filename = ''

    if file and file.filename != '':
        image_filename = file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

    new_tile = Tile(
        brand_name=brand_name,
        name=name,
        finish=finish,
        use=use,
        size=size,
        price=price,
        image=image_filename
    )
    db.session.add(new_tile)
    db.session.commit()
    return redirect(url_for('admin'))

@app.route('/admin/delete/<int:id>')
def delete_tile(id):
    tile = Tile.query.get_or_404(id)
    db.session.delete(tile)
    db.session.commit()
    return redirect(url_for('admin'))

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)

import cloudinary.uploader

@app.route('/upload', methods=['POST'])
def upload_image():
    file = request.files.get('file')
    if file:
        result = cloudinary.uploader.upload(file)
        return result['secure_url']
    return 'No file uploaded', 400
