"""Read FreeSurfer geometry (fix for dev, ll 126-128);

Code was taken from nibabel.freesurfer package
(https://github.com/nipy/nibabel/blob/master/nibabel/freesurfer/io.py).
This software is licensed under the following license:

The MIT License

Copyright (c) 2009-2019 Matthew Brett <matthew.brett@gmail.com>
Copyright (c) 2010-2013 Stephan Gerhard <git@unidesign.ch>
Copyright (c) 2006-2014 Michael Hanke <michael.hanke@gmail.com>
Copyright (c) 2011 Christian Haselgrove <christian.haselgrove@umassmed.edu>
Copyright (c) 2010-2011 Jarrod Millman <jarrod.millman@gmail.com>
Copyright (c) 2011-2019 Yaroslav Halchenko <debian@onerussian.com>
Copyright (c) 2015-2019 Chris Markiewicz <effigies@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import warnings
from collections import OrderedDict

import nibabel as nib
import numpy as np


def _fread3(fobj):
    """Read a 3-byte int from an open binary file object.

    Parameters
    ----------
    fobj : file
        File descriptor

    Returns
    -------
    n : int
        A 3 byte int
    """
    b1, b2, b3 = np.fromfile(fobj, ">u1", 3).astype(np.int64)
    return (b1 << 16) + (b2 << 8) + b3


def _read_volume_info(fobj):
    """Read the footer from a surface file.

    Parameters
    ----------
    fobj : file
        File descriptor

    Returns
    -------
    volume_info : array
        Key-value pairs found in the file.
    """
    volume_info = OrderedDict()
    head = np.fromfile(fobj, ">i4", 1)
    if not np.array_equal(head, [20]):  # Read two bytes more
        head = np.concatenate([head, np.fromfile(fobj, ">i4", 2)])
        if not np.array_equal(head, [2, 0, 20]) and not np.array_equal(
            head, [2, 1, 20]
        ):
            warnings.warn("Unknown extension code.", stacklevel=2)
            return volume_info
        head = [2, 0, 20]

    volume_info["head"] = head
    for key in [
        "valid",
        "filename",
        "volume",
        "voxelsize",
        "xras",
        "yras",
        "zras",
        "cras",
    ]:
        pair = fobj.readline().decode("utf-8").split("=")
        if pair[0].strip() != key or len(pair) != 2:
            raise OSError("Error parsing volume info.")
        if key in ("valid", "filename"):
            volume_info[key] = pair[1].strip()
        elif key == "volume":
            volume_info[key] = np.array(pair[1].split()).astype(int)
        else:
            volume_info[key] = np.array(pair[1].split()).astype(float)
    # Ignore the rest
    return volume_info


def read_geometry(filepath, read_metadata=False, read_stamp=False):
    """Read a triangular format Freesurfer surface mesh.

    Parameters
    ----------
    filepath : str
        Path to surface file.
    read_metadata : bool, optional
        If True, read and return metadata as key-value pairs.
        Valid keys:
        * 'head' : array of int
        * 'valid' : str
        * 'filename' : str
        * 'volume' : array of int, shape (3,)
        * 'voxelsize' : array of float, shape (3,)
        * 'xras' : array of float, shape (3,)
        * 'yras' : array of float, shape (3,)
        * 'zras' : array of float, shape (3,)
        * 'cras' : array of float, shape (3,)
    read_stamp : bool, optional
        Return the comment from the file

    Returns
    -------
    coords : numpy array
        nvtx x 3 array of vertex (x, y, z) coordinates.
    faces : numpy array
        nfaces x 3 array of defining mesh triangles.
    volume_info : OrderedDict
        Returned only if `read_metadata` is True.  Key-value pairs found in the
        geometry file.
    create_stamp : str
        Returned only if `read_stamp` is True.  The comment added by the
        program that saved the file.
    """
    volume_info = OrderedDict()

    TRIANGLE_MAGIC = 16777214

    with open(filepath, "rb") as fobj:
        magic = _fread3(fobj)

        if magic == TRIANGLE_MAGIC:  # Triangle file
            create_stamp = fobj.readline().rstrip(b"\n").decode("utf-8")
            test_dev = fobj.peek(1)[:1]
            if test_dev == b"\n":
                fobj.readline()
            vnum = np.fromfile(fobj, ">i4", 1)[0]
            fnum = np.fromfile(fobj, ">i4", 1)[0]
            coords = np.fromfile(fobj, ">f4", vnum * 3).reshape(vnum, 3)
            faces = np.fromfile(fobj, ">i4", fnum * 3).reshape(fnum, 3)

            if read_metadata:
                volume_info = _read_volume_info(fobj)
        else:
            raise ValueError(
                f"File {filepath} does not appear to be a Freesurfer surface "
                f"(triangle file)"
            )

    coords = coords.astype(float)  # XXX: due to mayavi bug on mac 32bits

    ret = (coords, faces)
    if read_metadata:
        if len(volume_info) == 0:
            warnings.warn("No volume information contained in the file", stacklevel=2)
        ret += (volume_info,)
    if read_stamp:
        ret += (create_stamp,)

    return ret


def read_morph_data(filepath):
    """Read a Freesurfer morphometry data file.

    This function reads in what Freesurfer internally calls "curv" file types,
    (e.g. ?h. curv, ?h.thickness), but as that has the potential to cause
    confusion where "curv" also refers to the surface curvature values,
    we refer to these files as "morphometry" files with PySurfer.

    Parameters
    ----------
    filepath : str
        Path to morphometry file

    Returns
    -------
    curv : numpy array
        Vector representation of surface morpometry values
    """
    with open(filepath, "rb") as fobj:
        magic = _fread3(fobj)
        if magic == 16777215:
            vnum = np.fromfile(fobj, ">i4", 3)[0]
            curv = np.fromfile(fobj, ">f4", vnum)
        else:
            vnum = magic
            _fread3(fobj)
            curv = np.fromfile(fobj, ">i2", vnum) / 100
    return curv

def read_annot_data(filepath):
    """Read a Freesurfer annotation file.

    This function reads a Freesurfer annotation file.

    Parameters
    ----------
    filepath : str
        Path to annotation file

    Returns
    -------
    annot : annotation array
        Vector representation of surface annotation values
    ctab : array
        Colortable
    names: list
        Names
    """
    annot, ctab, names = nib.freesurfer.io.read_annot(filepath)
    return annot, ctab, names

def read_mgh_data(filepath):
    """Read an MGH image file and return its data array.

    Parameters
    ----------
    filepath : str
        Path to mgh file

    Returns
    -------
    data_array : numpy array
        Image data array
    """
    data_array = np.array(nib.load(filepath).dataobj)

    assert (
        len(data_array.shape) == 3
        and data_array.shape[1] == 1
        and data_array.shape[2] == 1
    ), f"Expected data array to have shape Nx1x1. Instead, got {data_array.shape}"

    return data_array.squeeze()
