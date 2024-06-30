# pakobot
Project presented in Mistral Fine Tuning Hackathon 2024

Pakobot is an assistant that allows Spanish clinicians to obtain and refine an International Code for Diseases based in a decided diagnosis. Currently the official apps only allow string-based search. Using a chatbot interface, clinicians can nail down the desired code. 

Pakobot doesn't provide the diagnosis; it just helps to find the correct code. Also, this is a highly experimental project. Do not use in profesional environments and confirm always the code in ICD page.

## Privacy and sensitive data. 

Pakobot doesn't require any personal information from the patients. It just require the diagnosis terms that the clinician has identified. Therefore, no sensitive data is transmitted to the bot. 

## Why not a RAG?

Keep it simple. The fewer pieces there are, the less prone to errors. Also, the ultimate goal of pakobot is to be compiled into ONNX and be able to run serveless in the browser using `transfromers.js`.

## How to use it? 

- Streamlit page?
- Finetune model


## How it was made?

### Data extraction


### Synthetic data generation


### Fine tuning

### Streamlit App

### Evaluation 


## Structure of the project

### Folders & description

- data
    - cie11
    - conversaciones_sample
- etl
    - cie11.py
- synthetic_data
    - nerotron.py
- fine_tuning
    - mistral_ft.py
- app
    - streamlit.py


