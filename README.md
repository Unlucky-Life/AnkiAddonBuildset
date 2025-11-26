# AnkiAddonBuildset
A small tool kit to build your own Anki Addons !
  
## What is Anki?

Anki is a free, open-source spaced repetition flashcard application used to help people memorize information efficiently. It schedules reviews of cards based on how well you remember them so you spend more time on difficult items and less time on easy ones. Anki is extensible via add-ons written in Python that hook into its Qt-based GUI and internal events.

## What are Anki add-ons?

Anki add-ons are small Python packages that extend or modify Anki's behavior and user interface. Typical uses include custom review behavior, UI modifications, automated import/export features, and additional study tools. For Anki 2.1 and later, add-ons are written in Python 3 and installed into Anki's `addons21` folder. During development you can open the add-ons folder from Anki via `Tools → Add-ons → Open Add-ons Folder`, add your addon directory, and restart Anki to load changes.

Basic structure (common):

- `addons21/<your_addon_id>/__init__.py`: entrypoint for your addon
- Additional modules or resources inside your addon folder

Keep changes minimal and use Anki's provided hooks and APIs to interact with the GUI and core.

## Using GUI hooks

Anki exposes a number of GUI and lifecycle hooks through `aqt.gui_hooks` (commonly imported as `from aqt import gui_hooks`). These let you run code at specific times, for example when the main window initializes, when a reviewer shows a question or answer, or when the deck browser is shown.

Key points about hooks:

- Hooks are in-process call lists: append your callable to the hook to receive events.
- Your callable should be quick — long-running work should be offloaded to threads to avoid freezing the UI.
- Hook signatures vary; check arguments passed by the specific hook you use.

### Simple examples

1) Add a small change when the main window opens:

```python
from aqt import gui_hooks
from aqt.utils import showInfo

def on_window_init(window):
	# window is the main Anki window (mw)
	# run a quick info popup on start
	showInfo("Hello from my addon — window initialized")

gui_hooks.window_did_init.append(on_window_init)
```

2) React to reviewer events (when a question or answer is shown):

```python
from aqt import gui_hooks

def when_question_shown(reviewer):
	# reviewer is the reviewer instance; inspect reviewer.card or reviewer.mw
	print("Question shown for card id:", getattr(reviewer.card, 'id', None))

def when_answer_shown(reviewer):
	# run light-weight actions (logging, small UI tweaks)
	print("Answer shown")

gui_hooks.reviewer_did_show_question.append(when_question_shown)
gui_hooks.reviewer_did_show_answer.append(when_answer_shown)
```

3) Add an item to the Tools menu (example):

```python
from aqt import mw
from aqt.qt import QAction
from aqt.utils import showInfo

def my_tool_action():
	showInfo("My add-on tools action executed")

action = QAction("My Addon Action", mw)
action.triggered.connect(my_tool_action)
mw.form.menuTools.addAction(action)
```

Notes:

- Use `mw` (main window) and `mw.col` (collection) to access Anki internals when needed.
- Use `aqt.gui_hooks` to avoid modifying Anki's core UI code directly — hooks are safer and more compatible across versions.

## Where to put your addon

- During development: open Anki's add-ons folder and create `addons21/<your_addon_id>/` containing `__init__.py` and any modules.
- To distribute: package the folder as a zip or follow AnkiWeb submission guidelines.

## Further tips

- Keep UI actions responsive: avoid blocking the main thread.
- Test against the Anki version(s) you target; hooks and internals can change between releases.
- Read Anki's developer docs and inspect `aqt` and `anki` packages in your local Anki installation for available APIs.

---

If you want, I can add a minimal example addon folder inside this repo (with `__init__.py`) demonstrating the hooks above and instructions to install it locally. Want me to add that now?
