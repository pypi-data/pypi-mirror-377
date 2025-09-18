#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 05/02/2025
Last modified on 07/02/2025

Author: Alexis Sauvageon
Email: alexis.sauvageon@gmail.com

Description: This module defines geometrical classes and functions for managing 
2D elements (surfaces) within a 3D space, including operations such as mesh generation,
coordinate transformations, and surface construction. The Surface class supports advanced 
functionalities such as constructing surfaces from points, lines, or contours, applying 
transfinite meshing for structured quadrilateral grids, and converting the resulting mesh 
to VTK unstructured grids for visualization.
"""

import vtk
import numpy as np
from vtk.util import numpy_support
from pybmesh.geom.mesh import Elem
from pybmesh.geom.d0 import Point
from pybmesh.geom.d1 import Line, PolyLine
from pybmesh.utils.constants import _TOL
from pybmesh.utils.vtkquery import  nbEl, nbPt
from pybmesh.utils.vtkcorrection import are_dupNodes, are_id_oriented
from pybmesh.utils.detection import corner_mask_auto
import gmsh
# from pybmesh.utils.debug import plot_points_with_corners
from pybmesh.io.viewer import plot

class Surface(Elem):
    """
    A class to represent a surface constructed from points, lines, or contours.
    
    The Surface class supports multiple construction methods depending on the input:
      - A sequence of Point objects (forming a closed contour).
      - Multiple Line or PolyLine objects forming a closed contour.
      - A single Line representing a closed contour.
      - Two Line objects used to generate a surface between them.
    
    The generated surface mesh can be structured (quadrilaterals) or unstructured (triangles)
    based on the provided parameters.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize a Surface from the provided 1D elements.

        This constructor supports multiple construction methods based on the input arguments.
        Depending on the type and number of arguments, a surface can be created from:
          - A series of Point objects forming a closed contour.
          - A series of Line or PolyLine objects.
          - A single Line representing a contour.
          - Two Line objects to create a surface between them.

        Keyword Args:
            quad (bool): If True, use quadrilateral (structured) meshing (default: True).
            transfinite (bool): If True, apply transfinite meshing (default: True).
            pid (int): The part ID representing the mesh entity (default: 0).
            n, size, corners, grading, progression: Additional parameters for mesh generation.
        """
        self.quad = kwargs.get('quad', True)
        self.transfinite = kwargs.get('transfinite', True)
        pid = kwargs.get('pid', 0)
        super().__init__(pid=pid)  # Initialize the Mesh base class with the specified pid
        
        edges_point = None
        is_corners = None
        
        if len(args) > 1 and isinstance(args[0], Point):
            # Case 0: Surface(p1, p2, p3, ..., size=0.1, quad=True)
            edges_point, is_corners = self._build_surface_from_points(
                *args,
                n=kwargs.get('n', None),
                size=kwargs.get('size', None),
                corners=kwargs.get('corners', None)
            )

        elif len(args) > 2 and isinstance(args[0], Line):
            # Case 1: Surface(l1, l2, l3, ..., quad=True)
            edges_point, is_corners = self._build_surface_from_lines(
                *args,
                corners=kwargs.get('corners', None)
            )

        elif len(args) == 1 and isinstance(args[0], Line):
            # Case 2: Surface(Line, quad=True) Generate a grid based on a specified contour
            edges_point, is_corners = self._build_surface_from_contour(
                args[0],
                corners=kwargs.get('corners', None)
            )

        elif len(args) == 2 and isinstance(args[0], Line) and isinstance(args[1], Line):
            # Case 3 & 4: Surface(l1, l2, n=None, size=None, grading=1, progression='linear', quad=True)
            l1, l2 = args[0], args[1]
            if nbEl(l1) != nbEl(l2):
                raise ValueError("l1 and l2 must have the same number of elements.")

            # Build the surface from two lines
            edges_point, is_corners = self._build_surface_from_two_lines(
                l1, l2,
                n=kwargs.get('n', None),
                size=kwargs.get('size', None),
                grading=kwargs.get('grading', 1),
                progression=kwargs.get('progression', 'linear'),
            )
        elif len(args) == 0:
            pass
        else:
            raise ValueError("Unsupported constructor arguments for Surface")

        # # Display the points with corner markers for debugging/visualization purposes
        # plot_points_with_corners(edges_point, is_corners)
        if edges_point is not None:
            mesh = self._call_gmsh(edges_point, is_corners)
            self._build_ugrid(mesh)

    def set_orientation(self, normal=None, eps=1e-12):
        """
        Flip ONLY those surface faces whose normals have a negative dot w.r.t. `normal`.
        - Works for vtkPolyData and any vtkDataSet (e.g. vtkUnstructuredGrid) by extracting the surface.
        - If `normal` is None or "auto", pick the dominant axis (±x, ±y, or ±z) from the
          mean cell normal of the surface.
        - eps: tolerance around zero for the dot test.
        - If as_unstructured=True, returns a vtkUnstructuredGrid (casted from PolyData).
        Returns: (vtkDataSetOut, num_flipped_cells)
        """

    
        # 1) Ensure we operate on a polygonal surface
        dataobj = self._ugrid
        if isinstance(dataobj, vtk.vtkPolyData):
            poly_port = None
            poly_in = dataobj
        else:
            surf = vtk.vtkDataSetSurfaceFilter()
            surf.SetInputData(dataobj)
            surf.Update()
            poly_port = surf.GetOutputPort()
            poly_in = surf.GetOutput()
    
        # 2) Consistent winding + compute **cell** normals
        n = vtk.vtkPolyDataNormals()
        (n.SetInputConnection(poly_port) if poly_port else n.SetInputData(poly_in))
        n.ConsistencyOn()
        n.AutoOrientNormalsOn()      # coherent start; well still correct bad cells selectively
        n.SplittingOff()
        n.ComputePointNormalsOff()
        n.ComputeCellNormalsOn()
        n.Update()
        pd = n.GetOutput()           # polydata with CellData array "Normals"
    
        # 2.5) Auto-pick axis-aligned up if needed
        if normal is None or (isinstance(normal, str) and normal.lower() == "auto"):
            # Get mean cell normal
            carr = pd.GetCellData().GetArray("Normals")
            if carr is None or carr.GetNumberOfTuples() == 0:
                # Fallback: default to +Z if somehow normals are missing
                up = np.array([0.0, 0.0, 1.0], dtype=float)
            else:
                n_np = numpy_support.vtk_to_numpy(carr)  # shape (nCells, 3)
                mean_n = n_np.mean(axis=0)
                # If degenerate, fallback to +Z
                if not np.all(np.isfinite(mean_n)) or np.linalg.norm(mean_n) < 1e-20:
                    up = np.array([0.0, 0.0, 1.0], dtype=float)
                else:
                    # Pick axis with largest |component| and keep sign
                    idx = int(np.argmax(np.abs(mean_n)))
                    sign = 1.0 if mean_n[idx] >= 0.0 else -1.0
                    axes = np.eye(3)
                    up = sign * axes[idx]
        else:
            up = np.asarray(normal, dtype=float)
    
        # Normalize up and unpack
        up = up / (np.linalg.norm(up) + 1e-30)
        ux, uy, uz = map(float, up)
        
    
        # 3) Per-cell dot(normal, up) via ArrayCalculator (cell data)
        calc = vtk.vtkArrayCalculator()
        calc.SetInputData(pd)
        calc.SetAttributeTypeToCellData()
        calc.AddScalarVariable("Nx", "Normals", 0)
        calc.AddScalarVariable("Ny", "Normals", 1)
        calc.AddScalarVariable("Nz", "Normals", 2)
        ux, uy, uz = map(float, up / (np.linalg.norm(up) + 1e-30))
        calc.SetResultArrayName("updot")
        calc.SetFunction(f"Nx*{ux} + Ny*{uy} + Nz*{uz}")
        calc.Update()
        pd_with_dot = calc.GetOutput()
    
        # 4) Split with vtkThreshold on the per-cell scalar "updot"
        def threshold_range(lower, upper):
            thr = vtk.vtkThreshold()
            thr.SetInputData(pd_with_dot)
            thr.SetInputArrayToProcess(
                0, 0, 0, vtk.vtkDataObject.FIELD_ASSOCIATION_CELLS, "updot"
            )
            thr.SetLowerThreshold(lower)
            thr.SetUpperThreshold(upper)
            thr.Update()
            return thr.GetOutput()
    
        # Negative (strictly below -eps) -> needs flipping
        neg_ugrid = threshold_range(-1e30, -abs(eps))
        # Non-negative (>= -eps) -> OK; you can tighten this to [eps, +8) and
        # handle tiny magnitudes separately if desired.
        pos_ugrid = threshold_range(-abs(eps), 1e30)
    
        # Convert both threshold outputs (UGrids) back to PolyData surfaces
        to_surf = vtk.vtkDataSetSurfaceFilter()
        to_surf.SetInputData(neg_ugrid); to_surf.Update()
        neg_pd = to_surf.GetOutput()
    
        to_surf2 = vtk.vtkDataSetSurfaceFilter()
        to_surf2.SetInputData(pos_ugrid); to_surf2.Update()
        pos_pd = to_surf2.GetOutput()
    
        # Count how many cells were about to flip
        num_to_flip = neg_pd.GetNumberOfCells()
    
        # 5) Flip ONLY the negative part
        if num_to_flip > 0:
            rev = vtk.vtkReverseSense()
            rev.SetInputData(neg_pd)
            rev.ReverseCellsOn()
            rev.ReverseNormalsOn()
            rev.Update()
            flipped_neg_pd = rev.GetOutput()
        else:
            flipped_neg_pd = neg_pd  # empty
    
        # 6) Append back: (positive unchanged) + (flipped negative)
        app = vtk.vtkAppendPolyData()
        app.AddInputData(pos_pd)
        app.AddInputData(flipped_neg_pd)
        app.Update()
        oriented_pd = app.GetOutput()
    
        cast = vtk.vtkAppendFilter()       # PolyData -> UnstructuredGrid
        cast.AddInputData(oriented_pd)
        cast.Update()
        ug = vtk.vtkUnstructuredGrid()
        ug.ShallowCopy(cast.GetOutput())
        
        # Remove from both cell and point data if present
        temp_names = [
            "Normals",          # from vtkPolyDataNormals
            "updot",            # from ArrayCalculator
            "vtkOriginalCellIds",
            "vtkOriginalPointIds",
            "vtkValidPointMask",
            "vtkGhostType",
        ]
        cd = ug.GetCellData()
        pd_ = ug.GetPointData()
        for name in temp_names:
            if cd.GetArray(name): cd.RemoveArray(name)
            if pd_.GetArray(name): pd_.RemoveArray(name)
        self._ugrid = ug

    def _build_edges(self, edges_points):
        """
        Build edge connectivity from a list of edge points.

        Each edge is defined by a pair of consecutive points, with the final edge connecting
        the last point to the first to close the loop.

        Parameters:
            edges_points (list or np.ndarray): Sequence of points defining the edge coordinates.

        Returns:
            dict: A dictionary where each key is an edge index and the value is another dictionary containing:
                - 'pid1': Index of the first point.
                - 'pid2': Index of the second point.
                - 'p1': Coordinates of the first point.
                - 'p2': Coordinates of the second point.
                - 'dir': Normalized direction vector from p1 to p2.
        """
        edges = {}
        n = len(edges_points)

        # Process each edge from point[i] to point[i+1]
        for i in range(n - 1):
            p1 = edges_points[i]
            p2 = edges_points[i + 1]
            vec = p2 - p1
            norm = np.linalg.norm(vec)
            # Normalize the direction (avoid division by zero)
            if norm > 0:
                dir_vec = tuple((vec / norm).tolist())
            else:
                dir_vec = (0.0, 0.0, 0.0)

            edges[i] = {
                'pid1': i,
                'pid2': i + 1,
                'p1': p1,
                'p2': p2,
                'dir': dir_vec
            }

        # Handle the closing edge: from the last point to the first point.
        p1 = edges_points[-1]
        p2 = edges_points[0]
        vec = p2 - p1
        norm = np.linalg.norm(vec)
        if norm > 0:
            dir_vec = tuple((vec / norm).tolist())
        else:
            dir_vec = (0.0, 0.0, 0.0)

        edges[n - 1] = {
            'pid1': n - 1,
            'pid2': 0,
            'p1': p1,
            'p2': p2,
            'dir': dir_vec
        }

        return edges

    def _build_surface_from_points(self, *points, n=None, size=None, corners=None):
        """
        Build a surface from a sequence of Point objects.

        Ensures that the provided points form a closed contour, then creates a PolyLine.
        Unique points are extracted, and corner detection is performed either automatically
        or based on the provided corner points.

        Parameters:
            *points: Sequence of Point objects.
            n (int, optional): Number of segments for interpolation (default is None).
            size (float, optional): Segment size for interpolation (default is None).
            corners (list, optional): List of points to explicitly mark as corners (default is None).

        Returns:
            tuple: A tuple containing:
                - edges_points (np.ndarray): Unique points forming the surface edges.
                - is_corners (np.ndarray): Boolean array indicating corner points.
        """
        if (n, size) == (None, None):
            n = 1

        points = list(points)
        # Ensure points form a closed contour
        if not are_dupNodes(points[-1], points[0]):
            points.append(points[0])  # Close the contour by appending the first point at the end

        polyline = PolyLine(*points, n=n, size=size)

        points = polyline.get_points()

        flattened = np.vstack(points)
        edges_points = self._get_unique_points(flattened)
        if corners is None:
            is_corners = corner_mask_auto(edges_points)
        else:
            is_corners = np.array([
                any(are_dupNodes(pt, corner) for corner in corners)
                for pt in edges_points
            ])

        return edges_points, is_corners

    def _build_surface_from_lines(self, *lines, corners=None):
        """
        Build a surface from multiple Line or PolyLine objects.

        Validates that the provided lines form a closed contour and then extracts nodes
        to generate the surface mesh. Corner detection is applied automatically unless specified.

        Parameters:
            *lines: Sequence of Line or PolyLine objects.
            corners (list, optional): List of points to explicitly mark as corners (default is None).

        Returns:
            tuple: A tuple containing:
                - edges_points (np.ndarray): Unique points forming the surface edges.
                - is_corners (np.ndarray): Boolean array indicating corner points.
        """
        all_nodes = []  # To store all nodes from all lines

        # Iterate through each line to check if contour is closed and gather nodes/cells
        for i, line in enumerate(lines):
            line_points = line.get_points()
            grid = line.get_vtk_unstructured_grid()

            # Check if the contour is closed between lines
            if i < len(lines) - 1:
                next_line_points = lines[i + 1].get_points()
                # Ensure the end of the current line matches the start of the next line
                if not are_dupNodes(line_points[-1], next_line_points[0]):
                    raise ValueError(
                        f"The contour formed by lines is not closed. Line {i+1} end point does not match Line {i+2} start point."
                    )
                # Check if the contour is closed by comparing the first and last points of the entire sequence
                if not are_dupNodes(lines[0].get_points()[0], lines[-1].get_points()[-1]):
                    raise ValueError("The contour formed by lines is not closed. First and last line points do not match.")

            vtk_points = grid.GetPoints().GetData()
            all_nodes.append(numpy_support.vtk_to_numpy(vtk_points))

        flattened = np.vstack(all_nodes)
        # Extract unique points and detect corners
        edges_points = self._get_unique_points(flattened)
        if corners is None:
            is_corners = corner_mask_auto(edges_points)
        else:
            is_corners = np.array([
                any(are_dupNodes(pt, corner) for corner in corners)
                for pt in edges_points
            ])
        # Display the points with corner markers (for debugging)
        # plot_points_with_corners(edges_points, is_corners)
        return edges_points, is_corners

    def _build_surface_from_contour(self, polyline, corners=None):
        """
        Generate a surface from a single closed contour Line or PolyLine.

        Validates that the contour is closed and extracts unique edge points. Corner detection is
        performed automatically unless specified.

        Parameters:
            polyline (Line or PolyLine): A closed contour from which to generate the surface.
            corners (list, optional): List of points to explicitly mark as corners (default is None).

        Returns:
            tuple: A tuple containing:
                - edges_points (np.ndarray): Unique points forming the surface edges.
                - is_corners (np.ndarray): Boolean array indicating corner points.
        """
        points = polyline.get_points()
        # Ensure the polyline is a closed contour
        if not are_dupNodes(points[-1], points[0]):
            raise ValueError("The contour formed by lines is not closed.")

        flattened = np.vstack(points)
        edges_points = self._get_unique_points(flattened)
        if corners is None:
            is_corners = corner_mask_auto(edges_points)
        else:
            is_corners = np.array([
                any(are_dupNodes(pt, corner) for corner in corners)
                for pt in edges_points
            ])
        return edges_points, is_corners

    def _build_surface_from_two_lines(self, line1, line2, n=None, size=None, grading=1, progression='linear'):
        """
        Create a surface between two lines by generating intermediate lines.

        The method first checks the orientation of the lines and adjusts if necessary. Then,
        it generates two additional lines connecting the endpoints of the given lines to form
        a closed contour, from which the surface is built.

        Parameters:
            line1 (Line): The first boundary line.
            line2 (Line): The second boundary line.
            n (int, optional): Number of divisions for interpolation (default is None).
            size (float, optional): Size of each segment (default is None).
            grading (float, optional): Grading factor for non-uniform spacing (default is 1).
            progression (str, optional): Type of progression for spacing ('linear' by default).

        Returns:
            tuple: A tuple containing:
                - edges_points (np.ndarray): Unique points forming the surface edges.
                - is_corners (np.ndarray): Boolean array indicating corner points.
        """
        # Step 1: Check if the two lines have the same orientation
        reversed = False

        if are_id_oriented(line1, line2):
            line2.reverse_orientation()
            reversed = True

        # Create four new points to define the intermediate connecting lines
        nl1start = Point(*line1.get_end_point())
        nl1end = Point(*line2.get_start_point())
        nl2start = Point(*line2.get_end_point())
        nl2end = Point(*line1.get_start_point())

        auto_corners = [nl1start.coords, nl1end.coords, nl2start.coords, nl2end.coords]

        newLine1 = Line(nl1start, nl1end, n=n, size=size, grading=grading, progression=progression)
        newLine2 = Line(nl2start, nl2end, n=n, size=size, grading=1/grading, progression=progression)

        lines = (line1, newLine1, line2, newLine2)
        all_nodes = []  # To store all nodes from all lines

        # Iterate through each line to check if the contour is closed and gather nodes
        for i, line in enumerate(lines):
            line_points = line.get_points()
            grid = line.get_vtk_unstructured_grid()

            # Check if the contour is closed between consecutive lines
            if i < len(lines) - 1:
                next_line_points = lines[i + 1].get_points()
                # Ensure the end of the current line matches the start of the next line
                if not are_dupNodes(line_points[-1], next_line_points[0]):
                    raise ValueError(
                        f"The contour formed by lines is not closed. Line {i+1} end point does not match Line {i+2} start point."
                    )
                # Check if the overall contour is closed
                if not are_dupNodes(lines[0].get_points()[0], lines[-1].get_points()[-1]):
                    raise ValueError("The contour formed by lines is not closed. First and last line points do not match.")

            vtk_points = grid.GetPoints().GetData()
            all_nodes.append(numpy_support.vtk_to_numpy(vtk_points))

        flattened = np.vstack(all_nodes)
        # Extract unique edge points and mark corners based on auto_corners
        edges_points = self._get_unique_points(flattened)
        is_corners = np.array([
            any(are_dupNodes(pt, corner) for corner in auto_corners)
            for pt in edges_points
        ])

        if reversed:
            line2.reverse_orientation()  # Restore original orientation

        return edges_points, is_corners

    def _build_ugrid(self, mesh_data):
        """
        Construct the VTK unstructured grid from the mesh data generated by Gmsh.

        The method creates VTK points, maps Gmsh node tags to VTK indices, and constructs
        VTK cells (triangles and quadrilaterals) based on the element types in the mesh data.

        Parameters:
            mesh_data (dict): Dictionary containing mesh nodes and elements information.

        Returns:
            None: The unstructured grid is stored in the instance variable '_ugrid'.
        """
        # Create a VTK unstructured grid object
        self._ugrid = vtk.vtkUnstructuredGrid()

        # Extract nodes from the mesh_data
        node_tags = mesh_data['node_tags']      # List of node tags from gmsh
        node_coords = mesh_data['node_coords']  # Flat list: [x1, y1, z1, x2, y2, z2, ...]
        num_nodes = len(node_tags)

        # Create a mapping from gmsh node tag to index in vtkPoints.
        node_tag_to_index = {}
        # Create a VTK points container and pre-allocate memory
        vtk_points = vtk.vtkPoints()
        vtk_points.SetNumberOfPoints(num_nodes)
        for i, tag in enumerate(node_tags):
            x = node_coords[3 * i]
            y = node_coords[3 * i + 1]
            z = node_coords[3 * i + 2]
            vtk_points.SetPoint(i, x, y, z)
            node_tag_to_index[tag] = i  # Map gmsh node tag to VTK index

        # Set the points for the unstructured grid
        self._ugrid.SetPoints(vtk_points)

        # Prepare containers for cells and cell types
        cells = vtk.vtkCellArray()
        cell_types = vtk.vtkUnsignedCharArray()
        cell_types.SetNumberOfComponents(1)

        # Containers for cells by type (using gmsh element type codes)
        triangle_cells = []  # Gmsh type 2 (3-node triangles)
        quad_cells = []      # Gmsh type 3 (4-node quadrangles)

        # Iterate over each element block in the mesh data.
        for etype, elem_tags, enodes in zip(mesh_data['element_types'],
                                              mesh_data['element_tags'],
                                              mesh_data['element_node_tags']):
            if etype == 2:  # 3-node triangle (gmsh element type 2)
                n_nodes = 3
                for i in range(0, len(enodes), n_nodes):
                    cell = enodes[i:i + n_nodes]
                    vtk_cell = [node_tag_to_index[tag] for tag in cell]
                    triangle_cells.append(vtk_cell)
            elif etype == 3:  # 4-node quadrangle (gmsh element type 3)
                n_nodes = 4
                for i in range(0, len(enodes), n_nodes):
                    cell = enodes[i:i + n_nodes]
                    vtk_cell = [node_tag_to_index[tag] for tag in cell]
                    quad_cells.append(vtk_cell)
            # Additional element types (e.g., lines, tetrahedra) can be handled here if needed.

        # Insert triangle cells into the VTK cell array
        for cell in triangle_cells:
            cells.InsertNextCell(len(cell), cell)
            cell_types.InsertNextValue(vtk.VTK_TRIANGLE)

        # Insert quadrilateral cells into the VTK cell array
        for cell in quad_cells:
            cells.InsertNextCell(len(cell), cell)
            cell_types.InsertNextValue(vtk.VTK_QUAD)

        # Set all cells in the unstructured grid
        self._ugrid.SetCells(cell_types, cells)
        self._generate_pid_field()

    def _call_gmsh(self, edges_points, is_corner):
        """
        Interface with Gmsh to generate a 2D mesh surface from the provided edge points.

        The method creates Gmsh geometry, defines points, lines, and surfaces, applies transfinite
        meshing if required, and extracts the mesh data for further processing.

        Parameters:
            edges_points (np.ndarray): Array of unique points defining the surface edges.
            is_corner (np.ndarray): Boolean array indicating which points are corners.

        Returns:
            dict: A dictionary containing the following keys:
                - 'node_tags': List of Gmsh node tags.
                - 'node_coords': List of node coordinates (flattened).
                - 'element_types': List of element type codes.
                - 'element_tags': List of element tags.
                - 'element_node_tags': List of element connectivity (node tags).
        """
        # Initialize Gmsh and configure options
        gmsh.initialize()
        gmsh.option.setNumber("General.Verbosity", 0)
        gmsh.model.add("surface")
        # Convert edge points into Gmsh points and record corner points
        gmsh_points = []
        gmsh_corners = []
        for i, pt in enumerate(edges_points):
            gmsh_points.append(gmsh.model.geo.addPoint(pt[0], pt[1], pt[2], 1e10))
            if is_corner[i]:
                gmsh_corners.append(gmsh_points[i])

        # Create lines between consecutive points, then close the loop.
        gmsh_lines = [gmsh.model.geo.addLine(gmsh_points[i], gmsh_points[i + 1])
                      for i in range(len(gmsh_points) - 1)]
        gmsh_lines.append(gmsh.model.geo.addLine(gmsh_points[-1], gmsh_points[0]))

        # Set transfinite curve options if quadrilateral meshing is desired.
        if self.quad:
            for l in gmsh_lines:
                gmsh.model.geo.mesh.setTransfiniteCurve(l, 2)

        # Create a curve loop and a plane surface.
        cl = gmsh.model.geo.addCurveLoop(gmsh_lines)
        ps = gmsh.model.geo.addPlaneSurface([cl])

        if self.quad and self.transfinite:
            try:
                gmsh.model.geo.mesh.setTransfiniteSurface(ps, "Left", gmsh_corners)
            except:
                raise ValueError("Unable to mesh quads only, set transfinite to False")

        # Synchronize the geometry and set recombination options.
        gmsh.model.geo.synchronize()

        if self.quad:
            gmsh.model.mesh.setRecombine(2, ps)

        # Generate the 2D mesh.
        gmsh.model.mesh.generate(2)
        # gmsh.fltk.run()
        # Extract mesh data from Gmsh.
        nodeTags, nodeCoords, _ = gmsh.model.mesh.getNodes()
        elemTypes, elemTags, elemNodeTags = gmsh.model.mesh.getElements()
        gmsh.finalize()

        return {
            'node_tags': nodeTags,
            'node_coords': nodeCoords,
            'element_types': elemTypes,
            'element_tags': elemTags,
            'element_node_tags': elemNodeTags
        }

    def _get_unique_points(self, flattened):
        """
        Retrieve unique points from an array while preserving their original order.

        Parameters:
            flattened (np.ndarray): An array of points (each row representing a point).

        Returns:
            np.ndarray: Array of unique points in the original order.
        """
        # Get unique points and the indices of their first occurrence
        unique_points, unique_indices = np.unique(flattened, axis=0, return_index=True)

        # Sort the indices to preserve the original order
        sorted_indices = np.sort(unique_indices)

        # Return the unique points in the original order
        return flattened[sorted_indices]

    def copy(self):
        """
        Create a copy of the current Surface instance.

        The new Surface is created with default points and then the unstructured grid
        is deep-copied from the current instance. Other relevant attributes such as
        'quad' and 'transfinite' are also copied.

        Returns:
            Surface: A new Surface instance that is a copy of the current instance.
        """
        p0 = Point(0, 0, 0)
        p1 = Point(1, 0, 0)
        p2 = Point(1, 1, 0)
        p3 = Point(0, 1, 0)
        new_surf = Surface(p0, p1, p2, p3, n=1)
        new_ugrid = vtk.vtkUnstructuredGrid()
        new_ugrid.DeepCopy(self._ugrid)
        new_surf._ugrid = new_ugrid
        new_surf.quad = self.quad
        new_surf.transfinite = self.transfinite
        new_surf.pid = self._pid
        new_surf.color = self.color
        return new_surf

    def __repr__(self):
        """
        Return the string representation of the Surface.

        Returns:
            str: A string representation of the Surface, with the class name replaced from 'Elem' to 'Surface'.
        """
        repr_str = super().__repr__()
        repr_str = repr_str.replace("Elem", "Surface", 1)
        return repr_str

    @classmethod
    def help(cls):
        """
        Returns helpful information about the Surface class and its methods.
        """
        help_text = """
