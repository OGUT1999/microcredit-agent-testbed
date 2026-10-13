"""Prints the Workflow args for every group of a day: python3 groupargs.py RUN_DIR DAY"""
import json, sys
run, day = sys.argv[1], int(sys.argv[2])
d = f"{run}/prompts/day{day}"
for k in range(10):
    g = json.load(open(f"{d}/group{k}.json"))
    print(f"GROUP {k}:", json.dumps({"agents": g}, separators=(",", ":")))
print("ROLES:", json.dumps({"agents": json.load(open(f"{d}/roles.json"))}, separators=(",", ":")))
