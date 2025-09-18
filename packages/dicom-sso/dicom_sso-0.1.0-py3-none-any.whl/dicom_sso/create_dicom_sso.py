import datetime
import os
import warnings
from pathlib import Path

import highdicom as hd
import numpy as np
import vtk
from highdicom.color import CIELabColor
from highdicom.sr import CodedConcept
from pydicom.sr.codedict import codes

from vtkmodules.util import numpy_support
from vtkmodules.vtkCommonDataModel import vtkPolyData
from vtkmodules.vtkFiltersCore import vtkTriangleFilter

from dicom_sso.segment import Segment
from dicom_sso.surface import Surface
from dicom_sso.surface_segmentation import SurfaceSegmentation

warnings.filterwarnings('ignore', category=UserWarning)


def show_polydata(pd: vtk.vtkPolyData, filename: str | None) -> None:
    if filename is not None:
        writer = vtk.vtkPolyDataWriter()
        writer.SetInputData(pd)
        writer.SetFileTypeToASCII()
        writer.SetFileName(filename)
        writer.Write()

    ren = vtk.vtkRenderer()
    ren.SetBackground(0.3254, 0.3490, 0.3764)

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(pd)

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    ren.AddActor(actor)

    renwin = vtk.vtkRenderWindow()
    renwin.AddRenderer(ren)
    renwin.SetSize(1280, 800)

    # noinspection PyArgumentList
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())  # type: ignore
    iren.SetRenderWindow(renwin)
    iren.Initialize()
    iren.Start()


def sphere(center: tuple[float, float, float] = (0.0, 0.0, 0.0),
           radius: float = 0.5) -> vtkPolyData:
    source = vtk.vtkSphereSource()
    source.SetThetaResolution(32)
    source.SetPhiResolution(32)
    source.SetCenter(*center)
    source.SetRadius(radius)
    source.GetOutput()
    # noinspection PyArgumentList
    source.Update()

    return source.GetOutput()


def cube(
        center: tuple[float, float, float] = (0.0, 0.0, 0.0),
        size_x: float = 0.5,
        size_y: float = 0.5,
        size_z: float = 0.5) -> vtkPolyData:
    source = vtk.vtkCubeSource()
    source.SetXLength(size_x)
    source.SetYLength(size_y)
    source.SetZLength(size_z)
    source.SetCenter(*center)
    source.GetOutput()
    # noinspection PyArgumentList
    source.Update()

    return source.GetOutput()


def polydata_to_numpy(pd: vtkPolyData) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    def _get_triangles(_pd: vtkPolyData) -> np.ndarray:
        output = []

        polys = _pd.GetPolys()
        id_list = vtk.vtkIdList()
        polys.InitTraversal()
        while polys.GetNextCell(id_list):
            for i in range(id_list.GetNumberOfIds()):
                point_id = id_list.GetId(i)
                output.append(point_id + 1)  # DICOM uses 1-index notation

        return np.array(output, dtype=np.int32)

    triangle_filter = vtkTriangleFilter()
    triangle_filter.SetInputData(pd)
    triangle_filter.Update()
    triangle_pd = triangle_filter.GetOutput()

    points = numpy_support.vtk_to_numpy(triangle_pd.GetPoints().GetData()).astype(np.float32)
    triangles = _get_triangles(triangle_pd)
    normals = numpy_support.vtk_to_numpy(triangle_pd.GetPointData().GetNormals()).astype(np.float32)

    return points, triangles, normals


