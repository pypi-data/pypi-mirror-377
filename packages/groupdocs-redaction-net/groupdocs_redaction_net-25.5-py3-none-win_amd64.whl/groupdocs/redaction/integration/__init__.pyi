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

class DocumentFormatInstance:
    '''Represents a specific format of a document. Implement this class to add your own document types.'''
    
    def initialize(self, config : groupdocs.redaction.configuration.DocumentFormatConfiguration, settings : groupdocs.redaction.options.RedactorSettings) -> None:
        '''Performs initialization of the instance of document format handler.
        
        :param config: Format configuration
        :param settings: Default settings for redaction process.'''
        raise NotImplementedError()
    
    def load(self, input : io._IOBase) -> None:
        '''Loads the document from a stream.
        
        :param input: Stream to read from'''
        raise NotImplementedError()
    
    def save(self, output : io._IOBase) -> None:
        '''Saves the document to a stream.
        
        :param output: Target stream to save the document'''
        raise NotImplementedError()
    
    def is_redaction_accepted(self, description : groupdocs.redaction.redactions.RedactionDescription) -> bool:
        '''Checks for :py:class:`groupdocs.redaction.redactions.IRedactionCallback` implementation and invokes it, if specified.
        
        :param description: Redaction description
        :returns: True (by default) if redaction is accepted'''
        raise NotImplementedError()
    
    def perform_binary_check(self, input : io._IOBase) -> bool:
        '''Checks if the given stream contains a document, supported by this format instance.
        
        :param input: Document content stream
        :returns: True, if the document can be loaded by this format instance and false otherwise'''
        raise NotImplementedError()
    
    @property
    def password(self) -> str:
        '''Gets a password for password protected documents.'''
        raise NotImplementedError()
    
    @password.setter
    def password(self, value : str) -> None:
        '''Sets a password for password protected documents.'''
        raise NotImplementedError()
    

class IAnnotatedDocument:
    '''Defines methods that are required for access to annotations, such as comments. Needs to be implemented by :py:class:`groupdocs.redaction.integration.DocumentFormatInstance`-derived class to perform annotation redactions.'''
    

class ICellularFormatInstance:
    '''Defines methods that are required for access to spreadsheet formats, having one or many worksheets.'''
    
    def get_sheet_index(self, sheet_name : str) -> int:
        '''Gets the worksheet index by worksheet name, if possible.
        
        :param sheet_name: Worksheet name
        :returns: Worksheet index or -1 if not found'''
        raise NotImplementedError()
    

class IFixedFormatDocument:
    '''Defines methods that are required for access formats of fixed structure, such as PDF or presentations.'''
    
    def load_images(self, filters : List[groupdocs.redaction.redactions.RedactionFilter]) -> List[groupdocs.redaction.integration.IImageFormatInstance]:
        '''Loads an array of raster image instances, contained within the document, matching :py:class:`groupdocs.redaction.redactions.RedactionFilter` set.
        
        :param filters: An array of RedactionFilter instances to apply
        :returns: An array of raster image instances'''
        raise NotImplementedError()
    

class IImageFormatInstance:
    '''Defines methods that are required for raster image format redactions.'''
    
    def edit_area(self, top_left : Any, options : groupdocs.redaction.redactions.RegionReplacementOptions) -> groupdocs.redaction.RedactionResult:
        '''Replaces the area at given point with a rectangle of specific color and size.
        
        :param top_left: Top-left corner coordinates of filled area
        :param options: Color and size settings
        :returns: Image area redaction result'''
        raise NotImplementedError()
    

class IMetadataAccess:
    '''Defines methods that are required for access to metadata of a document, if format supports it.'''
    
    def get_metadata(self) -> groupdocs.redaction.integration.MetadataCollection:
        '''Retrieves a dictionary with document\'s metadata.
        
        :returns: Plain dictionary with metadata'''
        raise NotImplementedError()
    
    def change_metadata(self, metadata_item : groupdocs.redaction.integration.MetadataItem) -> groupdocs.redaction.RedactionResult:
        '''Changes the specified item of metadata from :py:class:`groupdocs.redaction.integration.MetadataCollection` or adds a new one, if not present.
        
        :param metadata_item: Metadata item with a new value assigned to it
        :returns: Metadata redaction result'''
        raise NotImplementedError()
    

class IPaginatedDocument:
    '''Defines methods that are required to manipulate a document\'s pages. Needs to be implemented by :py:class:`groupdocs.redaction.integration.DocumentFormatInstance`-derived class to perform page redactions.'''
    
    def remove_pages(self, origin : groupdocs.redaction.redactions.PageSeekOrigin, index : int, count : int) -> groupdocs.redaction.RedactionResult:
        '''Removes one or multiple pages depending on its start position, offset and count.
        
        :param origin: Search origin position, the beginning or the end of the document
        :param index: Start position index (0-based)
        :param count: Count of pages to remove
        :returns: Pages removal redaction result'''
        raise NotImplementedError()
    

