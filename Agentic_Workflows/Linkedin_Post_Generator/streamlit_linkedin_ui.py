# streamlit_linkedin_ui.py
import streamlit as st
from linkedin_post_workflow import run_workflow_auto

st.set_page_config(page_title="LinkedIn Post Generator", layout="centered")

st.title("🚀 LinkedIn Post Generator (LangGraph + Groq)")

# --- Input fields ---
with st.form("post_form"):
    topic = st.text_input("Topic", placeholder="e.g., AI in Aerospace Engineering")
    key_points = st.text_area("Key Points", placeholder="Comma-separated key points")
    tone = st.selectbox("Tone", ["professional", "friendly", "casual", "inspirational", "technical"])
    audience = st.text_input("Audience", placeholder="e.g., Data scientists, AI practitioners")

    submitted = st.form_submit_button("Generate Draft")

if submitted:
    if not topic or not key_points or not tone or not audience:
        st.error("⚠️ Please fill in all fields before generating a draft.")
    else:
        st.info("⏳ Running workflow...")

        # Prepare info dict
        info = {
            "topic": topic,
            "key_points": key_points,
            "tone": tone,
            "audience": audience,
        }

        # Run workflow (this will pause for feedback in CLI, so we adapt here)
        final_state = run_workflow_auto(info)

        # --- Display results ---
        if final_state.get("final_post"):
            st.success("✅ Post Approved & Published!")
            st.write("**Final Post:**")
            st.write(final_state["final_post"])
            st.write(f"**LinkedIn Post ID:** {final_state.get('post_id')}")
        elif final_state.get("post_error"):
            st.error(f"❌ Error posting: {final_state['post_error']}")
        else:
            st.warning("Draft generated but not yet approved.")

# --- Optional: Show workflow state ---
if st.checkbox("Show Workflow State"):
    st.json(run_workflow_auto.__defaults__)
