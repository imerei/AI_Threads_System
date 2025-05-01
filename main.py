# main.py
"""
Orchestrator for the AI Threads System with real-time visualization.
Runs the AI agent pipeline in a background thread, updates the UI with
avatars, progress bars, status labels, and logs each agent’s output.
"""
import os
import time
import threading
from playwright.sync_api import sync_playwright
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


from utils.config_loader import load_config
from agents.trend_agent import TrendAgent
from agents.content_agent import ContentAgent
from agents.seo_agent import SEOAgent
from agents.ethics_agent import EthicsAgent
from ui.visualizer import AgentVisualizer

STORAGE_STATE = "storageState.json"
USER_DATA_DIR = "playwright_profile"


def run_pipeline(visualizer, client, cfg):
    # 1) Trends: fetch and select top topic
    visualizer.update_progress(
        "TrendAgent", 0, "Starting…", message="Beginning trend fetch"
    )
    top_list = TrendAgent(client).get_top_topics()  # returns [top_topic]
    top_topic = top_list[0] if top_list else ""
    visualizer.update_progress(
        "TrendAgent",
        100,
        "Trends fetched",
        message=f"Fetched topic: {top_topic}"
    )

    # 2) Content: draft single post
    visualizer.update_progress(
        "ContentAgent", 0, "Starting…", message="Beginning content draft"
    )
    drafts = ContentAgent(client).create_posts(top_topic)
    visualizer.update_progress(
        "ContentAgent",
        100,
        "Draft ready",
        message=f"Drafted post: {drafts[0]}"
    )

    # 3) SEO: optimize draft
    visualizer.update_progress(
        "SEOAgent", 0, "Starting…", message="Beginning SEO optimization"
    )
    optimized = SEOAgent(client).optimize_posts(drafts)
    visualizer.update_progress(
        "SEOAgent",
        100,
        "Optimized",
        message=f"Optimized posts: {optimized}"
    )

    # 4) Ethics: final approval
    visualizer.update_progress(
        "EthicsAgent", 0, "Starting…", message="Beginning ethics review"
    )
    final_posts = EthicsAgent().filter_posts(optimized)
    visualizer.update_progress(
        "EthicsAgent",
        100,
        "Approved",
        message=f"Final approved posts: {final_posts}"
    )

    return final_posts



def post_to_threads(posts, cfg, headless=False):

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            USER_DATA_DIR,
            headless=headless
        )
        page = context.pages[0]
        thread_text = page.get_by_text("Log in with your Instagram account")

        # Navigate explicitly to Threads home
        page.goto("https://www.threads.com/")

        # Try to detect login form (username/email input); short timeout
        needs_login = None
        try:
            thread_text.wait_for(state="visible", timeout=3000)
            print("Login form detected—needs_login = True")
            needs_login = True
        except PlaywrightTimeoutError:
            # If the selector isn't found quickly, assume we're already logged in
            print("No login form—needs_login = False")
            needs_login = False

        # 2) If no storage file existed, perform login and then save it
        # if not os.path.exists(STORAGE_STATE):
        if needs_login:
            page.goto("https://www.threads.com/login")
            page.get_by_placeholder("Username, phone or email").fill(cfg["threads_username"])
            page.get_by_placeholder("Password").fill(cfg["threads_password"])
            page.get_by_role("button", name="Log in", exact=True).click()
            page.wait_for_load_state("networkidle")
            # Save cookies & localStorage so future runs reuse the session
            context.storage_state(path=STORAGE_STATE)

        # 3) Use the logged-in session to post each thread
        for content in posts:
            page.wait_for_timeout(5000)
            page.get_by_text("What's new?").click()
            page.get_by_role('textbox', name="Empty text field. Type to compose a new post.").fill(content)
            page.get_by_role(role="button", name="Post").click()
            time.sleep(2)

        context.close()


def main():
    # Load config and initialize the OpenAI client
    cfg    = load_config()
    client = cfg["openai_client"]

    # Set up the visualizer UI with all four agents
    agents = ["TrendAgent", "ContentAgent", "SEOAgent", "EthicsAgent"]
    visualizer = AgentVisualizer(agents)

    # Run the pipeline in a background thread so the UI remains responsive
    def pipeline_thread():
        final_posts = run_pipeline(visualizer, client, cfg)
        if final_posts:
            post_to_threads(final_posts, cfg)
        else:
            visualizer.update_progress(
                "EthicsAgent",
                100,
                "No posts to send",
                message="All content was filtered out; nothing to post."
            )

    threading.Thread(target=pipeline_thread, daemon=True).start()

    # Launch the Tkinter event loop
    visualizer.mainloop()


if __name__ == "__main__":
    main()
