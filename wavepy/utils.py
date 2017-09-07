#!/usr/bin/env python
# -*- coding: utf-8 -*-
# #########################################################################
# Copyright (c) 2015, UChicago Argonne, LLC. All rights reserved.         #
#                                                                         #
# Copyright 2015. UChicago Argonne, LLC. This software was produced       #
# under U.S. Government contract DE-AC02-06CH11357 for Argonne National   #
# Laboratory (ANL), which is operated by UChicago Argonne, LLC for the    #
# U.S. Department of Energy. The U.S. Government has rights to use,       #
# reproduce, and distribute this software.  NEITHER THE GOVERNMENT NOR    #
# UChicago Argonne, LLC MAKES ANY WARRANTY, EXPRESS OR IMPLIED, OR        #
# ASSUMES ANY LIABILITY FOR THE USE OF THIS SOFTWARE.  If software is     #
# modified to produce derivative works, such modified software should     #
# be clearly marked, so as not to confuse it with the version available   #
# from ANL.                                                               #
#                                                                         #
# Additionally, redistribution and use in source and binary forms, with   #
# or without modification, are permitted provided that the following      #
# conditions are met:                                                     #
#                                                                         #
#     * Redistributions of source code must retain the above copyright    #
#       notice, this list of conditions and the following disclaimer.     #
#                                                                         #
#     * Redistributions in binary form must reproduce the above copyright #
#       notice, this list of conditions and the following disclaimer in   #
#       the documentation and/or other materials provided with the        #
#       distribution.                                                     #
#                                                                         #
#     * Neither the name of UChicago Argonne, LLC, Argonne National       #
#       Laboratory, ANL, the U.S. Government, nor the names of its        #
#       contributors may be used to endorse or promote products derived   #
#       from this software without specific prior written permission.     #
#                                                                         #
# THIS SOFTWARE IS PROVIDED BY UChicago Argonne, LLC AND CONTRIBUTORS     #
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT       #
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS       #
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL UChicago     #
# Argonne, LLC OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,        #
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,    #
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;        #
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER        #
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT      #
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN       #
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE         #
# POSSIBILITY OF SUCH DAMAGE.                                             #
# #########################################################################

"""
Utility functions to help.
"""

from __future__ import (print_function)

import numpy as np
from scipy import constants


import matplotlib.pyplot as plt
import time
from tqdm import tqdm  # progress bar
import glob

import pickle as pl

import easygui_qt as easyqt
import os

import dxchange

import configparser
import shutil

from skimage.feature import match_template
from matplotlib.widgets import Slider, Button, RadioButtons, CheckButtons

__authors__ = "Walan Grizolli"
__copyright__ = "Copyright (c) 2016-2017, Argonne National Laboratory"
__version__ = "0.1.0"
__docformat__ = "restructuredtext en"
__all__ = ['print_color', 'print_red', 'print_blue', 'plot_profile',
           'select_file', 'select_dir', 'nan_mask_threshold',
           'crop_matrix_at_indexes', 'crop_graphic', 'crop_graphic_image',
           'crop_graphic_image', 'graphical_select_point_idx',
           'find_nearest_value', 'find_nearest_value_index',
           'dummy_images', 'graphical_roi_idx', 'crop_graphic', 'choose_unit',
           'datetime_now_str', 'time_now_str', 'date_now_str',
           'realcoordvec', 'realcoordmatrix_fromvec', 'realcoordmatrix',
           'reciprocalcoordvec', 'reciprocalcoordmatrix',
           'h5_list_of_groups',
           'progress_bar4pmap', 'load_ini_file', 'rocking_3d_figure']


hc = constants.value('inverse meter-electron volt relationship')  # hc
deg2rad = np.deg2rad(1)
rad2deg = np.rad2deg(1)


def print_color(message, color='red',
                highlights='on_white', attrs=''):
    """
    Print with colored characters. It is only a alias for colored print using
    the package :py:mod:`termcolor` and equals to::

        print(termcolor.colored(message, color, highlights, attrs=attrs))


    See options at https://pypi.python.org/pypi/termcolor

    Parameters
    ----------
    message : str
        Message to print.
    color, highlights: str

    attrs: list

    """
    import termcolor
    print(termcolor.colored(message, color, highlights, attrs=attrs))


def print_red(message):
    """
    Print with colored characters. It is only a alias for colored print using
    the package :py:mod:`termcolor` and equals to::

            print(termcolor.colored(message, color='red'))

    Parameters
    ----------
    message : str
        Message to print.
    """
    import termcolor
    print(termcolor.colored(message, color='red'))


def print_blue(message):
    """
    Print with colored characters. It is only a alias for colored print using
    the package :py:mod:`termcolor` and equals to::

            print(termcolor.colored(message, color='blue'))

    Parameters
    ----------
    message : str
        Message to print.
    """
    import termcolor
    print(termcolor.colored(message, 'blue'))


############
# Plot Tools
############


def _fwhm_xy(xvalues, yvalues):
    """
    Calculate FWHM of a vector  y(x)

    Parameters
    ----------
    xvalues : ndarray
        vector with the values of x
    yvalues : ndarray
        vector with the values of x

    Returns
    -------
    list
        list of values x and y(x) at half maximum in the format
        [[fwhm_x1, fwhm_x2],[fwhm_y1, fwhm_y2]]
    """

    from scipy.interpolate import UnivariateSpline
    spline = UnivariateSpline(xvalues,
                              yvalues-np.min(yvalues)/2-np.max(yvalues)/2,
                              s=0)
    # find the roots and return

    xvalues = spline.roots().tolist()
    yvalues = (spline(spline.roots()) + np.min(yvalues)/2 +
               np.max(yvalues)/2).tolist()

    if len(xvalues) == 2:
        return [xvalues, yvalues]

    else:
        return[[], []]


def mean_plus_n_sigma(array, n_sigma=5):

    '''
    TODO: Write Docstring
    '''
    return np.mean(array) + n_sigma*np.std(array)


def extent_func(img, pixelsize):
    '''
    TODO: Write Docstring
    pixelsize is a list of size 2 as [pixelsize_i, pixelsize_j]

    if pixelsize is a float, then pixelsize_i = pixelsize_j
    '''

    if isinstance(pixelsize, float):
        pixelsize = [pixelsize, pixelsize]

    return np.array((-img.shape[1]*pixelsize[1] / 2,
                     img.shape[1]*pixelsize[1] / 2,
                     -img.shape[0]*pixelsize[0] / 2,
                     img.shape[0]*pixelsize[0] / 2))


def plot_profile(xmatrix, ymatrix, zmatrix,
                 xlabel='x', ylabel='y', zlabel='z', title='Title',
                 xo=None, yo=None,
                 xunit='', yunit='', do_fwhm=True,
                 arg4main=None, arg4top=None, arg4side=None):
    """
    Plot contourf in the main graph plus profiles over vertical and horizontal
    lines defined with mouse.




    Parameters
    ----------
    xmatrix, ymatrix: ndarray
        `x` and `y` matrix coordinates generated with :py:func:`numpy.meshgrid`

    zmatrix: ndarray
        Matrix with the data. Note that ``xmatrix``, ``ymatrix`` and
        ``zmatrix`` must have the same shape

    xlabel, ylabel, zlabel: str, optional
        Labels for the axes ``x``, ``y`` and ``z``.

    title: str, optional
        title for the main graph #BUG: sometimes this title disappear

    xo, yo: float, optional
        if equal to ``None``, it allows to use the mouse to choose the vertical
        and horizontal lines for the profile. If not ``None``, the profiles
        lines are are centered at ``(xo,yo)``

    xunit, yunit: str, optional
        String to be shown after the values in the small text box

    do_fwhm: Boolean, optional
        Calculate and print the FWHM in the figure. The script to calculate the
        FWHM is not very robust, it works well if only one well defined peak is
        present. Turn this off by setting this var to ``False``

    *arg4main:
        `*args` for the main graph

    *arg4top:
        `*args` for the top graph

    *arg4side:
        `*args` for the side graph

    Returns
    -------

    ax_main, ax_top, ax_side: matplotlib.axes
        return the axes in case one wants to modify them.

    delta_x, delta_y: float

    Example
    -------

    >>> import numpy as np
    >>> import wavepy.utils as wpu
    >>> xx, yy = np.meshgrid(np.linspace(-1, 1, 101), np.linspace(-1, 1, 101))
    >>> wpu.plot_profile(xx, yy, np.exp(-(xx**2+yy**2)/.2))

    Animation of the example above:

    .. image:: img/plot_profile_animation.gif

    """

    if arg4side is None:
        arg4side = {}
    if arg4top is None:
        arg4top = {}
    if arg4main is None:
        arg4main = {'cmap': 'viridis'}
    from matplotlib.widgets import Cursor

    z_min, z_max = float(np.nanmin(zmatrix)), float(np.nanmax(zmatrix))

    fig = plt.figure(figsize=(11., 8.5))
    fig.suptitle(title, fontsize=14, weight='bold')

    # Main contourf plot
    main_subplot = plt.subplot2grid((4, 5), (1, 1), rowspan=3, colspan=3)
    ax_main = fig.gca()
    ax_main.minorticks_on()
    plt.grid(True)
    ax_main.get_yaxis().set_tick_params(which='both', direction='out')
    ax_main.get_xaxis().set_tick_params(which='both', direction='out')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    main_plot = main_subplot.contourf(xmatrix, ymatrix, zmatrix,
                                      256, **arg4main)

    colorbar_subplot = plt.subplot2grid((4, 20), (1, 0), rowspan=3, colspan=1)
    plt.colorbar(main_plot, cax=colorbar_subplot)

    # Top graph, horizontal profile. Empty, wait data from cursor on the graph.
    top_subplot = plt.subplot2grid((4, 5), (0, 1), rowspan=1, colspan=3)
    ax_top = fig.gca()
    ax_top.set_xticklabels([])
    plt.minorticks_on()
    plt.grid(True, which='both', axis='both')
    plt.ylabel(zlabel)
    plt.yticks(np.linspace(z_min, z_max, 3))
    plt.ylim(z_min, 1.05 * z_max)

    # Side graph, vertical profile. Empty, wait data from cursor on the graph.
    ax_side = side_subplot = plt.subplot2grid((4, 5), (1, 4),
                                              rowspan=3, colspan=1)
    ax_side.set_yticklabels([])
    plt.minorticks_on()
    plt.grid(True, which='both', axis='both')
    plt.xlabel(zlabel)
    ax_side.xaxis.set_label_position('top')
    plt.xticks(np.linspace(z_min, z_max, 3), rotation=-90)
    plt.xlim(z_min, 1.05 * z_max)

    def onclick(event):
        if (event.xdata is not None and event.ydata is not None and
           event.button == 2):

            return plot_profiles_at(event.xdata, event.ydata)

        if event.button == 3:
            for j in [main_subplot, top_subplot, side_subplot]:
                j.lines = []
                j.legend_ = None

            plt.draw()

    def plot_profiles_at(_xo, _yo):

        # catch the x and y position to draw the profile
        _xo = xmatrix[1, np.argmin(np.abs(xmatrix[1, :] - _xo))]
        _yo = ymatrix[np.argmin(np.abs(ymatrix[:, 1] - _yo)), 1]
        # print('xo: %.4f, yo: %.4f' % (xo, yo))

        # plot the vertical and horiz. profiles that pass at xo and yo
        lines = top_subplot.plot(xmatrix[ymatrix == _yo],
                                 zmatrix[ymatrix == _yo],
                                 lw=2, drawstyle='steps-mid', **arg4top)

        side_subplot.plot(zmatrix[xmatrix == _xo],
                          ymatrix[xmatrix == _xo],
                          lw=2, drawstyle='steps-mid', **arg4side)

        # plot the vertical and horz. lines in the main graph
        last_color = lines[0].get_color()
        main_subplot.axhline(_yo, ls='--', lw=2, color=last_color)
        main_subplot.axvline(_xo, ls='--', lw=2, color=last_color)

        message = r'$x_o = %.4g %s$' % (_xo, xunit)
        message = message + '\n' + r'$y_o = %.4g %s$' % (_yo, yunit)

        main_subplot_x_min, main_subplot_x_max = main_subplot.get_xlim()
        main_subplot_y_min, main_subplot_y_max = main_subplot.get_ylim()

        # calculate and plot the FWHM
        _delta_x = None
        _delta_y = None

        if do_fwhm:
            [fwhm_top_x,
             fwhm_top_y] = _fwhm_xy(xmatrix[(ymatrix == _yo) &
                                            (xmatrix > main_subplot_x_min) &
                                            (xmatrix < main_subplot_x_max)],
                                    zmatrix[(ymatrix == _yo) &
                                            (xmatrix > main_subplot_x_min) &
                                            (xmatrix < main_subplot_x_max)])

            [fwhm_side_x,
             fwhm_side_y] = _fwhm_xy(ymatrix[(xmatrix == _xo) &
                                             (ymatrix > main_subplot_y_min) &
                                             (ymatrix < main_subplot_y_max)],
                                     zmatrix[(xmatrix == _xo) &
                                             (ymatrix > main_subplot_y_min) &
                                             (ymatrix < main_subplot_y_max)])

            if len(fwhm_top_x) == 2:
                _delta_x = abs(fwhm_top_x[0] - fwhm_top_x[1])
                print('fwhm_x: %.4f' % _delta_x)
                message = message + '\n'
                message += r'$FWHM_x = {0:.4g} {1:s}'.format(_delta_x, xunit)
                message += '$'

                top_subplot.plot(fwhm_top_x, fwhm_top_y, 'r--+',
                                 lw=1.5, ms=15, mew=1.4)

            if len(fwhm_side_x) == 2:
                _delta_y = abs(fwhm_side_x[0] - fwhm_side_x[1])
                print('fwhm_y: %.4f\n' % _delta_y)
                message = message + '\n'
                message += r'$FWHM_y = {0:.4g} {1:s}'.format(_delta_y, xunit)
                message += '$'

                side_subplot.plot(fwhm_side_y, fwhm_side_x, 'r--+',
                                  lw=1.5, ms=15, mew=1.4)

        # adjust top and side graphs to the zoom of the main graph

        fig.suptitle(title, fontsize=14, weight='bold')

        top_subplot.set_xlim(main_subplot_x_min, main_subplot_x_max)
        side_subplot.set_ylim(main_subplot_y_min, main_subplot_y_max)

        plt.gcf().texts = []
        plt.gcf().text(.8, .75, message, fontsize=14, va='bottom',
                       bbox=dict(facecolor=last_color, alpha=0.5))

        plt.draw()

        return [_delta_x, _delta_y]

    [delta_x, delta_y] = [None, None]
    if xo is None and yo is None:
        # cursor on the main graph
        cursor = Cursor(ax_main, useblit=True, color='red', linewidth=2)
        fig.canvas.mpl_connect('button_press_event', onclick)
        plt.show(block=True)
    else:
        [delta_x, delta_y] = plot_profiles_at(xo, yo)

    return [ax_main, ax_top, ax_side, delta_x, delta_y]


