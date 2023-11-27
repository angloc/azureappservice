import json
import subprocess

# Function to get installed packages with versions using npm list
def get_installed_packages():
    result = subprocess.run(['npm', 'list', '--depth=0', '--json'], capture_output=True, text=True)
    data = json.loads(result.stdout)
    dependencies = data.get('dependencies', {})
    return {pkg: info['version'] for pkg, info in dependencies.items()}

# Read the existing package.json file
with open('package.json', 'r') as file:
    package_json = json.load(file)

installed_packages = get_installed_packages()

# Update dependencies and devDependencies with installed versions
for dep_type in ['dependencies', 'devDependencies']:
    if dep_type in package_json:
        for pkg, version in package_json[dep_type].items():
            if pkg in installed_packages:
                package_json[dep_type][pkg] = installed_packages[pkg]

# Write the updated package.json file
with open('package_updated.json', 'w') as file:
    json.dump(package_json, file, indent=4)

# Remove versions for raw package.json
for dep_type in ['dependencies', 'devDependencies']:
    if dep_type in package_json:
        for pkg in package_json[dep_type]:
            package_json[dep_type][pkg] = "*"

# Write the raw package.json file
with open('package_raw.json', 'w') as file:
    json.dump(package_json, file, indent=4)
