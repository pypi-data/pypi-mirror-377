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

class AnnotationRedaction(groupdocs.redaction.Redaction):
    '''Represents a redaction that replaces annotation text (comments, etc.) matching a given regular expression.'''
    
    def __init__(self, pattern : str, replacement : str) -> None:
        '''Initializes a new instance of AnnotationRedaction class.
        
        :param pattern: Regular expression to match
        :param replacement: Textual replacement for matched text'''
        raise NotImplementedError()
    
    def apply_to(self, format_instance : groupdocs.redaction.integration.DocumentFormatInstance) -> groupdocs.redaction.RedactorLogEntry:
        '''Applies the redaction to a given format instance.
        
        :param format_instance: An instance of a document to apply redaction
        :returns: Status of the redaction: success/failure and error message if any'''
        raise NotImplementedError()
    
    @property
    def description(self) -> str:
        '''Returns a string, describing the redaction and its parameters.'''
        raise NotImplementedError()
    
    @property
    def replacement(self) -> str:
        '''Gets a textual replacement for matched text.'''
        raise NotImplementedError()
    

class CellColumnRedaction(TextRedaction):
    '''Represents a text redaction that replaces text in a spreadsheet documents (CSV, Excel, etc.).'''
    
    def apply_to(self, format_instance : groupdocs.redaction.integration.DocumentFormatInstance) -> groupdocs.redaction.RedactorLogEntry:
        '''Applies the redaction to a given format instance.
        
        :param format_instance: An instance of a document to apply redaction
        :returns: Status of the redaction: success/failure and error message if any'''
        raise NotImplementedError()
    
    @property
    def description(self) -> str:
        '''Returns a string, describing the redaction and its parameters.'''
        raise NotImplementedError()
    
    @property
    def action_options(self) -> groupdocs.redaction.redactions.ReplacementOptions:
        '''Gets the :py:class:`groupdocs.redaction.redactions.ReplacementOptions` instance, specifying type of text replacement.'''
        raise NotImplementedError()
    
    @property
    def ocr_connector(self) -> groupdocs.redaction.integration.ocr.IOcrConnector:
        '''Gets the :py:class:`groupdocs.redaction.integration.ocr.IOcrConnector` implementation, required to extract text from graphic content.'''
        raise NotImplementedError()
    
    @ocr_connector.setter
    def ocr_connector(self, value : groupdocs.redaction.integration.ocr.IOcrConnector) -> None:
        '''Sets the :py:class:`groupdocs.redaction.integration.ocr.IOcrConnector` implementation, required to extract text from graphic content.'''
        raise NotImplementedError()
    
    @property
    def filter(self) -> groupdocs.redaction.redactions.CellFilter:
        '''Gets the column and worksheet filter.'''
        raise NotImplementedError()
    

class CellFilter:
    '''Provides an option to limit the scope of a :py:class:`groupdocs.redaction.redactions.CellColumnRedaction` to a worksheet and a column.'''
    
    def __init__(self) -> None:
        '''Initializes a new instance.'''
        raise NotImplementedError()
    
    @property
    def work_sheet_name(self) -> str:
        '''Gets a worksheet name (if applicable).'''
        raise NotImplementedError()
    
    @work_sheet_name.setter
    def work_sheet_name(self, value : str) -> None:
        '''Sets a worksheet name (if applicable).'''
        raise NotImplementedError()
    
    @property
    def work_sheet_index(self) -> int:
        '''Gets a worksheet index (zero-based).'''
        raise NotImplementedError()
    
    @work_sheet_index.setter
    def work_sheet_index(self, value : int) -> None:
        '''Sets a worksheet index (zero-based).'''
        raise NotImplementedError()
    
    @property
    def has_work_sheet_index(self) -> bool:
        '''Gets a value indicating whether the :py:attr:`groupdocs.redaction.redactions.CellFilter.work_sheet_index` is set or not.'''
        raise NotImplementedError()
    
    @property
    def column_index(self) -> int:
        '''Gets a column index (zero-based).'''
        raise NotImplementedError()
    
    @column_index.setter
    def column_index(self, value : int) -> None:
        '''Sets a column index (zero-based).'''
        raise NotImplementedError()
    
    @property
    def NO_INDEX(self) -> int:
        '''Represents a default value for filter, which is -1.'''
        raise NotImplementedError()


