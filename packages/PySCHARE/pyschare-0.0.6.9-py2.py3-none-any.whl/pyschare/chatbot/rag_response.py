# rag_response.py

import os
import json
from vertexai.generative_models import GenerativeModel, GenerationConfig, SafetySetting
from pyschare.chatbot.hybrid_approach import get_context_hybrid
from pyschare.data_processing.config import (LLM_PROJECT_ID, 
                                    MODEL_NAME, 
                                    LOCATION,
                                    short_term_history, 
                                    max_history, 
                                    COMBINED_FILE_NAME, 
                                    target_service, 
                                    lifetime)
from pyschare.chatbot.impersonation import get_vertex

get_vertex(target_service, lifetime, LLM_PROJECT_ID, LOCATION)

SYSTEM_INSTRUCTIONS = """
You are SCHARE AI, an assistant that answers questions using only the provided context.

Context comes from:
1. Dataset Metadata  
2. Variable Metadata  
3. Notebook Content

When answering:
- Clearly distinguish between datasets, variables, and notebooks.
- If using a dataset, include the exact dataset name (keep underscores) and key details.
- If referencing a variable, include its name, description, and dataset.
- If referencing notebook content, clarify that the information comes from a specific notebook section (mention the notebook name).

Use structured references when responding about datasets:
    - Example format:
      **Dataset Name**: `Dataset_Name`  
      **Year**: Year  
      **URL**: Data URL   
      **Sponsor**: Sponsor   

Use structured references when responding about variables:
    - Example format:
      **Variable**: `VariableName` 
      **Description**: Description   
      **Dataset Name**: `Dataset_Name`    

Use structured references when responding with notebook content:
    - Example format:
      **Notebook**: `Notebook Name`    
      **Section**: `Header/Title`    
      <div style="border-left: 4px solid #0066b2; padding: 10px; margin-top: 5px;">
        <strong>Summary:</strong><br>
        Provide a clear, concise summary of the relevant notebook section. Focus on:
        - Purpose of the analysis  
        - Key methods used  
        - Important findings or conclusions  
        </div>

    - Word limit: Aim for no more than **150 words**.

Use only the given context. If info is not available, say:
"I'm sorry, but I couldn't find that information in the available context."

Be concise, accurate, and professional.

Context Tracking:
- If a user refers to a dataset, variable, notebook, or concept using vague references like "that", "it", or "the previous one", resolve the reference using the most recently mentioned relevant object from the conversation history.
- Maintain awareness of the current topic of conversation (e.g., last mentioned dataset, variable, or notebook).
- If the last SCHARE-AI response included a dataset name, variable name, or a notebook name, assume follow-up questions refer to that object unless clearly stated otherwise.
"""

# Conversation history tracker
# conversation_history = []
# short_term_history = "short_term_history.json"
# max_history = 10


def format_history_for_prompt(history):
    """Format conversation history for inclusion in the prompt"""
    formatted = ""
    for message in history:
        if message["role"] == "user":
            formatted += f"User: {message['content']}\n\n"
        else:
            formatted += f"SCHARE-AI: {message['content']}\n\n"
    return formatted


def load_short_term_history():
    if os.path.exists(short_term_history):
        with open(short_term_history, "r") as f:
            return json.load(f)
    return []


def save_conversation_history(user_msg, ai_msg):
    memory = load_short_term_history()
    memory.extend([user_msg, ai_msg])
    memory = memory[-max_history:]

    with open(short_term_history, "w") as f:
        json.dump(memory, f, indent=2)


def generate_response(user_question):
    # Step 1: Build the combined context
    # combined_context = get_context_hybrid(user_question)
    combined_context = get_context_hybrid(user_question, COMBINED_FILE_NAME)

    # Step 2: Format conversation history
    conversation_history = load_short_term_history()
    formatted_history = format_history_for_prompt(conversation_history)

    # Step 3: Compose the full input prompt
    combined_input = f"""
        Instructions for AI Assistant:
        {SYSTEM_INSTRUCTIONS}

        Context:
        {combined_context}

        Previous Conversation:
        {formatted_history}

        User Question:
        {user_question}

        """

    # Step 4: Initialize Vertex AI and Gemini model
    # vertexai.init(project=LLM_PROJECT_ID, location="us-central1", credentials=creds)
    # Added new
    get_vertex(target_service, lifetime, LLM_PROJECT_ID, LOCATION)
    #

    model = GenerativeModel(MODEL_NAME)

    # Step 5: Configure generation settings
    generation_config = GenerationConfig(
        max_output_tokens=8192, temperature=0.7, top_p=0.95
    )

    safety_settings = [
        SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_NONE"),
        SafetySetting(
            category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_NONE"
        ),
        SafetySetting(
            category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="BLOCK_NONE"
        ),
        SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_NONE"),
    ]

    # Step 6: Generate the response
    responses = model.generate_content(
        [combined_input],
        generation_config=generation_config,
        safety_settings=safety_settings,
        stream=False,
    )

    full_response = responses.text

    # Step 7: Update conversation history
    user_msg = {"role": "user", "content": user_question}
    ai_msg = {"role": "assistant", "content": full_response}
    save_conversation_history(user_msg, ai_msg)

    return full_response
