import numpy as np

def _img_to_array(img):
    arr = img.imarr()
    arr = np.squeeze(arr)
    if arr.ndim != 2:
        raise ValueError(f"Expected 2D image array, got shape {arr.shape}")
    return arr

def _flux_center(data):
    h, w = data.shape
    yy, xx = np.mgrid[0:h, 0:w]
    wts = np.maximum(data, 0.0)
    tot = wts.sum()
    if tot <= 0:
        return (w - 1) / 2.0, (h - 1) / 2.0
    xc = (wts * xx).sum() / tot
    yc = (wts * yy).sum() / tot
    return float(xc), float(yc)

def _estimate_background(data, patch_frac=0.12):
    h, w = data.shape
    k = max(1, int(patch_frac * min(h, w)))
    patches = [
        data[0:k, 0:k],
        data[0:k, w - k:w],
        data[h - k:h, 0:k],
        data[h - k:h, w - k:w],
    ]
    means = [p.mean() for p in patches]
    return float(min(means))

def _radial_profile(data, xc, yc, bin_size=1.0):
    h, w = data.shape
    yy, xx = np.mgrid[0:h, 0:w]
    rr = np.sqrt((xx - xc) ** 2 + (yy - yc) ** 2).ravel()
    vv = data.ravel()
    rmax = rr.max()
    nbins = max(1, int(np.ceil((rmax + 1e-9) / bin_size)))
    idx = np.clip((rr / bin_size).astype(int), 0, nbins - 1)
    sum_v = np.bincount(idx, weights=vv, minlength=nbins)
    cnt_v = np.bincount(idx, minlength=nbins)
    with np.errstate(invalid="ignore", divide="ignore"):
        prof = sum_v / np.maximum(cnt_v, 1)
    r_centers = (np.arange(nbins) + 0.5) * bin_size
    return r_centers, prof

def _smooth_profile(prof):
    k = np.array([1, 2, 3, 2, 1], dtype=float)
    k /= k.sum()
    return np.convolve(prof, k, mode="same")

def _fwhm_width(r, prof, peak_idx, background):
    p_peak = prof[peak_idx]
    half = background + 0.5 * (p_peak - background)
    i_left = None
    for i in range(peak_idx, -1, -1):
        if prof[i] <= half:
            i_left = i
            break
    i_right = None
    for i in range(peak_idx, len(prof)):
        if prof[i] <= half:
            i_right = i
            break
    if i_left is not None and i_right is not None and i_right > i_left:
        def interp_x(i0, i1):
            y0, y1 = prof[i0], prof[i1]
            x0, x1 = r[i0], r[i1]
            if y1 == y0:
                return x0
            t = (half - y0) / (y1 - y0)
            return x0 + t * (x1 - x0)
        rL = interp_x(i_left - 1 if i_left > 0 else i_left, i_left)
        rR = interp_x(i_right, i_right + 1 if i_right + 1 < len(prof) else i_right)
        return float(max(1e-6, rR - rL))
    wL = max(0, peak_idx - 3)
    wR = min(len(prof), peak_idx + 4)
    rw = r[wL:wR]
    pw = np.maximum(prof[wL:wR] - background, 0.0)
    sw = pw.sum()
    if sw <= 0:
        return 2.0
    mu = (rw * pw).sum() / sw
    var = (pw * (rw - mu) ** 2).sum() / sw
    return float(max(2.0, 2.355 * np.sqrt(max(var, 1e-12))))

# paste this OVER your existing estimate_ring_parameters in ringfit/extraction.py