class CustomRedactionContext:
    '''Provides context for custom redaction processing.'''
    
    def __init__(self) -> None:
        raise NotImplementedError()
    
    @property
    def page_number(self) -> int:
        '''The page number of the document where the text appears.
        Note: Some document formats may not support page numbers.'''
        raise NotImplementedError()
    
    @page_number.setter
    def page_number(self, value : int) -> None:
        '''The page number of the document where the text appears.
        Note: Some document formats may not support page numbers.'''
        raise NotImplementedError()
    
    @property
    def text(self) -> str:
        '''The original text to be redacted.'''
        raise NotImplementedError()
    
    @text.setter
    def text(self, value : str) -> None:
        '''The original text to be redacted.'''
        raise NotImplementedError()
    

class CustomRedactionResult:
    '''Represents the result of a custom redaction operation.'''
    
    def __init__(self) -> None:
        raise NotImplementedError()
    
    @property
    def apply(self) -> bool:
        '''Indicates whether the redaction should be applied.
        If true, the redacted content will replace the original content.'''
        raise NotImplementedError()
    
    @apply.setter
    def apply(self, value : bool) -> None:
        '''Indicates whether the redaction should be applied.
        If true, the redacted content will replace the original content.'''
        raise NotImplementedError()
    
    @property
    def text(self) -> str:
        '''The redacted version of the text.
        This will replace the original content if Apply is true.'''
        raise NotImplementedError()
    
    @text.setter
    def text(self, value : str) -> None:
        '''The redacted version of the text.
        This will replace the original content if Apply is true.'''
        raise NotImplementedError()
    

class DeleteAnnotationRedaction(groupdocs.redaction.Redaction):
    '''Represents a text redaction that deletes annotations if text is matching given regular expression (optionally deletes all annotations).'''
    
    @overload
    def __init__(self) -> None:
        '''Initializes a new instance of DeleteAnnotationRedaction class, with settings to delete all annotations (matching everything).'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, pattern : str) -> None:
        '''Initializes a new instance of DeleteAnnotationRedaction class, deleting annotations matching given expression.
        
        :param pattern: Regular expression'''
        raise NotImplementedError()
    
    def apply_to(self, format_instance : groupdocs.redaction.integration.DocumentFormatInstance) -> groupdocs.redaction.RedactorLogEntry:
        '''Applies the redaction to a given format instance.
        
        :param format_instance: An instance of a document to apply redaction
        :returns: Status of the redaction: success/failure and error message if any'''
        raise NotImplementedError()
    
    @property
    def description(self) -> str:
        '''Returns a string, describing the redaction and its parameters.'''
        raise NotImplementedError()
    

class EraseMetadataRedaction(MetadataRedaction):
    '''Represents a metadata redaction that erases all metadata or metadata matching specific MetadataFilters from the document.'''
    
    @overload
    def __init__(self) -> None:
        '''Initializes a new instance of EraseMetadataRedaction class, erasing all metadata.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, filter : groupdocs.redaction.redactions.MetadataFilters) -> None:
        '''Initializes a new instance of EraseMetadataRedaction class, erasing metadata, matching specific combination of :py:class:`groupdocs.redaction.redactions.MetadataFilters`.
        
        :param filter: Filter for metadata to erase'''
        raise NotImplementedError()
    
    def apply_to(self, format_instance : groupdocs.redaction.integration.DocumentFormatInstance) -> groupdocs.redaction.RedactorLogEntry:
        '''Applies the redaction to a given format instance.
        
        :param format_instance: An instance of a document to apply redaction
        :returns: Status of the redaction: success/failure and error message if any'''
        raise NotImplementedError()
    
    @property
    def description(self) -> str:
        '''Returns a string, describing the redaction and its parameters.'''
        raise NotImplementedError()
    
    @property
    def filter(self) -> groupdocs.redaction.redactions.MetadataFilters:
        '''Gets the filter, which is used to select all or specific metadata, for example Author or Company.'''
        raise NotImplementedError()
    
    @filter.setter
    def filter(self, value : groupdocs.redaction.redactions.MetadataFilters) -> None:
        '''Sets the filter, which is used to select all or specific metadata, for example Author or Company.'''
        raise NotImplementedError()
    

