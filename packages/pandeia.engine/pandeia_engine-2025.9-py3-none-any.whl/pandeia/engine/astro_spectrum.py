# Licensed under a 3-clause BSD style license - see LICENSE.rst
from __future__ import division, absolute_import

import operator as op
import numpy as np
import astropy.constants as cs
import scipy.integrate as integ
import scipy.interpolate as interp
import scipy.signal
from astropy.io import fits
from astropy.table import Table
import astropy.units as u
import synphot as syn

from . import config as cf
from .normalization import NormalizationFactory
from .profile import ProfileFactory
from .extinction import ExtinctionFactory
from .sed import SEDFactory
from .coords import Grid
from .utils import spectrum_resample
from .custom_exceptions import EngineInputError, WavesetMismatch, DataError, RangeError, DataConfigurationError
from .pandeia_warnings import astrospectrum_warning_messages as warning_messages
from .constants import PANDEIA_RTOL, PANDEIA_ATOL, SPECTRAL_LINE_WINDOW, SPECTRAL_LINE_SUBSAMPLE, SPECTRAL_MAX_SAMPLES, SPECTRAL_MAX_CHUNK, SCENE_FOV_PIXBUFFER, SCENE_MAX_PIXELVAL, PANDEIA_WAVEUNITS, PANDEIA_FLUXUNITS

default_refdata_directory = cf.default_refdata_directory
# pyfftw.interfaces.cache.enable()

class ModelSceneCube(object):

    """
    This generates a model intensity cube of a scene. It takes the analytic descriptions
    of the components of the scene and samples them into a Grid.

    Here we put wavelength as the 3rd index to enable broadcasting. The cube is a stack
    of images, each at a different wavelength. If we wish to add or multiply a wavelength
    vector (e.g. throughput) with the cube, the cube needs to be in this index order for
    it to work efficiently. FITS, however, expects an order of (wave, y, x) so a transpose
    will be required to convert to that format. Other formats may have similar requirements.

    Parameters
    ----------
    source_spectra: list of pandeia.engine.astro_spectrum.AstroSpectrum instances
        Source spectra to add to the model cube
    grid: pandeia.engine.coord.Grid instance
        Grid describing the 2D spatial coordinates for each plane of the cube
    psf_upsamp: int
        How oversampled the grid is. Needed to generate a realistic brightest pixel rate

    Methods
    -------
    add_source:  add an AstroSpectrum to the cube
    export_to_fits: export model cube to a FITS file
    """

    def __init__(self, source_spectra, grid, psf_upsamp):
        self.grid = grid
        self.x = grid.x
        self.y = grid.y
        self.xsamp = grid.xsamp
        self.ysamp = grid.ysamp
        self.nx = grid.nx
        self.ny = grid.ny
        self.psf_upsamp = psf_upsamp
        self.wave = source_spectra[0].wave
        self.nw = self.wave.shape[0]
        self.central_profiles_list = []
        # now go through the source spectra and make sure they've been merged
        # onto the same wavelength set
        for s in source_spectra:
            if not np.array_equal(self.wave, s.wave):
                message = "Model cube input spectra must be sampled at the same wavelengths."
                raise EngineInputError(value=message)
        # stick wavelength as the 3rd index of the cube to enable broadcasting
        self.int = np.zeros(self.x.shape + (self.wave.size, ), dtype=np.float32)

        for source_spectrum in source_spectra:
            self.add_source(source_spectrum)

    def add_source(self, spectrum):
        """
        Add a source to the model cube.

        Parameters
        ----------
        spectrum: pandeia.engine.astro_spectrum.AstroSpectrum instance
            Spectrum object containing spatial and spectral information for the source to be added
        """
        src = spectrum.src
        src.grid = self.grid
        self.profile = ProfileFactory(self.psf_upsamp, config=src)
        plane = self.profile.normalized()
        central_pixel, extended = self.profile.brightest()
        self.central_profiles_list.append(central_pixel)

        # This broadcasting step can really spike the memory for large fields (like SOSS).
        # So we split up the task if there are a lot of wavelength planes at the cost of a few seconds of run time.
        # Potentially this could be done more elegantly
        if self.nw>SPECTRAL_MAX_CHUNK:
            self.int[:,:,0:SPECTRAL_MAX_CHUNK] += plane.reshape(plane.shape + (1,)) * spectrum.flux[0:SPECTRAL_MAX_CHUNK]
            self.int[:,:,SPECTRAL_MAX_CHUNK:] += plane.reshape(plane.shape + (1,)) * spectrum.flux[SPECTRAL_MAX_CHUNK:]
        else:
            self.int += plane.reshape(plane.shape + (1, )) * spectrum.flux

    def export_to_fits(self, fitsfile='ModelSceneCube.fits'):
        """
        Write model cube to a FITS file
        """
        header = self.grid.wcs_info()
        t1 = fits.PrimaryHDU(np.moveaxis(self.int, [0, 1, 2], [1, 2, 0]))
        c1 = fits.Column(name='wavelength', array=self.wave, format='D')
        t2 = fits.BinTableHDU.from_columns([c1])
        t1.header.update(header)
        tbhdu = fits.HDUList([t1,t2])
        tbhdu.writeto(fitsfile, overwrite=True)
        tbhdu.close()


