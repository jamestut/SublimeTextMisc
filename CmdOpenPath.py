import sublime
import sublime_plugin
import os
import stat
import subprocess

_event_listener = []

class CmdOpenPath(sublime_plugin.WindowCommand):
	def __init__(self, window):
		self.window = window
		self._cached_open = {}

	def run(self):
		wid = self.window.id()

		def do_open_file(fn):
			try:
				s = os.stat(fn)
			except FileNotFoundError:
				sublime.error_message(f"File '{fn}' not found.")
				return False
			except:
				pass

			if stat.S_ISDIR(s.st_mode):
				_event_listener._folder_to_open = fn
				sublime.run_command("new_window")
			else:
				self.window.run_command("open_file", {"file": fn})

			return True

		def on_done(v):
			if do_open_file(v):
				if wid in self._cached_open:
					del self._cached_open[wid]
			else:
				self._cached_open[wid] = v

		# default prefill. priority:
		# 1. last missed (failed) input
		# 2. current active file
		# 3. current first active directory
		# 4. default prefiller '/path/to/file/or/folder'

		# prio 1
		prefill = self._cached_open.get(wid, None)
		# prio 2
		if prefill is None:
			cv = self.window.active_view()
			prefill = cv.file_name()
		# prio 3
		if prefill is None:
			folders = self.window.folders()
			prefill = folders[0] if folders else None
		# prio 4
		if prefill is None:
			prefill = "/path/to/file/or/folder"

		self.window.show_input_panel("Open path",
			prefill, on_done, None, None)

class OpenFolderViewListener(sublime_plugin.EventListener):
	def __init__(self):
		super().__init__()
		global _event_listener
		_event_listener = self
		self._folder_to_open = None

	def on_new_window(self, window):
		if self._folder_to_open:
			pjdata = window.project_data()
			if pjdata is None:
				pjdata = {}
			folders = pjdata.setdefault("folders", [])
			folders.append({'path': self._folder_to_open})
			window.set_project_data(pjdata)
			self._folder_to_open = None
