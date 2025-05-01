"""EthicsAgent: Validates content against an ethical policy to prevent disallowed material."""
import yaml
import re


class EthicsAgent:
    def __init__(self, policy_path: str = "ethical_policy.yaml"):
        """Load the ethical policy rules from a YAML file."""
        with open(policy_path, 'r') as f:
            policy = yaml.safe_load(f)
        # The YAML is expected to define lists of banned topics/words:
        self.banned_topics = set(policy.get("banned_topics", []))
        self.banned_keywords = set(policy.get("banned_keywords", []))

    def check_content(self, content: str) -> bool:
        """
        Check a single post content string against banned topics/keywords.
        Returns True if content is compliant (no disallowed content), False if it violates policy.
        """
        text = content.lower()
        # Check for any banned topic keywords in the content
        for topic in self.banned_topics:
            if topic.lower() in text:
                return False
        # Check for specific banned keywords
        for word in self.banned_keywords:
            # Use word boundaries to avoid partial matches inside other words
            if re.search(rf"\b{re.escape(word.lower())}\b", text):
                return False
        return True

    def filter_posts(self, posts):
        """
        Filter out or flag any posts that violate the policy.
        Returns a list of compliant posts. (In this design, non-compliant posts are dropped.)
        """
        compliant_posts = []
        for post in posts:
            if self.check_content(post):
                compliant_posts.append(post)
            else:
                # If a post violates policy, we log it (for now just print a warning)
                print(f"[WARNING] Post content rejected by EthicsAgent: {post}")
        return compliant_posts
