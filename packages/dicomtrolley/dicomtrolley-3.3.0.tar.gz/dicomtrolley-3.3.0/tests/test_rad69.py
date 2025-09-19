import re
from unittest.mock import Mock
from uuid import uuid4

import pytest
import requests
from jinja2 import Template
from requests.exceptions import ChunkedEncodingError
from urllib3.exceptions import ProtocolError

from dicomtrolley.core import InstanceReference
from dicomtrolley.exceptions import DICOMTrolleyError
from dicomtrolley.http import HTTPMultiPartStream, PartIterator
from dicomtrolley.parsing import DICOMParseTree
from dicomtrolley.rad69 import (
    Rad69,
    XDSMissingDocumentError,
)
from dicomtrolley.xml_templates import (
    A_RAD69_RESPONSE_SOAP_HEADER_TEMPLATE,
    RAD69_SOAP_REQUEST_TEMPLATE,
)
from tests.conftest import set_mock_response, set_mock_response_list
from tests.factories import InstanceReferenceFactory, quick_dataset
from tests.mock_responses import (
    MockResponseList,
    MockUrls,
    RAD69_RESPONSE_INVALID_DICOM,
    RAD69_RESPONSE_INVALID_NON_DICOM,
    RAD69_RESPONSE_INVALID_NON_MULTIPART,
    RAD69_RESPONSE_OBJECT_NOT_FOUND,
    create_rad69_response_from_dataset,
    create_rad69_response_from_datasets,
    quick_rad69_response,
)


@pytest.fixture
def a_rad69(a_session):
    """A basic rad69 module that you can query"""
    return Rad69(session=a_session, url=MockUrls.RAD69_URL)


def test_rad69_get_dataset(a_rad69, requests_mock):
    """Retrieve dicom data via a rad69 call"""
    set_mock_response(
        requests_mock,
        create_rad69_response_from_dataset(
            quick_dataset(PatientName="Jim", StudyDescription="Thing")
        ),
    )

    ds = a_rad69.get_dataset(
        InstanceReference(
            study_uid="1",
            series_uid="2",
            instance_uid="3",
        )
    )

    assert ds.PatientName == "Jim"
    assert ds.StudyDescription == "Thing"


@pytest.mark.parametrize(
    "mock_response, error_contains",
    [
        (RAD69_RESPONSE_INVALID_DICOM, ".*Error parsing response"),
        (RAD69_RESPONSE_INVALID_NON_DICOM, ".*Calling.* failed"),
        (
            RAD69_RESPONSE_INVALID_NON_MULTIPART,
            ".*Expected multipart response",
        ),
        (RAD69_RESPONSE_OBJECT_NOT_FOUND, ".*Server returns 2 errors"),
    ],
)
def test_rad69_error_from_server(
    a_rad69, requests_mock, mock_response, error_contains
):
    """Server can return strange invalid dicom-like responses, http error codes
    or errors as in a soap response. Catch these and raise meaningful errors
    """
    set_mock_response(requests_mock, mock_response)

    with pytest.raises(DICOMTrolleyError) as e:
        a_rad69.get_dataset(
            InstanceReference(
                study_uid="1",
                series_uid="2",
                instance_uid="3",
            )
        )
    assert re.match(error_contains, str(e))


@pytest.fixture
def mock_rad69_response(requests_mock):
    """Make sure that calling the rad69 test url returns a response"""
    response = create_rad69_response_from_datasets(
        [quick_dataset(PatientName="Patient_1")]
    )
    set_mock_response(requests_mock, response)
    return requests_mock


@pytest.mark.parametrize(
    "underlying_error",
    (
        ChunkedEncodingError("Remote host just closed the connection. Rude"),
        ProtocolError("Remote host was really bad"),
    ),
)
def test_requests_chunked_encoding_error_handling(
    a_rad69, mock_rad69_response, monkeypatch, underlying_error
):
    """Recreates #20 and #22 uncaught error from unexpected server connection
    closing
    """

    # Rig bytestream reading to fail
    def failing_iter(*args, **kwargs):
        """Creates an iterator that fails at the first __next__ call"""
        an_iter = Mock()
        an_iter.__iter__ = Mock(return_value=iter([]))
        an_iter.__next__ = Mock(side_effect=underlying_error)
        return an_iter

    monkeypatch.setattr(
        "dicomtrolley.http.SafeChunks",
        failing_iter,
    )

    with pytest.raises(DICOMTrolleyError) as e:
        _ = [
            x for x in a_rad69.datasets([InstanceReferenceFactory()])
        ]  # emtpy call suffices due to mocking
    assert e.value  # make sure error is not emtpy


