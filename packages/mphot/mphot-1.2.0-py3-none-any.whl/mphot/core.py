import math
import os
from pathlib import Path
import logging

import numpy as np
import pandas as pd
from IPython.display import clear_output, display
from scipy.integrate import simpson as simps

from scipy.interpolate import griddata
from scipy.optimize import minimize
from astroquery.gaia import Gaia

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

grid_flux_ingredients_name = "pre_grid_03_to_3_microns_2400m_flux.pkl"
grid_radiance_ingredients_name = "pre_grid_03_to_3_microns_2400m_radiance.pkl"
vega_file = "vega_03_to_3_microns.csv"
wavelengths = np.arange(0.3, 3, 0.001)

pc = 3.0857e16  # parsec in meters


def interpolate_dfs(index: list, *data: pd.DataFrame) -> pd.DataFrame:
    """
    Interpolates multiple pandas DataFrames based on a given index.

    Args:
        index (list): A list of index values to interpolate over.
        data (pd.DataFrame): Variable number of pandas DataFrames to be interpolated.

    Returns:
        pd.DataFrame: A single DataFrame with interpolated values for the given index.
    """

    df = pd.DataFrame({"tmp": index}, index=index)
    for dat in data:
        dat = dat[~dat.index.duplicated(keep="first")]
        df = pd.concat([df, dat], axis=1)
    df = df.sort_index()
    df = df.interpolate("index").reindex(index)
    df.drop("tmp", axis=1, inplace=True)

    return df


def generate_system_response(
    efficiency_file: str, filter_file: str
) -> tuple[str, pd.Series]:
    """
    Generates a spectral response (SR) file by combining efficiency and filter data.

    Args:
        efficiency_file (str): Path to the CSV file containing efficiency data.
        filter_file (str): Path to the CSV file containing filter data.

    Returns:
        tuple: A tuple containing:
            - name (str): The name used to refer to the generated SR file.
            - dfSR (pd.Series): The spectral response data.
    """

    eff = pd.read_csv(efficiency_file, header=None)
    filt = pd.read_csv(filter_file, header=None)

    # name to refer to the generated file
    name = efficiency_file.split("/")[-1][:-4] + "_" + filter_file.split("/")[-1][:-4]

    # generates a SR, saved locally as 'name1_instrument_system_response.csv'
    SRFile = (
        Path(__file__).parent
        / "datafiles"
        / "system_responses"
        / f"{name}_instrument_system_response.csv"
    )

    effDF = pd.DataFrame({"eff": eff[1].values}, index=eff[0])

    filtDF = pd.DataFrame({"filt": filt[1].values}, index=filt[0])

    df = interpolate_dfs(wavelengths, effDF, filtDF)

    dfSR = df["eff"] * df["filt"]

    dfSR = dfSR[dfSR > 0]

    dfSR.to_csv(SRFile, header=False)

    logger.info(f"`{SRFile}` has been generated and saved!")

    return name, dfSR


def generate_flux_grid(sResponse: str) -> tuple[np.ndarray, np.ndarray]:
    """
    Generates a base flux grid based on atmospheric parameters and response functions, with the following ranges:
        airmass: 1 - 3
        pwv: 0.05 - 30 mm
        Teff: 450 - 36500 K

    This function reads in a spectral response file and a precomputed grid of flux ingredients,
    then interpolates and integrates these data to produce a grid of stellar flux responses
    for various combinations of precipitable water vapor (PWV), airmass, and temperature values.

    Args:
        sResponse (str): Path to the CSV file containing the spectral response function.

    Returns:
        tuple: A tuple containing:
            - coords (np.ndarray): A 4D array with shape
              representing the coordinates of the grid points. The last dimension
              contains the values of PWV, airmass, and temperature respectively.
            - data (np.ndarray): A 3D array with shape
              (len(pwv_values), len(airmass_values), len(temperature_values))
              containing the computed flux values for each combination of PWV,
              airmass, and temperature.
    """

    gridIngredients = pd.read_pickle(
        Path(__file__).parent / "datafiles" / grid_flux_ingredients_name
    )

    rsr = pd.read_csv(sResponse, header=None, index_col=0)

    pwv_values = np.array(
        [0.05, 0.1, 0.25, 0.5, 1.0, 1.5, 2.5, 3.5, 5.0, 7.5, 10.0, 20.0, 30.0]
    )
    airmass_values = np.array(
        [
            1.0,
            1.1,
            1.2,
            1.3,
            1.4,
            1.5,
            1.6,
            1.7,
            1.8,
            1.9,
            2.0,
            2.1,
            2.2,
            2.3,
            2.4,
            2.5,
            2.6,
            2.7,
            2.8,
            2.9,
            3.0,
        ]
    )
    temperature_values = np.array(
        [
            450,
            500,
            550,
            600,
            700,
            800,
            900,
            1000,
            1100,
            1200,
            1300,
            1400,
            1500,
            1600,
            1700,
            1800,
            2000,
            2100,
            2250,
            2320,
            2400,
            2440,
            2500,
            2600,
            2650,
            2710,
            2850,
            3000,
            3030,
            3100,
            3200,
            3250,
            3410,
            3500,
            3550,
            3650,
            3700,
            3800,
            3870,
            3940,
            4000,
            4070,
            4190,
            4230,
            4330,
            4410,
            4540,
            4600,
            4700,
            4830,
            4990,
            5040,
            5140,
            5170,
            5240,
            5280,
            5340,
            5490,
            5530,
            5590,
            5660,
            5680,
            5720,
            5770,
            5880,
            5920,
            6000,
            6060,
            6170,
            6240,
            6340,
            6510,
            6640,
            6720,
            6810,
            7030,
            7220,
            7440,
            7500,
            7800,
            8000,
            8080,
            8270,
            8550,
            8840,
            9200,
            9700,
            10400,
            10700,
            12500,
            14000,
            14500,
            15700,
            16700,
            17000,
            18500,
            20600,
            24500,
            26000,
            29000,
            31500,
            32000,
            32500,
            33000,
            34500,
            35000,
            36500,
        ]
    )
    gridSauce = interpolate_dfs(wavelengths, rsr, gridIngredients)

    gridSauce = gridSauce[(gridSauce[1] > 0)]
    atm_grid = []
    for i, pwv in enumerate(pwv_values):
        update_progress(i / (len(pwv_values) - 1))
        for airmass in airmass_values:
            for temperature in temperature_values:
                atmosphere_trans = gridSauce[str(pwv) + "_" + str(airmass)]
                simStar = gridSauce[str(temperature) + "K"]
                response = simps(
                    y=gridSauce[1] * atmosphere_trans * simStar, x=gridSauce.index
                )

                atm_grid.append((pwv, airmass, temperature, response))

    data = np.array([x[3] for x in atm_grid])
    data = data.reshape((len(pwv_values), len(airmass_values), len(temperature_values)))

    coords = np.zeros(
        (len(pwv_values), len(airmass_values), len(temperature_values), 3)
    )
    coords[..., 0] = pwv_values.reshape((len(pwv_values), 1, 1))
    coords[..., 1] = airmass_values.reshape((1, len(airmass_values), 1))
    coords[..., 2] = temperature_values.reshape((1, 1, len(temperature_values)))

    return coords, data


