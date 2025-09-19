import shutil
import tempfile
from pathlib import Path

import pytest

from pharmpy.internals.fs.cwd import chdir
from pharmpy.model import Model
from pharmpy.tools import fit


@pytest.fixture(scope='session')
def start_modelres(testdata):
    model_start, modelfit_results = _run_est(testdata, 'nonmem')
    return model_start, modelfit_results


@pytest.fixture(scope='session')
def start_modelres_dummy(testdata):
    model_start, modelfit_results = _run_est(testdata, 'dummy')
    return model_start, modelfit_results


def _run_est(testdata, esttool):
    tempdir = Path(tempfile.mkdtemp())
    with chdir(tempdir):
        shutil.copy2(testdata / 'nonmem' / 'models' / 'mox2.mod', tempdir)
        shutil.copy2(testdata / 'nonmem' / 'models' / 'mox_simulated_normal.csv', tempdir)
        model_start = Model.parse_model('mox2.mod')
        model_start = model_start.replace(
            datainfo=model_start.datainfo.replace(path=tempdir / 'mox_simulated_normal.csv')
        )
        modelfit_results = fit(model_start, esttool=esttool)
    return model_start, modelfit_results


@pytest.fixture(scope='session')
def model_count():
    def _model_count(rundir: Path):
        return sum(
            map(
                lambda path: 0 if path.name in ['.lock', '.datasets', 'input_model'] else 1,
                ((rundir / 'models').iterdir()),
            )
        )

    return _model_count
