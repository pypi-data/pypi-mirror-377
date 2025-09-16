
from typing import List, Optional, Dict, Iterable, Any, overload
import io
import collections.abc
from collections.abc import Sequence
from datetime import datetime
from aspose.pyreflection import Type
import aspose.pycore
import aspose.pydrawing
from uuid import UUID
import groupdocs.redaction
import groupdocs.redaction.configuration
import groupdocs.redaction.exceptions
import groupdocs.redaction.integration
import groupdocs.redaction.integration.ocr
import groupdocs.redaction.options
import groupdocs.redaction.redactions

class DocumentInfo(IDocumentInfo):
    '''Represents an information about document. Implements IDocumentInfo interface. See :py:class:`groupdocs.redaction.IDocumentInfo` for examples.'''
    
    @property
    def file_type(self) -> groupdocs.redaction.FileType:
        '''Gets the file format description.'''
        raise NotImplementedError()
    
    @property
    def page_count(self) -> int:
        '''Gets the total page count.'''
        raise NotImplementedError()
    
    @property
    def size(self) -> int:
        '''Gets the document size in bytes.'''
        raise NotImplementedError()
    
    @property
    def pages(self) -> List[groupdocs.redaction.PageInfo]:
        '''Gets the list of :py:class:`groupdocs.redaction.PageInfo` page information.'''
        raise NotImplementedError()
    