def generate_radiance_grid(sResponse: str) -> tuple[np.ndarray, np.ndarray]:
    """
    Generates a radiance base grid for atmospheric parameters, with the following ranges:
        airmass: 1 - 3
        pwv: 0.05 - 30 mm
        Teff: 450 - 36500 K

    This function reads in a spectral response file and a precomputed grid of radiance ingredients,
    then interpolates and integrates these data to produce a grid of atmospheric flux responses
    for various combinations of precipitable water vapor (PWV), airmass, and temperature values.

    Args:
        sResponse (str): Path to the spectral response CSV file.

    Returns:
        tuple: A tuple containing:
            - coords (np.ndarray): A 4D array of shape (len(pwv_values), len(airmass_values), len(temperature_values), 3)
              containing the coordinates for PWV, airmass, and temperature.
            - data (np.ndarray): A 3D array of shape (len(pwv_values), len(airmass_values), len(temperature_values))
              containing the integrated atmospheric flux responses.
    """

    gridIngredients = pd.read_pickle(
        Path(__file__).parent / "datafiles" / grid_radiance_ingredients_name
    )
    rsr = pd.read_csv(sResponse, header=None, index_col=0)

    pwv_values = np.array(
        [0.05, 0.1, 0.25, 0.5, 1.0, 1.5, 2.5, 3.5, 5.0, 7.5, 10.0, 20.0, 30.0]
    )
    airmass_values = np.array(
        [
            1.0,
            1.1,
            1.2,
            1.3,
            1.4,
            1.5,
            1.6,
            1.7,
            1.8,
            1.9,
            2.0,
            2.1,
            2.2,
            2.3,
            2.4,
            2.5,
            2.6,
            2.7,
            2.8,
            2.9,
            3.0,
        ]
    )
    temperature_values = np.array(
        [
            450,
            500,
            550,
            600,
            700,
            800,
            900,
            1000,
            1100,
            1200,
            1300,
            1400,
            1500,
            1600,
            1700,
            1800,
            2000,
            2100,
            2250,
            2320,
            2400,
            2440,
            2500,
            2600,
            2650,
            2710,
            2850,
            3000,
            3030,
            3100,
            3200,
            3250,
            3410,
            3500,
            3550,
            3650,
            3700,
            3800,
            3870,
            3940,
            4000,
            4070,
            4190,
            4230,
            4330,
            4410,
            4540,
            4600,
            4700,
            4830,
            4990,
            5040,
            5140,
            5170,
            5240,
            5280,
            5340,
            5490,
            5530,
            5590,
            5660,
            5680,
            5720,
            5770,
            5880,
            5920,
            6000,
            6060,
            6170,
            6240,
            6340,
            6510,
            6640,
            6720,
            6810,
            7030,
            7220,
            7440,
            7500,
            7800,
            8000,
            8080,
            8270,
            8550,
            8840,
            9200,
            9700,
            10400,
            10700,
            12500,
            14000,
            14500,
            15700,
            16700,
            17000,
            18500,
            20600,
            24500,
            26000,
            29000,
            31500,
            32000,
            32500,
            33000,
            34500,
            35000,
            36500,
        ]
    )
    gridSauce = interpolate_dfs(wavelengths, rsr, gridIngredients)

    gridSauce = gridSauce[(gridSauce[1] > 0)]
    atm_grid = []
    for i, pwv in enumerate(pwv_values):
        update_progress(i / (len(pwv_values) - 1))
        for airmass in airmass_values:
            for temperature in temperature_values:
                atmosphere_flux = gridSauce[str(pwv) + "_" + str(airmass)]
                response = simps(y=gridSauce[1] * atmosphere_flux, x=gridSauce.index)

                atm_grid.append((pwv, airmass, temperature, response))

    data = np.array([x[3] for x in atm_grid])
    data = data.reshape((len(pwv_values), len(airmass_values), len(temperature_values)))

    coords = np.zeros(
        (len(pwv_values), len(airmass_values), len(temperature_values), 3)
    )
    coords[..., 0] = pwv_values.reshape((len(pwv_values), 1, 1))
    coords[..., 1] = airmass_values.reshape((1, len(airmass_values), 1))
    coords[..., 2] = temperature_values.reshape((1, 1, len(temperature_values)))

    return coords, data


