#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests of the arrayviewer
"""
import os
from configparser import ConfigParser

import pytest
from pytestqt.plugin import QtBot
from unittest.mock import patch, Mock, MagicMock
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt, QTimer

from ArrayViewer import Viewer, Data
import numpy as np
import h5py


def test_load_data(window_files, qtbot, filepath='testData/'):
    """ Test loading of data """
    datatree = window_files['window'].datatree.Tree
    for fname in window_files['filenames']:
        splitted = os.path.split(fname)
        key = f"{os.path.split(splitted[0])[1]} - {splitted[1]}"
        assert datatree.findItems(key, Qt.MatchContains, 1)

    # Load one file a second time
    with patch.object(Viewer, 'QMessageBox', yesbox):
        with qtbot.waitSignal(window_files['window'].loader.doneLoading, timeout=10000):
            window_files['window'].load_files([window_files['filenames'][0]])


# def test_main():
#     """ Test Viewer main function (just to be sure) """
#     from ArrayViewer import Viewer
#     with patch.object(Viewer, "__name__", "__main__"):
#         with patch.object(Viewer.sys, 'argv', ['testData/W2.mat']):
#             with patch.object(Viewer.sys, 'exit') as mock_exit:
#                 Viewer.init()
#                 assert mock_exit.call_args[0][0] == 42


def test_basic_functions(window_files, qtbot):
    window = window_files['window']
    tree = window.datatree.Tree
    item = tree.topLevelItem(0)
    item.setExpanded(True)
    assert not item.child(0).isHidden()
    tree.setCurrentIndex(tree.indexFromItem(item.child(0)))
    window.Transp.setCheckState(2)
    window.Transp.setCheckState(0)


@pytest.fixture(scope="session")
def data_path(tmp_path_factory):
    folder = tmp_path_factory.mktemp("test_data")
    p = os.path.join(folder, "test.npy")
    np.save(p, np.random.rand(1, 3, 4))
    yield folder


@pytest.fixture(scope="session")
def main_window():
    """Main Window"""
    app = QApplication([])
    config = ConfigParser()
    config.add_section('opt')
    config.set('opt', 'first_to_last', 'False')
    config.set('opt', 'darkmode', 'False')

    def mockreturn(v0, v1):
        return 0

    with patch.object(Data.Loader, 'moveToThread', mockreturn):
        window = Viewer.ViewerWindow(app, config)
    yield window


@pytest.fixture(scope="session")
def window_files(main_window, data_path):
    filenames = [os.path.join(data_path, f) for f in os.listdir(data_path)]
    main_window.load_files(filenames)
    yield {'window': main_window, 'filenames': filenames}


class yesbox(QMessageBox):
    def __init__(self, icon, title, text, buttons=QMessageBox.NoButton):
        super().__init__(icon, title, text, buttons)

    def exec_(self):
        print("EXEC")
        return self.Yes

    def clickedButton(self):
        print("clickedBtn")
        return self.Yes

    def addButton(self, btn, role=None):
        if btn is QMessageBox.Yes:
            self.Yes = btn


if __name__ == "__main__":
    pytest.main()
