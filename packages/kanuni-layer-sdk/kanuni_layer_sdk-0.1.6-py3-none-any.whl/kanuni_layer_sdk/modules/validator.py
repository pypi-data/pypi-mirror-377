def validate_prompt(prompt: str) -> str:
    """
    Validates the given prompt to ensure it meets certain criteria before processing.
    
    Args:
        prompt (str): The prompt string to validate.
        
    Returns:
         validated string else raises ValueError
    """
    # Check if the prompt is None or empty
    if prompt is None or prompt.strip() == "":
        raise ValueError("Prompt cannot be null or empty.")
    
    #Encoding check
    try:
        prompt.encode('utf-8')                  
    except UnicodeEncodeError:
        raise ValueError("Prompt contains invalid characters that cannot be encoded in UTF-8.")     
    
    # Check if the prompt exceeds a certain length
    if prompt and len(prompt) > 1000:
        raise ValueError("Prompt exceeds maximum length of 1000 characters.")
    
    # remove special characters
    special_characters = "!#$%^&*()_+-=[]{}|;':\"<>/?`~"
    for char in special_characters:
        prompt = prompt.replace(char, "")

    # Convert to lowercase
    prompt = prompt.lower()

    print(f"Validated prompt:\n {prompt}\n\n")

    return prompt