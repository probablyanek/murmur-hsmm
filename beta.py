import os
import shutil
from flask import Flask, request, jsonify
from helper_code import *
from team_code import load_challenge_model, run_challenge_model

app = Flask(__name__)
UPLOAD_FOLDER = 'input'
OUTPUT_FOLDER = 'output'
MODEL_FOLDER = 'models'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

valve = ["Aortic", "Pulmonary", "Tricuspid", "Mitral"]
output = ["Present", "Unknown", "Absent", "Abnormal", "Normal"]
labels = ["AV", "PV", "TV", "MV"]

def run_model(model_folder, data_folder, output_folder, allow_failures, verbose):
    model = load_challenge_model(model_folder, verbose)
    patient_files = find_patient_files(data_folder)
    num_patient_files = len(patient_files)

    if num_patient_files == 0:
        raise Exception('No data was provided.')

    os.makedirs(output_folder, exist_ok=True)

    for i in range(num_patient_files):
        patient_data = load_patient_data(patient_files[i])
        recordings = load_recordings(data_folder, patient_data)
        
        try:
            classes, labels, probabilities = run_challenge_model(model, patient_data, recordings, verbose)
        except:
            if allow_failures:
                classes, labels, probabilities = list(), list(), list()
            else:
                raise

        head, tail = os.path.split(patient_files[i])
        root, extension = os.path.splitext(tail)
        output_file = os.path.join(output_folder, root + '.csv')
        patient_id = get_patient_id(patient_data)
        save_challenge_outputs(output_file, patient_id, classes, labels, probabilities)

@app.route('/predict', methods=['POST'])
def predict():
    files = ["", "", "", ""]
    for i in range(4):
        if f'file{i}' in request.files:
            file = request.files[f'file{i}']
            if file.filename == '':
                continue

            files[i] = f'data_{labels[i]}'
            filepath = os.path.join(UPLOAD_FOLDER, f'data_{labels[i]}.wav')
            file.save(filepath)

    n = sum(1 for file in files if file)
    with open(os.path.join(UPLOAD_FOLDER, 'data.txt'), 'w') as f:
        f.write(f'data {n} 4000\n')
        for i in range(4):
            if files[i]:
                f.write(f'{labels[i]} place.hea {files[i]}.wav place.tsv\n')
        f.write(f'#Age: \n#Pregnancy status: ')

    try:
        run_model(MODEL_FOLDER, UPLOAD_FOLDER, OUTPUT_FOLDER, False, 0)
        
        with open(os.path.join(OUTPUT_FOLDER, 'data.csv'), 'r') as f:
            lines = f.readlines()
            line = lines[2].strip().split(',')

            results = {
                'Murmur': [output[x] for x in range(3) if int(line[x]) == 1],
            }
            return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
