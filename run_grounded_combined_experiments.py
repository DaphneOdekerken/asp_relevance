import os
import time

from grounded_relevance import GroundedRelevanceSolver
from grounded_stability import StabilitySolver
from timeout import timeout


@timeout(5)
def run_single_stability_experiment(iat_file):
    solver = StabilitySolver()
    solver.enumerate_stable_arguments(iat_file)
    return solver


@timeout(5)
def run_single_grounded_relevance_experiment(iat_file):
    solver = GroundedRelevanceSolver()
    solver.enumerate_grounded_relevant_updates(iat_file)
    return solver


def run_combined_experiments():
    with os.scandir('generated') as entries:
        for iat_file in entries:
            print(iat_file.path)

            try:
                start_time = time.time()
                solver = run_single_stability_experiment(iat_file.path)
                end_time = time.time()
                print(end_time - start_time)
                if solver.last_model:
                    for symbols in solver.last_model:
                        print(str(symbols))
                else:
                    print('No model')
            except TimeoutError:
                print('Timed out')

            try:
                start_time = time.time()
                solver = run_single_grounded_relevance_experiment(
                    iat_file.path)
                end_time = time.time()
                print(end_time - start_time)
                if solver.last_model:
                    for symbols in solver.last_model:
                        print(str(symbols))
                else:
                    print('No model')
            except TimeoutError:
                print('Timed out')

            print('\n\n')


if __name__ == '__main__':
    run_combined_experiments()
