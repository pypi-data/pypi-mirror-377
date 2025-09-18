#!/usr/bin/env python3
"""
Frontend Entry Point for Agent Team Chat

This module provides the main entry point for the web frontend.
"""

import os
import sys
import json
import asyncio
from datetime import datetime
from typing import Dict, Any, List
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pkg_resources

from .database import Database
from .tools import (
    ToolContext, create_project, list_projects, send_message,
    get_recent_messages, set_agent_status, get_agent_status,
    search_docs, register_doc, get_project_summary, upload_image_base64
)

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    CORS(app)  # Enable CORS for frontend communication

    # Initialize database and context
    DB_PATH = os.environ.get('ATC_DB_PATH', './agent_team_chat.db')
    IMAGE_DIR = os.environ.get('ATC_IMAGE_DIR', './images')

    db = Database(DB_PATH)
    ctx = ToolContext(db=db, image_dir=IMAGE_DIR)

    # Ensure images directory exists
    os.makedirs(IMAGE_DIR, exist_ok=True)

    @app.route('/')
    def serve_frontend():
        """Serve the main HTML interface"""
        try:
            # Get frontend files from package data
            frontend_path = pkg_resources.resource_filename('agent_team_chat', 'frontend_files')
            return send_from_directory(frontend_path, 'index.html')
        except:
            # Fallback if package data not available
            return """
            <!DOCTYPE html>
            <html>
            <head><title>Agent Team Chat</title></head>
            <body>
                <h1>Agent Team Chat Frontend</h1>
                <p>Frontend files not found. Please run from development directory or reinstall package.</p>
                <p>API endpoints are available at /api/*</p>
            </body>
            </html>
            """

    @app.route('/<path:filename>')
    def serve_static(filename):
        """Serve static frontend files"""
        try:
            frontend_path = pkg_resources.resource_filename('agent_team_chat', 'frontend_files')
            return send_from_directory(frontend_path, filename)
        except:
            return "File not found", 404

    @app.route('/api/projects', methods=['GET'])
    def get_projects():
        """Get all projects"""
        try:
            result = list_projects(ctx)
            if result["success"]:
                return jsonify({
                    "success": True,
                    "projects": result["projects"]
                })
            else:
                return jsonify(result), 500
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/projects', methods=['POST'])
    def create_new_project():
        """Create a new project"""
        try:
            data = request.get_json()
            name = data.get('name', '').strip()
            description = data.get('description', '')

            if not name:
                return jsonify({"success": False, "error": "Project name is required"}), 400

            result = create_project(ctx, name=name, description=description)
            return jsonify(result)
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/projects/<int:project_id>/messages', methods=['GET'])
    def get_messages(project_id):
        """Get recent messages for a project"""
        try:
            limit = request.args.get('limit', 50, type=int)
            result = get_recent_messages(ctx, project_id=project_id, limit=limit)

            if result["success"]:
                # Add agent type information
                for message in result["messages"]:
                    message["is_agent"] = message["agent"] != "human_operator"

                return jsonify(result)
            else:
                return jsonify(result), 500
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/projects/<int:project_id>/messages', methods=['POST'])
    def send_new_message(project_id):
        """Send a new message to a project"""
        try:
            data = request.get_json()
            content = data.get('content', '').strip()
            agent = data.get('agent', 'human_operator')
            role = data.get('role', 'user')

            if not content:
                return jsonify({"success": False, "error": "Message content is required"}), 400

            result = send_message(
                ctx,
                project_id=project_id,
                agent=agent,
                role=role,
                content=content
            )
            return jsonify(result)
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/projects/<int:project_id>/summary', methods=['GET'])
    def get_project_summary_api(project_id):
        """Get project summary/digest"""
        try:
            result = get_project_summary(ctx, project_id=project_id)
            return jsonify(result)
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/agents', methods=['GET'])
    def get_agent_statuses():
        """Get status of all agents"""
        try:
            # Get all projects to find agents
            projects_result = list_projects(ctx)
            if not projects_result["success"]:
                return jsonify({"success": False, "error": "Failed to get projects"}), 500

            all_agents = set()
            agent_statuses = []

            # Collect agent names from all projects
            for project in projects_result["projects"]:
                messages_result = get_recent_messages(ctx, project_id=project["id"], limit=100)
                if messages_result["success"]:
                    for message in messages_result["messages"]:
                        if message["agent"] != "human_operator":
                            all_agents.add(message["agent"])

            # Get status for each agent
            for agent_name in all_agents:
                # Try to get status from any project (agents are global)
                project_id = projects_result["projects"][0]["id"] if projects_result["projects"] else 1
                status_result = get_agent_status(ctx, project_id=project_id, agent=agent_name)

                if status_result["success"]:
                    agent_info = status_result["status"]
                    agent_info["name"] = agent_name
                    agent_info["is_agent"] = True

                    # Determine specialization based on name
                    specializations = {
                        "APISpecialist": "Backend APIs",
                        "SecurityAuditor": "Security Review",
                        "UIExpert": "Frontend UI",
                        "DataAnalyst": "Data Processing",
                        "DevOpsBot": "CI/CD Pipeline",
                        "AuthExpert": "Authentication",
                        "DBAdmin": "Database Management"
                    }
                    agent_info["specialization"] = specializations.get(agent_name, "General AI")

                    agent_statuses.append(agent_info)

            return jsonify({
                "success": True,
                "agents": agent_statuses
            })
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/docs/search', methods=['GET'])
    def search_documentation():
        """Search documentation"""
        try:
            query = request.args.get('query', '').strip()
            if not query:
                return jsonify({"success": True, "results": []})

            result = search_docs(ctx, query=query)
            return jsonify(result)
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        try:
            # Test database connection
            projects = list_projects(ctx)
            return jsonify({
                "success": True,
                "status": "healthy",
                "database": "connected",
                "projects_count": len(projects.get("projects", [])) if projects["success"] else 0
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "status": "unhealthy",
                "error": str(e)
            }), 500

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"success": False, "error": "Endpoint not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"success": False, "error": "Internal server error"}), 500

    return app

