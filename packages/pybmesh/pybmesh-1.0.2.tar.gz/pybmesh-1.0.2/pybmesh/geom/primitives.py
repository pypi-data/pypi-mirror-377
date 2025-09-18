from __future__ import annotations
import math
import vtk
import numpy as np
from vtk.util import numpy_support  # noqa: F401  (import kept to preserve original environment)
from typing import Iterable, Callable, Dict, List, Tuple
from dataclasses import dataclass

from pybmesh.geom.mesh import Elem
from pybmesh.geom.d0 import Point
from pybmesh.geom.d1 import Line, PolyLine, Arc
from pybmesh.geom.d2 import Surface, Raccord2D
from pybmesh.utils.maths import polyline_sphere_crossings
from pybmesh.utils.meshtools import translate, rotate, syme, fuse
from pybmesh.io.viewer import plot


# ---------- Data structures ----------
@dataclass
class SegmentInfo:
    x0: float
    x1: float
    nr : int
    nx0 : int
    nx1 : int
    grading : float
    details : dict
    band : bool = False
    
    def __str__(self) -> str:
        def fmt(v):
            return f"{v:.6g}" if isinstance(v, (int, float)) else str(v)
        details_str = ", ".join(f"{k}={fmt(v)}" for k, v in self.details.items())
        tag = "Band" if self.band else "Segment"
        return (f"{tag} [{self.x0:.6g}, {self.x1:.6g}] "
                f"nr={self.nr}, nx0={self.nx0}, nx1={self.nx1}, grading={self.grading:.6g}"
                + (f", details: {{{details_str}}}" if details_str else ""))


ComputeFn = Callable[[float, float, int], Tuple[int, float, Dict[str, float]]]

class BandMesh:
    """
    Optimize coarsening bands in [x_init, x_end].
    Objective = w_size * sum_i (dr_in - dr_out)^2  +  w_nr * sum_j ((n_r_j - N*_j)/max(1, N*_j))^2
    Also enforces: band thickness = first post-band element size (dr0).
    """

    def __init__(self,
                 compute_fn: ComputeFn,
                 x_init: float,
                 x_end: float,
                 nx: int,
                 refLevel: List[int],
                 ):
        assert 0.0 < x_init < x_end, "Require 0 < x_init < x_end."
        self.compute_fn = compute_fn
        self.x_init = float(x_init)
        self.x_end = float(x_end)
        self.nx = int(nx)
        self.refLevel = [max(1, int(r)) for r in refLevel]
        
        xs, bounds = self._compute_positions()
        self.segment = self._make_segment(xs)

    
    def _compute_positions(self):
        """
        Place the *starts* of bands so that the m+1 non-band segments
        (pre-band0, between bands, and tail) have lengths in geometric
        progression: L_i = C * prod_{k=0..i-1} refLevel[k], with L_0 = C.
        Returns:
            xs     : list of band starts (len = m)
            bounds : cumulative non-band boundaries (len = m+1+1), starting at x_init, ending at x_end
        """
        m = len(self.refLevel)
        if m == 0:
            return [], [self.x_init, self.x_end]
        
        # multipliers for the (m+1) non-band segments: [1, r1, r1*r2, ..., r1*...*rm]
        multipliers = [1.0]
        refLevel = self.refLevel[1:]
        for r in refLevel:
            multipliers.append(multipliers[-1] * float(r))
    
        total_weight = sum(multipliers)                  # S P_i
        L = self.x_end - self.x_init                    # domain length
        base = L / total_weight                         # C
    
        # actual non-band segment lengths (ignoring band thickness)
        seg_lengths = [base * p for p in multipliers]   # len = m+1
    
        # band starts (xs) and convenience bounds (non-band cumulative)
        xs = [self.x_init]
        bounds = [self.x_init]
        cur = self.x_init
        for i in range(m):
            cur += seg_lengths[i]   # after non-band segment i
            xs.append(cur)          # start of band i
            bounds.append(cur)
        bounds.append(self.x_end)   # end after the tail segment
        return xs, bounds

    def _make_segment(self, xs):
        segs: List[SegmentInfo] = []
        if xs and xs[0] > self.x_init:
            x0 = self.x_init
            x1 = xs[0]
            nr, grading, details = self.compute_fn(x0, x1, self.nx)
            seg = SegmentInfo(x0=x0, x1=x1, nr=nr, nx0=self.nx, nx1=self.nx, grading=grading, details=details, band=False)
            segs.append(seg)
       
        nx = self.nx
        for i,lvl in enumerate(self.refLevel):
            nx = int(nx/lvl)
            x0 = xs[i]
            x2 = xs[i+1] if i < len(self.refLevel)-1 else self.x_end
            nr, grading, details = self.compute_fn(x0, x2, nx)  
            x1 = x0 + details['dr0'] if x0 + details['dr0'] < x2 else x2
            nr, grading, details = self.compute_fn(x0, x1, nx)
            seg = SegmentInfo(x0=x0, x1=x1, nr=nr, nx0=nx*lvl, nx1=nx, grading=grading, details=details, band=True)
            segs.append(seg)
            if x1 < x2:
                nr, grading, details = self.compute_fn(x1, x2, nx)
                seg = SegmentInfo(x0=x1, x1=x2, nr=nr, nx0=nx, nx1=nx, grading=grading, details=details, band=False)
                segs.append(seg)
        return segs