Surface Class
-------------
A class to represent a surface defined by points, lines, or a contour. The Surface class
allows the creation of a 2D mesh surface based on various input constructions such as:
- A list of Point objects (which will be connected in order).
- A list of Line or PolyLine objects.
- A single Line representing a closed contour.
- Two Line objects to form a surface between them.

Constructor:
-------------
\033[1;32mSurface(*args, quad=True, transfinite=True, color=(0, 0, 1))\033[0m
  - Accepts multiple overloads:
      1. \033[1;32mSurface(Point, Point, ..., n=None, size=None, corners=None)\033[0m
         - Constructs a surface from a sequence of Point objects.
      2. \033[1;32mSurface(Line, Line, ..., corners=None)\033[0m
         - Constructs a surface from multiple Line objects forming a closed contour.
      3. \033[1;32mSurface(Line, corners=None)\033[0m
         - Constructs a surface from a single closed contour Line (generally PolyLine or Circle).
      4. \033[1;32mSurface(Line, Line, n=None, size=None, grading=1, progression='linear')\033[0m
         - Constructs a surface from two Line objects by generating intermediate divisions.
  - \033[1;32mquad\033[0m: Boolean flag indicating if quadrilateral (structured) meshing is desired (default: True).
  - \033[1;32mtransfinite\033[0m: Boolean flag for applying transfinite meshing (default: True).
  - \033[1;32mpid\033[0m: The part ID (pid) representing the mesh entity (default: 0). 

Public Attributes:
------------------
\033[1;32mcolor\033[0m
    The RGB color associated with the element. The color is determined by the part ID (pid)
    and can be used for visualization purposes.                      

Inherited Methods:
-------------------
\033[1;34mtranslate(dx, dy, dz)\033[0m
    Translate all points in the surface by the vector (dx, dy, dz).
\033[1;34mrotate(center, pA, pB, axis, angle, angles, points)\033[0m
    \033[1;34mrotate(center=(0, 0, 0), axis=(0, 0, 1), angle=45)\033[0m
    Rotate all points around the specified axis ('x', 'y', or 'z') by a given angle in degrees.
    \033[1;34mrotate(center, angles=(30, 45, 60))\033[0m
    Rotate all points by specified angles around the X, Y, and Z axes, respectively.
    \033[1;34mrotate(pA=(1, 1, 1), pB=(2, 2, 2), angle=90)\033[0m
    Rotate all points around an axis defined by two points (pA and pB), by a given angle in degrees.
    
    \033[1;34mcenter\033[0m default to (0, 0, 0)
    Point class or tuple may be used for \033[1;34mcenter\033[0m, \033[1;34mpA\033[0m, \033[1;34mpB\033[0m
\033[1;34mscale(center, sx, sy, sz)\033[0m
    Scale all points by factors (sx, sy, sz) about the center (default to center of mass).
\033[1;34mget_vtk_unstructured_grid()\033[0m
    Retrieve the underlying vtkUnstructuredGrid.
\033[1;34mmerge_duplicate_nodes(verbose=False, tol=1e-5)\033[0m
    Merge duplicate nodes in the surface mesh within the given tolerance.
\033[1;34mcopy()\033[0m
    Create a deep copy of the Surface instance.
\033[1;34mpid\033[0m
    Accessor and setter for the part ID (pid). The pid uniquely identifies the element
    as a mesh entity with its own characteristics (e.g., material, function).
    
Usage Example:
---------------
  surface = Surface(p1, p2, p3, p4, quad=True)
  surface.translate(1, 2, 3)
  surface.rotate('z', 45)
  print(surface)
"""
        return help_text 


class Raccord2D(Surface):
    def __init__(
        self,
        L1: Line,
        L2: Line,
        quad: bool = True,
        pid: int = None,
    ):
        """
        Build a 2D raccord (fillet) between two lines by delegating
        to Surface's two-line constructor.

        Parameters
        ----------
        L1, L2
            The two boundary Line objects (must have same nbEl).
        quad
            Whether to generate quadrilaterals.
        transfinite
            Whether to apply transfinite meshing.
        pid
            Part ID to pass through to the mesh entity.
        **kwargs
            Any other Surface kwargs (n, size, grading, progression).
        """
        actual_pid = pid if pid is not None else (L1.pid or L2.pid or 1)

        super().__init__(
            pid=actual_pid
        )

        n1 = nbEl(L1)
        n2 = nbEl(L2)
        if n1 > n2:
            L1, L2 = L2, L1

        self.L1 = L1
        self.L2 = L2
        self.quad = quad

        self._build()

        
    def _build(self):
        n1 = nbEl(self.L1)
        n2 = nbEl(self.L2)

        # Triangular mesh fallback
        if not self.quad:
            self._build_tri_mesh()

        # Compute ratio of point counts
        if n1 == 0 :
            self._build_tri_mesh()
        ratio_f = n2 / n1
        if ratio_f == 1:
            s = Surface(self.L1, self.L2, n=1, quad=True, transfinite = True)
            self._ugrid = s._ugrid
            self._generate_pid_field()
        elif not float(ratio_f).is_integer():
            self._build_tri_mesh()
        else:
            ratio = int(ratio_f)
            # Factor ratio = 2^n * 3^m
            n = 0
            m = 0
            tmp = ratio
            while tmp % 2 == 0:
                tmp //= 2
                n += 1
            while tmp % 3 == 0:
                tmp //= 3
                m += 1
            lines = self._prepare_mesh(n, m)
            self._build_quad_mesh(lines)
            
            if tmp != 1:
                self._build_tri_mesh()
        
            
    def _build_tri_mesh(self):
        # Step 1: ensure L1 and L2 run in opposite directions around the fillet
        if are_id_oriented(self.L1, self.L2):
            self.L2.reverse_orientation()

        # Step 2: build the two spoke lines between the endpoints
        mid1 = Line(
            self.L1.get_end_point(),
            self.L2.get_start_point(),
            n=1,
            pid=self.pid
        )
        mid2 = Line(
            self.L2.get_end_point(),
            self.L1.get_start_point(),
            n=1,
            pid=self.pid
        )

        # Step 3: generate the triangular surface in one go
        tri_surf = Surface(
            self.L1,
            mid1,
            self.L2,
            mid2,
            quad=False,
            pid=self.pid
        )

        # Step 4: copy its grid back onto self
        new_grid = vtk.vtkUnstructuredGrid()
        new_grid.DeepCopy(tri_surf._ugrid)
        self._ugrid = new_grid
        self._pid   = self.pid
        self._generate_pid_field()

    def _prepare_mesh(self, n, m):      
        l_ints  = [self.L2]
        if (n == 0 and m == 1) or (m == 0 and n==1):
            l_ints.append(self.L1)
        else :
            l_ints  = [self.L2]
            for i in range(0,n):
                if (nbEl(self.L2)/(2**(i+1))) > nbEl(self.L1):
                    l_ints.append(self._interpolate_line(self.L1, self.L2, pos=(i+1)/(n+m), n = 2**(i+1)))
            lref = l_ints[-1]
            for i in range(0,m):
                if (nbEl(lref)/(3**(i+1))) > nbEl(self.L1):
                    l_ints.append(self._interpolate_line(self.L1, lref, pos=(i+1)/(m), n = 3**(i+1)))
        
            l_ints.append(self.L1)
            
        return l_ints
        
    def _build_quad_mesh(self, lines):
        n_steps = len(lines)-1
        strips  = []
        for i in range(n_steps):
            L1 = lines[i]
            L2 = lines[i+1]
            if nbEl(L1)/nbEl(L2) == 2:
               strips .append(self._racc_quad_double(L1, L2))
            else :
               strips .append(self._racc_quad_triple(L1, L2))
               
        # --- Merge all strips into one grid ---
        append = vtk.vtkAppendFilter()
        for strip in strips:
            append.AddInputData(strip._ugrid)
        append.Update()
        merged = append.GetOutput()

        # --- Remove duplicate points ---
        cleaner = vtk.vtkStaticCleanUnstructuredGrid()
        cleaner.SetInputData(merged)
        cleaner.SetTolerance(_TOL)
        cleaner.RemoveUnusedPointsOn()
        cleaner.Update()
        cleaned = cleaner.GetOutput()
        

        # --- Assign to self and regenerate pid field ---
        self._ugrid = cleaned
        self._generate_pid_field()
        self.set_orientation()

        


    def _racc_quad_double(self,L1, L2):
        # 1) Ensure boundary lines are oppositely oriented
        if not are_id_oriented(L1, L2):
            L2.reverse_orientation()
            
        n1 = nbEl(L1)
        n2 = nbEl(L2)
        if n1 > n2:
            L1, L2 = L2, L1
    
        # 2) Generate the intermediate spine at double resolution
        l_int = self._interpolate_line(L1, L2)
    
        # 3) Override even-indexed interpolated points directly on l_int's VTK grid
        vtk_pts_int = l_int.get_vtk_unstructured_grid().GetPoints()
        pts1 = L1.get_points()
        n1 = nbPt(L1)
        for i in range(0, n1, 2):
            # override point at idx = i*2 in the interpolated line
            x, y, z = pts1[i]
            vtk_pts_int.SetPoint(i * 2, x, y, z)
        vtk_pts_int.Modified()
        l_int.get_vtk_unstructured_grid().Modified()
        # 4) Extract updated coordinates into NumPy
        pts1 = np.asarray(pts1)  # shape (n1,3)
        pts_int = np.asarray(l_int.get_points())  # shape (2*n1,3)
    
        # 5) Bulk insert all points: L1 then modified l_int
        all_pts = np.vstack((pts1, pts_int))
        vtk_pts = vtk.vtkPoints()
        vtk_pts.SetData(vtk.util.numpy_support.numpy_to_vtk(all_pts, deep=True))
    
        # 6) Compute quad connectivity exactly as original
        num_quads = n1 - 1
        idx = np.arange(num_quads)
        even = (idx % 2 == 0)
        id1 = idx
        id2 = idx + 1
        base_int = n1
        id3 = np.empty(num_quads, dtype=int)
        id4 = np.empty(num_quads, dtype=int)
        # even-case
        id3[even] = base_int + (idx[even] + 1) * 2
        id4[even] = base_int + idx[even] * 2 + 1
        # odd-case
        id3[~even] = base_int + idx[~even] * 2 + 1
        id4[~even] = base_int + idx[~even] * 2
        quads = np.stack([id1, id2, id3, id4], axis=1)
    
        # 7) Create VTK cell array
        cell_array = vtk.vtkCellArray()
        for quad_ids in quads:
            cell_array.InsertNextCell(4, quad_ids)
    
        # 8) Assemble first strip
        grid1 = vtk.vtkUnstructuredGrid()
        grid1.SetPoints(vtk_pts)
        grid1.SetCells(vtk.VTK_QUAD, cell_array)
    
        # 9) Build second strip via Surface
        grid2 = Surface(L2, l_int, n=1, quad=True)._ugrid
    
        # 10) Append strips and wrap
        append = vtk.vtkAppendFilter()
        append.AddInputData(grid1)
        append.AddInputData(grid2)
        append.Update()
        merged = append.GetOutput()
        final = Elem(pid=self.pid)
        final._ugrid = merged
        final._generate_pid_field()
        return final

    def _racc_quad_triple(self,L1, L2):
        # 1) Ensure boundary lines are oppositely oriented
        if not are_id_oriented(L1, L2):
            L2.reverse_orientation()
            
        n1 = nbEl(L1)
        n2 = nbEl(L2)
        if n1 > n2:
            L1, L2 = L2, L1
    
        # 2) Generate the intermediate spine at double resolution
        l_int = self._interpolate_line(L1, L2, n=1)
    
        # 3) Override even-indexed interpolated points directly on l_int's VTK grid
        vtk_pts_int = l_int.get_vtk_unstructured_grid().GetPoints()
        pts1 = L1.get_points()
        n1 = nbPt(L1)
        for i in range(0, n1, 1):
            # override point at idx = i*2 in the interpolated line
            x, y, z = pts1[i]
            vtk_pts_int.SetPoint(i * 3, x, y, z)
        vtk_pts_int.Modified()
        l_int.get_vtk_unstructured_grid().Modified()
        # 4) Extract updated coordinates into NumPy
        pts1 = np.asarray(pts1)  # shape (n1,3)
        pts_int = np.asarray(l_int.get_points())  # shape (2*n1,3)
    
        # 5) Bulk insert all points: L1 then modified l_int
        all_pts = np.vstack((pts1, pts_int))
        vtk_pts = vtk.vtkPoints()
        vtk_pts.SetData(vtk.util.numpy_support.numpy_to_vtk(all_pts, deep=True))
    
        # 6) Compute quad connectivity exactly as original
        num_quads = n1 - 1
        idx = np.arange(num_quads)
        # p1 and p2
        id1 = idx
        id2 = idx + 1
        # id3 and id4 use the same formula for all quads
        base_int = n1
        id3 = base_int + (idx + 1) * 3 - 1
        id4 = base_int + (idx + 1) * 3 - 2
        quads = np.stack([id1, id2, id3, id4], axis=1)
    
        # 7) Create VTK cell array
        cell_array = vtk.vtkCellArray()
        for quad_ids in quads:
            cell_array.InsertNextCell(4, quad_ids)
    
        # 8) Assemble first strip
        grid1 = vtk.vtkUnstructuredGrid()
        grid1.SetPoints(vtk_pts)
        grid1.SetCells(vtk.VTK_QUAD, cell_array)
    
        # 9) Build second strip via Surface
        grid2 = Surface(L2, l_int, n=1, quad=True)._ugrid
    
        # 10) Append strips and wrap
        append = vtk.vtkAppendFilter()
        append.AddInputData(grid1)
        append.AddInputData(grid2)
        append.Update()
        merged = append.GetOutput()
        final = Elem(pid=self.pid)
        final._ugrid = merged
        final._generate_pid_field()
        return final



    # def _build_quad_mesh_double(self, repeat = 0):
    #     if not are_id_oriented(self.L1, self.L2):
    #         self.L2.reverse_orientation()    
            
    #     l_int = self._interpolate_line(self.L1, self.L2, n=2)

    #     vtk_pts_int = l_int.get_vtk_unstructured_grid().GetPoints()
    #     pts1    = self.L1.get_points()
        
    #     n1 = nbPt(self.L1)
    #     for i in range(n1):
    #         if i % 2 == 0:
    #             x, y, z = pts1[i]
    #             idx = i*2 
    #             vtk_pts_int.SetPoint(idx, x, y, z)
        
    #     vtk_pts_int.Modified()
    #     l_int.get_vtk_unstructured_grid().Modified()
    #     pts_int = l_int.get_points()
        
    #     S_grid      = vtk.vtkUnstructuredGrid()
    #     vtk_pts    = vtk.vtkPoints()
    #     cell_array = vtk.vtkCellArray()
    #     pt_id_map = {}

    #     for i in range(n1-1):
    #         if i % 2 ==0:
    #             p1 = pts1[i]
    #             p2 = pts1[i+1]
    #             p3 = pts_int[(i+1)*2]
    #             p4 = pts_int[2*i+1]
    #         else:
    #             p1 = pts1[i]
    #             p2 = pts1[i+1]
    #             p3 = pts_int[2*i+1]
    #             p4 = pts_int[2*i]
                
    #         # get or create point-ids
    #         id1 = self._insert_point(p1, pt_id_map, vtk_pts)
    #         id2 = self._insert_point(p2, pt_id_map, vtk_pts)
    #         id3 = self._insert_point(p3, pt_id_map, vtk_pts)
    #         id4 = self._insert_point(p4, pt_id_map, vtk_pts)
        
    #         # build the vtkQuad
    #         quad = vtk.vtkQuad()
    #         quad.GetPointIds().SetId(0, id1)
    #         quad.GetPointIds().SetId(1, id2)
    #         quad.GetPointIds().SetId(2, id3)
    #         quad.GetPointIds().SetId(3, id4)
    #         cell_array.InsertNextCell(quad)        
                
        
    #     S_grid.SetPoints(vtk_pts)
    #     S_grid.SetCells(vtk.VTK_QUAD, cell_array)
        
    #     # 5) clean up duplicates (optional but recommended)
    #     clean = vtk.vtkStaticCleanUnstructuredGrid()
    #     clean.SetInputData(S_grid)
    #     clean.SetTolerance(_TOL)
    #     clean.RemoveUnusedPointsOn()
    #     clean.Update()
    #     S_clean = clean.GetOutput()
        
    #     # 6) wrap into an Elem so you get coloring/pid-fields, etc.
    #     S1 = Elem(pid=self.pid)
    #     S1._ugrid = S_clean
    #     S1._generate_pid_field()

    #     S2 = Surface(self.L2,l_int,n=1,quad=True)

    #     # --- 1) Append the two grids ---
    #     append_filter = vtk.vtkAppendFilter()
    #     append_filter.AddInputData(S1._ugrid)
    #     append_filter.AddInputData(S2._ugrid)
    #     append_filter.Update()
    #     appended = append_filter.GetOutput()
        
    #     # --- 2) Remove duplicate points ---
    #     clean_filter = vtk.vtkStaticCleanUnstructuredGrid()
    #     clean_filter.SetInputData(appended)
    #     clean_filter.SetTolerance(_TOL)             # adjust tolerance as needed
    #     clean_filter.RemoveUnusedPointsOn()         # merge coincident points
    #     clean_filter.Update()
    #     merged_grid = clean_filter.GetOutput()
        
    #     # --- 3) Wrap into a single Elem (so you get coloring / pid-field, etc.) ---
    #     self._ugrid = merged_grid
    #     self._pid   = self.pid
    #     self._generate_pid_field()

   
    def _insert_point(self, pt, pt_id_map, vtk_pts):
        key = tuple(np.round(pt, 8))  # hashable with tolerance
        if key in pt_id_map:
            return pt_id_map[key]
        pid = vtk_pts.InsertNextPoint(pt)
        pt_id_map[key] = pid
        return pid        
    
    # def _interpolate_line(self, l1, l2, pos = 0.5, n = 1):
    #     # compute mid-points
    #     mid_start = (pos * l1.get_start_point() + l2.get_start_point() * (1-pos))
    #     mid_end   = (pos * l1.get_end_point()  + l2.get_end_point()    * (1-pos))

    #     # turn back into Point objects
    #     P_start = Point(*mid_start)
    #     P_end   = Point(*mid_end)

    #     # figure out how many segments each line has:
    #     #   (number of elements = number of nodes - 1)
    #     n1 = len(l1.get_points()) - 1
    #     n2 = len(l2.get_points()) - 1

    #     # ditto for grading (if you ever change it on PolyLine youd need to stash it)
    #     g1 = getattr(l1, "grading", 1)
    #     g2 = getattr(l2, "grading", 1)

    #     # choose the max discretization
    #     n_max      = int(max(n1, n2) / n) 
    #     grading_max = max(g1, g2)
        

    #     # copy progression from l1 (or pick whichever you prefer)
    #     progression = getattr(l1, "progression", "linear")

    #     # now build l3
    #     return Line(
    #         P_start,
    #         P_end,
    #         n=n_max,
    #         grading=grading_max,
    #         progression=progression,
    #         pid= l1.pid      # or whatever pid you want
    #     )

    def _interpolate_line(self, l1, l2, pos=0.5, n=1):
        """
        Build an intermediate *curved* line between l1 and l2 by interpolating
        corresponding points along normalized arc length.
    
        Parameters
        ----------
        l1, l2 : Line (or PolyLine)
            Boundary lines; they should represent the same "direction" so that
            start maps to start and end maps to end. If not, we flip l2 temporarily.
        pos : float in [0,1]
            Blend factor: 1.0 -> exactly l1, 0.0 -> exactly l2.
        n : int
            Divider applied to the target element count. By default (n=1) we use
            max(nbEl(l1), nbEl(l2)) elements; for transitional spines we use
            e.g. n=2, 4, 8... or 3, 9... so indices line up with your ratio logic.
    
        Returns
        -------
        Line
            A Line whose internal VTK points are overwritten to follow the blended
            curve. The number of elements is exactly:
                target_e = max(nbEl(l1), nbEl(l2)) // n
        """
    
        # --- Helper: cumulative chord-length parameterization in [0,1]
        def _arc_param(P):
            P = np.asarray(P, dtype=float)
            if P.shape[0] < 2:
                s = np.zeros((P.shape[0],), dtype=float)
                return P, s
            d = np.linalg.norm(np.diff(P, axis=0), axis=1)
            cum = np.concatenate(([0.0], np.cumsum(d)))
            L = cum[-1]
            s = cum / L if L > 0 else cum
            return P, s
    
        # --- Helper: interpolate points on polyline at s query values in [0,1]
        def _interp_polyline(P, sP, s_query):
            P = np.asarray(P, dtype=float)
            sP = np.asarray(sP, dtype=float)
            s_query = np.asarray(s_query, dtype=float)
    
            # Handle degenerate "point" or zero-length segments
            if len(P) == 1 or (len(P) > 1 and np.allclose(P, P[0])):
                return np.repeat(P[:1], len(s_query), axis=0)
    
            # For each s, find segment i with sP[i] <= s < sP[i+1]
            # np.searchsorted returns index where it should be inserted to keep order.
            idx = np.searchsorted(sP, s_query, side="right") - 1
            idx = np.clip(idx, 0, len(P) - 2)
    
            s0 = sP[idx]
            s1 = sP[idx + 1]
            # Avoid division by zero on coincident nodes
            denom = np.where(np.abs(s1 - s0) < 1e-15, 1.0, s1 - s0)
            t = (s_query - s0) / denom
            Q = P[idx] * (1.0 - t[:, None]) + P[idx + 1] * t[:, None]
            # Force endpoints exact
            Q[0] = P[0]
            Q[-1] = P[-1]
            return Q
    
        # --- Ensure orientation compatibility (start->start, end->end)
        reversed_tmp = False
        try:
            if not are_id_oriented(l1, l2):
                l2.reverse_orientation()
                reversed_tmp = True
    
            # --- Determine target element count exactly as before
            n1 = len(l1.get_points()) - 1
            n2 = len(l2.get_points()) - 1
            target_e = max(n1, n2) // max(1, int(n))  # integer division by design
            target_e = max(1, int(target_e))          # at least one element
            target_nodes = target_e + 1
    
            # --- Build s-grid so indices line up with your ratio math (uniform in s)
            s_query = np.linspace(0.0, 1.0, target_nodes)
    
            # --- Sample both boundaries by arc-length
            P1_raw = np.asarray(l1.get_points(), dtype=float)
            P2_raw = np.asarray(l2.get_points(), dtype=float)
            P1, s1 = _arc_param(P1_raw)
            P2, s2 = _arc_param(P2_raw)
    
            S1 = _interp_polyline(P1, s1, s_query)
            S2 = _interp_polyline(P2, s2, s_query)
    
            # --- Blend the two sampled polylines pointwise
            S = pos * S1 + (1.0 - pos) * S2
    
            # --- Create a Line with the right number of elements, then overwrite points
            P_start = Point(*S[0])
            P_end   = Point(*S[-1])
            # Keep grading/progression, but they won't matter after overwrite
            g1 = getattr(l1, "grading", 1)
            g2 = getattr(l2, "grading", 1)
            grading_max = max(g1, g2)
            progression = getattr(l1, "progression", "linear")
    
            L = Line(
                P_start,
                P_end,
                n=target_e,
                grading=grading_max,
                progression=progression,
                pid=l1.pid
            )
    
            # Overwrite every node coordinate to follow the blended curve
            vtk_pts = L.get_vtk_unstructured_grid().GetPoints()
            for i, (x, y, z) in enumerate(S):
                vtk_pts.SetPoint(i, float(x), float(y), float(z))
            vtk_pts.Modified()
            L.get_vtk_unstructured_grid().Modified()
    
            return L
        finally:
            # Restore original l2 orientation if we flipped it
            if reversed_tmp:
                l2.reverse_orientation()
            