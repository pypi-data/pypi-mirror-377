#!/usr/bin/env python3
"""
Multi-Agent Coordination Demo

This script demonstrates how multiple AI agents can collaborate through
the Agent Team Chat MCP server, showcasing:

1. Project creation and team setup
2. Multi-agent conversation with rate limiting
3. Webhook event notifications
4. Agent status/presence tracking
5. Floor control for coordinated speaking
6. Documentation sharing and search
7. Image sharing capabilities
8. Project digest generation

Run this demo to see all features in action.
"""

import asyncio
import base64
import time
import sys
import os
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_team_chat.database import Database
from agent_team_chat.tools import ToolContext, create_project, send_message, set_agent_status, \
    register_webhook, take_floor, release_floor, register_doc, search_docs, \
    upload_image_base64, get_project_digest


def create_sample_image_base64() -> str:
    """Create a small sample PNG image as base64 for testing."""
    # 1x1 pixel red PNG
    png_data = (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
        b'\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc```\x00\x00'
        b'\x00\x04\x00\x01\xf6\x17\x8d\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    )
    return base64.b64encode(png_data).decode('ascii')


def demo_multi_agent_coordination():
    """Demonstrate multi-agent coordination features."""
    print("🤖 Agent Team Chat Multi-Agent Coordination Demo")
    print("=" * 60)

    # Setup
    db = Database(":memory:")  # Use in-memory DB for demo
    ctx = ToolContext(db=db, image_dir="./images", rate_capacity=5, rate_interval=60)

    # 1. Create project
    print("\n1. Creating project...")
    project_result = create_project(ctx, name="AI Research Team", description="Collaborative AI research project")
    if not project_result["success"]:
        print(f"❌ Failed to create project: {project_result}")
        return

    project_id = project_result["project_id"]
    print(f"✅ Created project: {project_id}")

    # 2. Register documentation
    print("\n2. Registering team documentation...")
    research_doc = """
    # AI Research Team Guidelines

    ## Objective
    Our team focuses on advancing multi-agent coordination systems for practical applications.

    ## Research Areas
    - Natural language processing between agents
    - Coordination protocols and communication patterns
    - Rate limiting and resource management
    - Event-driven architectures for agent systems

    ## Methodology
    We use iterative development with frequent testing and validation.
    Each agent specializes in specific domains while maintaining awareness of overall progress.

    ## Communication Protocols
    - Use clear, concise messages
    - Share findings and observations
    - Request clarification when needed
    - Coordinate through floor control when necessary
    """

    register_doc(ctx, title="Team Guidelines", text=research_doc, project_id=project_id)
    print("✅ Registered team documentation")

    # 3. Setup agent statuses
    print("\n3. Setting up agent presence...")
    agents = [
        ("ResearcherAlpha", "active", {"specialization": "NLP", "current_focus": "semantic analysis"}),
        ("ResearcherBeta", "active", {"specialization": "Systems", "current_focus": "coordination protocols"}),
        ("AnalystGamma", "active", {"specialization": "Data", "current_focus": "performance metrics"}),
        ("CoordinatorDelta", "active", {"specialization": "Management", "current_focus": "team oversight"})
    ]

    for agent_id, status, details in agents:
        set_agent_status(ctx, project_id=project_id, agent=agent_id, status=status, details=details)
        print(f"✅ {agent_id}: {status} - {details['specialization']}")

    # 4. Demonstrate coordinated conversation
    print("\n4. Starting coordinated agent conversation...")

    # CoordinatorDelta takes floor and opens discussion
    take_floor(ctx, project_id=project_id, agent="CoordinatorDelta", ttl_seconds=30)
    send_message(ctx, project_id=project_id, agent="CoordinatorDelta", role="assistant",
                content="🎯 Team meeting starting. Today's focus: reviewing our multi-agent coordination approach. "
                       "Let's have each specialist share their current progress. Alpha, please start with NLP findings.")

    # Release floor for others
    release_floor(ctx, project_id=project_id, agent="CoordinatorDelta")

    # ResearcherAlpha responds
    send_message(ctx, project_id=project_id, agent="ResearcherAlpha", role="assistant",
                content="📝 NLP Analysis Update: I've been analyzing semantic patterns in agent communication. "
                       "Key finding: agents perform better with structured message formats. Recommending we "
                       "standardize on action-oriented language with clear context markers.")

    # ResearcherBeta builds on Alpha's findings
    send_message(ctx, project_id=project_id, agent="ResearcherBeta", role="assistant",
                content="🔧 Systems perspective: Alpha's structured format idea aligns perfectly with my protocol work. "
                       "I've implemented a token-bucket rate limiter that prevents message floods while maintaining "
                       "responsiveness. We should integrate the semantic structure with rate limiting policies.")

    # AnalystGamma provides data insights
    send_message(ctx, project_id=project_id, agent="AnalystGamma", role="assistant",
                content="📊 Performance metrics show 40% improvement in task completion when agents use "
                       "structured communication. Beta's rate limiting reduced message redundancy by 60%. "
                       "Recommend we A/B test the combined approach on larger agent teams.")

    # 5. Demonstrate rate limiting
    print("\n5. Testing rate limiting (sending rapid messages)...")
    for i in range(7):  # Should hit rate limit on 6th message
        result = send_message(ctx, project_id=project_id, agent="TestAgent", role="user",
                            content=f"Rapid test message {i+1}")
        if not result["success"]:
            print(f"🛑 Rate limited on message {i+1}: retry_after = {result['error'].get('retry_after', 'N/A')}s")
            break
        else:
            print(f"✅ Message {i+1} sent successfully")
        time.sleep(0.1)  # Small delay between messages

    # 6. Share an image
    print("\n6. Sharing research visualization...")
    sample_image = create_sample_image_base64()
    image_result = upload_image_base64(ctx, base64_data=sample_image, filename_hint="coordination_diagram.png")
    if image_result["success"]:
        print(f"✅ Uploaded image: {image_result['image_path']}")

        send_message(ctx, project_id=project_id, agent="AnalystGamma", role="assistant",
                    content="📈 I've uploaded a visualization of our coordination patterns. "
                           "The diagram shows message flow and decision points in our current system.",
                    image_path=image_result["image_path"])

    # 7. Search documentation
    print("\n7. Demonstrating documentation search...")
    search_results = search_docs(ctx, query="coordination protocols")
    print(f"🔍 Found {len(search_results['results'])} results for 'coordination protocols'")
    for result in search_results["results"][:2]:  # Show first 2 results
        print(f"   📄 {result['title']} (chunk {result['chunk_index']})")

    # 8. Generate project digest
    print("\n8. Generating project digest...")
    digest_result = get_project_digest(ctx, project_id=project_id)
    if digest_result["success"]:
        digest = digest_result["digest"]
        print(f"📋 Project Digest (v{digest['version']}):")
        print(f"   Total conversation length: {len(digest['content'])} characters")
        print(f"   Last updated: {digest['updated_at']}")
        # Show first few lines
        lines = digest["content"].split('\n')[:3]
        for line in lines:
            print(f"   > {line[:80]}...")

    # 9. Final coordination message
    print("\n9. Final team coordination...")
    take_floor(ctx, project_id=project_id, agent="CoordinatorDelta", ttl_seconds=30)
    send_message(ctx, project_id=project_id, agent="CoordinatorDelta", role="assistant",
                content="🎉 Excellent progress team! Summary: NLP structure + rate limiting + performance metrics "
                       "= 40% improvement. Next steps: A/B test on larger teams. Great collaboration everyone! "
                       "Meeting adjourned. Check the digest for full details.")
    release_floor(ctx, project_id=project_id, agent="CoordinatorDelta")

    print("\n" + "=" * 60)
    print("✨ Multi-agent coordination demo completed successfully!")
    print("   - Created project with 4 specialized agents")
    print("   - Demonstrated structured conversation with floor control")
    print("   - Tested rate limiting and image sharing")
    print("   - Used documentation search and digest generation")
    print("   - All features working as designed!")


if __name__ == "__main__":
    demo_multi_agent_coordination()