class FileType:
    '''Represents a file type. Provides methods to obtain a list of all file types supported by GroupDocs.Redaction, detect file type by extension, etc.'''
    
    @staticmethod
    def from_extension(extension : str) -> groupdocs.redaction.FileType:
        '''Maps file extension to file type.
        
        :param extension: File extension (including the period ".").
        :returns: When file type is supported returns it, otherwise returns default :py:attr:`groupdocs.redaction.FileType.unknown` file type.'''
        raise NotImplementedError()
    
    @staticmethod
    def get_supported_file_types() -> Iterable[groupdocs.redaction.FileType]:
        '''Retrieves supported file types
        
        :returns: Returns sequence of supported file types'''
        raise NotImplementedError()
    
    def equals(self, other : groupdocs.redaction.FileType) -> bool:
        '''Determines whether the current :py:class:`groupdocs.redaction.FileType` is the same as specified :py:class:`groupdocs.redaction.FileType` object.
        
        :param other: The object to compare with the current :py:class:`groupdocs.redaction.FileType` object.
        :returns: true
        if both :py:class:`groupdocs.redaction.FileType` objects are the same; otherwise,     false'''
        raise NotImplementedError()
    
    @property
    def file_format(self) -> str:
        '''Gets file type name, for example "Microsoft Word Document".'''
        raise NotImplementedError()
    
    @property
    def extension(self) -> str:
        '''Gets filename suffix (including the period "."), for instance ".doc".'''
        raise NotImplementedError()
    
    @property
    def unknown(self) -> groupdocs.redaction.FileType:
        '''Represents unknown file type.'''
        raise NotImplementedError()

    @property
    def tif(self) -> groupdocs.redaction.FileType:
        '''Tagged Image File (.tif)'''
        raise NotImplementedError()

    @property
    def tiff(self) -> groupdocs.redaction.FileType:
        '''Tagged Image File Format (.tiff)'''
        raise NotImplementedError()

    @property
    def jpg(self) -> groupdocs.redaction.FileType:
        '''JPEG Image (.jpg)'''
        raise NotImplementedError()

    @property
    def jpeg(self) -> groupdocs.redaction.FileType:
        '''JPEG Image (.jpeg)'''
        raise NotImplementedError()

    @property
    def png(self) -> groupdocs.redaction.FileType:
        '''Portable Network Graphic (.png)'''
        raise NotImplementedError()

    @property
    def gif(self) -> groupdocs.redaction.FileType:
        '''Graphical Interchange Format File (.gif)'''
        raise NotImplementedError()

    @property
    def bmp(self) -> groupdocs.redaction.FileType:
        '''Bitmap Image File (.bmp)'''
        raise NotImplementedError()

    @property
    def jp2(self) -> groupdocs.redaction.FileType:
        '''JPEG 2000 Core Image File (.jp2)'''
        raise NotImplementedError()

    @property
    def htm(self) -> groupdocs.redaction.FileType:
        '''Hypertext Markup Language File (.htm)'''
        raise NotImplementedError()

    @property
    def html(self) -> groupdocs.redaction.FileType:
        '''Hypertext Markup Language File (.html)'''
        raise NotImplementedError()

    @property
    def pdf(self) -> groupdocs.redaction.FileType:
        '''Portable Document Format File (.pdf)'''
        raise NotImplementedError()

    @property
    def ppt(self) -> groupdocs.redaction.FileType:
        '''PowerPoint Presentation (.ppt)'''
        raise NotImplementedError()

    @property
    def pptx(self) -> groupdocs.redaction.FileType:
        '''PowerPoint Open XML Presentation (.pptx)'''
        raise NotImplementedError()

    @property
    def odp(self) -> groupdocs.redaction.FileType:
        '''OpenDocument Presentation (.odp)'''
        raise NotImplementedError()

    @property
    def xls(self) -> groupdocs.redaction.FileType:
        '''Excel Spreadsheet (.xls)'''
        raise NotImplementedError()

    @property
    def xlsx(self) -> groupdocs.redaction.FileType:
        '''Microsoft Excel Open XML Spreadsheet (.xlsx)'''
        raise NotImplementedError()

    @property
    def xlsm(self) -> groupdocs.redaction.FileType:
        '''Excel Open XML Macro-Enabled Spreadsheet (.xlsm)'''
        raise NotImplementedError()

    @property
    def xlsb(self) -> groupdocs.redaction.FileType:
        '''Excel Binary Spreadsheet (.xlsb)'''
        raise NotImplementedError()

    @property
    def csv(self) -> groupdocs.redaction.FileType:
        '''Comma Separated Values File (.csv)'''
        raise NotImplementedError()

    @property
    def tsv(self) -> groupdocs.redaction.FileType:
        '''Tab Separated Values File (.tsv)'''
        raise NotImplementedError()

    @property
    def ods(self) -> groupdocs.redaction.FileType:
        '''OpenDocument Spreadsheet (.ods)'''
        raise NotImplementedError()

    @property
    def ots(self) -> groupdocs.redaction.FileType:
        '''OpenDocument Spreadsheet Template (.ots)'''
        raise NotImplementedError()

    @property
    def numbers(self) -> groupdocs.redaction.FileType:
        '''Apple Numbers Spreadsheet (.numbers)'''
        raise NotImplementedError()

    @property
    def md(self) -> groupdocs.redaction.FileType:
        '''Markdown Documentation File (.md)'''
        raise NotImplementedError()

    @property
    def doc(self) -> groupdocs.redaction.FileType:
        '''Microsoft Word Document (.doc)'''
        raise NotImplementedError()

    @property
    def docx(self) -> groupdocs.redaction.FileType:
        '''Microsoft Word Open XML Document (.docx)'''
        raise NotImplementedError()

    @property
    def docm(self) -> groupdocs.redaction.FileType:
        '''Word Open XML Macro-Enabled Document (.docm)'''
        raise NotImplementedError()

    @property
    def dot(self) -> groupdocs.redaction.FileType:
        '''Word Document Template (.dot)'''
        raise NotImplementedError()

    @property
    def dotx(self) -> groupdocs.redaction.FileType:
        '''Word Open XML Document Template (.dotx)'''
        raise NotImplementedError()

    @property
    def dotm(self) -> groupdocs.redaction.FileType:
        '''Word Open XML Macro-Enabled Document Template (.dotm)'''
        raise NotImplementedError()

    @property
    def rtf(self) -> groupdocs.redaction.FileType:
        '''Rich Text Format File (.rtf)'''
        raise NotImplementedError()

    @property
    def txt(self) -> groupdocs.redaction.FileType:
        '''Plain Text File (.txt)'''
        raise NotImplementedError()

    @property
    def odt(self) -> groupdocs.redaction.FileType:
        '''OpenDocument Text Document (.odt)'''
        raise NotImplementedError()

    @property
    def ott(self) -> groupdocs.redaction.FileType:
        '''OpenDocument Document Template (.ott)'''
        raise NotImplementedError()


