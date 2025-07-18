from flask import Flask, render_template, request, jsonify,send_file
import firebase_admin
from firebase_admin import credentials, storage

# Initialize Flask app
app = Flask(__name__)

# Initialize Firebase app
cred = credentials.Certificate("emergencybooking-31043-firebase-adminsdk-l69k0-98c85bc3f2.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': 'emergencybooking-31043.appspot.com'
})
bucket = storage.bucket()


@app.route('/')
def index():
    return render_template('upload.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    # Upload file to Firebase Storage
    blob = bucket.blob(file.filename)
    blob.upload_from_file(file)

    # Construct download URL
    download_url = f"/download/{file.filename}"

    # Redirect to download.html after successful upload
    return render_template('download.html', success_message="File uploaded successfully!", download_url=download_url)


@app.route('/download/<filename>')
def download_file(filename):
    # Download the file from Firebase Storage and serve as attachment
    blob = bucket.blob(filename)
    file_stream = blob.download_as_bytes()
    return send_file(
        file_stream,
        mimetype='application/octet-stream',
        as_attachment=True
    )


if __name__ == '__main__':
    app.run(debug=True)
