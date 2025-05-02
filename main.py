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


def run_pipeline(visualizer, client, banned_phrases, cfg, on_complete):
    # Initialize agents
    trend_agent = TrendAgent(client)
    content_agent = ContentAgent(client, banned_phrases)
    seo_agent = SEOAgent(client, banned_phrases)
    ethics_agent = EthicsAgent()

    # 1) Trends: fetch and select top topic
    visualizer.update_progress(
        "TrendAgent", 0, "Starting…", message="Beginning trend fetch"
    )
    top_list = trend_agent.get_top_topics()
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
    drafts = content_agent.create_posts(top_topic)
    draft_post = drafts[0] if drafts else ""
    visualizer.update_progress(
        "ContentAgent",
        100,
        "Draft ready",
        message=f"Drafted post: {draft_post}"
    )

    # 3) SEO: optimize draft
    visualizer.update_progress(
        "SEOAgent", 0, "Starting…", message="Beginning SEO optimization"
    )
    optimized = seo_agent.optimize_posts(drafts)
    optimized_post = optimized[0] if optimized else ""
    visualizer.update_progress(
        "SEOAgent",
        100,
        "Optimized",
        message=f"Optimized post: {optimized_post}"
    )

    # 4) Ethics: final approval
    visualizer.update_progress(
        "EthicsAgent", 0, "Starting…", message="Beginning ethics review"
    )
    final_posts = ethics_agent.filter_posts(optimized)
    final_post = final_posts[0] if final_posts else ""
    visualizer.update_progress(
        "EthicsAgent",
        100,
        "Approved",
        message=f"Final approved post: {final_post}"
    )

    # Once pipeline is complete, invoke the callback with the final post
    on_complete(final_post, top_topic)



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
        page.wait_for_timeout(5000)
        page.get_by_text("What's new?").click()
        page.get_by_role('textbox', name="Empty text field. Type to compose a new post.").fill(posts)
        page.get_by_role(role="button", name="Post").click()
        time.sleep(5)

        context.close()


def main():
    # Load configuration and OpenAI client
    cfg = load_config()
    client = cfg["openai_client"]
    banned = cfg.get("banned_phrases", [])

    # Initialize visualizer UI
    agents = ["TrendAgent", "ContentAgent", "SEOAgent", "EthicsAgent"]
    visualizer = AgentVisualizer(agents)

    # Callback when pipeline finishes or redo is triggered
    def on_pipeline_complete(final_post, topic):
        # Store for redo
        visualizer.current_topic = topic
        visualizer.current_post = final_post
        # Show control buttons
        visualizer.show_redo_button(lambda: on_redo(topic))
        visualizer.show_accept_button(lambda: on_accept(final_post))

    # Accept handler
    def on_accept(post):
        visualizer.disable_accept_button()
        visualizer.disable_redo_button()
        visualizer.update_progress(
            "EthicsAgent", 100, "User accepted post", message="Post accepted for publishing"
        )
        post_to_threads(post, cfg, headless=False)

    # Redo handler: regenerate content and re-run SEO and Ethics
    def on_redo(topic):
        visualizer.disable_accept_button()
        visualizer.disable_redo_button()
        # 2) Regenerate content
        visualizer.update_progress(
            "ContentAgent", 0, "Redoing content…", message="User requested redo"
        )
        drafts = ContentAgent(client, banned).create_posts(topic)
        draft_post = drafts[0] if drafts else ""
        visualizer.update_progress(
            "ContentAgent", 100, "Draft ready", message=f"Redrafted post: {draft_post}"
        )
        # 3) SEO
        visualizer.update_progress(
            "SEOAgent", 0, "Re-optimizing…", message="Redo SEO optimization"
        )
        optimized = SEOAgent(client, banned).optimize_posts(drafts)
        optimized_post = optimized[0] if optimized else ""
        visualizer.update_progress(
            "SEOAgent", 100, "Optimized", message=f"Re-optimized post: {optimized_post}"
        )
        # 4) Ethics
        visualizer.update_progress(
            "EthicsAgent", 0, "Re-reviewing…", message="Redo ethics review"
        )
        final_posts = EthicsAgent().filter_posts(optimized)
        final_post = final_posts[0] if final_posts else ""
        visualizer.update_progress(
            "EthicsAgent", 100, "Approved",
            message=f"Final approved post: {final_post}"
        )
        # Show buttons again
        visualizer.show_redo_button(lambda: on_redo(topic))
        visualizer.show_accept_button(lambda: on_accept(final_post))

    # Start pipeline in background
    #threading.Thread(
    #    target=run_pipeline,
    #    args=(visualizer, client, banned, cfg, on_pipeline_complete),
    #    daemon=True
    #).start()

    # Manual Run handler
    def on_manual_run():
        visualizer.disable_manual_run_button()
        visualizer.disable_auto_run_button()
        threading.Thread(
            target=run_pipeline,
            args=(visualizer, client, banned, cfg, on_pipeline_complete),
            daemon=True
        ).start()

    # Auto Run handler: runs pipeline and posts without user intervention
    def on_auto_run():
        visualizer.disable_manual_run_button()
        visualizer.disable_auto_run_button()

        def pipeline_and_post():
            final_posts = []

            def auto_complete(fp, _):
                final_posts.append(fp)

            run_pipeline(visualizer, client, banned, cfg, auto_complete)
            if final_posts:
                post_to_threads(final_posts[0], cfg, headless=True)

        threading.Thread(target=pipeline_and_post, daemon=True).start()

    # Only show run buttons; do not start pipeline until user clicks
    visualizer.show_manual_run_button(on_manual_run)
    visualizer.show_auto_run_button(on_auto_run)

    visualizer.mainloop()


if __name__ == "__main__":
    main()
