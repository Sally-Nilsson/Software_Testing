import pickle
import hashlib
import platform
import base64
import json
import sys
import os
import argparse

class CustomClass:
    def __init__(self, value):
        self.value = value

TEST_CASES = {
    "simple_int": 42,
    "simple_str": "Hi, This is a test string",
    "simple_float": 3.14,
    "list_of_primitives": [1, "a", 3.14, None],
    "dict_mixed": {"a": 1, "b": [1, 2, 3], "c": {"d": 4}},
    "nested": [[1, 2], [3, [4, 5]]],
    "recursive_list": None,  # Will be set below
    "float_precision": [0.1 + 0.2, 0.3],
    "tuple_of_objects": (1, 2, ("a", "b"), [3.0, 4.0]),
    "Tuple": (1, 2, 3),
    "True_False": True,
    "NoneType": None,
    "complex_number": complex(1, 2),
    "if_statment": 1 if True else 0,
    "for_loop": [i for i in range(5)],
    "while_loop": [i for i in range(5) if i % 2 == 0],
    "class_instance": CustomClass(42).value,
    "set_of_primitives": {1, 2, 3, 4},
    "large_list": list(range(1000)),
    "empty_string": "",
    "empty_list": [],
    "empty_dict": {},
    "empty_set": set(),
    "empty_tuple": (),
    "infinite_float": float('inf'),
    "negative_infinite_float": float('-inf'),
    "negative_zero": -0.0,
    "negative_int": -42,
    "float_nan": float('nan'),
    "float_inf": float('inf'),
    "float_-inf": float('-inf')
}

recursive = []
recursive.append(recursive)
TEST_CASES["recursive_list"] = recursive

def hash_and_store_pickle(obj, name, protocol=pickle.HIGHEST_PROTOCOL):
    data = pickle.dumps(obj, protocol=protocol)
    hash_digest = hashlib.sha256(data).hexdigest()
    b64_data = base64.b64encode(data).decode('utf-8')

    result = {
        "test_case": name,
        "hash": hash_digest,
        "pickle_data_base64": b64_data,
        "protocol": protocol,
        "python_version": sys.version,
        "platform": platform.platform()
    }

    dir_name = ""

    if "Linux" in platform.platform():
        dir_name = "Linux"
    elif "Windows" in platform.platform():
        dir_name = "Windows"
    else:
        dir_name = "Other"

    os.makedirs(dir_name, exist_ok=True)
    with open(os.path.join(dir_name, f"{name}.json"), "w") as f:
        json.dump(result, f, indent=2)

def create_pickle_file(protocol=pickle.HIGHEST_PROTOCOL):
    print("Creating pickle files...")
    for name, obj in TEST_CASES.items():
        hash_and_store_pickle(obj, name, protocol)
    print("Pickle files created.")

def load_pickle_files():
    results = {}
    for file_name in ["Linux", "Windows", "Other"]:
        if not os.path.exists(file_name):
            continue
        results[file_name] = {}
        for root, _, files in os.walk(file_name):
            for name in files:
                if name.endswith(".json"):
                    with open(os.path.join(root, name), "r") as f:
                        data = json.load(f)
                        results[file_name][name] = {
                            "hash": data["hash"],
                            "pickle_data_base64": data["pickle_data_base64"],
                            "protocol": data["protocol"],
                            "python_version": data["python_version"],
                            "platform": data["platform"]
                        }
    return results

def compare_results():
    linux_results = load_pickle_files().get("Linux", {})
    windows_results = load_pickle_files().get("Windows", {})

    differences = []

    for name in linux_results.keys() | windows_results.keys():
        linux_data = linux_results.get(name)
        windows_data = windows_results.get(name)

        if not linux_data or not windows_data:
            differences.append({
                "test_case": name,
                "status": "MISSING",
                "details": "Missing in one of the platforms"
            })
            continue

        if linux_data["hash"] != windows_data["hash"]:
            differences.append({
                "test_case": name,
                "status": "DIFFERENT",
                "details": "Hash mismatch"
            })

    return differences

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("create_file", help="If the pickle files should be created or not")
    args = parser.parse_args()

    if args.create_file == "False":
        create_files = False
    else:
        create_files = True
    if create_files:
        for folder in ["Linux", "Windows", "Other"]:
            if os.path.exists(folder) and folder in platform.platform():
                for root, dirs, files in os.walk(folder, topdown=False):
                    for file in files:
                        os.remove(os.path.join(root, file))
                    for dir in dirs:
                        os.rmdir(os.path.join(root, dir))
                os.rmdir(folder)
        create_pickle_file()
    else:
        final_results = compare_results()
        print("Comparison Results:")
        if final_results == []:
            print("No differences found.")
        for result in final_results:
            print(f"Test case: {result['test_case']}, Status: {result['status']}, Details: {result['details']}")
