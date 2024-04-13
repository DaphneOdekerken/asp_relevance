import clingo
import pathlib


PATH_TO_ENCODINGS = pathlib.Path('encodings')


class StabilitySolver:
    def __init__(self):
        self.last_model = None

    def on_model(self, model):
        self.last_model = model.symbols(shown=True)

    def enumerate_stable_arguments(self, iaf_file):
        control = clingo.Control(arguments=['--enum-mode=cautious'])
        control.load(str(iaf_file))
        control.load(str(PATH_TO_ENCODINGS / 'stability_filter.lp'))
        control.load(str(PATH_TO_ENCODINGS / 'grounded.dl'))
        control.load(str(PATH_TO_ENCODINGS / 'labels.dl'))
        control.load(str(PATH_TO_ENCODINGS / 'guess.dl'))
        control.load(str(PATH_TO_ENCODINGS / 'valid_completion.dl'))
        control.ground([('base', [])], context=self)
        control.solve(on_model=self.on_model)


if __name__ == '__main__':
    example = pathlib.Path('examples') / 'small.lp'
    solver = StabilitySolver()
    solver.enumerate_stable_arguments(example)
    for symbols in solver.last_model:
        print(str(symbols))
