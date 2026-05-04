import os
import re

from google import genai # https://ai.google.dev/gemini-api/docs/text-generation

if not os.environ.get("GEMINI_API_KEY"):
    from app.core import config
    config.load_env()

# The client gets the API key from the environment variable `GEMINI_API_KEY`.
client = genai.Client()

# new constants related to safety config
SAFETY_SETTINGS = [ # default values are off so setting most to block medium to high chances with a few low to high
    {"category" : "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}, 
    {"category" : "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_LOW_AND_ABOVE"},
    {"category" : "HARM_CATEGORY_HARRASSMENT", "threshold": "BLOCK_LOW_AND_ABOVE"},
    {"category" : "HARM_CATEGORY_SEXUAL_CONTENT", "threshold": "BLOCK_LOW_AND_ABOVE"},
    {"category" : "HARM_CATEGORY_VIOLENCE", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
]
SAFETY_THRESHOLD = 0.7

def sense_check(response):
    # checks for sensibility for depth or magnitude
    # input: response(string, assumed)
    # output: array of potential errors

    potential_errors = []

    # finds where magnitude (number) is mentioned
    mags = re.findall(r"[Mm]agnitude\s*(\d+(\.\d+)?)", response)
    for m in mags:
        mag = float(m[0])
        if mag< 0 or mag > 10:
            potential_errors.append(m)
    
    depths = re.findall(r"(\d+)\s*km\s*deep", response)
    for d in depths:
        depth = int(d)
        if depth< 0 or depth > 1000: # 1000km feels excessive but a quick guess at a silly number
            potential_errors.append(d)

    return potential_errors

# Async functions keep the thread responsive by releasing it for other tasks when waiting on io bound tasks
async def prompt(prompt_text: str) -> str:
    print(f"Querying: \"{prompt_text}\"")

    # Await tells the thread to execute the following async function and wait for it to complete before continuing here.
    response = await client.aio.models.generate_content(
        model="gemma-4-31b-it", 
        config=genai.types.GenerateContentConfig(
            system_instruction="""You are a chat bot for analysing graphs related to earthquakes and tsunamis.
                                Only respond to relevant questions, and respond factually, avoiding speculation."""
        ),
        contents=prompt_text,
        safety_settings=SAFETY_SETTINGS
        )
    
    # throw away the response if above the threshold
    if hasattr(response, "safety_ratings") and response.safety_ratings:
        for rating in response.safety_ratings:
            if rating.probability > SAFETY_THRESHOLD:
                print(f"Safety Category exceeded: {rating.category}")
                return "No Response Generated"

    # Take the text component or default if not provided.
    return response.text or "No response generated."

if __name__ == "__main__":
    # Executing an async function doesn't work in the same way as executing a synchronous function.
    # Calling `async def blah()` returns a coroutine object, you must have an event loop execute it in a particular way.
    # From inside an async function,
    #     there must already be an event loop, you can use `await` before calling another async function
    #     to yield control of the thread until the async function completes.
    # From inside a synchronous function,
    #     `asyncio.run(prompt("blah blah"))` aka `asyncio.run(<coroutine object prompt at 0x000001CC96CA7760>)`
    #     spawns an event loop and executes the coroutine object/async function call.
    # There are other things asyncio can do, such as executing async code without waiting, but these examples are most relevant.
    # You can simply call `await prompt(prompt_text)` when inside the body of an async function.
    import asyncio

    # default prompt asking for description
    response = asyncio.run(prompt("Tell me about this model"))
    






