"""
Vectorization realted function used by the price engine module
"""
from typing import Callable, Optional, Tuple, TypeVar, Union

import jax
import jax.numpy as jnp
from jax import jit, vmap

F = TypeVar("F", bound=Callable)


def get_vfunction(
    fun: F,
    spots: Union[jax.Array, float],
    strikes: Union[jax.Array, float],
    expires: Union[jax.Array, float],
    vols: Union[jax.Array, float],
    discount_rates: Union[jax.Array, float],
    dividends_rates: Optional[Union[jax.Array, float]] = None,
    are_calls: Optional[Union[jax.Array, bool]] = None,
    dtype: Optional[jnp.dtype] = None,
):
    """
    Returns a vectorized function for the Black-Scholes related functions.

    Args:
        fun (Callable): Function to vectorize.
        spots (Union[jax.Array, float]): Current asset price or array of prices.
        strikes (Union[jax.Array, float]): Option strike price or array of prices.
        expires (Union[jax.Array, float]): Option expiration time or array of times.
        vols (Union[jax.Array, float]): Option volatility value or array of values.
        discount_rates (Union[jax.Array, float]): Risk-free interest rate or array of rates.
        dividend_rates (Union[jax.Array, float], optional): Dividend rate or array of rates. Defaults to None.
        are_calls (Union[jax.Array, bool], optional): Boolean indicating whether option is a
                                                      call or put, or array of booleans. Defaults to None.
        dtype (jnp.dtype, optional): Data type of the output. Defaults to None.

    Returns:
        Vectorized function.
    """
    return jit(
        vmap(
            fun,
            in_axes=_get_vmap_mask(
                spots,
                strikes,
                expires,
                vols,
                discount_rates,
                dividends_rates,
                are_calls,
                dtype,
            ),
        )
    )


def _get_vmap_mask(
    spots: Union[jax.Array, float],
    strikes: Union[jax.Array, float],
    expires: Union[jax.Array, float],
    vols: Union[jax.Array, float],
    discount_rates: Union[jax.Array, float],
    dividend_rates: Optional[Union[jax.Array, float]] = None,
    are_calls: Optional[Union[jax.Array, bool]] = None,
    dtype: Union[jnp.dtype, None] = None,
) -> Tuple[Union[None, int], ...]:
    mask = tuple(
        map(
            lambda x: None if jnp.isscalar(x) else 0,
            [spots, strikes, expires, vols, discount_rates],
        )
    )

    if dividend_rates is not None:
        mask += (0,)

    if are_calls is not None:
        mask += (0,)

        if dtype is not None:
            mask += (None,)

    return mask
