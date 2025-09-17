from typing import TYPE_CHECKING

import pytest
import xobjects as xo
import xtrack as xt
from cpymad.madx import Madx
from ibs_conftest import (
    XTRACK_TEST_DATA,
    get_madx_ibs_growth_rates,
    get_parameters_from_madx_beam,
    get_ref_particle_from_madx_beam,
    set_madx_beam_parameters,
)

if TYPE_CHECKING:
    from xfields.ibs import IBSAmplitudeGrowthRates, IBSEmittanceGrowthRates

# ------------------------------------------------------------------------
# We compare our values to the ones of MAD-X, hence in the numpy function
# ours should be the first argument.
#
# We also use an absolute tolerance of 1e-8 by default, as growth rates
# this small or smaller should not be considered since the corresponding
# damping / growth time is crazy big:
#     if T = 1e-8 [1/s],
#     then tau = 1/T > 3 years,
#     and we are pretty safe from IBS.
#
# PLEASE NOTE: MAD-X computes the EMITTANCE growth times in [s], which the
# tests helpers convert to EMITTANCE growth rates in [1/s]. In Xsuite by
# convention we return the AMPLITUDE growth rates (to align with SR damping).
# In the tests, Xsuite results are first converted to emittance convention
# before comparing to the MAD-X values. This way we compare
# EMITTANCE GROWTH RATES (in [1/s]).

# ----- Test with negative charge particle ----- #


@pytest.mark.parametrize("bunched", [True, False])
def test_clic_dr_growth_rates(bunched):
    """Compare to MAD-X for the CLIC DR."""
    # -----------------------------------------------------
    # Have MAD-X load CLIC DR sequence, beam etc.
    clic_dr_dir = XTRACK_TEST_DATA / "clic_dr"
    madx = Madx(stdout=False)
    madx.call(str(clic_dr_dir / "sequence.madx"))
    madx.use(sequence="ring")
    # -----------------------------------------------------
    # Set beam parameters and get growth rates (named with
    # a T here because this is how it is in MAD-X)
    set_madx_beam_parameters(
        madx,
        total_beam_intensity=5e9,
        nemitt_x=5.66e-7,
        nemitt_y=3.70e-9,
        sigma_delta=1.75e-3,
        bunch_length=1.58e-3,
        bunched=bunched,
    )
    mad_Tx, mad_Ty, mad_Tz = get_madx_ibs_growth_rates(madx)
    # -----------------------------------------------------
    # Get equivalent xtrack.Line and parameters
    line = xt.Line.from_madx_sequence(madx.sequence.ring)
    line.particle_ref = get_ref_particle_from_madx_beam(madx)
    tw = line.twiss(method="4d")
    npart, gemitt_x, gemitt_y, sigd, bl = get_parameters_from_madx_beam(madx)
    # -----------------------------------------------------
    # Get growth rates with Nagaitsev formalism
    nag_rates = tw.get_ibs_growth_rates(
        formalism="nagaitsev",
        total_beam_intensity=npart,
        gemitt_x=gemitt_x,
        gemitt_y=gemitt_y,
        sigma_delta=sigd,
        bunch_length=bl,
        bunched=bunched,
    )
    # -----------------------------------------------------
    # Get growth rates with Bjorken-Mtingwa formalism
    bm_rates = tw.get_ibs_growth_rates(
        formalism="Bjorken-Mtingwa",
        total_beam_intensity=npart,
        gemitt_x=gemitt_x,
        gemitt_y=gemitt_y,
        sigma_delta=sigd,
        bunch_length=bl,
        bunched=bunched,
    )
    # -----------------------------------------------------
    # We make sure to convert our results to emittance convention
    # which is the convention used in MAD-X before we compare
    nag_rates = nag_rates.to_emittance_growth_rates()
    bm_rates = bm_rates.to_emittance_growth_rates()
    # -----------------------------------------------------
    # Compare the results - Nagaitsev
    if bunched is True:  # in Nagaitsev coasting makes big assumptions
        # Computed with different formalism than MAD-X so 11% isn't crazy
        xo.assert_allclose(nag_rates.Kx, mad_Tx, atol=1e-8, rtol=11.5e-2)
        xo.assert_allclose(nag_rates.Ky, mad_Ty, atol=1e-8, rtol=5e-2)
        xo.assert_allclose(nag_rates.Kz, mad_Tz, atol=1e-8, rtol=5e-2)
    # Compare the results - Bjorken-Mtingwa
    xo.assert_allclose(bm_rates.Kx, mad_Tx, atol=1e-8, rtol=11.5e-2)
    xo.assert_allclose(bm_rates.Ky, mad_Ty, atol=1e-8, rtol=5e-2)
    xo.assert_allclose(bm_rates.Kz, mad_Tz, atol=1e-8, rtol=5e-2)


