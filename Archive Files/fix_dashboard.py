code = open('dashboard/app.py', 'w', encoding='utf-8')
code.write("""import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import CognitiveOS

st.set_page_config(page_title="Cognitive OS", page_icon="🧠", layout="wide")

if "cos" not in st.session_state:
    with st.spinner("Initializing Cognitive OS..."):
        try:
            st.session_state.cos = CognitiveOS()
            st.session_state.initialized = True
        except Exception as e:
            st.error(f"Initialization error: {e}")
            st.session_state.initialized = False

if not st.session_state.get("initialized", False):
    st.error("System failed to initialize. Check your config.json and API key.")
    st.stop()

cos = st.session_state.cos

st.title("🧠 Cognitive OS")
st.caption("Persistent Intelligence Infrastructure")

with st.sidebar:
    st.header("System Status")
    st.metric("Total Memories", cos.get_memory_count())
    st.metric("User", cos.identity.get("name", "Unknown"))
    st.metric("Active Project", "Cognitive OS")
    st.divider()
    mode = st.radio("Mode", ["💬 Query", "⚡ Compare", "📥 Ingest", "📚 Memory Browser"])
    st.divider()
    st.caption("Local-first. Private. Persistent.")

if mode == "💬 Query":
    st.subheader("Query Your Memory System")
    prompt = st.text_area("Your question:", height=100)
    if st.button("Send", type="primary", use_container_width=True) and prompt:
        with st.spinner("Retrieving memories and querying Claude..."):
            response = cos.handle_query(prompt)
        st.markdown("### Response")
        st.write(response["text"])
        st.caption(f"Tokens: {response.get('tokens_used')} | Provider: {response.get('provider')}")
        context = response.get("context_packet", {})
        memories = context.get("memories", [])
        if memories:
            with st.expander(f"Retrieved Memories ({len(memories)})"):
                for mem in memories:
                    st.write(f"**{mem.get('importance','').upper()}** | {mem.get('category','')} | Score: {mem.get('retrieval_score',0)}")
                    st.write(mem.get("memory_text",""))
                    st.divider()

elif mode == "⚡ Compare":
    st.subheader("The Gap Demonstration")
    st.caption("Same question. Same model. The difference is memory.")
    prompt = st.text_area("Enter your question:", height=100)
    if st.button("Run Comparison", type="primary", use_container_width=True) and prompt:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**WITHOUT MEMORY**")
            with st.spinner("Querying..."):
                bare = cos.bare_query(prompt)
            st.write(bare["text"])
            st.caption(f"{bare.get('tokens_used', 0)} tokens")
        with col2:
            st.markdown("**WITH MEMORY**")
            with st.spinner("Retrieving memories..."):
                enriched = cos.handle_query(prompt)
            st.write(enriched["text"])
            st.caption(f"{enriched.get('tokens_used', 0)} tokens")
            context = enriched.get("context_packet", {})
            memories = context.get("memories", [])
            if memories:
                with st.expander("Memories Used"):
                    for mem in memories:
                        st.write(f"**{mem.get('importance','').upper()}** | {mem.get('category','')}")
                        st.write(mem.get("memory_text",""))
                        st.divider()

elif mode == "📥 Ingest":
    st.subheader("Add New Memories")
    raw_input = st.text_area("Paste your input here:", height=250)
    source = st.selectbox("Source type:", ["manual", "conversation", "document", "meeting", "decision"])
    if st.button("Extract Memories", type="primary", use_container_width=True) and raw_input:
        with st.spinner("Extracting memories with Claude..."):
            candidates = cos.ingest(raw_input, source=source)
        st.session_state.candidates = candidates
        st.session_state.dismissed = set()
        st.success(f"Found {len(candidates)} memory candidates.")
    if "candidates" in st.session_state and st.session_state.candidates:
        st.markdown("### Review Memories")
        if "dismissed" not in st.session_state:
            st.session_state.dismissed = set()
        remaining = [(i, c) for i, c in enumerate(st.session_state.candidates) if i not in st.session_state.dismissed]
        if not remaining:
            st.success("All memories reviewed. Ingest complete.")
            if st.button("Start New Ingest"):
                st.session_state.candidates = []
                st.session_state.dismissed = set()
                st.rerun()
        else:
            st.caption(f"{len(remaining)} remaining of {len(st.session_state.candidates)}")
            for i, candidate in remaining:
                with st.expander(f"Memory {i+1}: {candidate.get('memory_text','')[:70]}...", expanded=True):
                    edited_text = st.text_area("Memory text:", value=candidate.get("memory_text",""), key=f"text_{i}")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**Type:** {candidate.get('type')}")
                    with col2:
                        st.write(f"**Category:** {candidate.get('category')}")
                    with col3:
                        st.write(f"**Importance:** {candidate.get('importance')}")
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        if st.button("Approve", key=f"approve_{i}", type="primary"):
                            candidate["memory_text"] = edited_text
                            cos.store_memory(candidate)
                            st.session_state.dismissed.add(i)
                            st.rerun()
                    with col_b:
                        if st.button("Flag", key=f"flag_{i}"):
                            candidate["status"] = "pending_review"
                            candidate["memory_text"] = edited_text
                            cos.store_memory(candidate)
                            st.session_state.dismissed.add(i)
                            st.rerun()
                    with col_c:
                        if st.button("Reject", key=f"reject_{i}"):
                            st.session_state.dismissed.add(i)
                            st.rerun()

elif mode == "📚 Memory Browser":
    st.subheader("Memory Browser")
    memories = cos.get_all_memories()
    if not memories:
        st.info("No memories stored yet.")
    else:
        st.metric("Total Active Memories", len(memories))
        category_filter = st.selectbox("Filter by category:", ["All","people","resources","risk","relationships","patterns","context"])
        filtered = memories if category_filter == "All" else [m for m in memories if m.get("category") == category_filter]
        for mem in filtered:
            with st.expander(f"[{mem.get('importance','').upper()}] {mem.get('memory_text','')[:80]}..."):
                st.write(mem.get("memory_text",""))
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.caption(f"Type: {mem.get('type')}")
                with col2:
                    st.caption(f"Category: {mem.get('category')}")
                with col3:
                    st.caption(f"Retrieved: {mem.get('retrieval_count',0)} times")
""")
code.close()
print("Dashboard written successfully.")