def select_file(pattern='*', message_to_print=None):
    """
    List files under the subdirectories of the current working directory,
    and expected the user to choose one of them.

    The list of files is of the form ``number: filename``. The user choose
    the file by typing the number of the desired filename.


    Parameters
    ----------

    pattern: str
        list only files with this patter. Similar to pattern in the linux
        comands ls, grep, etc
    message_to_print: str, optional

    Returns
    -------

    filename: str
        path and name of the file

    Example
    -------

    >>>  select_file('*.dat')

    """

    pattern = input('File type: [' + pattern + ']: ') or pattern

    list_files = glob.glob(pattern, recursive=True)
    list_files.sort()

    if len(list_files) == 1:
        print_color("Only one option. Loading " + list_files[0])
        return list_files[0]
    elif len(list_files) == 0:
        print_color("\n\n\n# ================ ERROR ========================#")
        print_color("No files with pattern '" + pattern + "'")
    else:

        if message_to_print is None:
            print("\n\n\n#===============================================#")
            print('Enter the number of the file to be loaded:\n')
        else:
            print(message_to_print)

        for nOption, _ in enumerate(list_files):
            print(str(nOption) + ': ' + list_files[nOption])

        print('Any value different of the above raises GeneratorExit\n')

        try:
            choice = int(input())
            print('Selected file ' + list_files[choice])
            return list_files[choice]
        except ValueError:
            print('\nSelected value does not correspond to any option.')
            print('raise GeneratorExit!\n')
            raise GeneratorExit


def select_dir(message_to_print=None, pattern='**/'):
    """

    List subdirectories of the current working directory, and expected the
    user to choose one of them.

    The list of files is of the form ``number: filename``. The user choose
    the file by typing the number of the desired filename.

    Similar to :py:func:`wavepy.utils.select_file`

    Parameters
    ----------

    message_to_print:str, optional

    Returns
    -------

    str
        directory path

    See Also
    --------
    :py:func:`wavepy.utils.select_file`

    """

    return select_file(pattern=pattern, message_to_print=message_to_print)


def _check_empty_fname(fname):

    if fname == []:
        return None
    else:
        return fname


def gui_load_data_ref_dark_filenames(directory='',
                                     title="File name with Data"):

    originalDir = os.getcwd()

    if directory != '':

        if os.path.isdir(directory):
            os.chdir(directory)
        else:
            print_red("WARNING: Directory " + directory + " doesn't exist.")
            print_blue("MESSAGE: Using current working directory " +
                       originalDir)

    fname1 = easyqt.get_file_names(title=title)

    if len(fname1) == 3:
        [fname1, fname2, fname3] = fname1

    elif len(fname1) == 0:
        return [None, None, None]

    else:

        fname1 = fname1[0]  # convert list to string
        os.chdir(fname1.rsplit('/', 1)[0])

        fname2 = easyqt.get_file_names("File name with Reference")[0]
        fname3 = easyqt.get_file_names("File name with Dark Image")[0]

        fname3 = _check_empty_fname(fname3)

    os.chdir(originalDir)

    return fname1, fname2, fname3


def gui_load_data_ref_dark_files(directory='', title="File name with Data"):
    '''
        TODO: Write Docstring
    '''

    [fname1,
     fname2,
     fname3] = gui_load_data_ref_dark_filenames(directory=directory,
                                                title=title)

    print_blue('MESSAGE: Loading ' + fname1)
    print_blue('MESSAGE: Loading ' + fname2)
    print_blue('MESSAGE: Loading ' + fname3)

    return (dxchange.read_tiff(fname1),
            dxchange.read_tiff(fname2),
            dxchange.read_tiff(fname3))


def gui_load_data_dark_filenames(directory='', title="File name with Data"):
    '''
        TODO: Write Docstring
    '''

    originalDir = os.getcwd()

    if directory != '':

        if os.path.isdir(directory):
            os.chdir(directory)
        else:
            print_red("WARNING: Directory " + directory + " doesn't exist.")
            print_blue("MESSAGE: Using current working directory " +
                       originalDir)

    fname1 = easyqt.get_file_names("File name with Data")

    if len(fname1) == 2:
        [fname1, fname2] = fname1

    elif len(fname1) == 0:
        return [None, None]

    else:

        fname1 = fname1[0]  # convert list to string
        os.chdir(fname1.rsplit('/', 1)[0])
        fname2 = easyqt.get_file_names("File name with Dark Image")[0]

    os.chdir(originalDir)

    return fname1, fname2


def gui_load_data_dark_files(directory='', title="File name with Data"):
    '''
        TODO: Write Docstring
    '''

    fname1, fname2 = gui_load_data_dark_filenames(directory='',
                                                  title="File name with Data")

    print_blue('MESSAGE: Loading ' + fname1)
    print_blue('MESSAGE: Loading ' + fname2)

    return (dxchange.read_tiff(fname1), dxchange.read_tiff(fname2))


def load_files_scan(samplefileName, split_char='_', suffix='.tif'):
    '''

    alias for

    >>> glob.glob(samplefileName.rsplit('_', 1)[0] + '*' + suffix)

    '''

    return glob.glob(samplefileName.rsplit('_', 1)[0] + '*' + suffix)


def gui_list_data_phase_stepping(directory=''):
    '''
        TODO: Write Docstring
    '''

    originalDir = os.getcwd()

    if directory != '':

        if os.path.isdir(directory):
            os.chdir(directory)
        else:
            print_red("WARNING: Directory " + directory + " doesn't exist.")
            print_blue("MESSAGE: Using current working directory " +
                       originalDir)

    samplef1 = easyqt.get_file_names("Choose one of the scan " +
                                     "files with sample")

    if len(samplef1) == 3:
        [samplef1, samplef2, samplef3] = samplef1

    else:

        samplef1 = samplef1[0]
        os.chdir(samplef1.rsplit('/', 1)[0])

        samplef2 = easyqt.get_file_names("File name with Reference")[0]
        samplef3 = easyqt.get_file_names("File name with Dark Image")

        if len(samplef3) == 1:
            samplef3 = samplef3[0]
        else:
            samplef3 = ''
            print_red('MESSAGE: You choosed to not use dark images')

    print_blue('MESSAGE: Sample files directory: ' +
               samplef1.rsplit('/', 1)[0])

    samplef1.rsplit('/', 1)[0]

    listf1 = load_files_scan(samplef1)
    listf2 = load_files_scan(samplef2)
    listf3 = load_files_scan(samplef3)

    listf1.sort()
    listf2.sort()
    listf3.sort()

    return listf1, listf2, listf3


def _choose_one_of_this_options(header=None, list_of_options=None):
    """
    Plot contourf in the main graph plus profiles over vertical and horizontal
    line defined by mouse.

    Parameters
    ----------

    """
    for whatToPrint in header:
        print(whatToPrint)

    for optionChar, optionDescription in list_of_options:
        print(optionChar + ': ' + optionDescription)

    entry = input()

    if entry == '!':
        raise GeneratorExit

    return entry


# Tools for masking/croping

def nan_mask_threshold(input_matrix, threshold=0.0):
    """
    Calculate a square mask for array above OR below a threshold


    Parameters
    ----------
    input_matrix : ndarray
        2 dimensional (or n-dimensional?) numpy.array to be masked
    threshold: float
        threshold for masking. If real (imaginary) value, values below(above)
        the threshold are set to NAN

    Returns
    -------
    ndarray
        array with values either equal to 1 or NAN.


    Example
    -------

        To use as a mask for array use:

        >>> mask = nan_mask_threshold(input_array, threshold)
        >>> masked_array = input_array*mask

    Notes
    -----
        - Note that ``array[mask]`` will return only the values where ``mask == 1``.
        - Also note that this is NOT the same as the `masked arrays <http://docs.scipy.org/doc/numpy/reference/maskedarray.html>`_ in numpy.

    """

    mask_intensity = np.ones(input_matrix.shape)

    if np.isreal(threshold):
        mask_intensity[input_matrix <= threshold] = float('nan')
    else:
        mask_intensity[input_matrix >= np.imag(threshold)] = float('nan')

    return mask_intensity


def crop_matrix_at_indexes(input_matrix, list_of_indexes):
    """
    Alias for ``np.copy(inputMatrix[i_min:i_max, j_min:j_max])``

    Parameters
    ----------
    input_matrix : ndarray
        2 dimensional array
    list_of_indexes: list
        list in the format ``[i_min, i_max, j_min, j_max]``

    Returns
    -------
    ndarray
        copy of the sub-region ``inputMatrix[i_min:i_max, j_min:j_max]``
        of the inputMatrix.

    Warning
    -------
        Note the `difference of copy and view in Numpy
        <http://scipy-cookbook.readthedocs.io/items/ViewsVsCopies.html>`_.
    """

    if list_of_indexes == [0, -1, 0, -1]:
        return input_matrix

    return np.copy(input_matrix[list_of_indexes[0]:list_of_indexes[1],
                   list_of_indexes[2]:list_of_indexes[3]])


