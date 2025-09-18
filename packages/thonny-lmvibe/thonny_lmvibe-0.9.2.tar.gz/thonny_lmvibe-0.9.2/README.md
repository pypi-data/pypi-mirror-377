![](src/thonnycontrib/lmvibe/LMvibe2.png) 

# Thonny LMvibe Vibe Coding AI Assistant

**LMvibe - Your "little man's vibe" coding AI assistant, seamlessly integrated into the Thonny IDE.**

LMvibe brings the power of large language models directly into your favorite beginner-friendly IDE. It's designed to make coding a more creative, conversational, and less frustrating experience.

![](screenshot.png)

---

### Why is "Vibe Coding" with LMvibe in Thonny so Cool?

Thonny is the go-to IDE for learners, and LMvibe supercharges that experience. It's not just a chatbot; it's a coding partner that understands your context and directly generates / updates your code.

*   **For Beginners and Kids:** Coding can be intimidating. Getting stuck on a weird error message is frustrating. LMvibe turns that frustration into a learning opportunity. Instead of searching the web for cryptic errors, you can just ask your vibe assistant in plain English: "Why is this not working?" It makes coding feel less like a rigid science and more like a creative conversation.

*   **For Embedded Systems Users (MicroPython/CircuitPython):** Prototyping with microcontrollers is all about speed and iteration. LMvibe is a massive productivity booster. You can ask it to generate boilerplate code for a specific sensor (like an I2C BME280 sensor), explain a hardware protocol, or help you debug code that interacts with GPIO pins. It's like having an experienced hardware engineer by your side.

---

### Installation

Installing LMvibe is simple using Thonny's built-in plug-in manager.

1.  In Thonny, navigate to `Tools > Manage plug-ins...`.
2.  In the search bar, type `thonny-lmvibe` and press Enter.
3.  Click the `Install` button.
4.  Restart Thonny completely. You will now see the "LMvibe" panel at the bottom of the IDE.

### Configuration

Before you can use the assistant, you need to configure it with your API key.

1.  Navigate to `Tools > Options...`.
2.  Go to the `LMvibe` tab.
3.  Enter your Google AI API Key. You can get one from [Google AI Studio](https://aistudio.google.com/app/apikey).
4.  Click "Fetch Models" and select a suitable model (e.g., a `gemini-pro` model) from the dropdown.
5.  Click `OK`. You are now ready to start coding!

---

### How It Works: The Power of Context

The most powerful feature of LMvibe is its **context awareness**. When you ask a "Code-aware" or "Error Follow-up" question, the assistant doesn't just see your question—**it sees the entire, most recent version of your code in the active editor.** 

This is a game-changer. It means the AI understands all your variables, functions, and the overall structure of your script. This allows it to give you highly accurate, relevant answers that are specific to *your* project, not generic solutions you'd find online.

Make no mistake: in order to keep cost and complexity down, LMvibe is **one file only**, it will only keep track of your currently open and active code tab and is prompted to create on-file code only: exactly what you need for fast projects.

### API and Future Development

Currently, LMvibe is powered by the **Google Gemini API**. It provides a fantastic balance of power and accessibility.

The architecture is designed to be flexible. In the future, support for other APIs (like those from OpenAI, Anthropic, or local models) could be added to give users more choice.

---

### The 6 Main Functions

You can interact with LMvibe using six intuitive icon-based buttons. Each has a specific purpose to streamline your workflow.

| Logo (Filename) | Function | Description |
| :--- | :--- | :--- |
| ![](src/thonnycontrib/lmvibe/LMvibe1.png) | **Single Question** | This is for general questions that don't relate to your code. Ask it anything from "How does a Python dictionary work?" to "Give me an idea for a fun beginner project." |
| ![](src/thonnycontrib/lmvibe/LMvibe2.png) | **Code-aware Question** <br> *(Shortcut: Ctrl+Enter)* | This is the primary function. It sends your question **along with the entire code from your current editor**. Use this to ask "How can I optimize this function?" or "Add comments to explain my code." |
| ![](src/thonnycontrib/lmvibe/LMvibe3.png) | **Error Follow-up** | When you get an error in the Thonny shell, use this button. It sends your question, your full code, **and the last 20 lines from the shell**. Perfect for asking "What does this error mean and how do I fix it?" |
| ![](src/thonnycontrib/lmvibe/LMvibe4.png) | **Revert to Previous Code** | Made a change you don't like after asking a code-aware question? This button instantly reverts the code in your editor back to the version you had *before* the assistant made changes. It's a simple and safe undo. |
| ![](src/thonnycontrib/lmvibe/LMvibe5.png) | **Update Code in Editor** | If the assistant provides a Python code block in its answer, this button will automatically and completely replace the content of your editor with the new code. It's a fast way to apply the suggested fixes or additions. |
| ![](src/thonnycontrib/lmvibe/LMvibe6.png) | **Clear History** | This button clears the entire conversation history from the LMvibe panel. Use it to start a fresh conversation or to clean up the interface. |

In addition, LMvibe lets you select a passage in your code and then right-click on "Explain..." to interrogate the AI about the passage.

---

This project is licensed under the MIT License.