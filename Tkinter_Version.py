import os
import time
from tkinter import filedialog, Menu

import customtkinter as ctk
import pyperclip


def check_dir_access(directory):
	if not os.access(directory, os.R_OK):
		return False
	return True


def create_file_set(directory, subfolders=False):
	file_set = set()
	if subfolders:
		for root, dirs, files in os.walk(directory):
			for file in files:
				file_set.add(file)
		return file_set

	with os.scandir(directory) as dir:
		for file in dir:
			if file.is_file():
				file_set.add(file.name)
	return file_set


class App(ctk.CTk):
	def __init__(self):
		super().__init__()

		self.title("Compare Tool")
		self.geometry("670x370")
		self.minsize(670, 370)
		self.iconbitmap("icon.ico")

		self.results = Results(self)
		self.folders_to_compare = FoldersToCompare(self)
		self.menu = MenuBar(self)
		self.menu_visible = False

		self.bind("<Control-s>", lambda event: self.results.save_to_file())
		self.bind("<Control-r>", lambda event: self.results.reset_everything())
		self.bind("<Control-m>", lambda event: self.toggle_menu())

		self.mainloop()

	def get_results_frame(self):
		return self.results

	def get_folders_to_compare_frame(self):
		return self.folders_to_compare

	def get_settings_frame(self):
		return self.results.settings

	def get_information_frame(self):
		return self.results.information

	def quit(self):
		self.destroy()

	def toggle_menu(self):
		if self.menu_visible:
			self.menu.destroy()
			self.menu_visible = False
		else:
			self.menu = MenuBar(self)
			self.config(menu=self.menu)
			self.menu_visible = True


class FoldersToCompare(ctk.CTkFrame):
	def __init__(self, master):
		super().__init__(master, corner_radius=0)
		self.pack(fill="x", side="bottom")

		self.results = master.get_results_frame()
		self.settings = master.get_settings_frame()

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
			command=self.results.copy)
		self.copy_button.grid(row=2, column=2, sticky="nsew", pady=(2, 5), padx=(2, 5))

		self.compare_button = ctk.CTkButton(
			self,
			text="Compare",
			command=self.compare)
		self.compare_button.grid(row=2, column=1, sticky="nsew", pady=(2, 5), padx=(5, 2))

	def compare(self):
		self.results.clear_result()

		get_subfolders = self.settings.get_subfolders_settings_var()

		dir1 = self.dir1_var.get()
		dir2 = self.dir2_var.get()

		time_elapsed = time.time()
		if dir1 == dir2:
			self.results.reset_everything()
			self.results.edit_result_text("Cannot compare same directory.")
		if not check_dir_access(dir1):
			self.results.reset_everything()
			self.results.edit_result_text("Cannot access dir 1.")
		if not check_dir_access(dir2):
			self.results.reset_everything()
			self.results.edit_result_text("Cannot access dir 2.")

		list1 = create_file_set(dir1, get_subfolders)
		list2 = create_file_set(dir2, get_subfolders)

		if not list1:
			self.results.reset_everything()
			self.results.edit_result_text("No files exist in directory 1.")
		if not list2:
			self.results.reset_everything()
			self.results.edit_result_text("No files exist in directory 2.")

		if list1 == list2:
			self.results.reset_everything()
			self.results.edit_result_text("Both directories have the same content.")

		diff = list1.symmetric_difference(list2)

		numdif = len(diff)
		total_files = len(list1) + len(list2)

		for file in diff:
			self.results.edit_result_text(f"{file}\n")

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

		self.results.information.set_number_of_files(numdif)
		self.results.information.set_total_files(total_files)
		self.results.information.set_time_taken(total_time)

	def browse(self, entry):
		file = filedialog.askdirectory()
		entry.set(file)


