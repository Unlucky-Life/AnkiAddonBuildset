
"""Example Anki addon entrypoint.

This file contains multiple commented examples showing how to interact
with Anki's GUI and internals. It is intended to be placed inside
`addons21/<your_addon_id>/__init__.py` during development.

The examples are safe to import outside Anki (they'll be no-ops), and
illustrate common patterns:

- Using `aqt.gui_hooks` to react to events
- Adding a Tools menu action via `mw.form.menuTools`
- Accessing `mw` (main window) and `mw.col` (collection)
- Running background tasks to avoid blocking the UI

Note: When testing these snippets, put this file into Anki's add-ons
folder and restart Anki.
"""

#try:
	# Typical imports available when running inside Anki
	#from aqt import mw, gui_hooks
    #Find the hooks and their variables under: https://github.com/ankitects/anki/blob/main/qt/tools/genhooks_gui.py
	#from aqt.qt import QAction
	#from aqt.utils import showInfo
#except Exception:
	# If this file is imported outside Anki (for linting or packaging),
	# keep everything as no-op to avoid import errors.
	#mw = None
	#gui_hooks = None
	#QAction = None
	#showInfo = None


###############################################################################
# Example 1: run code when the main window initializes
###############################################################################
""""
def _on_window_init(window):
	# window == mw (main window). Keep this very quick.
	if showInfo:
		# show a tiny popup on Anki start (for demonstration)
		showInfo("Example addon: window initialized")


if gui_hooks:
	# Append the function to the hook so it runs after mw is ready
	gui_hooks.window_did_init.append(_on_window_init)

"""
###############################################################################
# Example 2: react to reviewer events (question/answer shown)
###############################################################################
"""
def _on_question_shown(reviewer):
	# reviewer is the reviewer instance. Keep actions light-weight.
	try:
		card = getattr(reviewer, 'card', None)
		cid = getattr(card, 'id', None)
		# simple debug print — in Anki this goes to its console/log
		print(f"[example_addon] Question shown, card id={cid}")
	except Exception:
		pass


def _on_answer_shown(reviewer):
	try:
		print("[example_addon] Answer shown")
	except Exception:
		pass


if gui_hooks:
	# Hook names can change across versions — these are common for 2.1+
	try:
		gui_hooks.reviewer_did_show_question.append(_on_question_shown)
		gui_hooks.reviewer_did_show_answer.append(_on_answer_shown)
	except Exception:
		# If a hook isn't available, ignore gracefully.
		pass

"""
###############################################################################
# Example 3: add an item to the Tools menu
###############################################################################
"""
def _my_tool_action():
	# This runs on the main thread and should be quick. For longer work,
	# dispatch to a background thread or show a dialog that performs work
	# asynchronously.
	if showInfo:
		showInfo("Example addon: Tools → My Addon Action executed")


def _register_menu_action():
	if not mw or not QAction:
		return
	try:
		action = QAction("My Addon Action", mw)
		action.triggered.connect(_my_tool_action)
		# Add to Tools menu so users can find it under `Tools` -> `My Addon Action`
		mw.form.menuTools.addAction(action)
	except Exception:
		pass


if mw:
	# Register immediately if mw is available; otherwise the window init
	# hook above can also register the action.
	_register_menu_action()

"""
###############################################################################
# Example 4: perform background work (do not block Anki UI)
###############################################################################
"""
def _do_background_work(data):
	# Example long-running work (network, heavy computation, db ops)
	import time
	time.sleep(1)
	# When done, if you need to update UI, schedule it on main thread
	try:
		if mw and showInfo:
			# showInfo must be called on the main thread; small examples
			# often work from here, but prefer using QTimer.singleShot
			# or gui_hooks to schedule UI updates in real addons.
			showInfo(f"Background task finished: {data}")
	except Exception:
		pass


def _start_background_work(data="hello"):
	# Start a thread for background work so the UI stays responsive
	try:
		import threading
		t = threading.Thread(target=_do_background_work, args=(data,))
		t.daemon = True
		t.start()
	except Exception:
		pass
"""

###############################################################################
# Quick usage examples (uncomment to test inside Anki):
###############################################################################

# 1) Use gui_hooks by registering functions (already done above):
#    gui_hooks.reviewer_did_show_question.append(_on_question_shown)

# 2) From other modules in your addon, access main window and collection:
#    from aqt import mw
#    col = mw.col  # Anki collection (database + models)

# 3) Start background work safely (call from a menu action or hook):
#    _start_background_work("some payload")

# 4) If you need to clean up on unload (rare), remove your hooks:
#    gui_hooks.reviewer_did_show_question.remove(_on_question_shown)


###############################################################################
# End of examples
###############################################################################