class AstroSpectrum(object):

    """
    Class that contains a 1D wavelength grid and methods to calculate a single point spectrum,
    for instance from a point source.

    Parameters
    ----------
    src: pandeia.engine.source.Source
        Source instance containing parameters relevant for the definition of the astro spectrum.
    webapp: bool
        Determines whether extra API checks are done

    Attributes
    ----------
    src: pandeia.engine.source.Source instance
        The input source containing parameters relevant for the definition of the astro spectrum.
    line_definition: list of pandeia.engine.source.Line instances
        The lines contained in the spectrum of self.src
    normalization: instance of pandeia.engine.normalization.Normalization subclass
        Normalization information defining the brightness of self.src
    sed: instance of pandeia.engine.sed.SED subclass
        Spectral energy distribution information for self.src (excluding lines)
    wave: 1D np.ndarray
        The wavelength vector of the spectrum
    flux: 1D np.ndarray
        The flux vector of the spectrum
    nw: int
           Number of wavelength points

    Methods
    -------
    export_to_fits_table()
        Write self.wave and self.flux to binary FITS table
    add_spectral_lines()
        Add spectral lines to the spectrum
    resample()
        Resample spectrum to a new set of wavelengths via interpolation
    trim()
        Trim spectrum to a specified wavelength range

    Notes
    -----

    """

    def __init__(self, src, webapp=False, **kwargs):

        self.src = src
        self.warnings = {}
        # get the spectrum information from the source
        self.line_definitions = sorted(self.src.spectrum['lines'], key=op.itemgetter("center"))
        self.normalization = NormalizationFactory(config=self.src.spectrum['normalization'], webapp=webapp)
        self.extinction = ExtinctionFactory(config=self.src.spectrum['extinction'], webapp=webapp)

        # if redshift is provided (it should be if config file is up-to-date) use it, else assume it's 0.0
        if 'redshift' in self.src.spectrum:
            z = self.src.spectrum['redshift']
        else:
            z = 0.0

        if z <= -1.0:
            msg = "Specified source redshift must be > -1.0."
            raise EngineInputError(value=msg)

        self.sed = SEDFactory(config=self.src.spectrum['sed'], webapp=webapp, z=z)

        self.wave, self.flux = (1.0 + z) * self.sed.wave, self.sed.flux
        self.nw = self.wave.size

        # Optional capability: the keyword has to exist and be set to false to have the non-default behavior
        if "extinction_first" in self.src.spectrum and self.src.spectrum["extinction_first"] == False:
            # apply normalization before extinction
            self.wave, self.flux = self.normalization.normalize(self.wave, self.flux)

            # apply extinction after redshift
            self.wave, self.flux = self.extinction.extinction(self.wave, self.flux)
        else:
            # apply extinction after redshift
            # the normalization is passed in so the bandpass can be obtained through its helper functions
            self.wave, self.flux = self.extinction.extinction(self.wave, self.flux)

            # apply normalization after extinction
            self.wave, self.flux = self.normalization.normalize(self.wave, self.flux)

        # update warnings...
        self.warnings.update(self.normalization.warnings)
        self.warnings.update(self.sed.warnings)

        # add lines after normalizing continuum since line strengths are currently specified
        # using physical units. future support for specifying line strengths as equivalent widths
        # would allow lines to be added before normalization.
        if len(self.line_definitions) > 0:
            self.add_spectral_lines()

        # Astropy Synphot usage ends here, so convert back to arrays
        self.wave = self.wave.to_value(PANDEIA_WAVEUNITS)
        self.flux = self.flux.to_value(PANDEIA_FLUXUNITS)

    def export_to_fits_table(self, fitsfile="source_spectrum.fits"):
        """
        Export the source spectrum to a fits file

        Parameters:
        fitsfile (str, optional): 
            name of the output file. Defaults to "source_spectrum.fits".
        """

        c1 = fits.Column(array=self.wave, format="D", name="wavelength", unit="micron")
        c2 = fits.Column(array=self.flux, format="D", name="flux", unit="mJy")
        tbhdu = fits.BinTableHDU.from_columns([c1, c2])
        tbhdu.writeto(fitsfile, overwrite=True)

    def add_spectral_lines(self):
        """
        This method adds lines to the spectrum by either adding the line flux (for emission lines) or calculating
        an absorption line using the optical depth, F = Fcont * exp(-tau). The sampling of the spectrum is checked for each line
        and new samples added as necessary to assure adequate sampling for each line. The sampling of the underlying spectrum is
        doubled to avoid any Nyquist smoothing effects.
        """
        # make a nyquist sampled version of the underlying wavelength set to mitigate the effects of resampling.
        # synphot is used for the resampling so flux is properly preserved in the process.
        halves = self.wave[0:-1] + 0.5 * np.diff(self.wave)

        # known issue with astropy: numpy's append function results in a Nonetype unit: http://docs.astropy.org/en/latest/known_issues.html#quantities-lose-their-units-with-some-operations
        nywave = np.append(self.wave.value, halves.value) * self.wave.unit
        nywave.sort()

        lines = []

        # loop through line definitions to build waveset properly sampled for all of them
        for line_definition in self.line_definitions:
            spectral_line = SpectralLine(line_definition)
            lines.append(spectral_line)
            # update wavelength set so that it optimally samples the line's wavelength region.
            nywave = spectral_line.line_waveset(nywave)

        # resample underlying spectrum to new wavelength set.
        # this method will update self.wave, self.flux, and self.nw accordingly.
        nyflux = np.nan_to_num(spectrum_resample(self.flux.value, self.wave.value, nywave.value))
        self.wave = nywave
        self.flux = nyflux << PANDEIA_FLUXUNITS
        self.nw = nywave.size

        # now apply the lines to the spectrum
        for spectral_line in lines:
            if spectral_line.emission_or_absorption == 'emission':
                self.flux = self.flux + spectral_line.flux(self.wave)
            elif spectral_line.emission_or_absorption == 'absorption':
                self.flux = self.flux * np.exp(-spectral_line.optical_depth(self.wave))
            else:
                raise EngineInputError(value="Invalid spectral line type: %s" % spectral_line.emission_or_absorption)

    def trim(self, wmin, wmax):
        """
        Trim spectrum to wavelength range specified by wmin and wmax

        Parameters
        ----------
        wmin: float
            Minimum wavelength (microns)
        wmax: float
            Maximum wavelength (microns)
        """
        valid_subs = np.where((self.wave >= wmin) & (self.wave <= wmax))
        if valid_subs is None or len(valid_subs[0]) == 0:
            # corner case: We have a spectrum that covers the wavelength range 
            # of the instrument setup, but it's so sparsely specified that no 
            # points fall within the range. (HETC-454)
            if (self.wave[0] <= wmin) and (self.wave[-1] >= wmax):
                wave = np.asarray([wmin,wmax])
                valid_subs = np.where((wave >= wmin) & (wave <= wmax))
                # 1D (linear) interpolation is all synphot does; I see no reason 
                # to create a spectrum here just to resample it
                int_spec = interp.interp1d(self.wave,self.flux)
                self.flux = int_spec(wave)
                self.wave = wave
            else:
                msg = "Spectrum for source does not have any overlap with instrument wavelength range."
                raise WavesetMismatch(value=msg)

        trim_wave = []
        # make sure trimmed wavelengths include wmin and wmax
        if not np.isclose(self.wave[valid_subs][0], wmin, atol=PANDEIA_ATOL, rtol=PANDEIA_RTOL):
            trim_wave.append(wmin)

        trim_wave.extend(self.wave[valid_subs])

        if not np.isclose(self.wave[valid_subs][-1], wmax, atol=PANDEIA_ATOL, rtol=PANDEIA_RTOL):
            trim_wave.append(wmax)

        trim_wave = np.array(trim_wave)

        # our spectra are in mJy, which is a flux DENSITY, so interpolation is appropriate for 
        # trimming (JETC-2812)
        int_spec = interp.interp1d(self.wave, self.flux, bounds_error=False, fill_value=np.nan)
        trim_flux = int_spec(trim_wave)

        self.wave = trim_wave
        self.flux = trim_flux
        self.nw = self.wave.size


