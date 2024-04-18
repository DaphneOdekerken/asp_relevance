import pathlib

from generate_dataset import generate_dataset
from run_complete_credulous_relevance_experiments import \
    run_complete_relevance_experiments
from run_grounded_relevance_experiments import \
    run_grounded_relevance_experiments

if __name__ == '__main__':
    generate_dataset(pathlib.Path('generated_grounded'),
                     [50, 100, 150, 200, 250])
    run_grounded_relevance_experiments()
    generate_dataset(pathlib.Path('generated_complete'),
                     [5, 10, 15, 20, 25])
    run_complete_relevance_experiments()
