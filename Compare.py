import os
from tkinter import filedialog, Tk
import time


# Welcome and start.
print('Welcome, Pick two directories to compare the contents of!')
print('\n')
time.sleep(1)
input('press ENTER to start...')
print("\n--------------------------\n")


# Create an instance of Tkinter
root = Tk()
root.withdraw()

# Open a folder selection dialog
dir1 = filedialog.askdirectory()
print(f"Directory one: {dir1}")
time.sleep(1)
dir2 = filedialog.askdirectory()
print(f'Directory two: {dir2}')
print("\n--------------------------\n")

# Make sure that the path is correct by normalizing it.
dir1 = os.path.normpath(dir1)
dir2 = os.path.normpath(dir2)


# Get a list of the files in each directory.
files1 = [f for f in os.listdir(dir1) if os.path.isfile(os.path.join(dir1, f))]
files2 = [f for f in os.listdir(dir2) if os.path.isfile(os.path.join(dir2, f))]


# Create a set for each directory.
list1 = set(files1)
list2 = set(files2)

# Find the symmetric difference between the two sets (i.e., the files that are unique to each set).
diff = list1.symmetric_difference(list2)

# Get the number of different files.
numdif = len(diff)

# Print the number of files and the names of the files that are unique to each set.
time.sleep(1)
print(
    f"There are {numdif} files that are different: {diff}")

# Exit
print('\n')
input("press enter to exit...")