class Disk(Surface):
    """
    Factory-like `Surface` subclass to build quarter / half / full disk meshes in one call.

    Parameters
    ----------
    rint : float
        Inner radius of the disk.
    rext : float
        Outer radius of the disk (must be > rint).
    ftype : {"quarter","half","full"}, optional
        Mesh fraction to produce. Defaults to "full".
    intype : {"square", "diamond", "circle"}, optional
        Shape of the inner patch: cartesian square or circular arc. Defaults to "square".
    optArea : {"hollow","central","all"}, optional
        Which areas to output when refinement bands are used. Defaults to "all".
    refLevels : Iterable[int] | None, optional
        Angular refinement factors per band (e.g. [2, 3]). If None, a simple 2-zone mesh is used.
    dx_min : float | None, optional
        Target minimal edge size along the inner perimeter; if set it controls `nx`.
    nx : int, optional
        Base angular subdivision count per quadrant (adjusted to be compatible with `refLevels`).
    nr : int | None, optional
        Radial subdivision (if None, it is auto-chosen to match inner/outer target spacings).
    center : tuple[float, float, float], optional
        Translation applied to the final mesh.
    theta : float, optional
        Additional rotation about +Z (degrees) before orienting the mesh to `normal`.
    normal : tuple[float, float, float], optional
        Target surface normal (mesh is rotated from +Z to this vector).
    pid : int, optional
        Property/material id carried by the resulting surface cells.

    Returns
    -------
    Surface
        The final `Surface` (already mirrored/fused/rotated/translated per arguments).

    Notes
    -----
    This class overrides `__new__` to act as a *factory*.
    It allocates a temporary instance to reuse private helpers, then returns a finished `Surface`.
    Behavior and topology are preserved exactly from your original code.
    """

    # --- One-call constructor that returns the final Surface `out`
    def __new__(
        cls,
        *,
        rint: float,
        rext: float,
        ftype: str = "full",          # "quarter" / "half" / "full"
        intype: str = "square",       # "square" or "diamond" or "circle"
        optArea: str = "all",         # "hollow", "central", "all"
        refLevels: Iterable[int] | None = None,  # e.g. [2, 3] or []
        dx_min: float | None = None,
        nx: int = 1,
        nr: int | None = None,
        center: tuple[float, float, float] = (0, 0, 0),
        theta: float = 0.0,
        normal: tuple[float, float, float] = (0, 0, 1),
        pid: int = 1,
    ):
        # Create a temporary, empty Surface; we only use it to access helper methods.
        self = super().__new__(cls)
        __pid = pid  # remember requested pid for the fused result

        # --- Angular subdivision selection -------------------------------------
        if dx_min is not None:
            # Ensure at least two divisions; approximate along inner square/arc
            nx = max(int(rint / dx_min), 2)

        # Make nx compatible with the angular refinement LCM (preserves original logic)
        if refLevels:
            lcm_val = list(refLevels)[0]
            for val in list(refLevels)[1:]:
                lcm_val = abs(lcm_val * val)
            if nx % lcm_val != 0:
                nx = math.ceil(nx / lcm_val) * lcm_val


        # --- Radial subdivision / grading ---------------------------------------
        nr, grading, details = self.__compute_nr_and_grading(rint, rext, nx, nr)

        # Keep radial count compatible with number of refinement levels
        if refLevels:
            if nr % len(list(refLevels)) != 0:
                nr = math.ceil(nx / len(list(refLevels))) * len(list(refLevels))

        # --- Geometry seeds ------------------------------------------------------
        P0 = Point(0, 0, 0)  # center
        PX: list[Point] = []
        PY: list[Point] = []
        PXY: list[Point | tuple[float, float, float]] = []

        # Inner (central) zone
        PX.append(Point(rint, 0, 0))
        PY.append(Point(0, rint, 0))
        if intype == "square":
            PXY.append(Point(rint, rint, 0))
        else:
            # point on the 45° arc
            PXY.append((rint * math.cos(math.radians(45)),
                        rint * math.sin(math.radians(45)), 0))

        # --- Build surfaces ------------------------------------------------------
        if refLevels:
            # With refinement bands: inner square + optional raccord + geometric bands
            def ring_points(r: float) -> tuple[Point, Point, Point]:
                """Convenience: three points at 0°, 45°, 90° for a given radius."""
                return (
                    Point(r, 0, 0),
                    Point(r * math.cos(math.radians(45)), r * math.sin(math.radians(45)), 0),
                    Point(0, r, 0),
                )

            x0 = rint
            factor1 =  1.10*math.sqrt(2)  if intype == "square" else 1.2
            x1 = factor1*rint

            # now compute bands
            bands = BandMesh(
                compute_fn=self.__compute_nr_and_grading,
                x_init=x1,
                x_end=rext,
                nx=nx,
                refLevel=refLevels,
            )
            
            segments = bands.segment
            
            if  intype != "circle":
                S1 = Surface(P0, PX[0], PXY[0], PY[0], n=nx, quad=True, pid=1)
                L_inner = PolyLine(PX[0], PXY[0], PY[0], n=nx)
            else : 
                L1 = Line(P0, PX[0], nx)
                L2 = Line(PY[0], P0,nx)
                L_inner = Arc.from_3_points(PX[0], PXY[0], PY[0], n=2 * nx + 1)  
                LC = fuse(L1,L2,verbose=False)
                LC = fuse(LC,L_inner,verbose=False)
                S1 = Surface(LC, n=1, quad=True, pid=1)

            pid = 5
            # Select which parts to keep according to `optArea`
            surfaces = [] if optArea == "hollow" else [S1]

            if optArea != "central":
                
                #case band 0
                OX, OXY, OY = ring_points(x1)
                L_outer = Arc.from_3_points(OX, OXY, OY, n=int(2*nx+1), pid=pid)
                n_ri, grad_i, detail_i = self.__compute_nr_and_grading(rint,x1,nx)
                Surf = Surface(L_inner, L_outer, n=n_ri, grading=grad_i,
                                           progression="geometric", pid=pid)
                surfaces.append(Surf)
                L_inner = L_outer
                
                for s in segments:
                    OX, OXY, OY = ring_points(s.x1)
                    L_outer = Arc.from_3_points(OX, OXY, OY, n=(2*s.nx1+1), pid=pid)
                    if s.band:
                        Surf = Raccord2D(L_inner, L_outer, quad=True,pid = pid)
                    else:
                        pass
                        Surf = Surface(L_inner, L_outer, n=s.nr, grading=s.grading,
                                                  progression="geometric", pid=pid)
                    surfaces.append(Surf)
                    L_inner = L_outer
                    pid = pid + 1

        else:
            # No refinement levels: inner square + one outer circular band
            PX.append(Point(rext, 0, 0))
            PXY.append(Point(rext * math.cos(math.radians(45)),
                             rext * math.sin(math.radians(45)), 0))
            PY.append(Point(0, rext, 0))

            if  intype != "circle":
                S1 = Surface(P0, PX[0], PXY[0], PY[0], n=nx, quad=True, pid=1)
                L0 = PolyLine(PX[0], PXY[0], PY[0], n=nx)            # inner edge
            else : 
                L1 = Line(P0, PX[0], nx)
                L2 = Line(PY[0], P0,nx)
                L0 = Arc.from_3_points(PX[0], PXY[0], PY[0], n=2 * nx + 1)  
                LC = fuse(L1,L2,verbose=False)
                LC = fuse(LC,L0,verbose=False)
                S1 = Surface(LC, n=1, quad=True, pid=1)

            L1 = Arc.from_3_points(PX[-1], PXY[-1], PY[-1], n=2 * nx + 1, pid=2)  # outer arc
            S2 = Surface(L0, L1, n=nr, grading=grading, progression="geometric", pid=5)
            if optArea == "hollow":
                surfaces = [S2]
            elif  optArea == "central":
                surfaces = [S1]
            else:     
                surfaces = [S1, S2]

        # --- Merge/fuse surfaces into a single unstructured grid -----------------
        append = vtk.vtkAppendFilter()
        for s in surfaces:
            # Support both Surface APIs (direct grid or `get_vtk_unstructured_grid`)
            if hasattr(s, "get_vtk_unstructured_grid"):
                append.AddInputData(s.get_vtk_unstructured_grid())
            else:
                append.AddInputData(s._ugrid)
        append.Update()
        merged = append.GetOutput()

        cleaner = vtk.vtkStaticCleanUnstructuredGrid()
        cleaner.SetInputData(merged)
        cleaner.SetTolerance(1e-6)
        cleaner.RemoveUnusedPointsOn()
        cleaner.Update()
        cleaned = cleaner.GetOutput()

        fused = Surface(pid=__pid)
        fused._ugrid = cleaned
        fused.pid = __pid

        # --- Mirror/fuse according to ftype, then orient, rotate, translate ------
        out = self.__make_by_ftype(fused, ftype)
        out.set_orientation(normal=(0, 0, 1))
        out = self.__rotate_about_z(out, theta)
        out = self.__align_z_to_normal(out, normal, center=(0, 0, 0))
        out = translate(out, center)

        return out

    # ---------------------- PRIVATE HELPERS (verbatim logic) ----------------------

    def __targets(
        self,
        rint: float,
        rext: float,
        nx: int,
        inner_mode: str = "cartesian",
        pad_in: float = 1.0,
        pad_out: float = 1.0,
    ) -> tuple[float, float]:
        """
        Target edge lengths at inner/outer radii for one quadrant.

        Returns
        -------
        (s_in, s_out) : tuple[float, float]
            Desired chord/segment lengths to compare against radial steps.
        """
        if inner_mode == "arc":
            s_in = (math.pi * rint) / (4.0 * nx)   # chord length along inner arc
        else:
            s_in = rint / nx                       # cartesian inner edge
        s_out = (math.pi * rext) / (4.0 * nx)      # chord length along outer arc
        return pad_in * s_in, pad_out * s_out

    def __compute_nr_and_grading(
        self,
        rint: float,
        rext: float,
        nx: int,
        nr: int | None = None,
        inner_mode: str = "cartesian",
        pad_in: float = 1.0,
        pad_out: float = 1.0,
        search_span: int = 6,
    ) -> tuple[int, float, dict]:
        """
        Choose radial divisions `nr` and geometric grading to match inner/outer target sizes.

        If `nr` is provided, use it directly (returning associated grading and details).
        Otherwise, search around an isometric guess to minimize mismatch at inner/outer rims.
        """
        assert rext > rint > 0 and nx >= 1
        s_in, s_out = self.__targets(rint, rext, nx, inner_mode, pad_in, pad_out)
        dtheta = math.pi / (4.0 * nx)

        def _eval(N: int) -> dict:
            q = (rext / rint) ** (1.0 / N)           # per-step radial ratio
            dr0 = rint * (q - 1.0)                   # first radial step
            drL = rext * (q - 1.0)                   # last radial step
            grading = q ** (N - 1)                   # total progression across band
            iso = (q - 1.0) / dtheta                 # compare against angular spacing
            err = (dr0 / s_in - 1.0) ** 2 + (drL / s_out - 1.0) ** 2
            ok_in = dr0 + 1e-12 >= s_in
            ok_out = drL + 1e-12 >= s_out
            return dict(
                nr=N, q=q, grading=grading, dr0=dr0, dr_last=drL,
                s_in=s_in, s_out=s_out, iso=iso, ok_in=ok_in, ok_out=ok_out, err=err
            )

        # If user forced `nr`, honor it and compute derived quantities.
        if nr is not None:
            sol = _eval(nr)
            return sol["nr"], sol["grading"], sol

        # Seed around "isometric" guess (q ~ 1 + dtheta)
        q_iso = 1.0 + dtheta
        n_star = max(1, math.log(rext / rint) / math.log(q_iso))
        seeds = [max(1, int(math.floor(n_star))), max(1, int(math.ceil(n_star)))]

        best = None
        tried: set[int] = set()
        for base in seeds:
            for k in range(-search_span, search_span + 1):
                N = max(1, base + k)
                if N in tried:
                    continue
                tried.add(N)
                sol = _eval(N)
                penalty = (0 if sol["ok_in"] else 1_000) + (0 if sol["ok_out"] else 1_000)
                score = penalty + sol["err"] + 0.1 * abs(sol["iso"] - 1.0)
                sol["score"] = score
                if best is None or score < best["score"]:
                    best = sol

        return best["nr"], best["grading"], best  # type: ignore[index]

    def __geometric_spacing_points(self, p1, p2, n: int, grading: float = 1.0) -> np.ndarray:
        """
        Interpolate `n` segments between points `p1` and `p2` using geometric spacing.

        Parameters
        ----------
        p1, p2 : array-like
            End points (3D).
        n : int
            Number of segments (returns n+1 points).
        grading : float
            Ratio of last step to first step (1.0 -> uniform).

        Returns
        -------
        numpy.ndarray
            Array of shape (n+1, 3) with interpolated points.
        """
        if n < 1:
            raise ValueError("n must be >= 1")
        p1 = np.asarray(p1, float)
        p2 = np.asarray(p2, float)
        if grading <= 0:
            raise ValueError("grading must be > 0")

        if abs(grading - 1.0) < 1e-12:
            t = np.linspace(0.0, 1.0, n + 1)
        else:
            q = grading ** (1.0 / (n - 1))
            i = np.arange(n + 1, dtype=float)
            t = (q ** i - 1.0) / (q ** n - 1.0)
        return p1 * (1.0 - t)[:, None] + p2 * t[:, None]

    def __dtheta(self, nx: int, ftype: str = "quarter") -> float:
        """Angular step per segment in a quadrant; kept for compatibility with original logic."""
        return math.pi / (4.0 * nx)

    def __geom_sum(self, first: float, q: float, n: int) -> float:
        """Geometric series partial sum: first + first*q + ... (n terms)."""
        if n <= 0:
            return 0.0
        if abs(q - 1.0) < 1e-12:
            return n * first
        return first * (q**n - 1.0) / (q - 1.0)

    def __plan_radial_bands(
        self, rint: float, rext: float, nx: int, refLevels: Iterable[int],
        inner_mode: str = "cartesian", pad_in: float = 1.0, pad_out: float = 1.0, ftype: str = "quarter"
    ):
        """
        Plan radial bands and per-band angular subdivisions from `refLevels`.

        Returns
        -------
        rings : list[float]
            Radii delimiting bands (including rint and rext).
        bands : list[dict]
            Per-band metadata: number of radial steps, grading, radii extents, and angular `no`.
        """
        assert rext > rint > 0 and nx >= 1

        base_no = 2 * nx                         # base angular divisions along the arc
        dth = self.__dtheta(nx, ftype)
        s_in, s_out = self.__targets(rint, rext, nx, inner_mode, pad_in, pad_out)

        rings = [float(rint)]
        bands = []

        dr_start = s_in
        r = float(rint)

        def choose_n_for_level(L: int) -> tuple[int, float]:
            """Pick `N` such that per-step ratio ~ (1 + dtheta), for a given level L."""
            n_star = 1.0 + math.log(L) / math.log(1.0 + dth)
            candidates = [max(2, int(math.floor(n_star))), max(2, int(math.ceil(n_star)))]
            best = None
            for N in sorted(set(candidates)):
                q = L ** (1.0 / (N - 1))
                err = abs((q - 1.0) - dth)
                item = (err, N, q)
                if best is None or item < best:
                    best = item
            _, Nbest, qbest = best  # type: ignore[misc]
            return Nbest, qbest

        cum_ref = 1
        for i, L in enumerate(refLevels):
            N, q = choose_n_for_level(L)
            dR = self.__geom_sum(dr_start, q, N)
            r_next = r + dR

            # Clip to outer radius by reducing N if necessary
            while r_next > rext * (1 + 1e-12) and N > 2:
                N -= 1
                q = L ** (1.0 / (N - 1))
                dR = self.__geom_sum(dr_start, q, N)
                r_next = r + dR

            # Final binary-search if still exceeding rext
            if r_next > rext * (1 + 1e-12):
                N = max(2, N)
                lo, hi = 1.0 + 1e-12, max(1.01, (rext / r) ** (1.0 / N))
                for _ in range(100):
                    mid = 0.5 * (lo + hi)
                    S = self.__geom_sum(dr_start, mid, N)
                    if abs(S - (rext - r)) <= 1e-12 * max(1.0, rext - r):
                        q = mid
                        break
                    if S < (rext - r):
                        lo = mid
                    else:
                        hi = mid
                else:
                    q = 0.5 * (lo + hi)
                dR = self.__geom_sum(dr_start, q, N)
                r_next = r + dR

            dr_last = dr_start * (q ** (N - 1))
            grading = q ** (N - 1)

            no_i = base_no / int(cum_ref)  # angular divisions for this band

            bands.append({
                'n': N, 'grading': grading, 'q': q,
                'dr0': dr_start, 'drL': dr_last,
                'x0': r, 'x1': r_next,
                'no': no_i, 'L': L, 'cumL': cum_ref,
            })

            rings.append(r_next)
            dr_start = dr_last
            r = r_next
            cum_ref *= L

            if r >= rext * (1 - 1e-12):
                break

        # Tail band up to rext (if any)
        if r < rext - 1e-12:
            dR = rext - r
            q_guess = 1.0 + dth
            N_guess = max(1, int(math.ceil(
                math.log(1.0 + (q_guess - 1.0) * dR / dr_start) / math.log(q_guess)
            )))
            N = max(1, N_guess)
            if N == 1:
                q_eff = 1.0
                grading = 1.0
                dr_last = dr_start
            else:
                q_eff = (rext / r) ** (1.0 / N)
                grading = q_eff ** (N - 1)
                dr_last = dr_start * grading

            _, s_out = self.__targets(rint, rext, nx, inner_mode, pad_in, pad_out)
            if dr_last + 1e-12 < s_out:
                # enforce minimal outer step
                N += 1
                if N == 1:
                    q_eff = 1.0; grading = 1.0; dr_last = dr_start
                else:
                    q_eff = (rext / r) ** (1.0 / N)
                    grading = q_eff ** (N - 1)
                    dr_last = dr_start * grading

            bands.append({
                'n': N, 'grading': grading, 'q': q_eff,
                'dr0': dr_start, 'drL': dr_last,
                'x0': r, 'x1': rext,
                'no': base_no / int(cum_ref),
                'L': L, 'cumL': cum_ref
            })
            rings.append(rext)

        return rings, bands

    def __make_by_ftype(self, q1: Surface, ftype: str) -> Surface:
        """
        Mirror/fuse a quadrant according to `ftype`.
        - "quarter": return as-is
        - "half":    mirror in YZ and fuse
        - "full":    mirror to half, fuse, mirror across ZX, fuse
        """
        ftype = (ftype or "quarter").lower()
        if ftype == "quarter":
            return q1
        if ftype == "half":
            q2 = syme(q1, plane="yz", pid=q1.pid)
            return fuse(q1, q2, pid=q1.pid, merge=True, verbose=False)
        if ftype == "full":
            q2 = syme(q1, plane="yz", pid=q1.pid)
            demi = fuse(q1, q2, pid=q1.pid, merge=True, verbose=False)
            q3 = syme(demi, plane="zx", pid=demi.pid)
            return fuse(demi, q3, pid=demi.pid, merge=True, verbose=False)
        raise ValueError("ftype must be one of: 'quarter', 'half', 'full'")

    def __rotate_about_z(self, mesh: Surface, theta_deg: float) -> Surface:
        """Rotate `mesh` about +Z by `theta_deg` degrees (no-op if |theta| ~ 0)."""
        if abs(theta_deg) < 1e-12:
            return mesh
        return rotate(mesh, axis="z", angle=float(theta_deg))

    def __align_z_to_normal(
        self, mesh: Surface, normal_vec: Iterable[float], center: tuple[float, float, float] = (0, 0, 0)
    ) -> Surface:
        """
        Rotate `mesh` so that +Z aligns with `normal_vec`, around a computed axis through `center`.
        """
        ez = np.array([0.0, 0.0, 1.0], dtype=float)
        n = np.array(normal_vec, dtype=float)
        n_norm = np.linalg.norm(n)
        if n_norm < 1e-15:
            raise ValueError("normal vector must be non-zero")
        n = n / n_norm

        c = float(np.clip(np.dot(ez, n), -1.0, 1.0))
        ang_deg = math.degrees(math.acos(c))
        if ang_deg < 1e-12:
            return mesh

        axis = np.cross(ez, n)
        ax_norm = np.linalg.norm(axis)
        if ax_norm < 1e-12:
            axis = (1.0, 0.0, 0.0)  # arbitrary axis if vectors are opposite colinear
        else:
            axis = tuple(axis / ax_norm)

        return rotate(mesh, center=center, axis=axis, angle=ang_deg)