class SpectralLine(object):

    """
    A spectral line - that is the information and methods needed to add a single line to a spectrum.
    The line could also form a component of a composite line (for instance a P Cygni line consisting
    of an emission line AND an absorption line). In this case, one would create two different instances
    of SpectralLine, with relevant profile parameters, and add them both to the spectrum. The class
    includes methods to create a wavelength window with finer sampling than the rest of the spectrum.
    The single line is modeled as a gaussian profile (only option right now, could be more later)
    with a FWHM, a central wavelength and a strength. The line can be either in emission or
    absorption. In the case of an emission line, the strength is an integrated line intensity in
    cgs units, and in the case of an absorption line the strength is a peak optical depth.

    Arguments
    definition - A dictionary containing the line parameters (center, width, strength, profile and emission_or_absorption).
    """

    def __init__(self, definition):
        """
        This needs to be updated to match configuration patterns used elsewhere in engine.  See #1904 for details.
        """
        self.center = definition['center'] * PANDEIA_WAVEUNITS
        self.width = definition['width'] * (u.km * u.second**-1)
        self.strength = definition['strength'] * u.mJy
        self.profile = definition['profile']
        self.emission_or_absorption = definition['emission_or_absorption']
        self.name = definition['name'] if 'name' in definition else ''

        # In wavelength units
        self.wave_width = self.width / cs.c * self.center

        # Run the sanity checks to make sure things are kosher.
        self._sanity_checks()

    def _sanity_checks(self):
        """
        Basic sanity check for lines. Strength must be positive, line width must be
        positive, center wavelength must be positive.

        Raises:
            EngineInputError: Useful error for the line parameters checked.
        """

        # Check the center, width and strength
        # Based on Issue #2263#issuecomment-263374621
        if self.center <= 0 or self.width <= 0 or self.strength < 0:
            msg = 'Invalid line configuration'
            if self.name:
                msg += ' for "' + self.name + '"'
            msg += ': Center must be > 0, width must be > 0 and strength must be >= 0.'
            raise EngineInputError(msg)

    def line_waveset(self, wave, window_factor=SPECTRAL_LINE_WINDOW):
        """
        Create set of wavelengths to optimally sample the spectral line.

        Arguments
        ---------
        wave: np.ndarray
            Wavelength set of spectrum to which line will be added
        window_factor: int
            Configure the size of the wavelength window over which wavelength samples are checked and, if necessary,
            created. Window size is 2 * window_factor * SPECTRAL_LINE_SUBSAMPLE.

        Returns
        -------
        lwave: np.ndarray
            Array of wavelengths
        """
        nsamp = window_factor * 2 * SPECTRAL_LINE_SUBSAMPLE  # Nyquist plus some oversampling
        wmin = np.max(self.center - self.wave_width * window_factor, 0)
        wmax = self.center + self.wave_width * window_factor

        # check input wavelength set over the line window to see if we need supplement with some more samples
        lsubs = (wave > wmin) & (wave < wmax)
        if len(wave[lsubs]) > nsamp:
            # if we're already sampled sufficiently over the line region, return wave unmodified
            # though just the units, to match the behavior of merge_wavelengths
            lwave = wave.value
        else:
            # otherwise create a finely sampled set over the line, merge with the input, and return result
            # NOTE (JETC-1668): lines (and therefore the additional line wavelengths) are specified in 
            # PANDEIA_WAVEUNITS (microns) but the spectrum is not yet guaranteed to be (and is most likely 
            # in Angstroms). We need to be absolutely sure the wavelengths are in the same units 
            # before merging, otherwise resampling the line flux might fail. This caused a bug present in 
            # v1.5.2 and fixed in v1.6
            lwaveset = np.linspace(wmin, wmax, int(nsamp))
            lwave = syn.utils.merge_wavelengths(wave.value, lwaveset.to_value(wave.unit))

        return lwave*wave.unit

    def flux(self, wave):
        """
        Calculate emission line flux over wavelength set, wave.

        Arguments
        ---------
        wave: np.ndarray
            Wavelengths over which to calculate line emission

        Returns
        -------
        flux: np.ndarray
            Line flux at wave
        """
        sigma = self.wave_width / 2.3548

        # normalized to a peak flux density of 1 mJy - note that flux will be unitless
        flux = np.exp(-(wave - self.center) ** 2 / (2. * sigma ** 2))

        # input line strength units in 10^-26 erg/cm^2/s (aka mJy)
        # because the flux is unitless and THIS calculation isn't unit-aware, we have to do some manual conversions
        int_flux = -integ.simpson(flux * 1e-26, x=(cs.c / (wave.to(u.m))))


        flux = flux * self.strength / int_flux

        return flux

    def optical_depth(self, wave):
        """
        Calculate absorption line optical depth over wavelength set, wave.

        Arguments
        ---------
        wave: np.ndarray
            Wavelengths over which to calculate line optical depth

        Returns
        -------
        tau: np.ndarray
            Line optical depth at wave
        """
        sigma = self.wave_width / 2.3548
        tau = np.exp(-(wave - self.center) ** 2 / (2. * sigma ** 2))
        tau *= self.strength
        # tau is unitless, but the calculation will produce mJy because of self.strength
        return tau.value


