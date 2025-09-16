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

class IOcrConnector:
    '''Defines methods that are required to apply textual redactions to image documents and embedded images.'''
    
    def recognize(self, image_stream : io._IOBase) -> groupdocs.redaction.integration.ocr.RecognizedImage:
        '''Does the OCR processing of an image, provided as a stream.
        
        :param image_stream: Stream, containing an image to process
        :returns: Structured recognized text, containing lines, words and their bounding rectangles'''
        raise NotImplementedError()
    

class RecognizedImage:
    '''Represents text, extracted from an image as a result of its recognition process.'''
    
    def __init__(self, lines : Iterable[groupdocs.redaction.integration.ocr.TextLine]) -> None:
        raise NotImplementedError()
    
    @property
    def text(self) -> str:
        '''Gets textual equivalent of the structured text.'''
        raise NotImplementedError()
    
    @property
    def lines(self) -> List[groupdocs.redaction.integration.ocr.TextLine]:
        '''Gets lines of text, with their fragments, recognized within the document.'''
        raise NotImplementedError()
    

class TextFragment:
    '''Represents a part of recognized text (word, symbol, etc), extracted by OCR engine.'''
    
    def __init__(self, text : str, rectangle : Any) -> None:
        '''Initializes a new instance of the recognized text fragment.
        
        :param text: textual content of the recognized text fragment
        :param rectangle: bounding rectangle of the recognized text fragment'''
        raise NotImplementedError()
    
    @property
    def text(self) -> str:
        '''Gets a textual content of the recognized text fragment.'''
        raise NotImplementedError()
    
    @property
    def rectangle(self) -> Any:
        '''Gets a bounding rectangle of the recognized text fragment.'''
        raise NotImplementedError()
    

class TextLine:
    '''Represents a line of text, extracted by OCR engine from an image.'''
    
    def __init__(self, fragments : Iterable[groupdocs.redaction.integration.ocr.TextFragment]) -> None:
        raise NotImplementedError()
    
    @property
    def fragments(self) -> List[groupdocs.redaction.integration.ocr.TextFragment]:
        '''Gets an array of text fragments, such as symbols and words, recognized in the line.'''
        raise NotImplementedError()
    

