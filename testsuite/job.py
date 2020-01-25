import os

HERE = os.path.dirname(__file__)

def main(runtime):
    script = os.path.join(HERE, 'testscript.py')
    runtime.tasks.run(script)