import streamlit as st
import shutil
import os
import numpy as np, os, sys
from helper_code import *
from team_code import load_challenge_model, run_challenge_model


# Initialize a list with 4 empty strings to hold the file paths
files = ["", "", "", ""]
valve = ["Aortic", "Pulmonary", "Tricuspid", "Mitral"]
output = ["Present","Unknown","Absent","Abnormal","Normal"]
labels = ["AV", "PV", "TV", "MV"]
model_folder = "./models"
data_folder = "./input"
output_folder = "./output"

# Create 2x2 grid for file uploaders
def run_model(model_folder, data_folder, output_folder, allow_failures, verbose):
    # Load models.
    if verbose >= 1:
        print('Loading Challenge model...')

    model = load_challenge_model(model_folder, verbose) ### Teams: Implement this function!!!

    # Find the patient data files.
    patient_files = find_patient_files(data_folder)
    num_patient_files = len(patient_files)

    if num_patient_files==0:
        raise Exception('No data was provided.')

    # Create a folder for the Challenge outputs if it does not already exist.
    os.makedirs(output_folder, exist_ok=True)

    # Run the team's model on the Challenge data.
    if verbose >= 1:
        print('Running model on Challenge data...')

    # Iterate over the patient files.
    for i in range(num_patient_files):
        if verbose >= 2:
            print('    {}/{}...'.format(i+1, num_patient_files))

        patient_data = load_patient_data(patient_files[i])
        recordings = load_recordings(data_folder, patient_data)

        # Allow or disallow the model to fail on parts of the data; helpful for debugging.
        try:
            classes, labels, probabilities = run_challenge_model(model, patient_data, recordings, verbose) ### Teams: Implement this function!!!
        except:
            if allow_failures:
                if verbose >= 2:
                    print('... failed.')
                classes, labels, probabilities = list(), list(), list()
            else:
                raise

        # Save Challenge outputs.
        head, tail = os.path.split(patient_files[i])
        root, extension = os.path.splitext(tail)
        output_file = os.path.join(output_folder, root + '.csv')
        patient_id = get_patient_id(patient_data)
        save_challenge_outputs(output_file, patient_id, classes, labels, probabilities)

    print('Done.')


def runMain():
    n = 0
    for i in range(4):
        if files[i] != "":
            n += 1    
    print(n)
    with open('.//input//data.txt', 'w') as f:
        f.write(f'data {n} 4000\n')
        for i in range(4):
            if files[i] != "":
                f.write(f'{labels[i]} place.hea {files[i]}.wav place.tsv\n')
                
        f.write(f'#Age: \n#Pregnancy status: ')

    run_model(model_folder, data_folder, output_folder, False, 0)
    # open output/data.csv then readlines and split second line at ","
    with open('.//output//data.csv', 'r') as f:
        
        try:
            lines = f.readlines()
            line = lines[2].strip().split(',')
            for x in range(0,3):
                if int(line[x]) == 1:
                    st.write(f'Murmur : {output[x]}')
                    
            for x in range(3,5):
                if int(line[x]) == 1:
                    st.write(f'Clinical outcome : {output[x]}')
                    
        except Exception as e:
            print(e)
            while True:
                try:
                    eval(input(">>>"))
                except Exception as e:
                    print(e)
                    continue


for i in range(2):
    cols = st.columns(2)
    for j in range(2):
        index = 2*i+j
        uploaded_file = cols[j].file_uploader(f"{valve[index]} Valve", type=['wav'])
        if uploaded_file is not None:
            # Save the file path to the specific index in the list
            files[index] = f'data_{labels[index]}'

            # Create the 'input' directory if it does not exist
            if not os.path.exists('.\\input'):
                os.makedirs('.\\input')

            # Create a new file in the 'input' directory with the name 'data_{label}'
            with open(f'.\\input\\data_{labels[index]}.wav', 'wb') as out_file:
                # Copy the contents of the uploaded file to the new file
                shutil.copyfileobj(uploaded_file, out_file)                # Add a custom check button underneath the file upload grid
st.markdown('<style>div.row-widget.stButton>button{width:200px;height:100px;font-size:20px;}</style>', unsafe_allow_html=True)

cols = st.columns([1,1,1])
if cols[1].button('Check'):
    runMain()  # Call the function when the button is pressed