class ExactPhraseRedaction(TextRedaction):
    '''Represents a text redaction that replaces exact phrase in the document\'s text, case insensitive by default.'''
    
    @overload
    def __init__(self, search_phrase : str, options : groupdocs.redaction.redactions.ReplacementOptions) -> None:
        '''Initializes a new instance of ExactPhraseRedaction class in case insensitive mode.
        
        :param search_phrase: String to search and replace
        :param options: Replacement options (textual, color)'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, search_phrase : str, is_case_sensitive : bool, options : groupdocs.redaction.redactions.ReplacementOptions) -> None:
        '''Initializes a new instance of ExactPhraseRedaction class.
        
        :param search_phrase: String to search and replace
        :param is_case_sensitive: True if case sensitive search is required
        :param options: Replacement options (textual, color)'''
        raise NotImplementedError()
    
    def apply_to(self, format_instance : groupdocs.redaction.integration.DocumentFormatInstance) -> groupdocs.redaction.RedactorLogEntry:
        '''Applies the redaction to a given format instance.
        
        :param format_instance: An instance of a document to apply redaction
        :returns: Status of the redaction: success/failure and error message if any'''
        raise NotImplementedError()
    
    @property
    def description(self) -> str:
        '''Returns a string, describing the redaction and its parameters.'''
        raise NotImplementedError()
    
    @property
    def action_options(self) -> groupdocs.redaction.redactions.ReplacementOptions:
        '''Gets the :py:class:`groupdocs.redaction.redactions.ReplacementOptions` instance, specifying type of text replacement.'''
        raise NotImplementedError()
    
    @property
    def ocr_connector(self) -> groupdocs.redaction.integration.ocr.IOcrConnector:
        '''Gets the :py:class:`groupdocs.redaction.integration.ocr.IOcrConnector` implementation, required to extract text from graphic content.'''
        raise NotImplementedError()
    
    @ocr_connector.setter
    def ocr_connector(self, value : groupdocs.redaction.integration.ocr.IOcrConnector) -> None:
        '''Sets the :py:class:`groupdocs.redaction.integration.ocr.IOcrConnector` implementation, required to extract text from graphic content.'''
        raise NotImplementedError()
    
    @property
    def search_phrase(self) -> str:
        '''Gets the string to search and replace.'''
        raise NotImplementedError()
    
    @property
    def is_case_sensitive(self) -> bool:
        '''Gets a value indicating whether the search is case-sensitive or not.'''
        raise NotImplementedError()
    
    @property
    def is_right_to_left(self) -> bool:
        '''Gets a value indicating if this text is right-to-Left or not, false by default.'''
        raise NotImplementedError()
    
    @is_right_to_left.setter
    def is_right_to_left(self, value : bool) -> None:
        '''Sets a value indicating if this text is right-to-Left or not, false by default.'''
        raise NotImplementedError()
    

class ICustomRedactionHandler:
    '''Provides an interface for implementing custom redaction logic.'''
    
    def redact(self, context : groupdocs.redaction.redactions.CustomRedactionContext) -> groupdocs.redaction.redactions.CustomRedactionResult:
        '''Applies custom redaction to specific document content.
        Currently, this is supported only for PDF :py:class:`groupdocs.redaction.redactions.PageAreaRedaction`.
        Users can define their own redaction logic, such as AI-based redaction,
        which may be more advanced than simple pattern-based methods.
        
        :param context: Contains the document content to be redacted along with related metadata.
        :returns: A :py:class:`groupdocs.redaction.redactions.CustomRedactionResult` indicating whether the redaction should be applied and the modified content.'''
        raise NotImplementedError()
    

class IRedactionCallback:
    '''Defines methods that are required for receiving information on each redaction change and optionally prevent it.'''
    
    def accept_redaction(self, description : groupdocs.redaction.redactions.RedactionDescription) -> bool:
        '''This call is triggered right before applying any redaction to the document and allows to log or forbid it.
        
        :param description: Contains information about particular match type, criteria, text and position
        :returns: Return true to accept or false to decline particular match redaction'''
        raise NotImplementedError()
    

class ImageAreaRedaction(groupdocs.redaction.Redaction):
    '''Represents a redaction that places colored rectangle in given area of an image document.'''
    
    def __init__(self, top_left : Any, options : groupdocs.redaction.redactions.RegionReplacementOptions) -> None:
        '''Initializes a new instance of ImageAreaRedaction class for redacting specific area size.
        
        :param top_left: Top-left area coordinates
        :param options: Area size and color'''
        raise NotImplementedError()
    
    def apply_to(self, format_instance : groupdocs.redaction.integration.DocumentFormatInstance) -> groupdocs.redaction.RedactorLogEntry:
        '''Applies the redaction to a given format instance.
        
        :param format_instance: An instance of a document to apply redaction
        :returns: Status of the redaction: success/failure and error message if any'''
        raise NotImplementedError()
    
    @property
    def description(self) -> str:
        '''Returns a string, describing the redaction and its parameters.'''
        raise NotImplementedError()
    
    @property
    def options(self) -> groupdocs.redaction.redactions.RegionReplacementOptions:
        '''Gets the :py:class:`groupdocs.redaction.redactions.RegionReplacementOptions` options with color and area parameters.'''
        raise NotImplementedError()
    
    @property
    def top_left(self) -> Any:
        '''Gets the top-left position of the area to remove'''
        raise NotImplementedError()
    

class MetadataRedaction(groupdocs.redaction.Redaction):
    '''Represents a base abstract class for document metadata redactions.'''
    
    def apply_to(self, format_instance : groupdocs.redaction.integration.DocumentFormatInstance) -> groupdocs.redaction.RedactorLogEntry:
        '''Applies the redaction to a given format instance.
        
        :param format_instance: An instance of a document to apply redaction
        :returns: Status of the redaction: success/failure and error message if any'''
        raise NotImplementedError()
    
    @property
    def description(self) -> str:
        '''Returns a string, describing the redaction and its parameters.'''
        raise NotImplementedError()
    
    @property
    def filter(self) -> groupdocs.redaction.redactions.MetadataFilters:
        '''Gets the filter, which is used to select all or specific metadata, for example Author or Company.'''
        raise NotImplementedError()
    
    @filter.setter
    def filter(self, value : groupdocs.redaction.redactions.MetadataFilters) -> None:
        '''Sets the filter, which is used to select all or specific metadata, for example Author or Company.'''
        raise NotImplementedError()
    

class MetadataSearchRedaction(MetadataRedaction):
    '''Represents a metadata redaction that searches and redacts metadata using regular expressions, matching keys and/or values.'''
    
    @overload
    def __init__(self, value_pattern : str, replacement : str) -> None:
        '''Initializes a new instance of MetadataSearchRedaction class, using value to match redacted items.
        
        :param value_pattern: Regular expression to search and replace
        :param replacement: Textual replacement'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, value_pattern : str, replacement : str, key_pattern : str) -> None:
        '''Initializes a new instance of MetadataSearchRedaction class, using item name and value to match redacted items.
        
        :param value_pattern: Regular expression to search and replace metadata item value
        :param replacement: Textual replacement
        :param key_pattern: Regular expression to search and replace metadata item name'''
        raise NotImplementedError()
    
    def apply_to(self, format_instance : groupdocs.redaction.integration.DocumentFormatInstance) -> groupdocs.redaction.RedactorLogEntry:
        '''Applies the redaction to a given format instance.
        
        :param format_instance: An instance of a document to apply redaction
        :returns: Status of the redaction: success/failure and error message if any'''
        raise NotImplementedError()
    
    @property
    def description(self) -> str:
        '''Returns a string, describing the redaction and its parameters.'''
        raise NotImplementedError()
    
    @property
    def filter(self) -> groupdocs.redaction.redactions.MetadataFilters:
        '''Gets the filter, which is used to select all or specific metadata, for example Author or Company.'''
        raise NotImplementedError()
    
    @filter.setter
    def filter(self, value : groupdocs.redaction.redactions.MetadataFilters) -> None:
        '''Sets the filter, which is used to select all or specific metadata, for example Author or Company.'''
        raise NotImplementedError()
    
    @property
    def replacement(self) -> str:
        '''Gets the textual replacement value.'''
        raise NotImplementedError()
    

