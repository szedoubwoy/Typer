import json
import os

# Pełna ścieżka do pliku JSON
script_dir = os.path.dirname(__file__)  # Uzyskaj katalog, w którym znajduje się skrypt
input_file_path = os.path.join(script_dir, 'top_scorers_corrected.json')  # Plik wejściowy
output_file_path = os.path.join(script_dir, 'top_scorers_cleaned.json')  # Plik wyjściowy

# Wczytaj dane z pliku JSON
with open(input_file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

# Funkcja do usunięcia nadmiarowych przecinków
def clean_name(name):
    # Usuń nadmiarowe przecinki z końca nazwiska
    return name.rstrip(',')

# Poprawianie nazwisk
cleaned_data = [[clean_name(player[0]), player[1]] for player in data]

# Zapisz poprawione dane do nowego pliku JSON
with open(output_file_path, 'w', encoding='utf-8') as file:
    json.dump(cleaned_data, file, ensure_ascii=False, indent=4)

print(f"Poprawiono dane i zapisano do '{output_file_path}'.")