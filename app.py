from flask import Flask, request, send_file
import pypandoc
import os
import tempfile
import logging
import pdfkit

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
)

app = Flask(__name__)
logger = logging.getLogger(__name__)

# Add health check endpoint (recommended for App Runner)
@app.route('/health')
def health_check():
    return {'status': 'healthy'}, 200

@app.route("/convert", methods=["POST"])
def convert_to_pdf():
    logger.info("Received conversion request")
    
    # Check if file was uploaded
    if 'file' not in request.files:
        logger.error("No file part in request")
        return "No file uploaded", 400
        
    uploaded_file = request.files['file']
    
    if uploaded_file.filename == '':
        logger.error("Empty filename in upload")
        return "No selected file", 400

    try:
        # Save uploaded file directly
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as temp_input:
            temp_input.write(uploaded_file.read())
            input_path = temp_input.name
            logger.debug(f"Saved uploaded file to {input_path}")

        # Create output temp file
        output_path = tempfile.mktemp(suffix=".pdf")
        
        # Convert using pandoc
        logger.info("Starting document conversion")
        
        # Convert DOCX -> HTML
        html_content = pypandoc.convert_file(input_path, 'html', format='docx')

        # Convert HTML -> PDF using pdfkit with options to prevent network errors
        options = {
            'quiet': '',
            'no-images': '',
            'disable-external-links': '',
            'disable-javascript': '',
            'encoding': 'UTF-8'
        }
        pdfkit.from_string(html_content, output_path, options=options)
        
        logger.info(f"Conversion successful. Output PDF: {output_path}")

        return send_file(
            output_path,
            mimetype="application/pdf",
            as_attachment=True,
            download_name="converted.pdf"
        )

    except Exception as e:
        logger.error(f"Conversion failed: {str(e)}", exc_info=True)
        return f"Error: {str(e)}", 500
        
    finally:
        # Cleanup temp files
        if 'input_path' in locals() and os.path.exists(input_path):
            logger.debug(f"Cleaning up input file: {input_path}")
            os.remove(input_path)
        if 'output_path' in locals() and os.path.exists(output_path):
            logger.debug(f"Cleaning up PDF file: {output_path}")
            os.remove(output_path)

if __name__ == "__main__":
    # Modified to work better in containerized environment
    app.run(host='0.0.0.0', port=8080)
