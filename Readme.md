# AI Persona Testing

This is an automated Python pipeline that uses GPT-4 to simulate realistic user interactions for Human-Computer Interaction (HCI) research. It automates the process of generating user personas, defining their actions (including errors), and executing browser-based tests on web interfaces.

## Table of Contents
- [Key Features](#key-features)
- [How It Works](#how-it-works)
- [Project Structure](#project-structure)
- [Setup and Installation](#setup-and-installation)
- [Usage](#usage)
- [Generated Outputs](#generated-outputs)
- [Dependencies](#dependencies)
- [License](#license)

## Key Features

-   **AI-Powered Persona Generation**: Creates four distinct and detailed user personas (Novice, Expert, Distracted, Accessibility-focused) using GPT-4.
-   **Dynamic Action Generation**: For each persona, GPT-4 generates a realistic sequence of actions, including common errors and delays tailored to their behavior type.
-   **Automated Browser Simulation**: Uses Selenium to open a real browser and execute the AI-generated action plan on your provided HTML files.
-   **Rich Data & Visual Outputs**: Generates persona summary cards (PNGs), before-and-after screenshots of each simulation, and detailed action logs.
-   **Automated Reporting**: Analyzes the simulation data and produces a final Excel report with key metrics like success rate, average steps, and total errors per persona.

## How It Works

The pipeline operates in four automated steps:

### Step 1: Generate Personas
The script calls the GPT-4 API to create four user personas. Each persona is defined by their demographics, technical comfort, goals, and frustrations, which directly influence their behavior in the simulation.
-   **Output**: `data/simpersonas.json`

### Step 2: Create Persona Cards
For easy visualization, the script generates summary "cards" for each persona as PNG images. These cards highlight the most important traits of the simulated user.
-   **Output**: PNG files in `data/persona_cards/`

### Step 3: Simulate Browser Interactions
This is the core of the pipeline. For each persona and each HTML interface:
1.  **Generate Action Plan**: GPT-4 creates a step-by-step action sequence. A *Novice* might type slowly and make typos, while an *Expert* might navigate quickly.
2.  **Execute Simulation**: Selenium launches a Chrome browser, loads the specified HTML file, and performs the actions.
3.  **Capture Evidence**: The simulator takes "before" and "after" screenshots to visually document the interaction.
-   **Outputs**: Screenshots in `screenshots/` and action data in `data/simpersona_actions.csv`.

### Step 4: Generate Reports
Finally, the script aggregates all the logged data, calculates performance metrics, and compiles them into a comprehensive report.
-   **Output**: `SimPersona_Analysis.xlsx`

## Project Structure

To run the script, your project must follow this folder structure. You will need to create the `data/interfaces` directory and provide the HTML files yourself.

```
your-project-folder/
│
├── Code.py                 # The main Python script
├── requirements.txt        # The project dependencies file
├── README.md               # This file
│
└── data/
    │
    └── interfaces/         # <-- YOU MUST CREATE THIS FOLDER
        ├── login.html      # <-- Add your test HTML files here
        ├── checkout.html
        └── profile.html
```

> **Note:** The script will automatically generate the `persona_cards`, `screenshots`, `simpersonas.json`, `simpersona_actions.csv`, and `SimPersona_Analysis.xlsx` files during its first run.

## Setup and Installation

Follow these steps to prepare your environment.

**1. Clone the Repository**
```bash
git clone <your-repository-url>
cd your-project-folder
```

**2. Create the Required Directory and Files**
Manually create the `data/interfaces` directory and place your HTML files (`login.html`, `checkout.html`, `profile.html`) inside it, as shown in the [Project Structure](#project-structure) section.

**3. Install Python Dependencies**
This project uses a `requirements.txt` file to manage dependencies.
First, create the `requirements.txt` file in your project's root directory with the following content:
```text
openai
pandas
selenium
Pillow
openpyxl
```
Then, install all the required libraries using pip:
```bash
pip install -r requirements.txt
```

**4. Set Up Your OpenAI API Key**
The script needs a valid GPT-4 API key. The recommended way is to set it as an environment variable.

-   **macOS / Linux:**
    ```bash
    export OPENAI_API_KEY="sk-your-api-key-here"
    ```
-   **Windows (Command Prompt):**
    ```bash
    set OPENAI_API_KEY="sk-your-api-key-here"
    ```

Alternatively, you can hardcode your key on line 20 of `Code.py`, but this is not recommended.

**5. Install a WebDriver**
Selenium requires a browser driver to control the browser.
-   Download the appropriate **ChromeDriver** for your version of Google Chrome.
-   Place the `chromedriver` executable in a location on your system's `PATH` (e.g., `/usr/local/bin` on macOS/Linux).

## Usage

Once the setup is complete, you can run the entire pipeline with a single command from your terminal:

```bash
python3 Code.py
```

The script will prompt you for confirmation before it starts making API calls to OpenAI, as this will consume your API credits. Type `yes` and press Enter to proceed.

## Generated Outputs

After a successful run, the following files and directories will be created in your project folder:

-   `data/simpersonas.json`: The raw JSON data for the four AI-generated personas.
-   `data/simpersona_actions.csv`: A detailed CSV log of every action taken by every persona.
-   `data/persona_cards/`: A folder containing the visual summary cards for each persona.
-   `screenshots/`: A folder containing before-and-after images of each browser simulation.
-   `SimPersona_Analysis.xlsx`: The final Excel report with a high-level summary and detailed logs.

## Dependencies

-   [openai](https://pypi.org/project/openai/): For interacting with the GPT-4 API.
-   [pandas](https://pypi.org/project/pandas/): For data manipulation and creating CSV/Excel reports.
-   [selenium](https://pypi.org/project/selenium/): For automating browser actions.
-   [Pillow](https://pypi.org/project/Pillow/): For creating the persona card images.
-   [openpyxl](https://pypi.org/project/openpyxl/): Required by Pandas to write `.xlsx` files.
