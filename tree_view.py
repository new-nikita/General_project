import os

# что игнорируем
IGNORE = {"__pycache__", ".idea", ".git", ".venv", "node_modules", ".DS_Store"}


def is_valid(name):
    if name.startswith("."):
        return False
    if name in IGNORE:
        return False
    return True


def print_tree(path, prefix=""):
    items = [i for i in sorted(os.listdir(path)) if is_valid(i)]

    for index, item in enumerate(items):
        full_path = os.path.join(path, item)

        connector = "└─ " if index == len(items) - 1 else "├─ "
        print(prefix + connector + item)

        if os.path.isdir(full_path):
            extension = "   " if index == len(items) - 1 else "│  "
            print_tree(full_path, prefix + extension)


if __name__ == "__main__":
    # root = "/Users/nikita/PycharmProjects/General_project_mobile_app/general_project_modile_app/lib/features"  # укажи нужную папку  # фронт
    root = "/Users/nikita/PycharmProjects/General_project_mobile_app/general_project_modile_app/lib"
    # root = "."
    # root = "frontend"
    # root = "backend"
    print(root + "/")
    print_tree(root)