def main() -> None:
    image_files = Path(os.environ['INPUT_FOLDER']).glob('*')
    image_datasets = sorted([hd.imread(str(f)) for f in image_files], key=lambda f: f.InstanceNumber)

    positions = [x.ImagePositionPatient for x in image_datasets]
    center = positions[len(positions) // 2]
    center[0] += image_datasets[0].Rows * image_datasets[0].PixelSpacing[0] / 2.0
    center[1] += image_datasets[0].Columns * image_datasets[0].PixelSpacing[1] / 2.0

    content_date = datetime.datetime.now()  # noqa: DTZ005

    # Create the Segmentation instance
    surface = SurfaceSegmentation(
        source_images=image_datasets,
        series_instance_uid=hd.UID(),
        series_number=int(image_datasets[0].SeriesNumber) + 10100,
        sop_instance_uid=hd.UID(),
        instance_number=1,
        manufacturer='LKEB',
        manufacturer_model_name='Symphony AI',
        software_versions='v1',
        device_serial_number='Device XYZ',
        series_description='Symphony Example Segmentation',
        content_creator_name='pjhdekoning',
        content_description='Aorta Segmentation',
        content_label='LKEB_AORTA_SEG',
        content_date=content_date.date(),
        content_time=content_date.time(),
    )

    surface.SegmentSequence = [
        Segment(
            segmented_property_category=codes.cid7150.AnatomicalStructure,
            segmented_property_type=codes.cid7166.BloodVessel,
            segment_number=1,
            segment_label='sphere',
            segment_algorithm_type='AUTOMATIC',
            surface_count=1,
            algorithm_name='Deep learning',
            algorithm_version='1.0',
            algorithm_family_code=codes.cid7162.ArtificialIntelligence,
            referenced_surface_number=1
        ),
        Segment(
            segmented_property_category=codes.cid7150.AnatomicalStructure,
            segmented_property_type=codes.cid7166.BloodVessel,
            segment_number=1,
            segment_label='cube',
            segment_algorithm_type='AUTOMATIC',
            surface_count=1,
            algorithm_name='Deep learning',
            algorithm_version='1.0',
            algorithm_family_code=codes.cid7162.ArtificialIntelligence,
            referenced_surface_number=2
        ),
        Segment(
            segmented_property_category=codes.cid7150.AnatomicalStructure,
            segmented_property_type=codes.cid7166.BloodVessel,
            segment_number=1,
            segment_label='box',
            segment_algorithm_type='AUTOMATIC',
            surface_count=1,
            algorithm_name='Deep learning',
            algorithm_version='1.0',
            algorithm_family_code=codes.cid7162.ArtificialIntelligence,
            referenced_surface_number=3
        ),
    ]

    surface.SurfaceSequence = [
        Surface(
            *polydata_to_numpy(sphere(center=center, radius=24)),
            surface_number=1,
            surface_comments='sphere',
            surface_processing='NO',
            recommended_display_cielab_value=CIELabColor(l_star=53.24, a_star=80.09, b_star=67.2),
            recommended_display_grayscale_value=32768,
            recommended_display_opacity=0.75,
            recommended_display_presentation_type='SURFACE',
            manifold='YES',
            finite_volume='UNKNOWN'),
        Surface(
            *polydata_to_numpy(cube(center=center, size_x=32, size_y=32, size_z=32)),
            surface_number=1,
            surface_comments='cube',
            surface_processing='NO',
            recommended_display_cielab_value=CIELabColor(l_star=87.73, a_star=-86.18, b_star=83.18),
            recommended_display_grayscale_value=32768,
            recommended_display_opacity=0.75,
            recommended_display_presentation_type='SURFACE',
            manifold='YES',
            finite_volume='UNKNOWN'),
        Surface(
            *polydata_to_numpy(cube(center=center, size_x=16, size_y=32, size_z=64)),
            surface_number=1,
            surface_comments='box',
            surface_processing='NO',
            recommended_display_cielab_value=CIELabColor(l_star=23.3, a_star=79.19, b_star=-107.86),
            recommended_display_grayscale_value=32768,
            recommended_display_opacity=0.5,
            recommended_display_presentation_type='WIREFRAME',
            manifold='YES',
            finite_volume='UNKNOWN'),
    ]
    surface.NumberOfSurfaces = len(surface.SurfaceSequence)

    surface.save_as('sso.dcm')


if __name__ == '__main__':
    main()
