import sublime
import sublime_plugin
import os
import stat

class SidebarCmdNewFile(sublime_plugin.WindowCommand):
	def run(self, paths):
		path = self._dir_path(paths)

		def on_done(v):
			if not v:
				return
			newfile = os.path.join(path, v)

			# check if file not exist
			try:
				os.stat(newfile)
				sublime.error_message(f"File '{newfile}' already exists!")
				return
			except FileNotFoundError:
				pass
			except Exception as ex:
				sublime.error_message(f"Error creating '{newfile}': {ex}")
				return

			# actually create the file
			try:
				with open(newfile, "w") as f:
					pass
			except Exception as ex:
				sublime.error_message(f"Error creating '{newfile}': {ex}")
				return

			self.window.open_file(newfile)

		self.window.show_input_panel("File name to create", "", on_done, None, None)

	def is_visible(self, paths):
		return bool(self._dir_path(paths))

	def _dir_path(self, paths):
		if len(paths) != 1:
			return None
		if paths[0][0] != "/":
			# must be absolute
			return None

		path = paths[0]
		try:
			is_dir = stat.S_ISDIR(os.stat(path).st_mode)
		except Exception as ex:
			print(f"Error stat '{path}': {ex}")
			return None

		if not is_dir:
			# assume file: we take the parent
			path, _ = os.path.split(path)

		return path
