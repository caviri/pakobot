from openai import OpenAI
import json
import os
import pandas as pd

ICD_FOLDER = "./data/cie11"
QUESTIONS_FOLDER = "./data/questions"
OUTPUT_FOLDER = "./data/conversations"
os.mkdir(OUTPUT_FOLDER, exist_ok=True)

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

Aqui tienes un ejemplo de conversación entre un asistente y un usuario.

- Usuario
Cúal es el código CIE para la varicela?
- Asistente
Varicela 1E90. \n El código para la varicela es 1E90. Pero ten en cuenta que hay categorías hijas: como \n - 1E90.0 Varicela sin complicaciones \n - 1E90.1 Meningitis por varicela \n - 1E90.2 Encefalitis por varicela. \n ¿Quieres saber más de estás categorías o de la descripción de la varicela? \n

Ahora quiero que tu me des UN EJEMPLO DE CONVERSACION entre un asistente y un usuario o inputs en español en ese formato.

Este es el contexto:

{{INFORMATION}}

Esta es la pregunta que recibes de estos médicos sobre esta información. Completa la respuesta. Puedes usar markdown.

- Usuario
{{QUESTION}}
- Asistente
""" 


def generate_output(prompt, client):

  completion = client.chat.completions.create(
    model="nvidia/nemotron-4-340b-instruct",
    messages=[{"role":"user","content": prompt}],
    temperature=1,
    top_p=0.85,
    max_tokens=1024,
    stream=False
  )

  response = completion.choices[0].dict()['message']["content"]
  return response


# Generation

data_dir = QUESTIONS_FOLDER

# Get a list of all files in the directory
files = os.listdir(data_dir)


for file in files:
  client = OpenAI(
    base_url = "https://integrate.api.nvidia.com/v1",
    api_key = os.getenv("NVIDIA_API_KEY")
    )
  output_path = OUTPUT_FOLDER + file.split('.')[0] + ".jsonl"
  if not os.path.exists(output_path):
    try:
        file_name_parts = file.split("_")

        # Get the other filename and index
        cie_filename = file_name_parts[0]
        index = int(file_name_parts[1].split('.')[0])
        print(cie_filename)
        # Load the other file into a dataframe
        dfcie11 = pd.read_json(ICD_FOLDER + cie_filename + ".json", orient='records', lines=True)

        # Get the context for the index
        i = dfcie11.loc[index]

        parents = eval(i['parents_human'])
        if len(parents) > 0:
          parent = str(parents[0][1])
        else:
          parent = "None"

        children = eval(i['children_human'])
        if len(children) > 0:
          children = ", ".join([c[1] + " code " + c[0] for c in children])
        else:
          children = "None"

        synonyms = ", ".join(eval(i['synonyms']))

        information = "Título: " + i['title'] + " Código: " + i['cie-code'] + ". Definición: " + i['definition'] + ". Sinónimos: " + synonyms + ". Categoría padre: " + parent + ". Categorías hijas: " + children

        with open(output_path, 'a', encoding='utf-8') as outfile:
          with open(os.path.join(data_dir, file), "r") as f:
              for n, line in enumerate(f):
                # Parse the JSONL line
                data_question = json.loads(line)

                prompt = question_string.replace("{INFORMATION}", information)
                prompt = prompt.replace("{QUESTION}", data_question["text"])

                # Modelo
                output = generate_output(prompt, client)
                output = output + " Recuerda, soy un asistente experimental. Debes comprobar siempre estos códigos en ![icd.who.int](https://icd.who.int/)"


                # Replace special characters and escape newlines
                markdown_content = output.replace('"', '\\"')  # Replace double quotes with escaped double quotes
                markdown_content = markdown_content.replace("'", "\\'")  # Replace single quotes with escaped single quotes
                markdown_content = markdown_content.replace("\\", "\\\\")  # Replace backslashes with double backslashes
                markdown_content = markdown_content.replace("\n", "\\n")  # Escape newlines


                conversation = """
                {
                  "messages": [
                      {
                          "role": "user",
                          "content": "{QUESTION}"
                      },
                      {
                          "role": "assistant",
                          "content": "{ANSWER}"
                      }
                  ]
                }
                """

                # Perform the replacements
                conversation = conversation.replace("{QUESTION}", data_question["text"])
                conversation = conversation.replace("{ANSWER}", markdown_content)
                #print(conversation)
                try:
                  data_conversation = json.loads(conversation)
                  #print(data_conversation)

                  # Write the dictionary as a JSON line
                  json.dump(data_conversation, outfile,  ensure_ascii=False)
                  outfile.write('\n')

                except Exception as e:
                  pass
                  #print(e)
                  #print(file + " " + str(n))
    except Exception as e:
      pass
      #print(e)
    print(file + " exported.")
  else:
    print( file + " exists.")