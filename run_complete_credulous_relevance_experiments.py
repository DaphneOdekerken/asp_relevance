import os
import pathlib
import time
from multiprocessing import Queue, Process
from queue import Empty

from complete_credulous_relevance import CompleteRelevanceSolver
from complete_credulous_stability import CompleteCredulousStabilitySolver
from reachability import ReachabilitySolver

SECONDS_UNTIL_TIMEOUT = 60
EXPERIMENT_RESULTS_FOLDER = pathlib.Path('experiment_results')


def run_single_complete_credulous_relevance_experiment(iat_file, queue):
    solver = CompleteRelevanceSolver()
    rel_arguments_to_add, rel_attacks_to_add, \
        rel_arguments_to_remove, rel_attacks_to_remove = \
        solver.enumerate_complete_credulous_relevant_updates(
            iat_file, 'in', 'a0')
    nr_relevant_items = \
        len(rel_arguments_to_add) + len(rel_attacks_to_add) \
        + len(rel_arguments_to_remove) + len(rel_attacks_to_remove)

    queue.put(nr_relevant_items)


def run_complete_relevance_experiments():
    if not EXPERIMENT_RESULTS_FOLDER.exists():
        EXPERIMENT_RESULTS_FOLDER.mkdir()
    with open(EXPERIMENT_RESULTS_FOLDER / 'complete_rel.csv',
              'w') as write_file_h1:
        write_file_h1.write(f'Arguments;Attacks;PercentageIncomplete;Index;'
                            f'Runtime;Timeout;NrRelevant;'
                            f'NrReachable;StabilityTime;StabilityStatus\n')
    with os.scandir('generated_complete') as entries:
        for iat_file in entries:
            print(iat_file.path)

            # Reachability: count number of reachable
            nr_reachable_items = 0
            solver = ReachabilitySolver()
            solver.enumerate_reachable(iat_file.path)
            if solver.last_model:
                nr_reachable_items = len(solver.last_model)
            print(f'Nr reachable: {nr_reachable_items}')

            # Stability
            start_time = time.time()
            solver = CompleteCredulousStabilitySolver()
            complete_credulous_stable = \
                solver.get_complete_credulous_stability(iat_file.path,
                                                        'in', 'a0')
            end_time = time.time()
            stability_time = (end_time - start_time)
            print(f'Stability-time: {stability_time}')
            stability_time = str(stability_time).replace('.', ',')

            start_time = time.time()

            # Create the shared queue
            queue = Queue()
            # Configure the child process
            process = Process(
                target=run_single_complete_credulous_relevance_experiment,
                args=(iat_file.path, queue,))
            # Start the child process
            process.start()
            # Wait for the result with a timeout
            try:
                # Get the result from the queue
                nr_relevant_items = queue.get(timeout=SECONDS_UNTIL_TIMEOUT)
                timed_out = 0

                # Stop the clock!
                end_time = time.time()
                duration_t = str(end_time - start_time).replace('.', ',')
                print('Total time: ' + duration_t)

                print('Nr of relevant items: ' + str(nr_relevant_items))
                print('NO TIMEOUT')
            except Empty:
                # No result in time limit, terminate
                process.terminate()
                # return no result
                print('TIMEOUT')

                duration_t = ''
                nr_relevant_items = ''
                timed_out = 1

            _, nr_args, nr_atts, perc_inc, _, _, index = \
                iat_file.name.split('_', 7)
            index = index.split('.', 1)[0]

            with open(pathlib.Path('experiment_results') / 'complete_rel.csv',
                      'a') as write_file:
                write_file.write(
                    f'{nr_args};{nr_atts};{perc_inc};{index};'
                    f'{duration_t};{timed_out};{nr_relevant_items};'
                    f'{nr_reachable_items};{stability_time};'
                    f'{complete_credulous_stable}\n')


if __name__ == '__main__':
    run_complete_relevance_experiments()
