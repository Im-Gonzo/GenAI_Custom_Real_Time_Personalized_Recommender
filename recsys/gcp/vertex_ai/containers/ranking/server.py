"""
Server for ranking model in Vertex AI.
Handles HTTP requests for ranking predictions.
"""

import os
import time
import pandas as pd
from flask import Flask, request, jsonify, g
from ranking_transformer import RankingTransformer
from ranking_predictor import RankingPredictor
from logger import logger, RequestContext

# Initialize Flask app
app = Flask(__name__)

# Initialize transformer and predictor
logger.info("🚀 Initializing ranking service components")
predictor = RankingPredictor()
transformer = RankingTransformer()


@app.before_request
def before_request():
    """Set up request context before processing."""
    # Generate and store request ID
    request_id = request.headers.get("X-Request-ID")
    g.request_id = RequestContext.set_request_id(request_id)

    # Track request start time
    g.start_time = time.time()

    # Log request details
    logger.info(f"📥 Received request: {request.method} {request.path}")


@app.after_request
def after_request(response):
    """Log after request is processed."""
    # Calculate request duration
    duration = time.time() - g.start_time

    # Log response
    logger.info(f"📤 Response sent: {response.status_code} (took {duration:.3f}s)")

    return response


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    logger.debug("🏥 Health check requested")
    return jsonify({"status": "healthy"})


@app.route("/predict", methods=["POST"])
def predict():
    """
    Prediction endpoint for ranking model.

    Request format:
    {
        "instances": [
            {
                "customer_id": "d327d0ad9e30085a436933dfbb7f77cf42e38447993a078ed35d93e3fd350ecf",
                "month_sin": 1.2246467991473532e-16,
                "month_cos": -1.0,
                "query_emb": [0.214135289, 0.571055949, 0.330709577, ...]
            }
        ]
    }

    Response format:
    {
        "ranking": [[0.98, "item_1"], [0.75, "item_2"], ...]
    }
    """
    try:
        # Start timing prediction process
        logger.timer_start("prediction_process")

        # Get request data
        request_json = request.get_json()

        # Validate input format
        if not request_json:
            logger.error("❌ Empty request body")
            return jsonify({"error": "Empty request body", "ranking": []}), 400

        if "instances" not in request_json:
            logger.error("❌ Missing 'instances' field in request")
            return jsonify({"error": "Missing 'instances' field", "ranking": []}), 400

        if not request_json["instances"]:
            logger.error("❌ Empty 'instances' array in request")
            return jsonify({"error": "Empty 'instances' array", "ranking": []}), 400

        # Validate required fields
        instance = request_json["instances"][0]
        required_fields = ["customer_id", "month_sin", "month_cos", "query_emb"]

        for field in required_fields:
            if field not in instance:
                logger.error(f"❌ Missing required field: {field}")
                return jsonify(
                    {"error": f"Missing required field: {field}", "ranking": []}
                ), 400

        # Additional validation for types
        if not isinstance(instance["customer_id"], str):
            logger.error("❌ customer_id must be a string")
            return jsonify(
                {"error": "customer_id must be a string", "ranking": []}
            ), 400

        if not isinstance(instance["query_emb"], list):
            logger.error("❌ query_emb must be a list of floats")
            return jsonify(
                {"error": "query_emb must be a list of floats", "ranking": []}
            ), 400

        logger.info(
            f"🧩 Processing prediction for customer: {instance['customer_id'][:8]}..."
        )

        # Start timing preprocessing
        logger.timer_start("preprocessing")
        # Preprocess inputs
        transformed_inputs = transformer.preprocess(request_json)
        logger.timer_end("preprocessing")

        # Check if we got candidates
        features = transformed_inputs["inputs"][0]["ranking_features"]
        if isinstance(features, pd.DataFrame) and features.empty:
            logger.warning("⚠️ No candidate features generated")
            return jsonify({"ranking": []})

        logger.data(f"Generated {len(features)} candidates for ranking")

        # Start timing prediction
        logger.timer_start("model_prediction")
        # Generate predictions
        prediction_result = predictor.predict(transformed_inputs["inputs"])
        logger.timer_end("model_prediction")

        # Start timing postprocessing
        logger.timer_start("postprocessing")
        # Postprocess results
        response = transformer.postprocess(prediction_result)
        logger.timer_end("postprocessing")

        # End timing total prediction process
        logger.timer_end("prediction_process")

        # Return response
        return jsonify(response)

    except ValueError as e:
        # Handle validation errors
        logger.error(f"❌ Validation error: {str(e)}")
        return jsonify({"error": f"Validation error: {str(e)}", "ranking": []}), 400

    except KeyError as e:
        # Handle missing key errors
        logger.error(f"❌ Missing key error: {str(e)}")
        return jsonify({"error": f"Missing key: {str(e)}", "ranking": []}), 400

    except Exception as e:
        # Handle all other errors
        logger.error(f"❌ Error processing request: {str(e)}", exc_info=True)

        # Provide a cleaner error message to the client
        error_type = type(e).__name__
        error_message = str(e)

        return jsonify({"error": f"{error_type}: {error_message}", "ranking": []}), 500


if __name__ == "__main__":
    # Get port from environment variable or use default
    port = int(os.environ.get("AIP_HTTP_PORT", 8080))

    # Set debug mode based on environment variable
    debug_mode = os.environ.get("DEBUG", "False").lower() == "true"

    # Log startup information
    logger.info(f"🚀 Starting ranking service on port {port} (debug={debug_mode})")

    # Run the Flask app
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
