import pathlib
import random

nr_of_arguments_list = [50, 100, 150, 200, 250]
ratio_of_defeats_list = [1, 1.5, 2]
nr_of_argumentation_frameworks = 50
ratio_uncertain_list = [0.05, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40]

DATA_SET_FOLDER = pathlib.Path('generated')

for nr_of_arguments in nr_of_arguments_list:
    for ratio_of_defeats in ratio_of_defeats_list:
        nr_of_defeats = int(nr_of_arguments * ratio_of_defeats)
        for nr_of_argumentation_framework in range(
                nr_of_argumentation_frameworks):
            for ratio_uncertain in ratio_uncertain_list:
                file_name = f'IAF_{str(nr_of_arguments)}_' \
                            f'{str(nr_of_defeats)}_' \
                            f'{str(int(ratio_uncertain * 100))}_' \
                            'args_atts_' \
                            f'{str(nr_of_argumentation_framework)}.pl'
                with open(DATA_SET_FOLDER / file_name, 'w') as write_file:
                    # First certain arguments are topics
                    write_file.write(f'topic(a0).\nargument(a0).\n')
                    write_file.write(f'topic(a1).\nargument(a1).\n')
                    write_file.write(f'topic(a2).\nargument(a2).\n')
                    write_file.write(f'topic(a3).\nargument(a3).\n')
                    write_file.write(f'topic(a4).\nargument(a4).\n')

                    # For the remaining arguments, we partition into certain
                    # and uncertain.
                    nr_uncertain_arguments = \
                        int(ratio_uncertain * nr_of_arguments)
                    shuffle_arguments = \
                        random.sample(range(5, nr_of_arguments),
                                      (nr_of_arguments - 5))
                    for argument_index in \
                            shuffle_arguments[:nr_uncertain_arguments]:
                        write_file.write(f'uarg(a{str(argument_index)}).\n')
                    for argument_index in \
                            shuffle_arguments[nr_uncertain_arguments:]:
                        write_file.write(f'argument('
                                         f'a{str(argument_index)}).\n')

                    # Get all (certain or uncertain) defeats
                    defeats = []
                    while len(defeats) < nr_of_defeats:
                        defeat = random.choices(range(nr_of_arguments), k=2)
                        if defeat not in defeats:
                            defeats.append(defeat)
                    # Partition between certain and uncertain
                    nr_of_uncertain_defeats = \
                        int(ratio_uncertain * nr_of_defeats)
                    shuffle_defeats = random.sample(range(
                        nr_of_defeats), nr_of_defeats)
                    for defeat_i in shuffle_defeats[:nr_of_uncertain_defeats]:
                        write_file.write(f'uatt(a{str(defeats[defeat_i][0])},'
                                         f'a{str(defeats[defeat_i][1])}).\n')
                    for defeat_i in shuffle_defeats[nr_of_uncertain_defeats:]:
                        write_file.write(f'att(a{str(defeats[defeat_i][0])},'
                                         f'a{str(defeats[defeat_i][1])}).\n')