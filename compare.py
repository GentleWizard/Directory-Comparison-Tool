import os
from tkinter import filedialog

# Welcome message
print('Welcome! \nPick two directories to compare the contents of.\n')

# Open a folder selection dialog for dir1 and print the selected directory
dir1 = filedialog.askdirectory()
print(f"Directory one: {dir1}")

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

# Check if the two directories exist and exit if they don't
def check_dir_access(directory, dir_number):
    if not os.access(directory, os.R_OK):
        print(f'error: Cannot access dir {dir_number}.')
        input('Press ENTER to exit...')
        exit()

check_dir_access(dir1, 1)
check_dir_access(dir2, 2)

def create_file_set(directory):
    with os.scandir(directory) as dir:
        return {file.name for file in dir if file.is_file()}
    
list1 = create_file_set(dir1)
list2 = create_file_set(dir2)

if not list1 or not list2:
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
print(f"There are {numdif} files that are different: {diff}")

# Wait for user input to exit
input("\nPress ENTER to exit...")
