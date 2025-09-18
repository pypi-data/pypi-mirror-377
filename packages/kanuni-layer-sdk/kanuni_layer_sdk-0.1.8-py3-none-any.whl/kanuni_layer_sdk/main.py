import asyncio
import inspect
from .modules import redactor, validate_prompt
from prompt_library import transform_prompt

async def reduct(prompt: str, opted_in: bool = True) -> str:
    #Validate the prompt input
    validated_prompt = validate_prompt(prompt)

    # Transform by adding context per the disability info in the prompt
    if inspect.iscoroutinefunction(transform_prompt):
        transformed_prompt = await transform_prompt(validated_prompt)
    else:
        # Run sync transform_prompt in a thread to avoid asyncio.run() inside a running loop
        transformed_prompt = await asyncio.to_thread(transform_prompt, validated_prompt)

    transformed_prompt_output = transformed_prompt['output']
    print(f"Transformed Prompt:\n {transformed_prompt_output}\n")

    # Redact sensitive information from the prompt if opted in
    redacted_prompt =  redactor(transformed_prompt_output, opted_in)
    return redacted_prompt

if __name__ == "__main__":
    response = asyncio.run (
        reduct(
        "My name is Jimmy Cricket with email <Jiminy.Cricket@example.com>, I am blind and deaf and mute. I am also quadriplegia and I would like to get directions to the nearest shopping centre. My credit card number is 4111 1111 1111 1111 and my phone number is +1 (555) 123-4567. Also, my SSN is 123-45-6789.",
       )
    )

    print(response)