class PageAreaFilter(RedactionFilter):
    '''Represents redaction filter, setting an area within a page of a document to apply redaction.'''
    
    def __init__(self, top_left : Any, size : aspose.pydrawing.Size) -> None:
        '''Initializes a new instance of PageAreaFilter class for redacting specific area.
        
        :param top_left: Top-left area coordinates
        :param size: Area size and color'''
        raise NotImplementedError()
    
    @property
    def rectangle(self) -> Any:
        '''Gets the rectangle (top-left position and size of the area) on a page.'''
        raise NotImplementedError()
    

class PageAreaRedaction(RegexRedaction):
    '''Represents a complex textual redaction that affects text, images and annotations in an area of the page.'''
    
    def apply_to(self, format_instance : groupdocs.redaction.integration.DocumentFormatInstance) -> groupdocs.redaction.RedactorLogEntry:
        '''Applies the redaction to a given format instance.
        
        :param format_instance: An instance of a document to apply redaction
        :returns: Status of the redaction: success/failure and error message if any'''
        raise NotImplementedError()
    
    @property
    def description(self) -> str:
        '''Returns a string, describing the redaction and its parameters.'''
        raise NotImplementedError()
    
    @property
    def action_options(self) -> groupdocs.redaction.redactions.ReplacementOptions:
        '''Gets the :py:class:`groupdocs.redaction.redactions.ReplacementOptions` instance, specifying type of text replacement.'''
        raise NotImplementedError()
    
    @property
    def ocr_connector(self) -> groupdocs.redaction.integration.ocr.IOcrConnector:
        '''Gets the :py:class:`groupdocs.redaction.integration.ocr.IOcrConnector` implementation, required to extract text from graphic content.'''
        raise NotImplementedError()
    
    @ocr_connector.setter
    def ocr_connector(self, value : groupdocs.redaction.integration.ocr.IOcrConnector) -> None:
        '''Sets the :py:class:`groupdocs.redaction.integration.ocr.IOcrConnector` implementation, required to extract text from graphic content.'''
        raise NotImplementedError()
    
    @property
    def image_options(self) -> groupdocs.redaction.redactions.RegionReplacementOptions:
        '''Gets the :py:class:`groupdocs.redaction.redactions.RegionReplacementOptions` options with color and area parameters.'''
        raise NotImplementedError()
    

