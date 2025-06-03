# Clean version of the iframe view

from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.views.decorators.csrf import csrf_exempt
from services.supporting_codes.resume_support_code import create_experienced_resume, create_fresher_resume


@xframe_options_sameorigin
@csrf_exempt
def template_preview_iframe(request, template_id):
    """
    Iframe-friendly template preview that won't be blocked
    """
    try:
        # Use appropriate sample data based on template
        if template_id == '6' or template_id == 6:
            sample_resume = create_fresher_resume()
        else:
            sample_resume = create_experienced_resume()

        # Extract template number
        template_id_str = str(template_id)
        if template_id_str.startswith('template'):
            template_number = template_id_str.replace('template', '')
        else:
            template_number = template_id_str

        # Render the template
        template_path = f'resumes/templates/template{template_number}.html'
        response = render(request, template_path, {'resume': sample_resume})

        # Set headers to allow iframe embedding
        response['X-Frame-Options'] = 'SAMEORIGIN'
        response['Content-Security-Policy'] = "frame-ancestors 'self'"

        return response

    except Exception as e:
        # Clean error page
        error_html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Template Preview</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    padding: 40px;
                    text-align: center;
                    background: #f8f9fa;
                    color: #333;
                }}
                .error-container {{
                    background: white;
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    max-width: 500px;
                    margin: 0 auto;
                }}
                .error-icon {{
                    font-size: 48px;
                    color: #dc3545;
                    margin-bottom: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="error-container">
                <div class="error-icon">📄</div>
                <h2>Template Preview Unavailable</h2>
                <p>Template {template_number} could not be loaded.</p>
                <p style="color: #666; font-size: 14px;">
                    Please ensure the template file exists.
                </p>
            </div>
        </body>
        </html>
        """

        response = HttpResponse(error_html)
        response['X-Frame-Options'] = 'SAMEORIGIN'
        response['Content-Security-Policy'] = "frame-ancestors 'self'"
        return response