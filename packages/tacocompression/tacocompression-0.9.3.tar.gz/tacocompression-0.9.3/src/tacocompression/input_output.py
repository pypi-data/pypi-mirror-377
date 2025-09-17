import pandas as pd
from pathlib import Path
from tacocompression.compression import FloatTuple, IntTuple


def load_inputs(locations: list[str], compress: bool) -> tuple[list[list[float]]|list[IntTuple|FloatTuple], list[str]]:
    time_series = []
    file_names = []
    for location in locations:
        path = Path(location)
        if not path.is_absolute():
            path = Path.cwd() / location
            assert path.exists()
        if path.is_file():
            file_names.append(path.name)
            time_series.append(load_file(path, compress))
        elif path.is_dir():
            for entry in path.iterdir():
                if entry.is_file() and entry.name.endswith(".csv"):
                    file_names.append(entry.name)
                    time_series.append(load_file(entry, compress))
    return time_series, file_names

def load_file(path: Path, compress: bool) -> list[float]|IntTuple|FloatTuple:
    if compress:
        content = pd.read_csv(path).iloc[:, 0].to_list()
    else:
        with open(path, "r") as f:
            content = [l[:-1] for l in f.readlines()]
        z_int = [int(x) for x in content[0].split(',')]
        if len(content) == 3:
            content = IntTuple(z_int, int(content[1]), int(content[2]))
        else:
            z_frac = [int(x) for x in content[1].split(',')]
            content = FloatTuple(z_int, z_frac, int(content[2]), int(content[3]), int(content[4]))
    return content


def save_output(data: list[list[float]|IntTuple|FloatTuple], filenames: list[str], output_location: str):
    output_dir = prepare_path(output_location)
    for t, fn in zip(data, filenames):
        with open(output_dir / fn, 'w') as f:
            for value in t:
                if isinstance(value, list):
                    f.write(str(value)[1:-1].replace(' ', '') + "\n")
                else:
                    f.write(f"{value}\n")

def prepare_path(location: str) -> Path:
    directory = Path(location)
    if not (directory.is_absolute()):
        directory = Path.cwd() / directory
    assert directory.exists()
    return directory
