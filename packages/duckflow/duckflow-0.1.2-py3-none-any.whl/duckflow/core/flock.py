import os
import json
import logging
from .duck import Duck

logger = logging.getLogger("duckflow")

def load_ducks(directory, defaults):
    duck_map = {}
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            with open(os.path.join(directory, filename)) as f:
                config = json.load(f)
            duck = Duck(config, defaults)
            duck_map[duck.id] = duck
    return duck_map

def load_flock_defs(path):
    with open(path) as f:
        return json.load(f)["flocks"]

def run_single_flock(duck_map, steps, input_text):
    data = input_text
    for step in steps:
        duck = duck_map[step["id"]]
        data = duck.run(data)
    return data

def run_flock(flocks, flock_name, duck_map, results, input_text):
    logger.info(f"Running flock: {flock_name}")
    steps = flocks[flock_name]
    if any("inputs" in step for step in steps):
        merged_inputs = {}
        for step in steps:
            if "inputs" in step:
                for dep in step["inputs"]:
                    if dep not in results:
                        results[dep] = run_flock(flocks, dep, duck_map, results, input_text)
                merged_inputs = {dep: results[dep] for dep in step["inputs"]}
                input_text = json.dumps(merged_inputs)
    output = run_single_flock(duck_map, steps, input_text)
    results[flock_name] = output
    return output
