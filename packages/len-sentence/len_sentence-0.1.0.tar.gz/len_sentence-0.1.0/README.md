# len_sentence

A Python library for counting words and characters in sentences across different languages and writing systems.

## Overview

`len_sentence` provides intelligent sentence length counting that adapts to different languages and writing systems. It uses ISO15924 script codes to determine the appropriate counting method for each language, handling everything from space-separated languages like English to character-based languages like Chinese and Japanese.

## Features

- **Multi-language support**: Handles various writing systems including Latin, Chinese (Traditional/Simplified), Japanese, Thai, Khmer, Myanmar, Tibetan, and more
- **ISO15924 compliance**: Uses standard 4-letter script codes for language identification
- **Special character handling**: Properly processes numbers, punctuation, and language-specific separators
- **Intelligent counting**: Automatically switches between word counting and character counting based on the script type

## Installation

```bash
pip install len_sentence
```

## Supported Language Scripts
The goal of the script is able to count the words from all the langauge of the world.

## API Reference

### `count_sentence(sentence, lang_code)`

Count the number of words or characters in a sentence based on the language script.

**Parameters:**
- `sentence` (str): The sentence to count
- `lang_code` (str): 4-letter ISO15924 script code

**Returns:**
- `int`: Number of words or characters in the sentence

**Raises:**
- `ValueError`: If the language code is not valid

## Examples

```python
from len_sentence import count_sentence

# Different scripts, different counting methods
count_sentence("Hello world!", "Latn")
count_sentence("你好世界", "Hans")
count_sentence("こんにちは", "Jpan")
count_sentence("བཀྲ་ཤིས་བདེ་ལེགས", "Tibt")
count_sentence("مرحبا بالعالم", "Arab")
count_sentence("Привет мир", "Cyrl")
```

## Development

### Setup
```bash
git clone <repository-url>
cd len-sentence
pip install -e .
```

### Building and Publishing
```bash
python setup.py sdist bdist_wheel
twine upload dist/*
```

## Contributing
Contributions are welcome! Please feel free to submit issues and pull requests.

## Author

**JackyHe398**  
Email: hekinghung@gmail.com

---

*Note: This library uses ISO15924 script codes. For a complete list of supported scripts, refer to the [Unicode Script Codes](https://unicode.org/iso15924/iso15924-codes.html) specification.*