class ConvolvedSceneCube(object):

    """
    The SceneCube contains the source flux distribution as seen through the optics
    of a telescope/instrument combination. It takes the sampled ModelSceneCube and
    convolves it with the appropriate PSF from PSFLibrary.

    This is a central class of the ETC. The cube has two spatial and one wavelength dimension.

    Parameters
    ----------
    Sources : list
        A list of Source instances containing the physical parameters
        of the sources within the scene.
    instrument : Instrument class
        An instance of the instrument class
    background : Background, optional
        A background spectrum.
    webapp: bool
        Determines whether extra API checks are done
    validate: bool
        Keyword controlling whether intermediate products are saved for validation.
    empty_scene : bool
        Set to True if the scene is empty, and several computationally intensive steps can be bypassed

    Attributes
    ----------
    PSFLibrary :
    instrument :
    Grid :
    flux_cube :
    flux_plus_bg :

    """

    def __init__(self, scene, instrument, background=None, webapp=False, validate=False, empty_scene=False):
        self.warnings = {}
        self.scene = scene
        if instrument.get_slit_pars()["slit_axis"] == "x":
            self.aper_width = instrument.get_slit_pars()['disp']
            self.aper_height = instrument.get_slit_pars()['xdisp']
        else:
            self.aper_height = instrument.get_slit_pars()['disp']
            self.aper_width = instrument.get_slit_pars()['xdisp']
        self.multishutter = instrument.get_slit_pars()['multishutter']
        nslice_str = instrument.get_slit_pars()['nslice']
        self.slit_shape = instrument.get_slit_pars()['slit_shape']

        if nslice_str is not None:
            self.nslice = int(nslice_str)
        else:
            self.nslice = 1

        self.empty_scene = empty_scene
        self.instrument = instrument
        if validate:
            self.psf_library = instrument.psf_library
            self.background = background

        self.fov_size = self.get_fov_size()

        # Figure out what the relevant wavelength range is, given the instrument mode
        wrange = self.instrument.get_wave_range()

        self.source_spectra = []
        spectra = []

        # run through the sources and check their wavelength extents. warn if they fall short of the
        # current instrument configuration's range.
        mins = []
        maxes = []
        key = None
        for i, src in enumerate(scene.sources):
            spectrum = AstroSpectrum(src, webapp=webapp)
            self.warnings.update(spectrum.warnings)
            smin = spectrum.wave.min()
            smax = spectrum.wave.max()
            if smin > wrange['wmin']:
                if smin > wrange['wmax']:
                    key = "spectrum_missing_red"
                    msg = warning_messages[key] % (smin, smax, wrange['wmax'])
                    self.warnings["%s_%s" % (key, i)] = msg
                else:
                    key = "wavelength_truncated_blue"
                    msg = warning_messages[key] % (smin, wrange['wmin'])
                    self.warnings["%s_%s" % (key, i)] = msg
            if smax < wrange['wmax']:
                if smax < wrange['wmin']:
                    key = "spectrum_missing_blue"
                    msg = warning_messages[key] % (smin, smax, wrange['wmin'])
                    self.warnings["%s_%s" % (key, i)] = msg
                else:
                    key = "wavelength_truncated_red"
                    msg = warning_messages[key] % (smax, wrange['wmax'])
                    self.warnings["%s_%s" % (key, i)] = msg

            spectra.append(spectrum)

            mins.append(smin)
            maxes.append(smax)

        wmin = max([np.array(mins).min(), wrange['wmin']])
        wmax = min([np.array(maxes).max(), wrange['wmax']])

        # make sure we have something within range and error out otherwise
        if wmax < wrange['wmin'] or wmin > wrange['wmax']:
            msg = "No wavelength overlap between source_spectra [%.2f, %.2f] and instrument [%.2f, %.2f]." % (
                np.array(mins).min(),
                np.array(maxes).max(),
                wrange['wmin'],
                wrange['wmax']
            )
            raise RangeError(value=msg)

        # warn if partial overlap between combined wavelength range of all sources and the instrument's wrange
        if wmin != wrange['wmin'] or wmax != wrange['wmax']:
            key = "scene_range_truncated"
            self.warnings[key] = warning_messages[key] % (wmin, wmax, wrange['wmin'], wrange['wmax'])

        """
        Trim spectrum and do the spectral convolution here on a per-spectrum basis.  Most efficient to do it here
        before the wavelength sets are merged.  Also easier and much more efficient than convolving
        an axis of a 3D cube.
        Also compute the filter leak (only valid for image projections), which needs pre- and 
        post-trimming products.
        """
        for i, spectrum in enumerate(spectra):
            if self.instrument.projection_type in ["image", "image_scan"]:
                # get the pre-trimming filter leak components
                full_filtered = self.focal_plane_rate(spectrum.flux, spectrum.wave)
                full = integ.simpson(full_filtered, x=spectrum.wave)

            # we trim here as an optimization so that we only convolve the section we need of a possibly very large spectrum
            spectrum.trim(wrange['wmin'], wrange['wmax'])

            if self.instrument.projection_type in ["image", "image_scan"]:
                # get the post-trimming filter leak components
                trim_filtered = self.focal_plane_rate(spectrum.flux, spectrum.wave)
                trim = integ.simpson(trim_filtered, x=spectrum.wave)

                # compute filter leak and set warning if applicable
                filter_leak = (full-trim)/full
                if filter_leak > self.instrument.max_filter_leak:
                    key = "filter_leak"
                    msg = warning_messages[key].format(filter_leak*100)
                    self.warnings["%s_%s" % (key, i)] = msg

            spectrum = instrument.spectrometer_convolve(spectrum)
            self.source_spectra.append(spectrum)
        # include the background in the wavelength array calculation, so it's eventually properly sampled
        background.trim(wrange['wmin'], wrange['wmax'])

        """
        different spectra will have different sets of wavelengths. the obvious future
        case will be user-supplied spectra, but this is also true for analytic spectra
        that have different emission/absorption lines. go through each of the spectra,
        merge all of the wavelengths sets into one, and then resample each spectrum
        onto the combined wavelength set.
        """
        self.wave = self.source_spectra[0].wave
        for s in self.source_spectra:
            # Specifying the threshold fixes bug JETC-1758
            self.wave = syn.utils.merge_wavelengths(self.wave, s.wave, threshold=PANDEIA_ATOL)
        # Also merge in the background wavelengths
        self.wave = syn.utils.merge_wavelengths(self.wave, background.wave, threshold=PANDEIA_ATOL)

        projection_type = instrument.projection_type

        """
        For the spectral projections, we could use the pixel sampling. However, this
        may oversample the cube for input spectra with no narrow features. So we first check
        whether the pixel sampling will give us a speed advantage. Otherwise, do not resample to
        an unnecessarily fine wavelength grid.
        """
        if projection_type in ('spec', 'slitless', 'slitless_scan', 'multiorder'):
            wave_pix = instrument.get_wave_pix()
            wave_pix_trim = wave_pix[np.where(np.logical_and(wave_pix >= wrange['wmin'],
                                                             wave_pix <= wrange['wmax']))]
            if wave_pix_trim.size < self.wave.size:
                self.wave = wave_pix_trim

        """
        There is no inherently optimal sampling for imaging modes, but we resample here to
        a reasonable number of wavelength bins if necessary. This helps keep the cube rendering reasonable
        for large input spectra. Note that the spectrum resampling now uses synphot's flux conserving method
        """
        if projection_type in ('image', 'image_scan'):
            if self.wave.size > SPECTRAL_MAX_SAMPLES:
                self.wave = np.linspace(wrange['wmin'], wrange['wmax'], SPECTRAL_MAX_SAMPLES)

        self.nw = self.wave.size
        self.total_flux = np.zeros(self.nw)

        for spectrum in self.source_spectra:
            nyflux = np.nan_to_num(spectrum_resample(spectrum.flux, spectrum.wave, self.wave))
            spectrum.wave = self.wave
            spectrum.flux = nyflux
            spectrum.nw = self.nw
            self.total_flux += spectrum.flux

        # also need to resample the background spectrum
        if background is not None:
            background.resample(self.wave)

        self.grid, self.aperture_list, self.flux_cube_list, self.flux_plus_bg_list = \
            self.create_flux_cube(background=background)

        if validate:
            self.dist = self.grid.dist()

    def brightest_pixel_rate(self, spectrum, central_profile_fraction, unique_offset):
        """
        Calculate the HST Brightest Pixel Rate in a pixel-less way.
        
        This only works for imaging projection types. It is assumed the calling method 
        knows that information.

        1. determine the fraction of total flux that lands on the brightest pixel (for 
           point sources).
        2. determine the fraction of that flux that lands on the detector (scale for the
           fact that the PSFs don't sum to 1)
        3. determine the fraction of flux that lands in the central pixel of the 
           (possibly extended) profile
        4. determine the fcal plane rate of the spectrum and integrate to a scalar value

        Multiplying the results of 1-4 together yields the brightest pixel rate (without dark current and postflash)

        5. add in dark current, postflash, and background. This happens in 
           DetectorSignal.calculate_brightest_pixel()

        Parameters:
        -----------
        spectrum: AstroSpectrum
            The spectrum of a single source
        central_profile_fraction: float
            The fraction of flux that ends up in the center pixel of the profile, 
            computed by the Profile class
        
        """
        # 1. Due to optical abberations, not all PSFs are brightest at the center.
        #    Correction factors have been derived that will compute the flux at
        #    various offsets relative to the total flux on the detector, as a 
        #    function of wavelength. Loop through them all to find the one that,
        #    when paired with this spectrum, produces the brightest pixel.
        fluxfrac = True
        try:
            ee_filename = default_refdata_directory + "/" + self.instrument.telescope.tel_name + "/" + self.instrument.inst_name + f"/optical/{self.instrument.inst_name}_ee_curves.fits"

            # The file contains a whole bunch of centering offsets that have
            # effectively variable brightness. Iterate through all of them to
            # find the one that would result in the greatest multiplier.
            with fits.open(ee_filename) as hdu:
                table_name = self.instrument.mode.upper()
                t = Table(hdu[table_name].data)
                fluxfrac = hdu[table_name].header["FLUXFRAC"]

                corr_wave = t['wavelength']/10000 # The file's units are Angstroms

                # Remove the column containing only wavelengths to just leave the aperture sizes in the table.
                t.remove_column('wavelength')

            corr_bright = []
            corrected_rates = []
            for offset in t.columns:
                # As of 2023-07-12, this portion of the code is only trivially used to check single
                # curves. If this functionality is expanded this code needs to be tested more thoroughly
                # tested as the rest of this module.
                if len(t.columns) > 1:
                    self.warnings["untested_code"] = "The FLUXFRAC path in the brightest_pixel_rate code has not been well tested."
                corr_interp = interp.make_interp_spline(corr_wave, t[offset], k=1)
                corr_offset = corr_interp(self.wave)

                corr_rate = spectrum.flux * corr_offset

                corr_bright.append(integ.trapezoid(corr_rate, x=self.wave))
                corrected_rates.append(corr_rate)
            max_val = np.argmax(corr_bright)
            corr_pix_rate = corrected_rates[max_val]
        except FileNotFoundError as exp:
            corr_pix_rate = spectrum.flux


        # 2. determine the fraction of that flux that lands on the detector, from the
        #    PSF. This is pre-tabulated in the PSFs and exposed via self.psf_library
        if fluxfrac:
            # As of 2023-07-12, none of our data files use this data path; it is not as well
            # tested as the rest of this module.
            self.warnings["untested_code"] = "The FLUXFRAC path in the brightest_pixel_rate code has not been well tested."
            centered = [psf for psf in self.instrument.psf_library._psfs if psf["source_offset"] == unique_offset]
            psf_wave, psf_sum = np.asarray([[x["wave"] for x in centered],[x["psfsum"] for x in centered]])

            # interpolate onto this observation's wavelength scale
            psf_interp = interp.make_interp_spline(psf_wave, psf_sum, k=1)
            psf_sum = psf_interp(self.wave)
        else:
            psf_sum = 1

        corr_psf_pix_rate = psf_sum * corr_pix_rate


        # 3. Determine the fraction of the flux that lands in the central pixel of
        #    the profile. This has been done for us by ModelSceneCube.
        #    It may be higher than 1 if the extended source was normalized to a point
        #    somewhere far from the center.
        corr_psf_profile_pix_rate = corr_psf_pix_rate * central_profile_fraction


        # 4. determine the focal plane rate of the spectrum and integrate to a scalar
        #    value 
        # Get the quantum yield
        corr_psf_profile_fp_pix_rate = self.focal_plane_rate(self.ote_rate(corr_psf_profile_pix_rate), spectrum.wave)
        q_yield, fano_factor = self.instrument.get_quantum_yield(self.wave)
        # convert the photon rate to electron rate by multiplying by the quantum
        # yield which is a function of wavelength
        brightest_pixel_rate = integ.trapezoid(corr_psf_profile_fp_pix_rate * q_yield, x=self.wave)
        # brightest_pixel_rate is now the rate (in e-/s or counts/s) of the source, in its
        # brightest pixel.

        return brightest_pixel_rate


    def get_fov_size(self, pixbuffer=SCENE_FOV_PIXBUFFER):
        """
        get_fov_size is the main function that determines the size of the FOV. There are
        four possible modes: 
        
        1. For multiorder (just NIRISS SOSS): Use the size given in the subarray
        2. If the scene is dynamic, the size is the size of the scene (plus
           SCENE_FOV_PIXBUFFER) between the minimum and maximum sizes. 
        3. If the scene is not dynamic, the size is custom_scene_size 
        4. If custom_scene_size is not set, the size is the PSF dimensions.

        In all cases, the scene is intended to be square. 
        
        Parameters
        ----------
        pixbuffer : int
           buffer size around the scene, by default SCENE_FOV_PIXBUFFER. This exists so
           that a point source at the edge of the scene will not be visibly cut off

        Returns
        -------
        fov_size: float
            The FOV size in arcseconds, for a square scene

        Raises
        ------
        DataError
            If appropriate defaults do not exist in the data
        EngineInputError
            If the scene size is larger than max_fov
        """
        # The scene size is the minimum size containing all sources, but at least as large as the PSF.


        instrument_name = self.instrument.get_name()
        aperture_name = self.instrument.get_aperture()
        readout_pattern = self.instrument.detector.get("readout_pattern", "default")
        psf_shape = self.instrument.psf_library.get_shape(instrument_name, aperture_name)
        psf_pix_scl_x, psf_pix_scl_y = self.instrument.psf_library.get_pix_scale(instrument_name, aperture_name)
        psf_size = np.max([psf_shape[1] * psf_pix_scl_x, psf_shape[0] * psf_pix_scl_y])

        if self.instrument.projection_type == 'multiorder':
            # for the multiorder case (i.e. SOSS), we need to set the FOV size based on the subarray used
            subarray = self.instrument.detector['subarray']
            aperture = self.instrument.instrument['aperture']
            subarray_config = self.instrument.subarray_config['default'][subarray]
            if readout_pattern in self.instrument.subarray_config:
                subarray_config = self.instrument.subarray_config[readout_pattern][subarray]
            nx = subarray_config['nx']
            ny = subarray_config['ny']
            pix_scale_x, pix_scale_y = self.instrument.psf_library.get_det_scale(instrument_name, aperture_name)
            disp_axis = self.instrument.dispersion_axis()
            if disp_axis == "x":
                fov_pix = ny
                fov_size = fov_pix * pix_scale_x
            else:
                fov_pix = nx
                fov_size = fov_pix * pix_scale_y

        elif self.instrument.dynamic_scene:
            scene_size = self.scene.get_size()
            # a scene size and maximum scene size must be defined for each instrument/mode.
            # if they're not defined at all, it's a data problem.
            try:
                inst_fov = self.instrument.scene_size
                max_fov = self.instrument.max_scene_size
            except AttributeError as e:
                message = "Instrument configuration must specify default and maximum scene sizes. (%s)" % e
                raise DataError(value=message)
            # the configured scene size must be smaller than the maximum. since they can come from
            # either the data files or input configuration, this is an input error.
            if inst_fov > max_fov:
                message = "Specified scene size, %f arcsec, larger than maximum allowed size of %f arcsec" % (inst_fov, max_fov)
                raise EngineInputError(value=message)

            # find the largest of the size of the defined scene, the configured instrument FOV, and the PSF image size.
            # if this is larger than the configured maximum FOV size, set it to the maximum value.
            fov_size = np.max([scene_size + pixbuffer * np.max([psf_pix_scl_x, psf_pix_scl_y]), inst_fov, psf_size])
            # warn if the fov size is larger than the instrument's maximum fov size.
            if fov_size > max_fov:
                key = "max_scene_size_reached"
                self.warnings[key] = warning_messages[key] % (fov_size, max_fov)
                fov_size = max_fov
        else:
            # If the scene is not dynamic and not multiorder, there are still cases where we want
            # to customize the scene size, like NIRSpec IFU (JETC-1704) and STIS CCD ImagingAcq 
            # (JETC-1584)
            try:
                fov_size = self.instrument.custom_scene_size
            except AttributeError as e:
                # otherwise, the usual behavior: Scene size is PSF size
                fov_size = psf_size

        # check to make sure at least one source is within the field of view. warn otherwise...
        if fov_size < self.scene.get_min_size():
            key = "scene_fov_too_small"
            self.warnings[key] = warning_messages[key] % fov_size

        return fov_size

    def focal_plane_rate(self, rate, wave):
        """
        Takes the output from self.ote_rate() and multiplies it by the components of efficiency within the
        system and returns the source rate at the focal plane in e-/s/pixel/micron.
        """
        filter_eff = self.instrument.get_filter_eff(wave)
        disperser_eff = self.instrument.get_disperser_eff(wave)
        internal_eff = self.instrument.get_internal_eff(wave)
        qe = self.instrument.get_detector_qe(wave)

        fp_rate = rate * filter_eff * disperser_eff * internal_eff * qe

        return fp_rate
    
    def ote_rate(self, rate):
        """
        Calculate source rate in e-/s/pixel/micron at the telescope entrance aperture given a flux cube in
        mJy/pixel.
        """
        # spectrum in mJy/pixel, wave in micron, f_lambda in photons/cm^2/s/micron
        # Conversion constant between mJy (1e-26 erg/s/cm**2/hz) and photons/s involves the planck constant (6.626e-27)
        # and is roughly equivalent to 1.50919 (JETC-5682)
        conversion_constant = 1/(cs.si.h.cgs / u.mJy.to(u.erg / u.cm**2))
        f_lambda = conversion_constant.value * (rate / np.array(self.wave, dtype=np.float32))
        ote_int = np.single(self.instrument.telescope.get_ote_eff(self.wave))
        coll_area = np.single(self.instrument.telescope.coll_area)
        a_lambda = coll_area * ote_int
        # e-/s/pixel/micron
        ote_rate = np.array(f_lambda * a_lambda, dtype=np.float32)

        return ote_rate

    def create_flux_cube(self, background=None):
        """
        Generate the list of convolved flux cubes that will go into the ETC calculation.
        The spectral convolution is already done and the spatial convolution is performed here
        using self.PSFLibrary (nominally as generated by webbPSF). The flux cube handles position-dependent
        PSFs by assigning PSF profiles to individual sources, convolving intermediate cubes of sources with
        common PSFs and finally co-adding cubes to create a final master flux cube. Typical ETC calculations, which do
        not have position-dependent PSFs, are not affected by this functionality.

        Parameters
        ----------
        background: background.Background instance

        Returns
        -------
        <tuple>:
            spatial grid used to create cube(s) (coords.Grid instance)
            list of apertures (list)
            list of flux cubes (list; one per aperture)
            list of flux cubes including background (list; one per aperture)

        """
        if self.instrument.psf_library is None:
            raise NotImplementedError('The use of a simple PSF in isolation is deprecated. Please provide PSFLibrary.')

        ### 1. Load information about PSFs and scene
        instrument_name = self.instrument.get_name()
        aperture_name = self.instrument.get_aperture()
        psf_pixsize_x, psf_pixsize_y = self.instrument.psf_library.get_pix_scale(instrument_name, aperture_name)
        psf_upsamp = self.instrument.psf_library.get_upsamp(instrument_name, aperture_name)
        kernel_npix_x, kernel_npix_y = self.instrument.psf_library.get_shape(instrument_name, aperture_name)

        detector_npix_x = int(np.round(self.fov_size / psf_pixsize_x / psf_upsamp))
        detector_npix_y = int(np.round(self.fov_size / psf_pixsize_y / psf_upsamp))

        if detector_npix_x % 2 == 0:
            detector_npix_x += 1
        if detector_npix_y % 2 == 0:
            detector_npix_y += 1
        detector_shape = (detector_npix_y, detector_npix_x)

        ### 2. Create the cubes to fill
        # The cube has to be in a y,x orientation
        # see coord.py Grid definition for more explanation
        flux_cube_list = [
            np.zeros(
                (int(detector_shape[0]),
                 int(detector_shape[1]),
                 self.nw), dtype=np.float32) for ir in range(self.nslice)]

        flux_plus_bg_list = [
            np.zeros(
                (int(detector_shape[0]),
                 int(detector_shape[1]),
                 self.nw), dtype=np.float32) for ir in range(self.nslice)]

        ### 3. Get background
        if background is not None:
            pupil_thru = self.instrument.psf_library.get_pupil_throughput(self.wave[0], instrument_name, aperture_name)
            self.bg = background.mjy_pix * pupil_thru
        else:
            self.bg = self.wave * 0.0

        ### 4. Create Model Scene Cube(s) from scene and source information
        self.grid = Grid(psf_pixsize_x * psf_upsamp, psf_pixsize_y * psf_upsamp, detector_shape[1], detector_shape[0])
        fine_grid = Grid(psf_pixsize_x, psf_pixsize_y, detector_shape[1] * psf_upsamp, detector_shape[0] * psf_upsamp)
        psf_associations = self.instrument.psf_library.associate_offset_to_source(self.scene.sources, instrument_name, aperture_name)
        unique_offsets = list(set(psf_associations))

        current_scenes = []
        for unique_offset in unique_offsets:
            offset_indices = [i for (i, v) in enumerate(psf_associations) if v == unique_offset]
            current_scene = ModelSceneCube([self.source_spectra[i] for i in offset_indices], fine_grid, psf_upsamp)
            # Catch calculations that are too bright to be computed, and have them abort immediately.
            if not np.all(np.isfinite(current_scene.int)):
                # warn the user about what they've done
                raise EngineInputError(value="Calculation error: at least one source is too bright to be computed "
                                             "correctly. Check your sources and source normalizations.")
            current_scenes.append(current_scene)

            # Do this part within the unique_offset loop so we match the correct profiles to the correct spectra
            if "imag" in self.instrument.projection_type and self.instrument.telescope.tel_name == "hst":
                brightest_pixel_list = []
                for idx, spectrum in enumerate([self.source_spectra[i] for i in offset_indices]):
                    brightest_pixel_list.append(self.brightest_pixel_rate(spectrum, current_scene.central_profiles_list[idx], unique_offset))
                self.brightest_pixel_rate_imaging = np.max(brightest_pixel_list)

        ### 5. Speedup check: Is this a single centered point source?
        # Check whether we have only a single point source near the center
        # (if we do, the convolution can be faster because we don't have to convolve a field larger
        # than the PSF kernel size, even if the scene is formally larger)
        self.single_point_source = True
        self.single_centered_source = True if len(self.scene.sources) == 1 else False # useful elsewhere.
        for src in self.scene.sources:
            if np.abs(src.position['x_offset']) > psf_pixsize_x*10:
                self.single_point_source = False
                self.single_centered_source = False
            elif np.abs(src.position['y_offset']) > psf_pixsize_y*10:
                self.single_point_source = False
                self.single_centered_source = False
            elif src.shape['geometry'] != 'point':
                self.single_point_source = False

        ### 6. Check and prepare scene parameters
        scene_npix_x = detector_shape[1] * psf_upsamp
        scene_npix_y = detector_shape[0] * psf_upsamp
        npix_x = int(detector_shape[1])
        npix_y = int(detector_shape[0])
        # Check to make sure npix is an integer
        if not (scene_npix_x % psf_upsamp) == 0:
            # This should never happen
            message = "Number of scene pixels, {}, is not divisible by the PSF upsampling factor, {}".format(
                scene_npix_x, psf_upsamp)
            raise DataConfigurationError(value=message)
        # Check to make sure npix is an integer
        if not (scene_npix_y % psf_upsamp) == 0:
            # This should never happen
            message = "Number of scene pixels, {}, is not divisible by the PSF upsampling factor, {}".format(
                scene_npix_y, psf_upsamp)
            raise DataConfigurationError(value=message)
        # close enough?
        # TODO: Use numpy.isclose with our usual parameters?
        if (np.abs(current_scene.xsamp / psf_pixsize_x - 1) > 1e-10):
            raise ValueError("scene sampling must be the same as PSF sampling")
        if (np.abs(current_scene.ysamp / psf_pixsize_y - 1) > 1e-10):
            raise ValueError("scene sampling must be the same as PSF sampling")
        # We have to make sure npix is an integer or it can't be used as an index
        new_shape = (npix_y, npix_x)

        ### 7. Make PSF convolution window parameters
        mini_x = int((scene_npix_x - kernel_npix_x)/2) # minimum index of the kernel size within the FOV
        maxi_x = int((scene_npix_x + kernel_npix_x)/2) # maximum index of the kernel size within the FOV
        mini_y = int((scene_npix_y - kernel_npix_y)/2) # minimum index of the kernel size within the FOV
        maxi_y = int((scene_npix_y + kernel_npix_y)/2) # maximum index of the kernel size within the FOV

        # if we have a rare instance where the PSF is larger than the scene, just effectively convolve it normally
        # (without this, the tiny window would actually have no pixels in it, producing a zero cube)
        if kernel_npix_x > scene_npix_x:
            mini_x = 0
            maxi_x = scene_npix_x
        if kernel_npix_y > scene_npix_y:
            mini_y = 0
            maxi_y = scene_npix_y

        ### 8. Make the masks
        fine_masks = []
        masks = []
        if self.aper_width is not None and self.aper_height is not None and self.slit_shape=="rectangle":
            offsets = [(i - (self.nslice - 1) / 2.) * self.aper_width for i in np.arange(self.nslice)]
            aperture_list = []
            for offset in offsets:
                slice_mask_fine = np.zeros((scene_npix_y,scene_npix_x))
                # Is this a multishutter instrument?
                if self.multishutter:
                    for shutter in self.multishutter:
                        new_mask = fine_grid.rectangular_mask(
                            width=self.aper_width,
                            height=self.aper_height,
                            xoff=offset + shutter[0],
                            yoff=shutter[1]
                        )
                        slice_mask_fine = np.maximum(slice_mask_fine, new_mask)
                else:
                    slice_mask_fine = fine_grid.rectangular_mask(
                        width=self.aper_width,
                        height=self.aper_height,
                        xoff=offset,
                        yoff=0.0
                    )
                fine_masks.append(slice_mask_fine)
                masks.append(AdvancedPSF._rebin(self,slice_mask_fine, new_shape))
                aperture_list.append({'width': self.aper_width, 'height': self.aper_height, 'offset': (0., offset)})
        elif self.aper_width is not None and self.slit_shape=="circle":
            # we do not have a use case for multiple or non-centered circular slits
            slice_mask_fine = fine_grid.circular_mask(
                self.aper_width/2, 
                xoff=0.0, 
                yoff=0.0
            )
            fine_masks.append(slice_mask_fine)
            masks.append(AdvancedPSF._rebin(self,slice_mask_fine, new_shape))
            aperture_list = [{'radius': self.aper_width, 'offset': (0., 0)}]
        else:
            # The cube indexing order is y,x
            slice_mask_fine = np.ones((scene_npix_y,scene_npix_x))
            fine_masks.append(slice_mask_fine)
            masks.append(AdvancedPSF._rebin(self,slice_mask_fine, new_shape))
            aperture_list = [self.grid.get_aperture()]


        ### 9. Run the convolution for each wavelength, for each unique PSF offset
        for iw in np.arange(self.nw):
            for current_scene, unique_offset, i in zip(current_scenes, unique_offsets, list(range(len(unique_offsets)))):
                profile = self.instrument.psf_library.get_psf(self.wave[iw], instrument_name, aperture_name, source_offset=unique_offset)
                psf_upsamp = profile['upsamp']
                kernel = np.asarray(profile['int'], dtype=np.float32)

                if i == 0:
                    psf = AdvancedPSF(
                        self.wave[iw],
                        kernel,
                        psf_upsamp=psf_upsamp,
                        current_scene=current_scene,
                        fine_masks=fine_masks,
                        masks=masks,
                        fine_shape=(scene_npix_y, scene_npix_x),
                        new_shape=new_shape,
                        grid=self.grid,
                        aperture_list=aperture_list,
                        mini_x=mini_x,
                        maxi_x=maxi_x,
                        mini_y=mini_y,
                        maxi_y=maxi_y,
                        bg_w=self.bg[iw],
                        single=self.single_point_source,
                        empty_scene = self.empty_scene
                    )
                    self.warnings.update(psf.warnings)
                else:
                    # if there are sources with different PSFs, calculate their intensities and add them,
                    # but do not add more background.
                    psf.add_intensity(
                        AdvancedPSF(
                            self.wave[iw],
                            kernel,
                            psf_upsamp=psf_upsamp,
                            current_scene=current_scene,
                            fine_masks=fine_masks,
                            masks=masks,
                            fine_shape=(scene_npix_x, scene_npix_y),
                            new_shape=new_shape,
                            grid=self.grid,
                            aperture_list=aperture_list,
                            mini_x=mini_x,
                            maxi_x=maxi_x,
                            mini_y=mini_y,
                            maxi_y=maxi_y,
                            bg_w=0.
                        )
                    )
                    self.warnings.update(psf.warnings)

            for islice in range(self.nslice):
                flux_cube_list[islice][:, :, iw] = psf.slice_int_list[islice]
                flux_plus_bg_list[islice][:, :, iw] = psf.slice_int_plus_bg_list[islice]

        return self.grid, aperture_list, flux_cube_list, flux_plus_bg_list

    def spectral_model_transform(self):
        """
        Create engine API format dict section containing properties of the wavelength coordinates
        used in the construction of a ConvolvedSceneCube.

        Returns
        -------
        t: dict (engine API compliant keys)
        """
        t = {}
        t['wave_refpix'] = 0
        t['wave_refval'] = self.wave[0]
        t['wave_max'] = self.wave.max()
        t['wave_min'] = self.wave.min()
        t['wave_size'] = self.wave.size
        # this is a bit of a hack since the wavelength sampling is NOT constant at this stage.
        # this is simply the mean step and should probably be removed altogether. if one wishes to
        # plot anything from this stage, they should instead use self.wave which provides the true
        # mapping of index -> wavelength
        if len(self.wave > 1):
            t['wave_step'] = (self.wave[-1] - self.wave[0]) / self.wave.size
        else:
            t['wave_step'] = 0.0
        return t

    def cube_wcs_info(self):
        """
        Create WCS headers and FITS binary table that describe the cube's coordinate system.

        Returns
        -------
        tbhdu: astropy.io.fits.BinTableHDU instance
            The wavelength sampling is irregularly spaced so we define a binary FITS
            table that contains the array of wavelengths, self.wave.
        header: dict
            Contains the WCS keys that define the coordinate transformation for all axes
        """
        header = self.grid.wcs_info()
        header['ctype3'] = 'WAVE-TAB'
        header['cname3'] = 'Wavelength'
        header['cunit3'] = 'um'
        header['PS3_0'] = 'WCS-TAB'
        header['PS3_1'] = 'WAVELENGTH'
        header['PS3_2'] = 'WAVE-INDEX'
        tbhdu = fits.BinTableHDU.from_columns([
            fits.Column(name='WAVELENGTH',
                        unit='um',
                        format="1D",
                        array=self.wave),
            fits.Column(name='WAVE-INDEX',
                        format="1J",
                        array=np.arange(self.wave.size))
        ])
        tbhdu.name = 'WCS-TAB'
        return tbhdu, header

    def export_to_fits(self, fitsfile='ModelDetectorCube'):
        """
        Write convolved scene cube to a FITS file

        Parameters
        ----------
        fitsfile: str
            The name of the fits file to write to.

        """
        header = self.grid.wcs_info()
        for slice_index,flux_plus_bg in enumerate(self.flux_plus_bg_list):
            fitsfile_slice = '{}{}.fits'.format(fitsfile, str(slice_index).strip())
            t1 = fits.PrimaryHDU(np.moveaxis(flux_plus_bg, [0, 1, 2], [1, 2, 0]))
            c1 = fits.Column(name='wavelength', array=self.wave, format='D')
            t2 = fits.BinTableHDU.from_columns([c1])
            t1.header.update(header)
            tbhdu = fits.HDUList([t1,t2])
            tbhdu.writeto(fitsfile_slice, overwrite=True)
            tbhdu.close()


