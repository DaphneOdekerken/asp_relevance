import os
import pathlib
import time

from complete_credulous_relevance import CompleteRelevanceSolver
from timeout import timeout


def run_single_complete_credulous_relevance_experiment(iat_file):
    solver = CompleteRelevanceSolver()
    result = solver.enumerate_complete_credulous_relevant_updates(
        iat_file, 'in', 'a0')
    return result


def run_complete_relevance_experiments():
    with open(pathlib.Path('experiment_results') / 'complete_rel.csv',
              'w') as write_file_h1:
        write_file_h1.write(f'Arguments;Attacks;PercentageIncomplete;Index;'
                            f'Runtime;Timeout;NrRelevant\n')
    with os.scandir('generated') as entries:
        for iat_file in entries:
            print(iat_file.path)
            try:
                start_time = time.time()
                rel_arguments_to_add, rel_attacks_to_add, \
                    rel_arguments_to_remove, rel_attacks_to_remove = \
                    run_single_complete_credulous_relevance_experiment(
                        iat_file.path)
                end_time = time.time()
                print(end_time - start_time)
                print('Relevant to add:')
                print(rel_arguments_to_add)
                print(rel_attacks_to_add)
                print('Relevant to remove:')
                print(rel_arguments_to_remove)
                print(rel_attacks_to_remove)
            except TimeoutError:
                print('Timed out')

            _, nr_args, nr_atts, perc_inc, _, _, index = \
                iat_file.path.split('_', 7)
            index = index.split('.', 1)[0]
            duration_t = str(end_time - start_time).replace('.', ',')
            total_nr_relevant = len(rel_arguments_to_add) + len(
                rel_arguments_to_remove) + len(rel_attacks_to_add) + len(
                rel_attacks_to_remove)
            if end_time - start_time > 60:
                timeout = 1
            else:
                timeout = 0
            with open(pathlib.Path('experiment_results') / 'complete_rel.csv',
                      'a') as write_file:
                write_file.write(
                    f'{nr_args};{nr_atts};{perc_inc};{index};'
                    f'{duration_t};{timeout};{total_nr_relevant}\n')


if __name__ == '__main__':
    run_complete_relevance_experiments()
