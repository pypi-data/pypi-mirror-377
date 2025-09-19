"""Models the MINT DICOM exchange protocol
See:
https://code.google.com/archive/p/medical-imaging-network-transport/downloads
"""
from typing import ClassVar, List, Sequence, Set
from xml.etree import ElementTree
from xml.etree.ElementTree import ParseError

from pydantic import model_validator
from pydicom.dataelem import DataElement
from pydicom.dataset import Dataset

from dicomtrolley.core import (
    DICOMObject,
    ExtendedQuery,
    Instance,
    Query,
    QueryLevels,
    Searcher,
    Series,
    Study,
)
from dicomtrolley.exceptions import DICOMTrolleyError
from dicomtrolley.fields import (
    InstanceLevel,
    SeriesLevel,
    SeriesLevelPromotable,
    StudyLevel,
)
from dicomtrolley.logs import get_module_logger

logger = get_module_logger("mint")


class MintQueryLevels:
    STUDY = "STUDY"
    SERIES = "SERIES"
    INSTANCE = "INSTANCE"

    ALL = {STUDY, SERIES, INSTANCE}

    @classmethod
    def translate(cls, value):
        """Translate from Query. For converting between queries

        Notes
        -----
        For MINT the query level values are identical to the generic query levels.
        Defining translation here anyway to be able to change generic values without
        side effects
        """
        translation = {
            QueryLevels.STUDY: cls.STUDY,
            QueryLevels.SERIES: cls.SERIES,
            QueryLevels.INSTANCE: cls.INSTANCE,
        }
        return translation[value]


class MintObject(DICOMObject):
    """Python representation of MINT xml"""

    xml_element: ClassVar[str]

    def all_instances(self):
        """
        Returns
        -------
        List[MintInstance]
            All instances contained in this object
        """
        raise NotImplementedError()


class MintInstance(Instance, MintObject):
    xml_element: ClassVar = "{http://medical.nema.org/mint}instance"
    parent: "MintSeries"

    @classmethod
    def init_from_element(cls, element, parent):
        data = parse_attribs(element)

        return cls(data=data, uid=data.SOPInstanceUID, parent=parent)


class MintSeries(Series, MintObject):
    xml_element: ClassVar = "{http://medical.nema.org/mint}series"
    instances: List[MintInstance]
    parent: "MintStudy"

    @classmethod
    def init_from_element(cls, element, parent):
        data = parse_attribs(element)

        series = cls(
            data=data,
            uid=data.SeriesInstanceUID,
            parent=parent,
            instances=[],
        )
        for x in element.findall(MintInstance.xml_element):
            series.instances.append(
                MintInstance.init_from_element(x, parent=series)
            )

        return series


class MintStudy(Study, MintObject):
    xml_element: ClassVar = "{http://medical.nema.org/mint}study"

    mint_uuid: str  # non-DICOM MINT-only id for this series
    last_modified: str
    series: List[MintSeries]

    @classmethod
    def init_from_element(cls, element):
        data = parse_attribs(element)

        study = cls(
            data=data,
            uid=data.StudyInstanceUID,
            mint_uuid=element.attrib["studyUUID"],
            last_modified=element.attrib["lastModified"],
            series=[],
        )
        for x in element.findall(MintSeries.xml_element):
            study.series.append(MintSeries.init_from_element(x, parent=study))

        return study

    def dump_content(self) -> str:
        """Dump entire contents of this study and containing series, instances

        For quick inspection in scripts
        """

        output = [str(self.data)]
        for series in self.series:
            output.append(str(series.data))
            for instance in series.instances:
                output.append(str(instance.data))
        return "\n".join(output)


class MintAttribute:
    """A DICOM element like PatientID=001"""

    xml_element = "{http://medical.nema.org/mint}attr"