def gui_align_two_images(img1, img2, option='crop', verbosePlot=True):
    '''


    GUI for the function :py:func:`wavepy:utils:align_two_images`, where
    the initial and final images are ploted, and the selection of the ROI is
    done graphically.


    Parameters
    ----------
    img1 : ndarray
        2 dimensional array
    img2 : ndarray
        2 dimensional array
    option: str
        option to crop both images or to fill the missing data of ``img2``

        'pad'
            ``img2`` will be padded with zeros to have the same size than img1.

        'crop'
            both images will be cropped to the size of ROI. Note that ``img2``
            will be exactally the ROI.
    verbose: boolean
        if ``True``, it plots ``img2`` to select the color scale, and in the
        end plots the final aligned images

    Returns
    -------
    img1, img2
        two ndarray

    See Also
    --------
        :py:func:`wavepy:utils:align_two_images`

    Examples
    --------

    >>> import wavepy.utils as wpu
    >>> import numpy as np
    >>> import matplotlib.pyplot as plt
    >>>
    >>> pad_i = 50
    >>> pad_j = 50
    >>>
    >>>
    >>> shift_j = -37  # x
    >>> shift_i = 21  # y
    >>>
    >>> foo1 = np.pad(wpu.dummy_images('Shapes', (201, 201), noise=1),
    >>>               ((pad_i, pad_i), (pad_j, pad_j)), 'constant')
    >>>
    >>>
    >>> foo2 = np.pad(wpu.dummy_images('Shapes', (201, 201), noise=1.7),
    >>>               ((pad_i + shift_i, pad_i - + shift_i),
    >>>                (pad_j + shift_j, pad_j - shift_j)), 'constant')
    >>>
    >>> plt.figure()
    >>> plt.imshow(foo1)
    >>> plt.figure()
    >>> plt.imshow(foo2)
    >>> plt.show(block=True)
    >>>
    >>> img1, img2 = wpu.gui_align_two_images(foo1, foo2, 'crop')
    >>>
    >>> plt.figure()
    >>> plt.imshow(img1)
    >>> plt.figure()
    >>> plt.imshow(img2)
    >>> plt.show(block=True)



    '''

    colorlimit = [img2.min(), img2.max()]
    cmap = 'viridis'

    if verbosePlot:

        [colorlimit,
         cmap] = plot_slide_colorbar(np.asarray(img2), title='Image 2',
                                     cmin_o=colorlimit[0],
                                     cmax_o=colorlimit[1])

    idxROI = graphical_roi_idx(img2, kargs4graph={'cmap': cmap,
                                                  'vmin': colorlimit[0],
                                                  'vmax': colorlimit[1]})

    if idxROI == [0, -1, 0, -1]:
        print('NO CROP')
        idxROI = 0

    [img1_aligned,
     img2_aligned] = align_two_images(img1, img2, option='crop',
                                      idxROI=idxROI)

    if verbosePlot:
        plot_slide_colorbar(img1_aligned, title='Image 1',
                            cmin_o=mean_plus_n_sigma(img1, n_sigma=-5),
                            cmax_o=mean_plus_n_sigma(img1, n_sigma=+5))

        plot_slide_colorbar(img2_aligned, title='Image 2',
                            cmin_o=mean_plus_n_sigma(img1, n_sigma=-5),
                            cmax_o=mean_plus_n_sigma(img1, n_sigma=+5))

    return img1_aligned, img2_aligned


def align_two_images(img1, img2, option='crop', idxROI=0):

    '''
    Align two images by using the cross
    correlation of the images to determine the misalignment.

    First, a region of interest (ROI) in ``img2`` is searched in ``img1``, and
    the necessary shift to align ``img2`` is determined. The shift is then
    applied to ``img2`` by croping it. Because of the shift, ``img2`` will be
    missing data on the edges, and there are two options to make the two images
    to have the same size: to crop ``img1`` or to pad ``img2``, as defined by
    the parameter ``option``.


    Parameters
    ----------
    img1: ndarray
        2 dimensional array
    img2: ndarray
        2 dimensional array
    option: str
        option to crop both images or to fill the missing data of ``img2``

        'pad'
            ``img2`` will be padded with zeros to have the same size than img1.

        'crop'
            both images will be cropped to the size of ROI. Note that ``img2``
            will be exactally the ROI.
    idxROI: list or integer
        ROI list of indexes ``[i_min, i_max, j_min,_j_max]``. If idxROI is an
        integer, then it is considered that
        ``[i_min, i_max, j_min,_j_max] = [idxROI, -idxROI, idxROI, -idxROI]``


    Returns
    -------
    ndarray, ndarray
        aligned images

    Examples
    --------

    >>> import wavepy.utils as wpu
    >>> import numpy as np
    >>> import matplotlib.pyplot as plt
    >>>
    >>> pad_i = 50
    >>> pad_j = 50
    >>>
    >>>
    >>> shift_j = -37  # x
    >>> shift_i = 21  # y
    >>>
    >>> foo1 = np.pad(wpu.dummy_images('Shapes', (201, 201), noise=1),
    >>>               ((pad_i, pad_i), (pad_j, pad_j)), 'constant')
    >>>
    >>>
    >>> foo2 = np.pad(wpu.dummy_images('Shapes', (201, 201), noise=1.7),
    >>>               ((pad_i + shift_i, pad_i - + shift_i),
    >>>                (pad_j + shift_j, pad_j - shift_j)), 'constant')
    >>>
    >>> plt.figure()
    >>> plt.imshow(foo1)
    >>> plt.figure()
    >>> plt.imshow(foo2)
    >>> plt.show(block=True)
    >>>
    >>> img1, img2 = wpu.align_two_images(foo1, foo2, 'crop', 100)
    >>>
    >>> plt.figure()
    >>> plt.imshow(img1)
    >>> plt.figure()
    >>> plt.imshow(img2)
    >>> plt.show(block=True)


    '''

    if isinstance(idxROI, list):
        [i_min, i_max, j_min, j_max] = idxROI

    elif isinstance(idxROI, int):
        [i_min, i_max, j_min, j_max] = [idxROI, img1.shape[0] - idxROI,
                                        idxROI, img1.shape[1] - idxROI]

    #    print_red('[i_min, i_max, j_min, j_max]')
    #    print_red([i_min, i_max, j_min, j_max])

    iL = i_max - i_min
    jL = j_max - j_min

    print_red('WARNING: Calculating image displacement... ' +
              'PROGRAM MAY FREEZE!!!')

    result = match_template(img1, img2[i_min:i_max, j_min:j_max])
    ij = np.unravel_index(np.argmax(result), result.shape)
    pos_x, pos_y = ij[::-1]
    print_blue('MESSAGE: pos_x, pos_y =' +
               ' {}, {}'.format(pos_x, pos_y))

    shift_x = pos_x - j_min
    shift_y = pos_y - i_min

    print_blue('MESSAGE: shift_x, shift_y =' +
               ' {}, {}'.format(shift_x, shift_y))

    if option == 'crop':

        img1 = img1[pos_y:pos_y + iL,
                    pos_x:pos_x + jL]
        img2 = img2[i_min:i_max, j_min:j_max]

    else:  # for option == 'pad' and fallback option

        if shift_y > 0:

            img2 = np.pad(img2[:-shift_y, :],
                          ((shift_y, 0), (0, 0)), 'constant')
        else:

            img2 = np.pad(img2[-shift_y:, :],
                          ((0, -shift_y), (0, 0)), 'constant')

        if shift_x > 0:

            img2 = np.pad(img2[:, :-shift_x],
                          ((0, 0), (shift_x, 0)), 'constant')
        else:

            img2 = np.pad(img2[:, -shift_x:],
                          ((0, 0), (0, -shift_x)), 'constant')

    return img1, img2


def align_many_imgs(samplefileName, idxROI=100, option='crop',
                    padMarginVal = 0, displayPlots=True):
    '''
    How to use
    ----------
        Create a folder with all the files you want to align. You may want to
        include a dark file. You will be asked to select one file which
        will be the reference, that is, all other files in this folder
        (with the same extension) will be aligned to the reference.

        Folders with the aligned files will be created inside this same folder.

    TODO: This function can be upgraded to use multiprocessing



    Parameters
    ----------
    samplefileName : string
        2 dimensional array

    idxROI : list or integer
        ROI list of indexes ``[i_min, i_max, j_min,_j_max]``. If idxROI is an
        integer, then it is considered that
        ``[i_min, i_max, j_min,_j_max] = [idxROI, -idxROI, idxROI, -idxROI]``

    option : str
        option to crop both images or to fill the missing data of ``img2``

        'pad'
            ``img2`` will be padded with zeros to have the same size than img1.

        'crop'
            both images will be cropped to the size of ROI. Note that ``img2``
            will be exactally the ROI.

    padMarginVal : int
        Value to pad ``img2`` when option is to pad.

    displayPlots : boolean
        Flag to display every aligned image (``displayPlots=True``) of
        to plot and save in the background (``displayPlots=False``).



    Returns
    -------
    list
        list with the filenames of the aligned images.

    See Also
    --------
        :py:func:`wavepy:utils:align_two_images`,
        :py:func:`wavepy:utils:gui_align_two_images`

    Examples
    --------

    >>> import wavepy.utils as wpu
    >>> samplefileName = easyqt.get_file_names("Choose the reference file " +
    >>>                                        "for alignment")[0]
    >>>
    >>> wpu.align_many_imgs(samplefileName)


    ``idxROI`` is the same as in :py:func:`wavepy:utils:align_two_images`:

    >>> import wavepy.utils as wpu
    >>> samplefileName = easyqt.get_file_names("Choose the reference file " +
    >>>                                        "for alignment")[0]
    >>>
    >>> wpu.align_many_imgs(samplefileName, idxROI=[400, 2100, 300, 2000],
    >>>                     dontShowPlots=False)


    '''

    if displayPlots:
        plt.ion()
    else:
        plt.ioff()

    data_dir = samplefileName.rsplit('/', 1)[0]
    os.chdir(data_dir)

    os.makedirs('aligned_tiff', exist_ok=True)
    os.makedirs('aligned_png', exist_ok=True)

    print_blue('MESSAGE: Loading files ' +
               samplefileName.rsplit('_', 1)[0] + '*.tif')

    listOfDataFiles = glob.glob(data_dir + '/*.tif')
    listOfDataFiles.sort()

    img_ref = dxchange.read_tiff(samplefileName)

    # Loop over the files in the folder

    outFilesList = []

    if padMarginVal > 0:
        img_ref = np.pad(img_ref, ((padMarginVal, padMarginVal),
                                   (padMarginVal, padMarginVal)),
                         'constant', constant_values=1)

    for imgfname in listOfDataFiles:

        img = dxchange.read_tiff(imgfname)

        print_blue('MESSAGE: aligning ' + imgfname)

        if padMarginVal == 0:
            img = np.pad(img, ((padMarginVal, padMarginVal),
                               (padMarginVal, padMarginVal)),
                         'constant', constant_values=1)

        # note that these two cases are different, with different effects
        # depending if we want to crop or to pad

        if option == 'pad':
            print_blue("MESSAGE: function align_many_imgs: using 'pad' mode")
            _, img_aligned = align_two_images(img_ref, img,
                                              'pad', idxROI=idxROI)
        else:
            print_blue("MESSAGE: function align_many_imgs: using 'crop' mode")
            img_aligned, _ = align_two_images(img, img_ref,
                                              'crop', idxROI=idxROI)

        #        if padMarginVal >= 0:
        #            img_aligned = img_aligned[padMarginVal:-padMarginVal,
        #                                      padMarginVal:-padMarginVal]

        # save files
        outfname = 'aligned_tiff/' + \
                   imgfname.split('.')[0].rsplit('/', 1)[-1] + \
                   '_aligned.tiff'

        outFilesList.append(outfname)

        dxchange.write_tiff(img_aligned, outfname)
        print_blue('MESSAGE: file ' + outfname + ' saved.')

        plt.figure(figsize=(8, 7))
        plt.imshow(img_aligned, cmap='viridis')
        plt.title('ALIGNED, ' + imgfname.split('/')[-1])
        plt.savefig(outfname.replace('tiff', 'png'))

        if displayPlots:
            plt.show(block=False)
            plt.pause(.1)
        else:
            plt.close()

    if not displayPlots:
        plt.ion()

    return outFilesList


