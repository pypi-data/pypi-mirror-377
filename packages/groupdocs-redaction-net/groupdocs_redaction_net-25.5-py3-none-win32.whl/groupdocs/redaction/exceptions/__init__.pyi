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

class DocumentFormatException(GroupDocsRedactionException):
    '''The exception that is thrown when document format is not recognized or is invalid.'''
    
    def __init__(self, message : str) -> None:
        '''Initializes a new instance of DocumentFormatException class.
        
        :param message: Message, describing exception context'''
        raise NotImplementedError()
    

class GroupDocsRedactionException:
    '''Represents base exception for all GroupDocs.Redaction exceptions.'''
    
    def __init__(self, message : str) -> None:
        '''Initializes a new instance of GroupDocsRedactionException class.
        
        :param message: Message, describing exception context'''
        raise NotImplementedError()
    

class IncorrectPasswordException(GroupDocsRedactionException):
    '''The exception that is thrown when specified password is incorrect.'''
    
    def __init__(self) -> None:
        '''Initializes a new instance of IncorrectPasswordException class.'''
        raise NotImplementedError()
    

class PasswordRequiredException(GroupDocsRedactionException):
    '''The exception that is thrown when password is required to load the document.'''
    
    def __init__(self) -> None:
        '''Initializes a new instance of PasswordRequiredException class.'''
        raise NotImplementedError()
    

class TrialLimitationsException(GroupDocsRedactionException):
    '''The exception that is thrown when user violates trial mode limitations.'''
    
    def __init__(self, message : str) -> None:
        '''Initializes a new instance of TrialLimitationsException class.
        
        :param message: Message, describing violated limitation'''
        raise NotImplementedError()
    

