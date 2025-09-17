
import jax
import jax.numpy as jnp
from typing import Tuple, Optional
from exojax.spec.spin_rotation import convolve_rigid_rotation
from exojax.utils.grids import velocity_grid as _velocity_grid

from luminare.initial import nmf_weights_and_coefficients
from luminare.continuum import create_design_matrix
from luminare.fourier import eval_at_point
from luminare.scalers import periodic_scalers
from luminare.utils import air_to_vacuum

import equinox as eqx

class StellarSpectrumModel(eqx.Module):
    model: callable
    n_parameters: int
    label_names: Tuple[str, ...]
    transform: callable
    inverse_transform: callable

    def __call__(self, θ):
        return self.model(θ)
    

def create_stellar_spectrum_model(
    λ: jnp.array,
    H: jnp.ndarray,
    X: jnp.ndarray,
    n_modes: Tuple[int, ...],
    stellar_label_names: Tuple[str, ...],
    min_stellar_labels: Optional[jnp.array],
    max_stellar_labels: Optional[jnp.array],
    n_stellar_label_points: Optional[jnp.array],
    λ_model: Optional[jnp.array] = None,    
    spectral_resolution: Optional[float] = None,
    max_vsini: Optional[float] = 200.0,
    continuum_regions: Optional[Tuple[float, float]] = None,
    continuum_n_modes: Optional[int] = None,
    model_in_air_wavelengths: bool = False,
    **kwargs
):  
    λ = jnp.array(λ)

    if continuum_regions is None and continuum_n_modes is None:
        continuum_model = lambda *_: 1
        n_continuum_model_parameters = 0
        A = jnp.empty((len(λ), 0))
    else:
        A = create_design_matrix(λ, continuum_regions, continuum_n_modes)
        continuum_model = lambda θ: A @ θ
        n_continuum_model_parameters = A.shape[1]

    rectified_flux_model = lambda θ: rectified_flux(θ, H, X, n_modes)
    n_flux_model_parameters = len(n_modes)

    if spectral_resolution is not None and max_vsini is not None:
        velocity_grid = _velocity_grid(spectral_resolution, max_vsini)
        p = len(λ)
        if p % 2 > 0:
            # TODO: fix this hack
            _flux_model = lambda θ: jnp.hstack([
                convolved_flux(
                    rectified_flux_model(θ[:-1])[:-1], 
                    θ[-1],
                    velocity_grid,
                    max_vsini
                ),
                1.0
            ])
        else:
            _flux_model = lambda θ: convolved_flux(
                rectified_flux_model(θ[:-1]), 
                θ[-1], 
                velocity_grid,
                max_vsini
            )
        n_flux_model_parameters += 1
        stellar_label_names = (*stellar_label_names, "vsini") 
    else:
        _flux_model = rectified_flux_model

    if model_in_air_wavelengths:
        if λ_model is not None:
            λ_model = air_to_vacuum(λ_model)
        else:
            λ_model = air_to_vacuum(λ)

    if λ_model is not None:
        # Need to interpolate from λ_model to λ
        def flux_model(θ):            
            return jnp.interp(λ, λ_model, _flux_model(θ))
    else:
        flux_model = _flux_model
        
    forward_model = jax.jit(lambda θ: (
        flux_model(θ[:n_flux_model_parameters])
    *   continuum_model(θ[n_flux_model_parameters:])
    ))

    transform_stellar_labels, inverse_transform_stellar_labels = periodic_scalers(
        *map(
            jnp.array,
            (
                n_stellar_label_points, 
                min_stellar_labels, 
                max_stellar_labels
            )
        )
    )
    n = len(n_stellar_label_points)
    transform = lambda x: jnp.hstack([transform_stellar_labels(x[:n]), x[n:]])
    inverse_transform = lambda x: jnp.hstack([inverse_transform_stellar_labels(x[:n]), x[n:]])
    n_parameters = n_flux_model_parameters + n_continuum_model_parameters


    # TODO: H is actually H.T, fix above
    vsinis = jnp.linspace(0, max_vsini, 20)
    Hi = jnp.array([jnp.interp(λ, λ_model, Hi) for Hi in H]).T
    # Hi should have shape (20, n_components, n_wavelengths)

    f = nmf_weights_and_coefficients(Hi, A, velocity_grid, max_vsini, large=jnp.inf)

    #return (forward_model, n_parameters, stellar_label_names, transform, inverse_transform)
    model = StellarSpectrumModel(
        model=forward_model,
        n_parameters=n_parameters,
        label_names=stellar_label_names,
        transform=transform,
        inverse_transform=inverse_transform,
    )
    return (model, f)
    

def basis_weights(
    θ: jax.Array, 
    X: jax.Array, 
    n_modes: Tuple[int, ...],
    epsilon: float
):
    W = jax.vmap(eval_at_point, in_axes=(None, None, 1))(θ, n_modes, X)
    return jnp.clip(W, epsilon, None)


def rectified_flux(
    θ: jax.Array,
    H: jax.Array,
    X: jax.Array,
    n_modes: Tuple[int, ...],
    epsilon: float = 0.0
):
    W = basis_weights(θ, X, n_modes, epsilon)
    return 1 - W @ H 


def convolved_flux(
    flux: jax.Array,
    vsini: float,
    velocity_grid: jax.Array,
    max_vsini: float
):
    vsini = jnp.clip(vsini, 0.0, max_vsini)
    return jax.lax.cond(
        vsini > 0,
        lambda: convolve_rigid_rotation(flux, velocity_grid, vsini),
        lambda: flux
    )