def interpolate_grid(
    coords: np.ndarray, data: np.ndarray, pwv: float, airmass: float, Teff: float
) -> float:
    """
    Interpolates between grid points, using a cubic method.

    Args:
        coords (np.ndarray): Coordinates of base grid generated.
        data (np.ndarray): Data of base grid generated.
        pwv (float): Precipitable water vapour value at zenith.
        airmass (float): Airmass of target/comparison star.
        Teff (float): Effective temperature of target/comparison star.

    Returns:
        float: Interpolated value of grid.
    """

    method = "cubic"
    Teffs = coords[..., 2][0, 0]
    Teff_lower = np.max(Teffs[Teffs <= Teff])
    Teff_upper = np.min(Teffs[Teffs >= Teff])

    if Teff_lower == Teff_upper:
        x = coords[..., 0][coords[..., 2] == Teff]  # pwv
        y = coords[..., 1][coords[..., 2] == Teff]  # airmass
        z = data[coords[..., 2] == Teff]  # effect

        interp = griddata(
            (x, y), z, (pwv, airmass), method=method
        )  # interpolated value
    else:
        x_lower = coords[..., 0][coords[..., 2] == Teff_lower]  # pwv
        y_lower = coords[..., 1][coords[..., 2] == Teff_lower]  # airmass
        z_lower = data[coords[..., 2] == Teff_lower]  # effect
        interp_lower = griddata(
            (x_lower, y_lower), z_lower, (pwv, airmass), method=method
        )  # interpolated value lower Teff

        x_upper = coords[..., 0][coords[..., 2] == Teff_upper]  # pwv
        y_upper = coords[..., 1][coords[..., 2] == Teff_upper]  # airmass
        z_upper = data[coords[..., 2] == Teff_upper]  # effect
        interp_upper = griddata(
            (x_upper, y_upper), z_upper, (pwv, airmass), method=method
        )  # interpolated value upper Teff

        w_lower = (Teff_upper - Teff) / (Teff_upper - Teff_lower)  # lower weight
        w_upper = (Teff - Teff_lower) / (Teff_upper - Teff_lower)  # upper weight

        interp = (
            w_lower * interp_lower + w_upper * interp_upper
        )  # final interpolated value

    return interp


def gaussian(delta: float, sigma: float) -> float:
    """
    Calculate the value of a Gaussian function.

    This function computes the value of a Gaussian (normal) distribution
    for a given delta and sigma.

    Args:
        delta (float): The difference from the mean (x - mu).
        sigma (float): The standard deviation of the distribution.

    Returns:
        float: The value of the Gaussian function at the given delta.
    """

    return (1.0 / (np.sqrt(2 * np.pi) * sigma)) * np.exp(-(delta**2) / (2 * sigma**2))


def integration_time(
    fwhm: float,
    N_star: float,
    N_sky: float,
    N_dc: float,
    plate_scale: float,
    well_depth: float,
    well_fill: float,
) -> float:
    """
    Calculate the integration time for a given set of parameters.

    Args:
        fwhm (float): Full width at half maximum of the point spread function.
        N_star (float): Number of star counts.
        N_sky (float): Number of sky counts.
        N_dc (float): Number of dark current counts.
        N_rn (float): Number of read noise counts.
        plate_scale (float): Plate scale in arcseconds per pixel.
        well_depth (float): Maximum well depth of the detector.
        well_fill (float): Fraction of the well depth to be filled.

    Returns:
        float: Calculated integration time.
    """

    sigma_IR = (fwhm / plate_scale) / 2.355  # in pix

    x = np.linspace(-0.5, 0.5, 100)
    y = x

    t = (well_depth * well_fill) / (
        N_star
        * simps(y=gaussian(y, sigma_IR), x=y)
        * simps(y=gaussian(x, sigma_IR), x=x)
        + (N_sky + N_dc)
    )

    return t


def convert_airmass(airmass: float, h: float) -> float:
    """
    Convert airmass at the observatory to an equivalent airmass at Paranal Observatory, assuming an isothermal atmospheric model.

    Args:
        airmass (float): Airmass at the observatory.
        h (float): Altitude of the observatory in meters.

    Returns:
        float: The equivalent converted airmass at Paranal Observatory.

    Reference:
        https://acp.copernicus.org/articles/7/6047/2007/
    """

    return airmass * np.exp((2440 - h) / 8000)


def scintillation_noise(
    r: float,
    t: float,
    N_star: float,
    h: float = 2440,
    C: float = 1.56,
    airmass: float = 1.5,
) -> float:
    """
    Calculate the scintillation noise for a given set of parameters.

    Args:
        r (float): Aperture radius in meters.
        t (float): Exposure time in seconds.
        N_star (float): Number of stars.
        h (float): Altitude of the observatory in meters. Default is 2440 for Paranal Observatory.
        C (float): Empirical coefficient. Default is 1.56, optimized for the 20-cm NGTS telescopes at Paranal Observatory.
        airmass (float, optional): Airmass value. Default is 1.5.

    Returns:
        float: The calculated scintillation noise.

    Reference:
        https://academic.oup.com/mnras/article/509/4/6111/6442285
    """

    return (
        np.sqrt(
            1e-5
            * C**2
            * pow(2 * r, -4 / 3)
            * t**-1
            * airmass**3
            * np.exp(-2 * h / 8000)
        )
        * N_star
        * t
    )


