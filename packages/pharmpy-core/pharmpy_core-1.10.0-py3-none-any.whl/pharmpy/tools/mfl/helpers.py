from collections import defaultdict
from itertools import chain, product
from typing import Callable, Iterable

from pharmpy.model import Model

from .feature.absorption import features as absorption_features
from .feature.allometry import features as allometry_features
from .feature.covariate import features as covariate_features
from .feature.direct_effect import features as direct_effect_features
from .feature.effect_comp import features as effect_comp_features
from .feature.elimination import features as elimination_features
from .feature.feature import Feature, FeatureFn, FeatureKey
from .feature.indirect_effect import features as indirect_effect_features
from .feature.lagtime import features as lagtime_features
from .feature.metabolite import features as metabolite_features
from .feature.peripherals import features as peripherals_features
from .feature.transits import features as transits_features
from .statement.statement import Statement

FeatureGenerator = Callable[[Model, Iterable[Statement]], Iterable[Feature]]

modelsearch_features = (
    absorption_features,
    elimination_features,
    transits_features,
    peripherals_features,
    lagtime_features,
)
structsearch_pd_features = (direct_effect_features, effect_comp_features, indirect_effect_features)
structsearch_metabolite_features = (metabolite_features, peripherals_features)


def all_funcs(model: Model, statements: Iterable[Statement]):
    return funcs(
        model,
        statements,
        (
            *modelsearch_features,
            covariate_features,
            allometry_features,
            *structsearch_pd_features,
            *structsearch_metabolite_features,
        ),
    )


def funcs(
    model: Model, statements: Iterable[Statement], generators: Iterable[FeatureGenerator]
) -> dict[FeatureKey, FeatureFn]:
    statements_list = list(statements)  # TODO: Only read statements once

    features = chain.from_iterable(
        map(
            lambda features: features(model, statements_list),
            generators,
        )
    )

    return dict(features)


def _group_incompatible_features(funcs):
    grouped = defaultdict(list)
    for key in funcs.keys():
        grouped[key[0]].append(key)
    return grouped.values()


def all_combinations(fns: dict[FeatureKey, FeatureFn]) -> Iterable[tuple[FeatureKey]]:
    grouped = _group_incompatible_features(fns)
    feats = ((None, *group) for group in grouped)
    for t in product(*feats):
        a = tuple(elt for elt in t if elt is not None)
        if a:
            yield a


def key_to_str(key: FeatureKey) -> str:
    name, *args = key
    return f'{name}({", ".join(map(str, args))})'


def get_funcs_same_type(funcs, feat):
    return [value for key, value in funcs.items() if key[0] == feat[0]]
