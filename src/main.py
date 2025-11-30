from flask import Flask, jsonify
from flask_cors import CORS

from src.api.routes import bp
from src.utils.logger import get_logger
from src.utils.config import get_settings

logger = get_logger()
settings = get_settings()


def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    
    # CORS configuration
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",  # Configure appropriately for production
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Register blueprints
    app.register_blueprint(bp)
    
    @app.route("/")
    def root():
        """Root endpoint"""
        return jsonify({
            "service": "Repository Intelligence Backend",
            "version": "1.0.0",
            "status": "running"
        })
    
    return app


app = create_app()


if __name__ == "__main__":
    logger.info("Starting Repository Intelligence Backend")
    app.run(
        host="0.0.0.0",
        port=8000,
        debug=True
    )

