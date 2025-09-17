from enum import StrEnum
from typing import List, Optional, Sequence


class ServiceType(StrEnum):
    BACKEND = "backend"
    FRONTEND = "frontend"


OptionalServiceType = Optional[ServiceType]
ListOfServiceTypes = List[ServiceType]
OptionalListOfServiceTypes = Optional[ListOfServiceTypes]
SequenceOfServiceTypes = Sequence[ServiceType]
OptionalSequenceOfServiceTypes = Optional[SequenceOfServiceTypes]


class Category(StrEnum):
    CORE = "core"
    AI = "ai"


OptionalCategory = Optional[Category]
ListOfCategories = List[Category]
OptionalListOfCategories = Optional[ListOfCategories]
SequenceOfCategories = Sequence[Category]
OptionalSequenceOfCategories = Optional[SequenceOfCategories]


class SimpleKey(StrEnum):
    STUDIO = "studio"
    NEXUS = "nexus"
    TELEMETRY = "telemetry"
    METADATA = "metadata"
    IDENTITY = "identity"
    ACCESS = "access"
    WORKSHOP = "workshop"
    RESEARCH = "research"
    SOAPIE = "soapie"
    MEDIX = "medix"
    DICOM = "dicom"
    SCRIBE = "scribe"
    CDS = "cds"
    IMAGING = "imaging"
    MCU = "mcu"


OptionalSimpleKey = Optional[SimpleKey]
ListOfSimpleKeys = List[SimpleKey]
OptionalListOfSimpleKeys = Optional[ListOfSimpleKeys]
SequenceOfSimpleKeys = Sequence[SimpleKey]
OptionalSequenceOfSimpleKeys = Optional[SequenceOfSimpleKeys]


class Key(StrEnum):
    STUDIO = "maleo-studio"
    NEXUS = "maleo-nexus"
    TELEMETRY = "maleo-telemetry"
    METADATA = "maleo-metadata"
    IDENTITY = "maleo-identity"
    ACCESS = "maleo-access"
    WORKSHOP = "maleo-workshop"
    RESEARCH = "maleo-research"
    SOAPIE = "maleo-soapie"
    MEDIX = "maleo-medix"
    DICOM = "maleo-dicom"
    SCRIBE = "maleo-scribe"
    CDS = "maleo-cds"
    IMAGING = "maleo-imaging"
    MCU = "maleo-mcu"


OptionalKey = Optional[Key]
ListOfKeys = List[Key]
OptionalListOfKeys = Optional[ListOfKeys]
SequenceOfKeys = Sequence[Key]
OptionalSequenceOfKeys = Optional[SequenceOfKeys]


class SimpleName(StrEnum):
    STUDIO = "Studio"
    NEXUS = "Nexus"
    TELEMETRY = "Telemetry"
    METADATA = "Metadata"
    IDENTITY = "Identity"
    ACCESS = "Access"
    WORKSHOP = "Workshop"
    RESEARCH = "Research"
    SOAPIE = "SOAPIE"
    MEDIX = "Medix"
    DICOM = "DICON"
    SCRIBE = "Scribe"
    CDS = "CDS"
    IMAGING = "Imaging"
    MCU = "MCU"


OptionalSimpleName = Optional[SimpleName]
ListOfSimpleNames = List[SimpleName]
OptionalListOfSimpleNames = Optional[ListOfSimpleNames]
SequenceOfSimpleNames = Sequence[SimpleName]
OptionalSequenceOfSimpleNames = Optional[SequenceOfSimpleNames]


class Name(StrEnum):
    STUDIO = "MaleoStudio"
    NEXUS = "MaleoNexus"
    TELEMETRY = "MaleoTelemetry"
    METADATA = "MaleoMetadata"
    IDENTITY = "MaleoIdentity"
    ACCESS = "MaleoAccess"
    WORKSHOP = "MaleoWorkshop"
    RESEARCH = "MaleoResearch"
    SOAPIE = "MaleoSOAPIE"
    MEDIX = "MaleoMedix"
    DICOM = "MaleoDICON"
    SCRIBE = "MaleoScribe"
    CDS = "MaleoCDS"
    IMAGING = "MaleoImaging"
    MCU = "MaleoMCU"


OptionalName = Optional[Name]
ListOfNames = List[Name]
OptionalListOfNames = Optional[ListOfNames]
SequenceOfNames = Sequence[Name]
OptionalSequenceOfNames = Optional[SequenceOfNames]
