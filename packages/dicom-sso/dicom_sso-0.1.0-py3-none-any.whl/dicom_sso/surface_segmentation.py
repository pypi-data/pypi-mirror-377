import datetime
from collections import defaultdict
from typing import Any
from collections.abc import Sequence

from highdicom import ContentCreatorIdentificationCodeSequence, SOPClass
# noinspection PyProtectedMember
from highdicom._module_utils import ModuleUsageValues, get_module_usage
from pydicom import Dataset
from pydicom.uid import ExplicitVRLittleEndian, SurfaceSegmentationStorage, UID
from pydicom.valuerep import PersonName


# Segment Description Macro
#   https://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_C.8.20.4.html#table_C.8.20-4
# Surface Segmentation Module
#   https://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_C.8.23.html#sect_C.8.23.1
# Surface Mesh Module
#   https://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_C.27.html#sect_C.27.1
# Algorithm Identification Macro
#   https://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_10.16.html#table_10-19
class SurfaceSegmentation(SOPClass):
    def __init__(  # noqa: PLR0913
            self,
            source_images: Sequence[Dataset],
            *,
            series_instance_uid: str,
            series_number: int,
            sop_instance_uid: str,
            instance_number: int,
            manufacturer: str,
            manufacturer_model_name: str,
            software_versions: str | tuple[str],
            device_serial_number: str,
            content_date: datetime.date,
            content_time: datetime.time,
            transfer_syntax_uid: str | UID = ExplicitVRLittleEndian,
            content_description: str | None = None,
            content_creator_name: str | PersonName | None = None,
            content_label: str | None = None,
            content_creator_identification: None | ContentCreatorIdentificationCodeSequence = None,
            **kwargs: Any  # noqa: ANN401
    ) -> None:
        if len(source_images) == 0:
            raise ValueError('At least one source image is required.')

        src_img = source_images[0]

        sop_class_uid = SurfaceSegmentationStorage
        super().__init__(
            study_instance_uid=src_img.StudyInstanceUID,
            series_instance_uid=series_instance_uid,
            series_number=series_number,
            sop_instance_uid=sop_instance_uid,
            instance_number=instance_number,
            sop_class_uid=sop_class_uid,
            manufacturer=manufacturer,
            modality='SEG',
            transfer_syntax_uid=transfer_syntax_uid,
            patient_id=src_img.PatientID,
            patient_name=src_img.PatientName,
            patient_birth_date=src_img.PatientBirthDate,
            patient_sex=src_img.PatientSex,
            accession_number=src_img.AccessionNumber,
            study_id=src_img.StudyID,
            study_date=src_img.StudyDate,
            study_time=src_img.StudyTime,
            referring_physician_name=getattr(src_img, 'ReferringPhysicianName', None),
            manufacturer_model_name=manufacturer_model_name,
            device_serial_number=device_serial_number,
            software_versions=software_versions,
            **kwargs
        )
        # Frame of Reference
        has_ref_frame_uid = hasattr(src_img, 'FrameOfReferenceUID')
        if has_ref_frame_uid:
            self.FrameOfReferenceUID = src_img.FrameOfReferenceUID
            self.PositionReferenceIndicator = getattr(src_img, 'PositionReferenceIndicator', None)
        else:
            # Only allow missing FrameOfReferenceUID if it is not required for this IOD
            usage = get_module_usage('frame-of-reference', src_img.SOPClassUID)
            if usage == ModuleUsageValues.MANDATORY:
                raise ValueError("Source images have no Frame Of Reference UID, but it is required by the IOD.")

        # General Reference
        referenced_series: dict[str, list[Dataset]] = defaultdict(list)
        for s_img in source_images:
            ref = Dataset()
            ref.ReferencedSOPClassUID = s_img.SOPClassUID
            ref.ReferencedSOPInstanceUID = s_img.SOPInstanceUID
            referenced_series[s_img.SeriesInstanceUID].append(ref)

        ref_image_seq: list[Dataset] = []
        for uid, referenced_images in referenced_series.items():
            ref = Dataset()
            ref.SeriesInstanceUID = uid
            ref.ReferencedInstanceSequence = referenced_images
            ref_image_seq.append(ref)

        self.ReferencedSeriesSequence = ref_image_seq

        self.ContentDate = content_date
        self.ContentTime = content_time
        if content_label is not None:
            self.ContentLabel = content_label
        else:
            self.ContentLabel = f'{src_img.Modality}_SEG'
        self.ContentDescription = content_description
        self.ContentCreatorName = content_creator_name
        if content_creator_identification is not None:
            if not isinstance(
                    content_creator_identification,
                    ContentCreatorIdentificationCodeSequence
            ):
                raise TypeError(
                    'Argument "content_creator_identification" must be of type '
                    'ContentCreatorIdentificationCodeSequence.'
                )
            self.ContentCreatorIdentificationCodeSequence = content_creator_identification
