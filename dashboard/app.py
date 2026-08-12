import streamlit as st
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from storage.memory_db import MemoryDB
from storage.vector_db import VectorDB
from ingestion.extractor import Extractor
from ingestion.structurer import Structurer
from retrieval.search_engine import SearchEngine
from llm_interface.interface import LLMInterface

def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

def render_tags(memory: dict):
    # Display-only: surfaces the structured fact_pattern_tags (which carry
    # posture/ruling/clustering tags) and the general tags on a memory card.
    fact_tags = memory.get('fact_pattern_tags', [])
    if not isinstance(fact_tags, list):
        fact_tags = []
    gen_tags = memory.get('tags', [])
    if not isinstance(gen_tags, list):
        gen_tags = []

    if fact_tags:
        st.markdown(
            "**Fact Pattern Tags:** " + ", ".join(f"`{t}`" for t in fact_tags)
        )
    if gen_tags:
        st.caption("Tags: " + ", ".join(gen_tags))

def initialize_system():
    if 'initialized' not in st.session_state:
        config = load_config()
        os.makedirs("data", exist_ok=True)

        st.session_state.config = config
        st.session_state.memory_db = MemoryDB(
            db_path=config["db_path"]
        )
        st.session_state.vector_db = VectorDB(
            db_path=config["chroma_path"]
        )
        st.session_state.extractor = Extractor(
            api_key=config["anthropic_api_key"],
            model=config["model"],
            ingestion_model=config["ingestion_model"]
        )
        st.session_state.structurer = Structurer(
            default_project=config["default_project"]
        )
        st.session_state.search_engine = SearchEngine(
            memory_db=st.session_state.memory_db,
            vector_db=st.session_state.vector_db,
            config=config
        )
        st.session_state.llm = LLMInterface(
            api_key=config["anthropic_api_key"],
            model=config["model"]
        )
        st.session_state.initialized = True

def parse_response(response_text: str):
    note_marker = "### 📊 Confidence Note"
    caveat_marker = "### Confidence Caveat"

    main = response_text
    confidence_note = None
    confidence_note_header = "Confidence Note"
    confidence_caveat = None

    if note_marker in main:
        parts = main.split(note_marker, 1)
        main = parts[0].strip()
        remainder = parts[1].strip()

        lines = remainder.split('\n')
        first_line = lines[0].strip()

        # First line may be ": LOW" or "LOW" or ": HIGH" etc
        if first_line.startswith(':'):
            level = first_line.replace(':', '').strip()
            if level:
                confidence_note_header = (
                    f"Confidence Note: {level}"
                )
            remainder = '\n'.join(lines[1:]).strip()
        elif first_line.upper() in [
            'HIGH', 'MEDIUM', 'LOW',
            'CONTRADICTED', 'INSUFFICIENT DATA'
        ]:
            confidence_note_header = (
                f"Confidence Note: {first_line}"
            )
            remainder = '\n'.join(lines[1:]).strip()

        if caveat_marker in remainder:
            note_parts = remainder.split(caveat_marker, 1)
            confidence_note = note_parts[0].strip()
            confidence_caveat = note_parts[1].strip()
        else:
            confidence_note = remainder.strip()

    return (
        main,
        confidence_note,
        confidence_note_header,
        confidence_caveat
    )

def parse_caveat(caveat_text: str):
    if not caveat_text:
        return None, None

    lines = caveat_text.split('\n')
    summary_lines = []
    bullet_lines = []
    in_bullets = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith('-') or \
           stripped.startswith('•') or \
           stripped.startswith('*'):
            in_bullets = True
        if in_bullets:
            bullet_lines.append(line)
        else:
            summary_lines.append(line)

    summary = '\n'.join(summary_lines).strip()
    bullets = '\n'.join(bullet_lines).strip()

    return summary, bullets

