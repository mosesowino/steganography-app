from flask import Flask, send_file, request, redirect, url_for
from flask import render_template
from PIL import Image
from pydub import AudioSegment
import io
import numpy as np
import cv2
import wave
import os
from operations import general_operations, processImage, processAudio
from werkzeug.utils import secure_filename, redirect


app = Flask(__name__)
# msg = None

def file_typeSpecificEncoding (file_type: str, message, filename):
    match file_type:
        case "audio":
            return encode_audio(message, filename)
        case "image":
            return encode_image(message, filename)
        case "video":
            return encode_video(message, filename)
        case _:
            return "Unsupported file type"

def file_typeSpecificDecoding(file_type, filename):
        match file_type:
            case "audio":
                return decode_audio(filename)
            case "image":
                return decode_image(filename)
            case "video":
                return decode_video(filename)
            case _:
                return "Unsupported file type"
                
        
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == "GET":
        return render_template('index.html')
        
    elif request.method == "POST":
        # data = request.form.get("secret_message")
        FILE_KEY = "file_to_encode"
        try:
            secret_message = request.form["secret_message"]
        except:
            encode = False
            FILE_KEY = "file_to_decode"
        else:
            encode = True
            
        file = request.files[FILE_KEY]
        filename = secure_filename(file.filename)
        filepath = os.path.join('uploaded_files', filename)
        # file.save('uploaded_files/' + file.filename)
        file.save(filepath)
        
        
        file_type: str = general_operations.determineFileType(filename)
        
        if encode:
            encoding_response =  file_typeSpecificEncoding(file_type, secret_message, filepath)
            if isinstance(encoding_response, str):
                if encoding_response.startswith("Unsupported"):
                    return encoding_response
                else:
                    return send_file(encoding_response, as_attachment=True)
            else:

                return "An error occurred, please try again."
            
            
        else:
            try:
                decoding_response =  file_typeSpecificDecoding(file_type, filepath)
            except ValueError:
                decoding_response = "No Message Found !"
           
            global msg 
            msg = decoding_response
            
            return render_template('index.html',message=msg)
            
    else:
        return redirect(url_for('home')) 



@app.route('/about', methods=['POST','GET'])
def about():
    return render_template('about.html')

def encode_image(message, filename):

    encoded_img = processImage.encode_img_data(filename, message)

    
    return os.path.abspath(encoded_img)
    
    
    
def decode_image(filename):
    decoded_message = processImage.decode_img_data(filename)
    
    return decoded_message



def encode_audio(message, filepath):
    audio_extension = general_operations.determineMediaType(filepath)
    if 'mp3' in audio_extension:
        general_operations.Mp3ToWav(filepath)
        
    audio = AudioSegment.from_file(filepath, format='wav')
    encoded_audio_file = processAudio.encode_aud_data(audio, message)

    output_path = 'downloads/encoded_audio.wav'
    
    encoded_audio_file.export(output_path, format="wav")

    return output_path



def decode_audio(filepath):
    file = AudioSegment.from_file(filepath, format='wav')
    decoded_message = processAudio.decode_aud_data(file)
    return decoded_message




if __name__ == '__main__':
    app.run(debug=True)