import os
import time

import pyperclip
import wx
import wx.lib.filebrowsebutton as filebrowse


def check_dir_access(directory):
	if not os.access(directory, os.R_OK):
		return False
	return True


def create_file_set(directory):
	file_set = set()
	with os.scandir(directory) as dir:
		for file in dir:
			if file.is_file():
				file_set.add(file.name)
	return file_set


class App(wx.Frame):
	def __init__(self, parent, title, size=(600, 300)):
		super().__init__(parent, title=title, size=size)
		self.panel = wx.Panel(self)

		self.panel.SetBackgroundColour(wx.WHITE)

		self.results = Results(self.panel)
		self.folders_to_compare = FoldersToCompare(self.panel, self.results)

		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.sizer.Add(self.results, 1, wx.EXPAND | wx.ALL, 5)
		self.sizer.Add(self.folders_to_compare, 0, wx.EXPAND | wx.ALL, 5)
		self.panel.SetSizer(self.sizer)

		self.Show()


class FoldersToCompare(wx.Panel):
	def __init__(self, parent, results):
		super().__init__(parent)
		self.results = results

		self.dir1_browse = filebrowse.DirBrowseButton(self)

		self.dir2_browse = filebrowse.DirBrowseButton(self)

		self.copy_button = wx.Button(self, label="Copy Results")
		self.copy_button.Bind(wx.EVT_BUTTON, self.copy)
		self.compare_button = wx.Button(self, label="Compare")
		self.compare_button.Bind(wx.EVT_BUTTON, self.compare)

		self.sizer = wx.GridBagSizer(5, 5)
		self.sizer.Add(self.dir1_browse, pos=(0, 2), flag=wx.ALIGN_CENTER_VERTICAL)

		self.sizer.Add(self.dir2_browse, pos=(1, 2), flag=wx.ALIGN_CENTER_VERTICAL)

		self.sizer.Add(self.copy_button, pos=(2, 2), flag=wx.ALIGN_RIGHT)
		self.sizer.Add(self.compare_button, pos=(2, 1), flag=wx.ALIGN_RIGHT)

		self.SetSizerAndFit(self.sizer)

	def compare(self, event):
		dir1 = self.dir1_browse.GetValue()
		dir2 = self.dir2_browse.GetValue()

		if dir1 == dir2:
			wx.MessageBox("The directories are the same.", "Error", wx.OK | wx.ICON_ERROR)
			return

		if not check_dir_access(dir1):
			wx.MessageBox("Directory one is not accessible, or does not exist.", "Error", wx.OK | wx.ICON_ERROR)
			return

		if not check_dir_access(dir2):
			wx.MessageBox("Directory two is not accessible, or does not exist.", "Error", wx.OK | wx.ICON_ERROR)
			return

		self.results.different_files_text.Clear()
		self.results.update_time_taken(0.0)
		self.results.update_total_different_files(0)
		self.results.update_total_files(0)

		wx.CallAfter(self.compare_different_files, dir1, dir2)

	def compare_different_files(self, dir1, dir2):
		time_elapsed = time.time()

		dir1_files = create_file_set(dir1)
		dir2_files = create_file_set(dir2)

		if not dir1_files:
			wx.MessageBox("Directory one is empty.", "Error", wx.OK | wx.ICON_ERROR)
			return

		if not dir2_files:
			wx.MessageBox("Directory two is empty.", "Error", wx.OK | wx.ICON_ERROR)
			return

		different_files = dir1_files.symmetric_difference(dir2_files)

		num_different_files = len(different_files)
		total_files = len(dir1_files) + len(dir2_files)

		for file in different_files:
			wx.CallAfter(self.results.append_different_file, file)

		wx.CallAfter(self.results.update_time_taken, time.time() - time_elapsed)
		wx.CallAfter(self.results.update_total_different_files, num_different_files)
		wx.CallAfter(self.results.update_total_files, total_files)

	def copy(self, event):
		self.results.copy()


class Results(wx.Panel):
	def __init__(self, parent):
		super().__init__(parent)

		self.time_taken_label = wx.StaticText(self, label="Time Taken: 0.0s")
		self.total_different_files_label = wx.StaticText(self, label="Total Different Files: 0")
		self.total_files_label = wx.StaticText(self, label="Total Files: 0")

		self.different_files_text = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY)

		self.sizer = wx.BoxSizer(wx.HORIZONTAL)
		self.sizer.Add(self.time_taken_label, 0, wx.EXPAND | wx.ALL, 5)
		self.sizer.Add(self.total_different_files_label, 0, wx.EXPAND | wx.ALL, 5)
		self.sizer.Add(self.total_files_label, 0, wx.EXPAND | wx.ALL, 5)

		self.main_sizer = wx.BoxSizer(wx.VERTICAL)
		self.main_sizer.Add(self.sizer, 0, wx.EXPAND)
		self.main_sizer.Add(self.different_files_text, 1, wx.EXPAND | wx.ALL, 5)

		self.SetSizerAndFit(self.main_sizer)

	def append_different_file(self, file):
		self.different_files_text.AppendText(file + "\n")

	def update_time_taken(self, time_taken):
		self.time_taken_label.SetLabel(f"Time Taken: {time_taken:.2f}s")

	def update_total_different_files(self, num_different_files):
		self.total_different_files_label.SetLabel(f"Total Different Files: {num_different_files}")

	def update_total_files(self, total_files):
		self.total_files_label.SetLabel(f"Total Files: {total_files}")

	def copy(self):
		pyperclip.copy(self.different_files_text.GetValue())
		wx.MessageBox("Results copied to clipboard.", "Success", wx.OK | wx.ICON_INFORMATION)


if __name__ == "__main__":
	app = wx.App()
	frame = App(None, title="Compare Tool")
	app.MainLoop()
