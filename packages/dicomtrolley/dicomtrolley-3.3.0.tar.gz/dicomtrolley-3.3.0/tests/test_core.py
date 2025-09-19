from datetime import date, datetime

import pytest
from pydicom.dataset import Dataset

from dicomtrolley.core import (
    DICOMObjectLevels,
    ExtendedQuery,
    Instance,
    InstanceReference,
    NonInstanceParameterError,
    NonSeriesParameterError,
    Query,
    Series,
    SeriesReference,
    Study,
    StudyReference,
    to_instance_refs,
    to_series_level_refs,
)
from dicomtrolley.exceptions import NoReferencesFoundError
from dicomtrolley.mint import MintQuery
from tests.factories import (
    InstanceReferenceFactory,
    SeriesReferenceFactory,
    StudyReferenceFactory,
    quick_image_level_study,
)


@pytest.fixture
def a_study():
    study = Study(uid="stu1", data=Dataset(), series=[])
    series = Series(uid="ser2", data=Dataset(), parent=study, instances=[])
    instance1 = Instance(uid="ins3", data=Dataset(), parent=series)
    instance2 = Instance(uid="ins4", data=Dataset(), parent=series)
    study.series = (series,)
    series.instances = (instance1, instance2)
    return study


def test_object_get(a_study):
    study = a_study
    series = a_study["ser2"]
    instance = a_study["ser2"]["ins3"]

    str(study.reference())
    str(series.reference())
    str(instance.reference())

    assert len(study.all_instances()) == 2
    assert len(series.all_instances()) == 2
    assert len(instance.all_instances()) == 1

    assert str(study) == "Study stu1"
    assert str(series) == "Series ser2"
    assert str(instance) == "Instance ins3"

    assert instance.root().uid == study.uid
    assert series.root().uid == study.uid
    assert study.root().uid == study.uid


def test_object_exceptions(a_study):

    with pytest.raises(KeyError):
        _ = a_study["unknown"]

    with pytest.raises(KeyError):
        _ = a_study["ser2"]["unknown"]


def test_query():
    """Make sure all parameters of a query are checked"""

    dicom_parameters = {
        "AccessionNumber": "123",
        "InstitutionName": "Hospital",
        "InstitutionalDepartmentName": "Department",
        "ModalitiesInStudy": "MR*",
        "PatientID": "1234",
        "PatientName": "Patient*",
        "PatientSex": "F",
        "StudyDescription": "A study",
        "StudyInstanceUID": "4567",
    }
    meta_parameters = {
        "query_level": "INSTANCE",
        "PatientBirthDate": date(year=1990, month=1, day=1),
        "min_study_date": datetime(year=2020, month=3, day=1),
        "max_study_date": datetime(year=2020, month=3, day=5),
        "include_fields": ["NumberOfStudyRelatedInstances"],
    }

    all_parameters = {**dicom_parameters, **meta_parameters}
    # this should just not raise any validation error
    ExtendedQuery(**all_parameters)


def test_query_to_string(an_extended_query):
    """Test printing query as human-readable"""
    query = Query(PatientName="TestPatient")
    short_string = query.to_short_string()
    assert (
        "ModalitiesInStudy" not in short_string
    )  # empty values should be omitted
    assert (
        "'query_level': 'STUDY'" in short_string
    )  # query level should be string
    assert "TestPatient" in short_string

    # class name should reflect child class
    assert (
        "MintQuery" in MintQuery(AccessionNumber="a_number").to_short_string()
    )


@pytest.mark.parametrize(
    "query_params",
    (
        {
            "query_level": "Unknown_level",
        },
        {"include_fields": ["NotADicomKeyword"]},
    ),
)
def test_query_validation_error(query_params):
    """These queries should fail validation"""
    with pytest.raises(ValueError):
        Query(**query_params)


def test_extract_instances():
    """These extractions should work"""
    assert len(to_instance_refs([InstanceReferenceFactory()])) == 1
    a_study = quick_image_level_study("123")
    assert len(to_instance_refs([a_study])) == 18


