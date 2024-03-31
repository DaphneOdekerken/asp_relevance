import clingo
import pathlib


PATH_TO_ENCODINGS = pathlib.Path('encodings')


class GroundedRelevanceSolver:
    def __init__(self):
        self.last_model = None

    def on_model(self, model):
        self.last_model = model.symbols(shown=True)

    def enumerate_grounded_relevant_updates(self, iaf_file):
        control = clingo.Control(arguments=['--enum-mode=brave'])
        control.load(str(iaf_file))
        control.load(str(PATH_TO_ENCODINGS / 'filter.lp'))
        control.load(str(PATH_TO_ENCODINGS / 'grounded.dl'))
        control.load(str(PATH_TO_ENCODINGS / 'labels.dl'))
        control.load(str(PATH_TO_ENCODINGS / 'guess.dl'))
        control.load(str(PATH_TO_ENCODINGS / 'grounded_relevant_args.dl'))
        control.load(str(PATH_TO_ENCODINGS / 'query_arg.dl'))
        control.load(str(PATH_TO_ENCODINGS / 'grounded_relevant_atts.dl'))
        control.load(str(PATH_TO_ENCODINGS / 'query_att.dl'))
        control.ground([('base', [])], context=self)
        with control.solve(on_model=self.on_model, async_=True) as handle:
            handle.wait(5)
            handle.cancel()


if __name__ == '__main__':
    example = pathlib.Path('examples') / 'small.lp'
    solver = GroundedRelevanceSolver()
    solver.enumerate_grounded_relevant_updates(example)
    for symbols in solver.last_model:
        print(str(symbols))
