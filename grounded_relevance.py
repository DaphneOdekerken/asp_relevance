import time

import clingo
import pathlib


PATH_TO_ENCODINGS = pathlib.Path('encodings')


class GroundedRelevanceSolver:
    def __init__(self):
        self.last_model = None
        self.grounding_time = None

    def on_model(self, model):
        self.last_model = model.symbols(shown=True)

    def enumerate_grounded_relevant_updates(self, iaf_file):
        control = clingo.Control(arguments=['--enum-mode=brave'])
        control.load(str(iaf_file))
        control.load(str(PATH_TO_ENCODINGS / 'filter.lp'))
        control.load(str(PATH_TO_ENCODINGS / 'grounded.dl'))
        control.load(str(PATH_TO_ENCODINGS / 'labels.dl'))
        control.load(str(PATH_TO_ENCODINGS / 'guess.dl'))
        control.load(str(PATH_TO_ENCODINGS / 'valid_completion.dl'))
        control.load(str(PATH_TO_ENCODINGS / 'grounded_relevant_args.dl'))
        control.load(str(PATH_TO_ENCODINGS / 'query_arg.dl'))
        control.load(str(PATH_TO_ENCODINGS / 'grounded_relevant_atts.dl'))
        control.load(str(PATH_TO_ENCODINGS / 'query_att.dl'))
        # control.load(str(PATH_TO_ENCODINGS / 'reachable.dl'))

        start_grounding_time = time.time()
        control.ground([('base', [])], context=self)
        end_grounding_time = time.time()
        self.grounding_time = end_grounding_time - start_grounding_time

        with control.solve(on_model=self.on_model, async_=True) as handle:
            handle.wait(5)
            handle.cancel()


if __name__ == '__main__':
    example = pathlib.Path('examples') / 'small.lp'
    solver = GroundedRelevanceSolver()
    solver.enumerate_grounded_relevant_updates(example)
    for symbols in solver.last_model:
        print(str(symbols))
