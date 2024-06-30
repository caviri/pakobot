import os
import json
from mistralai.client import MistralClient
from mistralai.models.jobs import TrainingParameters


# Path to the directory containing the JSONL files
CONVERSATIONS_FOLDER = "./data/conversations"

# Get a list of all files in the directory
files = os.listdir(CONVERSATIONS_FOLDER)

# Path to save the output JSONL file
#output_path = "/content/drive/MyDrive/MISTRAL-HACKATHON/Data/training.jsonl"
output_path = "training.jsonl"
# Open the output file in append mode
with open(output_path, 'a') as outfile:
  # Iterate over each file in the directory
  for file in files:
    # Open the current file in read mode
    with open(os.path.join(data_dir, file), 'r') as f:
      # Iterate over each line in the file
      for line in f:
        # Parse the JSONL line
        data = json.loads(line)

        # Write the dictionary as a JSON line to the output file
        json.dump(data, outfile)
        outfile.write('\n')

# Creating MISTRAL client
api_key = os.environ.get("MISTRAL_API_KEY")
client = MistralClient(api_key=api_key)

jobs = client.jobs.list()
print(jobs)

# Uploading data
with open("training.jsonl", "rb") as f:
    training_data = client.files.create(file=("training.jsonl", f))


created_job = client.jobs.create(
    model="open-mistral-7b",
    training_files=[training_data.id],
    hyperparameters=TrainingParameters(
        training_steps=10,
        learning_rate=0.0001,
        )
)
print("Created Job: " + created_job)

retrieved_job = client.jobs.retrieve(created_job.id)

print(f"Finetuned Model: {retrieved_job.fine_tuned_model}")