def get_precision(
    props: dict,
    props_sky: dict,
    Teff: float,
    distance: float,
    binning: float = 10,
    override_grid: bool = False,
    SPCcorrection: bool = True,
    N_sky: float | None = None,
    N_star: float | None = None,
    scn: float | None = None,
    h: float = 2440,
    C: float = 1.56,
    exp_time: float | None = None,
) -> dict:
    """
    Calculate the precision of astronomical observations based on various parameters.

    Args:
        props (dict):
            Dictionary containing properties of the instrument and observation.
            Expected keys:
            - "name": str, name of the instrument
            - "plate_scale": float, plate scale of the instrument
            - "N_dc": float, dark current noise
            - "N_rn": float, read noise
            - "well_depth": float, well depth of the detector
            - "well_fill": float, well fill level
            - "read_time": float, readout time of the detector
            - "r0": float, inner radius for aperture
            - "r1": float, outer radius for aperture
            - "ap_rad": float, optional, aperture radius

        props_sky (dict):
            Dictionary containing properties of the sky.
            Expected keys:
            - "pwv": float, precipitable water vapor
            - "airmass": float, airmass of the observation
            - "seeing": float, full width at half maximum (FWHM) of the seeing

        Teff (float):
            Effective temperature of the star in Kelvin.

        distance (float):
            Distance to the star in parsecs.

        binning (float, optional):
            Binning time in minutes. Default is 10.

        override_grid (bool, optional):
            If True, override existing grid files. Default is False.

        SPCcorrection (bool, optional):
            If True, apply SPC correction based on the effective temperature. Default is True.

        N_sky (float, optional):
            Number of sky counts, calculated if None. Default is None.

        N_star (float, optional):
            Number of star counts, calculated if None. Default is None.

        scn (float, optional):
            Scintillation noise, calculated if None. Default is None.

        h (float, optional):
            Altitude of the observatory in meters. Default is 2440 for Paranal Observatory.

        C (float, optional):
            Empirical coefficient used in the calculation of scn. Default is 1.56, optimized for the 20-cm NGTS telescopes at Paranal Observatory.

        exp_time (float, optional):
            Exposure time in seconds, calculated if None. Default is None.

    Returns:
        tuple: A tuple containing:
            image_precision : dict
                Precision of the image
            binned_precision : dict
                Precision of the binned image
            components : dict
                Various components used in the calculation
    """

    props = props.copy()
    props_sky = props_sky.copy()

    name = props["name"]
    plate_scale = props["plate_scale"]
    N_dc = props["N_dc"]
    N_rn = props["N_rn"]
    well_depth = props["well_depth"]
    well_fill = props["well_fill"]
    read_time = props["read_time"]

    if "min_exp" in props:
        min_exp = props["min_exp"]
    else:
        min_exp = 0

    if "max_exp" in props:
        max_exp = props["max_exp"]
    else:
        max_exp = np.inf

    r0 = props["r0"]
    r1 = props["r1"]

    pwv = props_sky["pwv"]
    airmass = props_sky["airmass"]
    fwhm = props_sky["seeing"]

    airmass_paranal = convert_airmass(airmass, h)

    ap = 3 * (
        fwhm / plate_scale
    )  ## approx pixel radius around target star ## changed on to 3* 2022/04/26 from 10/2.355*

    if "ap_rad" in props:
        ap = props["ap_rad"] * (fwhm / plate_scale)

    if (
        os.path.isfile(
            Path(__file__).parent / "grids" / f"{name}_precisionGrid_flux_coords.npy"
        )
        is False
    ) or (override_grid):
        # generate flux grid
        coords, data = generate_flux_grid(
            Path(__file__).parent
            / "datafiles"
            / "system_responses"
            / f"{name}_instrument_system_response.csv",
        )

        # save output
        np.save(
            Path(__file__).parent / "grids" / f"{name}_precisionGrid_flux_data.npy",
            data,
        )
        np.save(
            Path(__file__).parent / "grids" / f"{name}_precisionGrid_flux_coords.npy",
            coords,
        )

        # generate radiance grid
        coords, data = generate_radiance_grid(
            Path(__file__).parent
            / "datafiles"
            / "system_responses"
            / f"{name}_instrument_system_response.csv",
        )

        # save output
        np.save(
            Path(__file__).parent
            / "grids"
            / f"{name}_precisionGrid_radiance_coords.npy",
            coords,
        )
        np.save(
            Path(__file__).parent / "grids" / f"{name}_precisionGrid_radiance_data.npy",
            data,
        )

    # load grids
    coords = np.load(
        Path(__file__).parent / "grids" / f"{name}_precisionGrid_flux_coords.npy"
    )
    data_flux = np.load(
        Path(__file__).parent / "grids" / f"{name}_precisionGrid_flux_data.npy"
    )
    data_radiance = np.load(
        Path(__file__).parent / "grids" / f"{name}_precisionGrid_radiance_data.npy"
    )

    # get values from grids
    flux = interpolate_grid(coords, data_flux, pwv, airmass_paranal, Teff)
    radiance = interpolate_grid(coords, data_radiance, pwv, airmass_paranal, Teff)

    # collecting area of telescope
    A = np.pi * (r0**2 - r1**2)

    if N_star is None:
        N_star = flux * A / ((distance * pc) ** 2)
    else:
        flux = N_star * ((distance * pc) ** 2) / A

    if N_sky is None:
        N_sky = radiance * A * plate_scale**2
    else:
        radiance = N_sky / (A * plate_scale**2)

    ## correction
    if SPCcorrection:
        if (Teff <= 3042) and (Teff >= 1278):
            poly = np.load(Path(__file__).parent / "datafiles" / "16_order_poly.npy")
            N_star = N_star / (2.512 ** np.polyval(poly, Teff))

    t = integration_time(
        fwhm,
        N_star,
        N_sky,
        N_dc,
        plate_scale,
        well_depth,
        well_fill,
    )

    if exp_time is not None or (t < min_exp or t > max_exp):

        if t < min_exp:
            t = min_exp
        elif t > max_exp:
            t = max_exp

        if exp_time is not None:
            t = exp_time

        sigma_IR = (fwhm / plate_scale) / 2.355  # in pix

        x = np.linspace(-0.5, 0.5, 100)
        y = x

        well_fill_value = t * (
            N_star
            * simps(y=gaussian(y, sigma_IR), x=y)
            * simps(y=gaussian(x, sigma_IR), x=x)
            + (N_sky + N_dc)
        )
        well_fill = well_fill_value / well_depth

    npix = np.pi * ap**2

    if scn is None:
        scn = scintillation_noise(
            r0, t, N_star, h=h, C=C, airmass=airmass
        )  # use unconverted airmass here

    precision = np.sqrt(
        N_star * t + scn**2 + npix * (N_sky * t + N_dc * t + N_rn**2)
    ) / (N_star * t)

    precision_star = 1 / np.sqrt(N_star * t)
    precision_scn = np.sqrt(scn**2) / (N_star * t)
    precision_sky = np.sqrt(npix * (N_sky * t)) / (N_star * t)
    precision_dc = np.sqrt(npix * (N_dc * t)) / (N_star * t)
    precision_rn = np.sqrt(npix * (N_rn**2)) / (N_star * t)

    image_precision = {
        "All": precision,
        "Star": precision_star,
        "Scintillation": precision_scn,
        "Sky": precision_sky,
        "Dark current": precision_dc,
        "Read noise": precision_rn,
    }

    nImages = (binning * 60) / (t + read_time)

    binned_precision = {
        "All": precision / np.sqrt(nImages),
        "Star": precision_star / np.sqrt(nImages),
        "Scintillation": precision_scn / np.sqrt(nImages),
        "Sky": precision_sky / np.sqrt(nImages),
        "Dark current": precision_dc / np.sqrt(nImages),
        "Read noise": precision_rn / np.sqrt(nImages),
    }

    components = {
        "name": name,
        "Teff [K]": Teff,
        "distance [pc]": distance,
        "N_star [e/s]": N_star,
        "star_flux [e/m2/s]": flux / ((distance * pc) ** 2),
        "scn [e_rms]": scn,  # not sure of units
        "pixels in aperture [pix]": npix,
        "ap_radius [pix]": ap,
        "N_sky [e/pix/s]": N_sky,
        "sky_radiance [e/m2/arcsec2/s]": radiance,
        "seeing [arcsec]": fwhm,
        "pwv [mm]": pwv,
        "airmass": airmass,  # unconverted airmass
        'plate_scale ["/pix]': plate_scale,
        "N_dc [e/pix/s]": N_dc,
        "N_rn [e_rms/pix]": N_rn,  # not sure of units
        "A [m2]": A,
        "r0 [m]": r0,
        "r1 [m]": r1,
        "t [s]": t,
        "well_depth [e/pix]": well_depth,
        "peak well_fill": well_fill,  # peak pixel
        "binning [mins]": binning,
        "read_time [s]": read_time,
        "binned images": nImages,
        "altitude [m]": h,
    }

    return image_precision, binned_precision, components


