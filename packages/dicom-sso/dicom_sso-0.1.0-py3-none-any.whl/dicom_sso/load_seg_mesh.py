""" https://gist.github.com/issakomi/29e48917e77201f2b73bfa5fe7b30451 """
import sys
from pathlib import Path
from struct import unpack

import pydicom
import vtk
from vtkmodules.vtkCommonCore import vtkFloatArray, vtkPoints
from vtkmodules.vtkCommonDataModel import vtkCellArray


# CIELab to RGB
# https://getreuer.info/posts/colorspace/
def lab_inverse(x: float) -> float:
    return x * x * x if x >= 0.20689655172413793 else 108.0 / 841.0 * (x - 4.0 / 29.0)  # noqa: PLR2004


def gamma_correction(x: float) -> float:  # noqa: PLR2004
    return 12.92 * x if x <= 0.0031306684425005883 else 1.055 * pow(x, 0.4166666666666667) - 0.055  # noqa: PLR2004


# D65 white point
def cielab2rgb(l: float, a: float, b: float) -> tuple[float, float, float]:  # noqa: E741
    l_tmp = (l + 16.0) / 116.0

    x = 0.950456 * lab_inverse(l_tmp + a / 500.0)
    y = 1.000000 * lab_inverse(l_tmp)
    z = 1.088754 * lab_inverse(l_tmp - b / 200.0)

    r_tmp = 3.2406 * x - 1.5372 * y - 0.4986 * z
    g_tmp = -0.9689 * x + 1.8758 * y + 0.0415 * z
    b_tmp = 0.0557 * x - 0.2040 * y + 1.0570 * z

    m = min(r_tmp, b_tmp) if r_tmp <= g_tmp else min(g_tmp, b_tmp)

    if m < 0:
        r_tmp -= m
        g_tmp -= m
        b_tmp -= m
    r = gamma_correction(r_tmp)
    g = gamma_correction(g_tmp)
    b = gamma_correction(b_tmp)

    return r, g, b


def bytes2int(data: bytes, *, big_endian: bool = False) -> int:
    ba = bytearray(data)
    if big_endian:
        ba = reversed(ba)
    x = 0
    for offset, byte in enumerate(ba):
        x += byte << (offset * 8)
    return x


def load_seg_mesh(dataset: pydicom.Dataset) -> None:
    ren = vtk.vtkRenderer()
    ren.SetBackground(0.3254, 0.3490, 0.3764)

    count_surfaces = len(dataset.SurfaceSequence)
    count_points = 0
    count_polys = 0
    for s in dataset.SurfaceSequence:
        points = _read_points(s)
        polys = _read_triangles(s)
        normals = _read_normals(s)

        count_points += points.GetNumberOfPoints()
        count_polys += polys.GetNumberOfCells()

        poly_data = vtk.vtkPolyData()
        poly_data.SetPoints(points)
        poly_data.SetPolys(polys)
        poly_data.GetPointData().SetNormals(normals)

        # writer = vtk.vtkPolyDataWriter()
        # writer.SetInputData(poly_data)
        # writer.SetFileTypeToASCII()
        # writer.SetFileName(f'{s.SurfaceComments}_dicom.vtk')
        # writer.Write()

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(poly_data)

        # gen_normals = vtk.vtkPolyDataNormals()
        # gen_normals.SetInputData(poly_data)
        # gen_normals.ComputePointNormalsOn()
        # gen_normals.ComputeCellNormalsOff()
        # # noinspection PyArgumentList
        # gen_normals.Update()
        # mapper.SetInputData(gen_normals.GetOutput())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(*get_rgb_color(s))
        actor.GetProperty().SetOpacity(s.RecommendedPresentationOpacity)
        match s.RecommendedPresentationType:
            case 'SURFACE':
                actor.GetProperty().SetRepresentationToSurface()
            case 'WIREFRAME':
                actor.GetProperty().SetRepresentationToWireframe()
            case 'POINTS':
                actor.GetProperty().SetRepresentationToPoints()

        ren.AddActor(actor)

    message = str(count_surfaces) + (" surface, " if count_surfaces == 1 else " surfaces, ")
    message += str(count_points) + (" point, " if count_points == 1 else " points, ")
    message += str(count_polys) + (" triangle" if count_polys == 1 else " triangles")

    text = vtk.vtkTextActor()
    text.GetTextProperty().SetFontSize(16)
    text.GetTextProperty().SetColor(1.0, 1.0, 1.0)
    text.SetInput(message)
    text.SetPosition(4, 4)

    ren.AddViewProp(text)

    renwin = vtk.vtkRenderWindow()
    renwin.AddRenderer(ren)
    renwin.SetSize(1280, 800)

    # noinspection PyArgumentList
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())  # type: ignore
    iren.SetRenderWindow(renwin)
    iren.Initialize()
    iren.Start()


def get_rgb_color(s: pydicom.Dataset) -> tuple[float, float, float]:
    cielab = s.RecommendedDisplayCIELabValue
    l = (cielab[0] / 65535.0) * 100.0  # noqa: E741
    a = ((cielab[1] - 32896.0) / 65535.0) * 255.0
    b = ((cielab[2] - 32896.0) / 65535.0) * 255.0
    return cielab2rgb(l, a, b)


def _read_triangles(s: pydicom.Dataset) -> vtkCellArray:
    t_index = s.SurfaceMeshPrimitivesSequence[0].LongTrianglePointIndexList

    polys = vtk.vtkCellArray()  # type: ignore
    z = 0
    while z < len(t_index):
        # 12 bytes to 3 dwords
        polys.InsertNextCell(3)
        idx_1 = bytes2int(t_index[z: z + 3]) - 1
        idx_2 = bytes2int(t_index[z + 4: z + 7]) - 1
        idx_3 = bytes2int(t_index[z + 8: z + 11]) - 1
        polys.InsertCellPoint(idx_1)
        polys.InsertCellPoint(idx_2)
        polys.InsertCellPoint(idx_3)
        z += 12
    return polys


def _read_normals(s: pydicom.Dataset) -> vtkFloatArray:
    sequence = s.SurfacePointsNormalsSequence[0]
    num_normals = sequence.NumberOfVectors
    dimensionality = sequence.VectorDimensionality
    vectors = sequence.VectorCoordinateData
    coordinates = unpack(f"<{int(len(vectors) / 4)}f", vectors)

    normals = vtk.vtkFloatArray()
    normals.SetNumberOfComponents(dimensionality)
    for v_index in range(num_normals):
        vector = coordinates[v_index * 3: v_index * 3 + 3]
        normals.InsertNextTypedTuple(tuple(vector))

    return normals


def _read_points(s: pydicom.Dataset) -> vtkPoints:
    point_coordinates = s.SurfacePointsSequence[0].PointCoordinatesData
    coordinates = unpack(f"<{int(len(point_coordinates) / 4)}f", point_coordinates)
    points = vtk.vtkPoints()
    num_points = len(coordinates) // 3
    for p_index in range(num_points):
        point = coordinates[p_index * 3: p_index * 3 + 3]
        points.InsertNextPoint(point)
    return points


if __name__ == "__main__":
    load_seg_mesh(pydicom.dcmread(Path.resolve(Path(sys.argv[1]))))
