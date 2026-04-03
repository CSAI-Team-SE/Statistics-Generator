import os

from google import genai # https://ai.google.dev/gemini-api/docs/text-generation

if not os.environ.get("GEMINI_API_KEY"):
    from app.core import config
    config.load_env()

# The client gets the API key from the environment variable `GEMINI_API_KEY`.
client = genai.Client()

async def prompt(prompt_text: str) -> str:
    print(f"Querying: \"{prompt_text}\"")

    response = await client.aio.models.generate_content(
        model="gemma-4-31b-it", contents=prompt_text
    )
    # Take the text component
    return response.text or "No response generated."

if __name__ == "__main__":
    import asyncio
    # Wrap call with asyncio.run() to move off the main thread.
    # You can simply call `await prompt(prompt_text)` when inside the body of an async function
    print(asyncio.run(prompt("Tell me about this model")))
