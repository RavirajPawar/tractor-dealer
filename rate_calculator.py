import os

ignore = ["__pycache__", ".venv", ".vscode", ".git", "log", "uploads"]
total_lines, rate_per_line = 0, 50


for root, directories, files in os.walk("."):
    for file in files:
        file = os.path.join(root, file)
        is_ignore = False
        for i in ignore:
            if i in file:
                is_ignore = True
                break
        if not is_ignore:
            with open(file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                for line in lines:
                    line = line.strip()
            number_of_lines = len(lines)
            print(f"{file} has {number_of_lines}")
            total_lines += number_of_lines

print(
    f"total lines {total_lines} * rate per line {rate_per_line}\ncost= {total_lines*rate_per_line}"
)
