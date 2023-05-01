import os
import time
from tkinter import filedialog, Tk

# Welcome message
print('Welcome! Pick two directories to compare the contents of!')
print()

# Wait for user input
input('Press ENTER to start...')

print("\n--------------------------\n")

# Create an instance of Tkinter
root = Tk()
root.withdraw()

# Open a folder selection dialog for dir1 and print the selected directory
dir1 = filedialog.askdirectory()
print(f"Directory one: {dir1}")
time.sleep(1)

# Open a folder selection dialog for dir2 and print the selected directory
dir2 = filedialog.askdirectory()
print(f'Directory two: {dir2}')

print("\n--------------------------\n")

# Normalize directory paths to avoid inconsistencies due to different separators
dir1 = os.path.normpath(dir1)
dir2 = os.path.normpath(dir2)

# Check if the two directories are the same and exit if they are
if dir1 == dir2:
    print('error: Cannot compare same directory.')
    input('press ENTER to exit...')
    exit()

if not (os.access(dir1, os.R_OK)):
    print('error: Cannot access dir 1.')
    input('press ENTER to exit...')
    exit()
if not (os.access(dir2, os.R_OK)):
    print('error: Cannot access dir 2.')
    print('Press ENTER to exit...')
    exit()

# Get a list of the files in each directory
files1 = [f for f in os.listdir(dir1) if os.path.isfile(os.path.join(dir1, f))]
files2 = [f for f in os.listdir(dir2) if os.path.isfile(os.path.join(dir2, f))]


# Create a set for each directory
list1 = set(files1)
list2 = set(files2)

if len(list1) or len(list2) == 0:
    print('Information: No files exist in one of the directories, nothing to compare too.')
    input('Press ENTER to exit...')
    exit()


# Check if the two sets are the same and exit if they are
if list1 == list2:
    print('information: Both directories have the same content.')
    input('press ENTER to exit...')
    exit()

# Find the symmetric difference between the two sets (i.e., the files that are unique to each set)
diff = list1.symmetric_difference(list2)

# Get the number of different files
numdif = len(diff)

# Print the number of files and the names of the files that are unique to each set
time.sleep(1)
print(f"There are {numdif} files that are different: {diff}")

# Wait for user input to exit
print()
input("Press ENTER to exit...")
