"""Dimensionless parameters."""


def thermal_diffusivity(thermal_conductivity, density, isobaric_specific_heat):
    """Thermal diffusivity."""
    return thermal_conductivity / (density * isobaric_specific_heat)


def kinematic_viscosity(dynamic_viscosity, density):
    """Kinematic viscosity."""
    return dynamic_viscosity / density


def reynolds(velocity, characteristic_length, kinematic_viscosity):
    """Reynolds number."""
    return velocity * characteristic_length / kinematic_viscosity


def prandtl(dynamic_viscosity, isobaric_specific_heat, thermal_conductivity):
    """Prandtl number."""
    return (isobaric_specific_heat * dynamic_viscosity) / thermal_conductivity


def jakob(
    liquid_density,
    vapor_density,
    liquid_isobaric_specific_heat,
    subcooling,
    latent_heat_of_vaporization,
):
    """Jakob number."""
    return (liquid_density * liquid_isobaric_specific_heat * subcooling) / (
        vapor_density * latent_heat_of_vaporization
    )


def fourier(liquid_thermal_diffusivity, initial_bubble_diameter, time):
    """Fourier number."""
    return liquid_thermal_diffusivity * time / initial_bubble_diameter**2


def nusselt(heat_transfer_coefficient, characteristic_length, thermal_conductivity):
    """Nusselt number."""
    return heat_transfer_coefficient * characteristic_length / thermal_conductivity
