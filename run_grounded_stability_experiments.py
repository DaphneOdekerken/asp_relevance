import os
import time

from grounded_stability import StabilitySolver
from timeout import timeout


@timeout(5)
def run_single_stability_experiment(iat_file):
    solver = StabilitySolver()
    solver.enumerate_stable_arguments(iat_file)
    return solver


def run_grounded_stability_experiments():
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


if __name__ == '__main__':
    run_grounded_stability_experiments()
