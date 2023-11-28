# Read an existing Python requirements.txt and compare it with
# the currently installed packages using pip freeze.
# Output a requirements_new.txt listing just the packages in the existing requirements
# specifying the currently installed versions, in lower-case alpha order
# and a requirements_raw.txt with no explpicit versions to bring versions up-to-date

from subprocess import run, PIPE

# Read the original requirements.txt file
with open('requirements.txt', 'r') as f:
    original_requirements = f.readlines()
original_requirements = set([x.strip().split('==')[0] for x in original_requirements])

# Get the list of all installed packages with versions
installed_packages = run(["pip", "freeze"], stdout=PIPE, text=True).stdout.splitlines()
installed_packages = set([x.strip() for x in installed_packages])

# Filter to keep only top-level packages with versions
final_requirements = []
for package in sorted(installed_packages, key=lambda x: x.split('==')[0].lower()):
    package_name = package.split('==')[0]
    if package_name in original_requirements:
        final_requirements.append(package)

# Write the new requirements.txt file
with open('requirements_new.txt', 'w') as f:
    for package in final_requirements:
        f.write(f"{package}\n")

# Write the raw requirements.txt file
with open('requirements_raw.txt', 'w') as f:
    for package in final_requirements:
        f.write(f"{package.split('==')[0]}\n")
