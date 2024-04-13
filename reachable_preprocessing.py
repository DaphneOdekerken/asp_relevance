import time

import clingo
import pathlib


PATH_TO_ENCODINGS = pathlib.Path('encodings')


class ReachabilityPreprocessor:
    def __init__(self):
        self.last_model = None

    def on_model(self, model):
        self.last_model = model.symbols(shown=True)

    def enumerate_reachable(self, iaf_file):
        control = clingo.Control()
        control.load(str(iaf_file))
        control.load(str(PATH_TO_ENCODINGS / 'reachable_preprocessing.dl'))
        control.ground([('base', [])], context=self)
        with control.solve(on_model=self.on_model, async_=True) as handle:
            handle.wait(5)
            handle.cancel()
        with open('temp.lp', 'w') as writer:
            writer.write('topic(a0).\n')
            if self.last_model:
                for symbols in self.last_model:
                    writer.write(str(symbols)[2:] + '.\n')
        return 'temp.lp'


class GroundedRelevanceWithPreprocessingSolver:
    def __init__(self):
        self.last_model = None
        self.start_preprocessing_time = None
        self.end_preprocessing_time = None
        self.start_grounding_time = None
        self.end_grounding_time = None
        self.first_model_time = None
        self.finished_time = None

    def on_model(self, model):
        self.last_model = model.symbols(shown=True)
        if not self.first_model_time:
            if any('relevant' in symbols.name for symbols in self.last_model):
                self.first_model_time = time.time()

    def save_finished(self, _result):
        self.finished_time = time.time()

    def enumerate_grounded_relevant_updates(self, iaf_file, preprocess=True):
        self.start_preprocessing_time = time.time()
        if preprocess:
            file = ReachabilityPreprocessor().enumerate_reachable(iaf_file)
        else:
            file = iaf_file
        self.end_preprocessing_time = time.time()

        control = clingo.Control(arguments=['--enum-mode=brave'])
        control.load(file)
        control.load(str(PATH_TO_ENCODINGS / 'filter.lp'))
        control.load(str(PATH_TO_ENCODINGS / 'grounded.dl'))
        control.load(str(PATH_TO_ENCODINGS / 'labels.dl'))
        control.load(str(PATH_TO_ENCODINGS / 'guess.dl'))
        control.load(str(PATH_TO_ENCODINGS / 'valid_completion.dl'))
        control.load(str(PATH_TO_ENCODINGS / 'grounded_relevant_args.dl'))
        control.load(str(PATH_TO_ENCODINGS / 'query_arg.dl'))
        control.load(str(PATH_TO_ENCODINGS / 'grounded_relevant_atts.dl'))
        control.load(str(PATH_TO_ENCODINGS / 'query_att.dl'))

        self.start_grounding_time = time.time()
        control.ground([('base', [])], context=self)
        self.end_grounding_time = time.time()

        control.solve(on_model=self.on_model, on_finish=self.save_finished)