def find_nearest_value(input_array, value):
    """

    Alias for
    ``input_array.flatten()[np.argmin(np.abs(input_array.flatten() - value))]``

    In a array of float numbers, due to the precision, it is impossible to
    find exact values. For instance something like ``array1[array2==0.0]``
    might fail because the zero values in the float array ``array2`` are
    actually something like 0.0004324235 (fictious value).

    This function will return the value in the array that is the nearest to
    the parameter ``value``.

    Parameters
    ----------

    input_array: ndarray
    value: float

    Returns
    -------
    ndarray

    Example
    -------

    >>> foo = dummy_images('NormalDist')
    >>> find_nearest_value(foo, 0.5000)
    0.50003537554879007

    See Also
    --------

    :py:func:`wavepy:utils:find_nearest_value_index`

    """

    return input_array.flatten()[np.argmin(np.abs(input_array.flatten() -
                                                  value))]


def find_nearest_value_index(input_array, value):
    """

    Similar to :py:func:`wavepy.utils.find_nearest_value`, but returns
    the index of the nearest value (instead of the value itself)

    Parameters
    ----------

    input_array : ndarray
    value : float

    Returns
    -------

    tuple of ndarray:
        each array have the index of the nearest value in each dimension

    Note
    ----
    In principle it has no limit of the number of dimensions.


    Example
    -------

    >>> foo = dummy_images('NormalDist')
    >>> find_nearest_value(foo, 0.5000)
    0.50003537554879007
    >>> (i_index, j_index) = find_nearest_value_index(foo, 0.500)
    >>> foo[i_index[:], j_index[:]]
    array([ 0.50003538,  0.50003538,  0.50003538,  0.50003538])

    See Also
    --------
    :py:func:`wavepy:utils:find_nearest_value`


    """

    return np.where(input_array == find_nearest_value(input_array, value))


def dummy_images(imagetype=None, shape=(100, 100), **kwargs):
    """

    Dummy images for simple tests.


    Parameters
    ----------

    imagetype: str
        See options Below
    shape: tuple
        Shape of the image. Similar to :py:mod:`numpy.shape`
    kwargs:
        keyword arguments depending on the image type.


    Image types

        * Noise (default):    alias for ``np.random.random(shape)``

        * Stripes:            ``kwargs: nLinesH, nLinesV``

        * SumOfHarmonics: image is defined by:
          .. math:: \sum_{ij} Amp_{ij} \cos (2 \pi i y) \cos (2 \pi j x).

            * Note that ``x`` and ``y`` are assumed to in the range [-1, 1].
              The keyword ``kwargs: harmAmpl`` is a 2D list that can
              be used to set the values for Amp_ij, see **Examples**.

        * Shapes: see **Examples**. ``kwargs=noise``, amplitude of noise to be
          added to the image

        * NormalDist: Normal distribution where it is assumed that ``x`` and
          ``y`` are in the interval `[-1,1]`. ``keywords: FWHM_x, FWHM_y``


    Returns
    -------
        2D ndarray


    Examples
    --------

    >>> import matplotlib.pyplot as plt
    >>> plt.imshow(dummy_images())

    is the same than

    >>> plt.imshow(dummy_images('Noise'))


    .. image:: img/dummy_image_Noise.png
       :width: 350px


    >>> plt.imshow(dummy_images('Stripes', nLinesV=5))

    .. image:: img/dummy_image_stripe_V5.png
       :width: 350px


    >>> plt.imshow(dummy_images('Stripes', nLinesH=8))

    .. image:: img/dummy_image_stripe_H8.png
       :width: 350px


    >>> plt.imshow(dummy_images('Checked', nLinesH=8, nLinesV=5))

    .. image:: img/dummy_image_checked_v5_h8.png
       :width: 350px


    >>> plt.imshow(dummy_images('SumOfHarmonics', harmAmpl=[[1,0,1],[0,1,0]]))

    .. image:: img/dummy_image_harmonics_101_010.png
       :width: 350px

    >>> plt.imshow(dummy_images('Shapes', noise = 1))

    .. image:: img/dummy_image_shapes_noise_1.png
       :width: 350px

    >>> plt.imshow(dummy_images('NormalDist', FWHM_x = .5, FWHM_y=1.0))

    .. image:: img/dummy_image_NormalDist.png
       :width: 350px


    """

    if imagetype is None:
        imagetype = 'Noise'

    if imagetype == 'Noise':
        return np.random.random(shape)

    elif imagetype == 'Stripes':
        if 'nLinesH' in kwargs:
            nLinesH = kwargs['nLinesH']
            return np.kron([[1, 0] * nLinesH],
                           np.ones((shape[0], shape[1]/2/nLinesH)))
        elif 'nLinesV':
            nLinesV = kwargs['nLinesV']
            return np.kron([[1], [0]] * nLinesV,
                           np.ones((shape[0]/2/nLinesV, shape[1])))
        else:
            return np.kron([[1], [0]] * 10, np.ones((shape[0]/2/10, shape[1])))

    elif imagetype == 'Checked':

        if 'nLinesH' in kwargs:
            nLinesH = kwargs['nLinesH']

        else:
            nLinesH = 1

        if 'nLinesV' in kwargs:
            nLinesV = kwargs['nLinesV']
        else:
            nLinesV = 1

        return np.kron([[1, 0] * nLinesH, [0, 1] * nLinesH] * nLinesV,
                       np.ones((shape[0]/2/nLinesV, shape[1]/2/nLinesH)))
        # Note that the new dimension is int(shape/p)*p !!!

    elif imagetype == 'SumOfHarmonics':

        if 'harmAmpl' in kwargs:
            harmAmpl = kwargs['harmAmpl']
        else:
            harmAmpl = [[1, 1, 1, 1, 1], [1, 1, 1, 1, 1]]

        sumArray = np.zeros(shape)
        iGrid, jGrid = np.mgrid[-1:1:1j * shape[0], -1:1:1j * shape[1]]

        for i in range(len(harmAmpl)):
            for j in range(len(harmAmpl[0])):
                sumArray += harmAmpl[i][j] * np.cos(2 * np.pi * iGrid * i) \
                            * np.cos(2 * np.pi * jGrid * j)

        return sumArray

    elif imagetype == 'Shapes':

        if 'noise' in kwargs:
            noiseAmp = kwargs['noise']
        else:
            noiseAmp = 0.0

        dx, dy = int(shape[0]/10), int(shape[1]/10)
        square = np.ones((dx * 2, dy * 2))
        triangle = np.tril(square)

        array = np.random.rand(shape[0], shape[1]) * noiseAmp

        array[1 * dx:3 * dx, 2 * dy:4 * dy] += triangle
        array[5 * dx:7 * dx, 1 * dy:3 * dy] += triangle * -1

        array[2 * dx:4 * dx, 7 * dy:9 * dy] += np.tril(square, +1)

        array[6 * dx:8 * dx, 5 * dy:7 * dy] += square
        array[7 * dx:9 * dx, 6 * dy:8 * dy] += square * -1

        return array

    elif imagetype == 'NormalDist':

        FWHM_x, FWHM_y = 1.0, 1.0

        if 'FWHM_x' in kwargs:
            FWHM_x = kwargs['FWHM_x']
        if 'FWHM_y' in kwargs:
            FWHM_y = kwargs['FWHM_y']

        x, y = np.mgrid[-1:1:1j * shape[0], -1:1:1j * shape[1]]

        return np.exp(-((x/FWHM_x*2.3548200)**2 +
                        (y/FWHM_y*2.3548200)**2)/2)  # sigma for FWHM = 1

    else:
        print_color("ERROR: image type invalid: " + str(imagetype))

        return np.random.random(shape)


# noinspection PyClassHasNoInit,PyShadowingNames
def graphical_roi_idx(zmatrix, verbose=False, kargs4graph={}):
    """
    Function to define a rectangular region of interest (ROI) in an image.

    The image is plotted and, using the mouse, the user select the region of
    interest (ROI). The ROI is ploted as an transparent rectangular region.
    When the image is closed the function returns the indexes
    ``[i_min, i_max, j_min, j_max]`` of the ROI.

    Parameters
    ----------

    input_array : ndarray
    verbose : Boolean
        In the verbose mode it is printed some additional infomations,
        like the ROI indexes, as the user select different ROI's
    **kargs4graph :
        Options for the main graph. **WARNING:** not tested very well

    Returns
    -------

    list:
        indexes of the ROI ``[i_min, i_max, j_min,_j_max]``.
        Useful when the same crop must be applies to other images

    Note
    ----
    In principle it has no limit of the number of dimensions.


    Example
    -------
    See example at :py:func:`wavepy:utils:crop_graphic`


    See Also
    --------
    :py:func:`wavepy:utils:crop_graphic`
    """

    from matplotlib.widgets import RectangleSelector

    mutable_object_ROI = {'ROI_j_lim': [0, -1],
                          'ROI_i_lim': [0, -1]}

    def onselect(eclick, erelease):
        """eclick and erelease are matplotlib events at press and release"""

        ROI_j_lim = np.sort([eclick.xdata,
                             erelease.xdata]).astype(int).tolist()
        ROI_i_lim = np.sort([eclick.ydata,
                             erelease.ydata]).astype(int).tolist()
        # this round method has
        # an error of +-1pixel

        # if verbose: print(type(eclick.xdata))

        mutable_object_ROI['ROI_j_lim'] = [ROI_j_lim[0], ROI_j_lim[1]]
        mutable_object_ROI['ROI_i_lim'] = [ROI_i_lim[0], ROI_i_lim[1]]

        if verbose:
            print('\nSelecting ROI:')
            print(' lower position : (%d, %d)' % (ROI_j_lim[0], ROI_i_lim[0]))
            print(' higher position   : (%d, %d)' % (ROI_j_lim[1],
                                                     ROI_i_lim[1]))
            print(' width x and y: (%d, %d)' %
                  (ROI_j_lim[1] - ROI_j_lim[0], ROI_i_lim[1] - ROI_i_lim[0]))

        if eclick.button == 1:

            delROIx = ROI_j_lim[1] - ROI_j_lim[0]
            delROIy = ROI_i_lim[1] - ROI_i_lim[0]

            plt.xlim(ROI_j_lim[0] - .2 * delROIx,
                     ROI_j_lim[1] + .2 * delROIx)
            plt.ylim(ROI_i_lim[1] + .2 * delROIy,
                     ROI_i_lim[0] - .2 * delROIy)

        elif eclick.button == 2:
            plt.xlim(0, np.shape(zmatrix)[1])
            plt.ylim(np.shape(zmatrix)[0], 0)

        elif eclick.button == 3:

            delROIx = ROI_j_lim[1] - ROI_j_lim[0]
            delROIy = ROI_i_lim[1] - ROI_i_lim[0]

            plt.xlim(ROI_j_lim[0] - 5 * delROIx,
                     ROI_j_lim[1] + 5 * delROIx)
            plt.ylim(ROI_i_lim[1] + .5 * delROIy,
                     ROI_i_lim[0] - .5 * delROIy)

    class MyRectangleSelector(RectangleSelector):
        def release(self, event):
            super(MyRectangleSelector, self).release(event)
            self.to_draw.set_visible(True)
            self.canvas.draw()

    def toggle_selector(event):
        if verbose:
            print(' Key pressed.')
        if event.key in ['Q', 'q'] and toggle_selector.RS.active:
            if verbose:
                print(' RectangleSelector deactivated.')
            toggle_selector.RS.set_active(False)
        if event.key in ['A', 'a'] and not toggle_selector.RS.active:
            if verbose:
                print(' RectangleSelector activated.')
            toggle_selector.RS.set_active(True)

    fig = plt.figure(facecolor="white",
                     figsize=(10, 8))

    surface = plt.imshow(zmatrix,  # origin='lower',
                         **kargs4graph)

    plt.xlabel('Pixels')
    plt.ylabel('Pixels')
    plt.title('CHOOSE ROI, CLOSE WHEN DONE\n'
              'Middle Click: Reset, \n' +
              'Right Click: select ROI - zoom in,\n' +
              'Left Click: select ROI - zoom out',
              fontsize=16, color='r', weight='bold')
    plt.colorbar(surface)

    toggle_selector.RS = MyRectangleSelector(plt.gca(), onselect,
                                             drawtype='box',
                                             rectprops=dict(facecolor='purple',
                                                            edgecolor='black',
                                                            alpha=0.5,
                                                            fill=True))

    fig.canvas.mpl_connect('key_press_event', toggle_selector)
    plt.show(block=True)

    if verbose:
        print(mutable_object_ROI['ROI_i_lim'] +
              mutable_object_ROI['ROI_j_lim'])

    return mutable_object_ROI['ROI_i_lim'] + \
        mutable_object_ROI['ROI_j_lim']

    #  Note that the + signal concatenates the two lists


