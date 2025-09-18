# -*- coding: utf-8 -*-
"""
LMvibe - Little Mans Vibe Coding AI Assistant for Thonny.

This plugin integrates an AI coding assistant into the Thonny IDE, using
generative AI to help users write, debug, and understand Python code.
It features a chat interface, context-awareness of the editor and shell,
and Markdown rendering for clear responses.
"""

# Standard library imports
import json
import logging
import os
import queue
import re
import threading
import tkinter as tk
from tkinter import messagebox, ttk
from tkinter.scrolledtext import ScrolledText
from typing import Dict, List, Optional, Iterator
import importlib.resources
from abc import ABC, abstractmethod

# Third-party imports
try:
    import google.generativeai as genai
    from google.generativeai.types import GenerationConfig
except ImportError:
    genai = None  # Handle missing dependency gracefully.

try:
    import openai
except ImportError:
    openai = None # Handle missing dependency gracefully

try:
    import ollama
except ImportError:
    ollama = None # Handle missing dependency gracefully

try:
    from markdown_it import MarkdownIt
except ImportError:
    MarkdownIt = None  # Handle missing dependency gracefully.

# Thonny imports
from thonny import get_shell, get_workbench, THONNY_USER_DIR, ui_utils
from thonny.config_ui import ConfigurationPage
from thonny.languages import tr
from thonny.misc_utils import running_on_mac_os
from thonny.shell import ShellMenu

# Setup logging for the plugin
logger = logging.getLogger(__name__)

# --- Constants ---
ASSISTANT_USER_DIR = os.path.join(THONNY_USER_DIR, "lmvibe_assistant")
HISTORY_FILE = os.path.join(ASSISTANT_USER_DIR, "history.json")
MAX_HISTORY = 50  # Maximum number of messages to keep in the conversation history.

SYSTEM_PROMPT = (
    "You are LMvibe, an expert Python coding assistant integrated into the Thonny IDE. "
    "Your primary role is to help users write, understand, and debug Python code. "
    "Follow these instructions carefully:\n"
    "1.  **Expertise**: Act as an expert Python programmer. All code you "
    "provide must be Python unless the user explicitly requests another language.\n"
    "2.  **Context**: The user may provide you with their latest code revision "
    "and shell errors. Use this context to provide relevant and accurate answers.\n"
    "3.  **Response Structure**: Structure your response in two parts:\n"
    "    a. First, a clear, descriptive block of your thoughts and explanations. "
    "Describe the changes you made, the reasoning behind them, or the answer "
    "to the user's question.\n"
    "    b. Second, a single, complete Python code block. This block should "
    "contain the full, updated code for the file, not just snippets, "
    "corrections, or diffs.\n"
    "Only return the code block when you are asked to create or correct code. When you"
    "are only asked to explain, you can omit the code block\n"
    "4.  **Completeness**: Always output the entire code file. Do not omit "
    "parts of the code you didn't change. The user will use your output to "
    "replace their entire editor content.\n"
    "5.  **Clarity**: Be concise and clear in your explanations. If the user's "
    "request is ambiguous, ask for clarification."
)


# =============================================================================
# AI Service Abstraction Layer
# =============================================================================

class AIService(ABC):
    """Abstract Base Class defining the interface for an AI service."""
    def __init__(self, **kwargs):
        pass

    @abstractmethod
    def list_models(self, **kwargs) -> List[str]:
        """Fetch a list of compatible model names from the AI service."""
        pass

    @abstractmethod
    def send_message_stream(
        self,
        model_name: str,
        history: List[Dict[str, str]],
        prompt: str,
        **kwargs
    ) -> Iterator[Dict[str, any]]:
        """Send a prompt and stream the response from the AI model."""
        pass

class GeminiService(AIService):
    """An implementation of AIService for Google's Gemini models."""

    def list_models(self, api_key: str, **kwargs) -> List[str]:
        if not genai:
            raise RuntimeError("google-generativeai library is not installed.")
        genai.configure(api_key=api_key)
        all_models = genai.list_models()
        return sorted([
            m.name.replace("models/", "") for m in all_models
            if 'generateContent' in m.supported_generation_methods and "gemini" in m.name
        ])

    def send_message_stream(
        self,
        model_name: str,
        history: List[Dict[str, str]],
        prompt: str,
        api_key: str,
        **kwargs
    ) -> Iterator[Dict[str, any]]:
        if not genai:
            raise RuntimeError("google-generativeai library is not installed.")
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_name, system_instruction=SYSTEM_PROMPT)
            history_for_gemini = [
                {"role": "model" if m["role"] == "assistant" else "user", "parts": [m["content"]]}
                for m in history
            ]
            chat = model.start_chat(history=history_for_gemini)
            response = chat.send_message(
                prompt, stream=True, generation_config=GenerationConfig(temperature=0.7)
            )
            for chunk in response:
                try:
                    if chunk.text:
                        yield {"type": "chunk", "content": chunk.text}
                except (ValueError, IndexError):
                    logger.warning(f"Stream chunk issue detected: {chunk}", exc_info=True)
                    if hasattr(chunk, 'prompt_feedback') and chunk.prompt_feedback.block_reason:
                        yield {"type": "error", "content": f"Response blocked: {chunk.prompt_feedback.block_reason.name}"}
                        break
            usage_info = response.usage_metadata or {}
            yield {"type": "end", "usage": {
                "prompt_tokens": usage_info.prompt_token_count if hasattr(usage_info, 'prompt_token_count') else 0,
                "response_tokens": usage_info.candidates_token_count if hasattr(usage_info, 'candidates_token_count') else 0,
            }}
        except Exception as e:
            logger.error(f"Error during Gemini API call: {e}", exc_info=True)
            yield {"type": "error", "content": str(e)}
            yield {"type": "end", "usage": {}}

