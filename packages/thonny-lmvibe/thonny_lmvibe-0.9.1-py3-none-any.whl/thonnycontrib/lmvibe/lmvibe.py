# -*- coding: utf-8 -*-

# Standard library imports
import json
import locale
import logging
import os
import queue
import re
import threading
import tkinter as tk
from tkinter import messagebox, ttk
from tkinter.scrolledtext import ScrolledText
from typing import Dict, List, Optional
import importlib.resources

# Third-party imports
try:
    import google.generativeai as genai
    from google.generativeai.types import GenerationConfig
except ImportError:
    messagebox.showerror(
        "Missing Dependency",
        "The 'google-generativeai' library is required. "
        "Please install it (Tools > Manage plug-ins...).",
    )
    genai = None

try:
    from markdown_it import MarkdownIt
except ImportError:
    messagebox.showerror(
        "Missing Dependency",
        "The 'markdown-it-py' library is required. "
        "Please install it (Tools > Manage plug-ins...).",
    )
    MarkdownIt = None

# Thonny imports
from thonny import get_shell, get_workbench, THONNY_USER_DIR, ui_utils
from thonny.config_ui import ConfigurationPage
from thonny.languages import tr
from thonny.misc_utils import running_on_mac_os
from thonny.shell import ShellMenu

# Setup logging
logger = logging.getLogger(__name__)

# --- Constants ---
ASSISTANT_USER_DIR = os.path.join(THONNY_USER_DIR, "lmvibe_assistant")
HISTORY_FILE = os.path.join(ASSISTANT_USER_DIR, "history.json")
MAX_HISTORY = 50

SYSTEM_PROMPT = (
    "You are LMvibe, the 'little mans vibe Assistant', an expert Python coding assistant integrated into the Thonny IDE. "
    "Your primary role is to help users write, understand, and debug Python code. "
    "Follow these instructions carefully:\n"
    "1.  **Expertise**: Act as an expert Python programmer. All code you provide must be Python unless the user explicitly requests another language.\n"
    "2.  **Context**: The user may provide you with their latest code revision and shell errors. Use this context to provide relevant and accurate answers.\n"
    "3.  **Response Structure**: Structure your response in two parts:\n"
    "    a. First, a clear, descriptive block of your thoughts and explanations. Describe the changes you made, the reasoning behind them, or the answer to the user's question.\n"
    "    b. Second, a single, complete Python code block. This block should contain the full, updated code for the file, not just snippets, corrections, or diffs.\n"
    "4.  **Completeness**: Always output the entire code file. Do not omit parts of the code you didn't change. The user will use your output to replace their entire editor content.\n"
    "5.  **Clarity**: Be concise and clear in your explanations. If the user's request is ambiguous, ask for clarification."
)


# --- Configuration Page ---