def crop_graphic(xvec=None, yvec=None, zmatrix=None,
                 verbose=False, kargs4graph={}):
    """

    Function to crop an image to the ROI selected using the mouse.

    :py:func:`wavepy.utils.graphical_roi_idx` is first used to plot and select
    the ROI. The function then returns the croped version of the matrix, the
    cropped coordinate vectors ``x`` and  ``y``, and the
    indexes ``[i_min, i_max, j_min,_j_max]``

    Parameters
    ----------
    xvec, yvec: 1D ndarray
        vector with the coordinates ``x`` and ``y``. See below how the returned
        variables change dependnding whether these vectors are provided.
    zmatrix: 2D numpy array
        image to be croped, as an 2D ndarray
    **kargs4graph:
        kargs for main graph

    Returns
    -------
    1D ndarray, 1D ndarray:
        cropped coordinate vectors ``x`` and  ``y``. These two vectors are
        only returned the input vectors ``xvec`` and ``xvec`` are provided

    2D ndarray:
        cropped image
    list:
        indexes of the crop ``[i_min, i_max, j_min,_j_max]``. Useful when the
        same crop must be applies to other images

    Examples
    --------

    >>> import numpy as np
    >>> import matplotlib as plt
    >>> xVec = np.arange(0.,101)
    >>> yVec = np.arange(0.,101)
    >>> img = dummy_images('Shapes', size=(101,101), FWHM_x = .5, FWHM_y=1.0)
    >>> (imgCroped, idx4crop) = crop_graphic(zmatrix=img)
    >>> plt.imshow(imgCroped, cmap='Spectral')
    >>> (xVecCroped,
    >>>  yVecCroped,
    >>>  imgCroped, idx4crop) = crop_graphic(xVec, yVec, img)
    >>> plt.imshow(imgCroped, cmap='Spectral',
    >>>            extent=np.array([xVecCroped[0], xVecCroped[-1],
    >>>                             yVecCroped[0], yVecCroped[-1]])


    .. image:: img/graphical_roi_idx_in_action.gif
       :width: 350px

    See Also
    --------
    :py:func:`wavepy.utils.crop_graphic_image`
    :py:func:`wavepy.utils.graphical_roi_idx`
    """

    idx = graphical_roi_idx(zmatrix, verbose=verbose, kargs4graph=kargs4graph)

    if xvec is None or yvec is None:
        return crop_matrix_at_indexes(zmatrix, idx), idx

    else:
        return xvec[idx[2]:idx[3]], \
               yvec[idx[0]:idx[1]], \
               crop_matrix_at_indexes(zmatrix, idx), idx


def crop_graphic_image(image, verbose=False, **kargs4graph):
    """

    Similar to :py:func:`wavepy.utils.crop_graphic`, but only for the
    main matrix (and not for the x and y vectors). The function then returns
    the croped version of the image and
    the indexes ``[i_min, i_max, j_min,_j_max]``

    Parameters
    ----------
    zmatrix: 2D numpy array
        image to be croped, as an 2D ndarray

    **kargs4graph:
        kargs for main graph

    Returns
    -------
    2D ndarray:
        cropped image
    list:
        indexes of the crop ``[i_min, i_max, j_min,_j_max]``. Useful when
        the same crop must be applies to other images

    See Also
    --------
    :py:func:`wavepy.utils.crop_graphic`
    :py:func:`wavepy.utils.graphical_roi_idx`
    """

    idx = graphical_roi_idx(image, verbose=verbose, **kargs4graph)

    return crop_matrix_at_indexes(image, idx), idx


