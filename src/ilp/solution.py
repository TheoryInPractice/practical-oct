"""OCT or VC solution class."""


def vc_to_oct(solution):
    """Convert a VertexCover solution into an OCT solution.

    This is done by undoing the graph doubling done to reduce
    OCT to VC. The certificate is recovered as the vertes
    whose counterparts are both in the VC certificate.

    Parameters
    ----------
    solution : Solution
        Solution object representing a VertexCover solution.

    Returns
    -------
    Solution
        Solution object representing the corresponding OCT solution.
    """

    # Raise exception if there are an odd number of vertices
    if solution.n % 2 != 0:
        raise Exception('Vertices in VC->OCT solution must be even')

    # Copy graph and remove doubled nodes
    graph = solution.g.copy()
    graph.remove_nodes_from(map(str, range(int(solution.n / 2), solution.n)))

    # Construct new certificate
    certificate = [
        n
        for n in graph.nodes()
        if n in solution.certificate
        and str(int(n) + len(graph.nodes())) in solution.certificate
    ]

    # Return new solution
    return Solution(
        G=graph,
        certificate=certificate,
        threads=solution.threads,
        mipgap=solution.mipgap,
        time=solution.time,
        cuts=solution.cuts
    )


class Solution():
    """OCT Solution Class.

    Attributes
    ----------
    n : int
        Number of nodes in the graph.
    m : int
        Number of edges in the graph.
    g : Networkx Graph
        An instance of the original graph.
    threads : int
        Number of threads used to find the solution. Zero indicates
        solver was run in auto mode.
    time : double
        Length of time taken to find the solution.
    certificate : list
        List of nodes in the solution.
    opt : int
        Size of the solution.
    cuts : list
        List of cut tuples made during optimization of the form
        (cut_name, cut_number).
    """

    def __init__(self, *args, **kwargs):
        """Initialize Solution.

        Parameters
        ----------
        G : Networkx Graph
            Graph for solution.
        threads : int
            Number of threads used to find the solution.
        mipgap : float
            MIP relative tolerance on the gap from the best integer objective.
        certificate : list
            List of vertex names in the solution.
        time : float
            Time taken to find solution.
        cuts : list<tuple>
            List of all cuts made.
        """

        # Assign variables
        try:
            self.g = kwargs.pop('G')
            self.n = len(self.g.nodes())
            self.m = len(self.g.edges())
            self.threads = kwargs.pop('threads')
            self.mipgap = kwargs.pop('mipgap')
            self.certificate = kwargs.pop('certificate')
            self.time = kwargs.pop('time')
            self.cuts = kwargs.pop('cuts')
            self.opt = len(self.certificate)
        except KeyError as e:
            raise Exception('Missing required key word argument.') from e

    def __str__(self):
        """Return Solution info as a string."""

        return (
            'n = {}\n'
            'm = {}\n'
            'opt = {}\n'
            'time = {:.3f}\n'
            'threads = {}\n'
            'mipgap = {}\n'
            'certificate = {}\n'
            'cuts = \n{}'
        ).format(
            self.n, self.m, self.opt, self.time, self.threads, self.mipgap,
            ' '.join(map(str, self.certificate)),
            '\n'.join(['  {}: {}'.format(*cut) for cut in self.cuts])
        )
