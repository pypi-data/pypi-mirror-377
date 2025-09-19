"""MIT License

Copyright (c) 2025 Christian Hågenvik

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from pvtlib import fluid_mechanics
import numpy as np

#%% Test equations for evaluating homogeneous mixtures of oil and water in horizontal and vertical pipes (used in water-cut measurements)
def test_critical_velocity_for_uniform_wio_dispersion_horizontal_1():
    '''
    Test calculation of critical (minimum) velocity for maintaining homogeneous oil water mixture in a horizontal pipe. 
    Test is based on example from NFOGM Handbook of Water Fraction Metering Revision 2, December 2004, Appendix A
    
    Test with 5 cP (0.005 Pa⋅s)
    '''
    
    
    Vc = fluid_mechanics.critical_velocity_for_uniform_wio_dispersion_horizontal(
        ST_oil_aq=0.025, 
        rho_o=800,
        rho_aq=1025, 
        Visc_o=0.005, 
        D=0.1016
        )
    
    assert round(Vc,4) == 3.7731, f'Critical velocity for homogeneous oil water mixture in a horizontal pipe failed'
    

def test_critical_velocity_for_uniform_wio_dispersion_horizontal_2():
    '''
    Test calculation of critical (minimum) velocity for maintaining homogeneous oil water mixture in a horizontal pipe. 
    Test is based on example from NFOGM Handbook of Water Fraction Metering Revision 2, December 2004, Appendix A
    
    Test with 20 cP (0.020 Pa⋅s)
    '''
    
    
    Vc = fluid_mechanics.critical_velocity_for_uniform_wio_dispersion_horizontal(
        ST_oil_aq=0.025, 
        rho_o=800,
        rho_aq=1025, 
        Visc_o=0.020, 
        D=0.1016
        )
    
    assert round(Vc,4) == 2.0759, f'Critical velocity for homogeneous oil water mixture in a horizontal pipe failed'


def test_critical_velocity_for_uniform_wio_dispersion_horizontal_3():
    '''
    Test calculation of critical (minimum) velocity for maintaining homogeneous oil water mixture in a horizontal pipe. 
    Test is based on example from NFOGM Handbook of Water Fraction Metering Revision 2, December 2004, Appendix A
    
    Test if all parameters are zero, should return nan. 
    '''
    
    
    Vc = fluid_mechanics.critical_velocity_for_uniform_wio_dispersion_horizontal(
        ST_oil_aq=0.0, 
        rho_o=0.0,
        rho_aq=0.0, 
        Visc_o=0.0, 
        D=0.0
        )
    
    assert np.isnan(Vc), f'Critical velocity for homogeneous oil water mixture in a horizontal pipe failed'


def test_critical_velocity_for_uniform_wio_dispersion_vertical_1():
    '''
    Test calculation of critical (minimum) velocity for maintaining homogeneous oil water mixture in a vertical pipe. 
    Test is based on example from NFOGM Handbook of Water Fraction Metering Revision 2, December 2004, Appendix A
    
    Test with Betha = 10 vol%
    '''
    
    
    Vc = fluid_mechanics.critical_velocity_for_uniform_wio_dispersion_vertical(
        beta=10.0, 
        ST_oil_aq=0.025, 
        rho_o=800,
        rho_aq=1025, 
        Visc_o=0.005, 
        D=0.1016
        )
    
    assert round(Vc,4) == 1.1062, f'Critical velocity for homogeneous oil water mixture in a vertical pipe failed'
    
    
def test_critical_velocity_for_uniform_wio_dispersion_vertical_2():
    '''
    Test calculation of critical (minimum) velocity for maintaining homogeneous oil water mixture in a vertical pipe. 
    Test is based on example from NFOGM Handbook of Water Fraction Metering Revision 2, December 2004, Appendix A
    
    Test with Betha = 1 vol%
    '''
    
    
    Vc = fluid_mechanics.critical_velocity_for_uniform_wio_dispersion_vertical(
        beta=1.0, 
        ST_oil_aq=0.025, 
        rho_o=800,
        rho_aq=1025, 
        Visc_o=0.005, 
        D=0.1016
        )
    
    assert round(Vc,4) == 0.2651, f'Critical velocity for homogeneous oil water mixture in a vertical pipe failed'    
    
    
def test_critical_velocity_for_uniform_wio_dispersion_vertical_3():
    '''
    Test calculation of critical (minimum) velocity for maintaining homogeneous oil water mixture in a vertical pipe. 
    Test is based on example from NFOGM Handbook of Water Fraction Metering Revision 2, December 2004, Appendix A
    
    Test if all parameters are zero, should return nan.
    '''
    
    
    Vc = fluid_mechanics.critical_velocity_for_uniform_wio_dispersion_vertical(
        beta=100.0, 
        ST_oil_aq=0.0, 
        rho_o=0.0,
        rho_aq=0.0, 
        Visc_o=0.0, 
        D=0.0
        )
    
    assert np.isnan(Vc), f'Critical velocity for homogeneous oil water mixture in a vertical pipe failed'    

def test_critical_velocity_for_uniform_wio_dispersion_vertical_4():
    '''
    Test calculation of critical (minimum) velocity for maintaining homogeneous oil water mixture in a vertical pipe. 
    Test is based on example from NFOGM Handbook of Water Fraction Metering Revision 2, December 2004, Appendix A
    
    Test with Betha > 100 vol%, should return nan
    '''
    
    
    Vc = fluid_mechanics.critical_velocity_for_uniform_wio_dispersion_vertical(
        beta=300.0, 
        ST_oil_aq=0.025, 
        rho_o=800,
        rho_aq=1025, 
        Visc_o=0.005, 
        D=0.1016
        )
    
    assert np.isnan(Vc), f'Critical velocity for homogeneous oil water mixture in a vertical pipe failed'


# Test equations for oil-in-water and water-in-oil
def test_dominant_phase_corrected_density_1():
    '''
    Test calculation of dominant phase corrected density.
    Example: Measured density is 800 kg/m3 and the water fraction is 1 vol%.
    '''
    
    corrected_density = fluid_mechanics.dominant_phase_corrected_density(
        measured_total_density=703,
        ContaminantVolP=1.0,
        ContaminantPhase_EOS_density=1000
    )
    
    assert round(corrected_density, 2) == 700.0, f'Dominant phase corrected density calculation failed'


def test_dominant_phase_corrected_density_2():
    '''
    Test calculation of dominant phase corrected density.
    Example: Measured density is 850 kg/m3 and the water fraction is 5 vol%.
    '''
    
    corrected_density = fluid_mechanics.dominant_phase_corrected_density(
        measured_total_density=850,
        ContaminantVolP=5,
        ContaminantPhase_EOS_density=1000
    )
    
    assert round(corrected_density, 2) == 842.11, f'Dominant phase corrected density calculation failed'


def test_dominant_phase_corrected_density_3():
    '''
    Test calculation of dominant phase corrected density.
    Example: Measured density is 900 kg/m3 and the water fraction is 10 vol%.
    '''
    
    corrected_density = fluid_mechanics.dominant_phase_corrected_density(
        measured_total_density=900,
        ContaminantVolP=10,
        ContaminantPhase_EOS_density=1000
    )
    
    assert round(corrected_density, 2) == 888.89, f'Dominant phase corrected density calculation failed'


def test_dominant_phase_corrected_density_all_zeros():
    '''
    Test calculation of dominant phase corrected density when all parameters are zero.
    Should return nan.
    '''
    
    corrected_density = fluid_mechanics.dominant_phase_corrected_density(
        measured_total_density=0,
        ContaminantVolP=0.0,
        ContaminantPhase_EOS_density=0
    )
    
    assert corrected_density==0.0, f'Dominant phase corrected density calculation failed'


def test_dominant_phase_corrected_density_invalid_fraction():
    '''
    Test calculation of dominant phase corrected density when contaminant volume fraction is 100%.
    Should return nan.
    '''
    
    corrected_density = fluid_mechanics.dominant_phase_corrected_density(
        measured_total_density=800,
        ContaminantVolP=100,
        ContaminantPhase_EOS_density=1000
    )
    
    assert np.isnan(corrected_density), f'Dominant phase corrected density calculation failed'


def test_mass_percent_to_volume_percent_1():
    '''
    Test conversion from mass percentage to volume percentage.
    Example: Mass percentage is 10%, Dominant phase density is 800 kg/m3, Contaminant phase density is 1000 kg/m3.
    '''
    
    ContaminantVolP = fluid_mechanics.mass_percent_to_volume_percent(
        ContaminantMassP=10,
        DominantPhase_EOS_density=800,
        ContaminantPhase_EOS_density=1000
    )
    
    assert round(ContaminantVolP, 2) == 8.16, f'Mass to volume percentage conversion failed'


def test_mass_percent_to_volume_percent_2():
    '''
    Test conversion from mass percentage to volume percentage.
    Example: Mass percentage is 50%, Dominant phase density is 800 kg/m3, Contaminant phase density is 1000 kg/m3.
    '''
    
    ContaminantVolP = fluid_mechanics.mass_percent_to_volume_percent(
        ContaminantMassP=50,
        DominantPhase_EOS_density=800,
        ContaminantPhase_EOS_density=1000
    )
    
    assert round(ContaminantVolP, 2) == 44.44, f'Mass to volume percentage conversion failed'


def test_mass_percent_to_volume_percent_all_zeros():
    '''
    Test conversion from mass percentage to volume percentage when all parameters are zero.
    Should return nan.
    '''
    
    ContaminantVolP = fluid_mechanics.mass_percent_to_volume_percent(
        ContaminantMassP=0,
        DominantPhase_EOS_density=0,
        ContaminantPhase_EOS_density=0
    )
    
    assert np.isnan(ContaminantVolP), f'Mass to volume percentage conversion failed'


def test_mass_percent_to_volume_percent_invalid_density():
    '''
    Test conversion from mass percentage to volume percentage when densities are zero.
    Should return nan.
    '''
    
    ContaminantVolP = fluid_mechanics.mass_percent_to_volume_percent(
        ContaminantMassP=10,
        DominantPhase_EOS_density=0,
        ContaminantPhase_EOS_density=0
    )
    
    assert np.isnan(ContaminantVolP), f'Mass to volume percentage conversion failed'

def test_volume_percent_to_mass_percent_1():
    '''
    Test conversion from volume percentage to mass percentage.
    Example: Volume percentage is 10%, Dominant phase density is 800 kg/m3, Contaminant phase density is 1000 kg/m3.
    '''
    
    ContaminantMassP = fluid_mechanics.volume_percent_to_mass_percent(
        ContaminantVolP=10,
        DominantPhase_EOS_density=800,
        ContaminantPhase_EOS_density=1000
    )
    
    assert round(ContaminantMassP, 2) == 12.2, f'Volume to mass percentage conversion failed'


def test_volume_percent_to_mass_percent_2():
    '''
    Test conversion from volume percentage to mass percentage.
    Example: Volume percentage is 50%, Dominant phase density is 800 kg/m3, Contaminant phase density is 1000 kg/m3.
    '''
    
    ContaminantMassP = fluid_mechanics.volume_percent_to_mass_percent(
        ContaminantVolP=50,
        DominantPhase_EOS_density=800,
        ContaminantPhase_EOS_density=1000
    )
    
    assert round(ContaminantMassP, 2) == 55.56, f'Volume to mass percentage conversion failed'


def test_volume_percent_to_mass_percent_all_zeros():
    '''
    Test conversion from volume percentage to mass percentage when all parameters are zero.
    Should return nan.
    '''
    
    ContaminantMassP = fluid_mechanics.volume_percent_to_mass_percent(
        ContaminantVolP=0,
        DominantPhase_EOS_density=0,
        ContaminantPhase_EOS_density=0
    )
    
    assert np.isnan(ContaminantMassP), f'Volume to mass percentage conversion failed'


def test_volume_percent_to_mass_percent_invalid_density():
    '''
    Test conversion from volume percentage to mass percentage when densities are zero.
    Should return nan.
    '''
    
    ContaminantMassP = fluid_mechanics.volume_percent_to_mass_percent(
        ContaminantVolP=10,
        DominantPhase_EOS_density=0,
        ContaminantPhase_EOS_density=0
    )
    
    assert np.isnan(ContaminantMassP), f'Volume to mass percentage conversion failed'

def test_contaminant_volume_percent_from_mixed_density_1():
    '''
    Test calculation of contaminant volume percent from mixed density.
    Example: Measured density is 850 kg/m3, Dominant phase density is 800 kg/m3, Contaminant phase density is 1000 kg/m3.
    '''
    
    ContaminantVolP = fluid_mechanics.contaminant_volume_percent_from_mixed_density(
        measured_total_density=850,
        DominantPhase_EOS_density=800,
        ContaminantPhase_EOS_density=1000
    )
    
    assert round(ContaminantVolP, 2) == 25.0, f'Contaminant volume percent calculation failed'


def test_contaminant_volume_percent_from_mixed_density_2():
    '''
    Test calculation of contaminant volume percent from mixed density.
    Example: Measured density is 900 kg/m3, Dominant phase density is 800 kg/m3, Contaminant phase density is 1000 kg/m3.
    '''
    
    ContaminantVolP = fluid_mechanics.contaminant_volume_percent_from_mixed_density(
        measured_total_density=900,
        DominantPhase_EOS_density=800,
        ContaminantPhase_EOS_density=1000
    )
    
    assert round(ContaminantVolP, 2) == 50.0, f'Contaminant volume percent calculation failed'


def test_contaminant_volume_percent_from_mixed_density_all_zeros():
    '''
    Test calculation of contaminant volume percent from mixed density when all parameters are zero.
    Should return nan.
    '''
    
    ContaminantVolP = fluid_mechanics.contaminant_volume_percent_from_mixed_density(
        measured_total_density=0,
        DominantPhase_EOS_density=0,
        ContaminantPhase_EOS_density=0
    )
    
    assert np.isnan(ContaminantVolP), f'Contaminant volume percent calculation failed'


def test_contaminant_volume_percent_from_mixed_density_invalid_density():
    '''
    Test calculation of contaminant volume percent from mixed density when densities are equal.
    Should return nan.
    '''
    
    ContaminantVolP = fluid_mechanics.contaminant_volume_percent_from_mixed_density(
        measured_total_density=800,
        DominantPhase_EOS_density=800,
        ContaminantPhase_EOS_density=800
    )
    
    assert np.isnan(ContaminantVolP), f'Contaminant volume percent calculation failed'


def test_contaminant_volume_percent_from_mixed_density_measured_density_greater():
    '''
    Test calculation of contaminant volume percent from mixed density when measured density is greater than dominant phase density.
    Should return 100.
    '''
    
    ContaminantVolP = fluid_mechanics.contaminant_volume_percent_from_mixed_density(
        measured_total_density=1050,
        DominantPhase_EOS_density=800,
        ContaminantPhase_EOS_density=1000
    )
    
    assert ContaminantVolP == 100, f'Contaminant volume percent calculation failed'


def test_contaminant_volume_percent_from_mixed_density_measured_density_lower():
    '''
    Test calculation of contaminant volume percent from mixed density when measured density is lower than contaminant phase density.
    Should return 0.
    '''
    
    ContaminantVolP = fluid_mechanics.contaminant_volume_percent_from_mixed_density(
        measured_total_density=750,
        DominantPhase_EOS_density=800,
        ContaminantPhase_EOS_density=1000
    )
    
    assert ContaminantVolP == 0, f'Contaminant volume percent calculation failed'
