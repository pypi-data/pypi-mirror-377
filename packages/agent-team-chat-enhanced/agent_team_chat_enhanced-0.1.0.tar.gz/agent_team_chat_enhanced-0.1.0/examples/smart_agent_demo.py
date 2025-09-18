#!/usr/bin/env python3
"""
Smart Agent Behavior Demo

This example demonstrates proper agent etiquette:
- Cross-codebase chat discovery using relevance scoring
- Only replying when adding value (avoiding redundant messages)
- Finding the most relevant existing chats before creating new ones
- Checking context before acting
- Following the "silence is better than noise" principle

This shows how agents should behave in real-world scenarios with multiple
codebases and projects, ensuring they join the most relevant conversations.
"""

import sys
import os
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_team_chat.database import Database
from agent_team_chat.tools import ToolContext, find_or_create_project, send_message, \
    get_recent_messages, search_docs, list_projects, get_project_activity, \
    set_agent_status, register_doc


class SmartAgent:
    """Example of a well-behaved agent that follows best practices."""

    def __init__(self, name: str, ctx: ToolContext, specialization: str):
        self.name = name
        self.ctx = ctx
        self.specialization = specialization
        self.current_project_id = None

    def log(self, message: str):
        """Log agent actions for demonstration."""
        print(f"🤖 {self.name}: {message}")

    def should_reply(self, recent_messages: list, proposed_content: str) -> bool:
        """
        Smart logic to determine if the agent should reply.
        Returns False if the reply would be redundant or low-value.
        """
        if not recent_messages:
            return True  # First message in chat

        # Check if someone already said something similar
        recent_content = [msg["content"].lower() for msg in recent_messages[-5:]]
        proposed_lower = proposed_content.lower()

        # Don't reply if it's just an acknowledgment
        if any(word in proposed_lower for word in ["thanks", "great", "good job", "nice", "agree"]):
            if len(proposed_content.strip()) < 50:  # Short acknowledgments
                return False

        # Don't reply if someone recently said something very similar
        for content in recent_content:
            if self._similarity_score(content, proposed_lower) > 0.7:
                return False

        # Don't reply if the last 3 messages are all from this agent
        if len(recent_messages) >= 3:
            last_3_agents = [msg["agent"] for msg in recent_messages[:3]]
            if all(agent == self.name for agent in last_3_agents):
                return False

        return True

    def _similarity_score(self, text1: str, text2: str) -> float:
        """Simple similarity score based on common words."""
        words1 = set(text1.split())
        words2 = set(text2.split())
        if not words1 or not words2:
            return 0.0
        return len(words1 & words2) / len(words1 | words2)

    def find_most_relevant_chat(self, topic: str, keywords: list = None) -> dict:
        """
        Advanced chat discovery across multiple codebases/projects.
        Returns the most relevant chat based on topic, keywords, and activity.
        """
        self.log(f"🔍 Searching for most relevant chat about: {topic}")

        # Get all projects to search across
        projects_result = list_projects(self.ctx)
        if not projects_result["success"]:
            return {"found": False, "reason": "Could not list projects"}

        projects = projects_result["projects"]
        if not projects:
            return {"found": False, "reason": "No existing projects"}

        # Search across all chats for relevance
        candidates = []
        search_keywords = keywords or topic.split()

        for project in projects:
            relevance_score = 0
            project_id = project["id"]
            project_name = project["name"]

            # Score based on name similarity
            name_words = set(project_name.lower().split())
            topic_words = set(topic.lower().split())
            name_match = len(name_words.intersection(topic_words)) / len(topic_words) if topic_words else 0
            relevance_score += name_match * 40  # 40% weight for name match

            # Score based on recent message content
            messages_result = get_recent_messages(self.ctx, project_id=project_id, limit=20)
            if messages_result["success"]:
                messages = messages_result["messages"]
                content_matches = 0
                for msg in messages:
                    msg_words = set(msg["content"].lower().split())
                    for keyword in search_keywords:
                        if keyword.lower() in msg_words:
                            content_matches += 1

                if messages:
                    content_score = min(content_matches / len(messages), 1.0) * 30  # 30% weight
                    relevance_score += content_score

            # Score based on activity level (prefer active chats)
            activity_result = get_project_activity(self.ctx, project_id=project_id)
            if activity_result["success"]:
                activity = activity_result["activity"]
                active_agents = len(activity_result.get("active_agents", []))
                activity_score = min(active_agents / 5, 1.0) * 20  # 20% weight, cap at 5 agents
                relevance_score += activity_score

            # Boost score if this agent's specialization matches
            if self.specialization.lower() in project_name.lower():
                relevance_score += 10  # 10% boost for specialization match

            candidates.append({
                "project_id": project_id,
                "name": project_name,
                "relevance_score": relevance_score,
                "name_match": name_match,
                "recent_messages": len(messages) if messages_result["success"] else 0
            })

        # Sort by relevance score
        candidates.sort(key=lambda x: x["relevance_score"], reverse=True)

        if candidates and candidates[0]["relevance_score"] > 15:  # Minimum relevance threshold
            best_match = candidates[0]
            self.log(f"🎯 Found relevant chat: '{best_match['name']}' (score: {best_match['relevance_score']:.1f})")
            return {"found": True, "project": best_match, "all_candidates": candidates[:3]}

        return {"found": False, "reason": "No sufficiently relevant chats found", "candidates": candidates[:3]}

    def join_or_create_chat(self, topic: str, keywords: list = None) -> bool:
        """Smart way to find existing chats or create new ones across codebases."""
        self.log(f"Looking for chats about: {topic}")

        # Step 1: Try advanced relevance search first
        relevance_result = self.find_most_relevant_chat(topic, keywords)

        if relevance_result["found"]:
            best_project = relevance_result["project"]
            self.current_project_id = best_project["project_id"]
            self.log(f"✅ Joined most relevant chat: '{best_project['name']}'")
            self.log(f"   Relevance score: {best_project['relevance_score']:.1f}")
            self.log(f"   Recent activity: {best_project['recent_messages']} messages")
            return True

        # Step 2: Fallback to exact/similar name matching
        result = find_or_create_project(self.ctx, name=topic)

        if result["success"]:
            if result["action"] == "found_exact_match":
                self.current_project_id = result["project_id"]
                self.log(f"Joined existing chat: '{result['name']}'")
                return True
            elif result["action"] == "found_similar":
                # Show suggestions but don't auto-join
                self.log("Found similar chats:")
                for suggestion in result["suggestions"]:
                    self.log(f"  - '{suggestion['name']}' (ID: {suggestion['id']})")

                # For demo, join the first suggestion
                if result["suggestions"]:
                    first_suggestion = result["suggestions"][0]
                    self.current_project_id = first_suggestion["id"]
                    self.log(f"Joining similar chat: '{first_suggestion['name']}'")
                    return True
            elif result["action"] == "created_new":
                self.current_project_id = result["project_id"]
                self.log(f"Created new chat: '{topic}'")
                return True

        return False

    def check_context_before_acting(self):
        """Demonstrate proper context checking before sending messages."""
        if not self.current_project_id:
            self.log("No current project - need to join a chat first")
            return

        self.log("Checking current context...")

        # Check recent messages
        messages_result = get_recent_messages(self.ctx, project_id=self.current_project_id, limit=10)
        if messages_result["success"]:
            messages = messages_result["messages"]
            self.log(f"Found {len(messages)} recent messages")

            if messages:
                last_msg = messages[0]
                self.log(f"Last message from {last_msg['agent']}: {last_msg['content'][:50]}...")

        # Check activity level
        activity_result = get_project_activity(self.ctx, project_id=self.current_project_id)
        if activity_result["success"]:
            activity = activity_result["activity"]
            recent_agents = activity_result["active_agents"]
            self.log(f"Project activity: {activity}, {len(recent_agents)} active agents")

        # Search docs for relevant context
        search_result = search_docs(self.ctx, query=self.specialization)
        if search_result["success"] and search_result["results"]:
            self.log(f"Found {len(search_result['results'])} relevant docs")

    def send_smart_message(self, content: str, force: bool = False):
        """Send a message only if it adds value."""
        if not self.current_project_id:
            self.log("Cannot send message - not in any project")
            return

        if not force:
            # Check recent messages to decide if we should reply
            messages_result = get_recent_messages(self.ctx, project_id=self.current_project_id, limit=10)
            if messages_result["success"]:
                messages = messages_result["messages"]
                if not self.should_reply(messages, content):
                    self.log("💭 Decided NOT to reply (would be redundant/low-value)")
                    return

        # Send the message
        result = send_message(self.ctx,
                            project_id=self.current_project_id,
                            agent=self.name,
                            role="assistant",
                            content=content)

        if result["success"]:
            self.log(f"✅ Sent message (ID: {result['message_id']})")
        else:
            error_msg = result.get("error", {}).get("message", "Unknown error")
            self.log(f"❌ Failed to send: {error_msg}")

            # Handle rate limiting gracefully
            if result.get("error", {}).get("code") == "RATE_LIMITED":
                retry_after = result["error"].get("retry_after", 0)
                self.log(f"⏳ Rate limited - waiting {retry_after:.1f}s before retrying")