class PageRangeFilter(RedactionFilter):
    '''Represents redaction filter, setting page range inside a document to apply redaction.'''
    
    def __init__(self, origin : groupdocs.redaction.redactions.PageSeekOrigin, index : int, count : int) -> None:
        '''Initializes a new instance of RemovePageRedaction class.
        
        :param origin: Seek reference position, the beginning or the end of a document
        :param index: Start position index (0-based)
        :param count: Count of pages to remove'''
        raise NotImplementedError()
    
    @property
    def origin(self) -> groupdocs.redaction.redactions.PageSeekOrigin:
        '''Gets seek reference position, the beginning or the end of a document.'''
        raise NotImplementedError()
    
    @property
    def index(self) -> int:
        '''Gets start position index (0-based).'''
        raise NotImplementedError()
    
    @property
    def count(self) -> int:
        '''Gets the count of pages to remove.'''
        raise NotImplementedError()
    

class RedactionDescription:
    '''Represents a single change action info that performed during redaction process.'''
    
    @overload
    def __init__(self, redaction_type : groupdocs.redaction.redactions.RedactionType, action_type : groupdocs.redaction.redactions.RedactionActionType, original_text : str) -> None:
        '''Initializes a new instance of RedactionDescription class without replacement information.
        
        :param redaction_type: Type of data being redacted
        :param action_type: Action to be performed on these data
        :param original_text: Matched text, comment or annotation body'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, redaction_type : groupdocs.redaction.redactions.RedactionType, action_type : groupdocs.redaction.redactions.RedactionActionType, original_text : str, replacement : groupdocs.redaction.redactions.TextReplacement) -> None:
        '''Initializes a new instance of RedactionDescription class with replacement information.
        
        :param redaction_type: Type of data being redacted
        :param action_type: Action to be performed on these data
        :param original_text: Matched text, comment or annotation body
        :param replacement: Replacement text, matched text and its position within original string'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, redaction_type : groupdocs.redaction.redactions.RedactionType, action_type : groupdocs.redaction.redactions.RedactionActionType, image_area_replacement : groupdocs.redaction.redactions.RegionReplacementOptions, image_details : str) -> None:
        '''Initializes a new instance of RedactionDescription class with image area replacement information.
        
        :param redaction_type: Type of data being redacted
        :param action_type: Action to be performed on these data
        :param image_area_replacement: Image area replacement information
        :param image_details: Image textual description, by default it is String.Empty'''
        raise NotImplementedError()
    
    @property
    def redaction_type(self) -> groupdocs.redaction.redactions.RedactionType:
        '''Gets the type of document\'s data - text, metadata or annotations.'''
        raise NotImplementedError()
    
    @property
    def action_type(self) -> groupdocs.redaction.redactions.RedactionActionType:
        '''Gets the redaction operation: replacement, cleanup or deletion.'''
        raise NotImplementedError()
    
    @property
    def original_text(self) -> str:
        '''Gets the matched text, if any expression is provided.'''
        raise NotImplementedError()
    
    @property
    def replacement(self) -> groupdocs.redaction.redactions.TextReplacement:
        '''Gets the replacement information, can be null.'''
        raise NotImplementedError()
    
    @property
    def image_area_replacement(self) -> groupdocs.redaction.redactions.RegionReplacementOptions:
        '''Gets the replacement information for image area redactions, returns null for textual redactions.'''
        raise NotImplementedError()
    
    @property
    def details(self) -> str:
        '''Gets an optional details information for the item being redacted.'''
        raise NotImplementedError()
    
    @details.setter
    def details(self, value : str) -> None:
        '''Sets an optional details information for the item being redacted.'''
        raise NotImplementedError()
    

