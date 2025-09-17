#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
StereonetForge — dependency‑light stereonet plotter for planes (Dip / DipDir)

Author: Dr. Aram Fathian
Affiliation: Department of Earth, Energy, and Environment; Water, Sediment, Hazards, and Earth-surface Dynamics (waterSHED) Lab; University of Calgary
License: MIT
"""
from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from typing import Iterable, List, Optional, Sequence, Tuple, Dict

import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

# Keep fonts as text in vector outputs
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype']  = 42
matplotlib.rcParams['svg.fonttype'] = 'none'


# ------------------------- Math / projection helpers -------------------------

def deg2rad(a: float) -> float: return a * math.pi / 180.0
def rad2deg(a: float) -> float: return a * 180.0 / math.pi
def wrap_360(a: float) -> float: return a % 360.0

def trend_plunge_from_vector(vec: np.ndarray) -> Tuple[float, float]:
    """Vector -> (trend, plunge) in degrees for LOWER hemisphere."""
    N,E,D = vec
    if D < 0: N,E,D = -N,-E,-D
    trend = wrap_360(rad2deg(np.arctan2(E, N)))
    plunge = rad2deg(np.arcsin(np.clip(D, -1.0, 1.0)))
    return float(trend), float(plunge)

def vector_from_trend_plunge(trend_deg: float, plunge_deg: float) -> np.ndarray:
    T = deg2rad(trend_deg); P = deg2rad(plunge_deg)
    N = np.cos(P) * np.cos(T)
    E = np.cos(P) * np.sin(T)
    D = np.sin(P)
    v = np.array([N, E, D], dtype=float)
    n = np.linalg.norm(v)
    return v if n == 0 else v / n

def pole_from_plane(dip_deg: float, dipdir_deg: float) -> Tuple[float, float]:
    trend = wrap_360(dipdir_deg + 180.0)
    plunge = max(0.0, 90.0 - float(dip_deg))
    return trend, plunge

def schmidt_equal_area_xy(trend_deg: float, plunge_deg: float) -> Tuple[float, float]:
    r = math.sqrt(2.0) * math.sin(deg2rad((90.0 - plunge_deg)/2.0))
    T = deg2rad(trend_deg)
    x = r * math.sin(T); y = r * math.cos(T)
    return x,y

def mean_plane_from_poles(poles: Sequence[Tuple[float,float]]) -> Optional[Tuple[float,float]]:
    if len(poles) == 0: return None
    vecs = np.array([vector_from_trend_plunge(T,P) for T,P in poles], dtype=float)
    m = vecs.mean(axis=0); n = np.linalg.norm(m)
    if n == 0: return None
    m = m / n
    Tm, Pm = trend_plunge_from_vector(m)
    dip = max(0.0, 90.0 - Pm)
    dipdir = wrap_360(Tm + 180.0)
    return dip, dipdir

def great_circle_segments_for_plane(dip_deg: float, dipdir_deg: float, npts: int = 721, thresh: float = 0.12) -> List[Tuple[np.ndarray,np.ndarray]]:
    """Generate *arc* segments (no chord) for a plane great circle under Schmidt projection."""
    T_p, P_p = pole_from_plane(dip_deg, dipdir_deg)
    pole_vec = vector_from_trend_plunge(T_p, P_p)

    up = np.array([0.0, 0.0, -1.0])
    ref = up if abs(np.dot(up, pole_vec)) <= 0.95 else np.array([1.0,0.0,0.0])
    u = np.cross(pole_vec, ref); un = np.linalg.norm(u)
    if un == 0:
        ref = np.array([1.0,0.0,0.0])
        u = np.cross(pole_vec, ref); un = np.linalg.norm(u)
    u /= un
    v = np.cross(pole_vec, u); v /= np.linalg.norm(v)

    thetas = np.linspace(0, 2*math.pi, npts)
    xs, ys = [], []
    for th in thetas:
        vec = u*np.cos(th) + v*np.sin(th)
        if vec[2] < 0: vec = -vec
        T_line, P_line = trend_plunge_from_vector(vec)
        x,y = schmidt_equal_area_xy(T_line, P_line)
        xs.append(x); ys.append(y)

    segs: List[Tuple[np.ndarray,np.ndarray]] = []
    curx = [xs[0]]; cury = [ys[0]]
    for i in range(1, len(xs)):
        dx = xs[i] - xs[i-1]; dy = ys[i] - ys[i-1]
        if (dx*dx + dy*dy) ** 0.5 > thresh:
            if len(curx) >= 2: segs.append((np.array(curx), np.array(cury)))
            curx, cury = [xs[i]], [ys[i]]
        else:
            curx.append(xs[i]); cury.append(ys[i])
    if len(curx) >= 2: segs.append((np.array(curx), np.array(cury)))

    clean: List[Tuple[np.ndarray,np.ndarray]] = []
    for xseg, yseg in segs:
        r2 = xseg**2 + yseg**2
        mask = r2 <= 1.000001
        if mask.sum() >= 2: clean.append((xseg[mask], yseg[mask]))
    return clean


# ------------------------- KDE on the disk -------------------------

def gaussian_kde_on_disk(points_xy: Sequence[Tuple[float,float]], grid_n: int = 361, bandwidth: float = 0.09):
    xs = np.linspace(-1, 1, grid_n)
    ys = np.linspace(-1, 1, grid_n)
    Xg, Yg = np.meshgrid(xs, ys)
    R2 = Xg*Xg + Yg*Yg
    mask_circle = R2 <= 1.0
    Z = np.zeros_like(Xg, dtype=float)
    pts = np.array(points_xy, dtype=float)
    if pts.size == 0:
        return Xg, Yg, np.ma.array(Z, mask=~mask_circle)
    inv2s2 = 1.0 / (2.0 * bandwidth * bandwidth)
    norm = 1.0 / (2.0 * math.pi * bandwidth * bandwidth)
    for (px, py) in pts:
        dx = Xg - px
        dy = Yg - py
        Z += np.exp(-(dx*dx + dy*dy) * inv2s2)
    Z *= norm / max(len(pts), 1)
    return Xg, Yg, np.ma.array(Z, mask=~mask_circle)


# ------------------------- Column inference & parsing -------------------------

@dataclass
class ColumnHints:
    dip_hints: Tuple[str, ...] = ('dip','dip_','dip(deg)','dip (deg)','Dip','DIP')
    ddir_hints: Tuple[str, ...] = ('dipdir','dip_dir','dip direction','dipdirection','azimuth','az','dir','dd',
                                   'DipDir','DipDirection','Azimuth','Az','Dir','DD')
    group_hints: Tuple[str, ...] = ('group','face','set','cluster','class','domain','Group','Face','Set')

def _looks_like_dip(s: pd.Series) -> bool:
    v = pd.to_numeric(s, errors='coerce').dropna()
    return bool(len(v)) and (v.between(0,90).mean() > 0.8)

def _looks_like_dd(s: pd.Series) -> bool:
    v = pd.to_numeric(s, errors='coerce').dropna()
    return bool(len(v)) and (v.between(0,360).mean() > 0.8)

def _looks_like_group(s: pd.Series) -> bool:
    vals = s.dropna().astype(str).str.strip()
    return 1 <= vals.nunique() <= max(40, int(0.5*len(vals)))

def infer_columns(df: pd.DataFrame, hints: ColumnHints = ColumnHints()) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
    cols = list(df.columns)

    def find_by_hint(hlist: Iterable[str]) -> Optional[str]:
        for c in cols:
            cl = c.lower()
            if any(h in cl for h in hlist): return c
        return None

    dip_col = find_by_hint(hints.dip_hints)
    dd_col  = find_by_hint(hints.ddir_hints)
    group_col = find_by_hint(hints.group_hints)

    combined_col = None
    import re
    _combined_re = re.compile(r'^\\s*(\\d+(?:\\.\\d+)?)\\s*[/,;:\\-\\s]\\s*(\\d+(?:\\.\\d+)?)\\s*$')
    for c in cols:
        if df[c].dtype == object:
            s = df[c].astype(str).str.strip()
            m = s.str.match(_combined_re)
            if m.mean() > 0.6:
                combined_col = c
                break

    if dip_col is None:
        for c in cols:
            if _looks_like_dip(df[c]): dip_col=c; break
    if dd_col is None:
        for c in cols:
            if c!=dip_col and _looks_like_dd(df[c]): dd_col=c; break
    if group_col is None:
        for c in cols:
            if c not in (dip_col, dd_col) and _looks_like_group(df[c]): group_col=c; break

    return dip_col, dd_col, combined_col, group_col

def _derive_dipdir_if_strike(df: pd.DataFrame, dip_col: Optional[str], dd_col: Optional[str]) -> Optional[str]:
    if dd_col is not None: return dd_col
    strike_candidates = [c for c in df.columns if 'strike' in c.lower() or c.lower() in ('str', 'strike(deg)', 'strike (deg)')]
    for sc in strike_candidates:
        try:
            dd = (pd.to_numeric(df[sc], errors='coerce') + 90.0) % 360.0
            df['_dipdir_derived'] = dd
            return '_dipdir_derived'
        except Exception:
            continue
    return None

def parse_planes(df: pd.DataFrame,
                 dip_col: Optional[str],
                 dipdir_col: Optional[str],
                 combined_col: Optional[str]) -> List[Tuple[float,float]]:
    planes: List[Tuple[float,float]] = []
    if combined_col is not None and combined_col in df.columns:
        import re
        _combined_re = re.compile(r'^\\s*(\\d+(?:\\.\\d+)?)\\s*[/,;:\\-\\s]\\s*(\\d+(?:\\.\\d+)?)\\s*$')
        for s in df[combined_col].astype(str).fillna('').tolist():
            m = _combined_re.match(s)
            if not m: continue
            dip = float(m.group(1)); dd = float(m.group(2)) % 360.0
            planes.append((np.clip(dip, 0, 90), dd))
        if planes: return planes

    if dip_col is not None and dipdir_col is not None:
        dips = pd.to_numeric(df[dip_col], errors='coerce')
        ddirs= pd.to_numeric(df[dipdir_col], errors='coerce') % 360.0
        for d, az in zip(dips.tolist(), ddirs.tolist()):
            if pd.isna(d) or pd.isna(az): continue
            planes.append((float(np.clip(d, 0, 90)), float(az)))
        if planes: return planes

    return planes


# ------------------------- Plotting core -------------------------

@dataclass
class Style:
    cmap_name: str = 'tab10'
    ring_rel_levels: Tuple[float, ...] = (0.40, 0.56, 0.72, 0.86, 0.94)
    ring_fill_alphas: Tuple[float, ...] = (0.04, 0.10, 0.18, 0.30, 0.44)
    ring_line_alphas: Tuple[float, ...] = (0.30, 0.40, 0.50, 0.60, 0.70)
    ring_line_widths: Tuple[float, ...] = (0.9, 0.9, 0.9, 1.0, 1.1)
    kde_bandwidth: float = 0.09

    net_circle_lw: float = 2.8
    tick_w_general: float = 1.6
    tick_w_cardinal: float = 2.2
    tick_len_base: float = 0.040
    tick_len_non_factor: float = 0.7
    mean_plane_lw: float = 4.0
    plane_arc_lw: float = 1.3
    plane_arc_alpha: float = 0.12
    pole_marker_size: float = 48.0
    pole_linewidth: float = 1.3
    star_size: float = 24.0
    star_label_offset: float = 0.14
    center_plus_len: float = 0.035
    center_plus_lw: float = 1.8
    cardinal_fontsize: int = 18
    legend_fontsize: int = 9

def compute_groups(df: pd.DataFrame,
                   dip_col: Optional[str], dipdir_col: Optional[str], combined_col: Optional[str],
                   group_col: Optional[str]) -> Dict[str, List[Tuple[float,float]]]:
    if group_col is None or group_col not in df.columns:
        planes = parse_planes(df, dip_col, dipdir_col, combined_col)
        return {'All': planes}

    groups: Dict[str, List[Tuple[float,float]]] = {}
    for gval, df_g in df.groupby(group_col):
        planes = parse_planes(df_g, dip_col, dipdir_col, combined_col)
        gname = str(gval)
        groups[gname] = planes
    return groups

def poles_xy_from_planes(planes: Sequence[Tuple[float,float]]) -> List[Tuple[float,float]]:
    return [schmidt_equal_area_xy(*pole_from_plane(d, az)) for (d, az) in planes]

def intersection_line_from_means(mp1: Optional[Tuple[float,float]], mp2: Optional[Tuple[float,float]]) -> Optional[Tuple[float,float,float]]:
    if mp1 is None or mp2 is None: return None
    T1, P1 = pole_from_plane(*mp1); T2, P2 = pole_from_plane(*mp2)
    n1 = vector_from_trend_plunge(T1, P1); n2 = vector_from_trend_plunge(T2, P2)
    lv = np.cross(n1, n2); nrm = np.linalg.norm(lv)
    if nrm == 0: return None
    lv /= nrm
    Tlin, Plin = trend_plunge_from_vector(lv)
    x,y = schmidt_equal_area_xy(Tlin, Plin)
    return Tlin, Plin, x, y

def _parse_intersection_spec(spec: str, group_names: Sequence[str], nonempty: Sequence[str]) -> List[Tuple[str,str]]:
    gset = set(group_names)
    nn = [g for g in nonempty if g in gset]
    if spec is None or spec.lower() == 'auto':
        return [(nn[0], nn[1])] if len(nn) == 2 else []
    if spec.lower() == 'none':
        return []
    if spec.lower() == 'all':
        pairs = []
        for i in range(len(nn)):
            for j in range(i+1, len(nn)):
                pairs.append((nn[i], nn[j]))
        return pairs
    import re
    out = []
    for token in re.split(r'[,\s]+', spec.strip()):
        if not token: continue
        m = re.split(r'[|/xX]', token)
        if len(m) != 2: continue
        a, b = m[0].strip(), m[1].strip()
        if a in gset and b in gset and a != b:
            out.append((a,b))
    return out

def plot_stereonet(groups: Dict[str, List[Tuple[float,float]]],
                   out_prefix: str = 'stereonet_output',
                   style: Style = Style(),
                   figure_size: Tuple[float,float] = (10.5,10.5),
                   dpi: int = 170,
                   intersections: str = 'auto',
                   save_png: bool = True, save_svg: bool = True, save_pdf: bool = True):
    cmap = plt.get_cmap(style.cmap_name)
    names = list(groups.keys())
    color_map = {name: cmap(i % cmap.N) for i, name in enumerate(names)}

    polesXY: Dict[str, List[Tuple[float,float]]] = {g: poles_xy_from_planes(groups[g]) for g in names}
    means: Dict[str, Optional[Tuple[float,float]]] = {g: mean_plane_from_poles([pole_from_plane(d,az) for (d,az) in groups[g]]) for g in names}

    fig = plt.figure(figsize=figure_size, dpi=dpi)
    ax = plt.gca()
    ax.set_aspect("equal", "box")
    ax.set_xlim(-1.12, 1.12); ax.set_ylim(-1.12, 1.12)
    ax.axis("off")

    ax.add_artist(plt.Circle((0,0), 1.0, fill=False, linewidth=style.net_circle_lw, color="black"))
    card = dict(fontsize=style.cardinal_fontsize, fontweight="bold", color="black")
    ax.text(0, 1.085, "N", ha="center", va="bottom", **card)
    ax.text(1.085, 0, "E", ha="left", va="center", **card)
    ax.text(0, -1.11, "S", ha="center", va="top", **card)
    ax.text(-1.11, 0, "W", ha="right", va="center", **card)

    L = style.center_plus_len
    ax.plot([-L, L], [0,0], color="black", linewidth=style.center_plus_lw, alpha=0.8)
    ax.plot([0,0], [-L, L], color="black", linewidth=style.center_plus_lw, alpha=0.8)

    nesw = {0,90,180,270}
    for A in range(0, 360, 10):
        T = deg2rad(A); x0 = math.sin(T); y0 = math.cos(T)
        base = style.tick_len_base
        TL = base*1.5 if A in nesw else base*style.tick_len_non_factor
        w = style.tick_w_cardinal if A in nesw else style.tick_w_general
        x1 = math.sin(T) * (1.0 + TL); y1 = math.cos(T) * (1.0 + TL)
        ax.plot([x0, x1], [y0, y1], color="black", linewidth=w)

    for g in names:
        XY = np.array(polesXY[g], dtype=float)
        if XY.size == 0: continue
        Xg, Yg, Z = gaussian_kde_on_disk(XY, grid_n=361, bandwidth=style.kde_bandwidth)
        zmax = float(Z.max()) if Z.max() > 0 else 0.0
        if zmax <= 0: continue
        abs_levels = [lv * zmax for lv in style.ring_rel_levels]; prev = abs_levels[0] * 0.85
        for lv, fa, la, lw in zip(abs_levels, style.ring_fill_alphas, style.ring_line_alphas, style.ring_line_widths):
            ax.contourf(Xg, Yg, Z, levels=[prev, lv], colors=[color_map[g]], alpha=fa, zorder=0)
            ax.contour( Xg, Yg, Z, levels=[lv], colors=[color_map[g]], linewidths=lw, alpha=la, zorder=1)
            prev = lv
        ax.contourf(Xg, Yg, Z, levels=[abs_levels[-1], zmax], colors=[color_map[g]], alpha=max(style.ring_fill_alphas[-1]*1.4, style.ring_fill_alphas[-1]), zorder=0)
        ax.contour( Xg, Yg, Z, levels=[abs_levels[-1]], colors=[color_map[g]], linewidths=max(style.ring_line_widths[-1], 1.2), alpha=max(style.ring_line_alphas[-1], 0.8), zorder=1)

    for g in names:
        for dip, dipdir in groups[g]:
            for xs, ys in great_circle_segments_for_plane(dip, dipdir, npts=361, thresh=0.12):
                ax.plot(xs, ys, linewidth=style.plane_arc_lw, alpha=style.plane_arc_alpha, color=color_map[g], zorder=2)

    for g in names:
        XY = polesXY[g]
        X, Y = (zip(*XY) if len(XY) else ([], []))
        ax.scatter(X, Y, marker='x', s=style.pole_marker_size, linewidths=style.pole_linewidth, alpha=1.0, color=color_map[g],
                   label=f"Poles: {g} (n={len(XY)})", zorder=3)

    for g in names:
        mp = means[g]
        if mp is None: continue
        dip, dipdir = mp
        segs = great_circle_segments_for_plane(dip, dipdir, npts=721, thresh=0.12)
        for k,(xs,ys) in enumerate(segs):
            lbl = f"Mean plane {g} (Dip={dip:.0f}°, DipDir={dipdir:.0f}°)" if k==0 else None
            ax.plot(xs, ys, linewidth=style.mean_plane_lw, alpha=0.98, color=color_map[g], label=lbl, zorder=4)

    nonempty = [g for g in names if len(groups[g]) > 0]
    pair_specs = _parse_intersection_spec(intersections, names, nonempty)
    for idx,(a,b) in enumerate(pair_specs):
        ip = intersection_line_from_means(means[a], means[b])
        if ip is None: continue
        Tlin, Plin, xx, yy = ip
        ax.plot([xx], [yy], marker="*", markersize=style.star_size, color="black",
                markeredgecolor="black", markeredgewidth=1.1, zorder=5)
        ax.text(xx, yy - style.star_label_offset, f"{a}×{b}: {Tlin:.0f}/{Plin:.0f}", fontsize=style.legend_fontsize,
                ha="center", va="top", color="black")

    handles, labels = ax.get_legend_handles_labels()
    handles.append(matplotlib.lines.Line2D([], [], color='none', label="Measurements: Dip / Dip Direction (Azimuth), degrees"))
    labels.append("Measurements: Dip / Dip Direction (Azimuth), degrees")
    ax.legend(handles, labels, loc="upper left", bbox_to_anchor=(1.02, 1.0), fontsize=style.legend_fontsize, frameon=True)

    if save_png: plt.savefig(out_prefix + ".png", dpi=340, bbox_inches="tight")
    if save_svg: plt.savefig(out_prefix + ".svg", bbox_inches="tight")
    if save_pdf: plt.savefig(out_prefix + ".pdf", bbox_inches="tight")
    return fig, ax


# ------------------------- High-level API / CLI -------------------------

def plot_stereonet_from_csv(csv_path: str,
                            dip_col: Optional[str] = None,
                            dipdir_col: Optional[str] = None,
                            group_col: Optional[str] = None,
                            out_prefix: str = "stereonet_output",
                            style: Style = Style(),
                            figure_size: Tuple[float,float] = (10.5,10.5),
                            dpi: int = 170,
                            intersections: str = 'auto'):
    df = pd.read_csv(csv_path)

    dip_c, dd_c, comb_c, grp_c = infer_columns(df)
    dip_col = dip_col or dip_c
    dipdir_col = dipdir_col or _derive_dipdir_if_strike(df, dip_c or dip_col, dd_c or dipdir_col)
    group_col = group_col or grp_c

    groups = compute_groups(df, dip_col, dipdir_col, comb_c, group_col)
    return plot_stereonet(groups, out_prefix=out_prefix, style=style,
                          figure_size=figure_size, dpi=dpi, intersections=intersections)

def _build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="StereonetForge — stereonet plotter for planes (Dip / Dip Direction) with any number of groups.")
    p.add_argument("csv", help="Input CSV file.")
    p.add_argument("--dip-col", default=None, help="Column for Dip (deg). If omitted, auto-detect.")
    p.add_argument("--dipdir-col", default=None, help="Column for Dip Direction / Azimuth (deg). If omitted, auto-detect or derive from Strike.")
    p.add_argument("--group-col", default=None, help="Optional grouping column (Face/Set/etc). If omitted, all data are one group.")
    p.add_argument("--intersections", default="auto", help="none | auto | all | explicit pairs like 'A|B,B|C'. Default 'auto' draws one star only if there are exactly two groups.")
    p.add_argument("--cmap", default="tab10", help="Matplotlib colormap for groups (default: tab10).")
    p.add_argument("--kde-bandwidth", type=float, default=0.09, help="KDE bandwidth on unit disk.")
    p.add_argument("--out-prefix", default="stereonet_output", help="Output prefix (PNG/SVG/PDF).")
    p.add_argument("--figsize", default="10.5,10.5", help="Figure size inches, e.g. 10.5,10.5")
    p.add_argument("--dpi", type=int, default=170, help="Figure DPI.")
    return p

def main_cli():
    ap = _build_argparser()
    a = ap.parse_args()

    style = Style(cmap_name=a.cmap, kde_bandwidth=a.kde_bandwidth)
    fs = tuple(float(s) for s in a.figsize.split(","))

    plot_stereonet_from_csv(a.csv,
                            dip_col=a.dip_col, dipdir_col=a.dipdir_col, group_col=a.group_col,
                            out_prefix=a.out_prefix, style=style, figure_size=fs, dpi=a.dpi,
                            intersections=a.intersections)

if __name__ == "__main__":
    main_cli()
