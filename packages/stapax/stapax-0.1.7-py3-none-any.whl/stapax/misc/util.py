import jax
import jax.numpy as jnp
import jax.scipy as jsp


def transform_intervals(x: jnp.ndarray) -> jnp.ndarray:
    """
    Linearly transforms the interval (-1,1) on to (0,1).
    """
    return 0.5 + 0.5 * x


def inv_tril_matrix(L: jnp.ndarray) -> jnp.ndarray:
    """
    Compute the inverses of a batch of lower triangular matrices using JAX.

    Parameters:
    L : jax.numpy.ndarray
        A 3D array of shape (batch_size, n, n) with lower triangular matrices (assumed nonsingular).

    Returns:
    jax.numpy.ndarray
        The batch of inverses, shape (batch_size, n, n).
    """

    def invert_single(lower_matrix):
        n = lower_matrix.shape[-1]
        I = jnp.eye(n)
        return jsp.linalg.solve_triangular(lower_matrix, I, lower=True)

    # Vectorize over the batch dimension
    invert_batched = jax.vmap(invert_single)

    return invert_batched(L)