class RedactionFilter:
    '''Represents redaction filter, setting scope inside a document to apply redactions.'''
    

class RegexRedaction(TextRedaction):
    '''Represents a text redaction that searches and replaces text in the document by matching provided regular expression.'''
    
    def __init__(self, pattern : str, options : groupdocs.redaction.redactions.ReplacementOptions) -> None:
        '''Initializes a new instance of RegexRedaction class.
        
        :param pattern: Regular expression to search and replace
        :param options: Replacement options (textual, color)'''
        raise NotImplementedError()
    
    def apply_to(self, format_instance : groupdocs.redaction.integration.DocumentFormatInstance) -> groupdocs.redaction.RedactorLogEntry:
        '''Applies the redaction to a given format instance.
        
        :param format_instance: An instance of a document to apply redaction
        :returns: Status of the redaction: success/failure and error message if any'''
        raise NotImplementedError()
    
    @property
    def description(self) -> str:
        '''Returns a string, describing the redaction and its parameters.'''
        raise NotImplementedError()
    
    @property
    def action_options(self) -> groupdocs.redaction.redactions.ReplacementOptions:
        '''Gets the :py:class:`groupdocs.redaction.redactions.ReplacementOptions` instance, specifying type of text replacement.'''
        raise NotImplementedError()
    
    @property
    def ocr_connector(self) -> groupdocs.redaction.integration.ocr.IOcrConnector:
        '''Gets the :py:class:`groupdocs.redaction.integration.ocr.IOcrConnector` implementation, required to extract text from graphic content.'''
        raise NotImplementedError()
    
    @ocr_connector.setter
    def ocr_connector(self, value : groupdocs.redaction.integration.ocr.IOcrConnector) -> None:
        '''Sets the :py:class:`groupdocs.redaction.integration.ocr.IOcrConnector` implementation, required to extract text from graphic content.'''
        raise NotImplementedError()
    