def render_confidence_blocks(pattern_evidence: dict):
    if not pattern_evidence:
        return

    confidence_colors = {
        'high': '🟢',
        'medium': '🟡',
        'low': '🔴',
        'contradicted': '🚨',
        'insufficient_data': '⚪'
    }

    confidence_labels = {
        'high': 'HIGH CONFIDENCE',
        'medium': 'MEDIUM CONFIDENCE',
        'low': 'LOW CONFIDENCE',
        'contradicted': 'CONTRADICTED',
        'insufficient_data': 'INSUFFICIENT DATA'
    }

    confidence_order = {
        'high': 0,
        'medium': 1,
        'low': 2,
        'contradicted': 3,
        'insufficient_data': 4
    }

    sorted_evidence = sorted(
        pattern_evidence.items(),
        key=lambda x: (
            confidence_order.get(
                x[1].get('confidence_level', 'low'), 2
            ),
            -x[1].get('corroborating_count', 0)
        )
    )

    for key, evidence in sorted_evidence:
        entity = evidence.get('entity', '')
        entity_type = evidence.get(
            'entity_type', ''
        ).replace('_', ' ').title()
        confidence = evidence.get('confidence_level', 'low')
        corroborating_count = evidence.get(
            'corroborating_count', 0
        )
        deviating_count = evidence.get('deviating_count', 0)
        corroborating_ids = evidence.get('corroborating_ids', [])
        deviating_ids = evidence.get('deviating_ids', [])

        color = confidence_colors.get(confidence, '⚪')
        label = confidence_labels.get(
            confidence, 'LOW CONFIDENCE'
        )

        st.markdown(f"#### {color} {entity} — {entity_type}")
        st.markdown(f"**{label}**")

        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                "Corroborating Memories",
                corroborating_count
            )
        with col2:
            st.metric(
                "Deviating Memories",
                deviating_count
            )

        if confidence == 'contradicted':
            st.error(
                "⚠️ WARNING: Deviating memories outweigh "
                "corroborating memories. Review all memory IDs "
                "before relying on this conclusion."
            )
        elif deviating_count > 0:
            st.warning(
                f"⚠️ {deviating_count} memory(s) deviate "
                f"from this pattern."
            )

        if corroborating_ids:
            with st.expander(
                f"Corroborating Memory IDs "
                f"({corroborating_count})"
            ):
                st.caption(
                    "Use these IDs in the Memory Browser "
                    "to view and verify each memory."
                )
                for mem_id in corroborating_ids:
                    st.code(mem_id)

        if deviating_ids:
            with st.expander(
                f"⚠️ Deviating Memory IDs ({deviating_count})"
            ):
                st.caption(
                    "These memories contradict or deviate "
                    "from the pattern. Review carefully."
                )
                for mem_id in deviating_ids:
                    st.code(mem_id)

        st.markdown("---")

