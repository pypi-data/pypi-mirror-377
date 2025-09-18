#!/usr/bin/env python3
"""
Documentation System Demo

This script demonstrates the DocStation subsystem of Agent Team Chat,
showing how to:

1. Register documentation from text and URLs
2. Automatic chunking for large documents
3. Full-text search across documentation
4. Version management for documents
5. Chunk retrieval for detailed reading

Perfect for teams that need shared knowledge management.
"""

import requests
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_team_chat.database import Database
from agent_team_chat.tools import ToolContext, register_doc, register_doc_url, search_docs, \
    get_doc_chunk, list_docs, list_doc_versions


def demo_documentation_system():
    """Demonstrate documentation features."""
    print("📚 Agent Team Chat Documentation System Demo")
    print("=" * 60)

    # Setup
    db = Database(":memory:")
    ctx = ToolContext(db=db, image_dir="./images")

    # 1. Register various types of documentation
    print("\n1. Registering documentation from text...")

    # Technical specification
    tech_spec = """
    # Multi-Agent Communication Protocol Specification v2.1

    ## Overview
    This document specifies the communication protocol for coordinated multi-agent systems.
    The protocol ensures reliable message delivery, prevents infinite loops, and maintains
    system stability under high load conditions.

    ## Message Format
    All messages must follow the structured format:
    ```
    {
      "agent_id": "unique_identifier",
      "timestamp": "ISO_8601_timestamp",
      "message_type": "user|assistant|system|tool",
      "content": "message_content",
      "metadata": {
        "priority": "low|normal|high|urgent",
        "requires_response": boolean,
        "context_tags": ["tag1", "tag2"]
      }
    }
    ```

    ## Rate Limiting
    Each agent is subject to token bucket rate limiting:
    - Default capacity: 5 messages
    - Refill rate: 1 message per 12 seconds
    - Burst handling: Allow temporary exceeding for urgent messages

    ## Error Handling
    When an agent receives an error response:
    1. Log the error with context
    2. Check if retry is appropriate (non-permanent errors)
    3. Implement exponential backoff: 1s, 2s, 4s, 8s, then stop
    4. Notify system administrator for persistent errors

    ## Security Considerations
    - All webhook payloads must be HMAC-SHA256 signed
    - Timestamp verification prevents replay attacks
    - Agent authentication via secure tokens
    - Message content sanitization for safety

    ## Performance Guidelines
    - Keep messages under 1KB when possible
    - Use image uploads for visual content rather than embedding
    - Batch non-urgent operations
    - Monitor system metrics: response time, error rate, throughput

    ## Integration Patterns
    Common integration scenarios:
    - CI/CD pipeline notifications
    - Monitoring system alerts
    - Customer service escalations
    - Research collaboration workflows
    - Project management updates

    ## Troubleshooting
    Common issues and solutions:
    - "Rate limited" errors: Wait for retry_after seconds
    - "Floor held" errors: Check floor status, wait for release
    - Webhook delivery failures: Verify URL, check signature validation
    - Search not finding results: Try different keywords, check document indexing
    """

    register_doc(ctx, title="Communication Protocol Spec", text=tech_spec, source="internal")
    print("✅ Registered technical specification")

    # Best practices guide
    best_practices = """
    # Agent Team Collaboration Best Practices

    ## Communication Etiquette
    1. **Be Concise**: Keep messages focused and actionable
    2. **Provide Context**: Include relevant background information
    3. **Use Clear Language**: Avoid ambiguous terms and jargon
    4. **Respect Rate Limits**: Don't spam the system with messages
    5. **Signal Intent**: Clearly state what you're trying to accomplish

    ## Coordination Strategies
    - Use floor control for important announcements
    - Set status to indicate current activity and availability
    - Search documentation before asking questions
    - Share relevant images and files to enhance understanding
    - Generate project digests for meeting summaries

    ## Error Prevention
    - Validate inputs before sending messages
    - Handle rate limit responses gracefully
    - Check agent status before expecting responses
    - Use webhooks for real-time notifications
    - Monitor system health and performance

    ## Productivity Tips
    - Bookmark frequently accessed documents
    - Use search with specific keywords for better results
    - Leverage image uploads for visual explanations
    - Create project-specific documentation for context
    - Regular digest reviews help maintain project awareness
    """

    register_doc(ctx, title="Collaboration Best Practices", text=best_practices, source="team")
    print("✅ Registered best practices guide")

    # API reference
    api_reference = """
    # Agent Team Chat API Reference

    ## Core Chat Operations

    ### create_project(name, description)
    Creates a new project/channel for team communication.
    Returns: {"success": true, "project_id": integer}

    ### send_message(project_id, agent, role, content, image_path?)
    Sends a message to the project. Subject to rate limiting.
    Roles: "user", "assistant", "system", "tool"
    Returns: {"success": true, "message_id": integer} or rate limit error

    ### get_recent_messages(project_id, limit=50, before_id?)
    Retrieves recent messages from a project.
    Returns: {"success": true, "messages": [message_objects]}

    ## Agent Coordination

    ### set_agent_status(project_id, agent, status, details?)
    Updates agent presence and status information.
    Status values: "active", "idle", "away", or custom
    Returns: {"success": true, "agent": string, "status": string}

    ### take_floor(project_id, agent, ttl_seconds=60)
    Requests exclusive speaking rights for coordination.
    Returns: {"success": true, "holder": string} or floor conflict error

    ### release_floor(project_id, agent)
    Releases the speaking floor for other agents.
    Returns: {"success": true, "released": true}

    ## Documentation Management

    ### register_doc(title, text, source?, project_id?)
    Registers text content as searchable documentation.
    Automatically chunks large documents for optimal search.
    Returns: {"success": true, "doc_id": integer, "chunks": integer}

    ### search_docs(query, limit=20, offset=0)
    Full-text search across all registered documentation.
    Uses FTS5 with porter stemming for intelligent matching.
    Returns: {"success": true, "results": [search_results]}

    ### get_doc_chunk(doc_id, chunk_index)
    Retrieves a specific chunk of a document for detailed reading.
    Returns: {"success": true, "chunk": {text, sha256, created_at}}

    ## Webhook Management

    ### register_webhook(project_id, url, secret, events)
    Registers a webhook URL for real-time event notifications.
    Events: ["message.created", "status.updated", "floor.taken", etc.]
    Returns: {"success": true, "webhook_id": integer}

    ### Error Responses
    All tools return consistent error format:
    {
      "success": false,
      "error": {
        "code": "ERROR_CODE",
        "message": "Human readable description",
        "retry_after": seconds_to_wait  // for rate limits
      }
    }
    """

    register_doc(ctx, title="API Reference", text=api_reference, source="documentation")
    print("✅ Registered API reference")

    # 2. Register documentation from URL (example with fallback)
    print("\n2. Attempting to register documentation from URL...")
    try:
        # Try to register from a real URL (this might fail in demo environment)
        url_result = register_doc_url(ctx,
                                    url="https://httpbin.org/json",
                                    title="External API Example")
        print(f"✅ Registered from URL: doc_id {url_result['doc_id']}")
    except Exception as e:
        print(f"⚠️ URL registration failed (expected in demo): {e}")
        # Fallback: register as if it came from URL
        fallback_content = """
        # External API Integration Guide

        This document would normally be fetched from an external URL.
        It demonstrates how external documentation can be automatically
        ingested into the DocStation system for team reference.

        Common sources include:
        - API documentation sites
        - Internal wikis and knowledge bases
        - README files from repositories
        - Standards and specification documents
        - Training materials and guides
        """
        register_doc(ctx, title="External API Example", text=fallback_content,
                    source="https://httpbin.org/json")
        print("✅ Registered fallback external content")

    # 3. List all documentation
    print("\n3. Listing all registered documentation...")
    docs_list = list_docs(ctx, limit=10)
    print(f"📋 Found {len(docs_list['docs'])} documents:")
    for doc in docs_list["docs"]:
        print(f"   📄 {doc['title']} (v{doc['version']}) - {doc['source'] or 'no source'}")

    # 4. Demonstrate search functionality
    print("\n4. Testing search functionality...")

    search_queries = [
        "rate limiting",
        "webhook HMAC",
        "agent coordination",
        "error handling",
        "API reference",
        "best practices"
    ]

    for query in search_queries:
        results = search_docs(ctx, query=query, limit=3)
        print(f"🔍 Search '{query}': {len(results['results'])} results")
        for result in results["results"]:
            chunk_preview = result["text"][:80] + "..." if len(result["text"]) > 80 else result["text"]
            print(f"   📖 {result['title']} (chunk {result['chunk_index']}): {chunk_preview}")

    # 5. Demonstrate chunk retrieval
    print("\n5. Retrieving specific document chunks...")
    if docs_list["docs"]:
        first_doc = docs_list["docs"][0]
        doc_id = first_doc["id"]

        # Get first chunk
        chunk = get_doc_chunk(ctx, doc_id=doc_id, chunk_index=0)
        if chunk["success"]:
            chunk_data = chunk["chunk"]
            print(f"📖 First chunk of '{first_doc['title']}':")
            print(f"   Length: {len(chunk_data['text'])} characters")
            print(f"   SHA256: {chunk_data['sha256'][:16]}...")
            print(f"   Preview: {chunk_data['text'][:150]}...")

    # 6. Version management demonstration
    print("\n6. Demonstrating version management...")

    # Register an updated version of the best practices
    updated_practices = best_practices + """

    ## NEW SECTION: Advanced Coordination Patterns

    ### Hierarchical Communication
    - Designate lead agents for complex multi-step tasks
    - Use floor control for structured discussions
    - Implement escalation paths for conflict resolution

    ### Performance Optimization
    - Cache frequently accessed information
    - Use digest summaries for long conversation threads
    - Batch similar operations to reduce overhead

    ### Quality Assurance
    - Implement peer review for critical decisions
    - Use multiple agent perspectives for validation
    - Document lessons learned for future reference
    """

    register_doc(ctx, title="Collaboration Best Practices", text=updated_practices,
                source="team-v2")
    print("✅ Registered updated version of best practices")

    # List versions
    versions = list_doc_versions(ctx, title="Collaboration Best Practices")
    print(f"📚 Versions of 'Collaboration Best Practices': {len(versions['versions'])}")
    for version in versions["versions"]:
        print(f"   v{version['version']} - ID {version['id']} - {version['created_at']}")

    # 7. Advanced search with multiple keywords
    print("\n7. Advanced search demonstrations...")

    advanced_queries = [
        "coordination AND floor control",
        "webhook OR notification",
        "rate limit retry exponential",
        "security HMAC authentication"
    ]

    for query in advanced_queries:
        results = search_docs(ctx, query=query, limit=2)
        print(f"🔍 Advanced search '{query}': {len(results['results'])} results")

    print("\n" + "=" * 60)
    print("✨ Documentation system demo completed!")
    print("Key capabilities demonstrated:")
    print("   ✅ Text and URL-based document registration")
    print("   ✅ Automatic chunking for large documents")
    print("   ✅ Full-text search with relevance ranking")
    print("   ✅ Version management and history tracking")
    print("   ✅ Chunk-based retrieval for detailed reading")
    print("   ✅ Integration with team coordination features")
    print("")
    print("💡 The DocStation subsystem enables teams to:")
    print("   - Share knowledge efficiently across agents")
    print("   - Search for information without manual browsing")
    print("   - Maintain versioned documentation")
    print("   - Integrate external content automatically")


if __name__ == "__main__":
    demo_documentation_system()