class IDocumentInfo:
    '''Defines methods that are required for getting basic document information.'''
    
    @property
    def file_type(self) -> groupdocs.redaction.FileType:
        '''Gets the file format description.'''
        raise NotImplementedError()
    
    @property
    def page_count(self) -> int:
        '''Gets the total page count.'''
        raise NotImplementedError()
    
    @property
    def size(self) -> int:
        '''Gets the document size in bytes.'''
        raise NotImplementedError()
    
    @property
    def pages(self) -> List[groupdocs.redaction.PageInfo]:
        '''Gets the list of :py:class:`groupdocs.redaction.PageInfo` page information.'''
        raise NotImplementedError()
    

class License:
    '''Provides methods for applying license.'''
    
    def __init__(self) -> None:
        '''Initialize an instance of License class.'''
        raise NotImplementedError()
    
    @overload
    def set_license(self, license_path : str) -> None:
        '''Sets the GroupDocs.Redaction license from a file path.
        
        :param license_path: License file path.'''
        raise NotImplementedError()
    
    @overload
    def set_license(self, license_stream : io._IOBase) -> None:
        '''Sets the GroupDocs.Redaction license from a stream.
        
        :param license_stream: License stream.'''
        raise NotImplementedError()
    

class Metered:
    '''Provides methods which allow to activate product with Metered license and retrieve amount of MBs processed.
    Learn more about Metered licenses `here <https://purchase.groupdocs.com/faqs/licensing/metered>`.'''
    
    def __init__(self) -> None:
        '''Initializes a new instance of Metered class.'''
        raise NotImplementedError()
    
    def set_metered_key(self, public_key : str, private_key : str) -> None:
        '''Activates the product with Metered keys.
        
        :param public_key: The public key.
        :param private_key: The private key.'''
        raise NotImplementedError()
    
    @staticmethod
    def get_consumption_quantity() -> float:
        '''Retrieves the amount of MBs processed.
        
        :returns: consumption quantity'''
        raise NotImplementedError()
    
    @staticmethod
    def get_consumption_credit() -> float:
        '''Gets the consumption credit.
        
        :returns: consumption quantity'''
        raise NotImplementedError()
    

class PageInfo:
    '''Represents a brief page information.'''
    
    def __init__(self) -> None:
        raise NotImplementedError()
    
    @property
    def width(self) -> int:
        '''Gets the page width.'''
        raise NotImplementedError()
    
    @width.setter
    def width(self, value : int) -> None:
        '''Sets the page width.'''
        raise NotImplementedError()
    
    @property
    def height(self) -> int:
        '''Gets the page height.'''
        raise NotImplementedError()
    
    @height.setter
    def height(self, value : int) -> None:
        '''Sets the page height.'''
        raise NotImplementedError()
    
    @property
    def page_number(self) -> int:
        '''Gets the page number.'''
        raise NotImplementedError()
    
    @page_number.setter
    def page_number(self, value : int) -> None:
        '''Sets the page number.'''
        raise NotImplementedError()
    

class Redaction:
    '''Represents a base abstract class for all redaction types.'''
    
    def apply_to(self, format_instance : groupdocs.redaction.integration.DocumentFormatInstance) -> groupdocs.redaction.RedactorLogEntry:
        '''Applies the redaction to a given format instance.
        
        :param format_instance: An instance of a document to apply redaction
        :returns: Status of the redaction: success/failure and error message if any'''
        raise NotImplementedError()
    
    @property
    def description(self) -> str:
        '''Returns a string, describing the redaction and its parameters.'''
        raise NotImplementedError()
    

