#!/usr/bin/env python3
import json, csv, os, random, time
from datetime import datetime
from typing import Dict, List, Any
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import textwrap
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", " !!!key here!!! ")


class ActionGenerator:
    """Generates realistic action sequences using GPT-4"""
    
    def __init__(self, api_key):
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI library not installed. Run: pip install openai")
        if not api_key or api_key == "your-api-key-here":
            raise ValueError("Valid OpenAI API key required")
        
        self.client = OpenAI(api_key=api_key)
        print("[OK] GPT-4 Action Generator ACTIVE")
    
    def generate_actions(self, persona: Dict, task: str, task_description: str) -> List[Dict]:
        """Generate action sequence for persona performing task"""
        
        print(f"      [GPT] Generating actions for {persona['label']} on {task}...")
        
        prompt = f"""You are simulating a {persona['label']} interacting with a {task_description}.

PERSONA PROFILE:
- Type: {persona['type']}
- Behavior: {persona['behavior']['description']}
- Goals: {', '.join(persona['behavior']['goals'][:3])}
- Frustrations: {', '.join(persona['behavior']['frustrations'][:3])}
- Tech Comfort: {persona['demographics']['tech_comfort']}

TASK: {task_description}

Generate a realistic sequence of actions this user would take, INCLUDING realistic mistakes based on their behavior type:
- Novice: might click wrong things, type slowly, re-read instructions, make typos, click wrong fields
- Expert: fast, uses keyboard shortcuts, might skip reading, minimal errors
- Distracted: pauses, loses focus, goes back to check, interruptions, forgets steps
- Accessibility: uses tab navigation, relies on keyboard, slower but methodical, may struggle with poorly labeled elements

Return ONLY a JSON array of 6-15 actions in this format:
[
  {{"action": "look", "target": "page", "value": "", "notes": "Reading page carefully", "delay": 2.0}},
  {{"action": "click", "target": "username_field", "value": "", "notes": "Clicked username", "delay": 0.5}},
  {{"action": "type", "target": "username", "value": "truman123", "notes": "Typing username", "delay": 0.0}},
  {{"action": "error", "target": "username", "value": "", "notes": "Made a typo", "delay": 0.5}},
  {{"action": "clear", "target": "username", "value": "", "notes": "Fixing mistake", "delay": 0.3}},
  {{"action": "type", "target": "username", "value": "truman123", "notes": "Retyped correctly", "delay": 0.0}}
]

Action types: look, click, type, key (tab/enter), wait, error, clear, navigate
Valid targets: page, username_field, password_field, username, password, button, name_field, address_field, signup_link
Delays in seconds (float).

Include realistic errors:
- Novice: 2-4 errors (typos, wrong clicks, navigation mistakes)
- Expert: 0-1 errors (rare mistakes due to speed)
- Distracted: 2-3 errors (losing focus, forgetting steps, having to backtrack)
- Accessibility: 1-2 errors (tab navigation confusion, unclear labels)"""

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You generate realistic user interaction sequences with errors. Return only valid JSON arrays."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.9,
            max_tokens=1000
        )
        
        content = response.choices[0].message.content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        actions = json.loads(content)
        error_count = len([a for a in actions if a.get('action') == 'error'])
        print(f"         -> Generated {len(actions)} actions, {error_count} errors (GPT)")
        return actions


