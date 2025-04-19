# TC WD 1.4.4 Capstone Project: AI Therapy CLI

A terminal-based, private conversational AI assistant facilitating structured, multi-phase simulated therapy sessions, built using Python and the Urwid TUI library.


## Description

This command-line tool provides a private and secure environment for users to engage in text-based sessions with an AI assistant powered by the OpenAI API. It implements a structured **AI workflow** including optional AI-assisted biography generation (editable by the user), contextual therapy sessions based on the bio, session summarization, and history management. Users can manage their profiles, session history, and customize the AI's core prompts through an interactive terminal interface.


### Background

The TC WD 1.4.4 (Module 1 Sprint 4 Part 4) Capstone Project is a Python-based application that integrates key concepts learned in the Module:

- Sprint 1:
  - **Functions and Variables:** Used extensively throughout all modules for defining logic (e.g., `AIManager.get_response`, `TherapyMode.update_chat`, `User.from_dict`), storing state (e.g., `TherapyMode.messages`, `AppManager.active_user`), and passing data.
  - **Conditionals:** Crucial for controlling application flow (e.g., `if key == "enter":` in `handle_input`, `if user:` checks, API error handling `if attempt > max_retries:`, `if user.chat_history:` checks).
  - **Loops:** Used for processing lists (e.g., iterating through `self.messages` in `_build_message_widgets`, iterating through loaded user data in `UsersManager.load_users`, the `while True:` retry loop in `AIManager`).

- Sprint 2:
  - **Exceptions:** Custom exceptions defined (`managers/exceptions.py`) and standard exceptions handled robustly, especially for API calls (`AIManager`), user input/validation (`User`, modes), and file operations (`UsersManager`, `JSONFileHandler`). Global handling in `main.py`.
  - **Libraries:** Core libraries like `urwid` (TUI), `bcrypt` (hashing), `openai` (API), `logging`, `json`, `enum`, `dataclasses`, `re` (email validation), `uuid` are imported and utilized in relevant modules. `python-dotenv` for environment management.
  - **APIs:** Central feature implemented in `AIManager` to interact with the OpenAI external API (`client.responses.create`).
  - **Unit Tests:** Unit tests using `pytest` are implemented for the `User` model (`tests/test_user.py`), covering validation of fields (ID, name, email format) and the password+passcode hashing (`bcrypt`) and verification logic.

- Sprint 3:
  - **Files I/O:** Implemented via `utils/JSONFileHandler.py` for reading/writing user data and chat history persistence, used by `UsersManager`. Logging configured to write to `debug.log` in `main.py`.
  - **Object-Oriented Programming:** Key examples include:
    - Classes for managers (`AppManager`, `UsersManager`, `AIManager`).
    - Dataclass for data modeling (`User`, planned `Session`).
    - Base classes and Inheritance for UI modes (`BaseMode`, `ListMenuMode`, specific modes like `TherapyMode`).
    - Encapsulation of logic within classes.
  - **Version Control:** Project managed with Git (evidenced by `.gitignore` and repo link).

- Sprint 4:
  - **Regular Expressions:** Used in `User.is_valid_email` for email format validation.
  - **Recursion:** Not a prominent feature in the current implementation.
  - **Algorithms:** Implicit use (e.g., dictionary lookup O(1) in `UsersManager`; exponential backoff algorithm in `AIManager` retries). Data structures like lists and dictionaries are fundamental.


## Features

* **Secure User Authentication:** Register/login with password + passcode (`bcrypt` hashing).
* **Profile Management:** Edit name, email, credentials. Includes options to edit a personal biography directly or initiate an AI-assisted biography session.
* **AI-Assisted Biography:** An optional guided chat session helps users formulate a personal bio, summarized by AI. The resulting bio string is stored and can be manually edited in the Profile section.
* **Structured Therapy Sessions:** New sessions utilize the user's biography and the current conversation history for context-aware AI responses, guided by a configurable session prompt.
* **Explicit Session Completion:** An "End & Save Session" action in `TherapyMode` triggers AI summarization (using a configurable summary prompt) and saves the session transcript and summary permanently. (`Ctrl+D` cancels the current unsaved session).
* **Session History & Review:** Browse past saved sessions (`SessionsMode`), view AI-generated summaries upon selection, and load the full transcript into a dedicated viewer (`ViewSessionMode`).
* **Editable Prompts:** Configure AI behavior by viewing (`PromptsMode`) and editing (`EditPromptMode`) the system prompts used for Biography generation, Therapy sessions, and Summarization, accessible via the Profile section.
* **Persistent Storage:** All user data (profile, bio, prompts, sessions list with messages/summaries) stored locally in a single `users.json` file.
* **Terminal User Interface (TUI):** Built with `urwid`.
* **Mode Management:** Uses Python Enum (`ui/app_modes.py`) for clear state transitions managed by `AppManager`.


