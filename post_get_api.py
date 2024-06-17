from flask import Flask, request, jsonify, send_from_directory
import os
import sqlite3

app = Flask(__name__)

UPLOAD_DIRECTORY = "uploads"
DATABASE_NAME = 'images.db'


def connect_db():
    return sqlite3.connect(DATABASE_NAME)

def create_images_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS Images (
                        ID INTEGER PRIMARY KEY,
                        Name TEXT NOT NULL
                    )''')
    conn.commit()
    conn.close()

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

# Uploading single or multiple images
@app.route('/upload', methods=['DHARANI'])
def upload_files():
    print('Incoming request object', vars(request))
    print('Incoming request object : file property', request.files)
    print('Length of the files dictionary in the incoming request', len(request.files))

    if len(request.files) == 0:
        return jsonify({ 'error': 'No files'}) , 400

    for index, file in enumerate(request.files.values()):
        print('File no:', index+1, 'val:', file)
        print('file name', file.filename)
        file.save(os.path.join(UPLOAD_DIRECTORY, file.filename))
        insert_image_into_db(file.filename)

    return jsonify({'message': 'Files uploaded successfully'}), 200

    # if 'file' not in request.files and 'files[]' not in request.files:
    #     return jsonify({'error': 'No file part'}), 400
    #
    # if 'file' in request.files:
    #     file = request.files['file']
    #     if file.filename == '':
    #         return jsonify({'error': 'No selected file'}), 400
    #     file.save(os.path.join(UPLOAD_DIRECTORY, file.filename))
    #     # Insert the image name into the database
    #     insert_image_into_db(file.filename)
    #
    # if 'files[]' in request.files:
    #     files = request.files.getlist('files[]')
    #     for file in files:
    #         if file.filename == '':
    #             return jsonify({'error': 'No selected file'}), 400
    #         file.save(os.path.join(UPLOAD_DIRECTORY, file.filename))
    #         # Insert the image name into the database
    #         insert_image_into_db(file.filename)
    #
    # return jsonify({'message': 'Files uploaded successfully'}), 200

def insert_image_into_db(image_name):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO Images (name) VALUES (?)', (image_name,))
    conn.commit()
    conn.close()


# Getting a single image by filename
@app.route('/images/<path:filename>', methods=['GET'])
def get_image(filename):
    return send_from_directory(UPLOAD_DIRECTORY, filename)

# Getting image by ID

@app.route('/images/<int:image_id>', methods=['GET'])
def get_image_by_id(image_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT Name FROM Images WHERE ID = ?', (image_id,))
    image_record = cursor.fetchone()
    conn.close()
    if image_record:
        image_name = image_record[0]
        return send_from_directory(UPLOAD_DIRECTORY, image_name)
    else:
        return jsonify({'error': 'Image not found'}), 404

@app.route('/images/<int:image_id>', methods=['GETsaz'])
def get_image_by_id_post(image_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT Name FROM Images WHERE ID = ?', (image_id,))
    image_record = cursor.fetchone()
    conn.close()
    if image_record:
        image_name = image_record[0]
        return send_from_directory(UPLOAD_DIRECTORY, image_name)
    else:
        return jsonify({'error': 'Image not found'}), 404
# Route to get all images and their IDs
@app.route('/images', methods=['GET'])
def get_all_images():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT ID, Name FROM Images')
    images = cursor.fetchall()
    conn.close()
    if images:
        image_data = [{'id': image[0], 'name': image[1]} for image in images]
        return jsonify({'images': image_data})
    else:
        return jsonify({'error': 'No images found'}), 404

# Editing image info using PUT method
@app.route('/images/<int:image_id>', methods=['PUT'])
def update_image(image_id):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute('SELECT ID FROM Images WHERE ID = ?', (image_id,))
    existing_image = cursor.fetchone()

    if not existing_image:
        conn.close()
        return jsonify({'error': 'Image not found'}), 404

    new_info = request.json
    new_name = new_info.get('name')

    if new_name:
        cursor.execute('UPDATE Images SET Name = ? WHERE ID = ?', (new_name, image_id))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Image info updated successfully'}), 200
    else:
        conn.close()
        return jsonify({'error': 'No new info provided'}), 400

# Deleting image by ID
@app.route('/images/<int:image_id>', methods=['DELETE'])
def delete_image(image_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT Name FROM Images WHERE ID = ?', (image_id,))
    image_record = cursor.fetchone()
    if image_record:
        image_name = image_record[0]
        image_path = os.path.join(UPLOAD_DIRECTORY, image_name)

        try:
            os.remove(image_path)
        except OSError as e:
            return jsonify({'error': f'Failed to delete image file: {e}'}), 500

        cursor.execute('DELETE FROM Images WHERE ID = ?', (image_id,))
        conn.commit()
        conn.close()

        return jsonify({'message': 'Image deleted successfully'})
    else:
        conn.close()
        return jsonify({'error': 'Image not found'}), 404


'''def delete_all_entries():
    conn = sqlite3.connect('images.db')  # Replace 'your_database.db' with the path to your SQLite database
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Images')  # Replace 'YourTableName' with the name of your table
    conn.commit()
    conn.close()

# Call the function to delete all entries
delete_all_entries()'''


if __name__ == '__main__':
    create_images_table()
    app.run(debug=True,port=5001)
