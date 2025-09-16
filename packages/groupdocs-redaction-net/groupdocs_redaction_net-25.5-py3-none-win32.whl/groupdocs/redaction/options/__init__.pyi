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

class ILogger:
    '''Defines interface of a logger that can be used for logging events and errors in process of redaction.'''
    
    def error(self, message : str) -> None:
        '''Logs an error that occurred during redaction process.
        
        :param message: The error message.'''
        raise NotImplementedError()
    
    def trace(self, message : str) -> None:
        '''Logs an event that occurred during redaction process.
        
        :param message: The event message.'''
        raise NotImplementedError()
    
    def warning(self, message : str) -> None:
        '''Logs a warning that occurred during redaction process.
        
        :param message: The warning message.'''
        raise NotImplementedError()
    

class LoadOptions:
    '''Provides options that will be used to open a file.'''
    
    @overload
    def __init__(self) -> None:
        '''Initializes a new instance of LoadOptions class.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, password : str) -> None:
        '''Initializes a new instance of LoadOptions class with specified password.
        
        :param password: Password for protected files'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, pre_rasterize : bool) -> None:
        '''Initializes a new instance of LoadOptions class with specified pre-rasterization flag.
        
        :param pre_rasterize: If true, force rasterization on loading'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, password : str, pre_rasterize : bool) -> None:
        '''Initializes a new instance of LoadOptions class with specified password.
        
        :param password: Password for protected files
        :param pre_rasterize: If true, force rasterization on loading'''
        raise NotImplementedError()
    
    @property
    def password(self) -> str:
        '''Gets a password for password-protected documents.'''
        raise NotImplementedError()
    
    @password.setter
    def password(self, value : str) -> None:
        '''Sets a password for password-protected documents.'''
        raise NotImplementedError()
    
    @property
    def pre_rasterize(self) -> bool:
        '''Gets a value, indicating if the file is to be pre-rasterized.'''
        raise NotImplementedError()
    
    @pre_rasterize.setter
    def pre_rasterize(self, value : bool) -> None:
        '''Sets a value, indicating if the file is to be pre-rasterized.'''
        raise NotImplementedError()
    

class PreviewOptions:
    '''Provides options to sets requirements and stream delegates for preview generation.'''
    
    @property
    def width(self) -> int:
        '''Gets page preview width.'''
        raise NotImplementedError()
    
    @width.setter
    def width(self, value : int) -> None:
        '''Sets page preview width.'''
        raise NotImplementedError()
    
    @property
    def height(self) -> int:
        '''Gets page preview height.'''
        raise NotImplementedError()
    
    @height.setter
    def height(self, value : int) -> None:
        '''Sets page preview height.'''
        raise NotImplementedError()
    
    @property
    def page_numbers(self) -> List[int]:
        '''Gets an array of page numbers to generate preview.'''
        raise NotImplementedError()
    
    @page_numbers.setter
    def page_numbers(self, value : List[int]) -> None:
        '''Sets an array of page numbers to generate preview.'''
        raise NotImplementedError()
    
    @property
    def preview_format(self) -> PreviewOptions.PreviewFormats:
        '''Gets preview image format.'''
        raise NotImplementedError()
    
    @preview_format.setter
    def preview_format(self, value : PreviewOptions.PreviewFormats) -> None:
        '''Sets preview image format.'''
        raise NotImplementedError()
    

class RasterizationOptions:
    '''Provides options for converting files into PDF.'''
    
    def __init__(self) -> None:
        '''Initializes a new instance.'''
        raise NotImplementedError()
    
    def add_advanced_option(self, option_type : groupdocs.redaction.options.AdvancedRasterizationOptions) -> None:
        '''You can use this method to register an advanced rasterization option to apply.
        
        :param option_type: Provides information about the selected effect type (grayscale, border, etc.)'''
        raise NotImplementedError()
    
    @property
    def enabled(self) -> bool:
        '''Gets a value indicating whether all pages in the document need to be converted to images and put in a single PDF file. TRUE by default, set to FALSE in order to avoid rasterization.'''
        raise NotImplementedError()
    
    @enabled.setter
    def enabled(self, value : bool) -> None:
        '''Sets a value indicating whether all pages in the document need to be converted to images and put in a single PDF file. TRUE by default, set to FALSE in order to avoid rasterization.'''
        raise NotImplementedError()
    
    @property
    def page_index(self) -> int:
        '''Gets the index of the first page (0-based) to convert into PDF.'''
        raise NotImplementedError()
    
    @page_index.setter
    def page_index(self, value : int) -> None:
        '''Sets the index of the first page (0-based) to convert into PDF.'''
        raise NotImplementedError()
    
    @property
    def page_count(self) -> int:
        '''Gets the number of pages to be converted into PDF.'''
        raise NotImplementedError()
    
    @page_count.setter
    def page_count(self, value : int) -> None:
        '''Sets the number of pages to be converted into PDF.'''
        raise NotImplementedError()
    
    @property
    def compliance(self) -> groupdocs.redaction.options.PdfComplianceLevel:
        '''Gets the PDF Compliance level.'''
        raise NotImplementedError()
    
    @compliance.setter
    def compliance(self, value : groupdocs.redaction.options.PdfComplianceLevel) -> None:
        '''Sets the PDF Compliance level.'''
        raise NotImplementedError()
    
    @property
    def has_advanced_options(self) -> bool:
        '''Gets an indicator, which is true if advanced rasterization options are set.'''
        raise NotImplementedError()
    

class RedactorSettings:
    '''Represents redaction settings, allowing to customize the redaction process.'''
    
    @overload
    def __init__(self) -> None:
        '''Initializes a new instance of the RedactorSettings class.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, logger : groupdocs.redaction.options.ILogger) -> None:
        '''Initializes a new instance of the RedactorSettings class with a given ILogger instance.
        
        :param logger: An instance of a class, implementing ILogger interface'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, callback : groupdocs.redaction.redactions.IRedactionCallback) -> None:
        '''Initializes a new instance of the RedactorSettings class with a given IRedactionCallback instance.
        
        :param callback: An instance of a class, implementing IRedactionCallbck interface'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, ocr_connector : groupdocs.redaction.integration.ocr.IOcrConnector) -> None:
        '''Initializes a new instance of the RedactorSettings class with a given IOcrConnector instance.
        
        :param ocr_connector: A valid implementation of IOcrConnector interface'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, logger : groupdocs.redaction.options.ILogger, callback : groupdocs.redaction.redactions.IRedactionCallback) -> None:
        '''Initializes a new instance of the RedactorSettings class with given ILogger and IRedactionCallback instances.
        
        :param logger: An instance of a class, implementing ILogger interface
        :param callback: An instance of a class, implementing IRedactionCallbck interface'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, logger : groupdocs.redaction.options.ILogger, callback : groupdocs.redaction.redactions.IRedactionCallback, ocr_connector : groupdocs.redaction.integration.ocr.IOcrConnector) -> None:
        '''Initializes a new instance of the RedactorSettings class with given ILogger, IRedactionCallback and IOcrConnector instances.
        
        :param logger: An instance of a class, implementing ILogger interface
        :param callback: An instance of a class, implementing IRedactionCallbck interface
        :param ocr_connector: An instance of IOcrConnector interface implementation. Can be null'''
        raise NotImplementedError()
    
    @property
    def logger(self) -> groupdocs.redaction.options.ILogger:
        '''Gets an instance of a class, implementing :py:class:`groupdocs.redaction.options.ILogger`, that is used for logging events and errors.'''
        raise NotImplementedError()
    
    @logger.setter
    def logger(self, value : groupdocs.redaction.options.ILogger) -> None:
        '''Sets an instance of a class, implementing :py:class:`groupdocs.redaction.options.ILogger`, that is used for logging events and errors.'''
        raise NotImplementedError()
    
    @property
    def redaction_callback(self) -> groupdocs.redaction.redactions.IRedactionCallback:
        '''Gets an instance of a class, implementing :py:class:`groupdocs.redaction.redactions.IRedactionCallback`.'''
        raise NotImplementedError()
    
    @redaction_callback.setter
    def redaction_callback(self, value : groupdocs.redaction.redactions.IRedactionCallback) -> None:
        '''Sets an instance of a class, implementing :py:class:`groupdocs.redaction.redactions.IRedactionCallback`.'''
        raise NotImplementedError()
    
    @property
    def ocr_connector(self) -> groupdocs.redaction.integration.ocr.IOcrConnector:
        '''Gets an instance of a class, implementing :py:class:`groupdocs.redaction.integration.ocr.IOcrConnector` interface.'''
        raise NotImplementedError()
    
    @ocr_connector.setter
    def ocr_connector(self, value : groupdocs.redaction.integration.ocr.IOcrConnector) -> None:
        '''Sets an instance of a class, implementing :py:class:`groupdocs.redaction.integration.ocr.IOcrConnector` interface.'''
        raise NotImplementedError()
    