def best_gaia_filters(
    system_name: str, min_weight_sum: float = 0, support_points: int = 8000
) -> np.ndarray:
    """
    Determine the weights of the linear combination of Gaia filters that best resembles the instrument system response.

    Args:
        system_name (str):
            Name of the instrument.

        min_weight_sum (float, optional):
            The minimum sum of weights in the linear combination of Gaia filters. Default is 0.

        support_points (int, optional):
            The number of support points in the wavelength spectrum between 0.3 and 3.0 microns used to interpolate the instrument system response and Gaia filter transmission curves. Default is 8000.

    Returns:
        tuple: A tuple containing:
            image_precision : dict
                Precision of the image
            binned_precision : dict
                Precision of the binned image
            components : dict
                Various components used in the calculation
    """

    # Load transmission curves
    path = (
        Path(__file__).parent
        / "datafiles"
        / "system_responses"
        / f"{system_name}_instrument_system_response.csv"
    )
    trans = np.loadtxt(str(path), delimiter=",")

    gaia_filters = ["bp", "g", "rp"]
    N = len(gaia_filters)
    gaia_paths = [
        Path(__file__).parent
        / "datafiles"
        / "flux_calibration"
        / f"gaia_{gaia_filter}.csv"
        for gaia_filter in gaia_filters
    ]
    gaia_trans = []

    for gaia_path in gaia_paths:
        g_trans = np.loadtxt(str(gaia_path), delimiter=",")
        gaia_trans.append(g_trans)

    # Get best linear combination of Gaia filters
    lam = np.linspace(0.3, 3, support_points)
    trans_interp = np.interp(lam, trans[:, 0], trans[:, 1], left=0, right=0)
    gaia_trans_interp = np.column_stack(
        [
            np.interp(lam, g_trans[:, 0], g_trans[:, 1], left=0, right=0)
            for g_trans in gaia_trans
        ]
    )

    def squared_err(weights):
        err = gaia_trans_interp @ weights - trans_interp

        return err @ err

    def jacobian(weights):
        err = gaia_trans_interp @ weights - trans_interp

        return 2 * gaia_trans_interp.T @ err

    bounds = [(0, None)] * N
    cons = ({"type": "ineq", "fun": lambda weights: np.sum(weights) - min_weight_sum},)
    x0 = np.full(N, max(1.0, min_weight_sum / N))

    res = minimize(
        squared_err,
        x0,
        jac=jacobian,
        bounds=bounds,
        constraints=cons,
        options={"maxiter": 2000},
    )

    if not res.success:
        raise RuntimeError(f"Optimization failed: {res.message}")

    return res.x


