import pathlib

import pyperclip  # type: ignore


def camel_to_snake(name):
    name = list(name)
    name[0] = name[0].lower()
    out_name = []
    for char in name:
        if char.isupper():
            out_name.append('_')
            out_name.append(char.lower())
        else:
            out_name.append(char)
    return ''.join(out_name)


def parse_data(data: str):
    read_title = True
    title = ''

    parsed: dict[str, list[str]] = {}

    for line in data.strip().split('\n'):
        if not line:
            read_title = True
            continue
        if read_title:
            title = line.strip()
            read_title = False
            continue
        if title not in parsed:
            parsed[title] = []
        parsed[title].append(line.strip())

    return parsed


def generate_class_code(name: str, member_constants: list[str]):
    underscore_location = member_constants[0].index('_')
    parts: list[str] = [
        f'class {name}(msgspec.Struct):',
        f"    '''{name} colors'''",
    ]

    for member_constant in member_constants:
        member_name = camel_to_snake(member_constant[underscore_location+1:])
        parts.append(f'    {member_name}: Color')

    return '\n'.join(parts)


def main() -> None:
    data_path = pathlib.Path(__file__).parent / 'color_models_data.txt'
    data = data_path.read_text()
    parsed = parse_data(data)

    classes: dict[str, str] = {}
    for class_name in parsed:
        classes[class_name] = generate_class_code(class_name, parsed[class_name])

    full = '\n\n\n'.join(classes.values())
    pyperclip.copy(full)
    print(full)


if __name__ == '__main__':
    main()
