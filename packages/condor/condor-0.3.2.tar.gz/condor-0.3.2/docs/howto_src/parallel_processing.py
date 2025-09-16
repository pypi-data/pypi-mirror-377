"""
===================
Parallel Processing
===================
"""

# %%
# You should be able to treat models like any other function in terms of
# parallelization. This example shows using the built-in :mod:`multiprocessing` to do
# process-based parallelization of an explicit system.

import multiprocessing

import condor


class Model(condor.ExplicitSystem):
    x = input()
    output.y = -(x**2) + 2 * x + 1


if __name__ == "__main__":
    with multiprocessing.Pool(5) as p:
        models = p.map(Model, [1, 2, 3])

    for model in models:
        print(model.input, model.output)
