"""Solve OCT using GLPK."""


# Imports
from itertools import chain
from src.ilp.solution import Solution
import re
import subprocess


def _formulate_as_oct(G):
    """Formulate an OCT ILP given a graph G.

    Parameters
    ----------
    G : Networkx Graph
        Graph to formulate the OCT ILP from.

    Returns
    -------
    string
        ILP in CPLEX LP format.
    """

    # Output lines
    lines = []

    # Formulate objective
    lines.append('Minimize {}'.format(
        ' + '.join(['c{}'.format(n) for n in G.nodes()])
    ))

    # Formulate constraints
    lines.append('Subject To')
    lines += chain.from_iterable(
        (
            '    s{} + s{} + c{} + c{} >= 1'.format(e[0], e[1], e[0], e[1]),
            '    s{} + s{} - c{} - c{} <= 1'.format(e[0], e[1], e[0], e[1])
        )
        for e in G.edges()
    )

    # Formulate binary variables
    lines.append('Binary')
    lines += chain.from_iterable(
        ('    c{}'.format(n), '    s{}'.format(n))
        for n in G.nodes()
    )

    # End problem
    lines.append('End\n')

    # Return string containing all lines
    return '\n'.join(lines)


def _formulate_as_vc(G):
    """Formulate a Vertex Cover ILP given a graph G.

    Parameters
    ----------
    G : Networkx Graph
        Graph to formulate the VC ILP from.

    Returns
    -------
    string
        ILP in CPLEX LP format.
    """

    # Problem lines
    lines = []

    # Set objective
    lines.append('Minimize {}'.format(
        ' + '.join(['c{}'.format(n) for n in G.nodes()])
    ))

    # Set constraints
    lines.append('Subject To')
    lines += (
        '    c{} + c{} >= 1'.format(e[0], e[1])
        for e in G.edges()
    )

    # Set binary variables
    lines.append('Binary')
    lines += ('    c{}'.format(n) for n in G.nodes())

    # End Problem
    lines.append('End\n')

    # Return string containing all lines
    return '\n'.join(lines)


def _solution_from_output(output, graph, mipgap):
    """Construct a solution object from output.

    Parameters
    ----------
    output : string
        Output retrieved from glpsol.
    graph : Networkx Graph
        Graph problem was solved on.
    mipgap : float
        Allowed tolerance.
    timelimit : float
        Time limit for computation, in seconds.

    Returns
    -------
    Solution
        Solution object.
    """

    # Parse time from output
    time = float(re.findall(r'\nTime used: +(\d+\.\d+)', output)[-1])

    # Extract certificate text table
    certificate_text = re.search(
        r'\n\n +No\. +Column name[^\n]*\n[^\n]*\n(.*)(?=\n\nInteger)',
        output,
        re.DOTALL
    ).group(1)

    # Parse as table
    certificate_table = [line.split() for line in certificate_text.split('\n')]

    # Build certificate
    certificate = [
        vertex[1][1:]
        for vertex in certificate_table
        if vertex[1][0] == 'c' and vertex[3] == '1'
    ]

    # Construct solution
    return Solution(
        G=graph,
        threads=1,
        mipgap=mipgap,
        certificate=certificate,
        time=time,
        cuts=[('NA', 'NA')]
    )


def solve_with_glpk(G, formulation='OCT', mipgap=0,
                    timelimit=None, memlimit=None):
    """Solve an ILP problem instance with GLPK.

    Parameters
    ----------
    G : Networkx Graph
        Graph for which the problem will be computed
    formulation : string
        How the problem should be solved. Either OCT or VC.
    mipgap : float
        Allowed gap in tolerance
    timelimit : float
        Time limit for computation, in seconds.
    memlimit : int
        Memory limit in Mb.
    """

    # Typecast mipgap for safety
    mipgap = float(mipgap)
    if timelimit is not None:
        timelimit = float(timelimit)
    if memlimit is not None:
        memlimit = int(memlimit)

    # Get problem formulation
    if formulation == 'OCT':
        problem = _formulate_as_oct(G)
    elif formulation == 'VC':
        problem = _formulate_as_vc(G)
    else:
        raise Exception('Unknown Formulation')

    # Construct GLPK command
    command = [
        'glpsol', '--lp', '-o', '/dev/stdout',
        '--mipgap', str(mipgap)
    ]
    if timelimit is not None:
        command += ['--tmlim', str(int(timelimit))]
    if memlimit is not None:
        command += ['--memlim', str(memlimit)]
    command.append('/dev/stdin')

    # Call GLPK through `glpsol`
    # Read input from /dev/stdin and report to /dev/stdout
    glpsol = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Pass problem over stdin, then wait for glpsol to finish and grab output
    stdout, stderr = glpsol.communicate(input=bytes(problem, 'utf-8'))

    # Error on failure
    if glpsol.returncode:
        raise Exception(stdout)

    # Generate and return solution
    return _solution_from_output(
        stdout.decode('utf-8'),
        graph=G,
        mipgap=mipgap
    )
