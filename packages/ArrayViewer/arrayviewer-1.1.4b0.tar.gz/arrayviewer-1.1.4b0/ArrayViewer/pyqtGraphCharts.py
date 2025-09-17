"""
GraphWidget and ReshapeDialog for the ArrayViewer
"""
# Author: Alex Schwarz <alex.schwarz@informatik.tu-chemnitz.de>
import re
from itertools import combinations
from contextlib import suppress
from PyQt5.QtWidgets import (QCompleter, QDialog, QGridLayout, QLabel,
                             QLineEdit, QTextEdit, QVBoxLayout, QWidget)
from PyQt5.QtWidgets import QDialogButtonBox as DBB
from PyQt5 import QtCore
import pyqtgraph as pg
import numpy as np
from h5py._hl.dataset import Dataset


def _flat_with_padding(Array, padding=1, fill=np.nan):
    """ Flatten ND array into a 2D array and add a padding with given fill """
    # Reshape the array to 3D
    Arr = np.reshape(Array, Array.shape[:2] + (-1, ))
    rows = _rows_from_dim(Array.shape)
    # Add the padding to the right and bottom of the arrays
    A0 = np.ones([padding, Arr.shape[1], Arr.shape[2]]) * fill
    A1 = np.ones([Arr.shape[0] + padding, padding, Arr.shape[2]]) * fill
    pArr = np.append(np.append(Arr, A0, axis=0), A1, axis=1)
    # Stack the arrays according to the precalculated number of rows
    pA2D = np.hstack(np.split(np.hstack(pArr.T).T, rows)).T
    # Add the padding to the left and top of the arrays
    A0 = np.ones([padding, pA2D.shape[1]]) * fill
    A1 = np.ones([pA2D.shape[0] + padding, padding]) * fill
    pA2D = np.append(A1, np.append(A0, pA2D, axis=0), axis=1)
    return pA2D


def _rows_from_dim(dim):
    """ Returns a reasonable row count for the given dimensionality """
    if (len(dim) == 4 and .18 < 1.0 * dim[2] / dim[3] < 5.5):
        # If the Array is 4D and has reasonable ratio, keep that ratio.
        rows = dim[2]
    else:
        # Get the most equal division of the last dimension
        last_dim = np.prod(dim[2:])
        for n in range(int(np.sqrt(last_dim)), last_dim + 1):
            if last_dim%n == 0:
                rows = last_dim // n
                break
    return rows