class PersonaGenerator:
    """Generates detailed persona profiles using GPT-4"""
    
    def __init__(self, api_key):
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI library not installed. Run: pip install openai")
        if not api_key or api_key == "your-api-key-here":
            raise ValueError("Valid OpenAI API key required")
        
        self.client = OpenAI(api_key=api_key)
        print("[OK] GPT-4 Persona Generator ACTIVE")
    
    def generate_persona(self, persona_type: str) -> Dict[str, Any]:
        """Generate complete persona profile using GPT-4"""
        
        print(f"   [GPT] Generating {persona_type} persona...")
        
        persona_desc = {
            "novice": "new to interfaces, explores randomly, makes mistakes, reads everything carefully",
            "expert": "experienced user, uses shortcuts, efficient, fast navigator",
            "distracted": "multitasking user, forgets tasks, gets interrupted, loses focus",
            "accessibility-focused": "requires accessible interactions, uses assistive tech, keyboard navigation"
        }
        
        prompt = f"""Create a realistic {persona_type} user persona for HCI research.

Persona type: {persona_desc[persona_type]}

Return ONLY valid JSON in this exact format:
{{
  "age": [18-65],
  "gender": "[male/female/non-binary]",
  "location": "[country]",
  "occupation": "[specific job title]",
  "tech_experience": "[Low/Medium/High]",
  "description": "[2-3 sentences describing behavior patterns and how they interact with interfaces]",
  "goals": ["specific goal 1", "specific goal 2", "specific goal 3"],
  "frustrations": ["specific frustration 1", "specific frustration 2", "specific frustration 3"],
  "preferred_actions": ["specific action 1", "specific action 2", "specific action 3"]
}}

Make it realistic, diverse, and detailed. Base goals/frustrations on the persona type."""

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You create realistic HCI personas. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=500
        )
        
        content = response.choices[0].message.content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        base_persona = json.loads(content)
        persona_id = f"persona_{random.randint(10, 99):02d}"
        formatted_persona = self._format_persona_for_frontend(persona_id, persona_type, base_persona)
        
        print(f"   [OK] Generated: {persona_id} - {base_persona.get('occupation', 'N/A')}")
        return formatted_persona
    
    def _format_persona_for_frontend(self, persona_id: str, persona_type: str, base_data: Dict) -> Dict:
        """Format persona data for frontend consumption"""
        type_labels = {
            "novice": "Novice User",
            "expert": "Expert User",
            "distracted": "Distracted User",
            "accessibility-focused": "Accessibility User"
        }
        
        return {
            "id": persona_id,
            "label": type_labels.get(persona_type, persona_type.title()),
            "type": persona_type,
            "demographics": {
                "age": base_data["age"],
                "gender": base_data["gender"],
                "location": base_data["location"],
                "occupation": base_data["occupation"],
                "tech_comfort": base_data["tech_experience"]
            },
            "behavior": {
                "description": base_data["description"],
                "goals": base_data["goals"],
                "frustrations": base_data["frustrations"],
                "preferred_actions": base_data["preferred_actions"]
            }
        }


class PersonaCardGenerator:
    """Generates PNG persona cards"""
    
    @staticmethod
    def create_card(persona: Dict, output_path: str):
        """Create visual persona card"""
        width, height = 400, 600
        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)
        
        try:
            title_font = ImageFont.truetype("arial.ttf", 20)
            header_font = ImageFont.truetype("arial.ttf", 16)
            body_font = ImageFont.truetype("arial.ttf", 12)
        except:
            title_font = ImageFont.load_default()
            header_font = ImageFont.load_default()
            body_font = ImageFont.load_default()
        
        colors = {
            "novice": "#3b82f6",
            "expert": "#10b981",
            "distracted": "#f59e0b",
            "accessibility-focused": "#8b5cf6"
        }
        primary_color = colors.get(persona['type'], '#4f46e5')
        
        # Header
        draw.rectangle([0, 0, width, 80], fill=primary_color)
        title = persona['label']
        draw.text((20, 25), title, fill='white', font=title_font)
        
        # Demographics
        y = 100
        draw.text((20, y), f"ID: {persona['id']}", fill='#1f2937', font=header_font)
        y += 25
        draw.text((20, y), f"Age: {persona['demographics']['age']} | {persona['demographics']['gender'].title()}", fill='#4b5563', font=body_font)
        y += 20
        draw.text((20, y), f"Location: {persona['demographics']['location']}", fill='#4b5563', font=body_font)
        y += 20
        draw.text((20, y), f"Occupation: {persona['demographics']['occupation']}", fill='#4b5563', font=body_font)
        y += 30
        
        # Goals
        draw.text((20, y), "Goals:", fill='#1f2937', font=header_font)
        y += 20
        for goal in persona['behavior']['goals'][:3]:
            wrapped = textwrap.fill(f"- {goal}", width=50)
            for line in wrapped.split('\n'):
                draw.text((25, y), line, fill='#4b5563', font=body_font)
                y += 15
        
        y += 10
        # Frustrations
        draw.text((20, y), "Frustrations:", fill='#1f2937', font=header_font)
        y += 20
        for frust in persona['behavior']['frustrations'][:3]:
            wrapped = textwrap.fill(f"- {frust}", width=50)
            for line in wrapped.split('\n'):
                draw.text((25, y), line, fill='#4b5563', font=body_font)
                y += 15
        
        img.save(output_path)


