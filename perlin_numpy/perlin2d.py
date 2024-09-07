import numpy as np


def interpolant(t):
    return t*t*t*(t*(t*6 - 15) + 10)


def generate_perlin_noise_2d(
        shape, res, tileable=(False, False), interpolant=interpolant
):
    """Generate a 2D numpy array of perlin noise.

    Args:
        shape: The shape of the generated array (tuple of two ints).
            This must be a multple of res.
        res: The number of periods of noise to generate along each
            axis (tuple of two ints).
        tileable: If the noise should be tileable along each axis
            (tuple of two bools). Defaults to (False, False).
        interpolant: The interpolation function, defaults to
            t*t*t*(t*(t*6 - 15) + 10).

    Returns:
        A numpy array of shape shape with the generated noise.

    Raises:
        ValueError: If shape is not a multiple of res.
    """
    # Gradients
    angles = 2*np.pi*np.random.rand(res[0]+1, res[1]+1)
    gradients = np.dstack((np.cos(angles), np.sin(angles)))
    if tileable[0]:
        gradients[-1,:] = gradients[0,:]
    if tileable[1]:
        gradients[:,-1] = gradients[:,0]
    grid = np.stack(np.meshgrid(
        np.arange(0, shape[1]) * res[1] / shape[1],
        np.arange(0, shape[0]) * res[0] / shape[0],
    )[::-1], axis=-1)
    grid_floor = np.floor(grid).astype(int)
    grid_ceil = np.ceil(grid).astype(int)
    g00 = gradients[grid_floor[:,:,0], grid_floor[:,:,1]]
    g10 = gradients[grid_ceil[:,:,0], grid_floor[:,:,1]]
    g01 = gradients[grid_floor[:,:,0], grid_ceil[:,:,1]]
    g11 = gradients[grid_ceil[:,:,0], grid_ceil[:,:,1]]
    grid_frac = grid - grid_floor
    # Ramps
    n00 = np.sum(np.dstack((grid_frac[:,:,0]  , grid_frac[:,:,1]  )) * g00, 2)
    n10 = np.sum(np.dstack((grid_frac[:,:,0]-1, grid_frac[:,:,1]  )) * g10, 2)
    n01 = np.sum(np.dstack((grid_frac[:,:,0]  , grid_frac[:,:,1]-1)) * g01, 2)
    n11 = np.sum(np.dstack((grid_frac[:,:,0]-1, grid_frac[:,:,1]-1)) * g11, 2)
    # Interpolation
    t = interpolant(grid_frac)
    n0 = n00*(1-t[:,:,0]) + t[:,:,0]*n10
    n1 = n01*(1-t[:,:,0]) + t[:,:,0]*n11
    return np.sqrt(2)*((1-t[:,:,1])*n0 + t[:,:,1]*n1)


def generate_fractal_noise_2d(
        shape, res, octaves=1, persistence=0.5,
        lacunarity=2, tileable=(False, False),
        interpolant=interpolant
):
    """Generate a 2D numpy array of fractal noise.

    Args:
        shape: The shape of the generated array (tuple of two ints).
            This must be a multiple of lacunarity**(octaves-1)*res.
        res: The number of periods of noise to generate along each
            axis (tuple of two ints). Note shape must be a multiple of
            (lacunarity**(octaves-1)*res).
        octaves: The number of octaves in the noise. Defaults to 1.
        persistence: The scaling factor between two octaves.
        lacunarity: The frequency factor between two octaves.
        tileable: If the noise should be tileable along each axis
            (tuple of two bools). Defaults to (False, False).
        interpolant: The, interpolation function, defaults to
            t*t*t*(t*(t*6 - 15) + 10).

    Returns:
        A numpy array of fractal noise and of shape shape generated by
        combining several octaves of perlin noise.

    Raises:
        ValueError: If shape is not a multiple of
            (lacunarity**(octaves-1)*res).
    """
    noise = np.zeros(shape)
    frequency = 1
    amplitude = 1
    for _ in range(octaves):
        noise += amplitude * generate_perlin_noise_2d(
            shape, (frequency*res[0], frequency*res[1]), tileable, interpolant
        )
        frequency *= lacunarity
        amplitude *= persistence
    return noise