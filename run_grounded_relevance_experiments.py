import os
import pathlib
import time

from grounded_relevance import GroundedRelevanceSolver
from grounded_stability import StabilitySolver
from reachability import ReachabilitySolver
from timeout import timeout


@timeout(60)
def run_single_grounded_relevance_experiment(iat_file):
    solver = GroundedRelevanceSolver()
    solver.enumerate_grounded_relevant_updates(iat_file)
    return solver


def run_grounded_relevance_experiments():
    with os.scandir('generated') as entries:
        with open(pathlib.Path('experiment_results') / 'grounded_rel.csv',
                  'w') as write_file:
            write_file.write(f'Arguments;Attacks;PercentageIncomplete;Index'
                             f';Runtime;GroundingTime;Timeout;NrRelevant'
                             f';NrReachable;StabilityTime;StabilityStatus\n')
            for iat_file in entries:
                print(iat_file.path)

                # Reachability
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

                try:
                    start_time = time.time()
                    solver = run_single_grounded_relevance_experiment(
                        iat_file.path)
                    end_time = time.time()
                    print(end_time - start_time)

                    grounding_time = solver.grounding_time
                    print(f'Grounding time: {grounding_time}')
                    grounding_time = str(grounding_time).replace('.', ',')

                    nr_of_relevant_items = 0
                    if solver.last_model:
                        nr_of_relevant_items = len(solver.last_model)
                    print(f'Nr relevant: {nr_of_relevant_items}')

                    _, nr_args, nr_atts, perc_inc, _, _, index = \
                        iat_file.path.split('_', 7)
                    index = index.split('.', 1)[0]
                    duration = str(end_time - start_time).replace('.', ',')
                    write_file.write(f'{nr_args};{nr_atts};{perc_inc};'
                                     f'{index};{duration};{grounding_time};0;'
                                     f'{nr_of_relevant_items};'
                                     f'{nr_reachable_items};'
                                     f'{stability_time};{stability_status}\n')
                except TimeoutError:
                    # print('Timed out')
                    write_file.write(f'{nr_args};{nr_atts};{perc_inc};'
                                     f'{index};;;1;;{nr_reachable_items};'
                                     f'{stability_time};{stability_status}\n')


if __name__ == '__main__':
    run_grounded_relevance_experiments()