# ----- Test with positive charge particle ----- #


@pytest.mark.parametrize("bunched", [True, False])
def test_sps_injection_protons_growth_rates(bunched):
    """Compare to MAD-X for the SPS injection protons."""
    # -----------------------------------------------------
    # Have MAD-X load SPS sequence, beam etc.
    sps_dir = XTRACK_TEST_DATA / "sps_w_spacecharge"
    madx = Madx(stdout=False)
    madx.call(str(sps_dir / "sps_thin.seq"))
    madx.use(sequence="sps")
    # -----------------------------------------------------
    # Beam is fully setup in file, get growth rates (named
    # with a T here because this is how it is in MAD-X)
    madx.sequence.sps.beam.bunched = bunched
    mad_Tx, mad_Ty, mad_Tz = get_madx_ibs_growth_rates(madx)
    # -----------------------------------------------------
    # Get equivalent xtrack.Line and parameters
    line = xt.Line.from_madx_sequence(madx.sequence.sps)
    line.particle_ref = get_ref_particle_from_madx_beam(madx)
    tw = line.twiss(method="4d")
    npart, gemitt_x, gemitt_y, sigd, bl = get_parameters_from_madx_beam(madx)
    # -----------------------------------------------------
    # Get growth rates with Nagaitsev formalism
    nag_rates = tw.get_ibs_growth_rates(
        formalism="nagaitsev",
        total_beam_intensity=npart,
        gemitt_x=gemitt_x,
        gemitt_y=gemitt_y,
        sigma_delta=sigd,
        bunch_length=bl,
        bunched=bunched,
    )
    # -----------------------------------------------------
    # Get growth rates with Bjorken-Mtingwa formalism
    bm_rates = tw.get_ibs_growth_rates(
        formalism="Bjorken-Mtingwa",
        total_beam_intensity=npart,
        gemitt_x=gemitt_x,
        gemitt_y=gemitt_y,
        sigma_delta=sigd,
        bunch_length=bl,
        bunched=bunched,
    )
    # -----------------------------------------------------
    # We make sure to convert our results to emittance convention
    # which is the convention used in MAD-X before we compare
    nag_rates = nag_rates.to_emittance_growth_rates()
    bm_rates = bm_rates.to_emittance_growth_rates()
    # -----------------------------------------------------
    # Compare the results - Nagaitsev
    if bunched is True:  # in Nagaitsev coasting makes big assumptions
        # Computed with different formalism than MAD-X so 10% isn't crazy
        xo.assert_allclose(nag_rates.Kx, mad_Tx, atol=1e-8, rtol=2.5e-2)
        xo.assert_allclose(nag_rates.Ky, mad_Ty, atol=1e-8, rtol=10e-2)
        xo.assert_allclose(nag_rates.Kz, mad_Tz, atol=1e-8, rtol=2.5e-2)
    # Compare the results - Bjorken-Mtingwa
    xo.assert_allclose(bm_rates.Kx, mad_Tx, atol=1e-8, rtol=2.5e-2)
    xo.assert_allclose(bm_rates.Ky, mad_Ty, atol=1e-8, rtol=2.5e-2)
    xo.assert_allclose(bm_rates.Kz, mad_Tz, atol=1e-8, rtol=2.5e-2)


# ----- Test with ion particles ----- #


