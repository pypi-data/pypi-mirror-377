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

class DocumentFormatConfiguration:
    '''Represents a type reference for :py:class:`groupdocs.redaction.integration.DocumentFormatInstance`-derived class and supported file extensions list for faster format detection.'''
    
    def __init__(self) -> None:
        '''Initializes a new instance of DocumentFormatConfiguration class.'''
        raise NotImplementedError()
    
    def supports_extension(self, file_extension : str) -> bool:
        '''Checks if a given file extension can be handled as DocumentType.
        
        :param file_extension: File extension, format is ".ext"
        :returns: True if the extension is listed in ExtensionFilter'''
        raise NotImplementedError()
    
    @property
    def extension_filter(self) -> str:
        '''Gets a comma (",") delimited list of file extensions (for example ".pdf"), case insensitive.'''
        raise NotImplementedError()
    
    @extension_filter.setter
    def extension_filter(self, value : str) -> None:
        '''Sets a comma (",") delimited list of file extensions (for example ".pdf"), case insensitive.'''
        raise NotImplementedError()
    
    @property
    def document_type(self) -> Type:
        '''Gets the type of a class, inheriting from :py:class:`groupdocs.redaction.integration.DocumentFormatInstance`.'''
        raise NotImplementedError()
    
    @document_type.setter
    def document_type(self, value : Type) -> None:
        '''Sets the type of a class, inheriting from :py:class:`groupdocs.redaction.integration.DocumentFormatInstance`.'''
        raise NotImplementedError()
    

class RedactorConfiguration:
    '''Provides access to a list of supported formats, built-in and custom user formats.'''
    
    def find_format(self, file_extension : str) -> groupdocs.redaction.configuration.DocumentFormatConfiguration:
        '''Finds format configurations for a given file extension.
        
        :param file_extension: File extension, format is ".ext"
        :returns: If found, instance of :py:class:`groupdocs.redaction.configuration.DocumentFormatConfiguration`, null otherwise'''
        raise NotImplementedError()
    
    @staticmethod
    def get_instance() -> groupdocs.redaction.configuration.RedactorConfiguration:
        '''Provides a singleton instance with default configuration of built-in formats.
        
        :returns: Configuration instance'''
        raise NotImplementedError()
    
    @property
    def available_formats(self) -> List[groupdocs.redaction.configuration.DocumentFormatConfiguration]:
        '''Gets a list of recognized formats, see :py:class:`groupdocs.redaction.configuration.DocumentFormatConfiguration`.'''
        raise NotImplementedError()
    