def estimate_ring_parameters(img, bin_size=1.0, patch_frac=0.12, threshold_factor=0.25):
    data = _img_to_array(img)
    h, w = data.shape

    bkg = _estimate_background(data, patch_frac=patch_frac)
    pmax = float(np.nanmax(data))
    thr = bkg + threshold_factor * (pmax - bkg)

    yy, xx = np.mgrid[0:h, 0:w]
    mask = data >= thr

    if np.any(mask):
        wts = np.maximum(data - bkg, 0.0) * mask
        tot = wts.sum()
        if tot > 0:
            xc = float((wts * xx).sum() / tot)
            yc = float((wts * yy).sum() / tot)
        else:
            xc, yc = _flux_center(data)
    else:
        xc, yc = _flux_center(data)
        r, prof = _radial_profile(data, xc, yc, bin_size=bin_size)
        ps = _smooth_profile(prof)
        k = int(np.nanargmax(ps))
        return float(r[k]), _fwhm_width(r, ps, k, bkg), float(ps[k]), float(bkg), (xc, yc)

    r_pix = np.hypot(xx[mask] - xc, yy[mask] - yc)
    weights = (data[mask] - bkg).clip(min=0.0)

    if r_pix.size == 0:
        r, prof = _radial_profile(data, xc, yc, bin_size=bin_size)
        ps = _smooth_profile(prof)
        k = int(np.nanargmax(ps))
        return float(r[k]), _fwhm_width(r, ps, k, bkg), float(ps[k]), float(bkg), (xc, yc)

    rmax = float(r_pix.max())
    nbins = max(16, int(np.ceil((rmax + 1e-9) / bin_size)))
    idx = np.clip((r_pix / bin_size).astype(int), 0, nbins - 1)

    # histogram of radii for bright pixels (weighted by intensity above background)
    hist = np.bincount(idx, weights=weights, minlength=nbins)
    k = np.array([1, 2, 3, 2, 1], float); k /= k.sum()
    hist_s = np.convolve(hist, k, mode="same")
    centers = (np.arange(nbins) + 0.5) * bin_size

    pk = int(np.nanargmax(hist_s))
    radius = float(centers[pk])

    half = 0.5 * float(hist_s[pk])
    il = pk
    while il > 0 and hist_s[il] > half:
        il -= 1
    ir = pk
    while ir < nbins - 1 and hist_s[ir] > half:
        ir += 1

    def _interp(i0, i1):
        y0, y1 = hist_s[i0], hist_s[i1]
        x0, x1 = centers[i0], centers[i1]
        if y1 == y0:
            return x0
        t = (half - y0) / (y1 - y0)
        return x0 + t * (x1 - x0)

    if il > 0 and ir < nbins - 1:
        rL = _interp(il, il + 1)
        rR = _interp(ir - 1, ir)
        width = float(max(2.0, rR - rL))
    else:
        width = float(max(2.0, 0.1 * radius))

    # get a representative peak value from the azimuthal profile at this center
    r_prof, prof = _radial_profile(data, xc, yc, bin_size=bin_size)
    ps = _smooth_profile(prof)
    j = int(np.argmin(np.abs(r_prof - radius)))
    peak_val = float(ps[j])

    return radius, width, peak_val, float(bkg), (xc, yc)

def rbp_find_bright_points(img, threshold=None, radius=None, margin=None, max_it=999):
    data = _img_to_array(img)
    if threshold is None or radius is None:
        r0, w0, pmax, bkg, _ = estimate_ring_parameters(img)
        if threshold is None:
            threshold = bkg + 0.5 * (pmax - bkg)
        if radius is None:
            radius = max(1.0, 3.0 * w0)
    h, w = data.shape
    if margin is None:
        margin = int(np.ceil(radius + 1))
    mask = np.ones_like(data, dtype=bool)
    points = []
    for _ in range(max_it):
        masked = data * mask
        peak = masked.max()
        if peak < threshold:
            break
        y, x = np.unravel_index(np.argmax(masked), data.shape)
        if x < margin or x >= (w - margin) or y < margin or y >= (h - margin):
            mask[y, x] = False
            continue
        points.append((x, y))
        y0, y1 = max(0, y - int(radius)), min(h, y + int(radius) + 1)
        x0, x1 = max(0, x - int(radius)), min(w, x + int(radius) + 1)
        yy, xx = np.ogrid[y0:y1, x0:x1]
        dist = np.sqrt((xx - x) ** 2 + (yy - y) ** 2)
        mask[y0:y1, x0:x1][dist <= radius] = False
    return np.array(points)