def get_precision_gaia(
    props: dict,
    props_sky: dict,
    source_id: np.uint64,
    gaia_filter: str | None = None,
    min_weight_sum: float = 0,
    support_points: int = 8000,
    binning: float = 10,
    override_grid: bool = False,
    SPCcorrection: bool = True,
    N_sky: float | None = None,
    scn: float | None = None,
    h: float = 2440,
    C: float = 1.56,
    exp_time: float | None = None,
    Teff: float | None = None,
    distance: float | None = None,
) -> dict:
    """
    Calculate the precision of astronomical observations based on various parameters and perform calibration of fluxes to Gaia fluxes.

    Args:
        props (dict):
            Dictionary containing properties of the instrument and observation.
            Expected keys:
            - "name": str, name of the instrument
            - "plate_scale": float, plate scale of the instrument
            - "N_dc": float, dark current noise
            - "N_rn": float, read noise
            - "well_depth": float, well depth of the detector
            - "well_fill": float, well fill level
            - "read_time": float, readout time of the detector
            - "r0": float, inner radius for aperture
            - "r1": float, outer radius for aperture
            - "ap_rad": float, optional, aperture radius

        props_sky (dict):
            Dictionary containing properties of the sky.
            Expected keys:
            - "pwv": float, precipitable water vapor
            - "airmass": float, airmass of the observation
            - "seeing": float, full width at half maximum (FWHM) of the seeing

        source_id (np.int64):
            The source_id property of the target from the Gaia DR3 catalog.

        gaia_filter (str, optional):
            The Gaia filter used for calibration. Must be one of the following:
            - "bp"
            - "g"
            - "rp"
            - If None, filters are selected automatically.
            See https://www.cosmos.esa.int/web/gaia/edr3-passbands for further information. Default is None.

        min_weight_sum (float, optional):
            The minimum sum of Gaia filter weights for determining the best linear combination of Gaia filters. Only used if gaia_filter is not specified. Default is 0.

        support_points (int, optional):
            The number of support points in the wavelength spectrum between 0.3 and 3.0 microns for determining the best linear combination of Gaia filters. Only used if gaia_filter is not specified. Default is 8000.

        binning (float, optional):
            Binning time in minutes. Default is 10.

        override_grid (bool, optional):
            If True, override existing grid files. Default is False.

        SPCcorrection (bool, optional):
            If True, apply SPC correction based on the effective temperature. Default is True.

        N_sky (float, optional):
            Number of sky counts, calculated if None. Default is None.

        scn (float, optional):
            Scintillation noise, calculated if None. Default is None.

        h (float, optional):
            Altitude of the observatory in meters. Default is 2440 for Paranal Observatory.

        C (float, optional):
            Empirical coefficient used in the calculation of scn. Default is 1.56, optimized for the 20-cm NGTS telescopes at Paranal Observatory.

        exp_time (float, optional):
            Exposure time in seconds, calculated if None. Default is None.

        Teff (float, optional):
            Effective temperature of the star in Kelvin. If None, it will be fetched from the Gaia catalog. Default is None.

        distance (float, optional):
            Distance to the star in parsecs. If None, it will be calculated from the parallax fetched from the Gaia catalog. Default is None.

    Returns:
        tuple: A tuple containing:
            image_precision : dict
                Precision of the image
            binned_precision : dict
                Precision of the binned image
            components : dict
                Various components used in the calculation
    """
    name = props["name"]
    r0 = props["r0"]
    r1 = props["r1"]

    adql = f"""
    SELECT *
        FROM gaiadr3.gaia_source AS gaia
        WHERE gaia.source_id = {source_id}
    """
    job = Gaia.launch_job_async(adql)
    params = job.get_results().to_pandas()

    if Teff is None:
        Teff = float(params["teff_gspphot"].iloc[0])
    if distance is None:
        distance = 1 / (float(params["parallax"].iloc[0]) * 1e-3)  # pc

    if np.isnan(Teff):
        logger.warning(f"Teff value for source_id {source_id} is NaN.")
        Teff = 3000  # K
        logger.warning(f"Setting Teff to {Teff} K.")
    if np.isnan(distance):
        logger.warning(f"Distance value for source_id {source_id} is NaN.")
        distance = 10  # pc
        logger.warning(f"Setting distance to {distance} pc.")

    gaia_filters = np.array(["bp", "g", "rp"])
    gaia_fluxes = np.array([])
    mphot_fluxes = np.array([])

    # Determine used Gaia filters and weights
    if gaia_filter:
        filter_index = np.nonzero(gaia_filters == gaia_filter)[0][0]
        weights_vec = np.zeros(3)
        weights_vec[filter_index] = 1

        weights = 1
        gaia_filters = np.array([gaia_filter])
    else:
        weights = best_gaia_filters(
            name, min_weight_sum=min_weight_sum, support_points=support_points
        )
        weights_vec = weights

    for g_filter in gaia_filters:
        gaia_str = f"phot_{g_filter}_mean_flux"
        gaia_flux = float(params[gaia_str].iloc[0] / 0.7278)
        gaia_fluxes = np.append(gaia_fluxes, gaia_flux)

        # Get simulated Gaia flux
        props_instrument_gaia = props.copy()
        props_instrument_gaia["name"] = f"gaia_{g_filter}_inverse_atmosphere_paranal"

        ## Ideal conditions
        props_sky_gaia = {
            "pwv": 0.05,
            "airmass": 1,
            "seeing": props["plate_scale"],
        }

        _, _, components_gaia = get_precision(
            props_instrument_gaia,
            props_sky_gaia,
            Teff,
            distance,
            binning=binning,
            override_grid=override_grid,
            SPCcorrection=SPCcorrection,
            N_sky=N_sky,
            scn=scn,
            h=h,
            C=C,
            exp_time=exp_time,
        )

        mphot_flux = components_gaia["N_star [e/s]"] / (np.pi * (r0**2 - r1**2))
        mphot_fluxes = np.append(mphot_fluxes, mphot_flux)

    factor = np.sum(weights * gaia_fluxes) / np.sum(weights * mphot_fluxes)

    # Calibrate simulated flux
    _, _, components = get_precision(
        props,
        props_sky,
        Teff,
        distance,
        binning=binning,
        override_grid=override_grid,
        SPCcorrection=SPCcorrection,
        N_sky=N_sky,
        scn=scn,
        h=h,
        C=C,
        exp_time=exp_time,
    )

    N_star_cal = components["N_star [e/s]"] * factor

    image_precision, binned_precision, components_final = get_precision(
        props,
        props_sky,
        Teff,
        distance,
        binning=binning,
        override_grid=False,
        SPCcorrection=SPCcorrection,
        N_star=N_star_cal,
        N_sky=N_sky,
        scn=scn,
        h=h,
        C=C,
        exp_time=exp_time,
    )

    components_final["Gaia-BP weight"] = weights_vec[0]
    components_final["Gaia-G weight"] = weights_vec[1]
    components_final["Gaia-RP weight"] = weights_vec[2]

    return image_precision, binned_precision, components_final


