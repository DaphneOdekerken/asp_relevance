import os
import time

from complete_credulous_relevance import CompleteRelevanceSolver
from timeout import timeout


@timeout(5)
def run_single_complete_credulous_relevance_experiment(iat_file):
    solver = CompleteRelevanceSolver()
    result = solver.enumerate_complete_credulous_relevant_updates(
        iat_file, 'in', 'a0')
    return result


def run_grounded_relevance_experiments():
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


if __name__ == '__main__':
    run_grounded_relevance_experiments()
