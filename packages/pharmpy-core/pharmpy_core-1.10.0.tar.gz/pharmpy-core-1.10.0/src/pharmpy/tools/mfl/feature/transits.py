from functools import partial
from itertools import product
from typing import Iterable

from pharmpy.model import Model
from pharmpy.modeling import set_n_transit_compartments, set_transit_compartments

from ..statement.feature.symbols import Wildcard
from ..statement.feature.transits import TRANSITS_DEPOT_WILDCARD, Transits
from ..statement.statement import Statement
from .feature import Feature


def features(model: Model, statements: Iterable[Statement]) -> Iterable[Feature]:
    for statement in statements:
        if isinstance(statement, Transits):
            depots = (
                TRANSITS_DEPOT_WILDCARD
                if isinstance(statement.depot, Wildcard)
                else statement.depot
            )
            for count, depot in product(statement.counts, depots):
                if count == "N":
                    yield ('TRANSITS', count, depot.name), set_n_transit_compartments
                elif depot.name == 'DEPOT':
                    yield ('TRANSITS', count, depot.name), partial(
                        set_transit_compartments, n=count
                    )
                elif depot.name == 'NODEPOT':
                    yield ('TRANSITS', count, depot.name), partial(
                        set_transit_compartments, n=count + 1, keep_depot=False
                    )
                else:
                    raise ValueError(f'Transit depot {depot} not supported')
