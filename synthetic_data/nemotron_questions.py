# DATA
import os
import pandas as pd
from openai import OpenAI
import json

# Get the path to the directory containing the files.
ICD_FOLDER = "./data/cie11/"
OUTPUT_FOLDER = "./data/questions"
os.mkdir(OUTPUT_FOLDER, exist_ok=True)

# Get a list of all the files in the directory.
files = os.listdir(ICD_FOLDER)

# LLM
question_string = """
INSTRUCCIONES: Eres un gestor médico experto y tu tarea es asesorar a los médicos
y hacer su trabajo más fácil. Los médicos te hacen consultas sobre el código CIE
de diferentes enfermedades y tu les dices qué código es.
Recuerda que cada médico es diferente y tiene su propio vocabulario, también
tienen formas diferentes de plantear la pregunta y diferentes tonos, también diferentes estructuras.
No todos los médicos preguntan de la misma manera, es más, a veces son muy breves porque no tienen tiempo
y otras veces se extienden más. No siempre usan signos de interrogación y no siempre
hacen una afirmación y pregunta al final. Los médicos no tienen tiempo muchas veces,
eso quiere decir que no dedican tiempo a hacer la pregunta de la mejor manera posible.
Y cómo ya saben que tu función es la de proporcionar estos códigos, a veces no te hacen
ni la pregunta, simplemente te dan la información de la enfermedad y tu les das el código.
Evitan decir muchas veces "¿Cuál es el código...?" y también evitan decir "¿Me podrías dar el código...?
Te doy algunos ejemplos porque eres un poco limitadillo y así puedes inspirarte (OJO! Que no copiar ehh tontorrón): Dime el CIE de una proliferación celular anormal.
Búscame el CIE del crecimiento celular incontrolado.
Necesito el CIE de la proliferación celular no coordinada.
Encuéntrame el CIE de la proliferación anormal de células.
Localízame el CIE del reemplazo de tejido anormal.
Dime el CIE de la proliferación celular incontrolada.
Háblame del CIE de la proliferación celular anormal.
No encuentro el CIE del crecimiento celular no regulado.
¿Cuál es el CIE del reemplazo celular no normal?
Dime el CIE de la proliferación incontrolada de células.
Necesito el CIE del crecimiento anormal de células.
Búscame el CIE de la proliferación celular fuera de control.
Encuéntrame el CIE de una proliferación no coordinada con el organismo.
¿Cuál es el CIE del crecimiento celular descontrolado?
¿Cuál es el CIE de la reparación de tejido anormal?
No encuentro el CIE de la proliferación celular no regulada.
¿Cuál es el CIE de la proliferación no coordinada?
Dime el CIE del tejido de reemplazo anormal.
Localízame el CIE del crecimiento celular anormal.
Necesito el CIE de la proliferación fuera de control.
Ahora quiero que tu me des SOLO UNA lista sin NUMERAR EN MARKDOWN de 10 preguntas o inputs en español que recibes de estos
médicos sobre esta información:

""" 

def generate_output(information, client):
  completion = client.chat.completions.create(
    model="nvidia/nemotron-4-340b-instruct",
    messages=[{"role":"user","content":question_string + information}],
    temperature=1,
    top_p=0.85,
    max_tokens=1024,
    stream=False
  )

  response = completion.choices[0].dict()['message']["content"]
  return response

def save_output(output, name):
  with open(f'{OUTPUT_FOLDER}/{name}.jsonl', 'w') as f:
    for line in output.splitlines():
      f.write(json.dumps({'text': line.replace("- ","")}) + '\n')

# Generation
files = os.listdir(ICD_FOLDER)

for file in files:
  df = pd.read_json(ICD_FOLDER+ '/' + file, orient='records', lines=True)

  client = OpenAI(
    base_url = "https://integrate.api.nvidia.com/v1",
    api_key = os.getenv("NVIDIA_API_KEY")
  )

  for ii,i in df.iterrows():
    name = file.split('.')[0] + '_' + str(ii)
    if os.path.exists(f'{OUTPUT_FOLDER}/{name}.jsonl'):
      print(name + " exists.")
    else:
      parents = eval(i['parents_human'])
      if len(parents) > 0:
        parent = str(parents[0][1])
      else:
        parent = "None"

      synonyms = ", ".join(eval(i['synonyms']))

      information = "TITLE: " + i['title'] + ". DEFINITION: " + i['definition'] + ". SYNONYMS: " + synonyms + ". PARENT: " + parent #+ ". CHILDREN: " + children
      output = generate_output(information, client)
      #print(output)

      save_output(output, name)
      print(name)