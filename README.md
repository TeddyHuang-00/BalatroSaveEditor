# BalatroSaveEditor

This is a helper for managing saves of Balatro, including merging and editing.

:stop_sign: **This project is not affiliated with Balatro.** :stop_sign:

<details>
<summary> :floppy_disk: <strong>Please make sure you have backups in case of unexpected bugs.</strong> :floppy_disk: </summary>

:warning: The script is built without prior knowledge of how the game works, so bugs are expected when test cases don't fully cover or the game gets updates.

:warning: Please file an issue if you encounter any bug or the game crashes.

</details>

## Where to find save files

- Windows: `%APPDATA%\Roaming\Balatro`
- macOS: `~/Library/Application Support/Balatro`

## Installation

1. Clone this repo

   ```bash
   git clone https://github.com/TeddyHuang-00/BalatroSaveEditor.git && cd BalatroSaveEditor
   # or
   git clone git@github.com:TeddyHuang-00/BalatroSaveEditor.git && cd BalatroSaveEditor
   ```

2. Install dependencies

   ```bash
   pip install -r requirements.txt
   ```

## Usage

- List all options

  ```bash
  python main.py -h
  ```

- View save file

  ```bash
  python main.py view <save_file>
  ```

- Merge save files

  This will merge `left_save_file` and `right_save_file` with the most progress kept.

  ```bash
  python main.py merge <left_save_file> <right_save_file>
  ```

  You can change this behavior by using `-p` or `--prefer` option. This will make sure the progress of the specified save file is kept if there is any conflict.

  ```bash
  python main.py merge <left_save_file> <right_save_file> -p <left|right>
  ```

  You can also specify the output file by using `-o` or `--output` option.

  ```bash
  python main.py merge <left_save_file> <right_save_file> -o <output_save_file>
  ```

- Edit save file

  This will export the save file to a JSON file which can be edited.

  ```bash
  python main.py export <save_file>
  ```

  You can edit the JSON file and import it back to the save file.

  ```bash
  python main.py import <json_file>
  ```

  You can also specify the output file by using `-o` or `--output` option for both exporting and importing.

  ```bash
  python main.py export <save_file> -o <output_json_file>
  ```

## License

Open sourced under the [MIT license](LICENSE).

## Contributing

Feel free to submit a pull request if you find any bugs or want to add new features.
