import os

from google import genai # https://ai.google.dev/gemini-api/docs/text-generation

if not os.environ.get("GEMINI_API_KEY"):
    from app.core import config
    config.load_env()

# The client gets the API key from the environment variable `GEMINI_API_KEY`.
client = genai.Client()

# Async functions keep the thread responsive by releasing it for other tasks when waiting on io bound tasks
async def prompt(prompt_text: str) -> str:
    print(f"Querying: \"{prompt_text}\"")

#   Await tells the thread to execute the following async function and wait for it to complete before continuing here.
    response = await client.aio.models.generate_content(
        model="gemma-4-31b-it", contents=prompt_text
    )
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
    print(asyncio.run(prompt("Tell me about this model")))
