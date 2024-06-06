import os
import google.generativeai as genai
import google.api_core.exceptions
from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
import subprocess
import re
import pyperclip

# Configuration de l'API Gemini
api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    raise ValueError("La clé API 'GOOGLE_API_KEY' n'est pas définie dans les variables d'environnement.")
genai.configure(api_key=api_key)

def extract_command(response_text):
    """Extrait la commande de la réponse de l'API Gemini."""
    match = re.search(r"`([^`]+)`", response_text)
    return match.group(1) if match else None

def open_new_terminal_with_command(command):
    """Ouvre un nouveau terminal avec la commande copiée dans le presse-papiers."""
    pyperclip.copy(command)
    print("Commande copiée dans le presse-papiers.")
    current_dir = os.getcwd()

    # Pour Windows
    subprocess.run(f'start cmd /K "cd /d {current_dir}"', shell=True)

    # Pour macOS ou Linux, utilisez la ligne suivante et commentez celle de Windows
    # subprocess.run(f'gnome-terminal -- bash -c "cd \'{current_dir}\' && exec bash"', shell=True)

    print(f"Ouvrez le terminal et collez la commande en utilisant Ctrl+V (Windows) ou Cmd+V (Mac).")

def main():
    print("Terminal intelligent avec Gemini - Tapez 'exit' pour quitter")

    # Utilisation du modèle gemini-1.5-flash
    model = genai.GenerativeModel('gemini-1.5-flash')

    while True:
        user_input = prompt(
            "> ",
            history=FileHistory('history.txt'),
            auto_suggest=AutoSuggestFromHistory(),
        )

        if user_input.lower() == 'exit':
            break

        try:
            # Formuler la question pour obtenir uniquement la commande
            response = model.generate_content(f"Donne-moi uniquement la commande pour {user_input} en texte brut sans rien ajouter :")
            response_text = response.candidates[0].content.parts[0].text.strip()
            command = extract_command(response_text)
            if not command:
                command = response_text
        except google.api_core.exceptions.InvalidArgument as e:
            print(f"Erreur: {e}")
            continue
        except (IndexError, KeyError, AttributeError) as e:
            print(f"Erreur de réponse: {e}")
            continue

        if command:
            print(f"Commande suggérée: {command}")
            if input("Exécuter? (o/n): ").lower() == 'o':
                open_new_terminal_with_command(command)
                break
        else:
            print(response_text)  # Affiche la réponse complète si aucune commande n'est trouvée

if __name__ == "__main__":
    main()
