import jinja2
import os

class PromptService:
    """
    A service for generating Jinja2 prompts from templates.

    This service centralizes prompt creation logic, allowing for consistent
    prompts across the application using a template inheritance system.
    """
    def __init__(self, template_dirs):
        """
        Initializes the Jinja2 environment with the specified template directories.
        
        Args:
            template_dirs (list): A list of paths to directories containing templates.
        """
        self.loader = jinja2.FileSystemLoader(template_dirs)
        self.env = jinja2.Environment(loader=self.loader)

    def get_prompt(self, template_name, context):
        """
        Loads and renders a specified template with provided context.

        Args:
            template_name (str): The name of the template file to load.
            context (dict): A dictionary of variables to pass to the template.

        Returns:
            str: The rendered prompt.
        """
        try:
            template = self.env.get_template(template_name)
            return template.render(context)
        except jinja2.TemplateNotFound:
            return f"Error: Template '{template_name}' not found."

# --- Usage Example ---
if __name__ == "__main__":
    # Get template paths from environment variables as defined in your .env file
    shared_templates_path = os.getenv('SHARED_TEMPLATES_PATH', '/app/src/oak/prompt/shared_templates')
    prompt_templates_path = os.getenv('PROMPT_TEMPLATES_PATH', '/app/src/oak/prompt/library')
    
    # Ensure the paths are available
    if not shared_templates_path or not prompt_templates_path:
        print("Error: Template paths not set in environment variables.")
        exit(1)

    # Instantiate the service with the template directories
    prompt_service = PromptService(template_dirs=[shared_templates_path, prompt_templates_path])

    # Context data to pass to the template
    data = {
        'user_question': "What is a good stock recommendation for me?",
        'personal_context_html': {
            "user_goals": [
                {"id": 1, "user_id": "00ec53c9-c86a-4fdb-9cd4-9dff79b31392", "name": "Purchase land in the NC Mountains", "target_amount": 150000.0, "target_date": "2030-01-01", "current_amount": 0.0, "created_at": "2025-09-14T23:24:31.774941", "updated_at": "2025-09-14T23:24:31.774941", "status": "active", "image_url": "https://oak-quant.nyc3.digitaloceanspaces.com/goals/1/purchase_land_in_the_nc_mountains_1.png", "image_generation_status": "completed", "image_prompt": "Generate a vibrant, inspiring, and visually appealing **square image** representing the financial goal: 'Purchase land in the NC Mountains'. Focus on positive achievement and future success. Examples could include: a dream home, a graduation cap, a travel destination, a retirement scene, a strong investment portfolio graph. Avoid text and specific currency symbols. Make it aspirational, professional, realistic and memorable. The image should evoke a sense of accomplishment and motivation, suitable for a personal finance application. Ensure the image is square-shaped to fit well in the app's interface. The image should reflect the theme of financial success and personal achievement, without any text or logos. My brand colors are blue and green, so consider using these colors in the image to align with our branding."}
            ], 
            "portfolio_holdings": []
        },
        'knowledge_context': "I have a very high risk threshold."
    }

    # Generate the final prompt using a template named 'sample.jinja2'
    # NOTE: You would need to create a template file named 'sample.jinja2' in your prompt library directory
    # that extends 'base_template.jinja2' for this to work.
    # Example content for sample.jinja2:
    # {% extends 'base_template.jinja2' %}
    # {% block content %}
    # User's Question: {{ user_question }}
    # Context: {{ knowledge_context }}
    # {% endblock %}

    final_prompt = prompt_service.get_prompt('sample.jinja2', data)

    print("--- Final Rendered Prompt ---")
    print(final_prompt)