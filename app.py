from flask import Flask, request, jsonify
import openai

app = Flask(__name__)

@app.route('/api/gpt3', methods=['POST'])
def gpt3_api_call():
    data = request.json

    prompt = data['prompt']

    openai.api_key = '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'  # Replace with your actual OpenAI API key

    desired_proteins = data['desired_proteins']
    prompt += f"\nDesired amount of proteins: {desired_proteins} grams."

    desired_carbs = data['desired_carbs']
    prompt += f"\nDesired amount of carbohydrates per meal: {desired_carbs} grams."

    user_input = data['user_input']

    if user_input.lower() == "yes":
        dish_name = data['dish_name']
        prompt += f"\n\nRecipe: {dish_name}\n\nIngredients:\n- [Ingredients for {dish_name}]"
    else:
        prompt += "\n\nPlease suggest a recipe that fulfills these dietary requirements."

    response = openai.Completion.create(
        engine='davinci-codex',
        prompt=prompt,
        max_tokens=100,
        temperature=0.5,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    recipe_output = response.choices[0].text.strip()

    if user_input.lower() == "yes":
        return jsonify({'response': f'- [Ingredients for {dish_name}]\n\n{recipe_output}'})
    else:
        substitution_command = data.get('substitution_command')

        if substitution_command:
            substitution_response = check_substitutions(recipe_output, substitution_command)
            return jsonify({'response': substitution_response})

        return jsonify({'response': recipe_output})

def check_substitutions(recipe_output, substitution_command):
    ingredient, substitution = extract_ingredient_substitution(substitution_command)

    if is_substitution_valid(ingredient, substitution):
        recipe_output = recipe_output.replace(ingredient, substitution)
        response = f'Substitution successful. Updated recipe:\n\n{recipe_output}'
    else:
        response = f'Substitution failed. {substitution} cannot be used as a substitution for {ingredient}.'

    return response

def extract_ingredient_substitution(substitution_command):
    ingredient = ""
    substitution = ""
    command_parts = substitution_command.split(".")

    for part in command_parts:
        part = part.strip()

        if part.lower().startswith("i don't have"):
            ingredient = part[13:].strip()
        elif part.lower().startswith("i do have"):
            substitution = part[10:].strip()

    return ingredient, substitution