class LMvibeConfigPage(ConfigurationPage):
    def __init__(self, master):
        super().__init__(master)
        self._api_key_var = get_workbench().get_variable("lmvibe_assistant.api_key")
        self._model_var = get_workbench().get_variable("lmvibe_assistant.model")
        self._model_list_queue: queue.Queue = queue.Queue()

        pad_x, pad_y, label_width = 10, 5, 15
        api_key_label = ttk.Label(self, text=tr("Google AI API Key:"), width=label_width, anchor="w")
        api_key_label.grid(row=0, column=0, padx=(0, pad_x), pady=pad_y, sticky="w")
        self._api_key_entry = ttk.Entry(self, textvariable=self._api_key_var, show="*", width=50)
        self._api_key_entry.grid(row=0, column=1, pady=pad_y, sticky="ew")
        ui_utils.create_tooltip(self._api_key_entry, tr("Enter your API key from Google AI Studio"))
        model_label = ttk.Label(self, text=tr("Model:"), width=label_width, anchor="w")
        model_label.grid(row=1, column=0, padx=(0, pad_x), pady=pad_y, sticky="w")
        combobox_frame = ttk.Frame(self)
        combobox_frame.grid(row=1, column=1, pady=pad_y, sticky="ew")
        combobox_frame.columnconfigure(0, weight=1)
        self._model_combo = ttk.Combobox(combobox_frame, textvariable=self._model_var, state="readonly", values=[tr("<Click 'Fetch Models'>")])
        self._model_combo.grid(row=0, column=0, sticky="ew", padx=(0, pad_x))
        ui_utils.create_tooltip(self._model_combo, tr("Select the Gemini model to use"))
        self._fetch_button = ttk.Button(combobox_frame, text=tr("Fetch Models"), command=self._start_fetch_models)
        self._fetch_button.grid(row=0, column=1, sticky="e")
        ui_utils.create_tooltip(self._fetch_button, tr("Fetch available models using the API key"))
        self.columnconfigure(1, weight=1)
        if self._api_key_var.get():
            self._start_fetch_models(show_error=False)

    def _start_fetch_models(self, show_error=True):
        if not genai:
            if show_error: messagebox.showerror(tr("Error"), tr("The 'google-generativeai' library is missing."), parent=self)
            return
        api_key = self._api_key_var.get().strip()
        if not api_key:
            if show_error: messagebox.showerror(tr("Error"), tr("Google AI API Key cannot be empty."), parent=self)
            return
        self._fetch_button.configure(state="disabled")
        self._model_combo.configure(values=[tr("<Fetching...>")])
        self.update_idletasks()
        threading.Thread(target=self._fetch_models_thread, args=(api_key, show_error), daemon=True).start()
        self._check_model_list_queue()

    def _fetch_models_thread(self, api_key: str, show_error: bool):
        try:
            genai.configure(api_key=api_key)
            model_ids = sorted([m.name.replace("models/", "") for m in genai.list_models() if 'generateContent' in m.supported_generation_methods and "gemini" in m.name])
            if not model_ids: model_ids = [tr("<No compatible models found>")]
            self._model_list_queue.put({"success": True, "models": model_ids})
        except Exception as e:
            logger.error(f"Failed to fetch Gemini models: {e}", exc_info=True)
            error_message = tr("An unexpected error occurred.")
            if "API key not valid" in str(e): error_message = tr("API key not valid. Please check your key.")
            self._model_list_queue.put({"success": False, "error": error_message, "show_error": show_error})

    def _check_model_list_queue(self):
        try:
            result = self._model_list_queue.get_nowait()
            self._fetch_button.configure(state="normal")
            if result["success"]:
                models = result["models"]
                current_model = self._model_var.get()
                self._model_combo.configure(values=models)
                if current_model in models: self._model_var.set(current_model)
                elif models and not "<" in models: self._model_var.set(models)
                else: self._model_var.set("")
            else:
                self._model_combo.configure(values=[tr("<Fetch failed>")])
                self._model_var.set("")
                if result.get("show_error", True): messagebox.showerror(tr("Error Fetching Models"), result["error"], parent=self)
        except queue.Empty:
            self.after(100, self._check_model_list_queue)

    def apply(self): return True


# --- LMvibe Assistant View ---

