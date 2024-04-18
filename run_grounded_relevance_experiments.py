import os
import pathlib
import time

from multiprocessing import Process, Queue
from queue import Empty

from grounded_stability import StabilitySolver
from reachability import ReachabilitySolver
from grounded_relevance import GroundedRelevanceWithPreprocessingSolver


SECONDS_UNTIL_TIMEOUT = 60
EXPERIMENT_RESULTS_FOLDER = pathlib.Path('experiment_results')


def run_single_experiment(iat_file, with_preprocess: bool, queue):
    solver = GroundedRelevanceWithPreprocessingSolver()
    solver.enumerate_grounded_relevant_updates(
        iat_file, with_preprocess)

    nr_relevant_items = len(solver.last_model)
    preprocessing_time = solver.end_preprocessing_time - \
        solver.start_preprocessing_time
    grounding_time = solver.end_grounding_time - solver.start_grounding_time

    queue.put((nr_relevant_items, preprocessing_time, grounding_time))


def run_grounded_relevance_experiments():
    if not EXPERIMENT_RESULTS_FOLDER.exists():
        EXPERIMENT_RESULTS_FOLDER.mkdir()
    with open(EXPERIMENT_RESULTS_FOLDER / 'grounded_rel.csv', 'w') as write_file_h1:
        write_file_h1.write(f'Arguments;Attacks;PercentageIncomplete;Index;'
                            f'Runtime;PreprocessingTime;GroundingTime;'
                            f'Timeout;NrRelevant;'
                            f'NrReachable;StabilityTime;StabilityStatus\n')
    with open(EXPERIMENT_RESULTS_FOLDER / 'grounded_rel_pp.csv',
              'w') as write_file_h2:
        write_file_h2.write(
            f'Arguments;Attacks;PercentageIncomplete;Index;'
            f'Runtime;PreprocessingTime;GroundingTime;'
            f'Timeout;NrRelevant;'
            f'NrReachable;StabilityTime;StabilityStatus\n')
    with os.scandir('generated_grounded') as entries:
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
            solver = StabilitySolver()
            solver.enumerate_stable_arguments(iat_file.path)
            end_time = time.time()
            stability_time = (end_time - start_time)
            print(f'Stability-time: {stability_time}')
            stability_time = str(stability_time).replace('.', ',')

            stability_status = ''
            if solver.last_model:
                for symbols in solver.last_model:
                    stability_status += str(symbols)
            else:
                stability_status = 'Unstable'

            for with_preprocess in [True, False]:
                if with_preprocess:
                    filename = 'grounded_rel_pp.csv'
                else:
                    filename = 'grounded_rel.csv'

                start_time = time.time()

                # Create the shared queue
                queue = Queue()
                # Configure the child process
                process = Process(
                    target=run_single_experiment,
                    args=(iat_file.path, with_preprocess, queue,))
                # Start the child process
                process.start()
                # Wait for the result with a timeout
                try:
                    # Get the result from the queue
                    nr_relevant_items, preprocessing_time, grounding_time = \
                        queue.get(timeout=SECONDS_UNTIL_TIMEOUT)
                    preprocessing_t = str(preprocessing_time).replace('.', ',')
                    grounding_t = str(grounding_time).replace('.', ',')
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
                    preprocessing_t = ''
                    grounding_t = ''
                    timed_out = 1

                _, nr_args, nr_atts, perc_inc, _, _, index = \
                    iat_file.name.split('_', 7)
                index = index.split('.', 1)[0]

                with open(pathlib.Path('experiment_results') / filename, 'a') \
                        as write_file:
                    write_file.write(
                        f'{nr_args};{nr_atts};{perc_inc};{index};'
                        f'{duration_t};{preprocessing_t};{grounding_t};'
                        f'{timed_out};'
                        f'{nr_relevant_items};{nr_reachable_items};'
                        f'{stability_time};{stability_status}\n')


if __name__ == '__main__':
    run_grounded_relevance_experiments()