class BrowserSimulator:
    """Simulates persona interactions with HTML"""
    
    def __init__(self, headless=False):
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
    
    def load_page(self, file_path: str):
        """Load HTML file"""
        abs_path = os.path.abspath(file_path)
        self.driver.get(f"file://{abs_path}")
        time.sleep(1)
    
    def take_screenshot(self, path: str):
        """Capture screenshot"""
        self.driver.save_screenshot(path)
    
    def execute_actions(self, actions: List[Dict]) -> List[Dict]:
        """Execute GPT-generated action sequence"""
        executed_actions = []
        
        try:
            for action_plan in actions:
                action_type = action_plan.get("action", "")
                target = action_plan.get("target", "")
                value = action_plan.get("value", "")
                notes = action_plan.get("notes", "")
                delay = action_plan.get("delay", 0.0)
                
                # Execute based on action type
                if action_type == "look":
                    time.sleep(delay)
                    self._add_action(executed_actions, "look", target, value, notes)
                
                elif action_type == "click":
                    if target == "username_field":
                        elem = self.driver.find_elements(By.TAG_NAME, "input")[0]
                        elem.click()
                    elif target == "password_field":
                        elem = self.driver.find_elements(By.TAG_NAME, "input")[1]
                        elem.click()
                    elif target == "name_field":
                        elem = self.driver.find_elements(By.TAG_NAME, "input")[0]
                        elem.click()
                    elif target == "address_field":
                        elem = self.driver.find_elements(By.TAG_NAME, "input")[1]
                        elem.click()
                    elif target == "button":
                        elem = self.driver.find_element(By.TAG_NAME, "button")
                        elem.click()
                    elif target == "signup_link":
                        try:
                            elem = self.driver.find_element(By.LINK_TEXT, "Sign up")
                            elem.click()
                        except:
                            pass
                    
                    time.sleep(delay)
                    self._add_action(executed_actions, "click", target, value, notes)
                
                elif action_type == "type":
                    if target in ["username", "password", "name", "address"]:
                        # Type character by character if delay specified
                        if "slowly" in notes.lower():
                            for char in value:
                                self.driver.switch_to.active_element.send_keys(char)
                                time.sleep(0.3)
                        else:
                            self.driver.switch_to.active_element.send_keys(value)
                    
                    time.sleep(delay)
                    # Mask password
                    display_value = "********" if target == "password" else value
                    self._add_action(executed_actions, "type", target, display_value, notes)
                
                elif action_type == "key":
                    if target == "tab":
                        self.driver.switch_to.active_element.send_keys(Keys.TAB)
                    elif target == "enter":
                        self.driver.switch_to.active_element.send_keys(Keys.RETURN)
                    
                    time.sleep(delay)
                    self._add_action(executed_actions, "key", target, value, notes)
                
                elif action_type == "clear":
                    self.driver.switch_to.active_element.clear()
                    time.sleep(delay)
                    self._add_action(executed_actions, "clear", target, value, notes)
                
                elif action_type == "wait":
                    time.sleep(delay if delay > 0 else float(value))
                    self._add_action(executed_actions, "wait", target, value, notes)
                
                elif action_type == "navigate":
                    if target == "back":
                        self.driver.back()
                        time.sleep(delay)
                    self._add_action(executed_actions, "navigate", target, value, notes)
                
                elif action_type == "error":
                    # Error actions are just logged, not executed
                    time.sleep(delay)
                    self._add_action(executed_actions, "error", target, value, notes)
        
        except Exception as e:
            self._add_action(executed_actions, "error", "interaction", "", f"Execution error: {str(e)}")
        
        return executed_actions
    
    def _add_action(self, actions: List, action: str, target: str, value: str, notes: str):
        """Add action to log"""
        actions.append({
            "step": len(actions) + 1,
            "action": action,
            "target": target,
            "value": value,
            "timestamp": f"00:00:{len(actions)+1:02d}",
            "notes": notes
        })
    
    def close(self):
        """Close browser"""
        if self.driver:
            self.driver.quit()