@pytest.mark.parametrize("bunched", [True, False])
def test_sps_ions_growth_rates(bunched):
    """Compare to MAD-X for the SPS injection ions."""
    # -----------------------------------------------------
    # Have MAD-X load SPS sequence
    sps_dir = XTRACK_TEST_DATA / "sps_w_spacecharge"
    madx = Madx(stdout=False)
    madx.call(str(sps_dir / "sps_thin.seq"))
    madx.command.resbeam()
    # Ugly but let's just define an ion beam I know works
    madx.input(
        """
    beam, particle=ion, sequence=default_beam, bunched=true, radiate=false, mass=193.6872729,
               charge=82.0, energy=36994.8, pc=36994.292969055605, gamma=191.00274089304915,
               beta=0.9999862945347887, brho=1504.8741294778524, ex=6.603137104875076e-09,
               exn=1.2611999999541021e-06, ey=4.7544471970639516e-09, eyn=9.080999999669522e-07,
               et=0.001, sigt=0.19699092426253756, sige=0.0002122804713075153, kbunch=1.0,
               npart=349999999.99999994, bcurrent=2.432286253834961e-06, freq0=0.04337527083539999,
               circ=6911.5038, dtbyds=0.0, deltap=0.0, alfa=2.7410742582906136e-05, u0=0.0, qs=0.0,
               arad=4.9989457074038745e-17, bv=1.0, pdamp={1.0,1.0,2.0}, n1min=-1.0;
    """
    )
    madx.use(sequence="sps")
    # -----------------------------------------------------
    # Beam is fully setup in file, get growth rates (named
    # with a T here because this is how it is in MAD-X)
    madx.sequence.sps.beam.bunched = bunched
    mad_Tx, mad_Ty, mad_Tz = get_madx_ibs_growth_rates(madx)
    # -----------------------------------------------------
    # Get equivalent xtrack.Line and parameters
    line = xt.Line.from_madx_sequence(madx.sequence.sps)
    line.particle_ref = get_ref_particle_from_madx_beam(madx)
    tw = line.twiss(method="4d")
    npart, gemitt_x, gemitt_y, sigd, bl = get_parameters_from_madx_beam(madx)
    # -----------------------------------------------------
    # Get growth rates with Nagaitsev formalism
    nag_rates = tw.get_ibs_growth_rates(
        formalism="nagaitsev",
        total_beam_intensity=npart,
        gemitt_x=gemitt_x,
        gemitt_y=gemitt_y,
        sigma_delta=sigd,
        bunch_length=bl,
        bunched=bunched,
    )
    # -----------------------------------------------------
    # Get growth rates with Bjorken-Mtingwa formalism
    bm_rates = tw.get_ibs_growth_rates(
        formalism="Bjorken-Mtingwa",
        total_beam_intensity=npart,
        gemitt_x=gemitt_x,
        gemitt_y=gemitt_y,
        sigma_delta=sigd,
        bunch_length=bl,
        bunched=bunched,
    )
    # -----------------------------------------------------
    # We make sure to convert our results to emittance convention
    # which is the convention used in MAD-X before we compare
    nag_rates = nag_rates.to_emittance_growth_rates()
    bm_rates = bm_rates.to_emittance_growth_rates()
    # -----------------------------------------------------
    # Compare the results - Nagaitsev
    if bunched is True:  # in Nagaitsev coasting makes big assumptions
        # Computed with different formalism than MAD-X so 10% isn't crazy
        xo.assert_allclose(nag_rates.Kx, mad_Tx, atol=1e-8, rtol=2.5e-2)
        xo.assert_allclose(nag_rates.Ky, mad_Ty, atol=1e-8, rtol=2.5e-2)
        xo.assert_allclose(nag_rates.Kz, mad_Tz, atol=1e-8, rtol=2.5e-2)
    # Compare the results - Bjorken-Mtingwa
    xo.assert_allclose(bm_rates.Kx, mad_Tx, atol=1e-8, rtol=2.5e-2)
    xo.assert_allclose(bm_rates.Ky, mad_Ty, atol=1e-8, rtol=2.5e-2)
    xo.assert_allclose(bm_rates.Kz, mad_Tz, atol=1e-8, rtol=2.5e-2)


# ----- Test with vertical dispersion ----- #


@pytest.mark.parametrize("bunched", [True, False])
def test_hllhc14_growth_rates(bunched):
    """
    Compare to MAD-X for the HLLHC14 protons.
    The lattice has vertical dispersion so Nagaitsev
    vertical growth rate will be blatantly wrong.
    """
    # -----------------------------------------------------
    # Have MAD-X load HLLHC sequence, beam etc. as done in
    # the script next to it that creates the xtrack.Line
    hllhc14_dir = XTRACK_TEST_DATA / "hllhc14_input_mad"
    madx = Madx(stdout=False)
    madx.call(str(hllhc14_dir / "final_seq.madx"))
    madx.use(sequence="lhcb1")
    # -----------------------------------------------------
    # Beam is fully setup in file, get growth rates (named
    # with a T here because this is how it is in MAD-X)
    madx.sequence.lhcb1.beam.bunched = bunched
    mad_Tx, mad_Ty, mad_Tz = get_madx_ibs_growth_rates(madx)
    # -----------------------------------------------------
    # Get equivalent xtrack.Line and parameters
    line = xt.Line.from_madx_sequence(madx.sequence.lhcb1)
    line.particle_ref = get_ref_particle_from_madx_beam(madx)
    tw = line.twiss(method="4d")
    npart, gemitt_x, gemitt_y, sigd, bl = get_parameters_from_madx_beam(madx)
    # -----------------------------------------------------
    # Get growth rates with Nagaitsev formalism
    nag_rates = tw.get_ibs_growth_rates(
        formalism="nagaitsev",
        total_beam_intensity=npart,
        gemitt_x=gemitt_x,
        gemitt_y=gemitt_y,
        sigma_delta=sigd,
        bunch_length=bl,
        bunched=bunched,
    )
    # -----------------------------------------------------
    # Get growth rates with Bjorken-Mtingwa formalism
    bm_rates = tw.get_ibs_growth_rates(
        formalism="Bjorken-Mtingwa",
        total_beam_intensity=npart,
        gemitt_x=gemitt_x,
        gemitt_y=gemitt_y,
        sigma_delta=sigd,
        bunch_length=bl,
        bunched=bunched,
    )
    # -----------------------------------------------------
    # We make sure to convert our results to emittance convention
    # which is the convention used in MAD-X before we compare
    nag_rates = nag_rates.to_emittance_growth_rates()
    bm_rates = bm_rates.to_emittance_growth_rates()
    # -----------------------------------------------------
    # Compare the results - Nagaitsev (don't compare vertical
    # as lattice has Dy and formalism is wrong in this case)
    if bunched is True:  # in Nagaitsev coasting makes big assumptions
        xo.assert_allclose(nag_rates.Kx, mad_Tx, atol=1e-8, rtol=4e-2)
        # Not Ky - Nagaitsev does not account for vertical dispersion
        xo.assert_allclose(nag_rates.Kz, mad_Tz, atol=1e-8, rtol=2.5e-2)
    # Compare the results - Bjorken-Mtingwa
    xo.assert_allclose(bm_rates.Kx, mad_Tx, atol=1e-8, rtol=4e-2)
    xo.assert_allclose(bm_rates.Ky, mad_Ty, atol=1e-8, rtol=2.5e-2)
    xo.assert_allclose(bm_rates.Kz, mad_Tz, atol=1e-8, rtol=2.5e-2)