def pad_to_make_square(array, mode, **kwargs):
    '''
    #TODO: write docs
    '''

    diff_size = array.shape[0] - array.shape[1]

    if diff_size > 0:

        print(diff_size)
        return np.pad(array, ((0, 0),
                              (diff_size//2, diff_size - diff_size//2)),
                      mode, **kwargs)

    elif diff_size < 0:
        print(diff_size)
        return np.pad(array, ((-diff_size//2,
                               -diff_size + diff_size//2), (0, 0)),
                      mode, **kwargs)
    else:
        return array


def graphical_select_point_idx(zmatrix, verbose=False, kargs4graph={}):
    """

    Plot a 2D array and allow to pick a point in the image. Returns the last
    selected position x and y of the choosen point


    Parameters
    ----------
    zmatrix: 2D numpy array
        main image

    verbose: Boolean
        verbose mode

    **kargs4graph:
        kargs for main graph

    Returns
    -------
    int, int:
        two integers with the point indexes ``x`` and ``y``

    Example
    -------
    >>> jo, io = graphical_select_point_idx(array2D)
    >>> value = array2D[io, jo]

    See Also
    --------
    :py:func:`wavepy.utils.graphical_roi_idx`


    """

    from matplotlib.widgets import Cursor

    fig = plt.figure(facecolor="white",
                     figsize=(10, 8))

    surface = plt.imshow(zmatrix,  # origin='lower',
                         cmap='spectral', **kargs4graph)
    plt.autoscale(False)

    ax1, = plt.plot(zmatrix.shape[1]//2, zmatrix.shape[0]//2,
                    'r+', ms=30, picker=10)

    plt.grid()
    plt.xlabel('Pixels')
    plt.ylabel('Pixels')
    plt.title('CHOOSE POINT, CLOSE WHEN DONE\n' +
              'Middle Click: Select point\n',
              fontsize=16, color='r', weight='bold')
    plt.colorbar(surface)

    mutable_object_xy = {'xo': np.nan,
                         'yo': np.nan}

    def onclick(event):
        if event.button == 2:
            xo, yo = event.xdata, event.ydata

            ax1.set_xdata(xo)
            ax1.set_ydata(yo)
            plt.title('SELECT ROI, CLOSE WHEN DONE\n' +
                      'Middle Click: Select point\n' +
                      'x: {:.0f}, y: {:.0f}'.format(xo, yo),
                      fontsize=16, color='r', weight='bold')

            if verbose:
                print('x: {:.3f}, y: {:.3f}'.format(xo, yo))

            mutable_object_xy['xo'] = xo
            mutable_object_xy['yo'] = yo

        if event.button == 3:
            print('Hi')
            plt.lines = []
            plt.legend_ = None
            plt.draw()

    cursor = Cursor(plt.gca(), useblit=True, color='red', linewidth=2)
    fig.canvas.mpl_connect('button_press_event', onclick)
    plt.show(block=True)

    if mutable_object_xy['xo'] is np.nan:
        return None, None
    else:
        return int(mutable_object_xy['xo']), int(mutable_object_xy['yo'])


def plot_slide_colorbar(zmatrix, title='',
                        xlabel='', ylabel='',
                        cmin_o=None,
                        cmax_o=None,
                        **kwargs4imshow):
    '''
    TODO: Write docstring
    '''

    zmatrix = zmatrix.astype(float)
    # avoid problems when masking integer
    # images. necessary because integer NAN doesn't exist

    fig, ax = plt.subplots(figsize=(10, 9))
    plt.subplots_adjust(left=0.25, bottom=0.25)

    surf = plt.imshow(zmatrix, cmap='viridis', **kwargs4imshow)
    plt.title(title, fontsize=14, weight='bold')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    fig.colorbar(surf)

    axcmin = plt.axes([0.25, 0.1, 0.65, 0.03])
    axcmax = plt.axes([0.25, 0.15, 0.65, 0.03])

    if cmin_o is None:
        cmin_o = surf.get_clim()[0]

    if cmax_o is None:
        cmax_o = surf.get_clim()[1]

    min_slider_val = (9*cmin_o - cmax_o)/8
    max_slider_val = (9*cmax_o - cmin_o)/8

    scmin = Slider(axcmin, 'Min',
                   min_slider_val, max_slider_val,
                   valinit=cmin_o)
    scmax = Slider(axcmax, 'Max',
                   min_slider_val, max_slider_val,
                   valinit=cmax_o)

    resetax = plt.axes([0.8, 0.015, 0.1, 0.04])
    button = Button(resetax, 'Reset', hovercolor='0.975')

    cmapax = plt.axes([0.025, 0.2, 0.15, 0.25])
    radio1 = RadioButtons(cmapax, ('gray', 'gray_r',
                                   'viridis', 'viridis_r',
                                   'inferno', 'rainbow'), active=2)

    powax = plt.axes([0.025, 0.7, 0.15, 0.15])
    radio2 = RadioButtons(powax, ('lin', 'pow 1/7', 'pow 1/3',
                                  'pow 3', 'pow 7'), active=0)

    sparkax = plt.axes([0.025, 0.5, 0.15, 0.15])
    radio3 = RadioButtons(sparkax, ('none', 'sigma = 1',
                                    'sigma = 3', 'sigma = 5'), active=0)

    def update(val):
        cmin = scmin.val
        cmax = scmax.val

        if cmin < cmax:
            scmin.label.set_text('Min')
            scmax.label.set_text('Max')
        else:
            scmin.label.set_text('Max')
            scmax.label.set_text('Min')

        surf.set_clim(cmax, cmin)

        fig.canvas.draw_idle()

    scmin.on_changed(update)
    scmax.on_changed(update)

    def reset(event):
        scmin.set_val(cmin_o)
        scmax.set_val(cmax_o)
        scmin.reset()
        scmax.reset()
    button.on_clicked(reset)

    def colorfunc(label):
        surf.set_cmap(label)
        fig.canvas.draw_idle()
    radio1.on_clicked(colorfunc)

    def lin_or_pow(label):
        radio3.set_active(0)
        filter_sparks('none')
        if label == 'lin':
            n = 1
        elif label == 'pow 1/3':
            n = 1/3
        elif label == 'pow 1/7':
            n = 1/7
        elif label == 'pow 3':
            n = 3
        elif label == 'pow 7':
            n = 7

        zmatrix_2plot = ((zmatrix-zmatrix.min())**n*np.ptp(zmatrix) /
                         np.ptp(zmatrix)**n + zmatrix.min())
        surf.set_data(zmatrix_2plot)
        fig.canvas.draw_idle()

    radio2.on_clicked(lin_or_pow)

    def filter_sparks(label):
        zmatrix_2plot = surf.get_array().data
        if label == 'none':
            reset(None)
            return
        elif label == 'sigma = 1':
            sigma = 1
        elif label == 'sigma = 3':
            sigma = 3
        elif label == 'sigma = 5':
            sigma = 5

        scmin.set_val(mean_plus_n_sigma(zmatrix_2plot, -sigma))
        scmax.set_val(mean_plus_n_sigma(zmatrix_2plot, sigma))
        surf.set_clim(mean_plus_n_sigma(zmatrix_2plot, -sigma),
                      mean_plus_n_sigma(zmatrix_2plot, sigma))

    radio3.on_clicked(filter_sparks)

    plt.show(block=True)

    return [[scmin.val, scmax.val], radio1.value_selected]


def save_figs_with_idx(patternforname='graph', extension='png'):
    '''
    Use a counter to save the figures with suffix 1, 2, 3, ..., etc

    Parameters
    ----------

    str: patternforname
        Prefix for file name. Accept directories path.

    str: extension
        Format extension to save the figure. For file formats see
        `:py:func:matplotlib.pyplot.savefig`


    '''

    figname = get_unique_filename(patternforname, extension)
    plt.savefig(figname)
    print('MESSAGE: ' + figname + ' SAVED')


def save_figs_with_idx_pickle(figObj, patternforname='graph'):
    '''
    Save figures as pickle. It uses a counter to save the figures with
    suffix 1, 2, 3, ..., etc, to avoid overwriting existing files.

    Parameters
    ----------

    figObj: matplotlib figure object
        Figure to be pickled

    str: patternforname
        Prefix for file name. Accept directories path.


    Notes
    -----

    Save matplotlib figures to pickle. Note that not all types of graphs are
    fully supported. It can load most types of graphs, but it can only extract
    the functions of few types. It works well with plot and with
    :py:func:`plt.plot()` and :py:func:`plt.imshow()`

    '''

    if '_figCount_pickle' not in globals():

            from itertools import count
            global _figCount_pickle
            _figCount_pickle = count()
            next(_figCount_pickle)

    figname = str('{:s}_{:02d}.pickle'.format(patternforname,
                                              next(_figCount_pickle)))

    while os.path.isfile(figname):
        figname = str('{:s}_{:02d}.pickle'.format(patternforname,
                                                  next(_figCount_pickle)))

    pl.dump(figObj, open(figname, 'wb'))

    print('MESSAGE: ' + figname + ' SAVED')


def get_unique_filename(patternforname, extension='txt'):
    '''
    Produce a string in the format `patternforname_XX.extension`, where XX is
    the smalest number in order that the string is a unique filename.

    Parameters
    ----------

    patternforname: str
        Main part of the filename. Accept directories path.

    extension: str
        Sufix for file name.


    Notes
    -----

    This will just return the filename, it will not create any file.

    '''

    if '.' not in extension:
        extension = '.' + extension

    from itertools import count
    _Count_fname = count()
    next(_Count_fname)

    fname = str('{:s}_{:02d}'.format(patternforname,
                                      next(_Count_fname)) + extension)

    while os.path.isfile(fname):
        fname = str('{:s}_{:02d}'.format(patternforname,
                                          next(_Count_fname)) + extension)

    return fname


def rotate_img_graphical(array2D, order=1, mode='constant', verbose=False):
    '''
    GUI to rotate an image
    #TODO: Write this documentations!

    Parameters
    ----------
    order: int
        The order of the spline interpolation

    mode
        : {'constant', 'edge', 'symmetric', 'reflect', 'wrap'}, optional
        Points outside the boundaries of the input are filled according to
        the given mode. Modes match the behaviour of numpy.pad.


    Returns
    -------
    2D ndarray:
        cropped image
    list:
        indexes of the crop ``[i_min, i_max, j_min,_j_max]``. Useful
        when the same crop must be applies to other images

    Example
    -------

    >>> img = wpu.dummy_images('Shapes', noise=0)
    >>> img_rotated, angle = wpu.rotate_img_graphical(img)
    >>> plt.imshow(img_rotated, cmap='spectral_r', vmin=-10)

    See Also
    --------
    :py:func:`wavepy.utils.crop_graphic`
    :py:func:`wavepy.utils.graphical_roi_idx`
    '''

    import skimage.transform

    rot_ang = 0.0
    _array2D = np.copy(array2D)

    while 1:
        jo, io = graphical_select_point_idx(_array2D, verbose)

        if np.isnan(jo):
            break

        rot_ang += np.arctan2(array2D.shape[0]//2 - io,
                              jo - array2D.shape[1]//2)*rad2deg
        rot_ang = rot_ang % 360

        if verbose:

            print(jo)
            print(io)
            print('Rot Angle = {:.3f} deg'.format(rot_ang))

        _array2D = skimage.transform.rotate(array2D, -rot_ang,
                                            mode=mode, order=order)

    return skimage.transform.rotate(array2D, -rot_ang,
                                    mode=mode, order=order), rot_ang


def choose_unit(array):
    """

    Script to choose good(best) units in engineering notation
    for a ``ndarray``.

    For a given input array, the function returns ``factor`` and ``unit``
    according to

    .. math:: 10^{n} < \max(array) < 10^{n + 3}

    +------------+----------------------+------------------------+
    |     n      |    factor (float)    |        unit(str)       |
    +============+======================+========================+
    |     0      |    1.0               |   ``''`` empty string  |
    +------------+----------------------+------------------------+
    |     -9     |    10^-9             |        ``n``           |
    +------------+----------------------+------------------------+
    |     -6     |    10^-6             |     ``r'\mu'``         |
    +------------+----------------------+------------------------+
    |     -3     |    10^-3             |        ``m``           |
    +------------+----------------------+------------------------+
    |     +3     |    10^-6             |        ``k``           |
    +------------+----------------------+------------------------+
    |     +6     |    10^-9             |        ``M``           |
    +------------+----------------------+------------------------+
    |     +9     |    10^-6             |        ``G``           |
    +------------+----------------------+------------------------+

    ``n=-6`` returns ``\mu`` since this is the latex syntax for micro.
    See Example.


    Parameters
    ----------
    array : ndarray
        array from where to choose proper unit.

    Returns
    -------
    float, unit :
        Multiplication Factor and strig for unit

    Example
    -------

    >>> array1 = np.linspace(0,100e-6,101)
    >>> array2 = array1*1e10
    >>> factor1, unit1 = choose_unit(array1)
    >>> factor2, unit2 = choose_unit(array2)
    >>> plt.plot(array1*factor1,array2*factor2)
    >>> plt.xlabel(r'${0} m$'.format(unit1))
    >>> plt.ylabel(r'${0} m$'.format(unit2))

    The syntax ``r'$ string $ '`` is necessary to use latex commands in the
    :py:mod:`matplotlib` labels.

    """

    max_abs = np.max(np.abs(array))

    if 2e0 < max_abs <= 2e3:
        factor = 1.0
        unit = ''
    elif 2e-9 < max_abs <= 2e-6:
        factor = 1.0e9
        unit = 'n'
    elif 2e-6 < max_abs <= 2e-3:
        factor = 1.0e6
        unit = r'\mu'
    elif 2e-3 < max_abs <= 2e0:
        factor = 1.0e3
        unit = 'm'
    elif 2e3 < max_abs <= 2e6:
        factor = 1.0e-3
        unit = 'k'
    elif 2e6 < max_abs <= 2e9:
        factor = 1.0e-6
        unit = 'M'
    elif 2e9 < max_abs <= 2e12:
        factor = 1.0e-6
        unit = 'G'
    else:
        factor = 1.0
        unit = ''

    return factor, unit


# time functions
def datetime_now_str():
    """
    Returns the current date and time as a string in the format YYmmDD_HHMMSS.
    Alias for ``time.strftime("%Y%m%d_%H%M%S")``.

    Return
    ------
    str

    """

    from time import strftime

    return strftime("%Y%m%d_%H%M%S")


def time_now_str():
    """
    Returns the current time as a string in the format HHMMSS. Alias
    for ``time.strftime("%H%M%S")``.

    Return
    ------
    str

    """
    from time import strftime

    return strftime("%H%M%S")


def date_now_str():
    """
    Returns the current date as a string in the format YYmmDD. Alias
    for ``time.strftime("%Y%m%d")``.

    Return
    ------
    str

    """
    from time import strftime

    return strftime("%Y%m%d")


# coordinates in real and kspace.

def realcoordvec(npoints, delta):
    """
    Build a vector with real space coordinates based on the number of points
    and bin (pixels) size.

    Alias for ``np.mgrid[-npoints/2*delta:npoints/2*delta-delta:npoints*1j]``

    Parameters
    ----------
    npoints : int
        number of points
    delta : float
        vector with the values of x

    Returns
    -------
    ndarray
        vector (1D array) with real coordinates

    Example
    -------
    >>> realcoordvec(10,1)
    array([-5., -4., -3., -2., -1.,  0.,  1.,  2.,  3.,  4.])

    See Also
    --------
    :py:func:`wavepy.utils.realcoordmatrix_fromvec`
    :py:func:`wavepy.utils.realcoordmatrix`

    """
    #    return np.mgrid[-npoints/2.*delta:npoints/2.*delta:npoints*1j]

    return (np.linspace(1, npoints, npoints) - npoints//2 - 1) * delta


def realcoordmatrix_fromvec(xvec, yvec):
    """
    Alias for ``np.meshgrid(xvec, yvec)``

    Parameters
    ----------
    xvec, yvec : ndarray
        vector (1D array) with real coordinates

    Returns
    -------
    ndarray
        2 matrices (1D array) with real coordinates

    Example
    -------

    >>> vecx = realcoordvec(3,1)
    >>> vecy = realcoordvec(4,1)
    >>> realcoordmatrix_fromvec(vecx, vecy)
    [array([[-1.5, -0.5,  0.5],
    [-1.5, -0.5,  0.5],
    [-1.5, -0.5,  0.5],
    [-1.5, -0.5,  0.5]]),
    array([[-2., -2., -2.],
    [-1., -1., -1.],
    [ 0.,  0.,  0.],
    [ 1.,  1.,  1.]])]


    See Also
    --------
    :py:func:`wavepy.utils.realcoordvec`
    :py:func:`wavepy.utils.realcoordmatrix`

    """
    return np.meshgrid(xvec, yvec)


def realcoordmatrix(npointsx, deltax, npointsy, deltay):
    """
    Build a matrix (2D array) with real space coordinates based on the number
    of points and bin (pixels) size.

    Alias for
    ``realcoordmatrix_fromvec(realcoordvec(nx, delx), realcoordvec(ny, dely))``

    Parameters
    ----------
    npointsx, npointsy : int
        number of points in the x and y directions
    deltax, deltay : float
        step size in the x and y directions

    Returns
    -------
    ndarray, ndarray
        2 matrices (2D array) with real coordinates

    Example
    -------

    >>> realcoordmatrix(3,1,4,1)
    [array([[-1.5, -0.5,  0.5], [-1.5, -0.5,  0.5], [-1.5, -0.5,  0.5],
    [-1.5, -0.5,  0.5]]), array([[-2., -2., -2.], [-1., -1., -1.],
    [ 0.,  0.,  0.], [ 1.,  1.,  1.]])]

    See Also
    --------
    :py:func:`wavepy.utils.realcoordvec`
    :py:func:`wavepy.utils.realcoordmatrix_fromvec`

    """
    return realcoordmatrix_fromvec(realcoordvec(npointsx, deltax),
                                   realcoordvec(npointsy, deltay))


def grid_coord(array2D, pixelsize):

    if isinstance(pixelsize, float):
        pixelsize = [pixelsize, pixelsize]

    return realcoordmatrix(array2D.shape[1], pixelsize[1],
                           array2D.shape[0], pixelsize[0])


def reciprocalcoordvec(npoints, delta):
    """
    Create coordinates in the (spatial) frequency domain based on the number of
    points ``n`` and the step (binning) ``\Delta x`` in the **REAL SPACE**. It
    returns a vector of frequencies with values in the interval


    .. math:: \\left[ \\frac{-1}{2 \\Delta x} : \\frac{1}{2 \\Delta x} - \\frac{1}{n \\Delta x} \\right],


    with the same number of points.

    Parameters
    ----------
    npoints : int
        number of points
    delta : float
        step size in the **REAL SPACE**

    Returns
    -------
    ndarray


    Example
    -------

    >>> reciprocalcoordvec(10,1e-3)
    array([-500., -400., -300., -200., -100., 0., 100., 200., 300., 400.])

    See Also
    --------
    :py:func:`wavepy.utils.realcoordvec`
    :py:func:`wavepy.utils.reciprocalcoordmatrix`

    """

    return (np.linspace(0, 1, npoints, endpoint=False) - .5)/delta


def reciprocalcoordmatrix(npointsx, deltax, npointsy, deltay):
    """

    Similar to :py:func:`wavepy.utils.reciprocalcoordvec`, but for matrices
    (2D arrays).

    Parameters
    ----------
    npointsx, npointsy : int
        number of points in the x and y directions
    deltax, deltay : float
        step size in the x and y directions

    Returns
    -------
    ndarray, ndarray
        2 matrices (2D array) with coordinates in the frequencies domain

    Example
    -------

    >>> reciprocalcoordmatrix(5, 1e-3, 4, 1e-3)
    [array([[-500., -300., -100.,  100.,  300.],
    [-500., -300., -100.,  100.,  300.],
    [-500., -300., -100.,  100.,  300.],
    [-500., -300., -100.,  100.,  300.]]),
    array([[-500., -500., -500., -500., -500.],
    [-250., -250., -250., -250., -250.],
    [   0.,    0.,    0.,    0.,    0.],
    [ 250.,  250.,  250.,  250.,  250.]])]

    See Also
    --------
    :py:func:`wavepy.utils.realcoordmatrix`
    :py:func:`wavepy.utils.reciprocalcoordvec`
    """
    return np.meshgrid(reciprocalcoordvec(npointsx, deltax),
                       reciprocalcoordvec(npointsy, deltay))


def fouriercoordvec(npoints, delta):
    '''
    For back compability
    '''
    return reciprocalcoordvec(npoints, delta)


def fouriercoordmatrix(npointsx, deltax, npointsy, deltay):
    '''
    For back compability
    '''
    return reciprocalcoordmatrix(npointsx, deltax, npointsy, deltay)


# h5 tools
def h5_list_of_groups(h5file):
    """

    Get the names of all groups and subgroups in a hdf5 file.

    Parameters
    ----------
    h5file : h5py file


    Return
    ------
    list
        list of strings with group names

    Example
    -------


    >>> fh5 = h5py.File(filename,'r')
    >>> listOfGoups = h5_list_of_groups(fh5)
    >>> for group in listOfGoups: print(group)

    """

    list_of_goups = []
    h5file.visit(list_of_goups.append)

    return list_of_goups

# Progress bar


def progress_bar4pmap(res, sleep_time=1.0):
    """
    Progress bar from :py:mod:`tqdm` to be used with the function
    :py:func:`multiprocessing.starmap_async`.

    It holds the program in a loop waiting
    :py:func:`multiprocessing.starmap_async` to finish


    Parameters
    ----------

    res: result object of the :py:class:`multiprocessing.Pool` class
    sleep_time:


    Example
    -------

    >>> from multiprocessing import Pool
    >>> p = Pool()
    >>> res = p.starmap_async(...)  # use your function inside brackets
    >>> p.close()  # No more work
    >>> progress_bar4pmap(res)

    """

    old_res_n_left = res._number_left
    pbar = tqdm(total=old_res_n_left)

    while res._number_left > 0:
        if old_res_n_left != res._number_left:
            pbar.update(old_res_n_left - res._number_left)
            old_res_n_left = res._number_left
        time.sleep(sleep_time)

    pbar.close()
    print('')


def load_ini_file_terminal_dialog(inifname):
    """

    This function make use of `configparser
    <https://docs.python.org/3.5/library/configparser.html>`_ to set and get
    default optiona in a ``*.ini`` file.

    It is a terminal dialog that goes trough all key parameters in the
    ``ini`` file, ask if a value must be changed, ask the new value
    and update it in the ``ini`` file.

    Note that this function first update the ``ini`` file and then return the
    updated paramenters.

    The ``ini`` file must contain two sections: ``Files`` and ``Parameters``.
    The ``Files`` section list all files to be loaded. If you don't accept the
    default value that it is offered, it will run
    :py:func:`wavepy.utils.select_file` to select other file.

    The section ``Parameters`` can contain anything, in any format, but keep in
    mind that they are passed as string.


    Parameters
    ----------
    inifname : str
        name of the ``*.ini`` file.

    Return
    ------
    configparser object, configparser object, configparser object
        main configparser objects, configparser objects under
        section ``Parameters``, configparser objects under section ``Files``


    Examples
    --------

    Example of ``ini`` file::

        [Files]
        image_filename = file1.tif
        ref_filename = file2.tif

        [Parameters]
        par1 = 10.5e-5
        par2 = 10, 100, 500, 600
        par can have long name = 25
        par3 = the value can be anything



    Note that ``load_ini_file`` first set/update the parameters in the file,
    and we need to load each parameters afterwards:

    >>> ini_pars, ini_file_list = load_ini_file('configfile.ini')
    >>> par1 = float(ini_pars.get('par1'))
    >>> par2 = list(map(int, ini_pars.get('par2').split(',')))


    See Also
    --------
    :py:func:`wavepy.utils.load_ini_file`,
    :py:func:`wavepy.utils.get_from_ini_file`,
    :py:func:`wavepy.utils.set_at_ini_file`.

    """

    if not os.path.isfile(inifname):
        raise Exception("File " + inifname + " doesn't exist. You must " +
                        "create your init file first.")

    config = configparser.ConfigParser()
    config.read(inifname)

    print('\nMESSAGE: All sections and keys:')
    for sections in config.sections():
        print_red(sections)
        for key in config[sections]:
            print_blue('  ' + key + ':\t ' +
                       config[sections].get(key))

    ini_pars = config['Parameters']
    ini_file_list = config['Files']

    use_last_value = input('\nUse last values? [Y/n]: ')

    if use_last_value.lower() == 'n':

        for ftype in ini_file_list:
            kb_input = input('\nUse ' + ini_file_list.get(ftype) + ' as ' +
                             ftype + '? [Y/n]: ')
            if kb_input.lower() == 'n':
                patternForGlob = ('**/*.' +
                                  ini_file_list.get(ftype).split('.')[1])

                _filename = select_file(patternForGlob)
                if _filename[0] != '/':
                    _filename = os.getcwd() + '/' + _filename
                ini_file_list[ftype] = _filename

        for key in ini_pars:
            kb_input = input('\nEnter ' + key + ' value [' +
                             ini_pars.get(key) + '] : ')
            ini_pars[key] = kb_input or ini_pars[key]

        with open(inifname, 'w') as configfile:
            config.write(configfile)

    else:
        print('MESSAGE: Using values from ' + inifname)

    return config, ini_pars, ini_file_list


def load_ini_file(inifname):
    '''

    Parameters
    ----------
    inifname: str
        name of the ``*.ini`` file.

    Returns
    -------
    configparser objects


    Example
    -------

    Example of ``ini`` file::

        [Files]
        image_filename = file1.tif
        ref_filename = file2.tif

        [Parameters]
        par1 = 10.5e-5
        par2 = 10, 100, 500, 600
        par can have long name = 25
        par3 = the value can be anything

    If we create a file named ``.temp.ini`` with the example above, we can load
    it as:

    >>> config = load_ini_file('.temp.ini')
    >>> print(config['Parameters']['Par1'] )



    See Also
    --------
    :py:func:`wavepy.utils.load_ini_file_terminal_dialog`,
    :py:func:`wavepy.utils.get_from_ini_file`,
    :py:func:`wavepy.utils.set_at_ini_file`.


    '''

    if not os.path.isfile(inifname):
        raise Warning("File " + inifname + " doesn't exist. You must " +
                      "create your init file first.")
        return None

    config = configparser.ConfigParser()
    config.read(inifname)

    return config


def get_from_ini_file(inifname, section, key):

    '''

    Parameters
    ----------
    inifname: str
        name of the ``*.ini`` file.

    section: str
        section where key is placed


    key: str
        key from where to get the value(s)


    Returns
    -------
    str
        value of the ``configparser['section']['key']``

    Example
    -------

    Example of ``ini`` file::

        [Files]
        image_filename = file1.tif
        ref_filename = file2.tif

        [Parameters]
        par1 = 10.5e-5
        par2 = 10, 100, 500, 600
        par can have long name = 25
        par3 = the value can be anything


    If we create a file named ``.temp.ini`` with the example above, we can load
    it as:

    >>> inifname = '.temp.ini'
    >>> par = get_from_ini_file(inifname, 'Parameters','Par1')
    >>> print(par)


    See Also
    --------
    :py:func:`wavepy.utils.load_ini_file_terminal_dialog`,
    :py:func:`wavepy.utils.load_ini_file`,
    :py:func:`wavepy.utils.set_at_ini_file`.


    '''

    if not os.path.isfile(inifname):
        raise Warning("File " + inifname + " doesn't exist. You must " +
                      "create your init file first.")
        return None, None

    config = configparser.ConfigParser()
    config.read(inifname)

    return config[section][key]


def set_at_ini_file(inifname, section, key, value):

    '''

    Parameters
    ----------
    inifname: str
        name of the ``*.ini`` file.

    section: str
        section where the key is placed


    key: str
        key to set the value(s)


    Example
    -------
    >>> inifname = '.temp.ini'
    >>> par = set_at_ini_file(inifname, 'Parameters','Par1')


    See Also
    --------
    :py:func:`wavepy.utils.load_ini_file_terminal_dialog`,
    :py:func:`wavepy.utils.load_ini_file`,
    :py:func:`wavepy.utils.get_from_ini_file`.

    '''

    if not os.path.isfile(inifname):
        raise Warning("File " + inifname + " doesn't exist. You must " +
                      "create your init file first.")
        return None, None

    config = configparser.ConfigParser()
    config.read(inifname)

    config[section][key] = str(value)

    with open(inifname, 'w') as configfile:
        config.write(configfile)


def log_this(text='', preffname='', inifname=''):
    '''
    Write a variable to the log file. Creates one if there isn't one.

    Parameters
    ----------
    text: str
        text to be appended to the log file

    inifname: str
        (Optional) name of the inifile to be attached to the log.


    '''

    if 'logfilename' not in globals():

        if preffname == '':

            global logfilename
            from inspect import currentframe, getframeinfo

            cf = currentframe().f_back
            logfilename = (getframeinfo(cf).filename[:-3] +
                           '_' + datetime_now_str() + '.log')

        else:
            logfilename = (preffname +
                           '_' + datetime_now_str() + '.log')

        print_blue('MESSAGE: LOGFILE name: ' + logfilename)

    if text != '':
        with open(logfilename, 'a') as file:
            file.write(text + '\n')

    if os.path.isfile(inifname):

        with open(logfilename, 'a') as outfile:
            with open(inifname, 'r') as file1:
                outfile.write('\n\n##### START .ini file\n')
                outfile.write(file1.read())
                outfile.write('\n##### END .ini file\n\n\n')

    elif inifname == '':
        print_blue('LOG MESSAGE: ' + text)

    else:
        print_red('WARNING: inifname DOESNT exist.')


def fourier_spline_1d(vec1d, n=2):

    # reflec pad to avoid discontinuity at the edges
    pad_vec1d = np.pad(vec1d, (0, vec1d.shape[0]), 'reflect')

    fftvec = np.fft.fftshift(np.fft.fft(pad_vec1d))

    fftvec = np.pad(fftvec, pad_width=fftvec.shape[0]*(n-1)//2,
                    mode='constant', constant_values=0.0)

    res = np.fft.ifft(np.fft.ifftshift(fftvec))*n

    return res[0:res.shape[0]//2]


def fourier_spline_2d_axis(array, n=2, axis=0):

    # reflec pad to avoid discontinuity at the edges

    if axis == 0:
        padwidth = ((0, array.shape[0]), (0, 0))
    elif axis == 1:
        padwidth = ((0, 0), (0, array.shape[1]))

    pad_array = np.pad(array, pad_width=padwidth, mode='reflect')

    fftvec = np.fft.fftshift(np.fft.fft(pad_array, axis=axis), axes=axis)

    listpad = [(0, 0), (0, 0)]

    if fftvec.shape[axis]*(n-1) % 2 == 0:
        listpad[axis] = (fftvec.shape[axis]*(n-1)//2,
                         fftvec.shape[axis]*(n-1)//2)
    else:
        listpad[axis] = (fftvec.shape[axis]*(n-1)//2,
                         fftvec.shape[axis]*(n-1)//2 + 1)

    fftvec = np.pad(fftvec, pad_width=listpad,
                    mode='constant', constant_values=0.0)

    res = np.fft.ifft(np.fft.ifftshift(fftvec, axes=axis), axis=axis)*n
    res = np.real(res)

    if axis == 0:
        return res[0:res.shape[0]//2, :]
    elif axis == 1:
        return res[:, 0:res.shape[1]//2]


def fourier_spline_2d(array2d, n=2):

    res = fourier_spline_2d_axis(fourier_spline_2d_axis(array2d,
                                                        n=n, axis=0),
                                 n=n, axis=1)

    return res


def shift_subpixel_1d(array, frac_of_pixel, axis=0):

    if array.ndim == 1:
        return fourier_spline_1d(array, frac_of_pixel)[1::frac_of_pixel]
    elif array.ndim == 2:

        if axis == 0:
            return fourier_spline_2d_axis(array,
                                          frac_of_pixel,
                                          axis=0)[1::frac_of_pixel, :]

        elif axis == 1:
            return fourier_spline_2d_axis(array,
                                          frac_of_pixel,
                                          axis=0)[:, 1::frac_of_pixel]


def shift_subpixel_2d(array2d, frac_of_pixel):

    return fourier_spline_2d(array2d, frac_of_pixel)[1::frac_of_pixel,
                                                     1::frac_of_pixel]


def _mpl_settings_4_nice_graphs(fs=16, fontfamily='Utopia'):
    '''

    Note: a older version used latex. However if you have the fonts
    for Utopia (Regular, Bold and Italic), then latex is not necessary.
    install the fonts somewhere like:
    $CONDA_ENV_DIR/site-packages/matplotlib/mpl-data/fonts/ttf/
    '''

    plt.style.use('default')

    # Direct input

    params = {'font.size': fs,
              'font.family': fontfamily,
              'figure.facecolor': 'white'
              }

    plt.rcParams.update(params)


def rocking_3d_figure(ax, outfname='out.ogv',
                      elevAmp=50, azimAmpl=90,
                      elevOffset=0, azimOffset=0,
                      dpi=50, npoints=200,
                      del_tmp_imgs=True):
    """

    Saves an image at different view angles and join the images
    to make a short animation. The movement is defined by setting the elevation
    and azimut angles following a sine function. The frequency of the vertical
    movement (elevation) is twice of the horizontal (azimute), forming a
    figure eight movement.


    Parameters
    ==========

    ax : 3D axis object
        See example below how to create this object. If `None`, this will use
        the temporary images from a previous run

    outfname : str
        output file name. Note that the extension defines the file format.
        This function has been tested for the formats `.gif` (not recomended,
        big files and poor quality), `.mp4`, `.mkv` and `.ogv`. For
        LibreOffice, `.ogv` is the recomend format.

    elevAmp : float
        amplitude of elevation movement, in degrees

    azimAmpl : float
        amplitude of azimutal movement, in degrees. If negative, the image
        will continually rotate around the azimute direction (no azimute
        rocking)

    elevOffset : float
        offset of elevation movement, in degrees

    azimOffset : float
        offset of azimutal movement, in degrees

    dpi : float
        resolution of the individual images

    npoints : int
        number of intermediary images to form the animation. More images
        will make the the movement slower and the animation longer.

    remove_images : float
        the program creates `npoints` temporary images, and this flag defines
        if these images are deleted or not

    Example
    =======


    >>> fig = plt.figure()
    >>> ax = fig.add_subplot(111, projection='3d')
    >>> xx = np.random.rand(npoints)*2-1
    >>> yy = np.random.rand(npoints)*2-1
    >>> zz = np.sinc(-(xx**2/.5**2+yy**2/1**2))
    >>> ax.plot_trisurf(xx, yy, zz, cmap='viridis', linewidth=0.2, alpha = 0.8)
    >>> plt.show()
    >>> plt.pause(.5)
    >>> # this pause is necessary to plot the first image in the main screen
    >>> rocking_3d_figure(ax, 'out_080.ogv',
                          elevAmp=45, azimAmpl=45,
                          elevOffset=0, azimOffset=45, dpi=80)
    >>> # example of use of the del_tmp_imgs flag
    >>> rocking_3d_figure(ax, 'out_050.ogv',
                          elevAmp=60, azimAmpl=60,
                          elevOffset=10, azimOffset=45,
                          dpi=50, del_tmp_imgs=False)
    >>> rocking_3d_figure(None, 'out2_050.gif',
                          del_tmp_imgs=True)

    """

    if os.name is 'posix':
        pass

    else:
        print_red('ERROR: rocking_3d_figure: ' +
                  'this function is only implemented for Linux')
        return -1

    if shutil.which('ffmpeg') is None:
        print_red('ERROR: rocking_3d_figure: ' +
                  '"ffmpeg" function is no available. ' +
                  'Aborting rocking_3d_figure')
        return -1

    if shutil.which('convert') is None:
        print_red('ERROR: rocking_3d_figure: ' +
                  '"convert" function is no available. ' +
                  'Aborting rocking_3d_figure')
        return -1

    plt.pause(.5)

    outfname = get_unique_filename(outfname.split('.')[0],
                                   outfname.split('.')[-1])

    out_format = outfname.split('.')[-1]

    print_red('WARNING: rocking_3d_figure: making pictures for animation,' +
              ' them main figure will freeze for a while.')

    if ax is not None:
        for ii in np.linspace(0, npoints, npoints, dtype=int):

            text = ax.text2D(0.05, 0.95, str('{:d}/{:d}'.format(ii, npoints)),
                             transform=ax.transAxes)

            if azimAmpl > 0:
                azim = azimOffset + azimAmpl*np.sin(2*np.pi*ii/npoints)
            else:
                azim = azimOffset + 360*ii/npoints

            elev = elevOffset + elevAmp*np.sin(4*np.pi*ii/npoints)

            ax.view_init(elev=elev, azim=azim)

            plt.savefig('.animation_tmp_{:03d}.jpg'.format(ii), dpi=dpi)

            text.remove()
            if ii % 10 == 0:
                print(' {:d}/{:d}'.format(ii, npoints), flush=True)
            else:
                print('.', end='', flush=True)

        print_blue('MESSAGE: rocking_3d_figure: temp images created')

        ax.view_init(elev=30, azim=-60)

    cmd4dic = {'mkv': 'ffmpeg -framerate 25 -i .animation_tmp_%03d.jpg ' +
                      '-c:v libx264 -vf fps=30 -pix_fmt yuv420p ' + outfname,
               'gif': 'ffmpeg -framerate 25 -i .animation_tmp_%03d.jpg ' +
                      '-loop 4 ' + outfname,
               'mp4': 'ffmpeg -framerate 25 -i .animation_tmp_%03d.jpg ' +
                      outfname,
               'ogv': 'ffmpeg -framerate 25 -i .animation_tmp_%03d.jpg ' +
                      '-c:v libx264 -vf fps=30 -pix_fmt yuv420p ' +
                      outfname.split('.')[0] + '.mkv' +
                      '; ffmpeg -i ' + outfname.split('.')[0] + '.mkv' +
                      ' -codec:v libtheora -qscale:v 7 -codec:a ' +
                      'libvorbis -qscale:a 5 ' + outfname +
                      '; rm ' + outfname.split('.')[0] + '.mkv'}

    cmd4dic.setdefault('convert .animation_tmp_%03d.jpg ' + outfname)

    os.system(cmd4dic.get(out_format))
    print_blue('MESSAGE: rocking_3d_figure: saved ' + outfname)

    if del_tmp_imgs:
        files = glob.glob('.animation_tmp_*')
        for file in files:
            os.remove(file)

    return 1


def save_sdf_file(array, pixelsize, fname='output.sdf', extraHeader={}):
    '''
    Save an 2D array in the `Surface Data File Format (SDF)
    <https://physics.nist.gov/VSC/jsp/DataFormat.jsp#a>`_ , which can be
    viewed
    with the program `Gwyddion
    <http://gwyddion.net/documentation/user-guide-en/>`_ .
    It is also useful because it is a plain
    ASCII file


    Parameters
    ----------
    array: 2D ndarray
        data to be saved as *sdf*

    pixelsize: list
        list in the format [pixel_size_i, pixel_size_j]

    fname: str
        output file name

    extraHeader: dict
        dictionary with extra fields to be added to the header. Note that this
        extra header have not effect when using Gwyddion. It is used only for
        the asc file and when loaded by :py:func:`wavepy.utils.load_sdf`
        as *headerdic*.


    See Also
    --------
    :py:func:`wavepy.utils.load_sdf`


    '''

    if len(array.shape) != 2:
        print_red('ERROR: function save_sdf: array must 2-dimensional')
        raise TypeError

    header = 'aBCR-0.0\n' + \
             'ManufacID\t=\tgrizolli@anl.gov\n' + \
             'CreateDate\t=\t' + \
             datetime_now_str()[:-2].replace('_', '') + '\n' + \
             'ModDate\t=\t' + \
             datetime_now_str()[:-2].replace('_', '') + '\n' + \
             'NumPoints\t=\t' + str(array.shape[1]) + '\n' + \
             'NumProfiles\t=\t' + str(array.shape[0]) + '\n' + \
             'Xscale\t=\t' + str(pixelsize[1]) + '\n' + \
             'Yscale\t=\t' + str(pixelsize[0]) + '\n' + \
             'Zscale\t=\t1\n' + \
             'Zresolution\t=\t0\n' + \
             'Compression\t=\t0\n' + \
             'DataType\t=\t7 \n' + \
             'CheckType\t=\t0\n' + \
             'NumDataSet\t=\t1\n' + \
             'NanPresent\t=\t0\n'

    for key in extraHeader.keys():
        header += key + '\t=\t' + extraHeader[key] + '\n'

    header += '*'

    if array.dtype == 'float64':
        fmt = '%1.8g'

    elif array.dtype == 'int64':
        fmt = '%d'

    else:
        fmt = '%f'

    np.savetxt(fname, array.flatten(), fmt=fmt, header=header, comments='')

    print_blue('MESSAGE: ' + fname + ' saved!')


def load_sdf_file(fname):
    '''
    Load an 2D array in the `Surface Data File Format (SDF)
    <https://physics.nist.gov/VSC/jsp/DataFormat.jsp#a>`_ . The SDF format
    is useful because it can be viewed with the program `Gwyddion
    <http://gwyddion.net/documentation/user-guide-en/>`_ .
    It is also useful because it is a plain
    ASCII file

    Parameters
    ----------

    fname: str
        output file name

    Returns
    -------

    array: 2D ndarray
        data loaded from the ``sdf`` file

    pixelsize: list
        list in the format [pixel_size_i, pixel_size_j]

    headerdic
        dictionary with the header

    Example
    -------

    >>> import wavepy.utils as wpu
    >>> data, pixelsize = wpu.load_sdf('test_file.sdf')

    See Also
    --------
    :py:func:`wavepy.utils.save_sdf`


    '''

    with open(fname) as input_file:
        nline = 0
        header = ''
        print('########## HEADER from ' + fname)

        for line in input_file:
            nline += 1
            print(line, end='')

            if 'NumPoints' in line:
                xpoints = int(line.split('=')[-1])

            if 'NumProfiles' in line:
                ypoints = int(line.split('=')[-1])

            if 'Xscale' in line:
                xscale = float(line.split('=')[-1])

            if 'Yscale' in line:
                yscale = float(line.split('=')[-1])

            if 'Zscale' in line:
                zscale = float(line.split('=')[-1])

            if '*' in line:
                break
            else:
                header += line

    print('########## END HEADER from ' + fname)

    # Load data as numpy array
    data = np.loadtxt(fname, skiprows=nline)

    data = data.reshape(ypoints, xpoints)*zscale

    # Load header as a dictionary
    headerdic = {}
    header = header.replace('\t', '')

    for item in header.split('\n'):
        items = item.split('=')
        if len(items) > 1:
            headerdic[items[0]] = items[1]

    return data, [yscale, xscale], headerdic
