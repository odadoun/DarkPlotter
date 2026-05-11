import os
import sys
import hashlib
import json
import argparse

def AddHash(json_file):

    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            dictionary = json.load(f)
            input_string = dictionary["parameters-space"]+dictionary["collaboration"]+dictionary["experiment"]+dictionary["label"]
            hash_object = hashlib.md5(input_string.encode())
            hash_string = hash_object.hexdigest()
            dir_path, filename = os.path.split(json_file)
            filename_with_hash = filename.split(".")[0]+"-"+hash_string+"."+filename.split(".")[1]
            json_file_with_hash = os.path.join(dir_path, filename_with_hash)
            os.system("mv {0} {1} ".format(json_file, json_file_with_hash))
            print(f"Successfully completed")
    except FileNotFoundError:
        print(f"Error: The file '{json_file}' does not exist.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: The file '{json_file}' is not a valid JSON file.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)    
    
def main():

    parser = argparse.ArgumentParser(description='Renames a JSON file, by adding a hash based on the content of the json')
    parser.add_argument('json_file', nargs='?', help='Path to the JSON file')

    args = parser.parse_args()

    if args.json_file:
        AddHash(args.json_file)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()


