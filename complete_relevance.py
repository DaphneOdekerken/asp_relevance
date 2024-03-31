import clingo
import pathlib


PATH_TO_ENCODINGS = pathlib.Path('encodings')


class CompleteRelevanceSolver:
    def __init__(self):
        self.last_model = None
        self.new_completion_model = None
        self.last_completion_arguments = []
        self.last_completion_attacks = []
        self.topics = []
        self.initial_arguments = []
        self.initial_attacks = []
        self.uncertain_arguments = []
        self.uncertain_attacks = []

    def _parse_input(self, iaf_file):
        with open(iaf_file, 'r') as infile:
            text = infile.read().split("\n")

        for line in text:
            if line.startswith('topic'):
                self.topics.append(line.split('(')[1].split(')')[0])
            elif line.startswith('uarg'):
                self.uncertain_arguments.append(
                    line.split('(')[1].split(')')[0])
            elif line.startswith('uatt'):
                attack_from, attack_to = \
                    map(str.strip, line.split('(')[1].split(')')[0].split(','))
                self.uncertain_attacks.append((attack_from, attack_to))
            elif line.startswith('argument'):
                self.initial_arguments.append(
                    line.split('(')[1].split(')')[0])
            elif line.startswith('att'):
                attack_from, attack_to = \
                    map(str.strip, line.split('(')[1].split(')')[0].split(','))
                self.initial_attacks.append((attack_from, attack_to))

    def store_completion(self, model):
        self.last_model = model.symbols(shown=True)
        self.last_completion_arguments = []
        self.last_completion_attacks = []
        for symbol in self.last_model:
            if symbol.name == 'argument':
                self.last_completion_arguments.append(symbol.arguments[0].name)
            elif symbol.name == 'att':
                self.last_completion_attacks.append(
                    (symbol.arguments[0].name, symbol.arguments[1].name))

    def store_satisfiable(self, model):
        self.new_completion_model = model.symbols(shown=True)

    def enumerate_complete_relevant_updates(self, iaf_file, label, topic):
        self._parse_input(iaf_file)

        # NB: Credulous.

        # Line 2: instantiate relevant to add and remove.
        relevant_arguments_to_add = set()
        relevant_attacks_to_add = set()
        relevant_arguments_to_remove = set()
        relevant_attacks_to_remove = set()

        # Line 3: prepare clingo.
        guess_control = clingo.Control()
        guess_control.load(str(iaf_file))
        guess_control.load(str(PATH_TO_ENCODINGS / 'complete.dl'))
        guess_control.load(str(PATH_TO_ENCODINGS / 'valid_completion.dl'))
        guess_control.load(str(PATH_TO_ENCODINGS / 'labels.dl'))
        guess_control.load(str(PATH_TO_ENCODINGS / 'externals.dl'))
        guess_control.load(str(PATH_TO_ENCODINGS / 'guess.dl'))
        guess_control.ground([('base', [])], context=self)

        completion_control = clingo.Control()
        completion_control.load(str(iaf_file))
        completion_control.load(str(PATH_TO_ENCODINGS / 'complete.dl'))
        completion_control.load(str(PATH_TO_ENCODINGS / 'valid_completion.dl'))
        completion_control.load(str(PATH_TO_ENCODINGS / 'labels.dl'))
        completion_control.load(str(PATH_TO_ENCODINGS / 'externals.dl'))
        completion_control.ground([('base', [])], context=self)

        topic_label = clingo.Function('lab', [
            clingo.Function(label),
            clingo.Function(topic)
        ])
        topic_has_label = (topic_label, True)

        # Line 4.
        while True:
            # Line 5.
            with guess_control.solve(
                    on_model=self.store_completion, async_=True,
                    assumptions=[topic_has_label]) as handle:
                handle.wait(5)
                handle.cancel()

            # Line 6.
            if self.last_model:
                # Line 7 and 8 are handled in self.store_completion
                pass

                # Line 9 (for uncertain arguments).
                for query_uncertain_argument in self.uncertain_arguments:
                    # Line 10: check if query is new in this completion.
                    if query_uncertain_argument in \
                            self.last_completion_arguments:
                        # Line 11: Make completion without query.
                        externals_to_remove_later = []
                        for uarg in self.uncertain_arguments:
                            if uarg in self.last_completion_arguments and \
                                    uarg != query_uncertain_argument:
                                new_a = clingo.Function(
                                    'eargument', [clingo.Function(uarg)])
                            else:
                                new_a = clingo.Function(
                                    'enargument', [clingo.Function(uarg)])
                            completion_control.assign_external(new_a, True)
                            externals_to_remove_later.append(new_a)
                        for uatt in self.uncertain_attacks:
                            if uatt in self.last_completion_attacks:
                                new_a = clingo.Function(
                                    'eatt', [clingo.Function(uatt[0]),
                                            clingo.Function(uatt[1])])
                            else:
                                new_a = clingo.Function(
                                    'enatt', [clingo.Function(uatt[0]),
                                             clingo.Function(uatt[1])])
                            completion_control.assign_external(new_a, True)
                            externals_to_remove_later.append(new_a)

                        # Line 13: run solver for completion.
                        with completion_control.solve(
                                on_model=self.store_satisfiable,
                                async_=True,
                                assumptions=[topic_has_label]) as handle:
                            handle.wait(5)
                            handle.cancel()
                        # Line 14.
                        if not self.new_completion_model:
                            # Line 15.
                            relevant_arguments_to_add.add(
                                query_uncertain_argument)

                        # Cleaning up
                        self._clean_up_after_completion(completion_control,
                                                        externals_to_remove_later)

                    # Line 16.
                    else:
                        # Line 17: Make completion with query.
                        externals_to_remove_later = []
                        new_completion_arguments = \
                            self.last_completion_arguments + [
                                query_uncertain_argument]
                        for uarg in self.uncertain_arguments:
                            if uarg in new_completion_arguments:
                                new_a = clingo.Function(
                                    'eargument', [clingo.Function(uarg)])
                            else:
                                new_a = clingo.Function(
                                    'enargument', [clingo.Function(uarg)])
                            completion_control.assign_external(new_a, True)
                            externals_to_remove_later.append(new_a)
                        for uatt in self.uncertain_attacks:
                            if uatt in self.last_completion_attacks:
                                new_a = clingo.Function(
                                    'eatt', [clingo.Function(uatt[0]),
                                            clingo.Function(uatt[1])])
                            else:
                                new_a = clingo.Function(
                                    'enatt', [clingo.Function(uatt[0]),
                                             clingo.Function(uatt[1])])
                            completion_control.assign_external(new_a, True)
                            externals_to_remove_later.append(new_a)

                        # Line 19: run solver for completion.
                        with completion_control.solve(
                                on_model=self.store_satisfiable,
                                async_=True,
                                assumptions=[topic_has_label]) as handle:
                            handle.wait(5)
                            handle.cancel()
                        # Line 20.
                        if not self.new_completion_model:
                            # Line 21.
                            relevant_arguments_to_remove.add(
                                query_uncertain_argument)

                        # Cleaning up
                        self._clean_up_after_completion(completion_control,
                                                        externals_to_remove_later)

                # Line 9 (for uncertain attacks).
                for query_uncertain_attack in self.uncertain_attacks:
                    # Line 10: check if query is new in this completion.
                    if query_uncertain_attack in \
                            self.last_completion_attacks:
                        # Line 11: Make completion without query.
                        externals_to_remove_later = []
                        for uarg in self.uncertain_arguments:
                            if uarg in self.last_completion_arguments:
                                new_a = clingo.Function(
                                    'eargument',
                                    [clingo.Function(uarg)])
                            else:
                                new_a = clingo.Function(
                                    'enargument',
                                    [clingo.Function(uarg)])
                            completion_control.assign_external(new_a, True)
                            externals_to_remove_later.append(new_a)
                        for uatt in self.uncertain_attacks:
                            if uatt != query_uncertain_attack and \
                                    uatt in self.last_completion_attacks:
                                new_a = clingo.Function(
                                    'eatt', [clingo.Function(uatt[0]),
                                            clingo.Function(uatt[1])])
                            else:
                                new_a = clingo.Function(
                                    'enatt', [clingo.Function(uatt[0]),
                                             clingo.Function(uatt[1])])
                            completion_control.assign_external(new_a, True)
                            externals_to_remove_later.append(new_a)

                        # Line 13: run solver for completion.
                        with completion_control.solve(
                                on_model=self.store_satisfiable,
                                async_=True,
                                assumptions=[topic_has_label]) as handle:
                            handle.wait(5)
                            handle.cancel()
                        # Line 14.
                        if not self.new_completion_model:
                            # Line 15.
                            relevant_attacks_to_add.add(
                                query_uncertain_attack)

                        # Cleaning up
                        self._clean_up_after_completion(completion_control,
                                                        externals_to_remove_later)

                    # Line 16.
                    else:
                        # Line 17: Make completion with query.
                        externals_to_remove_later = []
                        for uarg in self.uncertain_arguments:
                            if uarg in self.last_completion_arguments:
                                new_a = clingo.Function(
                                    'eargument', [clingo.Function(uarg)])
                            else:
                                new_a = clingo.Function(
                                    'enargument', [clingo.Function(uarg)])
                            completion_control.assign_external(new_a, True)
                            externals_to_remove_later.append(new_a)
                        for uatt in self.uncertain_attacks:
                            if uatt in self.last_completion_attacks or \
                                    uatt == query_uncertain_attack:
                                new_a = clingo.Function(
                                    'eatt', [clingo.Function(uatt[0]),
                                            clingo.Function(uatt[1])])
                            else:
                                new_a = clingo.Function(
                                    'enatt', [clingo.Function(uatt[0]),
                                             clingo.Function(uatt[1])])
                            completion_control.assign_external(new_a, True)
                            externals_to_remove_later.append(new_a)

                        # Line 19: run solver for completion.
                        with completion_control.solve(
                                on_model=self.store_satisfiable,
                                async_=True,
                                assumptions=[topic_has_label]) as handle:
                            handle.wait(5)
                            handle.cancel()
                        # Line 20.
                        if not self.new_completion_model:
                            # Line 21.
                            relevant_attacks_to_remove.add(
                                query_uncertain_attack)

                        # Cleaning up
                        self._clean_up_after_completion(completion_control,
                                                        externals_to_remove_later)

                # Line 22: refine the original solver.
                with guess_control.backend() as backend:
                    refinement_rule_body = []
                    for uncertain_arg in self.uncertain_arguments:
                        if uncertain_arg in self.last_completion_arguments:
                            argument_sym = clingo.Function(
                                'argument', [clingo.Function(uncertain_arg)])
                            argument_atom = backend.add_atom(argument_sym)
                            refinement_rule_body.append(argument_atom)
                        else:
                            not_arg_sym = clingo.Function(
                                'nargument', [clingo.Function(uncertain_arg)])
                            not_argument_atom = backend.add_atom(not_arg_sym)
                            refinement_rule_body.append(not_argument_atom)
                    for u_att in self.uncertain_attacks:
                        if u_att[0] in self.last_completion_arguments and \
                                u_att[1] in self.last_completion_arguments:
                            if u_att in self.last_completion_attacks:
                                attack_sym = clingo.Function(
                                    'att', [clingo.Function(u_att[0]),
                                            clingo.Function(u_att[1])])
                                attack_atom = backend.add_atom(attack_sym)
                                refinement_rule_body.append(attack_atom)
                            else:
                                not_attack_sym = clingo.Function(
                                    'natt', [clingo.Function(u_att[0]),
                                             clingo.Function(u_att[1])])
                                not_attack_atom = backend.add_atom(
                                    not_attack_sym)
                                refinement_rule_body.append(not_attack_atom)
                    backend.add_rule(head=[], body=refinement_rule_body)

                # Cleaning up.
                self.last_model = None

            else:
                return relevant_arguments_to_add, relevant_attacks_to_add, \
                    relevant_arguments_to_remove, relevant_attacks_to_remove

    def _clean_up_after_completion(self, completion_control,
                                  externals_to_remove_later):
        for external_to_remove in externals_to_remove_later:
            completion_control.assign_external(
                external_to_remove, False)
        self.new_completion_model = None


if __name__ == '__main__':
    example = pathlib.Path('examples') / 'ac.lp'
    solver = CompleteRelevanceSolver()
    rel_arguments_to_add, rel_attacks_to_add, \
        rel_arguments_to_remove, rel_attacks_to_remove = \
        solver.enumerate_complete_relevant_updates(example, 'in', 'c')
    print('Relevant to add:')
    print(rel_arguments_to_add)
    print(rel_attacks_to_add)
    print('Relevant to remove:')
    print(rel_arguments_to_remove)
    print(rel_attacks_to_remove)