class OpenAIService(AIService):
    """Implementation for OpenAI-compatible APIs (ChatGPT, LMStudio)."""
    def __init__(self, base_url: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self._base_url = base_url

    def list_models(self, api_key: str, **kwargs) -> List[str]:
        if not openai:
            raise RuntimeError("openai library is not installed.")
        client = openai.OpenAI(api_key=api_key, base_url=self._base_url)
        try:
            models_response = client.models.list()
            models = [m.id for m in models_response.data]

            if self._base_url and "localhost" in self._base_url and not models:
                return ["<Load a model in LM Studio first>"]

            if self._base_url and "api.openai.com" in self._base_url:
                 return sorted([m for m in models if "gpt" in m])

            return sorted(models)
        except Exception as e:
            logger.error(f"Failed to fetch OpenAI models: {e}")
            if self._base_url and "404" in str(e):
                return ["<Load a model in LM Studio first>"]
            raise e

    def send_message_stream(
        self,
        model_name: str,
        history: List[Dict[str, str]],
        prompt: str,
        api_key: str,
        **kwargs
    ) -> Iterator[Dict[str, any]]:
        if not openai:
            raise RuntimeError("openai library is not installed.")
        client = openai.OpenAI(api_key=api_key, base_url=self._base_url)
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history + [{"role": "user", "content": prompt}]
        try:
            stream = client.chat.completions.create(
                model=model_name, messages=messages, stream=True, temperature=0.7
            )
            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    yield {"type": "chunk", "content": content}
            yield {"type": "end", "usage": {}}
        except Exception as e:
            logger.error(f"Error during OpenAI API call: {e}", exc_info=True)
            yield {"type": "error", "content": str(e)}
            yield {"type": "end", "usage": {}}


class OllamaService(AIService):
    """Implementation for Ollama's local AI server using the official library."""
    def __init__(self, base_url: str = "http://localhost:11434", **kwargs):
        super().__init__(**kwargs)
        self._host = base_url

    def list_models(self, **kwargs) -> List[str]:
        """Fetches a list of locally available Ollama models."""
        if not ollama:
            raise RuntimeError("The 'ollama' library is not installed.")
        try:
            client = ollama.Client(host=self._host)
            models_info = client.list()


            # The ollama library returns a dictionary like {'models': [...]}.
            # Safely get the list of models, which may be empty if none are downloaded.
            models_list = models_info.get('models', [])

            return sorted([model.get('model',"ERROR") for model in models_list])

        except ollama.ResponseError as e:
            logger.error(f"Ollama API error at {self._host}: {e.status_code} - {e.error}", exc_info=True)
            raise RuntimeError(f"Ollama API error ({e.status_code}): {e.error}")
        except Exception as e:
            logger.error(f"Failed to fetch Ollama models from {self._host}: {e}", exc_info=True)
            raise RuntimeError(f"Could not connect to Ollama at {self._host}. Is it running? Details: {e}")

    def send_message_stream(
        self,
        model_name: str,
        history: List[Dict[str, str]],
        prompt: str,
        **kwargs
    ) -> Iterator[Dict[str, any]]:
        if not ollama:
            raise RuntimeError("The 'ollama' library is not installed.")
        messages = [{'role': 'system', 'content': SYSTEM_PROMPT}] + history + [{'role': 'user', 'content': prompt}]
        try:
            client = ollama.Client(host=self._host)
            stream = client.chat(model=model_name, messages=messages, stream=True)
            for chunk in stream:
                content = chunk['message'].get('content')
                if content:
                    yield {"type": "chunk", "content": content}
                if chunk.get('done'):
                    usage = {
                        "prompt_tokens": chunk.get('prompt_eval_count', 0),
                        "response_tokens": chunk.get('eval_count', 0),
                    }
                    yield {"type": "end", "usage": usage}
                    break
        except Exception as e:
            logger.error(f"Error during Ollama API call: {e}", exc_info=True)
            yield {"type": "error", "content": str(e)}
            yield {"type": "end", "usage": {}}

# --- Service Registry ---
AI_SERVICES = {
    "Google Gemini": {"class": GeminiService, "requires": "api_key"},
    "OpenAI (ChatGPT)": {"class": OpenAIService, "requires": "api_key"},
    "Ollama": {"class": OllamaService, "requires": "base_url"},
    "LMStudio": {"class": OpenAIService, "requires": "base_url"},
}
DEFAULT_BASE_URLS = {
    "Ollama": "http://localhost:11434",
    "LMStudio": "http://localhost:1234/v1",
}


# =============================================================================
# GUI Components
# =============================================================================

class LMvibeConfigPage(ConfigurationPage):
    """The configuration page for LMvibe, managing settings for all providers."""

    def __init__(self, master):
        super().__init__(master)
        self._service_var = get_workbench().get_variable("lmvibe_assistant.service")
        self._provider_settings_var = get_workbench().get_variable("lmvibe_assistant.provider_settings")
        self._settings_data = json.loads(self._provider_settings_var.get())
        self._api_key_var = tk.StringVar()
        self._base_url_var = tk.StringVar()
        self._model_var = tk.StringVar()
        self._previous_service = self._service_var.get()
        self._model_list_queue: queue.Queue = queue.Queue()
        self._setup_ui()
        self._load_settings_for_service(self._service_var.get())

    def _setup_ui(self):
        pad_x, pad_y = 10, 5
        self.columnconfigure(1, weight=1)

        service_label = ttk.Label(self, text=tr("AI Service:"), anchor="w")
        service_label.grid(row=0, column=0, padx=(0, pad_x), pady=pad_y, sticky="w")
        self._service_combo = ttk.Combobox(
            self, textvariable=self._service_var, state="readonly", values=list(AI_SERVICES.keys())
        )
        self._service_combo.grid(row=0, column=1, pady=pad_y, sticky="ew")
        self._service_combo.bind("<<ComboboxSelected>>", self._on_service_change)

        self._api_key_label = ttk.Label(self, text=tr("API Key:"), anchor="w")
        self._api_key_entry = ttk.Entry(self, textvariable=self._api_key_var, show="*", width=50)
        ui_utils.create_tooltip(self._api_key_entry, tr("Enter your API key from the selected service"))

        self._base_url_label = ttk.Label(self, text=tr("Server URL:"), anchor="w")
        self._base_url_entry = ttk.Entry(self, textvariable=self._base_url_var, width=50)
        ui_utils.create_tooltip(self._base_url_entry, tr("URL of your local AI server (e.g., for Ollama, LMStudio)"))

        model_label = ttk.Label(self, text=tr("Model:"), anchor="w")
        model_label.grid(row=3, column=0, padx=(0, pad_x), pady=pad_y, sticky="w")
        combobox_frame = ttk.Frame(self)
        combobox_frame.grid(row=3, column=1, pady=pad_y, sticky="ew")
        combobox_frame.columnconfigure(0, weight=1)
        self._model_combo = ttk.Combobox(
            combobox_frame, textvariable=self._model_var, state="readonly", values=[tr("<Select a service first>")]
        )
        self._model_combo.grid(row=0, column=0, sticky="ew", padx=(0, pad_x))
        self._fetch_button = ttk.Button(
            combobox_frame, text=tr("Fetch Models"), command=self._start_fetch_models
        )
        self._fetch_button.grid(row=0, column=1, sticky="e")

    def _on_service_change(self, event=None):
        self._save_settings_for_service(self._previous_service)
        new_service = self._service_var.get()
        self._load_settings_for_service(new_service)
        self._previous_service = new_service

    def _load_settings_for_service(self, service_name: str):
        if not service_name:
            return

        service_settings = self._settings_data.get(service_name, {})

        self._api_key_var.set(service_settings.get("api_key", ""))
        self._base_url_var.set(service_settings.get("base_url", DEFAULT_BASE_URLS.get(service_name, "")))
        self._model_var.set(service_settings.get("model", ""))
        self._model_combo.configure(values=[self._model_var.get()] if self._model_var.get() else [tr("<Click 'Fetch Models'>")])

        self._api_key_label.grid_remove()
        self._api_key_entry.grid_remove()
        self._base_url_label.grid_remove()
        self._base_url_entry.grid_remove()

        requirement = AI_SERVICES.get(service_name, {}).get("requires")
        if requirement == "api_key":
            self._api_key_label.grid(row=1, column=0, padx=(0, 10), pady=5, sticky="w")
            self._api_key_entry.grid(row=1, column=1, pady=5, sticky="ew")
            self._api_key_label.configure(text=f"{service_name.replace(' (ChatGPT)', '')} API Key:")
        elif requirement == "base_url":
            self._base_url_label.grid(row=2, column=0, padx=(0, 10), pady=5, sticky="w")
            self._base_url_entry.grid(row=2, column=1, pady=5, sticky="ew")

    def _save_settings_for_service(self, service_name: str):
        if not service_name:
            return

        if service_name not in self._settings_data:
            self._settings_data[service_name] = {}

        self._settings_data[service_name]["api_key"] = self._api_key_var.get()
        self._settings_data[service_name]["base_url"] = self._base_url_var.get()
        self._settings_data[service_name]["model"] = self._model_var.get()

    def apply(self):
        self._save_settings_for_service(self._service_var.get())
        self._provider_settings_var.set(json.dumps(self._settings_data, indent=2))
        return True

    def _start_fetch_models(self, show_error: bool = True):
        service_name = self._service_var.get()
        api_key = self._api_key_var.get().strip()
        base_url = self._base_url_var.get().strip()

        if not service_name:
            if show_error: messagebox.showerror(tr("Error"), tr("Please select an AI service."), parent=self)
            return

        requirement = AI_SERVICES[service_name].get("requires")
        if requirement == "api_key" and not api_key:
            if show_error: messagebox.showerror(tr("Error"), tr("API Key cannot be empty."), parent=self)
            return
        if requirement == "base_url" and not base_url:
            if show_error: messagebox.showerror(tr("Error"), tr("Server URL cannot be empty."), parent=self)
            return

        self._fetch_button.configure(state="disabled")
        self._model_combo.configure(values=[tr("<Fetching...>")])
        self.update_idletasks()

        args = (service_name, api_key, base_url, show_error)
        threading.Thread(target=self._fetch_models_thread, args=args, daemon=True).start()
        self._check_model_list_queue()

    def _fetch_models_thread(self, service_name: str, api_key: str, base_url: str, show_error: bool):
        try:
            service_info = AI_SERVICES[service_name]
            service_class = service_info["class"]

            if service_name == "LMStudio":
                service_instance = service_class(base_url=base_url)
                model_ids = service_instance.list_models(api_key="lm-studio")
            else:
                service_instance = service_class(base_url=base_url)
                model_ids = service_instance.list_models(api_key=api_key)

            if not model_ids:
                model_ids = [tr("<No compatible models found>")]
            self._model_list_queue.put({"success": True, "models": model_ids})
        except Exception as e:
            logger.error(f"Failed to fetch models: {e}", exc_info=True)
            self._model_list_queue.put({"success": False, "error": str(e), "show_error": show_error})

    def _check_model_list_queue(self):
        try:
            result = self._model_list_queue.get_nowait()
            self._fetch_button.configure(state="normal")
            if result["success"]:
                models = result["models"]
                current_model = self._model_var.get()
                self._model_combo.configure(values=models)
                if current_model in models:
                    self._model_var.set(current_model)
                elif models and not models[0].startswith("<"):
                    self._model_var.set(models[0])
                else:
                    self._model_var.set("")
            else:
                self._model_combo.configure(values=[tr("<Fetch failed>")])
                self._model_var.set("")
                if result.get("show_error", True):
                    messagebox.showerror(tr("Error Fetching Models"), result["error"], parent=self)
        except queue.Empty:
            self.after(100, self._check_model_list_queue)

class LMvibeAssistantView(ttk.Frame):
    """The main view for the LMvibe assistant, containing the chat display and input."""

    def __init__(self, master):
        super().__init__(master)
        self._message_queue: queue.Queue = queue.Queue()
        self._conversation_history: List[Dict[str, str]] = []
        self._current_ai_response_accumulator: str = ""
        self._is_streaming: bool = False
        self._code_cache: Optional[str] = None
        self._last_action: Optional[str] = None
        self._last_assistant_response_start_index: Optional[str] = None
        self._ai_service: Optional[AIService] = None
        self._markdown = MarkdownIt() if MarkdownIt else None
        self._setup_styles()
        self._load_button_images()
        self._load_history()
        self._setup_ui()
        self._check_queue()

    def _setup_styles(self):
        style = ttk.Style(self)
        style.configure("Flat.TButton", borderwidth=0, relief="flat", padding=0)
        style.map("Flat.TButton", background=[("active", style.lookup("TButton", "lightcolor"))])

    def _load_button_images(self):
        self._button_images: Dict[str, tk.PhotoImage] = {}
        image_mapping = {
            "single": "LMvibe1.png", "code_aware": "LMvibe2.png", "error": "LMvibe3.png",
            "revert": "LMvibe4.png", "update": "LMvibe5.png", "clear": "LMvibe6.png",
        }
        for name, filename in image_mapping.items():
            try:
                with importlib.resources.path('thonnycontrib.lmvibe', filename) as path:
                    img = tk.PhotoImage(file=str(path))
                    img = img.subsample(2, 2)
                    self._button_images[name] = img
            except (FileNotFoundError, tk.TclError) as e:
                logger.error(f"Failed to load image {filename}: {e}", exc_info=True)
                self._button_images[name] = None

    def _setup_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self._text_area = ScrolledText(self, wrap=tk.WORD, state="disabled", bd=0, padx=5, pady=5)
        self._text_area.grid(row=0, column=0, sticky="nsew")
        self._setup_text_area_tags()
        self._render_history()
        self._text_menu = ui_utils.TextMenu(self._text_area)
        self._text_area.bind("<Button-2>" if running_on_mac_os() else "<Button-3>", self._show_text_menu, True)

        input_frame = ttk.Frame(self)
        input_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        input_frame.columnconfigure(0, weight=1)

        self._input_text = ScrolledText(
            input_frame, height=4, wrap=tk.WORD, highlightthickness=1,
            highlightbackground="light grey", insertbackground="black"
        )
        self._input_text.grid(row=0, column=0, sticky="ew", columnspan=2)
        self._input_text.bind("<Control-Return>", self._handle_ctrl_enter)

        action_button_frame = ttk.Frame(input_frame)
        action_button_frame.grid(row=1, column=0, sticky="w", pady=(5, 0))
        util_button_frame = ttk.Frame(input_frame)
        util_button_frame.grid(row=1, column=1, sticky="e", pady=(5, 0))

        self._btn_single = self._create_button(action_button_frame, "single", tr("Single Question"), self._send_single_question)
        self._btn_code_aware = self._create_button(action_button_frame, "code_aware", tr("Code-aware Question (Ctrl+Enter)"), self._send_code_aware_question)
        self._btn_error_followup = self._create_button(action_button_frame, "error", tr("Error Follow-up"), self._send_error_follow_up)
        self._btn_revert_code = self._create_button(util_button_frame, "revert", tr("Revert to Previous Code"), self._revert_editor_code, state="disabled")
        self._btn_update_editor = self._create_button(util_button_frame, "update", tr("Update Code in Editor"), self._update_editor_code)
        self._clear_button = self._create_button(util_button_frame, "clear", tr("Clear History"), self._clear_conversation)

        self._token_label_var = tk.StringVar()
        token_label = ttk.Label(input_frame, textvariable=self._token_label_var, anchor="e")
        token_label.grid(row=0, column=1, sticky="se", padx=5)

    def _create_button(self, parent, name, tooltip_text, command, state="normal"):
        button = ttk.Button(
            parent, image=self._button_images.get(name), style="Flat.TButton",
            command=command, state=state
        )
        button.pack(side="left", padx=(0, 5))
        ui_utils.create_tooltip(button, tooltip_text)
        return button

    def _handle_ctrl_enter(self, event=None):
        self._send_code_aware_question()
        return "break"

    def _show_text_menu(self, event):
        self._text_menu.tk_popup(event.x_root, event.y_root)

    def _toggle_all_controls(self, enabled: bool):
        state = "normal" if enabled else "disabled"
        for btn in [self._btn_single, self._btn_code_aware, self._btn_error_followup, self._btn_update_editor, self._clear_button]:
            btn.config(state=state)
        self._input_text.config(state="normal" if enabled else "disabled")
        self._btn_revert_code.config(state="normal" if enabled and self._code_cache else "disabled")

    def _send_message(self, user_prompt: str, code_context: Optional[str] = None, shell_context: Optional[str] = None):
        wb = get_workbench()
        service_name = wb.get_option("lmvibe_assistant.service")

        try:
            provider_settings_str = wb.get_option("lmvibe_assistant.provider_settings")
            all_settings = json.loads(provider_settings_str)
            service_settings = all_settings.get(service_name, {})
        except (json.JSONDecodeError, KeyError):
            messagebox.showerror(tr("Configuration Error"), tr("Could not load settings. Please configure the plugin."), parent=self)
            return

        model_name = service_settings.get("model")
        api_key = service_settings.get("api_key")
        base_url = service_settings.get("base_url")

        if not service_name or not model_name or "<" in model_name:
            messagebox.showerror(tr("Configuration Error"), tr("Please select a service and a valid model in Tools > Options > LMvibe."), parent=self)
            return

        try:
            service_class = AI_SERVICES[service_name]["class"]
            self._ai_service = service_class(base_url=base_url)
        except KeyError:
            messagebox.showerror(tr("Configuration Error"), tr(f"AI service '{service_name}' is not recognized."), parent=self)
            return

        self._add_message_to_history("user", user_prompt)
        self._render_message("user", user_prompt)
        self._input_text.delete("1.0", tk.END)
        self._toggle_all_controls(False)
        self._token_label_var.set("")

        self._text_area.configure(state="normal")
        self._text_area.insert(tk.END, f"\n\n{tr('Assistant')}:", ("assistant_message", "bold"))
        self._last_assistant_response_start_index = self._text_area.index(tk.INSERT)
        self._text_area.configure(state="disabled")
        self._text_area.see(tk.END)

        self._current_ai_response_accumulator = ""
        self._is_streaming = True

        full_api_prompt = user_prompt
        if code_context:
            full_api_prompt += f"\n\nHere is the current code:\n```python\n{code_context}\n```"
        if shell_context:
            full_api_prompt += f"\n\nHere is the recent shell output/error:\n```\n{shell_context}\n```"

        api_args = {
            "model_name": model_name, "history": self._conversation_history[:-1],
            "prompt": full_api_prompt, "api_key": api_key,
        }
        threading.Thread(target=self._call_api_thread, kwargs=api_args, daemon=True).start()

    def _call_api_thread(self, **kwargs):
        if not self._ai_service: return
        stream = self._ai_service.send_message_stream(**kwargs)
        for event in stream:
            self._message_queue.put(event)

    def _check_queue(self):
        try:
            message = self._message_queue.get_nowait()
            msg_type = message.get("type")
            if msg_type == "chunk":
                self._handle_stream_chunk(message["content"])
            elif msg_type == "end":
                self._handle_stream_end(message.get("usage", {}))
            elif msg_type == "error":
                self._handle_stream_error(message["content"])
        except queue.Empty:
            pass
        finally:
            self.after(100, self._check_queue)

    def _handle_stream_chunk(self, content: str):
        self._text_area.configure(state="normal")
        self._text_area.insert(tk.END, content)
        self._text_area.configure(state="disabled")
        self._text_area.see(tk.END)
        self._current_ai_response_accumulator += content

    def _handle_stream_end(self, usage: dict):
        self._is_streaming = False
        self._toggle_all_controls(True)
        full_response = self._current_ai_response_accumulator
        if full_response:
            self._add_message_to_history("assistant", full_response)
            self._rerender_last_message_as_markdown(full_response)
            if self._last_action in ["code_aware", "error"]:
                self._update_editor_code(auto_confirm=True)
        if usage and any(usage.values()):
            token_str = f"Tokens: {usage.get('prompt_tokens', 0)} in / {usage.get('response_tokens', 0)} out"
            self._token_label_var.set(token_str)
        self._current_ai_response_accumulator = ""
        self._last_action = None

    def _handle_stream_error(self, error_content: str):
        self._is_streaming = False
        self._toggle_all_controls(True)
        self._render_message("error", error_content, is_error=True)
        self._current_ai_response_accumulator = ""
        self._last_action = None

    def _rerender_last_message_as_markdown(self, full_response: str):
        display_content = full_response
        if self._last_action in ["code_aware", "error"]:
            placeholder = f"\n\n[{tr('Code was automatically updated in the editor.')}]"
            display_content = re.sub(r"```python\n.*?\n```", placeholder, full_response, flags=re.DOTALL)
        self._text_area.configure(state="normal")
        if self._last_assistant_response_start_index:
            self._text_area.delete(self._last_assistant_response_start_index, tk.END)
            self._render_markdown(display_content)
            self._last_assistant_response_start_index = None
        else:
            self._render_markdown(display_content)
        self._text_area.configure(state="disabled")
        self._text_area.see(tk.END)

    def _render_markdown(self, md_text: str):
        if not self._markdown:
            self._text_area.insert(tk.END, "\n" + md_text)
            return
        try:
            tokens = self._markdown.parse(md_text)
            active_tags = []
            is_in_list = False
            for token in tokens:
                if token.type.endswith("_open"):
                    tag_name = token.type.replace("_open", "")
                    if tag_name.startswith("heading"):
                        self._text_area.insert(tk.END, "\n\n")
                        active_tags.append(f"h{token.tag[1]}")
                    elif tag_name == "paragraph" and not is_in_list: self._text_area.insert(tk.END, "\n")
                    elif "list" in tag_name: is_in_list = True
                    elif tag_name == "list_item": self._text_area.insert(tk.END, "\n•  ", ("list_item",))
                    elif tag_name == "strong": active_tags.append("bold")
                    elif tag_name == "em": active_tags.append("italic")
                elif token.type.endswith("_close"):
                    tag_name = token.type.replace("_close", "")
                    if tag_name.startswith("heading") and f"h{token.tag[1]}" in active_tags: active_tags.remove(f"h{token.tag[1]}")
                    elif "list" in tag_name: is_in_list = False
                    elif tag_name == "strong" and "bold" in active_tags: active_tags.remove("bold")
                    elif tag_name == "em" and "italic" in active_tags: active_tags.remove("italic")
                elif token.type == "text": self._text_area.insert(tk.END, token.content, tuple(active_tags))
                elif token.type == "code_inline": self._text_area.insert(tk.END, token.content, tuple(active_tags + ["code"]))
                elif token.type == "fence":
                    self._text_area.insert(tk.END, "\n\n")
                    self._text_area.insert(tk.END, token.content, ("code_block",))
                    self._add_code_copy_button(token.content)
                    self._text_area.insert(tk.END, "\n")
                elif token.type == "softbreak": self._text_area.insert(tk.END, "\n")
                elif token.type == "inline" and token.children:
                    for child in token.children:
                        child_tags = list(active_tags)
                        if child.type == "text": self._text_area.insert(tk.END, child.content, tuple(child_tags))
                        elif child.type == "code_inline": self._text_area.insert(tk.END, child.content, tuple(child_tags + ["code"]))
                        elif child.type.startswith("strong"): child_tags.append("bold")
                        elif child.type.startswith("em"): child_tags.append("italic")
        except Exception as e:
            logger.error(f"Markdown rendering error: {e}", exc_info=True)
            self._text_area.insert(tk.END, "\n" + md_text)

    def _add_code_copy_button(self, code_content: str):
        button_frame = ttk.Frame(self._text_area)
        copy_button = ttk.Button(button_frame, text=tr("Copy Code"), command=lambda c=code_content: self._copy_to_clipboard(c))
        copy_button.pack(side=tk.LEFT)
        self._text_area.insert(tk.END, "\n", ())
        self._text_area.window_create(tk.INSERT + "-1c", window=button_frame, padx=20, pady=3, align="bottom")

    def _copy_to_clipboard(self, text: str):
        self.clipboard_clear()
        self.clipboard_append(text)

    def _send_single_question(self):
        user_prompt = self._input_text.get("1.0", tk.END).strip()
        if user_prompt:
            self._last_action = "single"
            self._send_message(user_prompt)

    def _send_code_aware_question(self):
        user_prompt = self._input_text.get("1.0", tk.END).strip()
        if not user_prompt: return
        editor_code = self._get_editor_content()
        if editor_code is None: return
        self._code_cache = editor_code
        self._btn_revert_code.config(state="normal")
        self._last_action = "code_aware"
        self._send_message(user_prompt, code_context=editor_code)

    def _send_error_follow_up(self):
        user_prompt = self._input_text.get("1.0", tk.END).strip()
        if not user_prompt: return
        editor_code = self._get_editor_content()
        if editor_code is None: return
        self._code_cache = editor_code
        self._btn_revert_code.config(state="normal")
        shell_content = self._get_shell_content()
        self._last_action = "error"
        self._send_message(user_prompt, code_context=editor_code, shell_context=shell_content)

    def _update_editor_code(self, auto_confirm: bool = False):
        if not self._conversation_history:
            return
        last_message = self._conversation_history[-1]
        if last_message.get("role") != "assistant":
            if not auto_confirm:
                messagebox.showinfo(tr("Information"), tr("The last message is not from the assistant."), parent=self)
            return
        content = last_message.get("content", "")
        code_blocks = re.findall(r"```python\n(.*?)\n```", content, re.DOTALL)
        if not code_blocks:
            if not auto_confirm:
                messagebox.showinfo(tr("Information"), tr("No Python code block found in the last response."), parent=self)
            return
        new_code = max(code_blocks, key=len)
        editor = get_workbench().get_editor_notebook().get_current_editor()
        if not editor:
            if not auto_confirm:
                messagebox.showwarning(tr("No Active Editor"), tr("Please open an editor to update the code."), parent=self)
            return
        if auto_confirm or messagebox.askyesno(tr("Confirm Code Update"), tr("Replace the entire content of the current editor?")):
            text_widget = editor.get_text_widget()
            text_widget.delete("1.0", tk.END)
            text_widget.insert("1.0", new_code)
            editor.focus_set()

    def _revert_editor_code(self):
        if not self._code_cache:
            messagebox.showinfo(tr("Information"), tr("No previous code version is cached."), parent=self)
            return
        editor = get_workbench().get_editor_notebook().get_current_editor()
        if not editor:
            messagebox.showwarning(tr("No Active Editor"), tr("Please open an editor to revert the code."), parent=self)
            return
        if messagebox.askyesno(tr("Confirm Revert"), tr("Revert the code in the editor to its previous version?")):
            text_widget = editor.get_text_widget()
            text_widget.delete("1.0", tk.END)
            text_widget.insert("1.0", self._code_cache)
            self._code_cache = None
            self._btn_revert_code.config(state="disabled")

    def _clear_conversation(self):
        if messagebox.askyesno(tr("Clear Conversation"), tr("Are you sure?")):
            self._text_area.configure(state="normal")
            self._text_area.delete("1.0", tk.END)
            self._text_area.configure(state="disabled")
            self._conversation_history = []
            self._save_history()
            self._token_label_var.set("")
            self._code_cache = None
            self._btn_revert_code.config(state="disabled")

    def _add_message_to_history(self, role: str, content: str):
        message = {"role": role, "content": content}
        if role == "assistant": message["action"] = self._last_action
        self._conversation_history.append(message)
        if len(self._conversation_history) > MAX_HISTORY:
            self._conversation_history = self._conversation_history[-MAX_HISTORY:]
        self._save_history()

    def _save_history(self):
        try:
            os.makedirs(ASSISTANT_USER_DIR, exist_ok=True)
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(self._conversation_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save history: {e}", exc_info=True)

    def _load_history(self):
        if not os.path.exists(HISTORY_FILE):
            self._conversation_history = []
            return
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                history = json.load(f)
            if isinstance(history, list):
                placeholder = f"\n[{tr('Code block removed from history on restart')}]\n"
                for message in history:
                    if message.get("role") == "assistant":
                        message["content"] = re.sub(r"```python\n.*?\n```", placeholder, message.get("content", ""), flags=re.DOTALL)
                self._conversation_history = history
            else: self._conversation_history = []
        except Exception as e:
            logger.error(f"Failed to load or clean history: {e}", exc_info=True)
            self._conversation_history = []

    def _render_history(self):
        self._text_area.configure(state="normal")
        self._text_area.delete("1.0", tk.END)
        for msg in self._conversation_history:
            self._render_message(msg.get("role"), msg.get("content"), action=msg.get("action"))
        self._text_area.configure(state="disabled")
        self._text_area.see(tk.END)

    def _render_message(self, role: str, content: str, is_error: bool = False, action: Optional[str] = None):
        if self._is_streaming and role == "assistant" and not is_error: return
        self._text_area.configure(state="normal")
        if is_error:
            self._text_area.insert(tk.END, f"\n{tr('Error')}:\n", ("error_message", "bold"))
            self._text_area.insert(tk.END, content + "\n", ("error_message",))
        elif role == "user":
            self._text_area.insert(tk.END, f"\n\n{tr('You')}:\n", ("user_message", "bold"))
            self._text_area.insert(tk.END, content, ("user_message",))
        elif role == "assistant":
            self._text_area.insert(tk.END, f"\n\n{tr('Assistant')}:\n", ("assistant_message", "bold"))
            self._render_markdown(content)
        self._text_area.configure(state="disabled")
        if not self._is_streaming: self._text_area.see(tk.END)

    def _get_editor_content(self) -> Optional[str]:
        editor = get_workbench().get_editor_notebook().get_current_editor()
        if not editor:
            messagebox.showwarning(tr("No Active Editor"), tr("Please open an editor tab first."), parent=self)
            return None
        return editor.get_text_widget().get("1.0", tk.END)

    def _get_shell_content(self) -> str:
        shell = get_shell()
        if not shell: return ""
        lines = shell.text.get("1.0", tk.END).strip().split('\n')
        return "\n".join(lines[-20:])

    def _setup_text_area_tags(self):
        default_font = tk.font.nametofont("TkDefaultFont").copy()
        bold_font = default_font.copy(); bold_font.configure(weight="bold")
        italic_font = default_font.copy(); italic_font.configure(slant="italic")
        code_font = tk.font.nametofont("TkFixedFont").copy()
        default_size = default_font.cget("size")
        code_font.configure(size=default_size)
        h1_font = default_font.copy(); h1_font.configure(size=int(default_size * 1.5), weight="bold")
        h2_font = default_font.copy(); h2_font.configure(size=int(default_size * 1.3), weight="bold")
        self._text_area.tag_configure("h1", font=h1_font, spacing1=10, spacing3=5)
        self._text_area.tag_configure("h2", font=h2_font, spacing1=8, spacing3=4)
        self._text_area.tag_configure("bold", font=bold_font)
        self._text_area.tag_configure("italic", font=italic_font)
        self._text_area.tag_configure("code", font=code_font, background="#f0f0f0")
        self._text_area.tag_configure("code_block", font=code_font, background="#f5f5f5", lmargin1=20, lmargin2=20, spacing1=5, spacing3=5, borderwidth=1, relief="sunken")
        self._text_area.tag_configure("user_message", foreground="dark green", spacing3=5)
        self._text_area.tag_configure("assistant_message", foreground="black", spacing3=10)
        self._text_area.tag_configure("error_message", foreground="red", font=italic_font)
        self._text_area.tag_configure("list_item", lmargin1=20, lmargin2=20)


# =============================================================================
# Thonny Plugin Integration
# =============================================================================

def _explain_selection_with_lmvibe(source: str):
    text_widget = get_workbench().get_editor_notebook().get_current_editor().get_text_widget() if source == 'editor' else get_shell().text
    if not text_widget: return
    try:
        selected_text = text_widget.get(tk.SEL_FIRST, tk.SEL_LAST).strip()
        view = get_workbench().get_view("LMvibeAssistantView", create=True)
        if selected_text and isinstance(view, LMvibeAssistantView):
            get_workbench().show_view("LMvibeAssistantView")
            prompt = f"{tr('Explain the following selected code')}:\n\n```python\n{selected_text}\n```"
            view._last_action = "single"
            view._send_message(prompt)
    except tk.TclError: pass

def _selection_exists(source: str) -> bool:
    text_widget = get_workbench().get_editor_notebook().get_current_editor().get_text_widget() if source == 'editor' else get_shell().text
    if not text_widget: return False
    try:
        return bool(text_widget.tag_ranges(tk.SEL))
    except tk.TclError:
        return False

def load_plugin():
    """Entry point for the Thonny plugin."""
    if not MarkdownIt:
        logger.warning("LMvibe plugin disabled. Missing core dependency: 'markdown-it-py'.")
        return
    if not any([genai, openai, ollama]):
        logger.warning("LMvibe disabled: Please install at least one AI library: 'google-generativeai', 'openai', or 'ollama'.")
        return

    wb = get_workbench()

    wb.set_default("lmvibe_assistant.service", "Google Gemini")
    wb.set_default("lmvibe_assistant.provider_settings", "{}")

    if wb.get_option("lmvibe_assistant.api_key") is not None:
        logger.info("Migrating old LMvibe settings to new structured format.")
        old_api_key = wb.get_option("lmvibe_assistant.api_key", "")
        old_model = wb.get_option("lmvibe_assistant.model", "")

        migrated_settings = {
            "Google Gemini": {"api_key": old_api_key, "model": old_model, "base_url": ""}
        }
        wb.set_option("lmvibe_assistant.provider_settings", json.dumps(migrated_settings, indent=2))

        wb.set_option("lmvibe_assistant.api_key", None)
        wb.set_option("lmvibe_assistant.model", None)
        wb.set_option("lmvibe_assistant.base_url", None)

    wb.add_view(LMvibeAssistantView, "LMvibe", "w")
    wb.add_configuration_page("LMvibe", "LMvibe", LMvibeConfigPage, 90)

    try:
        with importlib.resources.path('thonnycontrib.lmvibe', "LMvibeicon.png") as icon_path:
            icon = str(icon_path)
    except FileNotFoundError:
        icon = None

    wb.add_command(
        command_id="show_lmvibe", menu_name="view", command_label="Show LMvibe",
        handler=lambda: get_workbench().show_view("LMvibeAssistantView"),
        image=icon, include_in_toolbar=True, caption="LMVibe Assistant", group=50
    )
    wb.add_command(
        command_id="explain_editor_selection_with_lmvibe", menu_name="edit",
        command_label=tr("Explain with LMvibe"),
        handler=lambda: _explain_selection_with_lmvibe('editor'),
        tester=lambda: _selection_exists('editor'), group=150
    )

    original_add_extra_items = ShellMenu.add_extra_items
    def patched_add_extra_items(shell_menu):
        original_add_extra_items(shell_menu)
        shell_menu.add_separator()
        shell_menu.add_command(
            label=tr("Explain with LMvibe"),
            command=lambda: _explain_selection_with_lmvibe('shell'),
            tester=lambda: _selection_exists('shell')
        )
    ShellMenu.add_extra_items = patched_add_extra_items

    logger.info("LMvibe plugin loaded successfully.")
