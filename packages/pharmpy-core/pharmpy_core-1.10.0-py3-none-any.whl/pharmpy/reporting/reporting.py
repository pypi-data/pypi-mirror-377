import os
import re
import shutil
import ssl
import warnings
from pathlib import Path
from urllib.request import URLError, urlopen

from bs4 import BeautifulSoup
from csscompressor import compress
from sphinx.application import Sphinx

from pharmpy.internals.fs.cwd import chdir
from pharmpy.internals.fs.tmp import TemporaryDirectory


# This spoofer is needed to trick jupyter_client to turn off stdout and stderr
# These can cause problems when running from rstudio on Windows
# Does nothing on platforms other than Windows
class SpoofExecutable:
    def __enter__(self):
        if os.name == 'nt' and self._check_rstudio():
            import sys

            self.executable = sys.executable
            sys.executable = 'pythonw.exe'

    def __exit__(self, exc_type, exc_value, traceback):
        if os.name == 'nt' and self._check_rstudio():
            import sys

            sys.executable = self.executable

    def _check_rstudio(self):
        # rstudio is setting the environment variable RSTUDIO in the running process
        # This gets inherited by child processes
        rstudio = os.environ.get("RSTUDIO", None)
        return rstudio == "1"


def generate_report(rst_path, results_path, target_path):
    """Generate report from rst and results json"""
    results_path = Path(results_path)
    with TemporaryDirectory() as tmpdirname:
        tmp_path = Path(tmpdirname)
        source_path = tmp_path / 'source'
        source_path.mkdir()
        shutil.copy(rst_path, source_path / 'results.rst')
        # FIXME: Crude templating for now. Could move to separate directory
        shutil.copy(rst_path.parent.parent / 'amd' / 'common.rst', source_path / 'common.txt')
        if results_path.is_dir():
            results_path /= 'results.json'
        shutil.copy(results_path, source_path)

        conf_path = Path(__file__).resolve().parent

        # Change directory for results.json to be found
        with chdir(source_path):
            with open(os.devnull, 'w') as devnull:
                with warnings.catch_warnings():
                    # Don't display deprecation warnings.
                    # See https://github.com/pharmpy/pharmpy/issues/20
                    warnings.filterwarnings("ignore", message="The app.add_stylesheet")
                    warnings.filterwarnings("ignore", message="The app.add_javascript")
                    # Deprecation warning in jupyter_sphinx
                    warnings.filterwarnings("ignore", message="Passing a schema to Validator")
                    # Deprecation warning in python 3.10
                    warnings.filterwarnings(
                        "ignore",
                        message="The distutils package is deprecated and slated for removal in "
                        "Python 3.12. Use setuptools or check PEP 632 for potential alternatives",
                    )
                    warnings.filterwarnings("ignore", "There is no current event loop")
                    # From jupyter-core 5.1.2
                    warnings.filterwarnings(
                        "ignore", "Jupyter is migrating its paths to use standard platformdirs"
                    )
                    warnings.filterwarnings(
                        "ignore", "The alias 'sphinx.util.progress_message' is deprecated"
                    )
                    warnings.filterwarnings(
                        "ignore", "nodes.Node.traverse\\(\\) is obsoleted by Node.findall\\(\\)."
                    )
                    # From Python 3.11
                    warnings.filterwarnings(
                        "ignore", "'imghdr' is deprecated and slated for removal in Python 3.13"
                    )
                    warnings.filterwarnings(
                        "ignore",
                        "zmq.eventloop.ioloop is deprecated in pyzmq 17.",
                    )
                    # From Python 3.13 and nbclient
                    warnings.filterwarnings(
                        "ignore",
                        "Parsing dates involving a day of month without",
                    )

                    with SpoofExecutable():
                        app = Sphinx(
                            str(source_path),
                            str(conf_path),
                            str(tmp_path),
                            str(tmp_path),
                            "singlehtml",
                            status=devnull,
                            warning=devnull,
                        )
                        app.build()

        # Write missing altair css
        with open(tmp_path / '_static' / 'altair-plot.css', 'w') as dh:
            dh.write(
                """.vega-actions a {
    margin-right: 12px;
    color: #757575;
    font-weight: normal;
    font-size: 13px;
}

.vega-embed {
    margin-bottom: 20px;
    margin-top: 20px;
    width: 100%;
}
"""
            )
        report_path = tmp_path / 'results.html'
        embed_css_and_js(tmp_path / 'results.html', report_path)
        shutil.copy(report_path, target_path)


def embed_css_and_js(html, target):
    """Embed all external css and javascript into an html"""
    with open(html, 'r', encoding='utf-8') as sh:
        with warnings.catch_warnings():
            # Don't display deprecation warnings.
            # Deprecation warning with lxml 5.3.0
            warnings.filterwarnings(
                "ignore",
                message=r"The 'strip_cdata' option of HTMLParser\(\) has never done anything",
            )

            soup = BeautifulSoup(sh, features='lxml')

    scripts = soup.find_all("script", attrs={"src": True})

    for script in scripts:
        source = script.attrs['src']
        # Remove versioning of scripts that was added by Sphinx 8.1
        source = re.sub(r'\?v=.*', '', source)
        if source.startswith('http'):
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE  # To avoid CERTIFICATE_VERIFY_FAILED
            try:
                with urlopen(source, context=ctx) as infile:
                    content = infile.read().decode('utf-8')
            except URLError:
                # Skip file if it cannot be found or if network is down
                continue
        else:
            path = html.parent / source
            if path.name == 'thebelab-helper.js':  # This file wasn't created
                continue
            with open(path, 'r') as sh:
                content = sh.read()

        # Minification with jsmin didn't work
        tag = soup.new_tag('script')
        tag['type'] = 'text/javascript'
        tag.append(content)
        script.replace_with(tag)

    stylesheets = soup.find_all("link", attrs={"rel": "stylesheet"})

    for stylesheet in stylesheets:
        stylesheet_src = stylesheet.attrs['href']
        # Remove versioning of css files that was added by Sphinx 8.1
        stylesheet_src = re.sub(r'\?v=.*', '', stylesheet_src)
        if stylesheet_src.startswith("https"):
            continue
        tag = soup.new_tag("style")
        tag['type'] = 'text/css'
        path = html.parent / stylesheet_src
        if path.name == 'thebelab.css':  # This file wasn't created
            continue
        with open(path, 'r') as sh:
            content = sh.read()
        if '@import' in content:
            import_files = re.findall(r'@import\s+url\("([A-Za-z0-9.]+)"\)', content)
            for name in import_files:
                with open(path.parent / name, 'r') as import_file:
                    import_content = import_file.read()
                content = re.sub(r'@import\s+url\("' + name + r'"\);', import_content, content)
        minified_content = compress(content)
        tag.append(minified_content)
        stylesheet.replace_with(tag)

    with open(target, 'w', encoding='utf-8') as dh:
        dh.write(str(soup))
