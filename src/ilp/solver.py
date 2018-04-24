"""Solve OCT by reducing to an ILP.

This module relies on IBM CPLEX and GLPK. They are not on PyPi
and must be installed independently of `requirements.txt`.
"""


# Imports
from src.ilp.cplex.solver import solve_with_cplex
from src.ilp.glpk.solver import solve_with_glpk
from src.ilp.solution import vc_to_oct
from src.ilp.solution import Solution
import getopt
import networkx as nx
import os
import sys


# Constants
FORMULATIONS = ('OCT', 'VC')
SOLVERS = ('GLPK', 'CPLEX')
FORMULATION = '--formulation'
MIPGAP = '--mipgap'
SOLVER = '--solver'
THREADS = '--threads'
TIMELIMIT = '--timelimit'
MEMLIMIT = '--memlimit'
CONVERT_TO_OCT = '--convert-to-oct'
USAGE = (
    'Usage: python -m src.ilp.solver '
    '[--formulation=] [--mipgap=] [--solver=] '
    '[--threads=] [--timelimit=] [--memlimit=] '
    '[--convert-to-oct=] <edgelist-file>'
)


def read_edgelist(filename):
    """Read edgelist.

    Parameters
    ----------
    filename : string
        Edgelist filename

    Returns
    -------
    Networkx Graph
        Networkx Graph formed from input file
    """

    # Split file extension
    name, extension = os.path.splitext(filename)

    # Read file
    if extension == '.edgelist':
        with open(filename, 'r') as edgelist:
            lines = edgelist.readlines()
        G = nx.parse_edgelist(lines[1:])
    else:
        G = nx.read_edgelist(filename)

    return G


def solve(G, formulation='OCT', mipgap=0, solver='GLPK',
          threads=1, timelimit=None, memlimit=None,
          convert_to_oct=False):
    """Solve an ILP problem instance with CPLEX or GLPK.

    Parameters
    ----------
    G : Networkx Graph
        Graph for which OCT will be computed
    formulation : string
        How problem should be solved. Either OCT or VC.
    mipgap : float
        Allowed gap in tolerance
    solver : string
        Solver used to compute solution. Either GLPK or CPLEX.
    threads : int
        Number of threads to use.
    timelimit : float
        Time limit for computation, in seconds.
    memlimit : int
        Memory limit in Mb.
    convert_to_oct : bool
        If True and formulation=VC, the solution will be converted
        to an OCT solution before returning.
    """

    # Solve
    if not G.nodes():
        return Solution(
            G=G,
            threads=threads,
            mipgap=mipgap,
            certificate=[],
            time=0,
            cuts=[]
        )
    elif solver == 'GLPK':
        solution = solve_with_glpk(
            G,
            formulation=formulation,
            mipgap=mipgap,
            timelimit=timelimit,
            memlimit=memlimit
        )
    elif solver == 'CPLEX':
        solution = solve_with_cplex(
            G,
            formulation=formulation,
            mipgap=mipgap,
            threads=threads,
            timelimit=timelimit,
            memlimit=memlimit
        )
    else:
        raise Exception('Unknown Solver')

    # Return
    if formulation == 'VC' and convert_to_oct:
        return vc_to_oct(solution)
    else:
        return solution


def main():
    """Parse call, solve, and report solution."""

    # Default options
    opts_dict = {
        FORMULATION: 'OCT',
        MIPGAP: '0',
        SOLVER: 'GLPK',
        THREADS: '1',
        TIMELIMIT: None,
        MEMLIMIT: None,
        CONVERT_TO_OCT: False
    }

    # Validate options
    try:

        # Get and parse options
        opts, args = getopt.getopt(sys.argv[1:], None, [
            'formulation=', 'mipgap=', 'solver=',
            'threads=', 'timelimit=', 'memlimit=',
            'convert-to-oct='
        ])

        # Error if input file is not specified
        if not args:
            raise Exception(USAGE)

        # Override options with any specified
        for opt in opts:
            opts_dict[opt[0]] = opt[1]

        # Cast datatypes
        opts_dict[MIPGAP] = float(opts_dict[MIPGAP])
        opts_dict[THREADS] = int(opts_dict[THREADS])
        if opts_dict[TIMELIMIT] is not None:
            opts_dict[TIMELIMIT] = float(opts_dict[TIMELIMIT])
        if opts_dict[MEMLIMIT] is not None:
            opts_dict[MEMLIMIT] = int(opts_dict[MEMLIMIT])
        if opts_dict[CONVERT_TO_OCT] == 'True':
            opts_dict[CONVERT_TO_OCT] = True

        # Validate enumeration options
        if (opts_dict[FORMULATION] not in FORMULATIONS or
                opts_dict[SOLVER] not in SOLVERS):
            raise Exception(USAGE)

    except getopt.GetoptError:

        # Except if unable to parse
        raise Exception(USAGE)

    # Get filename and extension
    filename = os.path.abspath(args[0])

    # Get graph
    G = read_edgelist(filename)

    # Find and print solution
    print(solve(
        G,
        formulation=opts_dict[FORMULATION],
        mipgap=opts_dict[MIPGAP],
        solver=opts_dict[SOLVER],
        threads=opts_dict[THREADS],
        timelimit=opts_dict[TIMELIMIT],
        memlimit=opts_dict[MEMLIMIT],
        convert_to_oct=opts_dict[CONVERT_TO_OCT]
    ))


if __name__ == '__main__':
    main()
