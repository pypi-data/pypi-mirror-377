import pytest
import numpy as np
from PyQt5.QtCore import Qt, QObject, QModelIndex, QAbstractTableModel
from ArrayViewer.Editor import dataModel

@pytest.fixture
def sample_data():
    """Fixture to provide sample data for the tests."""
    return np.array([[1, 2], [3, 4], [5, 6]])

@pytest.fixture
def model(sample_data):
    """Fixture to initialize the dataModel."""
    return dataModel(sample_data)

def test_row_count(model, sample_data):
    """Test that rowCount returns the correct number of rows."""
    assert model.rowCount(None) == sample_data.shape[0]

def test_column_count(model, sample_data):
    """Test that columnCount returns the correct number of columns."""
    assert model.columnCount(None) == sample_data.shape[1]

def test_set_data_valid_index(model):
    """Test that setData updates the model's data at a valid index."""
    index = model.index(0, 0)
    assert model.setData(index, 42)
    assert model._data[0, 0] == 42

def test_set_data_invalid_role(model):
    """Test that setData fails when using an invalid role."""
    index = model.index(0, 0)
    assert not model.setData(index, 42, role=Qt.UserRole)  # Qt.UserRole is not editable
    assert model._data[0, 0] == 1

def test_set_data_invalid_value(model):
    """Test that setData gracefully fails when provided with an invalid value."""
    index = model.index(0, 0)
    assert not model.setData(index, "invalid")
    assert model._data[0, 0] == 1

def test_data_for_display_role(model):
    """Test that data returns the correct value for the DisplayRole."""
    index = model.index(0, 0)
    assert model.data(index, role=Qt.DisplayRole).toString() == "1"

def test_data_for_edit_role(model):
    """Test that data returns the correct value for the EditRole."""
    index = model.index(0, 0)
    assert model.data(index, role=Qt.EditRole).toString() == "1"

def test_set_full_data(model):
    """Test that set_full_data properly resets the model's data."""
    new_data = [[7, 8], [9, 10]]
    changes = {(0, 0): 99, (1, 1): 100}
    model.set_full_data(new_data, changes)
    assert model._data[0, 0] == 99
    assert model._data[1, 1] == 100

def test_flags(model):
    """Test that flags return the correct flags for valid and invalid indices."""
    index = QModelIndex()
    assert model.flags(index) == Qt.ItemIsEnabled

    valid_index = model.index(0, 0)
    assert model.flags(valid_index) == (Qt.ItemIsEnabled | Qt.ItemIsEditable)