class RegularPolygon(Surface):
    """
    Factory-style `Surface` to generate a mesh of a regular N-gon with
    a square-ish inner patch and optional graded refinement bands up to the outer boundary.

    Parameters
    ----------
    n_sides : int
        Number of sides of the regular polygon (n_sides > 2).
    rint : float
        Inner *apothem* (distance from center to an inner polygon edge). Controls the inner patch size.
    rext : float
        Outer *apothem* (distance from center to the outer polygon edges). Must be > rint.
    ftype : {"quarter","half","full"}, optional
        Symmetry fraction to return. Not all fractions are valid for a given `n_sides`:
        - quarter: only valid if `n_sides % 4 == 0`
        - demi:    valid if `n_sides % 2 == 0`
        - full:    always valid
        If an invalid fraction is requested, a `ValueError` is raised.
    intype : {"square","none"}, optional
        Inner core patch: a cartesian square (default) or a tiny similar N-gon if "none".
    optArea : {"exterior","central","all"}, optional
        Which areas to keep when refinement bands are used. Defaults to "all".
    refLevels : Iterable[int] | None, optional
        Angular refinement multipliers per radial band (e.g. [2,3]). If None, a simple 2-zone mesh is built.
    dx_min : float | None, optional
        Target minimal segment along the inner perimeter; if set it influences the base angular subdivision `nx`.
    nx : int, optional
        Base per-quarter angular subdivision used to discretize polylines (adjusted for `refLevels`).
    nr : int | None, optional
        Radial subdivision. If None, it is auto-chosen to balance inner/outer target sizes.
    center : tuple[float, float, float], optional
        Final translation for the mesh.
    theta : float, optional
        Extra rotation about +Z (degrees) applied *before* orienting to `normal`.
    normal : tuple[float, float, float], optional
        Target surface normal (mesh is rotated from +Z to this vector).
    pid : int, optional
        Property/material id carried by the resulting cells.

    Notes
    -----
    - `rint`/`rext` are **apothem** distances (center to edge). The polygon circumradii are R = r / cos(pi/N).
    - The construction mirrors your `Disk` class:
      inner square -> optional raccord -> geometric bands -> merge/clean -> symmetry fraction -> orient/translate.
    - Instead of circular arcs we sample the *true N-gon boundary* using a polar distance function, so the outer
      polylines follow straight edges with kinks at vertices.
    """

    # ------------------------- public factory ---------------------------------
    def __new__(
        cls,
        *,
        n_sides: int,
        rint: float,
        rext: float,
        ftype: str = "full",
        intype: str = "square",
        optArea: str = "all",
        refLevels: Iterable[int] | None = None,
        dx_min: float | None = None,
        nx: int = 1,
        nr: int | None = None,
        center: Tuple[float, float, float] = (0.0, 0.0, 0.0),
        theta: float = 0.0,
        normal: Tuple[float, float, float] = (0.0, 0.0, 1.0),
        pid: int = 1,
    ):
        # Create a temporary, empty Surface; we only use it to access helper methods.
        self = super().__new__(cls)
        __pid = pid  # remember requested pid for the fused result

        # --- Angular subdivision selection -------------------------------------
        if dx_min is not None:
            # Ensure at least two divisions; approximate along inner square/arc
            nx = max(int(rint / dx_min), 2)

        # Make nx compatible with the angular refinement LCM (preserves original logic)
        if refLevels:
            lcm_val = list(refLevels)[0]
            for val in list(refLevels)[1:]:
                lcm_val = abs(lcm_val * val)
            if nx % lcm_val != 0:
                nx = math.ceil(nx / lcm_val) * lcm_val

        # --- Radial subdivision / grading ---------------------------------------
        nr, grading, details = self.__compute_nr_and_grading(rint, rext, nx, nr)

        # Keep radial count compatible with number of refinement levels
        if refLevels:
            if nr % len(list(refLevels)) != 0:
                nr = math.ceil(nx / len(list(refLevels))) * len(list(refLevels))

        # --- fraction validity -------------------------------------------------
        ftype = (ftype or "full").lower()
        if ftype == "quarter" and (n_sides % 2 != 0):
            raise ValueError("quarter mesh is only possible when n_sides % 2 == 0")
        self._check_length_consistency(rint,rext)
    
        # P_int = self._build_sidepoints(3*rint,n_sides)
        P_ext = self._build_sidepoints(rext,n_sides)
        # ---- central zone ----- 
        # if n_sides % 2 != 0:
        S1, L_inner = self._build_inner_geometry(rint, nx, n_sides, intype)
        
        if optArea != "hollow":
            surfaces = [S1]
        else:
            surfaces=[]
            
        if optArea != "central":           
            if refLevels:
                
                r_ref = rint * math.sqrt(2) if intype == "square" else rint
                levels = list(refLevels)
                
                x0 = rint
                factor1 =  math.sqrt(2)  if intype == "square" else 1
                factor2 =  1.25 if n_sides % 2 else 1.05
                x1 = factor1*factor2*rint / math.cos(math.pi/n_sides)
                 
                P_b0 = self._build_sidepoints(x1,n_sides)
                L_outer = self._build_polyline_points(P_b0, nx, n_sides, pid=2)        
   
                nr, grading, details = self.__compute_nr_and_grading(x0, x1, nx)
                S_band = Surface(L_inner, L_outer, n=nr, grading=grading,
                                          progression="geometric", pid=pid)
                L_inner = L_outer
                surfaces.append(S_band)
                
                # now compute bands
                bands = BandMesh(
                    compute_fn=self.__compute_nr_and_grading,
                    x_init=x1,
                    x_end=rext,
                    nx=nx,
                    refLevel=refLevels,
                )
                
                segments = bands.segment
                pid = 2
                for s in segments:
                    _P0 = self._build_sidepoints(s.x0, n_sides)
                    _P1 = self._build_sidepoints(s.x1, n_sides)
                    _L0 = self._build_polyline_points(_P0, s.nx0, n_sides, pid=3)  
                    _L1 = self._build_polyline_points(_P1, s.nx1, n_sides, pid=3)  
                    if s.band:
                        Surf = Raccord2D(_L0, _L1, quad=True,pid = pid)
                    else:
                        Surf = Surface(_L0, _L1, n=s.nr, grading=s.grading,
                                                  progression="geometric", pid=pid)
                    surfaces.append(Surf)
                    pid = pid + 1
           
            else:
                L_ext = self._build_polyline_points(P_ext, nx, n_sides, pid = 3)
                S2 = Surface(L_inner, L_ext, n=nr, grading=grading, progression="geometric", pid = 3)
                surfaces.append(S2)
            
        # --- Merge/fuse surfaces into a single unstructured grid -----------------
        append = vtk.vtkAppendFilter()
        for s in surfaces:
            # Support both Surface APIs (direct grid or `get_vtk_unstructured_grid`)
            if hasattr(s, "get_vtk_unstructured_grid"):
                append.AddInputData(s.get_vtk_unstructured_grid())
            else:
                append.AddInputData(s._ugrid)
        append.Update()
        merged = append.GetOutput()

        cleaner = vtk.vtkStaticCleanUnstructuredGrid()
        cleaner.SetInputData(merged)
        cleaner.SetTolerance(1e-8)
        cleaner.RemoveUnusedPointsOn()
        cleaner.Update()
        cleaned = cleaner.GetOutput()

        fused = Surface(pid=__pid)
        fused._ugrid = cleaned
        fused.pid = __pid
        
        # --- Mirror/fuse according to ftype, then orient, rotate, translate ------
        out = self.__make_by_ftype(fused, ftype, n_sides)
        out.set_orientation(normal=(0, 0, 1))
        out = self.__rotate_about_z(out, theta)
        out = self.__align_z_to_normal(out, normal, center=(0, 0, 0))
        out = translate(out, center)

        return out      
            

               

    # ------------------------- private helpers --------------------------------

    
    def _check_length_consistency(self, rint: float, rext: float) -> None:
        """Ensure central area fits within the allowed geometry.
        
        Raises ValueError if condition is violated, with guidance.
        """
        factor = 2.99
        if rext <= factor * rint:
            rext_min = math.ceil(factor * rint)
            rint_max = math.floor(rext / factor)
            raise ValueError(
                f"Inconsistent dimensions: diag of square with rint={rint} "
                f"is too large for rext={rext}. "
                f"-> Smallest allowed rext = {rext_min} "
                f"or Biggest allowed rint = {rint_max}"
            )
            
    def _check_circle_consistency(self, rint: float, rext: float) -> None:
        """Ensure square diagonal fits within the allowed geometry.
        
        Raises ValueError if condition is violated, with guidance.
        """
        factor = 10 * (math.sqrt(2) - 1) + 1  #  1.828
        if rext <= factor * rint:
            rext_min = math.ceil(factor * rint)
            rint_max = math.floor(rext / factor)
            raise ValueError(
                f"Inconsistent dimensions: diag of square with rint={rint} "
                f"is too large for rext={rext}. "
                f"-> Smallest allowed rext = {rext_min} "
                f"or Biggest allowed rint = {rint_max}"
            )
            
    def _build_sidepoints(self, r: float, n_sides: int) -> List[Point]:
        """Generate internal points based on rint and number of sides."""
        __P: List[Point] = []
        angle_ref = 2 * math.pi / n_sides
    
        if n_sides % 2 != 0:  # odd number of sides
            __P = [
                Point(r * math.sin(i * angle_ref), r * math.cos(i * angle_ref), 0)
                for i in range(0, n_sides // 2 + 1)
            ]
            __P.append(Point(0, r * math.cos((n_sides // 2) * angle_ref)  , 0))
    
        else:  # even number of sides
            H = r / math.cos(angle_ref/2)
            __P = [
                Point(H * math.sin(i * angle_ref) , H * math.cos(i * angle_ref), 0)
                for i in range(0, n_sides // 4 + 1)
            ]
            for pt in __P : pt.rotate((0,0,0),'z', angle_ref/2*360/2/math.pi)
            __P.pop(0)
            __P.insert(0,Point(0,r,0))
            __P.append(Point(r,0,0))
        return __P.copy()
    
    def _build_inner_geometry(self, r: float, n: int, n_sides: int, intype: str = "diamond"):
        """
        Create inner surface S1 and inner boundary L_inner.
    
        Args:
            r (float): size parameter (was rint)
            n (int):   element count along each constructed edge (was nx)
            n_sides (int): polygon sides (parity used to mirror/fuse)
            intype (str): "square", "circle", or anything else -> 45° diamond
    
        Returns:
            (S1, L_inner): tuple of constructed Surface and inner curve (PolyLine or Arc)
        """
        if r <= 0:
            raise ValueError("r must be > 0")
        if n <= 0:
            raise ValueError("n must be > 0")
    
        # Base points (pid=1)
        P1 = Point(0,  r, 0, pid=1)   # top
        P3 = Point( r, 0, 0, pid=1)   # right
        P5 = Point(0, -r, 0, pid=1)   # bottom
        P6 = Point(0,  0, 0, pid=1)   # center
    
        if intype == "square":
            P2 = Point(r,  r, 0, pid=1)
            P4 = Point(r, -r, 0, pid=1)
        elif intype == "circle":
            # For circle we still need P2 (quarter point) to define the arc
            c45 = math.cos(math.radians(45.0))
            s45 = math.sin(math.radians(45.0))
            P2 = Point(r * c45, r * s45, 0, pid=1)
            P4 = Point(r * c45, -r * s45, 0, pid=1)
        else:
            # default "diamond" (45° corner on the right side)
            c45 = math.cos(math.radians(45.0))
            s45 = math.sin(math.radians(45.0))
            P2 = Point(r * c45,  r * s45, 0, pid=1)
            P4 = Point(r * c45, -r * s45, 0, pid=1)
    
        if intype != "circle":
            # Build rectangular/diamond patch with 3 lines plus center edge
            L1 = Line(P6, P3, n=n)
            L2 = Line(P3, P2, n=n)
            L3 = Line(P2, P1, n=n)
            L4 = Line(P1, P6, n=n)
            S1 = Surface(L1, L2, L3, L4, n=1, pid=1)
    
            if n_sides % 2:  # odd -> mirror across zx and fuse
                S1_bis = syme(S1, plane='zx')
                S1 = fuse(S1, S1_bis, pid=1, verbose=False)
                L_inner = PolyLine(P1, P2, P3, P4, P5, n=n, pid=2)
            else:
                L_inner = PolyLine(P1, P2, P3, n=n, pid=2)
    
        else:
            # Circular quarter patch
            L1 = Line(P6, P3, n=n)
            L2 = Line(P1, P6, n=n)
            L_inner = Arc.from_3_points(P3, P2, P1, n=2 * n + 1, pid=2)
    
            LC = fuse(L1, L2, verbose=False)
            LC = fuse(LC, L_inner, verbose=False)
            S1 = Surface(LC, n=1, quad=True, pid=1)
    
            if n_sides % 2:  # odd -> mirror & update L_inner to span half-turn
                S1_bis = syme(S1, plane='zx')
                S1 = fuse(S1, S1_bis, pid=1, verbose=False)
                L_inner = Arc.from_3_points(P5, P3, P1, n=4 * n + 1, pid=2)
    
        return S1, L_inner
    
    def _build_polyline_points(self, Plist, n_elem: int, n_sides: int, pid:int = 1):
        """
        Given a list of vertices Plist, a base element count n_elem,
        and the number of polygon sides n_sides, return a polyline Lpts
        with regularly distributed points (last segment ~ half size).
        """
        # Compute total number of points along the polyline
        if n_sides % 2:   # odd
            n_central = n_elem * 4
        else:             # even
            n_central = n_elem * 2
    
        S = len(Plist) - 1   # number of segments
        if S <= 0:
            raise ValueError("Plist must contain at least two points")
    
        target_sum = n_central
    
        # weights: all segments weight=1, last segment weight=0.5
        if n_sides % 2:  # odd
            weights = [1.0] * max(S - 1, 0) + [0.5]
        else:  # even
            if n_sides == 4:
                weights = [1.0, 1.0]
            elif n_sides % 4 == 0:
                weights = [0.5] + [1.0] * max(S - 2, 0) + [0.5]
            else:
                weights = [0.5] + [1.0] * max(S - 1, 0)
     

        sum_w = sum(weights)
    
        # ideal (real-valued) allocations
        ideal = [target_sum * (w / sum_w) for w in weights]
    
        # start with floors
        n_per_seg = [int(math.floor(x)) for x in ideal]
    
        # distribute leftover points by largest fractional parts
        rem = target_sum - sum(n_per_seg)
        if rem > 0:
            fracs = [(ideal[i] - n_per_seg[i], i) for i in range(S)]
            fracs.sort(reverse=True)  # descending
            for _, idx in fracs[:rem]:
                n_per_seg[idx] += 1
    
        # cap the last segment so it stays close to "half"
        last_cap = int(math.ceil(ideal[-1]))
        if n_per_seg[-1] > last_cap:
            excess = n_per_seg[-1] - last_cap
            n_per_seg[-1] = last_cap
            if excess > 0:
                fracs_no_last = [(ideal[i] - n_per_seg[i], i) for i in range(S - 1)]
                fracs_no_last.sort(reverse=True)
                k = 0
                while excess > 0 and k < len(fracs_no_last):
                    j = fracs_no_last[k][1]
                    n_per_seg[j] += 1
                    excess -= 1
                    k += 1
                i = 0
                while excess > 0:
                    n_per_seg[i % (S - 1)] += 1
                    excess -= 1
                    i += 1
    
        # Final check
        assert sum(n_per_seg) == target_sum, (
            f"Expected {target_sum}, got {sum(n_per_seg)} with {n_per_seg}"
        )
    
        # Build and fuse segments
        Lpts = Line(Plist[0], Plist[1], n=n_per_seg[0])
        for i in range(1, S):
            L_tmp = Line(Plist[i], Plist[i+1], n=n_per_seg[i])
            Lpts = fuse(Lpts, L_tmp, verbose=False, pid = pid)
    
        return Lpts.copy()

  
    
    def __targets(
        self,
        rint: float,
        rext: float,
        nx: int,
        inner_mode: str = "cartesian",
        pad_in: float = 1.0,
        pad_out: float = 1.0,
    ) -> tuple[float, float]:
        """
        Target edge lengths at inner/outer radii for one quadrant.

        Returns
        -------
        (s_in, s_out) : tuple[float, float]
            Desired chord/segment lengths to compare against radial steps.
        """
        if inner_mode == "arc":
            s_in = (math.pi * rint) / (4.0 * nx)   # chord length along inner arc
        else:
            s_in = rint / nx                       # cartesian inner edge
        s_out = (math.pi * rext) / (4.0 * nx)      # chord length along outer arc
        return pad_in * s_in, pad_out * s_out

    def __compute_nr_and_grading(
        self,
        rint: float,
        rext: float,
        nx: int,
        nr: int | None = None,
        inner_mode: str = "cartesian",
        pad_in: float = 1.0,
        pad_out: float = 1.0,
        search_span: int = 6,
    ) -> tuple[int, float, dict]:
        """
        Choose radial divisions `nr` and geometric grading to match inner/outer target sizes.

        If `nr` is provided, use it directly (returning associated grading and details).
        Otherwise, search around an isometric guess to minimize mismatch at inner/outer rims.
        """
        assert rext > rint > 0 and nx >= 1
        s_in, s_out = self.__targets(rint, rext, nx, inner_mode, pad_in, pad_out)
        dtheta = math.pi / (4.0 * nx)

        def _eval(N: int) -> dict:
            q = (rext / rint) ** (1.0 / N)           # per-step radial ratio
            dr0 = rint * (q - 1.0)                   # first radial step
            drL = rext * (q - 1.0)                   # last radial step
            grading = q ** (N - 1)                   # total progression across band
            iso = (q - 1.0) / dtheta                 # compare against angular spacing
            err = (dr0 / s_in - 1.0) ** 2 + (drL / s_out - 1.0) ** 2
            ok_in = dr0 + 1e-12 >= s_in
            ok_out = drL + 1e-12 >= s_out
            return dict(
                nr=N, q=q, grading=grading, dr0=dr0, dr_last=drL,
                s_in=s_in, s_out=s_out, iso=iso, ok_in=ok_in, ok_out=ok_out, err=err
            )

        # If user forced `nr`, honor it and compute derived quantities.
        if nr is not None:
            sol = _eval(nr)
            return sol["nr"], sol["grading"], sol

        # Seed around "isometric" guess (q ~ 1 + dtheta)
        q_iso = 1.0 + dtheta
        n_star = max(1, math.log(rext / rint) / math.log(q_iso))
        seeds = [max(1, int(math.floor(n_star))), max(1, int(math.ceil(n_star)))]

        best = None
        tried: set[int] = set()
        for base in seeds:
            for k in range(-search_span, search_span + 1):
                N = max(1, base + k)
                if N in tried:
                    continue
                tried.add(N)
                sol = _eval(N)
                penalty = (0 if sol["ok_in"] else 1_000) + (0 if sol["ok_out"] else 1_000)
                score = penalty + sol["err"] + 0.1 * abs(sol["iso"] - 1.0)
                sol["score"] = score
                if best is None or score < best["score"]:
                    best = sol
        return best["nr"], best["grading"], best  # type: ignore[index]

    def __geometric_spacing_points(self, p1, p2, n: int, grading: float = 1.0) -> np.ndarray:
        """
        Interpolate `n` segments between points `p1` and `p2` using geometric spacing.

        Parameters
        ----------
        p1, p2 : array-like
            End points (3D).
        n : int
            Number of segments (returns n+1 points).
        grading : float
            Ratio of last step to first step (1.0 -> uniform).

        Returns
        -------
        numpy.ndarray
            Array of shape (n+1, 3) with interpolated points.
        """
        if n < 1:
            raise ValueError("n must be >= 1")
        p1 = np.asarray(p1, float)
        p2 = np.asarray(p2, float)
        if grading <= 0:
            raise ValueError("grading must be > 0")

        if abs(grading - 1.0) < 1e-12:
            t = np.linspace(0.0, 1.0, n + 1)
        else:
            q = grading ** (1.0 / (n - 1))
            i = np.arange(n + 1, dtype=float)
            t = (q ** i - 1.0) / (q ** n - 1.0)
        return p1 * (1.0 - t)[:, None] + p2 * t[:, None]

    def __dtheta(self, nx: int, ftype: str = "quarter") -> float:
        """Angular step per segment in a quadrant; kept for compatibility with original logic."""
        return math.pi / (4.0 * nx)

    def __geom_sum(self, first: float, q: float, n: int) -> float:
        """Geometric series partial sum: first + first*q + ... (n terms)."""
        if n <= 0:
            return 0.0
        if abs(q - 1.0) < 1e-12:
            return n * first
        return first * (q**n - 1.0) / (q - 1.0)


    def __make_by_ftype(self, q1: Surface, ftype: str, n_side: int) -> Surface:
        """
        Mirror/fuse a quadrant according to `ftype`, with parity rules on `n_side`.
    
        Parity rules:
        - n_side even (pair): same behavior as before
            * "quarter": return as-is
            * "half":    mirror in YZ and fuse
            * "full":    mirror to half (YZ), fuse, then mirror across ZX, fuse
        - n_side odd (impair):
            * "quarter": not allowed (raises ValueError)
            * "half":    do nothing (return as-is)
            * "full":    mirror in YZ and fuse  (i.e., previous "half")
        """
        if n_side < 1:
            raise ValueError("n_side must be >= 1")
    
        ftype = (ftype or "quarter").lower()
        is_odd = (n_side % 2 == 1)
    
        if not is_odd:  # even (pair): original behavior
            if ftype == "quarter":
                return q1
            if ftype == "half":
                q2 = syme(q1, plane="yz", pid=q1.pid)
                return fuse(q1, q2, pid=q1.pid, merge=True, verbose=False)
            if ftype == "full":
                q2 = syme(q1, plane="yz", pid=q1.pid)
                demi = fuse(q1, q2, pid=q1.pid, merge=True, verbose=False)
                q3 = syme(demi, plane="zx", pid=demi.pid)
                return fuse(demi, q3, pid=demi.pid, merge=True, verbose=False)
            raise ValueError("ftype must be one of: 'quarter', 'half', 'full'")

        # odd (impair)
        if ftype == "quarter":
            raise ValueError("With an odd n_side, 'quarter' is not allowed.")
        if ftype == "half":
            return q1
        if ftype == "full":
            q2 = syme(q1, plane="yz", pid=q1.pid)
            return fuse(q1, q2, pid=q1.pid, merge=True, verbose=False)
    
        raise ValueError("ftype must be one of: 'quarter', 'half', 'full'")


    def __rotate_about_z(self, mesh: Surface, theta_deg: float) -> Surface:
        """Rotate `mesh` about +Z by `theta_deg` degrees (no-op if |theta| ~ 0)."""
        if abs(theta_deg) < 1e-12:
            return mesh
        return rotate(mesh, axis="z", angle=float(theta_deg))

    def __align_z_to_normal(
        self, mesh: Surface, normal_vec: Iterable[float], center: tuple[float, float, float] = (0, 0, 0)
    ) -> Surface:
        """
        Rotate `mesh` so that +Z aligns with `normal_vec`, around a computed axis through `center`.
        """
        ez = np.array([0.0, 0.0, 1.0], dtype=float)
        n = np.array(normal_vec, dtype=float)
        n_norm = np.linalg.norm(n)
        if n_norm < 1e-15:
            raise ValueError("normal vector must be non-zero")
        n = n / n_norm

        c = float(np.clip(np.dot(ez, n), -1.0, 1.0))
        ang_deg = math.degrees(math.acos(c))
        if ang_deg < 1e-12:
            return mesh

        axis = np.cross(ez, n)
        ax_norm = np.linalg.norm(axis)
        if ax_norm < 1e-12:
            axis = (1.0, 0.0, 0.0)  # arbitrary axis if vectors are opposite colinear
        else:
            axis = tuple(axis / ax_norm)

        return rotate(mesh, center=center, axis=axis, angle=ang_deg)