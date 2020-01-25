import os

# compute relative location of this file
HERE = os.path.dirname(__file__)

def main(runtime):
    'main entry point for a job is the main() function'

    # find our abspath to the script
    script = os.path.join(HERE, 'testscript.py')

    # run this script as a task under this job
    # Note:
    #   if --testbed-file is provided, the corresponding loaded 'testbed'
    #   object will be provided to each script within this job automatically
    runtime.tasks.run(script)