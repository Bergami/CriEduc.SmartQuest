# Changelog

## [Unreleased] - 2024-12-17

### ✅ Added
- **Header Image Support**: Automatic categorization and extraction of images from document headers
  - Added `images` array to `document_metadata` in API response
  - Implemented position-based image categorization using PyMuPDF
  - Images are base64-encoded with position metadata (x, y, width, height)
  
- **Storage Architecture**: Provider-agnostic storage service for future database migration
  - Created `DocumentStorageService` for generic document artifact storage
  - Implemented `BaseDocumentProvider` abstract class for extensibility
  - Added storage methods for responses, images, text, and original documents

### 🛠️ Changed
- **Refactored Azure Service**: Updated `AzureDocumentIntelligenceService` to inherit from `BaseDocumentProvider`
- **Enhanced AnalyzeService**: Added image categorization logic with `_is_header_image()` method
- **Updated HeaderParser**: Modified to accept optional `header_images` parameter
- **Improved Documentation**: Updated ARCHITECTURE.md and README.md with new features

### 🗑️ Removed
- **Unused Schemas**: Removed `upload.py` schemas that were not being used anywhere in the codebase
- **Obsolete Code**: Cleaned up unused imports and deprecated code sections

### 🔧 Technical Details
- **Image Categorization Logic**: Uses Y-position with 20% threshold for header vs content classification
- **Provider Pattern**: Implemented factory pattern for easy addition of new document providers
- **Storage Abstraction**: Separated storage concerns from document analysis logic
- **Future-Ready**: Architecture prepared for database storage migration

### 📊 API Changes
- **New Response Field**: Added `images` array to `document_metadata`
- **Enhanced Metadata**: Images include position data and base64 content
- **Backward Compatibility**: Existing API responses remain unchanged when no header images are present

### 🧪 Testing
- **Image Categorization**: Tested with manual debugging and position verification
- **Storage Integration**: Verified new storage service architecture
- **API Compatibility**: Ensured backward compatibility with existing responses

### 📝 Documentation Updates
- **ARCHITECTURE.md**: Added storage architecture section and updated component descriptions
- **README.md**: Enhanced with new features, tech stack updates, and improved project structure
- **Code Comments**: Added comprehensive documentation for new image processing methods

---

## Previous Versions

### Initial Release
- Basic document processing with Azure Document Intelligence
- Header parsing with modular field extraction
- Question and context block detection
- Context-question mapping algorithms
- FastAPI-based REST API
- Comprehensive test suite
