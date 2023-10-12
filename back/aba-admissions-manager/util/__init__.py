import os

package_dir = os.path.dirname(os.path.abspath(__file__))

# Initialize an empty dictionary to store the file contents
file_contents = {}

# Read the files within the package directory
for filename in os.listdir(package_dir):
    if filename.endswith('.txt'):
        file_path = os.path.join(package_dir, filename)
        with open(file_path, 'r') as file:
            content = file.read()
            file_contents[filename] = content

# Make the file contents accessible within the package
__all__ = list(file_contents.keys())
