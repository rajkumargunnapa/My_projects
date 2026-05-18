import streamlit as st
from review_workflow import workflow  # import your compiled graph

# Page config
st.set_page_config(
    page_title="Product Review Analyzer",
    page_icon="🛍️",
    layout="centered",
)

# Header
st.markdown(
    """
    <h1 style="text-align:center; color:#4CAF50;">
        🛒 Product Review Analyzer
    </h1>
    <p style="text-align:center; font-size:18px;">
        Share your feedback and get instant sentiment analysis, diagnosis, and a personalized response.
    </p>
    """,
    unsafe_allow_html=True,
)

# Input box
st.markdown("### ✍️ Write your review below:")
user_review = st.text_area("Your review/feedback matters!", "", height=150)

# Submit button
if st.button("🚀 Submit Review"):
    if user_review.strip():
        # Prepare initial state
        initial_state = {"review": user_review}

        # Run workflow
        final_state = workflow.invoke(initial_state)

        # Results section
        st.markdown("---")
        st.markdown("## 📊 Results")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 🔎 Sentiment")
            st.success(final_state.get("sentiment", "N/A"))

        with col2:
            if "diagnosis" in final_state:
                st.markdown("### 🩺 Diagnosis")
                st.json(final_state["diagnosis"])

        st.markdown("### 💬 Response")
        st.info(final_state.get("response", "N/A"))
    else:
        st.warning("⚠️ Please enter a review before analyzing.")