class RegionReplacementOptions:
    '''Represents color and area parameters for image region replacement. See :py:class:`groupdocs.redaction.redactions.ImageAreaRedaction`.'''
    
    @overload
    def __init__(self, fill_color : aspose.pydrawing.Color, size : aspose.pydrawing.Size) -> None:
        '''Initializes a new instance of RegionReplacementOptions class.
        
        :param fill_color: Color to fill the area
        :param size: Filled area size'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, fill_color : aspose.pydrawing.Color, font : Any, expected_text : str) -> None:
        '''Initializes a new instance of RegionReplacementOptions class which size matches given text.
        
        :param fill_color: Color to fill the area
        :param font: Expected text font
        :param expected_text: Expected text'''
        raise NotImplementedError()
    
    @property
    def fill_color(self) -> aspose.pydrawing.Color:
        '''Gets the color to fill the redacted area.'''
        raise NotImplementedError()
    
    @fill_color.setter
    def fill_color(self, value : aspose.pydrawing.Color) -> None:
        '''Sets the color to fill the redacted area.'''
        raise NotImplementedError()
    
    @property
    def size(self) -> aspose.pydrawing.Size:
        '''Gets the rectangle with and height.'''
        raise NotImplementedError()
    
    @size.setter
    def size(self, value : aspose.pydrawing.Size) -> None:
        '''Sets the rectangle with and height.'''
        raise NotImplementedError()
    

class RemovePageRedaction(groupdocs.redaction.Redaction):
    '''Represents a redaction that removes a page (slide, worksheet, etc.) from a document.'''
    
    def __init__(self, origin : groupdocs.redaction.redactions.PageSeekOrigin, index : int, count : int) -> None:
        '''Initializes a new instance of RemovePageRedaction class.
        
        :param origin: Seek reference position, the beginning or the end of a document
        :param index: Start position index (0-based)
        :param count: Count of pages to remove'''
        raise NotImplementedError()
    
    def apply_to(self, format_instance : groupdocs.redaction.integration.DocumentFormatInstance) -> groupdocs.redaction.RedactorLogEntry:
        '''Applies the redaction to a given format instance.
        
        :param format_instance: An instance of a document to apply redaction
        :returns: Status of the redaction: success/failure and error message if any'''
        raise NotImplementedError()
    
    @property
    def description(self) -> str:
        '''Returns a string, describing the redaction and its parameters.'''
        raise NotImplementedError()
    
    @property
    def origin(self) -> groupdocs.redaction.redactions.PageSeekOrigin:
        '''Gets seek reference position, the beginning or the end of a document.'''
        raise NotImplementedError()
    
    @property
    def index(self) -> int:
        '''Gets start position index (0-based).'''
        raise NotImplementedError()
    
    @property
    def count(self) -> int:
        '''Gets the count of pages to remove.'''
        raise NotImplementedError()
    

class ReplacementOptions:
    '''Represents options for matched text replacement.'''
    
    @overload
    def __init__(self, replacement : str) -> None:
        '''Initializes a new instance of ReplacementOptions class with replacement text as an option.
        
        :param replacement: Textual replacement'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, color : aspose.pydrawing.Color) -> None:
        '''Initializes a new instance of ReplacementOptions class with colored rectangle as an option.
        
        :param color: Rectangle color'''
        raise NotImplementedError()
    
    @property
    def action_type(self) -> groupdocs.redaction.redactions.ReplacementType:
        '''Gets the replacement action: draw box or replace text.'''
        raise NotImplementedError()
    
    @property
    def replacement(self) -> str:
        '''Gets the textual replacement value.'''
        raise NotImplementedError()
    
    @replacement.setter
    def replacement(self, value : str) -> None:
        '''Sets the textual replacement value.'''
        raise NotImplementedError()
    
    @property
    def box_color(self) -> aspose.pydrawing.Color:
        '''Gets the color for a :py:attr:`groupdocs.redaction.redactions.ReplacementType.DRAW_BOX` option (ignored otherwise).'''
        raise NotImplementedError()
    
    @box_color.setter
    def box_color(self, value : aspose.pydrawing.Color) -> None:
        '''Sets the color for a :py:attr:`groupdocs.redaction.redactions.ReplacementType.DRAW_BOX` option (ignored otherwise).'''
        raise NotImplementedError()
    
    @property
    def filters(self) -> List[groupdocs.redaction.redactions.RedactionFilter]:
        '''Gets an array of filters to apply with this redaction.'''
        raise NotImplementedError()
    
    @filters.setter
    def filters(self, value : List[groupdocs.redaction.redactions.RedactionFilter]) -> None:
        '''Sets an array of filters to apply with this redaction.'''
        raise NotImplementedError()
    
    @property
    def custom_redaction(self) -> groupdocs.redaction.redactions.ICustomRedactionHandler:
        '''Gets a custom redaction :py:class:`groupdocs.redaction.redactions.ICustomRedactionHandler` handler that allows users to define their own redaction logic.'''
        raise NotImplementedError()
    
    @custom_redaction.setter
    def custom_redaction(self, value : groupdocs.redaction.redactions.ICustomRedactionHandler) -> None:
        '''Sets a custom redaction :py:class:`groupdocs.redaction.redactions.ICustomRedactionHandler` handler that allows users to define their own redaction logic.'''
        raise NotImplementedError()
    

class TextRedaction(groupdocs.redaction.Redaction):
    '''Represents a base abstract class for document text redactions.'''
    
    def apply_to(self, format_instance : groupdocs.redaction.integration.DocumentFormatInstance) -> groupdocs.redaction.RedactorLogEntry:
        '''Applies the redaction to a given format instance.
        
        :param format_instance: An instance of a document to apply redaction
        :returns: Status of the redaction: success/failure and error message if any'''
        raise NotImplementedError()
    
    @property
    def description(self) -> str:
        '''Returns a string, describing the redaction and its parameters.'''
        raise NotImplementedError()
    
    @property
    def action_options(self) -> groupdocs.redaction.redactions.ReplacementOptions:
        '''Gets the :py:class:`groupdocs.redaction.redactions.ReplacementOptions` instance, specifying type of text replacement.'''
        raise NotImplementedError()
    
    @property
    def ocr_connector(self) -> groupdocs.redaction.integration.ocr.IOcrConnector:
        '''Gets the :py:class:`groupdocs.redaction.integration.ocr.IOcrConnector` implementation, required to extract text from graphic content.'''
        raise NotImplementedError()
    
    @ocr_connector.setter
    def ocr_connector(self, value : groupdocs.redaction.integration.ocr.IOcrConnector) -> None:
        '''Sets the :py:class:`groupdocs.redaction.integration.ocr.IOcrConnector` implementation, required to extract text from graphic content.'''
        raise NotImplementedError()
    

