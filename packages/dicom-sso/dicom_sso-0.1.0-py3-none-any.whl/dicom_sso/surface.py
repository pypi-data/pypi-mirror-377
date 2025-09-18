from typing import Literal

import numpy as np
from highdicom.color import CIELabColor
from pydicom import Dataset


class Surface(Dataset):
    def __init__(
            self,
            points: np.ndarray,
            triangles: np.ndarray,
            normals: np.ndarray,
            *,
            surface_number: int,
            surface_comments: str,
            surface_processing: Literal['YES', 'NO'],
            recommended_display_cielab_value: CIELabColor,
            recommended_display_grayscale_value: int,
            recommended_display_opacity: float,
            recommended_display_presentation_type: Literal['SURFACE', 'WIREFRAME', 'POINTS'],
            finite_volume: Literal['YES', 'NO', 'UNKNOWN'],
            manifold: Literal['YES', 'NO', 'UNKNOWN']) -> None:
        super().__init__()
        surface_points = Dataset()
        surface_points.NumberOfSurfacePoints = points.shape[0]
        surface_points.PointCoordinatesData = points.tobytes()

        surface_points_normals = Dataset()
        surface_points_normals.NumberOfVectors = normals.shape[0]
        surface_points_normals.VectorDimensionality = normals.shape[1]
        surface_points_normals.VectorCoordinateData = normals.tobytes()

        primitives = Dataset()
        primitives.TriangleStripSequence = []
        primitives.TriangleFanSequence = []
        primitives.LineSequence = []
        primitives.FacetSequence = []
        primitives.LongTrianglePointIndexList = triangles.tobytes()
        primitives.LongEdgePointIndexList = None
        primitives.LongVertexPointIndexList = None

        self.SurfaceNumber = surface_number
        self.SurfaceComments = surface_comments
        self.SurfaceProcessing = surface_processing
        self.RecommendedDisplayGrayscaleValue = recommended_display_grayscale_value
        self.RecommendedDisplayCIELabValue = list(recommended_display_cielab_value.value)
        self.RecommendedPresentationOpacity = recommended_display_opacity
        self.RecommendedPresentationType = recommended_display_presentation_type
        self.FiniteVolume = finite_volume
        self.Manifold = manifold  # or UNKNOWN, NO
        self.SurfacePointsSequence = [surface_points]
        self.SurfacePointsNormalsSequence = [surface_points_normals]
        self.SurfaceMeshPrimitivesSequence = [primitives]