def main():
    """Main entry point for the web frontend"""
    print("🌐 Starting Agent Team Chat Web Frontend...")

    # Get configuration from environment
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', '5000'))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

    db_path = os.environ.get('ATC_DB_PATH', './agent_team_chat.db')
    image_dir = os.environ.get('ATC_IMAGE_DIR', './images')

    print(f"📊 Database: {db_path}")
    print(f"🖼️  Images: {image_dir}")
    print(f"🚀 Frontend: http://{host}:{port}")
    print(f"📡 API: http://{host}:{port}/api/*")

    # Initialize sample documentation if needed
    try:
        from .database import Database
        from .tools import ToolContext, search_docs, register_doc

        db = Database(db_path)
        ctx = ToolContext(db=db, image_dir=image_dir)

        # Add sample documentation if empty
        docs_result = search_docs(ctx, query="agent")
        if docs_result["success"] and not docs_result["results"]:
            print("📚 Adding sample documentation...")
            register_doc(ctx,
                title="Agent Team Chat User Guide",
                text="""
                # Agent Team Chat User Guide

                ## Getting Started
                1. Select a project from the sidebar
                2. Start typing messages to communicate with AI agents
                3. Agents will automatically respond based on their specializations

                ## Agent Types
                - **APISpecialist**: Backend API development and integration
                - **SecurityAuditor**: Security reviews and vulnerability assessments
                - **UIExpert**: Frontend user interface design and implementation
                - **DataAnalyst**: Data processing and analysis
                - **DevOpsBot**: CI/CD pipeline and deployment automation

                ## Cross-Codebase Discovery
                Agents use intelligent relevance scoring to find the most appropriate
                conversations across different projects and codebases.
                """,
                source="system"
            )
            print("✅ Sample documentation added")

    except Exception as e:
        print(f"⚠️  Documentation setup warning: {e}")

    # Create and run the app
    app = create_app()

    print("\nPress Ctrl+C to stop the server")
    print("=" * 50)

    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    main()