class IPreviewable:
    '''Defines methods to create preview of the document.'''
    
    def generate_preview(self, preview_options : groupdocs.redaction.options.PreviewOptions) -> None:
        '''Generates preview images of specific pages in a given image format.
        
        :param preview_options: Image properties and page range settings'''
        raise NotImplementedError()
    
    def get_document_info(self) -> groupdocs.redaction.IDocumentInfo:
        '''Gets the general information about the document - size, page count, etc.
        
        :returns: An instance of IDocumentInfo'''
        raise NotImplementedError()
    

class IRasterizableDocument:
    '''Defines methods that are required for saving document in any binary form. Built-in types save a document as a PDF with images of its pages.'''
    
    @overload
    def rasterize(self, output : io._IOBase) -> None:
        '''Saves the document to a stream as a PDF.
        
        :param output: Target stream'''
        raise NotImplementedError()
    
    @overload
    def rasterize(self, output : io._IOBase, options : groupdocs.redaction.options.RasterizationOptions) -> None:
        '''Saves the document to a stream as a PDF with page range and compliance options.
        
        :param output: Target stream
        :param options: PDF conversion options'''
        raise NotImplementedError()
    

class ITextualFormatInstance:
    '''Defines methods that are required for redacting textual data in any document, containing text.'''
    

class MetadataCollection:
    '''Represents a dictionary of :py:class:`groupdocs.redaction.integration.MetadataItem` with its title as a key.'''
    
    def __init__(self) -> None:
        '''Initializes a new instance of MetadataCollection class.'''
        raise NotImplementedError()
    
    def add_range(self, items : groupdocs.redaction.integration.MetadataCollection) -> None:
        '''Adds a specified collection of MetadataItem objects to this instance.
        
        :param items: A collection of MetadataItem instances'''
        raise NotImplementedError()
    

class MetadataItem:
    '''Represents an item of metadata, common for all supported formats and used in metadata redactions.'''
    
    def __init__(self) -> None:
        '''Initializes a new instance.'''
        raise NotImplementedError()
    
    def create_clone(self) -> groupdocs.redaction.integration.MetadataItem:
        '''Creates a deep clone of current instance.
        
        :returns: Object clone'''
        raise NotImplementedError()
    
    @property
    def original_name(self) -> str:
        '''Gets an original name of the metadata item, as it appears in the document.'''
        raise NotImplementedError()
    
    @original_name.setter
    def original_name(self, value : str) -> None:
        '''Sets an original name of the metadata item, as it appears in the document.'''
        raise NotImplementedError()
    
    @property
    def category(self) -> str:
        '''Gets a category of the metadata item, for example resource ID for an embedded resource metadata item.'''
        raise NotImplementedError()
    
    @category.setter
    def category(self, value : str) -> None:
        '''Sets a category of the metadata item, for example resource ID for an embedded resource metadata item.'''
        raise NotImplementedError()
    
    @property
    def filter(self) -> groupdocs.redaction.redactions.MetadataFilters:
        '''Gets a value of :py:class:`groupdocs.redaction.redactions.MetadataFilters`, assigned to this metadata item which is used in item filtration.'''
        raise NotImplementedError()
    
    @filter.setter
    def filter(self, value : groupdocs.redaction.redactions.MetadataFilters) -> None:
        '''Sets a value of :py:class:`groupdocs.redaction.redactions.MetadataFilters`, assigned to this metadata item which is used in item filtration.'''
        raise NotImplementedError()
    
    @property
    def values(self) -> List[str]:
        '''Gets the metadata item value.'''
        raise NotImplementedError()
    
    @values.setter
    def values(self, value : List[str]) -> None:
        '''Sets the metadata item value.'''
        raise NotImplementedError()
    
    @property
    def is_custom(self) -> bool:
        '''Gets a value indicating whether this item is custom (added by the authors of the document).'''
        raise NotImplementedError()
    
    @is_custom.setter
    def is_custom(self, value : bool) -> None:
        '''Sets a value indicating whether this item is custom (added by the authors of the document).'''
        raise NotImplementedError()
    
    @property
    def dictionary_key(self) -> str:
        '''Gets a dictionary key for :py:class:`groupdocs.redaction.integration.MetadataCollection`, using its OriginalName and other data.'''
        raise NotImplementedError()
    
    @property
    def actual_value(self) -> str:
        '''Gets the string representation of the metadata item value.'''
        raise NotImplementedError()
    