class MintQuery(ExtendedQuery):
    """Things you can search for with the MINT find DICOM studies function

    Notes
    -----
    * All string arguments support (*) as a wildcard
    """

    limit: int = 0  # how many results to return. 0 = all

    @model_validator(mode="after")
    def min_max_study_date_xor(cls, values):  # noqa: B902, N805
        """Min and max should both be given or both be empty"""
        min_date = values.min_study_date
        max_date = values.max_study_date
        if min_date and not max_date:
            raise ValueError(
                f"min_study_date parameter was passed"
                f"({min_date}), "
                f"but max_study_date was not. Both need to be given"
            )
        elif max_date and not min_date:
            raise ValueError(
                f"max_study_date parameter was passed ({max_date}), "
                f"but min_study_date was not. Both need to be given"
            )
        return values

    @model_validator(mode="after")
    def include_fields_check(self):
        """Include fields should match query level"""
        if isinstance(self, list):
            # Interplay with base Query field_validator for include fields
            return self  # don't check
        else:
            include_fields = self.include_fields
        if not include_fields:
            return self  # May not exist if include_fields is invalid type

        query_level = self.query_level
        if query_level:  # May be None for child classes
            valid_fields = get_valid_fields(query_level=query_level)
            for field in include_fields:
                if field not in valid_fields:
                    raise ValueError(
                        f'"{field}" is not a valid include field for query '
                        f"level {query_level}. Valid fields: {valid_fields}"
                    )
        return self

    def __str__(self):
        return str(self.as_parameters())

    def as_parameters(self):
        """All non-empty query parameters. For use as url parameters"""
        parameters = {x: y for x, y in self.dict().items() if y}

        if "min_study_date" in parameters:
            parameters["min_study_date"] = parameters[
                "min_study_date"
            ].strftime("%Y%m%d")

        if "max_study_date" in parameters:
            parameters["max_study_date"] = parameters[
                "max_study_date"
            ].strftime("%Y%m%d")

        if "PatientBirthDate" in parameters:
            parameters["PatientBirthDate"] = parameters[
                "PatientBirthDate"
            ].strftime("%Y%m%d")

        if "query_level" in parameters:
            parameters["QueryLevel"] = MintQueryLevels.translate(
                parameters.pop("query_level")
            )

        if "include_fields" in parameters:
            parameters["IncludeFields"] = ",".join(
                parameters.pop("include_fields")
            )

        return parameters


def get_valid_fields(query_level) -> Set[str]:
    """All fields that can be returned at the given MINT query level"""
    if query_level == MintQueryLevels.INSTANCE:
        return (
            StudyLevel.fields
            | SeriesLevel.fields
            | SeriesLevelPromotable.fields
            | InstanceLevel.fields
        )
    elif query_level == MintQueryLevels.SERIES:
        return (
            StudyLevel.fields
            | SeriesLevel.fields
            | SeriesLevelPromotable.fields
        )
    elif query_level == MintQueryLevels.STUDY:
        return StudyLevel.fields
    else:
        raise ValueError(
            f'Unknown query level "{query_level}". Valid values '
            f"are {MintQueryLevels.ALL}"
        )


class Mint(Searcher):
    """A connection to a mint server"""

    def __init__(self, session, url):
        """
        Parameters
        ----------
        session: requests.session
            A logged-in session over which MINT calls can be made
        url: str
            MINT endpoint, including protocol and port. Like https://server:8080/mint
        """

        self.session = session
        self.url = url

    def find_studies(self, query: Query) -> Sequence[MintStudy]:
        """Get all studies matching query

        Parameters
        ----------
        query: Query
            Search based on these parameters. See Query object

        Returns
        -------
        List[MintStudy]
            All studies matching query. Might be empty.
            If Query.QueryLevel is SERIES or INSTANCE, MintStudy objects might
            contain MintSeries and MintInstance instances.
        """

        logger.info(f"Running query {query.to_short_string()}")
        search_url = self.url + "/studies"
        response = self.session.get(
            search_url, params=MintQuery.init_from_query(query).as_parameters()
        )
        return parse_mint_studies_response(response)


def parse_mint_studies_response(response) -> List[MintStudy]:
    """Parse the xml response to a MINT find DICOM studies call

    Raises
    ------
    DICOMTrolleyError
        If parsing fails
    """
    xml_raw = response.text
    try:
        studies = ElementTree.fromstring(xml_raw).findall(
            MintStudy.xml_element
        )
    except ParseError as e:
        raise DICOMTrolleyError(
            f"Could not parse server response from {response.url} "
            f"({response.status_code}:{response.reason}) as MINT "
            f"studies. Response text was: {xml_raw}"
        ) from e
    logger.info(f"parsed {len(studies)} studies from mint response")
    return [MintStudy.init_from_element(x) for x in studies]


def parse_attribs(element):
    """Parse xml attributes from a MINT find call to DICOM elements in a Dataset"""
    dataset = Dataset()
    for child in element.findall(MintAttribute.xml_element):
        attr = child.attrib
        val = attr.get("val", "")  # treat missing val as empty
        dataset[attr["tag"]] = DataElement(attr["tag"], attr["vr"], val)

    return dataset


MintInstance.update_forward_refs()  # enables pydantic validation
MintSeries.update_forward_refs()
MintStudy.update_forward_refs()
