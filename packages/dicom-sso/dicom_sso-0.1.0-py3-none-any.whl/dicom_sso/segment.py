from highdicom.seg import SegmentAlgorithmTypeValues
from highdicom.sr import CodedConcept
from pydicom import Dataset
from pydicom.sr import Code


class Segment(Dataset):
    def __init__(
            self,
            *,
            segmented_property_category: Code | CodedConcept,
            segmented_property_type: Code | CodedConcept,
            segment_number: int,
            segment_label: str,
            segment_algorithm_type: SegmentAlgorithmTypeValues | str,
            surface_count: int,
            algorithm_version: str,
            algorithm_name: str,
            algorithm_family_code: Code | CodedConcept,
            referenced_surface_number: int) -> None:
        super().__init__()

        alg_id_seq = Dataset()
        alg_id_seq.AlgorithmFamilyCodeSequence = [CodedConcept.from_code(algorithm_family_code)]
        alg_id_seq.AlgorithmVersion = algorithm_version
        alg_id_seq.AlgorithmName = algorithm_name

        referenced_surface_seq = Dataset()
        referenced_surface_seq.SegmentSurfaceGenerationAlgorithmIdentificationSequence = [alg_id_seq]
        referenced_surface_seq.ReferencedSurfaceNumber = referenced_surface_number
        referenced_surface_seq.SegmentSurfaceSourceInstanceSequence = []

        self.SegmentNumber = segment_number
        self.SegmentLabel = segment_label
        self.SegmentAlgorithmType = segment_algorithm_type
        self.SegmentedPropertyCategoryCodeSequence = [CodedConcept.from_code(segmented_property_category)]
        self.SegmentedPropertyTypeCodeSequence = [CodedConcept.from_code(segmented_property_type)]
        self.SurfaceCount = surface_count
        self.ReferencedSurfaceSequence = [referenced_surface_seq]
