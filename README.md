
# OracleGPT

OracleGPT is an interactive chatbot that uses advanced machine learning models to engage in conversation. It features a graphical user interface built with CustomTkinter, speech recognition, and text-to-speech capabilities, making it accessible and easy to use for various purposes including education, accessibility, and entertainment.

## Features

- **Graphical User Interface**: Built using CustomTkinter for a modern look.
- **Speech Recognition**: Allows users to interact using voice commands.
- **Text-to-Speech**: Converts text responses from the chatbot into audible speech.
- **OpenAI Integration**: Leverages the power of OpenAI's models for generating human-like text responses.

## Installation

To set up OracleGPT on your system, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/iebgit/chatgptbot.git
   ```
2. Install the necessary Python packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

To run OracleGPT, navigate to the cloned directory and run:
```bash
python chat.py
```

## Configuration

- **Voice Settings**: The application supports switching between male and female voices using the `male_voice` flag in the settings.
- **Language**: Set the default language for text-to-speech in the `language` variable.

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Acknowledgements

- [OpenAI](https://www.openai.com/)
- [Tkinter Documentation](https://docs.python.org/3/library/tkinter.html)
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
- [gTTS](https://pypi.org/project/gTTS/)
- [speech_recognition](https://pypi.org/project/SpeechRecognition/)
