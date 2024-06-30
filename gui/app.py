import streamlit as st
import os
from mistralai.client import MistralClient
import time

mistral_api_key = os.environ.get("MISTRAL_API_KEY")
mistral_client = MistralClient(api_key=mistral_api_key)

def openai_response(messages, model="ft:open-mistral-7b:7ccb0f03:20240630:de18ea79"):

    response = mistral_client.chat(
        model=model,
        temperature=0,
        messages=messages
        )

    message = response.choices[0].dict()['message']["content"]
    for word in message.split():
        yield word + " "
        time.sleep(0.05)

st.sidebar.title("Pakobot")
st.sidebar.markdown("This projects aims to help doctors in Spain to find the right [International code for diseases v11 (ICD-11)](https://www.who.int/standards/classifications/classification-of-diseases) easily.")
st.sidebar.markdown("For documentation please refer to [github.com/caviri/pakobot](https://github.com/caviri/pakobot)")
st.sidebar.markdown("This is an experimental project and should not be used for professional medical practice.")
st.sidebar.markdown("Project created by [Carlos Vivar Rios](http://www.carlosvivarrios.com) and  presented to the Mistral Fine Tuning Hackathon 2024")

model = st.text_input("Please introduce the fine tuned model", value="ft:open-mistral-7b:7ccb0f03:20240630:de18ea79")
# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Dime el código para la Leucemia."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        response = st.empty()  # Create a placeholder for the response
        response_text = ""
        for word in openai_response(st.session_state.messages):
            response_text += word
            response.write(response_text)
        
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response_text})