class SaveOptions:
    '''Provides options for changing an output file name and/or converting the document to image-based PDF (rasterization).'''
    
    @overload
    def __init__(self) -> None:
        '''Initializes a new instance with defaults: rasterize to PDF - false, add suffix - false.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, rasterize_to_pdf : bool, suffix : str) -> None:
        '''Initializes a new instance with given parameters.
        
        :param rasterize_to_pdf: True, if all pages in the document need to be converted to images and put in a single PDF file
        :param suffix: This text will be added to the end of file name, if not empty also sets AddSuffix to true'''
        raise NotImplementedError()
    
    @property
    def add_suffix(self) -> bool:
        '''Gets a value indicating whether the file name needs to be changed before saving. False by default.'''
        raise NotImplementedError()
    
    @add_suffix.setter
    def add_suffix(self, value : bool) -> None:
        '''Sets a value indicating whether the file name needs to be changed before saving. False by default.'''
        raise NotImplementedError()
    
    @property
    def redacted_file_suffix(self) -> str:
        '''Gets a custom suffix for output file name. If it is not specified, the :py:attr:`groupdocs.redaction.options.SaveOptions.SAVE_SUFFIX` constant will be used.'''
        raise NotImplementedError()
    
    @redacted_file_suffix.setter
    def redacted_file_suffix(self, value : str) -> None:
        '''Sets a custom suffix for output file name. If it is not specified, the :py:attr:`groupdocs.redaction.options.SaveOptions.SAVE_SUFFIX` constant will be used.'''
        raise NotImplementedError()
    
    @property
    def rasterize_to_pdf(self) -> bool:
        '''Gets a value indicating whether all pages in the document need to be converted to images and put in a single PDF file.'''
        raise NotImplementedError()
    
    @rasterize_to_pdf.setter
    def rasterize_to_pdf(self, value : bool) -> None:
        '''Sets a value indicating whether all pages in the document need to be converted to images and put in a single PDF file.'''
        raise NotImplementedError()
    
    @property
    def rasterization(self) -> groupdocs.redaction.options.RasterizationOptions:
        '''Gets the rasterization settings.'''
        raise NotImplementedError()
    
    @property
    def SAVE_SUFFIX(self) -> str:
        '''Represents default suffix value, which is "Redacted".'''
        raise NotImplementedError()


class AdvancedRasterizationOptions:
    '''Flags enumeration to manage the advanced rasterization options to be applied.'''
    
    NONE : AdvancedRasterizationOptions
    '''No advanced options to apply.'''
    TILT : AdvancedRasterizationOptions
    '''Tilt to incline the rasterized image to a random angle.'''
    NOISE : AdvancedRasterizationOptions
    '''Add random spots to rasterized page images.'''
    BORDER : AdvancedRasterizationOptions
    '''Add border line to imitate page scan effect.'''
    GRAYSCALE : AdvancedRasterizationOptions
    '''Make page images grayscale to imitate grayscale scan.'''

class PdfComplianceLevel:
    '''Represents a list of supported PDF compliance levels.'''
    
    AUTO : PdfComplianceLevel
    '''The output file will comply with the PDF/A-1b standard by default.'''
    PDF_A1A : PdfComplianceLevel
    '''The output file will comply with the PDF/A-1a standard.'''