class Results(ctk.CTkFrame):
	def __init__(self, master):
		super().__init__(master, corner_radius=0)
		self.pack(fill="both", expand=True, side="top")

		self.information = Information(self)
		self.settings = Settings(self)
		self.settings.hide_settings()
		self.just_launched = True

		self.different_files = ctk.CTkTextbox(self, corner_radius=3)
		self.different_files.insert("end", "")
		self.different_files.configure(state="disabled", text_color="lightgrey", corner_radius=3)
		self.different_files.pack(side="right", fill="both", expand=True, pady=5, padx=(2, 5))

	def get_information_frame(self):
		return self.information

	def edit_result_text(self, text):
		self.different_files.configure(state="normal")
		self.different_files.insert("end", text)
		self.different_files.configure(state="disabled")

	def clear_result(self):
		self.different_files.configure(state="normal")
		self.different_files.delete("1.0", "end")
		self.different_files.configure(state="disabled")

	def reset_everything(self):
		self.clear_result()
		self.information.set_number_of_files(0)
		self.information.set_total_files(0)
		self.information.set_time_taken("0.0s")

	def copy(self):
		data = self.different_files.get("1.0", "end")
		pyperclip.copy(data)

	def toggle_settings(self):
		if self.just_launched:
			self.just_launched = False
			self.settings.show_settings()
			self.information.settings_button.configure(text="Hide Settings")
			return
		if self.settings.winfo_ismapped():
			self.settings.hide_settings()
			self.information.settings_button.configure(text="Show Settings")
		else:
			self.settings.show_settings()
			self.information.settings_button.configure(text="Hide Settings")

	def save_to_file(self):
		save_to = filedialog.asksaveasfile(
			initialdir="/",
			title="Save As",
			filetypes=(("Text Files", "*.txt"), ("All Files", "*.*")),
			defaultextension=".txt"
		)
		if save_to is None:
			return
		data = self.different_files.get("1.0", "end")
		save_to.write(data)
		save_to.close()


class Information(ctk.CTkFrame):
	def __init__(self, master):
		super().__init__(master, corner_radius=3)
		self.pack(side="left", fill="both", padx=(5, 2), pady=5, ipadx=5, ipady=5)

		self.time_taken = "0.0s"
		self.time_taken_label = ctk.CTkLabel(self, text=f"Time Taken: {self.time_taken}")
		self.time_taken_label.pack(padx=(5, 10), pady=0, anchor="w")

		self.total_different_files = 0
		self.total_different_files_label = ctk.CTkLabel(self,
														text=f"Total Different Files: {self.total_different_files}")
		self.total_different_files_label.pack(padx=(5, 10), pady=(2, 0), anchor="w")

		self.total_files = 0
		self.total_files_label = ctk.CTkLabel(self, text=f"Total Files: {self.total_files}")
		self.total_files_label.pack(padx=(5, 10), pady=0, anchor="w")

		self.settings_button = ctk.CTkButton(self, text="Show Settings", command=master.toggle_settings)
		self.settings_button.pack(side="bottom", pady=5, padx=5)

	def set_number_of_files(self, number):
		self.total_different_files = number
		self.total_different_files_label.configure(text=f"Total Different Files: {self.total_different_files}")

	def set_total_files(self, number):
		self.total_files = number
		self.total_files_label.configure(text=f"Total Files: {self.total_files}")

	def set_time_taken(self, time):
		self.time_taken = time
		self.time_taken_label.configure(text=f"Time Taken: {self.time_taken}")


class Settings(ctk.CTkScrollableFrame):
	def __init__(self, master):
		super().__init__(master, corner_radius=3, label_text='Settings')
		self.pack(side="left", fill="both", padx=(0, 5), pady=5)

		self.check_subfolders_var = ctk.BooleanVar()
		self.check_subfolders = ctk.CTkCheckBox(self, text="Check Subfolders", variable=self.check_subfolders_var)
		self.check_subfolders.pack(pady=5, padx=5, anchor="w")

	def hide_settings(self):
		self.pack_forget()

	def show_settings(self):
		self.pack(side="left", fill="both", padx=(0, 5), pady=5)

	def get_hidden_files_settings_var(self):
		return self.check_hidden_files_var.get()

	def get_subfolders_settings_var(self):
		return self.check_subfolders_var.get()


class MenuBar(Menu):
	def __init__(self, master):
		super().__init__(master)
		self.results = master.get_results_frame()
		# Create the "File" menu
		self.file_menu = Menu(self, tearoff=0)
		self.file_menu.add_command(label="Save As", command=self.results.save_to_file)
		self.file_menu.add_separator()
		self.file_menu.add_command(label="Exit", command=master.quit)
		self.add_cascade(label="File", menu=self.file_menu)

		# Create the "Edit" menu
		self.edit_menu = Menu(self, tearoff=0)
		self.edit_menu.add_command(label="Copy", command=self.results.copy)
		self.add_cascade(label="Edit", menu=self.edit_menu)

		# Create the "View" menu
		self.view_menu = Menu(self, tearoff=0)
		self.view_menu.add_command(label="Show/Hide Settings", command=self.results.toggle_settings)
		self.view_menu.add_command(label="Refresh", command=self.results.reset_everything)
		self.add_cascade(label="View", menu=self.view_menu)

		# Create the "Help" menu
		self.help_menu = Menu(self, tearoff=0)
		self.help_menu.add_command(label="About")
		self.add_cascade(label="Help", menu=self.help_menu)


if __name__ == "__main__":
	app = App()
