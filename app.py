from flask import Flask, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
import os
import subprocess


app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp3', 'wav'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def execute_command(png_name,audio_name):
    command = 'python /data/SadTalker/inference.py --driven_audio /data/SadTalker/uploads/%s --source_image /data/SadTalker/uploads/%s --enhancer gfpgan'%(png_name,audio_name)

    try:
        result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        return f"Command executed successfully. Output: {result.decode('utf-8')}"
    except subprocess.CalledProcessError as e:
        return f"Error executing command. Output: {e.output.decode('utf-8')}"

def run_script(png_name,audio_name):
    try:
        output = subprocess.check_output(['python', '/data/SadTalker/inference.py --driven_audio /data/SadTalker/uploads/%s --source_image /data/SadTalker/uploads/%s --enhancer gfpgan'%(audio_name,png_name)])
        return output
    except subprocess.CalledProcessError as e:
        return str(e)


import re

def extract_last_mp4(text):
    pattern = r'\./results/(.*\.mp4)'
    matches = re.findall(pattern, text)
    
    if matches:
        return matches[-1]
    else:
        return None

from flask import Flask, send_from_directory


@app.route('/video/<filename>')
def get_video(filename):
    return send_from_directory('results', filename)


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        sound_file = request.files['sound']
        image_file = request.files['image']
        
        if sound_file and allowed_file(sound_file.filename):
            sound_filename = secure_filename(sound_file.filename)
            sound_file.save(os.path.join(app.config['UPLOAD_FOLDER'], sound_filename))
            
        if image_file and allowed_file(image_file.filename):
            image_filename = secure_filename(image_file.filename)
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

        print("start")
        
        #return redirect(url_for('upload_file'))
        result = execute_command(image_filename,sound_filename)
        print(result)

        r = extract_last_mp4(result)
        print(r)
        return redirect(url_for('get_video', filename=r))

        #return """<a href="%s">生成结果</a>"""%(r)
    
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8000,debug=True)
