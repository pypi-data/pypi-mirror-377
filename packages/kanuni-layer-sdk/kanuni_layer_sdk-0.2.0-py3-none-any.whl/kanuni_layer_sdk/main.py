import asyncio
import inspect
from .modules import redactor, validate_prompt
from prompt_library import transform_multiple_keys as transform_prompt

async def reduct(prompt: str, opted_in: bool = True) -> str:
    #Validate the prompt input
    print("")
    validated_prompt = validate_prompt(prompt)

    # Redact sensitive information from the prompt if opted in
    redacted_result =  redactor(validated_prompt, opted_in)

    # Extract 'reducted_prompt' and 'categories' robustly (handle string fallback)
    if isinstance(redacted_result, dict):
        reducted_prompt = redacted_result.get("reducted_prompt", validated_prompt)
        categories = redacted_result.get("categories", [])
    else:
        reducted_prompt = str(redacted_result)
        categories = []

    print(f"Redacted Prompt:\n {reducted_prompt}\n\nCategories: {categories}\n")

    # Transform by adding context per the disability info in the prompt
    if inspect.iscoroutinefunction(transform_prompt):
        refined_disability_addition = await transform_prompt(categories)
    else:
        # Run sync transform_prompt in a thread to avoid asyncio.run() inside a running loop
        refined_disability_addition = await asyncio.to_thread(transform_prompt, categories)
    curated_prompt = f"{reducted_prompt}\n{refined_disability_addition['output']}"

    return curated_prompt

if __name__ == "__main__":
    response = asyncio.run (
        reduct(
        "My name is Jimmy Cricket with email <Jiminy.Cricket@example.com>, I am blind and deaf and mute. I am also quadriplegia and I would like to get directions to the nearest shopping centre. My credit card number is 4111 1111 1111 1111 and my phone number is +1 (555) 123-4567. Also, my SSN is 123-45-6789.",
       )
    )

    print(response)
