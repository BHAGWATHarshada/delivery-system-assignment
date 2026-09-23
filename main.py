import argparse
import json
import os

from delivery import generate_report
from utils import load_json


def main():
    parser = argparse.ArgumentParser(description='Mystery Delivery System')
    parser.add_argument('input', nargs='?', default='base_case.json', help='input JSON file')
    parser.add_argument('--output', '-o', default='report.json', help='output report file')
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f" file not found  : {args.input}")
        return

    data = load_json(args.input)
    report = generate_report(data)

    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=4)

    print(f"report written to {args.output}")


if __name__ == '__main__':
    main()
