import os
import pathlib
import time

from grounded_stability import StabilitySolver
from reachability import ReachabilitySolver
from reachable_preprocessing import GroundedRelevanceWithPreprocessingSolver


def run_grounded_relevance_experiments():
    with open(pathlib.Path('experiment_results') / 'grounded_rel.csv',
              'w') as write_file_h1:
        write_file_h1.write(f'Arguments;Attacks;PercentageIncomplete;Index;'
                            f'Runtime;PreprocessingTime;GroundingTime;'
                            f'FirstModelTime;Timeout;NrRelevant;'
                            f'NrReachable;StabilityTime;StabilityStatus\n')
    with open(pathlib.Path('experiment_results') / 'grounded_rel_pp.csv',
              'w') as write_file_h2:
        write_file_h2.write(
            f'Arguments;Attacks;PercentageIncomplete;Index;'
            f'Runtime;PreprocessingTime;GroundingTime;'
            f'FirstModelTime;Timeout;NrRelevant;'
            f'NrReachable;StabilityTime;StabilityStatus\n')
    with os.scandir('generated') as entries:
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

            for with_preprocess in [True, False]:
                grounding_t = ''
                start_to_first_model_t = ''
                timeout = 0

                if with_preprocess:
                    filename = 'grounded_rel_pp.csv'
                else:
                    filename = 'grounded_rel.csv'

                start_time = time.time()
                solver = GroundedRelevanceWithPreprocessingSolver()
                solver.enumerate_grounded_relevant_updates(
                    iat_file.path, with_preprocess)
                end_time = time.time()
                print(end_time - start_time)

                preprocessing_time = \
                    solver.end_preprocessing_time - \
                    solver.start_preprocessing_time
                print(f'Preprocessing time: {preprocessing_time}')
                preprocessing_t = str(preprocessing_time).replace('.', ',')

                if solver.end_grounding_time:
                    grounding_time = solver.end_grounding_time - \
                                     solver.start_grounding_time
                    print(f'Grounding time: {grounding_time}')
                    grounding_t = str(grounding_time).replace('.', ',')

                if solver.first_model_time:
                    start_to_first_model_time = \
                        solver.first_model_time - start_time
                    print(f'Time to first model: '
                          f'{start_to_first_model_time}')
                    start_to_first_model_t = str(
                        start_to_first_model_time).replace('.', ',')

                if solver.finished_time is None:
                    timeout = 1

                nr_of_relevant_items = 0
                if solver.last_model:
                    nr_of_relevant_items = len(solver.last_model)
                print(f'Nr relevant: {nr_of_relevant_items}')

                _, nr_args, nr_atts, perc_inc, _, _, index = \
                    iat_file.path.split('_', 7)
                index = index.split('.', 1)[0]
                duration_t = str(end_time - start_time).replace('.', ',')

                with open(pathlib.Path('experiment_results') / filename, 'a') \
                        as write_file:
                    write_file.write(
                        f'{nr_args};{nr_atts};{perc_inc};{index};'
                        f'{duration_t};{preprocessing_t};{grounding_t};'
                        f'{start_to_first_model_t};{timeout};'
                        f'{nr_of_relevant_items};{nr_reachable_items};'
                        f'{stability_time};{stability_status}\n')


if __name__ == '__main__':
    run_grounded_relevance_experiments()
