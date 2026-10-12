# My Shorekeeper - Local AI Companion

A highly personalized, locally-hosted AI assistant inspired by the character Shorekeeper from *Wuthering Waves*.

Powered by a 4-bit quantized **Qwen 2.5 3B** neural core running locally on an NVIDIA GPU, Shorekeeper acts as a proactive daily helper. She features a continuous voice-listening loop, natural language tool interception, and a sleek CustomTkinter interface—all while strictly adhering to her ethereal, poetic persona.

## 🌟 Features

* **Completely Local Inference:** Runs entirely on your local hardware using the `transformers` library (No paid API keys required).

* **Voice Activation & Custom UI:** Continuous background listening for the wake word ("Shore") combined with a cinematic, expandable chat interface.

* **Dynamic Memory:** She learns and updates her knowledge about your routines and goals dynamically via `My_blueprint.txt`.

* **Native Web Search:** Silently queries DuckDuckGo for real-time information and summarizes it in character.

* **Application Launcher:** Uses natural language to seamlessly open local Windows applications (e.g., "Shore, can you launch VS Code?").

* **Email Assistant:** Drafts contextual, professional emails, copies them to your clipboard, and automatically launches your browser directly to the relevant Gmail search.

* **Media Player:** Acts as a home assistant to instantly tune into and play requested songs on YouTube.

## 💻 Prerequisites

* **OS:** Windows 10/11 (due to the `subprocess` command structures used).

* **Hardware:** An NVIDIA GPU with at least **4 GB VRAM**.

* **Python:** Python 3.10 or higher.

* **CUDA:** PyTorch must be installed with CUDA support.

## ⚙️ Installation

1. **Clone the repository:**

   ```
   git clone https://github.com/yourusername/my-shorekeeper.git
   cd my-shorekeeper
   
   ```

2. **Install CUDA-enabled PyTorch:**
   Ensure your PyTorch installation can communicate with your dedicated GPU.

   ```
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
   
   ```

3. **Install the Required Libraries:**

   ```
   pip install transformers==4.45.2 tokenizers==0.20.1 safetensors accelerate
   pip install speechrecognition customtkinter pillow pyperclip duckduckgo-search pywhatkit
   
   ```

4. **Prepare the Knowledge Files:**
   Ensure the following configuration files are placed in the same directory as the script. (You can customize these to fit your own needs):

   * `Shorekeeper_Persona.txt`: The core identity and behavioral directives.

   * `My_blueprint.txt`: Your personal context, goals, and dynamically saved memories.

   * `shorekeeper_voice_template.txt`: Formatting rules for her speech cadence.

   * `H.jpg`: The background image for the GUI.

## 🚀 Usage

Run the main Python script from your terminal:

```
python shorekeeper.py

```

* **Voice Mode:** Ensure the Mic button says "ON". Say "Shore" or "Sure" to wake her up, wait for the status to change to "Listening...", and speak your command.

* **Text Mode:** Simply type your message into the input field at the bottom and press Enter.

### Example Commands

* *"Shore, search the web for the latest updates on Python 3.12."*

* *"Can you open File Explorer for me?"*

* *"Draft an email reply to Dr. Sahu about the project."*

* *"Play the Wuthering Waves main theme."*

* *"Remember that I am shifting my deep work hours to start at 9:00 AM."*

## 🛠️ Built With

* [HuggingFace Transformers](https://huggingface.co/docs/transformers/index)

* [Qwen 2.5 3B (Unsloth 4-bit)](https://huggingface.co/unsloth/qwen2.5-3b-instruct-unsloth-bnb-4bit)

* [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)

* [DuckDuckGo Search](https://pypi.org/project/duckduckgo-search/)