class AdvancedPSF(object):

    """
    Convolve scene with PSF from a PSF library (e.g., one calculated using WebbPSF).

    Parameters
    ----------
    wave: float
        Wavelength (in microns) at which the scene is to be convolved.
    kernel: np.ndarray
        An interpolated PSF at the wavelength specified by wave.
    psf_upsamp: float
        The amount by which the PSF is oversampled
    current_scene: np.ndarray
        The plane of the scene we're operating on.
    fine_masks: np.ndarray
        A mask array showing geometric slit sizes (oversampled)
    masks: np.ndarray
        A mask array showing geometric slit sizes (non-oversampled)
    grid: Grid or IrregularGrid
        The grid describing the FOV, providing a mapping of pixel to position in arcseconds
    aperture_list: list
        A list of all the aperture masks (slits) that went into making the mask and fine_mask
    mini_x:
    maxi_x:
    mini_y:
    maxi_y:
        Precomputed parameters by which the scene might need to be sliced, for single-star mode.
    fine_shape: tuple
        The dimensions of the upsampled (fine) mask
    new_shape: tuple
        The dimensions of the non-upsampled mask
    bg_w: float
        Sky background rate at wavelength.
    single: Bool
        If True, assume that we only have a single point source near or at the center, and then
        only convolve a field the size of the PSF kernel (leaving the rest of the FOV at zero source flux).
    empty_scene: Bool
        If True, it's an empty scene and we can just return the empty array.
    """
    def __init__(self, wave, kernel, psf_upsamp=1, current_scene=None, fine_masks=None, masks=None, grid=None,
                 aperture_list=[], mini_x=0, maxi_x=-1, mini_y=0, maxi_y=-1, fine_shape=(0, 0), new_shape=(0, 0),
                 bg_w=0, single=False, empty_scene=False):

        # For API compatibility
        self.aperture_list = aperture_list
        self.grid = grid
        self.warnings = {}

        windex = np.abs(current_scene.wave - wave).argmin() # find nearest index

        self.slice_int_list = []
        self.slice_int_plus_bg_list = []
        self.slice_mask_list = []

        if empty_scene:
            self.intensity = np.zeros(fine_shape)
            # See Issue #71 for discussion and benchmarks about
            # these different FFT methods. astropy.convolution plus pyFFTW yields a significant
            # speed-up, of order 30% or more.
            #
            #The original method
            # import stsci.convolve as stsci
            # self.intensity = stsci.convolve2d(model_scene.int[:, :, windex], kernel, fft=1, mode='wrap')
            #
            # Basic astropy.convolution with FFTs with parameters set to produce numbers that
            # match the original method
            # self.intensity = convolve_fft(model_scene.int[:, :, windex], kernel[:-1, :-1], normalize_kernel=False)
        elif single:
            # This does not use the grid class, so indexing must be y,x (see the Grid class for more)
            self.intensity = np.zeros(fine_shape)
            # mode='same' forces the FFT output to be the same shape as the input scene to be convolved with
            # (first argument to the function)
            self.intensity[mini_y:maxi_y, mini_x:maxi_x] = scipy.signal.fftconvolve(current_scene.int[mini_y:maxi_y, mini_x:maxi_x, windex],kernel,mode='same')
        else:
            self.intensity = scipy.signal.fftconvolve(current_scene.int[:, :, windex], kernel, mode='same')

        # Add the background
        self.intensity_plus_bg = self.intensity + bg_w / psf_upsamp ** 2

        """
        We can now operate with any number of physical spectral apertures (slices) of the FOV. A single slit
        mode simply has nslice=1. An imaging mode is also a slice, but with infinite aperture.
        A multishutter instrument can create a slice aperture mask consisting of a discrete number of mutually
        offset rectangles. In principle, one could create an IFU with each slice consisting of discrete shutters.
        This could be used to simulate different IFU designs, such as lenslet or micro-mirror arrays.
        """
        for idx, fine_mask in enumerate(fine_masks):
            slice_int, slice_int_plus_bg = self._apply_slit_mask(fine_mask, new_shape)
            # for this purpose a set of multiple shutters is treated as a single aperture and uses
            # the properties of the central shutter.
            
            self.slice_int_list.append(slice_int)
            self.slice_int_plus_bg_list.append(slice_int_plus_bg)
            self.slice_mask_list.append(masks[idx])


    def add_intensity(self, psf):
        """
        Add another compatible PSF intensity.

        Parameters
        ----------
        psf : AdvancedPSF instance
            A previously computed AdvancedPSF to add.

        """

        self.slice_int_list = [slice_int + add_slice_int for slice_int, add_slice_int in
                               zip(self.slice_int_list, psf.slice_int_list)]
        self.slice_int_plus_bg_list = [slice_int + add_slice_int for slice_int, add_slice_int in
                                       zip(self.slice_int_plus_bg_list, psf.slice_int_plus_bg_list)]

        self.warnings.update(psf.warnings)

    def _apply_slit_mask(self, slit_mask, new_shape):
        """
        Applies a slit mask, and also rebins to a new shape.

        Parameters
        ----------
        slit_mask : 2D ndarray
            Slit mask as generated by self._create_slit_mask()
        new_shape : list-like
            New shape for array after binning

        Returns: list-like of 2D ndarrays
            Intensity image, intensity plus background image, aperture mask
        """
        intensity = self._rebin(self.intensity * slit_mask, new_shape)
        intensity_plus_bg = self._rebin(self.intensity_plus_bg * slit_mask, new_shape)
        return intensity, intensity_plus_bg

    def _rebin(self, a, shape):
        """
        Re-bin a 2D array.

        Parameters
        ----------
        a : ndarray
            Array to be re-binned
        shape : list-like
            New shape after re-binning

        Returns
        -------
        ndarray
        """
        # While the array shape is defined as x,y, it's actually implemented as y,x; hence the subscripts
        # see coord.py Grid definition for more explanation
        sh = int(shape[0]), int(a.shape[0] // shape[0]), int(shape[1]), int(a.shape[1] // shape[1])
        new = a.reshape(sh).sum(-1).sum(1)
        return new

    def _rebin_1d_mean(self, a, shape):
        """
        Re-bin a 1D array using averaging.

        Parameters
        ----------
        a : 1D ndarray
            Array to be re-binned
        shape : int
            New length after re-binning

        Returns
        -------
        ndarray
        """
        sh = shape, a.shape[1] // shape
        new = a.reshape(sh).mean(-1)
        return new