class SimPersonaPipeline:
    """Complete research pipeline - GPT-4 powered only"""
    
    def __init__(self, api_key):
        self.base_dir = os.getcwd()
        self.data_dir = os.path.join(self.base_dir, "data")
        self.interfaces_dir = os.path.join(self.data_dir, "interfaces")
        self.cards_dir = os.path.join(self.data_dir, "persona_cards")
        self.screenshots_dir = os.path.join(self.base_dir, "screenshots")
        
        for directory in [self.data_dir, self.cards_dir, self.screenshots_dir]:
            os.makedirs(directory, exist_ok=True)
        
        # Initialize GPT-4 generators (will raise error if API key invalid)
        self.persona_generator = PersonaGenerator(api_key=api_key)
        self.action_generator = ActionGenerator(api_key=api_key)
        self.personas = []
        self.action_logs = []
        
        print(f"[DIR] Working in: {self.base_dir}")
        print(f"[DIR] Data folder: {self.data_dir}")
        print(f"[DIR] Screenshots: {self.screenshots_dir}")
    
    def step1_generate_personas(self):
        """Generate 4 GPT-powered personas"""
        print("\n[STEP 1] GENERATING PERSONAS (GPT-4)")
        print("-" * 60)
        
        persona_types = ["novice", "expert", "distracted", "accessibility-focused"]
        for ptype in persona_types:
            persona = self.persona_generator.generate_persona(ptype)
            self.personas.append(persona)
            print(f"      -> {ptype}: {persona['id']}")
        
        json_path = os.path.join(self.data_dir, "simpersonas.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.personas, f, indent=2, ensure_ascii=False)
        print(f"\n   [SAVED] data/simpersonas.json")
    
    def step2_create_persona_cards(self):
        """Generate persona card PNGs"""
        print("\n[STEP 2] CREATING PERSONA CARDS")
        print("-" * 60)
        
        existing_cards = [f for f in os.listdir(self.cards_dir) if f.endswith('.png')] if os.path.exists(self.cards_dir) else []
        
        if len(existing_cards) >= 4:
            print(f"   [INFO] Found {len(existing_cards)} existing persona cards")
            skip = input("   Skip card generation? (y/n): ").strip().lower()
            if skip == 'y':
                print(f"   [SKIP] Skipping persona card generation")
                return
        
        for persona in self.personas:
            card_path = os.path.join(self.cards_dir, f"{persona['id']}.png")
            try:
                PersonaCardGenerator.create_card(persona, card_path)
                print(f"   [IMAGE] Created: {os.path.basename(card_path)}")
            except Exception as e:
                print(f"   [WARNING] Card error: {e}")
        
        print(f"\n   [SAVED] data/persona_cards/")
    
    def step3_simulate_tasks(self):
        """Simulate browser interactions with GPT-generated actions"""
        print("\n[STEP 3] SIMULATING INTERACTIONS (GPT-4 Driven)")
        print("-" * 60)
        
        type_labels = {
            "novice": "Novice User",
            "expert": "Expert User",
            "distracted": "Distracted User",
            "accessibility-focused": "Accessibility User"
        }
        
        task_labels = {
            "login": "Login Form",
            "checkout": "Checkout Form",
            "profile": "Profile Update"
        }
        
        task_descriptions = {
            "login": "a login form with username, password fields and a login button",
            "checkout": "a checkout form with name and address fields and a place order button",
            "profile": "a profile update form with a name field and save button"
        }
        
        interfaces = [
            ("login", "Login", os.path.join(self.interfaces_dir, "login.html")),
            ("checkout", "Checkout", os.path.join(self.interfaces_dir, "checkout.html")),
            ("profile", "Profile", os.path.join(self.interfaces_dir, "profile.html"))
        ]
        
        for persona in self.personas:
            for interface_type, interface_name, file_path in interfaces:
                print(f"\n   [SIM] {persona['type']} -> {interface_name}")
                
                if not os.path.exists(file_path):
                    print(f"      [WARNING] File not found: {file_path}")
                    continue
                
                # Generate action plan using GPT-4
                action_plan = self.action_generator.generate_actions(
                    persona, 
                    interface_type, 
                    task_descriptions[interface_type]
                )
                
                if not action_plan:
                    print(f"      [WARNING] No actions generated")
                    continue
                
                simulator = BrowserSimulator(headless=False)
                try:
                    simulator.load_page(file_path)
                    
                    before_path = os.path.join(self.screenshots_dir, f"{persona['type']}_{interface_type}_before.png")
                    simulator.take_screenshot(before_path)
                    
                    # Execute the GPT-generated action plan
                    executed_actions = simulator.execute_actions(action_plan)
                    
                    time.sleep(1)
                    after_path = os.path.join(self.screenshots_dir, f"{persona['type']}_{interface_type}_after.png")
                    simulator.take_screenshot(after_path)
                    
                    # Log actions with error tracking
                    error_count = len([a for a in executed_actions if a['action'] == 'error'])
                    success = 'error' not in [a['action'] for a in executed_actions[-3:]] if executed_actions else False
                    
                    action_summary = "; ".join([f"{a['action']}({a['target']})" for a in executed_actions[:5]])
                    if len(executed_actions) > 5:
                        action_summary += f" ... +{len(executed_actions)-5} more"
                    
                    self.action_logs.append({
                        "persona_id": persona['id'],
                        "persona_label": type_labels.get(persona['type'], persona['type']),
                        "task": interface_type,
                        "task_label": task_labels.get(interface_type, interface_name),
                        "steps_count": len(executed_actions),
                        "errors": error_count,
                        "success": 1 if success else 0,
                        "actions": action_summary,
                        "estimated_time": len(executed_actions) * 2.5
                    })
                    
                    print(f"      [OK] Completed: {len(executed_actions)} actions, {error_count} errors")
                    
                except Exception as e:
                    print(f"      [ERROR] Error: {e}")
                finally:
                    simulator.close()
                    time.sleep(2)
        
        csv_path = os.path.join(self.data_dir, "simpersona_actions.csv")
        if self.action_logs:
            df = pd.DataFrame(self.action_logs)
            df.to_csv(csv_path, index=False)
            print(f"\n   [SAVED] data/simpersona_actions.csv")
    
    def step4_generate_reports(self):
        """Generate analysis reports"""
        print("\n[STEP 4] GENERATING REPORTS")
        print("-" * 60)
        
        if not self.action_logs:
            print("   [WARNING] No action logs")
            return
        
        df = pd.DataFrame(self.action_logs)
        
        print("\n   [METRICS] SUMMARY")
        print("   " + "-" * 56)
        print(f"   {'Persona':<20} {'Steps':<8} {'Errors':<8} {'Success'}")
        print("   " + "-" * 56)
        
        for persona_label in df['persona_label'].unique():
            pdata = df[df['persona_label'] == persona_label]
            if len(pdata) > 0:
                steps = int(pdata['steps_count'].mean())
                errors = int(pdata['errors'].sum())
                success_rate = (pdata['success'].sum() / len(pdata)) * 100
                print(f"   {persona_label:<20} {steps:<8} {errors:<8} {success_rate:.0f}%")
        
        excel_path = os.path.join(self.base_dir, "SimPersona_Analysis.xlsx")
        try:
            with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                summary = df.groupby('persona_label').agg({
                    'steps_count': 'mean',
                    'errors': 'sum',
                    'success': 'mean'
                }).reset_index()
                summary['success'] = (summary['success'] * 100).round(1)
                summary.columns = ['Persona', 'Avg Steps', 'Total Errors', 'Success Rate (%)']
                summary.to_excel(writer, sheet_name='Summary', index=False)
                df.to_excel(writer, sheet_name='Detailed Actions', index=False)
            
            print(f"\n   [SAVED] SimPersona_Analysis.xlsx")
        except Exception as e:
            print(f"   [WARNING] Excel error: {e}")
    
    def run_complete_pipeline(self):
        """Run all steps"""
        print("\n" + "="*60)
        print("SimPersona - GPT-4 Powered Research Pipeline")
        print("="*60)
        
        self.step1_generate_personas()
        self.step2_create_persona_cards()
        self.step3_simulate_tasks()
        self.step4_generate_reports()
        
        print("\n" + "="*60)
        print("[SUCCESS] PIPELINE COMPLETE!")
        print("="*60)
        print(f"\n[DIR] All files saved in: {self.base_dir}")
        print(f"\n[FILES] Generated files:")
        print(f"   [OK] data/simpersonas.json")
        print(f"   [OK] data/simpersona_actions.csv")
        print(f"   [OK] data/persona_cards/ (4 PNG files)")
        print(f"   [OK] screenshots/ (24 PNG files)")
        print(f"   [OK] SimPersona_Analysis.xlsx")
        print(f"\n[INFO] All personas and actions were AI-generated by GPT-4")
        print(f"\n[WEB] Open index.html in browser to view dashboard!")
        print(f"[PATH] Full path: {os.path.join(self.base_dir, 'index.html')}")


def main():
    print("="*60)
    print("SimPersona - GPT-4 Powered Research Pipeline")
    print("="*60)
    print("\n[REQUIRED] This pipeline requires GPT-4 API access")
    print("   No fallback modes available\n")
    
    # Check OpenAI library
    if not OPENAI_AVAILABLE:
        print("[ERROR] OpenAI library not installed")
        print("   Run: pip install openai")
        print("\n[STOP] Cannot proceed without OpenAI library")
        return
    
    # Check API key
    api_key = OPENAI_API_KEY
    if not api_key or api_key == "your-api-key-here":
        print("[ERROR] No valid API key found")
        print("   Set OPENAI_API_KEY environment variable, or")
        print("   Add your key at line 20 in Code.py")
        print("\n[STOP] Cannot proceed without valid API key")
        return
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print(f"[OK] API Key found: {api_key[:15]}...{api_key[-4:]}")
    print(f"[OK] Mode: 100% GPT-4 Powered")
    print(f"   - Personas: AI-generated")
    print(f"   - Actions: AI-generated with realistic errors")
    
    # Check folder structure
    data_dir = os.path.join(os.getcwd(), "data")
    interfaces_dir = os.path.join(data_dir, "interfaces")
    
    print(f"\n[CHECK] Folder structure...")
    
    if not os.path.exists(interfaces_dir):
        print(f"[ERROR] Missing: data/interfaces/ folder")
        print(f"   Create: {interfaces_dir}")
        print(f"   Add files: login.html, checkout.html, profile.html")
        print("\n[STOP] Cannot proceed without interface files")
        return
    
    required_files = [
        ("login.html", os.path.join(interfaces_dir, "login.html")),
        ("checkout.html", os.path.join(interfaces_dir, "checkout.html")),
        ("profile.html", os.path.join(interfaces_dir, "profile.html"))
    ]
    
    missing = []
    for name, full_path in required_files:
        if not os.path.exists(full_path):
            missing.append(name)
    
    if missing:
        print(f"[ERROR] Missing HTML files in data/interfaces/:")
        for f in missing:
            print(f"   - {f}")
        print("\n[STOP] Cannot proceed without all interface files")
        return
    
    print(f"[OK] All interface files found")
    
    # Confirm before running (since it will use API credits)
    print("\n" + "-"*60)
    print("[WARNING] This will use your OpenAI API credits")
    print("-"*60)
    
    confirm = input("\n[CONFIRM] Proceed with GPT-4 powered simulation? (yes/no): ").strip().lower()
    
    if confirm not in ['yes', 'y']:
        print("\n[CANCELLED] Pipeline cancelled by user")
        return
    
    print("\n[START] Initializing GPT-4 powered pipeline...")
    
    try:
        pipeline = SimPersonaPipeline(api_key=api_key)
        pipeline.run_complete_pipeline()
    except Exception as e:
        print(f"\n[ERROR] Pipeline failed: {e}")
        print("\nPossible issues:")
        print("   - Invalid API key")
        print("   - Insufficient API credits")
        print("   - Network connection issues")
        print("   - Rate limit exceeded")

if __name__ == "__main__":
    main()