class TextReplacement:
    '''Represents a textual replacement information.'''
    
    def __init__(self, index : int, original : str, replacement : str) -> None:
        '''Initializes a new instance of TextReplacement class.
        
        :param index: Index of a matched text within source string
        :param original: Original matched string
        :param replacement: String, replacing OriginalText in source string'''
        raise NotImplementedError()
    
    @property
    def index(self) -> int:
        '''Gets an index of the matched text within source string.'''
        raise NotImplementedError()
    
    @property
    def original_text(self) -> str:
        '''Gets the original matched string.'''
        raise NotImplementedError()
    
    @property
    def replacement(self) -> str:
        '''Gets the string, replacing OriginalText.'''
        raise NotImplementedError()
    

class MetadataFilters:
    '''Represents a list of the most common types of document metadata.'''
    
    NONE : MetadataFilters
    '''Empty filter setting, matches no metadata items.'''
    AUTHOR : MetadataFilters
    '''Author of the document.'''
    CATEGORY : MetadataFilters
    '''Category of the document.'''
    COMMENTS : MetadataFilters
    '''Comment for the document.'''
    COMPANY : MetadataFilters
    '''Company of the Author.'''
    CONTENT_STATUS : MetadataFilters
    '''Content status.'''
    CREATED_TIME : MetadataFilters
    '''Created time.'''
    HYPERLINK_BASE : MetadataFilters
    '''Hyperlink base.'''
    LAST_PRINTED : MetadataFilters
    '''Last printed date and time.'''
    LAST_SAVED_BY : MetadataFilters
    '''Last saved by user.'''
    LAST_SAVED_TIME : MetadataFilters
    '''Last saved date and time.'''
    NAME_OF_APPLICATION : MetadataFilters
    '''Name of application where the document was created.'''
    MANAGER : MetadataFilters
    '''Author\'s manager name.'''
    REVISION_NUMBER : MetadataFilters
    '''Revision number.'''
    SUBJECT : MetadataFilters
    '''Subject of the document.'''
    TEMPLATE : MetadataFilters
    '''Document template name.'''
    TITLE : MetadataFilters
    '''Document title.'''
    TOTAL_EDITING_TIME : MetadataFilters
    '''Total editing time.'''
    VERSION : MetadataFilters
    '''Document\'s version.'''
    DESCRIPTION : MetadataFilters
    '''Document\'s description.'''
    KEYWORDS : MetadataFilters
    '''Document\'s keywords.'''
    CONTENT_TYPE : MetadataFilters
    '''Content type.'''
    ALL : MetadataFilters
    '''All types of the metadata items.'''

class PageSeekOrigin:
    '''Provides the fields that represent reference points in a document for seeking.'''
    
    BEGIN : PageSeekOrigin
    '''Specifies the beginning of a document.'''
    END : PageSeekOrigin
    '''Specifies the end of a document.'''

class RedactionActionType:
    '''Represents actions that can be taken to perform redaction.'''
    
    REPLACEMENT : RedactionActionType
    '''Redacted text was replaced with another or covered with a block.'''
    CLEANUP : RedactionActionType
    '''Data were removed, but an empty object remains in the document.'''
    DELETION : RedactionActionType
    '''Data and related structures were removed from the document.'''

class RedactionType:
    '''Represents a type of document\'s data, affected by redaction.'''
    
    TEXT : RedactionType
    '''The document\'s body text.'''
    METADATA : RedactionType
    '''The document\'s metadata.'''
    ANNOTATION : RedactionType
    '''The annotations within document\'s text.'''
    IMAGE_AREA : RedactionType
    '''The area within an image.'''
    PAGE : RedactionType
    '''The page of a document.'''

class ReplacementType:
    '''Represents a type of replacement for the matched text.'''
    
    REPLACE_STRING : ReplacementType
    '''Replaces matched text with another string, for instance exemption code.'''
    DRAW_BOX : ReplacementType
    '''Draws a rectangle of specific color (Black by default) instead of redacted text.'''

