#pylint: disable=no-name-in-module
from PyQt5.QtCore import QUrl
#pylint: enable=no-name-in-module

def sanitise_filename(maybe_qurl_filename):
    return (
        QUrl(maybe_qurl_filename).toLocalFile() if 'file://' in maybe_qurl_filename
        else maybe_qurl_filename
    )