def _unravel_flat_with_padding(ind, sh, pad=1):
    """ Unravel a clicked index onto its corresponding n-D-index """
    ind = [i - pad if i > pad else 0 for i in ind]
    cols = np.prod(sh[2:]) // _rows_from_dim(sh)
    box_index = [ind[0] // (sh[0] + pad), ind[1] // (sh[1] + pad)]
    ind.extend(np.unravel_index(box_index[1] * cols + box_index[0], sh[2:]))
    ind[0] = ind[0] % (sh[0] + pad)
    ind[1] = ind[1] % (sh[1] + pad)
    return ind


def _get_shape_from_str(string):
    """
    Returns an array with the elements of the string. All brackets are
    removed as well as empty elements in the array.
    """
    return np.array([_f for _f in string.strip("()[]").split(",") if _f],
                    dtype=int)


def _setlocator(axis, lim, nPad=None):
    """ Set the locator of an axis with the given limits and set the ticks """
    if isinstance(lim, list):
        loc = axis.get_major_locator()()
        axis.set_major_locator(FixedLocator(loc))
        d = (np.arange(len(loc)) - 1) * (loc[2] - loc[1]) * lim[2] + lim[0]
    elif isinstance(lim, tuple):
        loc = np.arange(-lim[0] - nPad, lim[-1], lim[0] + nPad)
        axis.set_major_locator(FixedLocator(loc))
        d = loc - (np.arange(0, len(loc)) * nPad - nPad)
    else:
        axis.set_major_locator(FixedLocator(np.arange(len(lim))))
        d = lim

    if all(d.astype(int) == d.astype(float)):
        axis.set_ticklabels(d.astype(int))
    else:
        d = np.vectorize(reformat)(d)
        axis.set_ticklabels(d.astype(float))


def reformat(dat):
    """ Format the numberstrings correctly. """
    if dat is None or isinstance(dat, np.ma.core.MaskedConstant):
        return ""
    if not 1e-5 < np.abs(dat) < 1e5:
        return f"{dat:.5e}"
    return f"{dat:.5f}"


def _suggestion(previous_val, value):
    """ Returns all possible factors """
    pfactors = []
    divisor = 2
    while value > 1:
        while value % divisor == 0:
            pfactors.append(divisor)
            value /= divisor
        divisor += 1
        if divisor * divisor > value:
            if value > 1:
                pfactors.append(value)
            break
    factors = []
    for n in range(1, len(pfactors) + 1):
        for x in combinations(pfactors, n):
            y = 1
            for a in x:
                y = y * a
            factors.append(int(y))
    factors = list(set(factors))
    factors.sort(reverse=True)
    return [previous_val + f"{i}," for i in factors]


class GraphWidget(QWidget):
    """ Draws the data graph. """
    def __init__(self, parent=None):
        """ Initialize the figure. """
        super().__init__(parent)

        # Setup the canvas, figure and axes
        self._axes = pg.PlotWidget(background='w')
        self._ui = parent
        self.noPrintTypes = parent.noPrintTypes
        self._clim = (0, 1)
        self._fix_limits = [None, None]
        self._img = None
        self._cb = None
        self.has_cb = False
        self.has_operation = False
        self._colormap = pg.colormap.get('viridis')
        self._opr = (lambda x: x)
        self._oprdim = np.array([], dtype=int)
        self._oprcorr = None
        self.cutout = np.array([])
        self.ticks = [[0, -1, 1]]
        self._tick_str = [0, 0]

        # Add a cursor
        # self._cursor = Cursor(self._axes, color='red', linewidth=1)
        # if self._ui.config.getboolean('opt', 'cursor', fallback=False):
            # self._cursor.visible = False
        self.last_clicked = (None, None)
        # self.annotation = self._figure.text(0.3, 0.95, "0, 0", visible=False)
        self._axes.scene().sigMouseClicked.connect(self.onclick)

        # Animation
        self._anim_timer = QtCore.QTimer()
        self._anim_timer.setInterval(parent.config.getint('opt', 'anim_speed',
                                                          fallback=300))
        self._anim_timer.timeout.connect(self._animate)
        self._anim_step = 0
        self._anim_dim = None
        self._anim_cutout = np.array([])

        # self._canv.draw()

        # Add a label Text that may be changed in later Versions to display the
        # position and value below the mouse pointer
        self._layout = QVBoxLayout(self)
        self._layout.addWidget(self._axes)
        self._txt = QLabel(self)
        self._txt.setText('')
        self._layout.addWidget(self._txt)

    def onclick(self, event):
        """ Handle click events in PyQtGraph """
        # Only react to clicks if not in Animation mode
        if self._anim_dim is not None:
            return

        # Get the click position in data coordinates
        pos = event.pos()
        view_pos = self._axes.plotItem.vb.mapSceneToView(pos)
        x, y = view_pos.x(), view_pos.y()

        # Initialize xyz list for coordinates
        xyz = []

        if isinstance(self._img, pg.PlotDataItem):  # Line plots
            # Find closest point
            data = self._img.getData()
            if data is None:
                return
            xdata, ydata = data
            idx = np.argmin(np.abs(xdata - x))
            xyz = [xdata[idx], ydata[idx]]
            dat = reformat(xyz[1])
            fstr = "x: {xyz[0]}, y: {dat}"

        elif isinstance(self._img, pg.ImageItem):  # Image plots
            xyz.append(int(np.round(x)))
            xyz.append(int(np.round(y)))
            try:
                dat = reformat(self._img.image[xyz[1], xyz[0]])
                fstr = "x: {xyz[0]}, y: {xyz[1]}, z: {dat}"
            except IndexError:
                return

        elif isinstance(self._img, pg.ScatterPlotItem):  # Scatter plots
            # Find closest point
            points = self._img.scatter.points()
            if not points:
                return
            pos_arr = np.array([(p.pos().x(), p.pos().y()) for p in points])
            dist = np.sum((pos_arr - np.array([x, y]))**2, axis=1)
            idx = np.argmin(dist)
            xyz.append(x)
            xyz.append(y)
            dat = [reformat(v) for v in self.cutout[idx]]
            fstr = str([float(d) for d in dat])[1:-2]

        # Adjust x and y value for reshaped data
        if len(self.ticks) > 2:
            xyz = _unravel_flat_with_padding(xyz, self.cutout.shape)
            fstr = "index: {xyz}, value: {dat}"

        # Replace index for picked values
        for i, tick in enumerate(self.ticks):
            if isinstance(tick, list):
                xyz[i] = tick[2] * xyz[i] + tick[0]
            else:
                with suppress(IndexError):
                    xyz[i] = tick[xyz[i]]

        # Handle modifier keys
        modifiers = event.modifiers()
        if modifiers & QtCore.Qt.ShiftModifier:
            self._ui.Shape.set_non_scalar_values(xyz)
        elif modifiers & QtCore.Qt.ControlModifier:
            self._ui.Shape.set_non_scalar_values(['', ''] + xyz[2:])
        elif modifiers & QtCore.Qt.AltModifier:
            self.spawn_micro_plot(xyz)
        else:
            # Update annotation text
            if xyz == self.last_clicked:
                if hasattr(self, 'text_item'):
                    self._axes.removeItem(self.text_item)
                self.last_clicked = (None, None)
            else:
                # Create or update text annotation
                if hasattr(self, 'text_item'):
                    self._axes.removeItem(self.text_item)
                self.text_item = pg.TextItem(
                    text=fstr.format(xyz=xyz, dat=dat),
                    color='k',
                    anchor=(0.5, 1.0)
                )
                self._axes.addItem(self.text_item)
                self.text_item.setPos(self._axes.plotItem.vb.viewRange()[0][1],
                                      self._axes.plotItem.vb.viewRange()[1][1])
                self.last_clicked = xyz

    def fix_limit(self, idx):
        """ Fix the current value of the minimum(idx 0) or maximum(idx 1). """
        if self._fix_limits[idx] is None:
            self._fix_limits[idx] = self._clim[idx]
            return 1
        self._fix_limits[idx] = None
        return 0

    def start_animation(self, dim=None):
        """ Start the animation over the given dimension. """
        if dim in self._tick_str[0]:
            return False
        if dim in self._oprdim:
            # remove from operation dimensions
            self._oprdim = np.setxor1d(self._oprdim, dim)
            data = self._ui.get(0)
            if isinstance(data, np.ndarray):
                self.cutout = data

        self._anim_dim = dim - (self._tick_str[0] < dim).sum()
        self._anim_step = 0
        self._anim_cutout = self.cutout
        self._anim_timer.start()
        self._axes.clear()
        self.plot()
        self._animate()
        return True

    def stop_animation(self):
        """ Stop the animation and set the cutout back to its original form. """
        self._anim_dim = None
        if self._anim_timer.isActive():
            self._anim_timer.stop()
            self.cutout = self._anim_cutout

    def set_anim_speed(self):
        """ Set the timeout time of the animation timer. """
        anim_speed = self._ui.config.getint('opt', 'anim_speed', fallback=300)
        self._anim_timer.setInterval(anim_speed)

    def spawn_micro_plot(self, location):
        """ Show a small window with the timecourse of selected location. """
        key = self._ui._slice_key()
        data = self._ui.get(0)
        if key in self._ui.slices:
            sl = list(int(s) if s.isdigit() else None for s in self._ui.slices[key])
        else:
            sl = [None for _ in data.shape]

        i = 0
        for j, s in enumerate(sl):
            if s is None:
                sl[j] = location[i]
                i += 1
        plot_data = data[(*sl[:-1],)]

        micro_plot = MicroPlot(self, plot_data, sl[:-1], key)
        micro_plot.show()

    def _animate(self):
        """ Perform one animation step. """
        if self._anim_dim >= self._anim_cutout.ndim:
            self.stop_animation()
            return
        self._anim_step = (self._anim_step + 1) % self._anim_cutout.shape[self._anim_dim]
        self.cutout = self._anim_cutout.take(self._anim_step, self._anim_dim)
        self._axes.clear()
        self._axes.set_title(f"Animation on timestep: {self._anim_step}")
        self.plot()
        # self._canv.draw()

    def _n_D_plot(self):
        """ Plot multi-dimensional data. """
        sh = self.cutout.shape
        nPad = sh[0] // 100 + 1
        if self._ui.Plot3D.isChecked() and self.cutout.ndim == 3 and sh[2] in (3, 4):
            nPad = -1
            mm = [np.nanmin(self.cutout), np.nanmax(self.cutout)]
            dat = np.swapaxes((self.cutout - mm[0]) / (mm[1] - mm[0]), 0, 1)
        else:
            dat = _flat_with_padding(self.cutout, nPad)
        if self.cutout.dtype == np.float16:
            dat = dat.astype(np.float32)
        self._img = pg.ImageItem(dat)
        self._img.setColorMap(self._colormap)
        self._set_ticks(self._tick_str[1], len(sh))

    def _two_D_plot(self):
        """ Plot 2-dimensional data. """
        if self._ui.MMM.isChecked():
            self._img = []
            self._img += self._axes.plot(np.nanmax(self.cutout, axis=0),
                                         pen=pg.mkPen('r', width=2), name='Max')
            self._img += self._axes.plot(np.nanmean(self.cutout, axis=0),
                                         pen=pg.mkPen('k', width=2), name='Mean')
            self._img += self._axes.plot(np.nanmin(self.cutout, axis=0),
                                         pen=pg.mkPen('b', width=2), name='Min')
            self._axes.addLegend()
        else:
            dat = self.cutout.T
            if self.cutout.dtype == np.float16:
                dat = dat.astype(np.float32)
            self._img = pg.ImageItem(dat)
            self._axes.addItem(self._img)
            self._img.setColorMap(self._colormap)
        self._set_ticks(self._tick_str[1])

    def _n_D_scatter(self):
        """ Plot up to four rows as a scatter (x, y, size, color)"""
        if self.cutout.shape[1] < 4:
            col = 'b'
        else:
            col = self.cutout[:, 3] - np.nanmin(self.cutout[:, 3])
            col /= np.nanmax(col)
        if self.cutout.shape[1] < 3:
            siz = .25
        else:
            siz = self.cutout[:, 2] - np.nanmin(self.cutout[:, 2])
            siz = 1 + 100 * siz / np.nanmax(siz)
        self._axes.clear()
        scatterItem = pg.ScatterPlotItem(
            x=self.cutout[:, 0],
            y=self.cutout[:, 1],
            size=siz,
            # brush=(pg.mkBrush(color=self._colormap.getColors())),
        )
        self._img = self._axes.addItem(scatterItem)

    def _set_ticks(self, s, transp=True, plotDimensions=2):
        """ Set the ticks of plots according to the selected slices. """
        # Calculate the ticks for the plot by checking the limits
        return
        slices = (slice(n, n+1) if isinstance(n, int) else n for n in s)
        self.ticks = []
        for n in slices:
            if isinstance(n, slice):
                self.ticks.append([n.start or 0, n.stop or -1, n.step or 1])
            else:
                self.ticks.append(np.array(n))
        if transp and self._ui.Transp.isChecked():
            self.ticks[0], self.ticks[1] = self.ticks[1], self.ticks[0]
        if plotDimensions < 3:
            # Set the x-ticks
            xticks = [(i, reformat(val)) for i, val in enumerate(self.ticks[0])]
            self._axes.getAxis('bottom').setTicks([xticks])
        if plotDimensions == 2 and not isinstance(s[1], tuple):
            # Set the y-ticks
            yticks = [(i, reformat(val)) for i, val in enumerate(self.ticks[1])]
            self._axes.getAxis('left').setTicks([yticks])

    def clear(self):
        """ Clear the figure. """
        self._cb = None
        self._axes.clear()

    def colorbar(self, minmax=None):
        """ Add a colorbar to the graph or remove it, if it is existing. """
        if not isinstance(self._img, pg.ImageItem):
            return
        if not self.has_cb:
            if self._cb:
                self._cb = None
        elif self._cb is None:
            self._cb = pg.ColorBarItem(colorMap=self._colormap)
            self._cb.setImageItem(self._img)

    def colormap(self, mapname=None):
        """ Replace colormap with the given one. """
        if mapname:
            self._colormap = pg.colormap.get(mapname, source='matplotlib')
        if not isinstance(self._img, pg.ImageItem):
            return
        self._img.setColorMap(self._colormap)

    def figure(self):
        """ Return the local figure variable. """
        return self._figure

    def has_opr(self):
        """ Check if the operation is None. """
        return self.has_operation

    def renew_cutout(self, data, slices):
        """ Renew the value of self.cutout with the given data and slices """
        newslice = []
        for i, sli in enumerate(slices):
            if isinstance(sli, tuple):
                data = data.take(sli, axis=i)
                newslice.append(slice(None))
            else:
                newslice.append(sli)
        self.cutout = data[tuple(newslice)].squeeze()

    def renewPlot(self, s, scalDims):
        """ Draw given data. """
        self._axes.clear()
        data = self._ui.get(0)
        self._anim_timer.stop()
        if isinstance(data, self.noPrintTypes):
            # Print strings or lists of strings to the graph directly
            self._axes.text(-0.1, 1.1, str(data), va='top', wrap=True)
            self._axes.axis('off')
        elif isinstance(data, Dataset) and data.shape == ():
            # Print single values of h5py arrays to the graph directly
            self._axes.text(-0.1, 1.1, data[()], va='top', wrap=True)
            self._axes.axis('off')
        elif isinstance(data[0], list):
            # If there is an array of lists plot each element as a graph
            self._img = [self._axes.plot(lst) for lst in data]
        else:
            non_scalar_idx = list(set(range(data.ndim)) - set(scalDims))
            s_mod = tuple(s[i] for i in non_scalar_idx)
            self._tick_str = [scalDims, s_mod]
            # Cut out the chosen piece of the array and plot it
            self.renew_cutout(data, s)
            if len(self._oprdim) and not all(np.isin(self._oprdim, scalDims)):
                a = np.setdiff1d(self._oprdim, scalDims)
                self._oprcorr = tuple(b - (scalDims <= b).sum() for b in a)
                self.cutout = self._opr(self.cutout)
            else:
                self._oprcorr = None
            # Transpose the first two dimensions if it is chosen
            if self._ui.Transp.isChecked() and self.cutout.ndim > 1:
                self.cutout = np.swapaxes(self.cutout, 0, 1)
            self.plot()
            self.reapply_setup()

    def plot(self):
        """ Draw one plot step """
        # Check for empty dimensions
        if 0 in self.cutout.shape:
            self._axes.clear()
            return
        # Print the Value(s) directly
        if self.cutout.ndim == 0 or self._ui.PrintFlat.isChecked():
            self._axes.clear()
            text_item = pg.TextItem(str(self.cutout))
            self._axes.addItem(text_item)
        # Graph an 1D-cutout
        elif self.cutout.ndim == 1:
            self._axes.clear()
            self._img = self._axes.plot(self.cutout)
            self._set_ticks(self._tick_str[1], False, 1)
            alim = self._axes.get_ylim()
            if alim[0] > alim[1]:
                self._axes.invert_yaxis()
        # 2D-cutout will be shown using imshow, scatter or plot
        elif self.cutout.ndim == 2:
            if self._ui.Plot2D.isChecked():
                unsave = self._ui.config.getboolean('opt', 'unsave', fallback=False)
                if self.cutout.shape[1] > 500 and not unsave:
                    msg = "You are trying to plot more than 500 lines!"
                    msg += " (change to 'unsave' mode in options to plot them anyway)"
                    self._ui.info_msg(msg, -1)
                    return
                self._img = self._axes.plot(self.cutout)
                self._set_ticks(self._tick_str[1], 1)
            elif self._ui.PlotScat.isChecked() and self.cutout.shape[1] <= 4:
                self._n_D_scatter()
            else:
                self._two_D_plot()
        # higher-dimensional cutouts will first be flattened
        elif self.cutout.ndim >= 3:
            self._n_D_plot()
        # self._canv.draw()

    def reapply_setup(self):
        """
            Reapply the basic setup such that the colorbar, colormap,
            limits, cursor and annotations are in the usual position.
        """
        # Reset the colorbar. A better solution would be possible, if the
        # axes were not cleared everytime.
        self.colorbar()
        self.colormap()
        if self.cutout.size > 0:
            self._clim = (np.nanmin(self.cutout), np.nanmax(self.cutout))
            # Set the minimum and maximum values from the data
            if self._ui.txtMin.text()[-1] != "\U0001F512":
                self._ui.txtMin.setText(f"min : {reformat(self._clim[0])}")
            if self._ui.txtMax.text()[-1] != "\U0001F512":
                self._ui.txtMax.setText(f"max : {reformat(self._clim[1])}")
        else:
            # Reset the minimum and maximum text
            self._ui.txtMin.setText('min : ')
            self._ui.txtMax.setText('max : ')

        # if isinstance(self._img, list):
            # for i in self._img:
                # i.set_picker(5.)
        # else:
            # self._img.set_picker(True)
        # self._cursor = Cursor(self._axes, useblit=False, color='red', linewidth=1)
        # if self._ui.config.getboolean('opt', 'cursor', fallback=False):
            # self._cursor.visible = False
        # self.annotation.remove()
        # self.annotation = self._figure.text(0.3, 0.95, "0, 0", visible=False,
                                            # backgroundcolor="silver")
        # self._canv.mpl_connect('pick_event', self.onclick)

    def set_operation(self, operation="None"):
        """ Set an operation to be performed on click on a dimension. """
        self.has_operation = (operation != "None")
        if not self.has_operation:
            self._oprdim = np.array([], dtype=int)
            self._opr = (lambda x: x)
        else:
            operations = {'nanmin': np.nanmin, 'nanmax': np.nanmax,
                          'nanmean': np.nanmean, 'nanmedian': np.nanmedian}
            self._opr = lambda x: operations[operation](x, axis=self._oprcorr)
        return self._oprdim

    def set_oprdim(self, value=None):
        """ Set the operation dimension. """
        if value is None:
            self._oprdim = np.array([], dtype=int)
        else:
            self._oprdim = np.setxor1d(self._oprdim, value)
        if self.has_operation:
            return self._oprdim
        return []

    def toggle_colorbar(self):
        """ Toggle the state of the colorbar """
        self.has_cb = not self.has_cb
        self.colorbar()


class ReshapeDialog(QDialog):
    """ A Dialog for Reshaping the Array. """
    def __init__(self, parent=None):
        """ Initialize. """
        super().__init__(parent)

        # Setup the basic window
        self.resize(400, 150)
        self.setWindowTitle("Reshape the current array")
        self.prodShape = 0
        self.info_msg = parent.info_msg
        gridLayout = QGridLayout(self)

        # Add the current and new shape boxes and their labels
        curShape = QLabel(self)
        curShape.setText("current shape")
        gridLayout.addWidget(curShape, 0, 0, 1, 1)
        self.txtCurrent = QLineEdit(self)
        self.txtCurrent.setEnabled(False)
        gridLayout.addWidget(self.txtCurrent, 0, 1, 1, 1)
        newShape = QLabel(self)
        newShape.setText("new shape")

        gridLayout.addWidget(newShape, 1, 0, 1, 1)
        self.txtNew = QLineEdit(self)
        self.txtNew.textEdited.connect(self._key_press)
        self.cmpl = QCompleter([])
        self.cmpl.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
        self.txtNew.setCompleter(self.cmpl)
        gridLayout.addWidget(self.txtNew, 1, 1, 1, 1)

        # Add a button Box with "OK" and "Cancel"-Buttons
        self.buttonBox = DBB(DBB.Cancel|DBB.Ok, QtCore.Qt.Horizontal)
        gridLayout.addWidget(self.buttonBox, 3, 1, 1, 1)
        self.buttonBox.button(DBB.Cancel).clicked.connect(self.reject)
        self.buttonBox.button(DBB.Ok).clicked.connect(self.accept)

    def _key_press(self, keyEv):
        """ Whenever a key is pressed check for comma and set autofill data."""
        if keyEv and keyEv[-1] == ',':
            shape = _get_shape_from_str(str(keyEv))
            if self.prodShape%shape.prod() == 0:
                rest = self.prodShape // shape.prod()
                self.cmpl.model().setStringList(_suggestion(keyEv, rest))
            else:
                self.cmpl.model().setStringList([keyEv + " Not fitting"])
        return keyEv

    def reshape_array(self, data):
        """ Reshape the currently selected array. """
        while True:
            # Open a dialog to reshape
            self.txtCurrent.setText(str(data.shape))
            self.prodShape = np.array(data.shape).prod()
            self.txtNew.setText("")
            # If "OK" is pressed
            if data.shape and self.exec_():
                # Get the shape sting and split it
                sStr = str(self.txtNew.text())
                if sStr == "":
                    continue
                # Try if the array could be reshaped that way
                try:
                    data = np.reshape(data, _get_shape_from_str(sStr))
                # If it could not be reshaped, get another user input
                except ValueError:
                    self.info_msg("Data could not be reshaped!", -1)
                    continue
                return data, _get_shape_from_str(sStr)
            # If "CANCEL" is pressed
            return data, None


class NewDataDialog(QDialog):
    """ A Dialog for Creating new Data. """
    def __init__(self, parent=None):
        """ Initialize. """
        super().__init__(parent)

        # Setup the basic window
        self.resize(400, 150)
        self.setWindowTitle("Create new data or change the current one")
        Layout = QVBoxLayout(self)
        self.data = {}
        self.lastText = ""
        self.returnVal = None

        # Add the current and new shape boxes and their labels
        label = QLabel(self)
        label.setText(("Use 'this' to reference the current data and 'cutout' "
                       + "for the current view.\nBefore saving enter the "
                       + "variable you want to save.\n"
                       + "Otherwise the original data will be overwritten."))
        Layout.addWidget(label)
        self.history = QTextEdit(self)
        self.history.setEnabled(False)
        Layout.addWidget(self.history)
        self.cmd = QLineEdit(self)
        Layout.addWidget(self.cmd)
        self.err = QLineEdit(self)
        self.err.setEnabled(False)
        self.err.setStyleSheet("color: rgb(255, 0, 0);")
        Layout.addWidget(self.err)

        # Add a button Box with "OK" and "Cancel"-Buttons
        self.buttonBox = DBB(DBB.Cancel|DBB.Ok|DBB.Save, QtCore.Qt.Horizontal)
        Layout.addWidget(self.buttonBox)
        self.buttonBox.button(DBB.Cancel).clicked.connect(self.reject)
        self.buttonBox.button(DBB.Ok).clicked.connect(self._on_accept)
        self.buttonBox.button(DBB.Save).clicked.connect(self._on_save)

    def _on_accept(self):
        """ Try to run the command and append the history on pressing 'OK'. """
        try:
            var, value = self._parsecmd(str(self.cmd.text()))
            methods = {'np': np, 'self': self}
            self.data[var] = eval(value, {'__buildins__': None}, methods)
        except Exception as err:
            self.err.setText(str(err))
            return
        self.history.append(self.cmd.text())
        self.lastText = str(self.cmd.text())
        self.cmd.setText("")

    def _on_save(self):
        """ Return the object currently in the textBox to the Viewer. """
        if re.findall(r"\=", self.cmd.text()):
            return
        if self.cmd.text() == "":
            self.returnVal = re.split(r"\=", self.lastText)[0].strip()
            self.accept()
        else:
            self.returnVal = self.cmd.text().strip()
            if self.returnVal is not None:
                self.accept()
            else:
                return

    def _parsecmd(self, cmd):
        """ Parse the command given by the user. """
        try:
            var, expr = cmd.split("=", 1)
        except ValueError as e:
            raise ValueError("No '=' in expression") from e
        for op in ['(', ')', '[', ']', '{', '}', ',',
                   '+', '-', '*', '/', '%', '^']:
            expr = expr.replace(op, f" {op} ")
        expr = " " + expr + " "
        for datum in self.data:
            expr = expr.replace(f" {datum} ", f"self.data['{datum}']")
        return var.strip(), expr.replace(" ", "")

    def new_data(self, data, cutout):
        """ Generate New Data (maybe using the currently selected array). """
        self.data = {'this': data, 'cutout': cutout}
        self.history.clear()
        while True:
            # Open a dialog to reshape
            self.cmd.setText("")
            self.cmd.setFocus()
            # If "Save" is pressed
            if self.exec_() or self.returnVal is not None:
                if self.data['this'] is None:
                    return (re.split(r"\=", self.lastText)[0].strip(),
                            self.data[self.returnVal])
                if self.cmd.text() == "":
                    return 1, self.data[self.returnVal]
                return str(self.cmd.text()), self.data[self.returnVal]
            return 0, []

class MicroPlot(QDialog):
    def __init__(self, parent, data, local_slice, key):
        super().__init__(parent)
        layout = QVBoxLayout()
        self.setWindowTitle(f"Timecourse of {key} {local_slice}")
        fig = Figure()
        canv = FigureCanvasQTAgg(fig)
        canv.axes = fig.add_subplot(111)
        canv.axes.plot(data)
        layout.addWidget(canv)
        self.setLayout(layout)