class RedactionPolicy:
    '''Represents a sanitization policy, containing a set of specific redactions to apply.'''
    
    @overload
    def __init__(self) -> None:
        '''Creates a new instance of Redaction policy.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, redactions : List[groupdocs.redaction.Redaction]) -> None:
        '''Creates a new instance of Redaction policy with a specific list of redactions.
        
        :param redactions: An array of redactions for the policy'''
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def load(file_path : str) -> groupdocs.redaction.RedactionPolicy:
        '''Loads an instance of :py:class:`groupdocs.redaction.RedactionPolicy` from a file path.
        
        :param file_path: Path to XML file
        :returns: Redaction policy'''
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def load(input : io._IOBase) -> groupdocs.redaction.RedactionPolicy:
        '''Loads an instance of :py:class:`groupdocs.redaction.RedactionPolicy` from a stream.
        
        :param input: Stream containing XML configuration
        :returns: Redaction policy'''
        raise NotImplementedError()
    
    @overload
    def save(self, file_path : str) -> None:
        '''Saves the redaction policy to a file.
        
        :param file_path: Path to file.'''
        raise NotImplementedError()
    
    @overload
    def save(self, output : io._IOBase) -> None:
        '''Saves the redaction policy to a stream.
        
        :param output: Target stream to save the policy'''
        raise NotImplementedError()
    
    @property
    def redactions(self) -> List[groupdocs.redaction.Redaction]:
        '''Gets an array of fully configured :py:class:`groupdocs.redaction.Redaction`-derived classes.'''
        raise NotImplementedError()
    

class RedactionResult:
    '''Represents a result of the redaction operation.'''
    
    @staticmethod
    def skipped(description : str) -> groupdocs.redaction.RedactionResult:
        '''Initializes a new instance of RedactionResult class with Skipped status.
        
        :param description: Reason why the operation was skipped
        :returns: Skipped redaction result'''
        raise NotImplementedError()
    
    @staticmethod
    def partial(description : str) -> groupdocs.redaction.RedactionResult:
        '''Initializes a new instance of RedactionResult class with PartiallyApplied status.
        
        :param description: Reason why the operation was not fully applied
        :returns: Partially applied redaction result'''
        raise NotImplementedError()
    
    @staticmethod
    def failed(description : str) -> groupdocs.redaction.RedactionResult:
        '''Initializes a new instance of RedactionResult class with Failed status.
        
        :param description: Failure or exception details
        :returns: Failed redaction result'''
        raise NotImplementedError()
    
    @staticmethod
    def successful() -> groupdocs.redaction.RedactionResult:
        '''Initializes a new instance of RedactionResult class with Applied (successful) status.
        
        :returns: Successful redaction result'''
        raise NotImplementedError()
    
    @property
    def status(self) -> groupdocs.redaction.RedactionStatus:
        '''Gets the execution status.'''
        raise NotImplementedError()
    
    @property
    def error_message(self) -> str:
        '''Gets the error message for diagnostics.'''
        raise NotImplementedError()
    

class Redactor(groupdocs.redaction.integration.IPreviewable):
    '''Represents a main class that controls document redaction process, allowing to open, redact and save documents.'''
    
    @overload
    def __init__(self, file_path : str) -> None:
        '''Initializes a new instance of :py:class:`groupdocs.redaction.Redactor` class using file path.
        
        :param file_path: Path to the file'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, document : io._IOBase) -> None:
        '''Initializes a new instance of :py:class:`groupdocs.redaction.Redactor` class using stream.
        
        :param document: Source stream of the document'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, file_path : str, load_options : groupdocs.redaction.options.LoadOptions) -> None:
        '''Initializes a new instance of :py:class:`groupdocs.redaction.Redactor` class for a password-protected document using its path.
        
        :param file_path: Path to file.
        :param load_options: Options, including password.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, file_path : str, load_options : groupdocs.redaction.options.LoadOptions, settings : groupdocs.redaction.options.RedactorSettings) -> None:
        '''Initializes a new instance of :py:class:`groupdocs.redaction.Redactor` class for a password-protected document using its path and settings.
        
        :param file_path: Path to file.
        :param load_options: File-dependent options, including password.
        :param settings: Default settings for redaction process.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, document : io._IOBase, load_options : groupdocs.redaction.options.LoadOptions) -> None:
        '''Initializes a new instance of :py:class:`groupdocs.redaction.Redactor` class for a password-protected document using stream.
        
        :param document: Source input stream.
        :param load_options: Options, including password.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, document : io._IOBase, load_options : groupdocs.redaction.options.LoadOptions, settings : groupdocs.redaction.options.RedactorSettings) -> None:
        '''Initializes a new instance of :py:class:`groupdocs.redaction.Redactor` class for a password-protected document using stream and settings.
        
        :param document: Source input stream.
        :param load_options: Options, including password.
        :param settings: Default settings for redaction process.'''
        raise NotImplementedError()
    
    @overload
    def apply(self, redaction : groupdocs.redaction.Redaction) -> groupdocs.redaction.RedactorChangeLog:
        '''Applies a redaction to the document.
        
        :param redaction: An instance of :py:class:`groupdocs.redaction.Redaction` to apply
        :returns: Success or failure and error message in this case'''
        raise NotImplementedError()
    
    @overload
    def apply(self, redactions : List[groupdocs.redaction.Redaction]) -> groupdocs.redaction.RedactorChangeLog:
        '''Applies a set of redactions to the document.
        
        :param redactions: An array of redactions to apply
        :returns: Success or failure and error message in this case'''
        raise NotImplementedError()
    
    @overload
    def apply(self, policy : groupdocs.redaction.RedactionPolicy) -> groupdocs.redaction.RedactorChangeLog:
        '''Applies a redaction policy to the document.
        
        :param policy: Redaction policy
        :returns: Success or failure and error message in this case'''
        raise NotImplementedError()
    
    @overload
    def save(self) -> str:
        '''Saves the document to a file with the following options: AddSuffix = true, RasterizeToPDF = true.
        
        :returns: Path to redacted document'''
        raise NotImplementedError()
    
    @overload
    def save(self, save_options : groupdocs.redaction.options.SaveOptions) -> str:
        '''Saves the document to a file.
        
        :param save_options: Options to add suffix or rasterize
        :returns: Path to redacted document'''
        raise NotImplementedError()
    
    @overload
    def save(self, document : io._IOBase, rasterization_options : groupdocs.redaction.options.RasterizationOptions) -> None:
        '''Saves the document to a stream, including custom location.
        
        :param document: Target stream
        :param rasterization_options: Options to rasterize or not and to specify pages for rasterization'''
        raise NotImplementedError()
    
    def generate_preview(self, preview_options : groupdocs.redaction.options.PreviewOptions) -> None:
        '''Generates preview images of specific pages in a given image format.
        
        :param preview_options: Image properties and page range settings'''
        raise NotImplementedError()
    
    def get_document_info(self) -> groupdocs.redaction.IDocumentInfo:
        '''Gets the general information about the document - size, page count, etc.
        
        :returns: An instance of IDocumentInfo'''
        raise NotImplementedError()
    

