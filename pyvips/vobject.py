# wrap VipsObject

from __future__ import division

import gc
import logging

import pyvips
from pyvips import ffi, vips_lib, gobject_lib, Error, _to_bytes, _to_string

logger = logging.getLogger(__name__)


class VipsObject(pyvips.GObject):
    """Manage a VipsObject."""

    def __init__(self, pointer):
        # logger.debug('VipsObject.__init__: pointer = %s', pointer)
        super(VipsObject, self).__init__(pointer)

    @staticmethod
    def print_all(msg):
        """Print all objects.

        Print a table of all active libvips objects. Handy for debugging.

        """

        gc.collect()
        logger.debug(msg)
        vips_lib.vips_object_print_all()
        logger.debug()

    # slow! eeeeew
    def _get_pspec(self, name):
        # logger.debug('VipsObject.get_typeof: self = %s, name = %s',
        #              str(self), name)

        pspec = ffi.new('GParamSpec **')
        argument_class = ffi.new('VipsArgumentClass **')
        argument_instance = ffi.new('VipsArgumentInstance **')
        vo = ffi.cast('VipsObject *', self.pointer)
        result = vips_lib.vips_object_get_argument(vo, _to_bytes(name),
                                                   pspec, argument_class,
                                                   argument_instance)

        if result != 0:
            return None

        return pspec[0]

    def get_typeof(self, name):
        """Get the GType of a GObject property.

        This function returns 0 if the property does not exist.

        """

        # logger.debug('VipsObject.get_typeof: self = %s, name = %s',
        #              str(self), name)

        pspec = self._get_pspec(name)
        if pspec is None:
            # need to clear any error, this is horrible
            Error('')
            return 0

        return pspec.value_type

    def get_blurb(self, name):
        """Get the blurb for a GObject property."""

        c_str = gobject_lib.g_param_spec_get_blurb(self._get_pspec(name))
        return _to_string(ffi.string(c_str))

    def get(self, name):
        """Get a GObject property.

        The value of the property is converted to a Python value.

        """

        logger.debug('VipsObject.get: name = %s', name)

        pspec = self._get_pspec(name)
        if pspec is None:
            raise Error('Property not found.')
        gtype = pspec.value_type

        gv = pyvips.GValue()
        gv.set_type(gtype)
        go = ffi.cast('GObject *', self.pointer)
        gobject_lib.g_object_get_property(go, _to_bytes(name), gv.pointer)

        return gv.get()

    def set(self, name, value):
        """Set a GObject property.

        The value is converted to the property type, if possible.

        """

        logger.debug('VipsObject.set: name = %s, value = %s', name, value)

        gtype = self.get_typeof(name)

        gv = pyvips.GValue()
        gv.set_type(gtype)
        gv.set(value)
        go = ffi.cast('GObject *', self.pointer)
        gobject_lib.g_object_set_property(go, _to_bytes(name), gv.pointer)

    def set_string(self, string_options):
        """Set a series of properties using a string.

        For example::

            'fred=12, tile'
            '[fred=12]'

        """

        vo = ffi.cast('VipsObject *', self.pointer)
        cstr = _to_bytes(string_options)
        result = vips_lib.vips_object_set_from_string(vo, cstr)

        return result == 0

    def get_description(self):
        """Get the description of a GObject."""

        vo = ffi.cast('VipsObject *', self.pointer)
        return _to_string(ffi.string(vips_lib.vips_object_get_description(vo)))


__all__ = ['VipsObject']