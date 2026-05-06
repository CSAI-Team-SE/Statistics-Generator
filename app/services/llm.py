import os
import re

from typing import AsyncIterator, List, Optional
from google import genai # https://ai.google.dev/gemini-api/docs/text-generation
from google.genai import types
from app.core import config


config.load_env()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") # get the Gemini API key from the environment variable, which should be set in a .env file in the project root (see instructions in the error message below)

if not GEMINI_API_KEY: # if the API key is not set in the environment variable, raise an error with instructions on how to set it
    raise RuntimeError(
        "GEMINI_API_KEY is missing. Create a .env file in the project root "
        "and add GEMINI_API_KEY=your-api-key-here."
    )

client = genai.Client(api_key=GEMINI_API_KEY) # initialise the Gemini API client with the API key from the environment variable

MODEL_NAME = os.environ.get("GEMINI_MODEL", "gemma-4-31b-it") # default to gemma but more robust as model can now be set in env variable (not that it will change but just in case)

# system instruction for the LLM, providing context and guidelines for responses
SYSTEM_INSTRUCTION = """ 
You are a chatbot for analysing graphs related to earthquakes and tsunamis.

Only answer questions that are relevant to:
- the graph
- the dataset
- earthquakes
- tsunamis
- the statistics shown to the user

Use the provided data context when answering.
Be factual, concise, and avoid speculation.

Formatting rules:
- Do not use Markdown formatting.
- Do not use **bold text**, headings, tables, or Markdown symbols.
- Use plain text only.
- Use simple bullet points with hyphens if needed.
- Format statistic labels like this:
  Average magnitude: the average earthquake magnitude is about 6.9.
  Timeframe: the data covers around 21 years.
  Magnitude range: the values vary by about 2.6.
  Statistical significance: the p-value suggests a relationship in this dataset.

If the question is unrelated, politely say that you can only help with the graph or dataset.
"""


# safety settings for the LLM (reworked as they had some issues with the previous ones (spelling errors and removed violence as i checked and im pretty sure it was outdated))
SAFETY_SETTINGS = [
    types.SafetySetting(
        category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    ),
    types.SafetySetting(
        category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
    ),
    types.SafetySetting(
        category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
    ),
    types.SafetySetting(
        category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
    ),
]


def check_prompt_format(prompt_text: str) -> List[str]: # new function to check prompt input format
    errors = []

    if not prompt_text.strip():
        errors.append("Prompt cannot be empty.")
    
    if len(prompt_text) > 1000:
        errors.append("Prompt is too long. Maximum length is 1000 characters.")

    return errors


# function to build the prompt context for the LLM, combining the current prompt with any relevant data context and previous interactions
def build_prompt_contents(prompt_text: str, data_context: Optional[str] = None, history: Optional[List] = None) -> List[types.Content]:
    contents = []
    
    if data_context:
        data_context_msg = f"Graph and dataset context for this analysis:\n{data_context.strip()}"
        contents.append(types.Content(role="user", parts=[types.Part(text=data_context_msg)]))
        # Add a placeholder model response to acknowledge the data if we have history coming up
        if history or prompt_text:
            contents.append(types.Content(role="model", parts=[types.Part(text="I have received the graph data and statistics. How can I help you analyse them?")]))

    if history:
        for message in history:
            role = "user" if getattr(message, "role", None) == "user" else "model"
            content = getattr(message, "content", "")
            contents.append(types.Content(role=role, parts=[types.Part(text=content.strip())]))

    contents.append(types.Content(role="user", parts=[types.Part(text=prompt_text.strip())]))

    return contents

# checks the LLM response for any potential errors, such as unrealistic magnitudes or depths (cleaned up variable names and added comments for clarity)
def sense_check(response: str) -> List[str]:
    potential_errors = []

    # finds where magnitude (number) is mentioned
    magnitudes = re.findall(r"[Mm]agnitude\s*(\d+(\.\d+)?)", response)


    for m in magnitudes:
        magnitude = float(m[0])

        if magnitude < 0 or magnitude > 10:
            potential_errors.append(f"Unusual magnitude found: {magnitude}")
    
    # finds where depth (number) is mentioned
    depths = re.findall(r"(\d+)\s*km\s*deep", response)

    for d in depths:
        depth = int(d)

        if depth < 0 or depth > 1000: # 1000km feels excessive but a quick guess at a silly number
            potential_errors.append(f"Unusual depth found: {depth}")

    return potential_errors


# Async functions keep the thread responsive by releasing it for other tasks when waiting on io bound tasks
async def stream_prompt(prompt_text: str, data_context: Optional[str] = None, history: Optional[List] = None) -> AsyncIterator[str]:
    format_errors = check_prompt_format(prompt_text)


    if format_errors: # if there are any format errors, yield them to the user and stop the function (as the prompt is not valid)
        yield "Prompt format errors:\n" 

        for error in format_errors:
            yield f"- {error}\n"
        return

    contents = build_prompt_contents(prompt_text = prompt_text, data_context = data_context, history = history)

    response_stream = await client.aio.models.generate_content_stream( # this is the async version of the generate_content function, it returns an async generator that yields responses as they are generated by the LLM, allowing for streaming responses
        model=MODEL_NAME,
        contents=contents,
        config=types.GenerateContentConfig(
            safety_settings=SAFETY_SETTINGS,
            system_instruction=SYSTEM_INSTRUCTION,
            ),
    )

    full_response = ""

    async for response_part in response_stream:
        try:
            response_text = response_part.text or ""
        except Exception:
            response_text = ""

        if response_text:
            full_response += response_text
            yield response_text
    
        
    potential_errors = sense_check(full_response)
    if potential_errors:
        yield "\n\nPotential issues with the response:\n"

        for error in potential_errors:
            yield f"- {error}\n"