from flask import Blueprint, request, jsonify
from typing import Optional

from src.models.schemas import (
    QuestionRequest,
    QuestionResponse,
    ChangeRequest,
    ChangeValidationResponse,
    ImpactAssessment,
    DecisionResponse
)
from src.services.analysis_service import AnalysisService
from src.services.repository_service import RepositoryService
from src.utils.logger import get_logger
from pydantic import ValidationError

logger = get_logger()
bp = Blueprint("api", __name__, url_prefix="/api/v1")

# Initialize services
analysis_service = AnalysisService()
repository_service = RepositoryService()


def validate_request(schema_class, data):
    """Validate request data against Pydantic schema"""
    try:
        return schema_class(**data)
    except ValidationError as e:
        raise ValueError(f"Validation error: {e.json()}")


@bp.route("/question", methods=["POST"])
def ask_question():
    """Answer architecture or framework questions about the repository"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        request_obj = validate_request(QuestionRequest, data)
        response = analysis_service.answer_question(request_obj)
        return jsonify(response.model_dump()), 200
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error answering question: {e}")
        return jsonify({"error": f"Failed to answer question: {str(e)}"}), 500


@bp.route("/validate", methods=["POST"])
def validate_change():
    """Validate a change request or feature proposal"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        request_obj = validate_request(ChangeRequest, data)
        response = analysis_service.validate_change(request_obj)
        return jsonify(response.model_dump()), 200
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error validating change: {e}")
        return jsonify({"error": f"Failed to validate change: {str(e)}"}), 500


@bp.route("/impact", methods=["POST"])
def analyze_impact():
    """Analyze impact of a change request"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        request_obj = validate_request(ChangeRequest, data)
        response = analysis_service.analyze_impact(request_obj)
        return jsonify(response.model_dump()), 200
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error analyzing impact: {e}")
        return jsonify({"error": f"Failed to analyze impact: {str(e)}"}), 500


@bp.route("/analyze", methods=["POST"])
def full_analysis():
    """Perform full analysis: validation + impact + decision"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        request_obj = validate_request(ChangeRequest, data)
        response = analysis_service.full_analysis(request_obj)
        return jsonify(response.model_dump()), 200
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error performing full analysis: {e}")
        return jsonify({"error": f"Failed to perform analysis: {str(e)}"}), 500


@bp.route("/index", methods=["POST"])
def index_repository():
    """
    Index a repository for analysis
    
    Accepts:
    - Local file path: {"repository_path": "/path/to/repo"}
    - GitHub URL: {"repository_path": "https://github.com/user/repo"}
    - PDF file path: {"repository_path": "/path/to/file.pdf"}
    """
    try:
        data = request.get_json()
        if not data or "repository_path" not in data:
            return jsonify({"error": "repository_path is required"}), 400
        
        repository_path = data["repository_path"]
        cleanup = data.get("cleanup", True)  # Default to cleanup temp dirs
        
        logger.info(f"Indexing request: {repository_path}")
        
        # Validate path exists (unless it's a GitHub URL)
        if not repository_path.startswith("http"):
            from pathlib import Path
            if not Path(repository_path).exists():
                return jsonify({
                    "error": f"Path does not exist: {repository_path}",
                    "hint": "Please provide a valid file or directory path"
                }), 400
        
        try:
            success = repository_service.index_repository(repository_path, cleanup=cleanup)
            
            if success:
                source_type = "GitHub URL" if "github.com" in repository_path.lower() else (
                    "PDF file" if repository_path.lower().endswith('.pdf') else "Local path"
                )
                return jsonify({
                    "status": "success",
                    "message": f"Successfully indexed: {repository_path}",
                    "source": source_type
                }), 200
            else:
                return jsonify({
                    "error": "Failed to index repository. Check logs for details.",
                    "hint": "Ensure the path is correct and contains indexable files"
                }), 500
        except Exception as e:
            logger.error(f"Error during indexing: {e}", exc_info=True)
            return jsonify({
                "error": f"Indexing failed: {str(e)}",
                "details": "Check server logs for more information"
            }), 500
            
    except Exception as e:
        logger.error(f"Error in index endpoint: {e}", exc_info=True)
        return jsonify({"error": f"Failed to process request: {str(e)}"}), 500


@bp.route("/index/file", methods=["POST"])
def index_file():
    """
    Index a single file (e.g., PDF)
    
    Accepts multipart/form-data with 'file' field
    """
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Save uploaded file temporarily
        import tempfile
        import os
        temp_dir = tempfile.mkdtemp(prefix="uploaded_file_")
        file_path = os.path.join(temp_dir, file.filename)
        file.save(file_path)
        
        logger.info(f"Indexing uploaded file: {file.filename}")
        success = repository_service.index_repository(file_path, cleanup=True)
        
        # Cleanup temp file
        try:
            os.remove(file_path)
            os.rmdir(temp_dir)
        except:
            pass
        
        if success:
            return jsonify({
                "status": "success",
                "message": f"Successfully indexed file: {file.filename}"
            }), 200
        else:
            return jsonify({"error": "Failed to index file"}), 500
            
    except Exception as e:
        logger.error(f"Error indexing file: {e}", exc_info=True)
        return jsonify({"error": f"Failed to index file: {str(e)}"}), 500


@bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "repository-intelligence"}), 200

