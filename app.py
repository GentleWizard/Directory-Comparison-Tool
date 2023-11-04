import os
import time
from tkinter import filedialog

import customtkinter as ctk
import pyperclip


def check_dir_access(directory):
	if not os.access(directory, os.R_OK):
		return False
	return True


def create_file_set(directory):
	file_set = set()
	with os.scandir(directory) as _dir:
		for file in _dir:
			if file.is_file():
				file_set.add(file.name)
	return file_set


class App(ctk.CTk):
	def __init__(self):
		super().__init__()

		self.title("Compare Tool")
		self.geometry("600x300")

		self.folders_to_compare = FoldersToCompare(self)
		self.results = Results(self)

		self.mainloop()


class FoldersToCompare(ctk.CTkFrame):
	def __init__(self, master):
		super().__init__(master, corner_radius=0)
		self.master = master
		self.pack(fill="x", side="bottom")

		self.grid_columnconfigure(1, weight=1)

		self.dir1_var = ctk.StringVar()
		self.dir1 = ctk.CTkEntry(self, placeholder_text="Directory one", textvariable=self.dir1_var)
		self.dir1.grid(row=0, column=1, sticky="nsew", pady=(5, 2), padx=(5, 2))

		self.dir1_browse = ctk.CTkButton(self, text="Browse", command=lambda: self.browse(self.dir1_var))
		self.dir1_browse.grid(row=0, column=2, sticky="nsew", pady=(5, 2), padx=(2, 5))

		self.dir2_var = ctk.StringVar()
		self.dir2 = ctk.CTkEntry(self, placeholder_text="Directory two", textvariable=self.dir2_var)
		self.dir2.grid(row=1, column=1, sticky="nsew", pady=(2, 2), padx=(5, 2))

		self.dir2_browse = ctk.CTkButton(self, text="Browse", command=lambda: self.browse(self.dir2_var))
		self.dir2_browse.grid(row=1, column=2, sticky="nsew", pady=(2, 2), padx=(2, 5))

		self.copy_button = ctk.CTkButton(
			self,
			text="Copy Results",
			command=self.copy)
		self.copy_button.grid(row=2, column=2, sticky="nsew", pady=(2, 5), padx=(2, 5))

		self.compare_button = ctk.CTkButton(
			self,
			text="Compare",
			command=self.compare)
		self.compare_button.grid(row=2, column=1, sticky="nsew", pady=(2, 5), padx=(5, 2))

	def copy(self):
		data = self.master.results.different_files.get("1.0", "end")
		pyperclip.copy(data)

	def compare(self):

		dir1 = self.dir1_var.get()
		dir2 = self.dir2_var.get()

		time_elapsed = time.time()
		if dir1 == dir2:
			self.master.results.reset_everything()
			self.master.results.edit_result_text("Cannot compare same directory.")
		if not check_dir_access(dir1):
			self.master.results.reset_everything()
			self.master.results.edit_result_text("Cannot access dir 1.")
		if not check_dir_access(dir2):
			self.master.results.reset_everything()
			self.master.results.edit_result_text("Cannot access dir 2.")

		task1 = create_file_set(dir1)
		task2 = create_file_set(dir2)

		list1 = task1
		list2 = task2

		if not list1:
			self.master.results.reset_everything()
			self.master.results.edit_result_text("No files exist in directory 1.")
		if not list2:
			self.master.results.reset_everything()
			self.master.results.edit_result_text("No files exist in directory 2.")

		if list1 == list2:
			self.master.results.reset_everything()
			self.master.results.edit_result_text("Both directories have the same content.")

		diff = list1.symmetric_difference(list2)

		numdif = len(diff)
		total_files = len(list1) + len(list2)

		for file in diff:
			self.master.results.edit_result_text(f"{file}\n")

		time_taken = round(time.time() - time_elapsed, 2)
		total_time = ""
		if time_taken < 60:
			total_time = f"{time_taken}s"
		elif time_taken > 60:
			time_taken = round(time_taken / 60, 2)
			total_time = f"{time_taken}m"
		elif time_taken > 3600:
			time_taken = round(time_taken / 3600, 2)
			total_time = f"{time_taken}h"

		self.master.results.set_number_of_files(numdif)
		self.master.results.set_total_files(total_files)
		self.master.results.set_time_taken(total_time)

	@staticmethod
	def browse(entry):
		file = filedialog.askdirectory()
		entry.set(file)


class Results(ctk.CTkFrame):
	def __init__(self, master):
		super().__init__(master, corner_radius=0)
		self.pack(fill="both", expand=True, side="top")

		self.information = ctk.CTkFrame(self, corner_radius=3)
		self.information.pack(side="left", fill="both", padx=(5, 0), pady=5, ipadx=5, ipady=5)

		self.time_taken = "0.0s"
		self.time_taken_label = ctk.CTkLabel(self.information, text=f"Time Taken: {self.time_taken}")
		self.time_taken_label.pack(padx=(5, 10), pady=0, anchor="w")

		self.total_different_files = 0
		self.total_different_files_label = ctk.CTkLabel(
			self.information,
			text=f"Total Different Files: {self.total_different_files}"
		)
		self.total_different_files_label.pack(padx=(5, 10), pady=(2, 0), anchor="w")

		self.total_files = 0
		self.total_files_label = ctk.CTkLabel(self.information, text=f"Total Files: {self.total_files}")
		self.total_files_label.pack(padx=(5, 10), pady=0, anchor="w")

		self.different_files = ctk.CTkTextbox(self)
		self.different_files.insert("end", "")
		self.different_files.configure(state="disabled", text_color="lightgrey", corner_radius=3)
		self.different_files.pack(side="right", fill="both", expand=True, padx=(0, 5), pady=5)

	def edit_result_text(self, text):
		self.different_files.configure(state="normal")
		self.different_files.insert("end", text)
		self.different_files.configure(state="disabled")

	def clear_result(self):
		self.different_files.configure(state="normal")
		self.different_files.delete("1.0", "end")
		self.different_files.configure(state="disabled")

	def set_number_of_files(self, number):
		self.total_different_files = number
		self.total_different_files_label.configure(text=f"Total Different Files: {self.total_different_files}")

	def set_total_files(self, number):
		self.total_files = number
		self.total_files_label.configure(text=f"Total Files: {self.total_files}")

	def set_time_taken(self, time_taken):
		self.time_taken = time_taken
		self.time_taken_label.configure(text=f"Time Taken: {self.time_taken}")

	def reset_everything(self):
		self.clear_result()
		self.set_number_of_files(0)
		self.set_total_files(0)
		self.set_time_taken("0.0s")


if __name__ == "__main__":
	app = App()