class RedactorChangeLog:
    '''Represents results for a list of redactions, passed to Apply() method of :py:class:`groupdocs.redaction.Redactor` class.'''
    
    def __init__(self) -> None:
        '''Initializes a new instance of RedactorChangeLog class.'''
        raise NotImplementedError()
    
    @property
    def status(self) -> groupdocs.redaction.RedactionStatus:
        '''Gets the final status of all applied redactions.'''
        raise NotImplementedError()
    
    @property
    def redaction_log(self) -> List[groupdocs.redaction.RedactorLogEntry]:
        '''Gets the list of :py:class:`groupdocs.redaction.RedactorLogEntry` instances.'''
        raise NotImplementedError()
    

class RedactorLogEntry:
    '''Represents results of applying redaction.'''
    
    def __init__(self, redaction : groupdocs.redaction.Redaction, result : groupdocs.redaction.RedactionResult) -> None:
        '''Initializes a new instance of RedactorLogEntry class for redaction.
        
        :param redaction: Reference to redaction
        :param result: Redaction result, reported by format handler'''
        raise NotImplementedError()
    
    @property
    def result(self) -> groupdocs.redaction.RedactionResult:
        '''Gets the result, returned by :py:class:`groupdocs.redaction.integration.DocumentFormatInstance`.'''
        raise NotImplementedError()
    
    @property
    def redaction(self) -> groupdocs.redaction.Redaction:
        '''Gets the reference to redaction and its options.'''
        raise NotImplementedError()
    

class RedactionStatus:
    '''Represents a redaction completion status.'''
    
    APPLIED : RedactionStatus
    '''Redaction was fully and successfully applied.'''
    PARTIALLY_APPLIED : RedactionStatus
    '''Redaction was applied only to a part of its matches.'''
    SKIPPED : RedactionStatus
    '''Redaction was skipped (not applied).'''
    FAILED : RedactionStatus
    '''Redaction failed with exception.'''