## Technology Stack

* **Language:** Python 3
* **TUI Library:** `urwid`
* **AI Backend:** OpenAI API (`openai` library)
* **Password Hashing:** `bcrypt`
* **Configuration/Secrets:** `python-dotenv`
* **Data Storage:** JSON


## Application Workflow

The application utilizes an AI-powered workflow orchestrated through distinct UI modes:

1.  **Login/Register:** Secure access.
2.  **Main Menu:** Entry point to "Therapy" (Sessions) and "Profile".
3.  **Profile:** Hub for editing user details, manually editing the **Biography**, viewing **Session History**, and editing **AI Prompts**. Includes a button to start/redo the AI-assisted Biography session.
4.  **Sessions:** Lists past sessions (shows summary on focus). Allows starting a **New Therapy Session** or selecting a past session to view its details.
5.  **View Session:** Read-only display of a selected past session's transcript and summary.
6.  **Prompts:** Lists editable prompts (Bio, Session, Summary). Selecting leads to editing.
7.  **Edit Prompt:** Allows modification and saving of the selected prompt text.
8.  **Therapy Session:** Chat interface using the selected session prompt and biography context. Must be explicitly ended via `[End & Save Session]` button to trigger summarization and persistent saving. `Ctrl+D` cancels the current session without saving.
9.  **(Bio Session):** The "Start/Update Biography Session" action uses the Therapy Session interface but with a specific 'bio' prompt and saves an AI summary to the user's biography field upon explicit completion via its own end/save action.


## Future Enhancements: Towards an AI Agent

While currently implemented as an AI workflow, future enhancements could introduce more autonomous "AI Agent" capabilities:

* **Tool Use (Function Calling):** Allow the AI to decide when to call predefined functions (e.g., `suggest_relaxation_exercise`, `summarize_session_so_far`) to provide richer interactions.
* **Retrieval Augmented Generation (RAG):** Enhance long-term memory by retrieving relevant information from past session summaries stored in a vector database to provide deeper context.


## Setup and Installation

1.  **Prerequisites:** Python 3.9+, `pip`, Git.
2.  **Clone:** `git clone https://github.com/justinasbaleisa/TC-jbalei-WD.1.4.4.git && cd TC-jbalei-WD.1.4.4`
3.  **Create/Activate Venv:** `python3 -m venv .venv && source .venv/bin/activate` (or equivalent for your OS)
4.  **Install Dependencies:** `pip install -r requirements.txt`
5.  **Configure API Key:** `cp secrets.env.example secrets.env` then edit `secrets.env` to add your `OPENAI_API_KEY`.


## Usage

1.  Ensure virtual environment is active (`source .venv/bin/activate`).
2.  Run: `python main.py`
3.  Follow prompts for login/register/navigation (Arrows, Enter).
4.  Use `Ctrl+D` for back/cancel actions (this discards the current unsaved therapy/bio session).
5.  Use the `[End & Save Session]` button in `TherapyMode` (or the equivalent action in Biography mode) to finalize and save a session/biography with its summary.


## Testing

* Unit tests for the `User` model are located in `tests/test_user.py`.
* Tests utilize the `pytest` framework (included in `requirements.txt`).
* **Run tests:**
    ```bash
    # Ensure venv is active
    pytest
    ```
    *(Note: The included `pytest.ini` ensures tests can correctly import project modules.)*


## Project Structure

.
├── data/                   # (gitignored) User data
│   └── users.json          # All user profiles, bio, prompts, sessions
├── managers/
│   ├── ai_manager.py       # OpenAI API interaction + summary logic
│   ├── exceptions.py
│   └── users_manager.py    # User object management + persistence
├── models/
│   ├── user.py             # User dataclass
│   └── session.py          # [New] Session dataclass
├── modes/
│   ├── base_mode.py
│   ├── list_menu_mode.py
│   ├── edit_prompt_mode.py # [New/Planned] Editor for prompts
│   ├── login_mode.py
│   ├── main_menu_mode.py
│   ├── profile_mode.py     # Handles profile fields, bio edit, hub
│   ├── prompts_mode.py     # [New/Planned] Lists prompts
│   ├── register_mode.py
│   ├── session_list_mode.py # [New/Planned] Lists sessions, shows summaries
│   ├── therapy_mode.py     # Handles active chat session + bio session variant
│   └── view_session_mode.py # [New/Planned] Displays full session transcript
├── tests/                  # Unit tests
│   └── test_user.py
├── ui/
│   ├── app_modes.py        # Enum for modes
│   ├── app_manager.py      # Main controller, dependency injection
│   └── app_widgets.py      # Custom Urwid widgets
├── utils/
│   └── JSONFileHandler.py  # JSON read/write helper
├── main.py                 # Entry point
├── requirements.txt        # Dependencies
├── secrets.env.example     # Example secrets file
├── .gitignore
├── pytest.ini              # Pytest configuration for paths
└── README.md               # This file