def vega_mag(
    SRFile: str,
    props_sky: dict,
    N_star: float,
    sky_radiance: float,
    A: float,
) -> dict:
    """
    Calculate the Vega magnitude for a given spectral response file and sky properties.

    Args:
        SRFile (str):
            Path to the spectral response CSV file.
        props_sky (dict):
            Dictionary containing properties of the sky.
            Expected keys:
            - "pwv": float, precipitable water vapor
            - "airmass": float, airmass of the observation
        N_star (float):
            Number of star counts.
        sky_radiance (float):
            Sky radiance value.
        A (float):
            Aperture area in square meters.

    Returns:
        dict:
            A dictionary containing the Vega magnitude information:
            - "star [mag]": Vega magnitude of the star.
            - "sky [mag/arcsec2]": Vega magnitude of the sky per arcsecond squared.
            - "vega_flux [e/s]": Vega flux in electrons per second.
    """

    gridIngredients = pd.read_pickle(
        Path(__file__).parent / "datafiles" / grid_flux_ingredients_name
    )
    vega = pd.read_csv(
        Path(__file__).parent / "datafiles" / vega_file,
        header=None,
        index_col=0,
    )

    rsr = pd.read_csv(SRFile, header=None, index_col=0)
    rsr = rsr[1].rename("rsr")

    vega = vega[1].rename("vega")

    gridSauce = interpolate_dfs(wavelengths, rsr, gridIngredients, vega)

    gridSauce = gridSauce[(gridSauce["rsr"] > 0)]

    pwv_values = np.array(
        [0.05, 0.1, 0.25, 0.5, 1.0, 1.5, 2.5, 3.5, 5.0, 7.5, 10.0, 20.0, 30.0]
    )
    airmass_values = np.array(
        [
            1.0,
            1.1,
            1.2,
            1.3,
            1.4,
            1.5,
            1.6,
            1.7,
            1.8,
            1.9,
            2.0,
            2.1,
            2.2,
            2.3,
            2.4,
            2.5,
            2.6,
            2.7,
            2.8,
            2.9,
            3.0,
        ]
    )

    pwv = props_sky["pwv"]
    airmass = props_sky["airmass"]

    # lazy way to get atmosphere profile
    pwv = min(pwv_values, key=lambda x: abs(x - pwv))
    airmass = min(airmass_values, key=lambda x: abs(x - airmass))

    atmosphere_trans = gridSauce[str(pwv) + "_" + str(airmass)]

    simStar = gridSauce["vega"]

    vega = simps(
        y=gridSauce["rsr"] * atmosphere_trans * simStar, x=gridSauce.index
    )  # e/s/m2

    vega_dict = {
        "star [mag]": -2.5 * np.log10(N_star / (vega * A)),
        "sky [mag/arcsec2]": -2.5 * np.log10(sky_radiance / vega),
        "vega_flux [e/s]": vega * A,
    }

    return vega_dict


def update_progress(progress: float | int) -> None:
    """
    Updates and displays a progress bar in the console.

    Args:
        progress (float or int): A number between 0 and 1 representing the progress percentage.
                                 If an integer is provided, it will be converted to a float.
                                 Values less than 0 will be treated as 0, and values greater than or equal to 1 will be treated as 1.

    Returns:
        None
    """

    bar_length = 20
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
    if progress < 0:
        progress = 0
    if progress >= 1:
        progress = 1

    block = int(round(bar_length * progress))

    clear_output(wait=True)
    text = "Progress: [{0}] {1:.1f}%".format(
        "#" * block + "-" * (bar_length - block), progress * 100
    )
    print(text)