# ----- Test for conversion between conventions ----- #


def test_convention_conversions():
    """
    Make sure conversions and conventions are ok.
    We test with SPS because it's faster.
    """
    # -----------------------------------------------------
    # Have MAD-X load SPS sequence, beam etc.
    sps_dir = XTRACK_TEST_DATA / "sps_w_spacecharge"
    madx = Madx(stdout=False)
    madx.call(str(sps_dir / "sps_thin.seq"))
    madx.use(sequence="sps")
    # -----------------------------------------------------
    # Get equivalent xtrack.Line and parameters
    line = xt.Line.from_madx_sequence(madx.sequence.sps)
    line.particle_ref = get_ref_particle_from_madx_beam(madx)
    tw = line.twiss(method="4d")
    npart, gemitt_x, gemitt_y, sigd, bl = get_parameters_from_madx_beam(madx)
    # -----------------------------------------------------
    # Note: the validity of the values themselves is tested
    # in the above tests, here we just check the conversions
    # -----------------------------------------------------
    # Get growth rates with Nagaitsev formalism
    amp_rates: IBSAmplitudeGrowthRates = tw.get_ibs_growth_rates(
        formalism="nagaitsev",
        total_beam_intensity=npart,
        gemitt_x=gemitt_x,
        gemitt_y=gemitt_y,
        sigma_delta=sigd,
        bunch_length=bl,
    )
    # We do a first conversion to get the emittance version
    emit_rates: IBSEmittanceGrowthRates = amp_rates.to_emittance_growth_rates()
    # -----------------------------------------------------
    # Check that the factor 2 is correct between conventions
    # Specifically for rates, emit. is twice amp. convention
    xo.assert_allclose(emit_rates.Kx, 2 * amp_rates.Kx, atol=0, rtol=1e-5)
    xo.assert_allclose(emit_rates.Ky, 2 * amp_rates.Ky, atol=0, rtol=1e-5)
    xo.assert_allclose(emit_rates.Kz, 2 * amp_rates.Kz, atol=0, rtol=1e-5)
    # -----------------------------------------------------
    # Check they both give the same amplitude rise times
    atimes1 = amp_rates.to_amplitude_growth_times()
    atimes2 = emit_rates.to_amplitude_growth_times()
    assert atimes1 == atimes2  # they're both tuples
    # -----------------------------------------------------
    # Check they both give the same emittance rise times
    etimes1 = amp_rates.to_emittance_growth_times()
    etimes2 = emit_rates.to_emittance_growth_times()
    assert etimes1 == etimes2  # they're both tuples
    # -----------------------------------------------------
    # Check they both give the same amplitude growth rates
    # I have implemented __eq__ so we can compare like this
    arates1 = amp_rates
    arates2 = emit_rates.to_amplitude_growth_rates()
    assert arates1 == arates2
    # -----------------------------------------------------
    # Check they both give the same emittance growth rates
    # I have implemented __eq__ so we can compare like this
    erates1 = emit_rates
    erates2 = amp_rates.to_emittance_growth_rates()
    assert erates1 == erates2