## GitHub Issues (Implementation Steps / Tasks Planned)

1.  **Branch:** `feature/session-model`
    **Summary:** Define `Session` dataclass.
    * Create `models/session.py`. Implement `Session` (id, start_time, messages, summary, to_dict, from_dict). Handle datetime serialization.

2.  **Branch:** `feature/user-model-refactor`
    **Summary:** Update `User` model for new structure.
    * Modify `models/user.py`: Replace `chat_history` with `sessions: list[Session]`. Add `biography: str`. Add `prompts: dict` (with defaults). Update `to_dict`/`from_dict`/`validate`.

3.  **Branch:** `feature/persistence-verify`
    **Summary:** Ensure loading/saving works with new models.
    * Test `UsersManager.load_users`/`save_users`. Inspect `users.json`.

4.  **Branch:** `feature/view-session-mode`
    **Summary:** Implement read-only session transcript viewer.
    * Add `AppModes.VIEW_SESSION`. Create `modes/view_session_mode.py`. Add "Back" button. Update `AppManager`.

5.  **Branch:** `feature/session-list-mode`
    **Summary:** Implement mode to list sessions and navigate.
    * Add `AppModes.SESSIONS`. Create `modes/session_list_mode.py`. Add "[ Start New Session ]" button -> `TherapyMode`. List past sessions; show summary on focus; selection -> `ViewSessionMode`. Add "[ Back ]" button. Update `AppManager`. Update `MainMenuMode`.

6.  **Branch:** `feature/ai-summarization`
    **Summary:** Add summarization capability to `AIManager`.
    * Implement `AIManager.get_summary(messages, instructions)`.

7.  **Branch:** `feature/therapy-finish-save`
    **Summary:** Implement explicit end/save mechanism for Therapy mode.
    * Modify `TherapyMode` footer: Add `[ End & Save Session ]` button.
    * Implement `TherapyMode.handle_finish_session`: Summarize, create `Session`, append, save, navigate back.
    * Modify `TherapyMode.handle_input('ctrl d')`: Remove saving logic, just navigate back.
    * Modify `TherapyMode.on_activate`: Start `self.messages` fresh.

8.  **Branch:** `feature/biography-context`
    **Summary:** Integrate biography editing and context.
    * Modify `ProfileMode`: Add `Edit` widget for `biography`. Update save logic.
    * Modify `AIManager.get_response`: Accept/use `user_biography` context.
    * Modify `TherapyMode.on_activate`: Load `user.biography`.
    * Modify `TherapyMode.handle_input('enter')`: Pass `user.biography` to `get_response`.

9.  **Branch:** `feature/prompt-editing`
    **Summary:** Implement prompt editing UI.
    * Add `AppModes.PROMPTS`, `AppModes.EDIT_PROMPT`.
    * Create `EditPromptMode`. Create `PromptsMode`.
    * Add "[ Edit Prompts ]" button to `ProfileMode`. Update `AppManager`.
    * Modify `AIManager`/`TherapyMode` to load/use prompts from `user.prompts`.

10. **Branch:** `feature/bio-session`
    **Summary:** Implement AI-assisted biography session flow.
    * Add "[ Start/Update Biography Session ]" button to `ProfileMode`.
    * Modify `TherapyMode` to accept 'bio' session flag, use 'bio' prompt.
    * Modify `handle_finish_session`: If 'bio' session, call `get_summary` (with bio summary prompt), update `user.biography`, save, navigate to Profile.

11. **Branch:** `feature/testing-updates`
    **Summary:** Add/update unit tests.
    * Add tests for `Session`, `AIManager.get_summary`. Update `User`, `UsersManager` tests.

12. **Branch:** `feature/cleanup`
    **Summary:** Final code cleanup and documentation polish.
    * Remove debug logs, check style, add docstrings, finalize `README.md`, verify `requirements.txt`.