def display_number(x: float, p: int = 3) -> str:
    """
    Convert a number to a string with the given precision.

    Args:
        x (float): The number to be converted.
        p (int, optional): The precision (number of significant digits). Default is 3.

    Returns:
        str: The number represented as a string with the specified precision.

    Examples:
    >>> display_number(123.456, 4)
    '123.5'
    >>> display_number(0.00123456, 2)
    '0.0012'
    >>> display_number(123456, 2)
    '1.2e+05'
    """

    x = float(x)

    if x == 0.0:
        return "0." + "0" * (p - 1)

    out = []

    if x < 0:
        out.append("-")
        x = -x

    e = int(math.log10(x))
    tens = math.pow(10, e - p + 1)
    n = math.floor(x / tens)

    if n < math.pow(10, p - 1):
        e = e - 1
        tens = math.pow(10, e - p + 1)
        n = math.floor(x / tens)

    if abs((n + 1.0) * tens - x) <= abs(n * tens - x):
        n = n + 1

    if n >= math.pow(10, p):
        n = n / 10.0
        e = e + 1

    m = "%.*g" % (p, n)

    if e < -2 or e >= p:
        out.append(m[0])
        if p > 1:
            out.append(".")
            out.extend(m[1:p])
        out.append("e")
        if e > 0:
            out.append("+")
        out.append(str(e))
    elif e == (p - 1):
        out.append(m)
    elif e >= 0:
        out.append(m[: e + 1])
        if e + 1 < len(m):
            out.append(".")
            out.extend(m[e + 1 :])
    else:
        out.append("0.")
        out.extend(["0"] * -(e + 1))
        out.append(m)

    return "".join(out)


def display_results(r1: tuple, r2: tuple = None) -> None:
    """
    Display the results of the photometric analysis.

    Args:
        props_sky (dict):
            Dictionary containing properties of the sky.
        r1 (tuple):
            A tuple containing image precision, binned precision, and components for the first set of results.
                - image_precision1 (dict):
                    Dictionary containing image precision metrics for the first set.
                - binned_precision1 (dict):
                    Dictionary containing binned precision metrics for the first set.
                - components1 (dict):
                    Dictionary containing components for the first set.
        r2 (tuple, optional):
            A tuple containing image precision, binned precision, and components for the second set of results.
                - image_precision2 (dict):
                    Dictionary containing image precision metrics for the second set.
                - binned_precision2 (dict):
                    Dictionary containing binned precision metrics for the second set.
                - components2 (dict):
                    Dictionary containing components for the second set.

    Returns:
        None
            This function displays the results using pandas DataFrames and does not return any value.
    """

    pd.set_option("display.float_format", display_number)

    image_precision1, binned_precision1, components1 = r1

    # Copy the values to avoid directly editing the original dictionaries
    image_precision1 = image_precision1.copy()
    binned_precision1 = binned_precision1.copy()
    components1 = components1.copy()
    name1 = components1["name"]
    components1.pop("name")

    props_sky1 = {
        "pwv": components1["pwv [mm]"],
        "airmass": convert_airmass(components1["airmass"], components1["altitude [m]"]),
        "seeing": components1["seeing [arcsec]"],
    }

    SRFile1 = (
        Path(__file__).parent
        / "datafiles"
        / "system_responses"
        / f"{name1}_instrument_system_response.csv"
    )

    vega1 = vega_mag(
        SRFile1,
        props_sky1,
        components1["N_star [e/s]"],
        components1["sky_radiance [e/m2/arcsec2/s]"],
        components1["A [m2]"],
    )

    if r2 is not None:
        image_precision2, binned_precision2, components2 = r2

        # Copy the values to avoid directly editing the original dictionaries
        image_precision2 = image_precision2.copy()
        binned_precision2 = binned_precision2.copy()
        components2 = components2.copy()
        name2 = components2["name"]
        components2.pop("name")

        props_sky2 = {
            "pwv": components2["pwv [mm]"],
            "airmass": convert_airmass(
                components2["airmass"], components2["altitude [m]"]
            ),
            "seeing": components2["seeing [arcsec]"],
        }

        SRFile2 = (
            Path(__file__).parent
            / "datafiles"
            / "system_responses"
            / f"{name2}_instrument_system_response.csv"
        )

        vega2 = vega_mag(
            SRFile2,
            props_sky2,
            components2["N_star [e/s]"],
            components2["sky_radiance [e/m2/arcsec2/s]"],
            components2["A [m2]"],
        )

        columns = [
            [
                "single frame [ppt]",
                "single frame [ppt]",
                f"{components1['binning [mins]']} minute binned [ppt]",
                f"{components2['binning [mins]']} minute binned [ppt]",
            ],
            [name1, name2, name1, name2],
        ]
        values = (
            np.c_[
                list(image_precision1.values()),
                list(image_precision2.values()),
                list(binned_precision1.values()),
                list(binned_precision2.values()),
            ]
            * 1000  # convert to ppt
        )
        display(pd.DataFrame(values, index=image_precision1.keys(), columns=columns))

        columns = [[name1, name2]]

        for k, v in components1.items():
            if not isinstance(v, (str, bool)):
                components1[k] = display_number(v)

        for k, v in components2.items():
            if not isinstance(v, (str, bool)):
                components2[k] = display_number(v)

        values = np.c_[list(components1.values()), list(components2.values())]
        display(pd.DataFrame(values, index=components1.keys(), columns=columns))

        columns = [[name1, name2]]
        values = np.c_[list(vega1.values()), list(vega2.values())]
        display(pd.DataFrame(values, index=vega1.keys(), columns=columns))

    else:
        columns = [
            [
                "single frame [ppt]",
                f"{components1['binning [mins]']} minute binned [ppt]",
            ],
            [name1, name1],
        ]
        values = (
            np.c_[
                list(image_precision1.values()),
                list(binned_precision1.values()),
            ]
            * 1000  # convert to ppt
        )
        display(pd.DataFrame(values, index=image_precision1.keys(), columns=columns))

        columns = [[name1]]

        for k, v in components1.items():
            if (type(v) != str) and (type(v) != bool):
                components1[k] = display_number(v)

        values = np.c_[list(components1.values())]
        display(pd.DataFrame(values, index=components1.keys(), columns=columns))

        columns = [[name1]]
        values = np.c_[list(vega1.values())]
        display(pd.DataFrame(values, index=vega1.keys(), columns=columns))