def test_to_instance_refs_exceptions(a_study_level_study):
    """These extractions should not work"""
    # cannot use parametrize as I also want to use fixtures
    with pytest.raises(NonInstanceParameterError):
        # A study reference never contains instances
        to_instance_refs([StudyReference(study_uid="123")])

    with pytest.raises(NonInstanceParameterError):
        # Should raise on any part of input
        to_instance_refs(
            [InstanceReferenceFactory(), StudyReference(study_uid="123")]
        )

    with pytest.raises(NonInstanceParameterError):
        # A DICOMObject that does not contain full-depth information
        to_instance_refs(a_study_level_study)


def test_to_series_level_refs(a_study_level_study):
    """Test extracting series level references from DICOMObjects

    Notes
    -----
    Cannot use parametrize as I want to use factory boy objects which should be
    initialised during this test function execution and not (like parameterize)
    at module loading.
    """

    with pytest.raises(NonSeriesParameterError):
        # A study reference does not contain series level info
        to_series_level_refs([StudyReferenceFactory()])

    with pytest.raises(NonSeriesParameterError):
        # A study reference does not contain series level info
        to_series_level_refs(
            [SeriesReferenceFactory(), StudyReferenceFactory()]
        )

    with pytest.raises(NonSeriesParameterError):
        # A study reference does not contain series level info
        to_series_level_refs(a_study_level_study)

    # this should just work
    to_series_level_refs(
        [SeriesReferenceFactory(), InstanceReferenceFactory()]
    )


def test_contained_references_for_references():
    """DICOM object references can only return themselves, or error"""

    instance_ref: InstanceReference = InstanceReferenceFactory()
    # an instance reference is the deepest level, so this can always return itself
    for level in DICOMObjectLevels:
        assert (
            instance_ref.contained_references(max_level=level)[0]
            == instance_ref
        )

    series_ref: SeriesReference = SeriesReferenceFactory()
    # a series reference can return itself at series or study level
    for level in (DICOMObjectLevels.STUDY, DICOMObjectLevels.SERIES):
        assert (
            series_ref.contained_references(max_level=level)[0] == series_ref
        )

    # but can't return instance level. There is not info for that
    with pytest.raises(NoReferencesFoundError):
        series_ref.contained_references(max_level=DICOMObjectLevels.INSTANCE)

    # study ref can only return at study level
    study_ref: StudyReference = StudyReferenceFactory()
    assert (
        study_ref.contained_references(max_level=DICOMObjectLevels.STUDY)[0]
        == study_ref
    )

    for level in (DICOMObjectLevels.INSTANCE, DICOMObjectLevels.SERIES):
        with pytest.raises(NoReferencesFoundError):
            study_ref.contained_references(max_level=level)


def test_contained_references_for_dicom_objects(some_studies):
    """DICOM objects can contain additional dicom levels"""
    image_level_study, study_level_study = some_studies

    # If images (instances) are in there, this should be OK:
    assert (
        len(
            image_level_study.contained_references(
                max_level=DICOMObjectLevels.INSTANCE
            )
        )
        == 18
    )
    assert (
        len(
            image_level_study.contained_references(
                max_level=DICOMObjectLevels.SERIES
            )
        )
        == 2
    )
    assert (
        len(
            image_level_study.contained_references(
                max_level=DICOMObjectLevels.STUDY
            )
        )
        == 1
    )

    # But if there is no image info, trying to go deeper will fail
    for level in (DICOMObjectLevels.INSTANCE, DICOMObjectLevels.SERIES):
        with pytest.raises(NoReferencesFoundError):
            study_level_study.contained_references(max_level=level)

    # staying at the same level is OK though
    assert study_level_study.contained_references(
        max_level=DICOMObjectLevels.STUDY
    )

    # Anything is OK for an instance, as it is the deepest level
    an_instance = image_level_study.series[0].instances[0]
    for level in DICOMObjectLevels:
        assert an_instance.contained_references(max_level=level)

    # Just topping off with series. as we're on such a nice testing spree here
    a_series = image_level_study.series[0]
    a_series.instances = []  # without instances
    for level in (DICOMObjectLevels.SERIES, DICOMObjectLevels.STUDY):
        assert a_series.contained_references(max_level=level)
    with pytest.raises(NoReferencesFoundError):
        a_series.contained_references(max_level=DICOMObjectLevels.INSTANCE)
