import os

import clingo

from complete_credulous_stability import CompleteCredulousStabilitySolver
from complete_sceptical_stability import CompleteScepticalStabilitySolver
from grounded_stability import GroundedStabilitySolver

with os.scandir('generated_grounded') as entries:
    for iaf_file in entries:
        grounded_solver = GroundedStabilitySolver()
        grounded_solver.enumerate_stable_arguments(iaf_file.path)
        grounded_in_stable = \
            clingo.Function('is_in', [clingo.Function('a0')]) in \
            grounded_solver.last_model
        grounded_out_stable = \
            clingo.Function('is_out', [clingo.Function('a0')]) in \
            grounded_solver.last_model
        grounded_undec_stable = \
            clingo.Function('is_undec', [clingo.Function('a0')]) in \
            grounded_solver.last_model

        complete_sceptical_solver = CompleteScepticalStabilitySolver()
        complete_sceptical_solver.enumerate_stable_arguments(iaf_file.path)
        complete_sceptical_in_stable = \
            clingo.Function('is_in', [clingo.Function('a0')]) in \
            complete_sceptical_solver.last_model
        complete_sceptical_out_stable = \
            clingo.Function('is_out', [clingo.Function('a0')]) in \
            complete_sceptical_solver.last_model

        complete_credulous_solver = CompleteCredulousStabilitySolver()
        complete_credulous_undec_stable = \
            complete_credulous_solver.get_complete_credulous_stability(
                iaf_file.path, 'undec', 'a0')

        # Test sceptical IN/OUT stability (same for GR and CP)
        if grounded_in_stable != complete_sceptical_in_stable:
            raise Exception('IN stability statuses did not correspond.')
        if grounded_out_stable != complete_sceptical_out_stable:
            raise Exception('OUT stability statuses did not correspond.')

        # Test credulous UNDEC stability (same for GR and CP)
        if grounded_undec_stable != complete_credulous_undec_stable:
            raise Exception('UNDEC stability statuses did not correspond.')