def demo_smart_agent_behavior():
    """Demonstrate smart agent behavior patterns."""
    print("🧠 Smart Agent Behavior Demo")
    print("=" * 50)
    print("Demonstrating proper agent etiquette and smart behavior")
    print()

    # Setup
    db = Database(":memory:")
    ctx = ToolContext(db=db, image_dir="./images")

    # Register some documentation first
    guide_text = """
    # Codebase Architecture Guide

    ## Key Components
    - Authentication module: handles user login and tokens
    - API layer: REST endpoints for client communication
    - Database layer: PostgreSQL with connection pooling
    - Cache layer: Redis for session and API response caching

    ## Common Issues
    - Token expiration: Check auth.py line 147 for validation logic
    - Database timeouts: Increase connection pool size in config.py
    - Cache misses: Review cache key generation in cache_utils.py
    """

    register_doc(ctx, title="Codebase Architecture", text=guide_text, source="internal")

    # Create agents with different specializations
    auth_expert = SmartAgent("AuthExpert", ctx, "authentication")
    api_specialist = SmartAgent("APISpecialist", ctx, "api")
    db_admin = SmartAgent("DBAdmin", ctx, "database")

    print("👥 Created 3 specialized agents:")
    print("   - AuthExpert (authentication specialist)")
    print("   - APISpecialist (API specialist)")
    print("   - DBAdmin (database specialist)")
    print()

    # Scenario 1: Cross-codebase chat discovery
    print("📋 SCENARIO 1: Cross-codebase chat discovery")
    print("-" * 40)

    # Create several projects representing different codebases
    auth_expert.join_or_create_chat("Frontend Authentication Module")
    auth_expert.send_smart_message(
        "🔐 Frontend auth module is complete. Token storage and refresh logic implemented.",
        force=True
    )

    api_specialist.join_or_create_chat("Backend API Gateway")
    api_specialist.send_smart_message(
        "🌐 API gateway is handling authentication middleware. Rate limiting active.",
        force=True
    )

    db_admin.join_or_create_chat("User Database Schema")
    db_admin.send_smart_message(
        "💾 User table optimized. Auth token indexes created for fast lookups.",
        force=True
    )

    print()

    # Now demonstrate smart discovery - agent looking for "authentication" work
    print("🔍 New agent joining, looking for authentication-related work...")
    new_auth_agent = SmartAgent("SecurityAuditor", ctx, "security")

    # This should find the most relevant chat across all codebases
    if new_auth_agent.join_or_create_chat("authentication security", ["auth", "token", "security"]):
        new_auth_agent.check_context_before_acting()
        new_auth_agent.send_smart_message(
            "🔐 I'm here to audit authentication security across all modules. "
            "I see there's work happening on auth - I'll review the token handling for vulnerabilities."
        )

    print()

    # Scenario 2: Agent avoids redundant replies
    print("📋 SCENARIO 2: Avoiding redundant replies")
    print("-" * 35)

    # Third agent joins and tries to add redundant info
    if db_admin.join_or_create_chat("User Authentication"):
        db_admin.check_context_before_acting()
        # This should be filtered out as redundant
        db_admin.send_smart_message("Thanks for the update, looking into this now.")

        # But this should go through as it adds value
        db_admin.send_smart_message(
            "💾 From the database side: I see we have orphaned sessions when tokens expire. "
            "I'll add a cleanup job to remove these every hour. This should improve performance."
        )

    print()

    # Scenario 3: Show activity checking
    print("📋 SCENARIO 3: Context-aware participation")
    print("-" * 35)

    # Expert joins a different project
    if auth_expert.join_or_create_chat("Database Performance"):
        auth_expert.check_context_before_acting()

        # Agent should recognize this isn't their specialty
        auth_expert.send_smart_message(
            "🤝 I see this is about database performance. While that's not my specialty, "
            "I can share that the auth module makes heavy use of user session queries. "
            "@DBAdmin might have insights on optimizing those."
        )

    print()
    print("=" * 50)
    print("✨ Smart Agent Demo Complete!")
    print()
    print("Key behaviors demonstrated:")
    print("✅ Cross-codebase chat discovery with relevance scoring")
    print("✅ Agents find the most relevant chat across multiple projects")
    print("✅ Smart ranking based on topic, content, activity, and specialization")
    print("✅ Agents check context before acting")
    print("✅ Agents avoid redundant or low-value replies")
    print("✅ Agents provide specific, actionable information")
    print("✅ Agents know when to defer to specialists")
    print("✅ Agents reference documentation and code locations")
    print()
    print("This prevents chat spam and ensures agents join the most relevant conversations!")
    print("Perfect for teams with multiple codebases and overlapping concerns!")


if __name__ == "__main__":
    demo_smart_agent_behavior()