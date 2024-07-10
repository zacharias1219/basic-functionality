# AI Chatbot Creator

This repository contains the initial part of a comprehensive AI-powered chatbot creation platform. The application allows users to create customizable chatbots by selecting AI models, configuring settings, and integrating with various services. Users receive a code snippet to deploy the chatbot on their websites.

## Key Features

1. **AI-Powered Chatbots:**
   - Users can choose between multiple AI models (e.g., GPT-3.5 Turbo, GPT-4).
   - Chatbots are created based on user-specified configurations and settings.

2. **Content Parsing:**
   - The application can parse content from websites, PDFs, and Word documents to enhance chatbot responses.

3. **Integration Capabilities:**
   - Seamless integration with popular CRM systems (e.g., Salesforce, HubSpot).
   - Integration with email marketing platforms (e.g., MailChimp) to automate campaigns.

4. **Lead Generation and Automation:**
   - Chatbots capture visitor information and store leads in integrated CRM systems.
   - Automated email campaigns are triggered based on chatbot interactions.

## Project Structure

```plaintext
chatbot_project/
├── app.py
├── ai.py
├── parser.py
├── integrators/
│   ├── __init__.py
│   ├── salesforce.py
│   ├── hubspot.py
│   ├── mailchimp.py
├── models.py
├── requirements.txt
├── static/
│   └── styles.css
└── templates/
    └── index.html