def main():
    st.set_page_config(
        page_title="Cognitive OS — Legal Intelligence",
        page_icon="⚖️",
        layout="wide"
    )

    initialize_system()

    st.title("⚖️ Cognitive OS — Legal Intelligence Platform")

    memory_count = st.session_state.memory_db.count()
    vector_count = st.session_state.vector_db.count()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Memories", memory_count)
    with col2:
        st.metric("Vector Index", vector_count)
    with col3:
        st.metric("System Status", "Online")

    st.markdown("---")

    tab1, tab2, tab3 = st.tabs([
        "Query Intelligence",
        "Ingest Transcript",
        "Memory Browser"
    ])

    # TAB 1 — QUERY
    with tab1:
        st.subheader("Query Legal Intelligence")

        with st.expander("Search Filters", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                filter_practice_area = st.selectbox(
                    "Practice Area",
                    ["All"] + st.session_state.config[
                        "practice_areas"
                    ]
                )
                filter_memory_type = st.selectbox(
                    "Memory Type",
                    ["All"] + st.session_state.config[
                        "memory_types"
                    ]
                )
            with col2:
                filter_judge = st.text_input(
                    "Judge Name (optional)"
                )
                filter_opposing_counsel = st.text_input(
                    "Opposing Counsel (optional)"
                )

        query = st.text_area(
            "Enter your query",
            placeholder="e.g. What strategies have worked against aggressive opposing counsel in contract disputes?",
            height=100
        )

        if st.button("Query", type="primary"):
            if query:
                with st.spinner(
                    "Retrieving legal intelligence..."
                ):
                    practice_area = (
                        None
                        if filter_practice_area == "All"
                        else filter_practice_area
                    )
                    memory_type = (
                        None
                        if filter_memory_type == "All"
                        else filter_memory_type
                    )
                    judge = (
                        filter_judge
                        if filter_judge else None
                    )
                    opposing_counsel = (
                        filter_opposing_counsel
                        if filter_opposing_counsel else None
                    )

                    context = st.session_state.search_engine.retrieve(
                        prompt=query,
                        practice_area=practice_area,
                        memory_type=memory_type,
                        judge=judge,
                        opposing_counsel=opposing_counsel
                    )

                    memories = context.get("memories", [])

                    if memories:
                        response = st.session_state.llm.query(
                            prompt=query,
                            context_packet=context
                        )

                        # Parse all sections
                        (
                            main_response,
                            confidence_note,
                            confidence_note_header,
                            confidence_caveat
                        ) = parse_response(response)

                        caveat_summary, caveat_bullets = (
                            parse_caveat(confidence_caveat)
                        )

                        # --- INTELLIGENCE RESPONSE ---
                        st.subheader("Intelligence Response")
                        st.write(main_response)

                        # --- CONFIDENCE NOTE ---
                        if confidence_note:
                            st.markdown("---")
                            st.markdown(
                                f"### {confidence_note_header}"
                            )
                            st.write(confidence_note)

                        # --- CONFIDENCE CAVEAT ---
                        if caveat_summary or caveat_bullets:
                            st.markdown("---")
                            st.markdown(
                                "### ⚠️ Confidence Caveat"
                            )

                            if caveat_summary:
                                st.write(caveat_summary)

                            if caveat_bullets:
                                with st.expander(
                                    "View Confidence Details"
                                ):
                                    st.markdown(caveat_bullets)

                            pattern_evidence = context.get(
                                "pattern_evidence", {}
                            )
                            if pattern_evidence:
                                with st.expander(
                                    "View Pattern Evidence Details"
                                ):
                                    render_confidence_blocks(
                                        pattern_evidence
                                    )

                        # --- SOURCE MEMORIES ---
                        st.markdown("---")
                        st.subheader("Source Memories")

                        breakdown = context.get(
                            "memory_breakdown", {}
                        )
                        cols = st.columns(5)
                        labels = [
                            "Matter", "Client",
                            "Precedent", "Judgment",
                            "Operational"
                        ]
                        keys = [
                            "matter", "client",
                            "precedent", "partner_judgment",
                            "operational"
                        ]
                        for i, (label, key) in enumerate(
                            zip(labels, keys)
                        ):
                            with cols[i]:
                                st.metric(
                                    label,
                                    breakdown.get(key, 0)
                                )

                        with st.expander("View Source Memories"):
                            for i, memory in enumerate(memories):
                                with st.expander(
                                    f"[{memory.get('memory_type', '').upper()}] "
                                    f"[{memory.get('practice_area', '').upper()}] "
                                    f"Score: {memory.get('retrieval_score', 0)} "
                                    f"ID: {memory.get('id', '')} — "
                                    f"{memory.get('memory_text', '')[:60]}..."
                                ):
                                    st.write(
                                        memory.get('memory_text', '')
                                    )
                                    render_tags(memory)
                                    col1, col2, col3 = st.columns(3)
                                    with col1:
                                        st.caption(
                                            f"ID: {memory.get('id')}"
                                        )
                                        st.caption(
                                            f"Type: {memory.get('memory_type')}"
                                        )
                                        st.caption(
                                            f"Category: {memory.get('extraction_category')}"
                                        )
                                        st.caption(
                                            f"Practice Area: {memory.get('practice_area')}"
                                        )
                                    with col2:
                                        st.caption(
                                            f"Outcome: {memory.get('outcome')}"
                                        )
                                        st.caption(
                                            f"Importance: {memory.get('importance')}"
                                        )
                                        st.caption(
                                            f"Confidence: {memory.get('confidence')}"
                                        )
                                    with col3:
                                        st.caption(
                                            f"Judge: {memory.get('judge')}"
                                        )
                                        st.caption(
                                            f"Opposing Counsel: {memory.get('opposing_counsel')}"
                                        )
                                        st.caption(
                                            f"Source Attorney: {memory.get('source_attorney')}"
                                        )
                    else:
                        st.warning(
                            "No relevant memories found. "
                            "Try ingesting some transcripts first."
                        )
            else:
                st.warning("Please enter a query.")

    # TAB 2 — INGEST
    with tab2:
        st.subheader("Ingest Legal Transcript or Document")

        source_name = st.text_input(
            "Source Name",
            placeholder="e.g. Smith v Jones Deposition 2024"
        )

        ingest_text = st.text_area(
            "Paste transcript or document text here",
            placeholder="Paste full court transcript, deposition, hearing notes, or any legal document...",
            height=300
        )

        if st.button(
            "Extract and Store Memories", type="primary"
        ):
            if ingest_text and source_name:
                with st.spinner(
                    "Extracting legal intelligence from document..."
                ):
                    candidates = (
                        st.session_state.extractor.extract(
                            ingest_text
                        )
                    )

                    if candidates:
                        structured = (
                            st.session_state.structurer
                            .structure_batch(
                                candidates=candidates,
                                source=source_name
                            )
                        )

                        saved_count = 0
                        for memory in structured:
                            try:
                                st.session_state.memory_db.save(
                                    memory
                                )
                                st.session_state.vector_db.add(
                                    memory
                                )
                                saved_count += 1
                            except Exception as e:
                                st.error(
                                    f"Failed to save memory: {e}"
                                )

                        st.success(
                            f"Successfully extracted and stored "
                            f"{saved_count} memories from "
                            f"{source_name}"
                        )

                        st.subheader("Extracted Memories Preview")
                        type_counts = {}
                        for memory in structured:
                            t = memory.get(
                                'memory_type', 'unknown'
                            )
                            type_counts[t] = (
                                type_counts.get(t, 0) + 1
                            )

                        cols = st.columns(len(type_counts))
                        for i, (t, count) in enumerate(
                            type_counts.items()
                        ):
                            with cols[i]:
                                st.metric(
                                    t.replace("_", " ").title(),
                                    count
                                )

                        with st.expander(
                            "View Extracted Memories"
                        ):
                            for memory in structured:
                                with st.expander(
                                    f"[{memory.get('memory_type', '').upper()}] "
                                    f"ID: {memory.get('id', '')} — "
                                    f"{memory.get('memory_text', '')[:60]}..."
                                ):
                                    st.write(
                                        memory.get('memory_text', '')
                                    )
                                    render_tags(memory)
                                    col1, col2, col3 = st.columns(3)
                                    with col1:
                                        st.caption(
                                            f"ID: {memory.get('id')}"
                                        )
                                        st.caption(
                                            f"Category: {memory.get('extraction_category')}"
                                        )
                                        st.caption(
                                            f"Practice Area: {memory.get('practice_area')}"
                                        )
                                    with col2:
                                        st.caption(
                                            f"Outcome: {memory.get('outcome')}"
                                        )
                                        st.caption(
                                            f"Importance: {memory.get('importance')}"
                                        )
                                    with col3:
                                        st.caption(
                                            f"Judge: {memory.get('judge')}"
                                        )
                                        st.caption(
                                            f"Opposing Counsel: {memory.get('opposing_counsel')}"
                                        )
                    else:
                        st.error(
                            "No memories extracted. "
                            "Check the document content."
                        )
            else:
                st.warning(
                    "Please enter both a source name "
                    "and document text."
                )

    # TAB 3 — MEMORY BROWSER
    with tab3:
        st.subheader("Memory Browser")

        col1, col2 = st.columns(2)
        with col1:
            browse_type = st.selectbox(
                "Filter by Memory Type",
                ["All"] + st.session_state.config["memory_types"]
            )
        with col2:
            browse_area = st.selectbox(
                "Filter by Practice Area",
                ["All"] + st.session_state.config["practice_areas"]
            )

        if st.button("Browse Memories"):
            all_memories = (
                st.session_state.memory_db.get_all_active()
            )

            if browse_type != "All":
                all_memories = [
                    m for m in all_memories
                    if m.get('memory_type') == browse_type
                ]

            if browse_area != "All":
                all_memories = [
                    m for m in all_memories
                    if m.get('practice_area') == browse_area
                ]

            st.write(f"Showing {len(all_memories)} memories")

            with st.expander(
                f"View All Memories ({len(all_memories)})"
            ):
                for memory in all_memories:
                    with st.expander(
                        f"[{memory.get('memory_type', '').upper()}] "
                        f"ID: {memory.get('id', '')} — "
                        f"{memory.get('memory_text', '')[:60]}..."
                    ):
                        st.write(memory.get('memory_text', ''))
                        render_tags(memory)
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.caption(
                                f"ID: {memory.get('id')}"
                            )
                            st.caption(
                                f"Type: {memory.get('memory_type')}"
                            )
                            st.caption(
                                f"Category: {memory.get('extraction_category')}"
                            )
                            st.caption(
                                f"Importance: {memory.get('importance')}"
                            )
                        with col2:
                            st.caption(
                                f"Practice Area: {memory.get('practice_area')}"
                            )
                            st.caption(
                                f"Matter Type: {memory.get('matter_type')}"
                            )
                            st.caption(
                                f"Outcome: {memory.get('outcome')}"
                            )
                            st.caption(
                                f"Confidence: {memory.get('confidence')}"
                            )
                        with col3:
                            st.caption(
                                f"Judge: {memory.get('judge')}"
                            )
                            st.caption(
                                f"Opposing Counsel: {memory.get('opposing_counsel')}"
                            )
                            st.caption(
                                f"Source Attorney: {memory.get('source_attorney')}"
                            )

if __name__ == "__main__":
    main()