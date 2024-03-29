"""
Black '76 prices for options on forwards and futures
"""
from typing import Optional, Union

import jax
import jax.numpy as jnp
from jax import grad, jit

from ..math.bs_common import compute_undiscounted_call_prices
from ..utils.arrays import cast_arrays


def black_price(
    spots: jax.Array,
    strikes: jax.Array,
    expires: jax.Array,
    vols: jax.Array,
    discount_rates: jax.Array,
    dividend_rates: Optional[jax.Array] = None,
    are_calls: Optional[jax.Array] = None,
    dtype: Optional[jnp.dtype] = None,
) -> jax.Array:
    """
    Compute the option prices for european options using the Black '76 model.

    :param spots: (jax.Array): Array of current asset prices.
    :param strikes: (jax.Array): Array of option strike prices.
    :param expires: (jax.Array): Array of option expiration times.
    :param vols: (jax.Array): Array of option volatility values.
    :param discount_rates: (jax.Array): Array of risk-free interest rates. Defaults to None.
    :param dividend_rates: (jax.Array): Array of dividend rates. Defaults to None.
    :param are_calls: (jax.Array): Array of booleans indicating whether options are calls (True) or puts (False).
    :param dtype: (jnp.dtype): Data type of the output. Defaults to None.
    :return: (jax.Array): Array of computed option prices.
    """
    shape = spots.shape

    [spots, strikes, expires, vols] = cast_arrays(
        [spots, strikes, expires, vols], dtype
    )

    if dividend_rates is None:
        dividend_rates = jnp.zeros(shape, dtype=dtype)

    discount_factors = jnp.exp((discount_rates - dividend_rates) * expires)
    forwards = discount_factors * spots

    undiscounted_calls = compute_undiscounted_call_prices(
        forwards, strikes, expires, vols, discount_rates
    )

    if are_calls is None:
        return discount_factors * undiscounted_calls

    undiscounted_forwards = forwards - strikes
    undiscouted_puts = undiscounted_calls - undiscounted_forwards
    return jnp.exp((-1 * discount_rates) * expires) * jnp.where(
        are_calls, undiscounted_calls, undiscouted_puts
    )


@jit
def delta_black(
    spots: Union[jax.Array, float],
    strikes: Union[jax.Array, float],
    expires: Union[jax.Array, float],
    vols: Union[jax.Array, float],
    discount_rates: Union[jax.Array, float],
    dividend_rates: Optional[Union[jax.Array, float]] = None,
    are_calls: Optional[jax.Array] = None,
    dtype: Optional[jnp.dtype] = None,
) -> jax.Array:
    """
    Compute the option deltas for european options using the Black '76 model.

    :param spots: (jax.Array): Array of current asset prices.
    :param strikes: (jax.Array): Array of option strike prices.
    :param expires: (jax.Array): Array of option expiration times.
    :param vols: (jax.Array): Array of option volatility values.
    :param discount_rates: (jax.Array): Array of risk-free interest rates. Defaults to None.
    :param dividend_rates: (jax.Array): Array of dividend rates. Defaults to None.
    :param are_calls: (jax.Array): Array of booleans indicating whether options are calls (True) or puts (False).
    :param dtype: (jnp.dtype): Data type of the output. Defaults to None.
    :return: (jax.Array): Array of computed option deltas.
    """
    return grad(black_price, argnums=0)(
        spots, strikes, expires, vols, discount_rates, dividend_rates, are_calls, dtype
    )


@jit
def gamma_black(
    spots: Union[jax.Array, float],
    strikes: Union[jax.Array, float],
    expires: Union[jax.Array, float],
    vols: Union[jax.Array, float],
    discount_rates: Union[jax.Array, float],
    dividend_rates: Optional[Union[jax.Array, float]] = None,
    are_calls: Optional[jax.Array] = None,
    dtype: Optional[jnp.dtype] = None,
) -> jax.Array:
    """
    Compute the option gammas for european options using the Black '76 model.

    :param spots: (jax.Array): Array of current asset prices.
    :param strikes: (jax.Array): Array of option strike prices.
    :param expires: (jax.Array): Array of option expiration times.
    :param vols: (jax.Array): Array of option volatility values.
    :param discount_rates: (jax.Array): Array of risk-free interest rates. Defaults to None.
    :param dividend_rates: (jax.Array): Array of dividend rates. Defaults to None.
    :param are_calls: (jax.Array): Array of booleans indicating whether options are calls (True) or puts (False).
    :param dtype: (jnp.dtype): Data type of the output. Defaults to None.
    :return: (jax.Array): Array of computed option gammas.
    """
    return grad(grad(black_price, argnums=0), argnums=0)(
        spots, strikes, expires, vols, discount_rates, dividend_rates, are_calls, dtype
    )