@pytest.fixture
def some_studies():
    tree = DICOMParseTree()
    tree.insert(
        data=[],
        study_uid="study1",
        series_uid="series1",
        instance_uid="instance1",
    )
    tree.insert(
        data=[],
        study_uid="study1",
        series_uid="series1",
        instance_uid="instance2",
    )
    tree.insert(
        data=[],
        study_uid="study1",
        series_uid="series2",
        instance_uid="instance1",
    )
    return tree.as_studies()


def test_rad69_template(some_studies):
    """Verify that all fields in the main soap template are filled correctly"""

    rendered = Template(RAD69_SOAP_REQUEST_TEMPLATE).render(
        uuid="a_uuid",
        studies=some_studies,
        transfer_syntax_list=["1.2.840.10008.1.2", "1.2.840.10008.1.2.1"],
    )

    assert "study1" in rendered
    assert "series1" in rendered
    assert "series2" in rendered
    assert "instance1" in rendered
    assert "instance2" in rendered


@pytest.fixture
def some_instances():
    """Some instances that can be used in trolley search and download commands"""
    return [
        InstanceReference(
            study_uid="study1",
            series_uid="series1",
            instance_uid="s1_instance1",
        ),
        InstanceReference(
            study_uid="study1",
            series_uid="series1",
            instance_uid="s1_instance2",
        ),
        InstanceReference(
            study_uid="study1",
            series_uid="series2",
            instance_uid="s2_instance1",
        ),
    ]


def test_request_splitting(a_rad69, mock_rad69_response, some_instances):
    """Rad69 downloader can split requests per series to lighten server load"""
    results = a_rad69.datasets(some_instances)
    call_history = mock_rad69_response.request_history

    # results is an iterator that should only issue requests when needed
    # without having read any results, no calls should have been done
    assert len(call_history) == 0

    # When asking for results, call should be issued
    _ = next(results)
    assert len(call_history) == 1
    _ = next(results)
    assert len(call_history) == 2

    # Check that the actual instances called for are as expected
    call_1 = call_history[0].text
    call_2 = call_history[1].text
    assert "s1_instance1" in call_1
    assert "s1_instance2" in call_1
    assert "s2_instance1" not in call_1
    assert "s2_instance1" in call_2


def test_request_splitting_disabled(
    a_rad69, mock_rad69_response, some_instances
):
    """Check that turning off request splitting works as expected"""
    a_rad69.request_per_series = False
    _ = list(a_rad69.datasets(some_instances))
    assert len(mock_rad69_response.request_history) == 1
    assert "s1_instance1" in mock_rad69_response.request_history[0].text
    assert "s1_instance2" in mock_rad69_response.request_history[0].text
    assert "s2_instance1" in mock_rad69_response.request_history[0].text


def test_wado_datasets_async(a_rad69, requests_mock):
    set_mock_response(
        requests_mock,
        create_rad69_response_from_dataset(
            quick_dataset(PatientName="patient1", StudyDescription="a_study")
        ),
    )

    instances = [
        InstanceReference(study_uid="1", series_uid="2", instance_uid="3"),
        InstanceReference(study_uid="4", series_uid="5", instance_uid="6"),
    ]
    a_rad69.use_async = True
    datasets = [x for x in a_rad69.datasets(instances)]
    assert len(datasets) == 2
    assert datasets[0].PatientName == "patient1"
    assert (
        requests_mock.last_request.headers["Content-type"]
        == "application/soap+xml"
    )


def test_wado_datasets_streamed(a_rad69, requests_mock):
    """Handle streamed / chunked response"""
    datasets = [
        quick_dataset(PatientName=f"Patient_{idx}") for idx in range(3)
    ]
    response = create_rad69_response_from_datasets(datasets)
    set_mock_response(requests_mock, response)

    # check with empty call because mock response does not care
    datasets = [x for x in a_rad69.datasets([InstanceReferenceFactory()])]

    assert len(datasets) == 3


