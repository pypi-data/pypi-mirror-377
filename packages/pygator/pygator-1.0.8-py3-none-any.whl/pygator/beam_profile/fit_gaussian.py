import numpy as np
from scipy.optimize import curve_fit

def gaussian_2d_rotated(coords, A, x0, y0, w_x, w_y, B, theta=0):
    x, y = coords
    xr = (x - x0) * np.cos(theta) - (y - y0) * np.sin(theta)
    yr = (x - x0) * np.sin(theta) + (y - y0) * np.cos(theta)
    return (A * np.exp(-2 * ((xr / w_x)**2 + (yr / w_y)**2)) + B).ravel()


def fit_gaussian(image):
    y = np.arange(image.shape[0])
    x = np.arange(image.shape[1])
    x, y = np.meshgrid(x, y)

    A_init = np.max(image) - np.min(image)
    x0_init = image.shape[1] / 2
    y0_init = image.shape[0] / 2
    w_x_init = image.shape[1] / 4
    w_y_init = image.shape[0] / 4
    B_init = np.min(image)
    theta_init=0

    initial_guess = (A_init, x0_init, y0_init, w_x_init, w_y_init, B_init,theta_init)

    popt, _ = curve_fit(gaussian_2d, (x, y), image.ravel(), p0=initial_guess)

    return popt


def fit_gaussian_roi(image, roi_size=100, downsample=1, meshgrid_cache={},warn_once=[False],theta_user=0):
    """
    Fit a 2D Gaussian to a small ROI around the brightest pixel.

    Parameters:
    - image: 2D numpy array (grayscale image)
    - roi_size: size of the square ROI (must be even-ish and small, e.g., 50-150)
    - downsample: integer factor to downsample the image for fitting
    - meshgrid_cache: dict to store cached meshgrids to avoid recomputation

    Returns:
    - params: (A, x0, y0, w_x, w_y, B) with coordinates scaled back to full-res
    """
    # --- Check for saturation ---
    bit_depth_max = 255  # adjust as needed
    saturated_mask = image >= bit_depth_max
    num_saturated = np.sum(saturated_mask)

    if num_saturated > 0 and not warn_once[0]:
        total_pixels = image.size
        percent_saturated = 100.0 * num_saturated / total_pixels
        print(f"Warning: {num_saturated} pixels saturated "
              f"({percent_saturated:.3f}% of image). Max = {np.max(image)}")
        warn_once[0] = True   # remember that we already warned

    # Step 1: Find max pixel for ROI center
    max_y, max_x = np.unravel_index(np.argmax(image), image.shape)
    half = roi_size // 2
    y1, y2 = max(0, max_y - half), min(image.shape[0], max_y + half)
    x1, x2 = max(0, max_x - half), min(image.shape[1], max_x + half)
    cropped = image[y1:y2, x1:x2]

    # Step 2: Downsample if needed
    if downsample > 1:
        import cv2
        cropped = cv2.resize(cropped, (cropped.shape[1] // downsample, cropped.shape[0] // downsample),
                             interpolation=cv2.INTER_AREA)

    # Step 3: Meshgrid caching
    h, w = cropped.shape
    if (h, w) not in meshgrid_cache:
        y = np.arange(h)
        x = np.arange(w)
        meshgrid_cache[(h, w)] = np.meshgrid(x, y)
    xg, yg = meshgrid_cache[(h, w)]

    # Step 4: Initial guess
    A_init = np.max(cropped) - np.min(cropped)
    x0_init = w / 2
    y0_init = h / 2
    w_x_init = w / 4
    w_y_init = h / 4
    B_init = np.min(cropped)
    theta_init=0

    # --- Fit with fixed user theta ---
    theta_user_rad = theta_user * np.pi / 180
    fitfun_fixed = lambda coords, A, x0, y0, w_x, w_y, B: gaussian_2d_rotated(
        coords, A, x0, y0, w_x, w_y, B, theta=theta_user_rad
    )
    popt_fixed, _ = curve_fit(
        fitfun_fixed,
        (xg, yg),
        cropped.ravel(),
        p0=(A_init, x0_init, y0_init, w_x_init, w_y_init, B_init),
        maxfev=10000
    )
    A, x0, y0, w_x, w_y, B = popt_fixed

    # --- Fit with free theta (diagnostic only) ---
    try:
        popt_free, _ = curve_fit(
            gaussian_2d_rotated,
            (xg, yg),
            cropped.ravel(),
            p0=(A_init, x0_init, y0_init, w_x_init, w_y_init, B_init, theta_init),
            maxfev=10000
        )
        theta_fit = popt_free[-1]
    except Exception:
        theta_fit = np.nan  # fallback if free fit fails

    # Rescale to full image coords
    x0 = x1 + x0 * downsample
    y0 = y1 + y0 * downsample
    w_x *= downsample
    w_y *= downsample

    return (A, x0, y0, w_x, w_y, B, theta_fit, theta_user_rad)