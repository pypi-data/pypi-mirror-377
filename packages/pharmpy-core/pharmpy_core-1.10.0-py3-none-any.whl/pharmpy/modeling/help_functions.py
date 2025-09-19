from __future__ import annotations

import warnings

from pharmpy.basic import Expr


def _get_epsilons(model, list_of_eps):
    rvs = model.random_variables

    if list_of_eps is None:
        return rvs.epsilons
    else:
        eps = []
        for eps_str in list_of_eps:
            try:
                eps.append(rvs[eps_str.upper()])
            except KeyError:
                warnings.warn(f'Epsilon "{eps_str}" does not exist')
        return eps


def _get_etas(model, list_of_etas, include_symbols=False, fixed_allowed=False, iov_allowed=False):
    rvs = model.random_variables
    list_of_etas = _format_input_list(list_of_etas)
    all_valid_etas = False

    if list_of_etas is None:
        list_of_etas = rvs.etas.names
        all_valid_etas = True

    etas = []
    for eta_str in list_of_etas:
        try:
            eta = eta_str  # FIXME: upper/lower case sensitive in pharmpy but not in nonmem
            if not fixed_allowed and _has_fixed_params(model, eta):
                if not all_valid_etas:
                    raise ValueError(f'Random variable cannot be set to fixed: {eta}')
                continue
            if not iov_allowed and rvs[eta].level == 'IOV':
                if not all_valid_etas:
                    raise ValueError(f'Random variable cannot be IOV: {eta}')
                continue
            if eta not in etas:
                etas.append(eta)
        except KeyError:
            if include_symbols:
                etas_symbs = _get_eta_symbs(eta_str, rvs, model.statements)
                etas += [eta for eta in etas_symbs if eta not in etas]
                continue
            raise KeyError(f'Random variable does not exist: {eta_str}')
    return etas


def _get_eta_symbs(eta_str, rvs, sset):
    expr = sset.before_odes.full_expression(eta_str)
    if expr == Expr(eta_str):
        ass = sset.find_assignment(eta_str)
        if ass is not None:
            expr = ass.expression
        else:
            raise KeyError(f'Symbol "{eta_str}" does not exist')
    exp_symbs = expr.free_symbols
    # try:
    #    exp_symbs = sset.before_odes.full_expression(eta_str).free_symbols
    # except AttributeError:
    #    raise KeyError(f'Symbol "{eta_str}" does not exist')
    return [str(e) for e in exp_symbs.intersection(rvs.etas.free_symbols)]


def _has_fixed_params(model, rv):
    param_names = model.random_variables[rv].parameter_names

    for p in model.parameters:
        if p.name in param_names and p.fix:
            return True
    return False


def _format_input_list(list_of_names):
    if list_of_names and isinstance(list_of_names, str):
        list_of_names = [list_of_names]
    return list_of_names


def _format_options(list_of_options, no_of_variables):
    options = []
    for option in list_of_options:
        if isinstance(option, str) or not option:
            option = [option]
        if isinstance(option, list) and len(option) == 1:
            option *= no_of_variables
        options.append(option)

    return options


def _as_integer(n):
    if isinstance(n, int):
        return n
    elif isinstance(n, float):
        if int(n) == n:
            return int(n)
    raise TypeError