class LMvibeAssistantView(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self._message_queue: queue.Queue = queue.Queue()
        self._conversation_history: List[Dict[str, str]] = []
        self._markdown = MarkdownIt() if MarkdownIt else None
        self._current_ai_response_accumulator = ""
        self._is_streaming = False
        self._code_cache: Optional[str] = None
        self._last_action: Optional[str] = None
        self._last_assistant_response_start_index: Optional[str] = None
        
        self._setup_styles()
        self._load_button_images()
        self._load_history()

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)

        self._text_area = ScrolledText(self, wrap=tk.WORD, state="disabled", bd=0, padx=5, pady=5)
        self._text_area.grid(row=0, column=0, sticky="nsew")
        self._setup_text_area_tags()
        self._render_history()

        input_frame = ttk.Frame(self)
        input_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        input_frame.columnconfigure(0, weight=1)

        self._input_text = ScrolledText(
            input_frame, height=4, wrap=tk.WORD, 
            highlightthickness=1, highlightbackground="light grey",
            insertbackground="black" 
        )
        self._input_text.grid(row=0, column=0, sticky="ew", columnspan=2)
        self._input_text.bind("<Control-Return>", self._handle_ctrl_enter)

        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=1, column=0, sticky="ew", pady=(5, 0))
        
        # --- Create Buttons with Images and Tooltips ---
        img_single = self._button_images.get("single")
        self._btn_single = ttk.Button(button_frame, 
                                      image=img_single,
                                      style="Flat.TButton",
                                      command=self._send_single_question)
        self._btn_single.pack(side="left", padx=(0, 5))
        ui_utils.create_tooltip(self._btn_single, tr("Single Question"))

        img_code_aware = self._button_images.get("code_aware")
        self._btn_code_aware = ttk.Button(button_frame, 
                                          image=img_code_aware,
                                          style="Flat.TButton",
                                          command=self._send_code_aware_question)
        self._btn_code_aware.pack(side="left", padx=(0, 5))
        ui_utils.create_tooltip(self._btn_code_aware, tr("Code-aware Question (Ctrl+Enter)"))

        img_error = self._button_images.get("error")
        self._btn_error_followup = ttk.Button(button_frame, 
                                              image=img_error,
                                              style="Flat.TButton",
                                              command=self._send_error_follow_up)
        self._btn_error_followup.pack(side="left")
        ui_utils.create_tooltip(self._btn_error_followup, tr("Error Follow-up"))
        
        util_frame = ttk.Frame(input_frame)
        util_frame.grid(row=1, column=1, sticky="e", pady=(5,0))
        
        img_revert = self._button_images.get("revert")
        self._btn_revert_code = ttk.Button(util_frame, 
                                           image=img_revert,
                                           style="Flat.TButton",
                                           command=self._revert_editor_code, state="disabled")
        self._btn_revert_code.pack(side="left", padx=(0, 5))
        ui_utils.create_tooltip(self._btn_revert_code, tr("Revert to Previous Code"))
        
        img_update = self._button_images.get("update")
        self._btn_update_editor = ttk.Button(util_frame, 
                                             image=img_update,
                                             style="Flat.TButton",
                                             command=self._update_editor_code)
        self._btn_update_editor.pack(side="left", padx=(0, 10))
        ui_utils.create_tooltip(self._btn_update_editor, tr("Update Code in Editor"))
        
        img_clear = self._button_images.get("clear")
        self._clear_button = ttk.Button(util_frame, 
                                        image=img_clear,
                                        style="Flat.TButton",
                                        command=self._clear_conversation)
        self._clear_button.pack(side="left")
        ui_utils.create_tooltip(self._clear_button, tr("Clear History"))

        self._token_label_var = tk.StringVar()
        token_label = ttk.Label(input_frame, textvariable=self._token_label_var, anchor="e")
        token_label.grid(row=0, column=1, sticky="se", padx=5)

        self._text_menu = ui_utils.TextMenu(self._text_area)
        self._text_area.bind("<Button-2>" if running_on_mac_os() else "<Button-3>", self._show_text_menu, True)

        self._check_queue()

    def _setup_styles(self):
        style = ttk.Style(self)
        style.configure("Flat.TButton", borderwidth=0, relief="flat", focuscolor=style.lookup("TButton", "background"))
        style.map("Flat.TButton", background=[("active", style.lookup("TButton", "lightcolor"))])
        
    def _handle_ctrl_enter(self, event=None):
        self._send_code_aware_question()
        return "break"

    def _load_button_images(self):
        self._button_images = {}
    
        image_mapping = {
            "single": "LMvibe1.png",
            "code_aware": "LMvibe2.png",
            "error": "LMvibe3.png",
            "revert": "LMvibe4.png",
            "update": "LMvibe5.png",
            "clear": "LMvibe6.png",
        }

        for name, filename in image_mapping.items():
            try:
                # Greift sicher auf die Bilddateien innerhalb des installierten Pakets zu
                with importlib.resources.path('thonnycontrib.lmvibe', filename) as path:
                    img = tk.PhotoImage(file=str(path))
                    img = img.subsample(2, 2)  # Make image half size
                    self._button_images[name] = img
            except (FileNotFoundError, tk.TclError) as e:
                logger.error(f"Failed to load image {filename}: {e}")
                self._button_images[name] = None
    
    def _toggle_buttons(self, enabled: bool):
        state = "normal" if enabled else "disabled"
        self._btn_single.config(state=state)
        self._btn_code_aware.config(state=state)
        self._btn_error_followup.config(state=state)
        self._btn_update_editor.config(state=state)
        self._clear_button.config(state=state)
        self._input_text.config(state="normal" if enabled else "disabled")
        if enabled and self._code_cache:
            self._btn_revert_code.config(state="normal")
        else:
            self._btn_revert_code.config(state="disabled")

    def _show_text_menu(self, event): self._text_menu.tk_popup(event.x_root, event.y_root)

    def _send_single_question(self):
        user_prompt = self._input_text.get("1.0", tk.END).strip()
        if not user_prompt: return
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
        if not self._conversation_history: return
        last_message = self._conversation_history[-1]
        if last_message.get("role") != "assistant":
            if not auto_confirm: messagebox.showinfo(tr("Information"), tr("The last message is not from the assistant."), parent=self)
            return
        content = last_message.get("content", "")
        match = re.search(r"```python\n(.*?)\n```", content, re.DOTALL)
        if not match:
            if not auto_confirm: messagebox.showinfo(tr("Information"), tr("No Python code block found in the last response."), parent=self)
            return
        new_code = match.group(1)
        editor = get_workbench().get_editor_notebook().get_current_editor()
        if not editor:
            if not auto_confirm: messagebox.showwarning(tr("No Active Editor"), tr("Please open an editor to update the code."), parent=self)
            return
        if auto_confirm or messagebox.askyesno(tr("Confirm Code Update"), tr("Are you sure you want to replace the entire content of the current editor?")):
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
        if messagebox.askyesno(tr("Confirm Revert"), tr("Are you sure you want to revert the code in the editor to its previous version?")):
            text_widget = editor.get_text_widget()
            text_widget.delete("1.0", tk.END)
            text_widget.insert("1.0", self._code_cache)
            self._code_cache = None
            self._btn_revert_code.config(state="disabled")

    def _send_message(self, user_prompt: str, code_context: Optional[str] = None, shell_context: Optional[str] = None):
        if not genai or not MarkdownIt: return
        api_key = get_workbench().get_option("lmvibe_assistant.api_key")
        model_name = get_workbench().get_option("lmvibe_assistant.model")
        if not api_key or not model_name or "<" in model_name:
            messagebox.showerror(tr("Configuration Error"), tr("Please configure API Key and select a model."), parent=self)
            return
        self._add_message_to_history("user", user_prompt)
        self._render_message("user", user_prompt)
        self._input_text.delete("1.0", tk.END)
        self._toggle_buttons(False)
        self._token_label_var.set("")
        
        self._text_area.configure(state="normal")
        self._text_area.insert(tk.END, f"\n\n{tr('Assistant')}:", ("assistant_message", "bold"))
        self._last_assistant_response_start_index = self._text_area.index(tk.INSERT)
        self._text_area.configure(state="disabled")
        self._text_area.see(tk.END)
        
        self._current_ai_response_accumulator = ""
        self._is_streaming = True
        full_api_prompt = user_prompt
        if code_context: full_api_prompt += f"\n\nHere is the current version of the code I'm working on:\n```python\n{code_context}\n```"
        if shell_context: full_api_prompt += f"\n\nHere is the recent output/error from the shell:\n```\n{shell_context}\n```"
        threading.Thread(target=self._call_api_thread, args=(api_key, model_name, full_api_prompt), daemon=True).start()

    def _call_api_thread(self, api_key: str, model_name: str, final_user_prompt: str):
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_name, system_instruction=SYSTEM_PROMPT)
            history_for_gemini = [{"role": "model" if m["role"] == "assistant" else "user", "parts": [m["content"]]} for m in self._conversation_history[:-1]]
            chat = model.start_chat(history=history_for_gemini)
            response = chat.send_message(final_user_prompt, stream=True, generation_config=GenerationConfig(temperature=0.7))
            for chunk in response:
                try:
                    if chunk.text:
                        self._message_queue.put({"type": "stream_chunk", "content": chunk.text})
                        self._current_ai_response_accumulator += chunk.text
                except (ValueError, IndexError):
                     logger.warning(f"Stream chunk issue detected: {chunk}", exc_info=True)
                     if hasattr(chunk, 'prompt_feedback') and chunk.prompt_feedback.block_reason:
                         self._message_queue.put({"type": "error", "content": f"{tr('Response blocked')}: {chunk.prompt_feedback.block_reason.name}"})
                         break
            usage_info = {}
            if response.usage_metadata:
                usage_info = {"prompt_tokens": response.usage_metadata.prompt_token_count, "response_tokens": response.usage_metadata.candidates_token_count}
            self._message_queue.put({"type": "stream_end", "usage": usage_info})
        except Exception as e:
            logger.error(f"Error during API call: {e}", exc_info=True)
            self._message_queue.put({"type": "error", "content": f"{tr('API error')}: {e}"})
            self._message_queue.put({"type": "stream_end", "usage": {}})

    def _check_queue(self):
        try:
            message = self._message_queue.get_nowait()
            if message["type"] == "stream_chunk":
                self._text_area.configure(state="normal")
                self._text_area.insert(tk.END, message["content"])
                self._text_area.configure(state="disabled")
                self._text_area.see(tk.END)
            elif message["type"] == "stream_end":
                self._is_streaming = False
                self._toggle_buttons(True)
                full_response = self._current_ai_response_accumulator
                if full_response:
                    self._add_message_to_history("assistant", full_response)
                    self._rerender_last_message_as_markdown(full_response)
                    if self._last_action in ["code_aware", "error"]:
                        self._update_editor_code(auto_confirm=True)
                usage = message.get("usage", {})
                if usage: self._token_label_var.set(f"Tokens: {usage.get('prompt_tokens', 0)} in / {usage.get('response_tokens', 0)} out")
                self._current_ai_response_accumulator = ""
                self._last_action = None
            elif message["type"] == "error":
                self._is_streaming = False
                self._toggle_buttons(True)
                self._render_message("error", message["content"], is_error=True)
                self._current_ai_response_accumulator = ""
                self._last_action = None
        except queue.Empty:
            pass
        finally:
            self.after(100, self._check_queue)
    
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

    def _add_message_to_history(self, role: str, content: str):
        message = {"role": role, "content": content}
        if role == "assistant":
            message["action"] = self._last_action
        self._conversation_history.append(message)
        if len(self._conversation_history) > MAX_HISTORY:
            self._conversation_history = self._conversation_history[-MAX_HISTORY:]
        self._save_history()

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
            if not self._is_streaming:
                self._text_area.insert(tk.END, f"\n\n{tr('Assistant')}:", ("assistant_message", "bold"))
                display_content = content
                if action in ["code_aware", "error"]:
                    placeholder = f"\n\n[{tr('Code was automatically updated in the editor.')}]"
                    display_content = re.sub(r"```python\n.*?\n```", placeholder, display_content, flags=re.DOTALL)
                self._render_markdown(display_content)
        self._text_area.configure(state="disabled")
        if not self._is_streaming: self._text_area.see(tk.END)
    
    def _render_markdown(self, md_text: str):
        if not self._markdown:
            self._text_area.insert(tk.END, "\n" + md_text)
            return
        
        try:
            tokens = self._markdown.parse(md_text)
            active_tags = []
            list_counters = [] 
            is_in_list = False

            for token in tokens:
                if token.type.endswith("_open"):
                    tag_name = token.type.replace("_open", "")
                    if tag_name.startswith("heading"):
                        self._text_area.insert(tk.END, "\n\n")
                        active_tags.append(f"h{token.tag}")
                    elif tag_name == "paragraph":
                        if not is_in_list:
                            self._text_area.insert(tk.END, "\n")
                    elif tag_name == "bullet_list":
                        is_in_list = True
                    elif tag_name == "ordered_list":
                        is_in_list = True
                        list_counters.append(token.meta.get('start', 1))
                    elif tag_name == "list_item":
                        self._text_area.insert(tk.END, "\n")
                        if list_counters:
                            counter = list_counters[-1]
                            self._text_area.insert(tk.END, f"{counter}. ", ("list_item",))
                            list_counters[-1] += 1
                        else:
                            self._text_area.insert(tk.END, "•  ", ("list_item",))
                    elif tag_name == "strong":
                        active_tags.append("bold")
                    elif tag_name == "em":
                        active_tags.append("italic")

                elif token.type.endswith("_close"):
                    tag_name = token.type.replace("_close", "")
                    if tag_name.startswith("heading"):
                        tag_to_remove = f"h{token.tag}"
                        if tag_to_remove in active_tags: active_tags.remove(tag_to_remove)
                    elif tag_name == "bullet_list":
                        is_in_list = False
                    elif tag_name == "ordered_list":
                        is_in_list = False
                        if list_counters: list_counters.pop()
                    elif tag_name == "strong":
                        if "bold" in active_tags: active_tags.remove("bold")
                    elif tag_name == "em":
                        if "italic" in active_tags: active_tags.remove("italic")

                elif token.type == "text":
                    self._text_area.insert(tk.END, token.content, tuple(active_tags))
                
                elif token.type == "code_inline":
                    self._text_area.insert(tk.END, token.content, tuple(active_tags + ["code"]))

                elif token.type == "fence":
                    self._text_area.insert(tk.END, "\n\n")
                    self._text_area.insert(tk.END, token.content, ("code_block",))
                    self._add_code_copy_button(token.content)
                    self._text_area.insert(tk.END, "\n")

                elif token.type == "softbreak":
                    self._text_area.insert(tk.END, "\n")
                
                elif token.type == "inline" and token.children:
                    for child in token.children:
                        if child.type == "text":
                            self._text_area.insert(tk.END, child.content, tuple(active_tags))
                        elif child.type == "code_inline":
                            self._text_area.insert(tk.END, child.content, tuple(active_tags + ["code"]))
                        elif child.type == "strong_open":
                            active_tags.append("bold")
                        elif child.type == "strong_close":
                            if "bold" in active_tags: active_tags.remove("bold")
                        elif child.type == "em_open":
                            active_tags.append("italic")
                        elif child.type == "em_close":
                            if "italic" in active_tags: active_tags.remove("italic")
                        elif child.type == "softbreak":
                            self._text_area.insert(tk.END, "\n")

        except Exception as e:
            logger.error(f"Markdown rendering error: {e}", exc_info=True)
            self._text_area.insert(tk.END, "\n" + md_text)

    def _add_code_copy_button(self, code_content: str):
        button_frame = ttk.Frame(self._text_area)
        copy_button = ttk.Button(button_frame, text=tr("Copy Code"), command=lambda c=code_content: self._copy_code(c))
        copy_button.pack(side=tk.LEFT)
        self._text_area.insert(tk.END, "\n", ())
        self._text_area.window_create(tk.INSERT + "-1c", window=button_frame, padx=20, pady=3, align="bottom")

    def _copy_code(self, code: str):
        self.clipboard_clear()
        self.clipboard_append(code)

    def _save_history(self):
        try:
            os.makedirs(ASSISTANT_USER_DIR, exist_ok=True)
            with open(HISTORY_FILE, "w", encoding="utf-8") as f: json.dump(self._conversation_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save history: {e}", exc_info=True)

    def _load_history(self):
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    self._conversation_history = json.load(f)
                
                if isinstance(self._conversation_history, list):
                    placeholder = f"\n[{tr('Code block removed from history on restart')}]\n"
                    for message in self._conversation_history:
                        if message.get("role") == "assistant":
                            content = message.get("content", "")
                            message["content"] = re.sub(r"```python\n.*?\n```", placeholder, content, flags=re.DOTALL)
                else:
                    self._conversation_history = []
            except Exception as e:
                logger.error(f"Failed to load or clean history: {e}", exc_info=True)
                self._conversation_history = []
        else:
            self._conversation_history = []


    def _render_history(self):
        self._text_area.configure(state="normal")
        self._text_area.delete("1.0", tk.END)
        for msg in self._conversation_history: 
            self._render_message(msg.get("role"), msg.get("content"), action=msg.get("action"))
        self._text_area.configure(state="disabled")
        self._text_area.see(tk.END)
    
    def _setup_text_area_tags(self):
        default_font = tk.font.nametofont("TkDefaultFont")
        bold_font = default_font.copy(); bold_font.configure(weight="bold")
        italic_font = default_font.copy(); italic_font.configure(slant="italic")
        code_font = tk.font.Font(family=get_workbench().get_option("view.editor_font_family"), size=get_workbench().get_option("view.editor_font_size") - 1)
        h1_font = default_font.copy(); h1_font.configure(size=int(default_font.cget("size") * 1.5), weight="bold")
        h2_font = default_font.copy(); h2_font.configure(size=int(default_font.cget("size") * 1.3), weight="bold")
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

# --- Thonny Integration ---

def _explain_selection_with_lmvibe(source: str):
    text_widget = None
    if source == 'editor':
        editor = get_workbench().get_editor_notebook().get_current_editor()
        if editor: text_widget = editor.get_text_widget()
    elif source == 'shell':
        shell = get_shell()
        if shell: text_widget = shell.text
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
    text_widget = None
    if source == 'editor':
        editor = get_workbench().get_editor_notebook().get_current_editor()
        if editor: text_widget = editor.get_text_widget()
    elif source == 'shell':
        shell = get_shell()
        if shell: text_widget = shell.text
    if not text_widget: return False
    try: return bool(text_widget.tag_ranges(tk.SEL))
    except tk.TclError: return False

def load_plugin():
    if genai is None or MarkdownIt is None:
        logger.warning("LMvibe plugin disabled due to missing dependencies.")
        return
    wb = get_workbench()
    wb.set_default("lmvibe_assistant.api_key", "")
    wb.set_default("lmvibe_assistant.model", "")
    wb.add_view(LMvibeAssistantView, "LMvibe", "w")
    wb.add_configuration_page("LMvibe", "LMvibe", LMvibeConfigPage, 90)
    wb.add_command(command_id="explain_editor_selection_with_lmvibe", menu_name="edit", command_label=tr("Explain with LMvibe"), handler=lambda: _explain_selection_with_lmvibe('editor'), tester=lambda: _selection_exists('editor'), group=150)
    original_add_extra_items = ShellMenu.add_extra_items
    def patched_add_extra_items(shell_menu):
        original_add_extra_items(shell_menu)
        shell_menu.add_separator()
        shell_menu.add_command(label=tr("Explain with LMvibe"), command=lambda: _explain_selection_with_lmvibe('shell'), tester=lambda: _selection_exists('shell'))
    ShellMenu.add_extra_items = patched_add_extra_items
    logger.info("LMvibe plugin loaded.")