@pytest.fixture
def a_rad69_multipart_response(requests_mock):
    """A http multipart response from a rad69 server"""
    datasets = [
        quick_dataset(PatientName=f"Patient_{idx}") for idx in range(3)
    ]
    set_mock_response(
        requests_mock, create_rad69_response_from_datasets(datasets)
    )
    return requests.post(MockUrls.RAD69_URL)


def test_http_multi_part_stream(a_rad69_multipart_response):
    stream = HTTPMultiPartStream(a_rad69_multipart_response)
    parts = [part for part in stream]
    assert len(parts) == 4


@pytest.mark.parametrize("chunk_size", [1, 2, 16, 64, 1024, 271360])
def test_http_multi_part_stream_chunk_size(
    a_rad69_multipart_response, chunk_size
):
    """Different chunk sizes should not affect function"""
    stream = HTTPMultiPartStream(
        a_rad69_multipart_response, stream_chunk_size=chunk_size
    )
    parts = [part for part in stream]
    assert len(parts) == 4


@pytest.mark.parametrize(
    "boundary, byte_stream, parts",
    [
        (
            b"--a_boundary123",
            b"--a_boundary123\r\nsome content--a_boundary123andthensome",
            [b"\r\nsome content"],
        ),
        (b"--123", b"--123content--123content2", [b"content"]),
        (
            b"--123",
            b"--123contentbutnoendboundary",
            [],
        ),
        (b"--123", b"--123--123--123content--123", [b"content"]),
        (b"--123", b"nostart_but_end--123", [b"nostart_but_end"]),
    ],
)
def test_break_off_first_part(boundary, byte_stream, parts):
    """Test the function used to break a bytestream into parts"""
    iterator = PartIterator(
        bytes_iterator=(x for x in [byte_stream]), boundary=boundary
    )
    parts_found = [x for x in iterator]
    assert parts == parts_found


def test_huge_xml_part(requests_mock, a_rad69):
    """Do things work if the initial xml part to a response is much larger than
    chunk size? Just to be sure
    """

    big_header = Template(A_RAD69_RESPONSE_SOAP_HEADER_TEMPLATE).render(
        dids=list(uuid4() for i in range(7000))
    )
    set_mock_response(
        requests_mock,
        create_rad69_response_from_datasets(
            [quick_dataset(PatientName="Patient_1")], soap_header=big_header
        ),
    )

    sets = list(
        a_rad69.datasets(objects=[InstanceReferenceFactory()])
    )  # mock call does not care about which objects are passed
    assert len(sets) == 1


@pytest.fixture
def rad69_2nd_response_is_error(requests_mock):
    """Calling rad69 endpoint will yield response, error, response"""
    # Set up: calling rad69 endpoint will yield response, error, response
    resp1 = quick_rad69_response(PatientName="Jim")
    resp2 = RAD69_RESPONSE_OBJECT_NOT_FOUND
    resp3 = quick_rad69_response(PatientName="Jen")
    set_mock_response_list(
        requests_mock,
        MockResponseList(
            url=resp1.url, method=resp1.method, responses=[resp1, resp2, resp3]
        ),
    )


def test_xds_missing_document(rad69_2nd_response_is_error, a_rad69, caplog):
    """Recreates issue 32, errors that should be ignored"""
    a_rad69.errors_to_ignore = [XDSMissingDocumentError]
    # call rad69 with dummy 3 references to trigger 3 calls
    studies = list(
        a_rad69.datasets([InstanceReferenceFactory() for x in range(3)])
    )
    # response 2 caused an error, should have been ignored
    assert len(studies) == 2
    assert any(
        "Ignoring error" in x for x in caplog.messages
    )  # but warning issued


def test_xds_missing_document_default(rad69_2nd_response_is_error, a_rad69):
    """By default no errors are ignored. All are propagated"""
    some_instances = [InstanceReferenceFactory() for x in range(3)]
    with pytest.raises(XDSMissingDocumentError):
        list(a_rad69.datasets(some_instances))
