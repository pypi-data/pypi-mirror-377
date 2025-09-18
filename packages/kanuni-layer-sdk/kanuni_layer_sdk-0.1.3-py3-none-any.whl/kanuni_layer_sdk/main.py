from .modules import redactor, validate_prompt

def main(prompt: str, opted_in: bool = True) -> str:
    validated_prompt = validate_prompt(prompt)
    redacted_prompt =  redactor(validated_prompt, opted_in)
    return redacted_prompt

if __name__ == "__main__":
    response = main(
        "My name is Jimmy Cricket with email <Jiminy.Cricket@example.com>, I am blind and deaf and mute. I am also quadriplegia and I would like to get directions to the nearest shopping centre. My credit card number is 4111 1111 1111 1111 and my phone number is +1 (555) 123-4567. Also, my SSN is 123-45-6789.",
    )

    print(response)
