import streamlit as st
import requests
from streamlit_mermaid import st_mermaid

API_URL = "http://localhost:8000"

st.set_page_config(page_title="RAG Dashboard", page_icon="🤖", layout="wide")

st.title("🤖 Chat with your PDF")

with st.sidebar:
    st.header("📂 Upload PDF")
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    
    if uploaded_file is not None:
        if st.button("Upload & Process"):
            with st.spinner("Uploading and indexing..."):
                files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
                try:
                    response = requests.post(f"{API_URL}/upload", files=files)
                    if response.status_code == 200:
                        st.success("Success upload ✅")
                    else:
                        st.error(f"Error: {response.text}")
                except Exception as e:
                    st.error(f"Connection Error: {e}")

    st.markdown("---")
    st.header("✨ Magic Tools")

    if st.button("📄 Generate Summary", use_container_width=True):
        with st.spinner("Reading & Summarizing... ☕"):
            try:
                response = requests.get(f"{API_URL}/generate/summary")
                if response.status_code == 200:
                    data = response.json()
                    if "summary" in data:
                        st.session_state['active_tool'] = 'summary'
                        st.session_state['summary_text'] = data["summary"]
                    elif "error" in data:
                        st.warning(f"Warning: {data['error']}")
                else:
                    st.error(f"Server Error: {response.text}")
            except Exception as e:
                st.error(f"Connection Error: {e}")

    if st.button("🎴 Generate Flashcards", use_container_width=True):
        with st.spinner("Generating Flashcards..."):
            try:
                response = requests.get(f"{API_URL}/generate/flashcards")
                if response.status_code == 200:
                    data = response.json()
                    if "flashcards" in data:
                        st.session_state['active_tool'] = 'flashcards' 
                        st.session_state['flashcards'] = data["flashcards"]
                    elif "error" in data:
                        st.warning(f"Warning: {data['error']}")
                else:
                    st.error(f"Server Error: {response.text}")
            except Exception as e:
                st.error(f"Connection Error: {e}")

    if st.button("📝 Generate Quiz", use_container_width=True):
        with st.spinner("Creating a Quiz... "):
            try:
                response = requests.get(f"{API_URL}/generate/quiz")
                if response.status_code == 200:
                    data = response.json()
                    if "quiz" in data:
                        st.session_state['active_tool'] = 'quiz'
                        st.session_state['quiz'] = data["quiz"]
                        st.session_state['user_answers'] = {}
                    elif "error" in data:
                        st.warning(f"Warning: {data['error']}")
                else:
                    st.error(f"Server Error: {response.text}")
            except Exception as e:
                st.error(f"Connection Error: {e}")

    if st.button("Generate Mind Map", use_container_width=True):
        with st.spinner("Building interactive map..."):
            try:
                response = requests.get(f"{API_URL}/generate/mindmap")
                if response.status_code == 200:
                    data = response.json()
                    if "interactive_data" in data:
                        st.session_state['active_tool'] = 'mindmap'
                        st.session_state['mindmap_data'] = data["interactive_data"]
                    elif "error" in data:
                        st.warning(f"Warning: {data['error']}")
                else:
                    st.error(f"Server Error: {response.text}")
            except Exception as e:
                st.error(f"Connection Error: {e}")

    if st.button("📊 Generate Slides", use_container_width=True):
        with st.spinner("Creating PowerPoint... "):
            try:
                response = requests.post(f"{API_URL}/generate/slides")
                if response.status_code == 200:
                    st.session_state['active_tool'] = 'slides'
                    st.session_state['ppt_data'] = response.content
                    st.success("Slides Ready! Look at the main area. ")
                else:
                    st.error(f"Server Error: {response.text}")
            except Exception as e:
                st.error(f"Connection Error: {e}")

col1, col2 = st.columns([6, 4], gap="medium")

with col1:
    st.subheader("💬 Chat")
    
    chat_container = st.container(height=500, border=True)
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    if prompt := st.chat_input("Ask something about your PDF:"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)

        with chat_container:
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                message_placeholder.markdown("Thinking... ")
                
                try:
                    payload = {"question": prompt}
                    response = requests.post(f"{API_URL}/ask", json=payload)
                    
                    if response.status_code == 200:
                        answer = response.json().get("answer", "No answer found.")
                        message_placeholder.markdown(answer)
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                    else:
                        message_placeholder.markdown("Error getting answer.")
                except Exception as e:
                    message_placeholder.markdown(f" Connection Error: {e}")

with col2:
    st.subheader("🛠️ Tools & Results")
    
    results_container = st.container(height=500, border=True)
    
    with results_container:
        if 'active_tool' not in st.session_state:
            st.info("Select a tool from the sidebar.")
        
        elif st.session_state['active_tool'] == 'summary':
            st.info("📄 **Document Summary**")
            
            if 'summary_text' in st.session_state:
                summary = st.session_state['summary_text']
                
                st.markdown(summary)
                st.markdown("---")
                
                c1, c2 = st.columns(2)
                
                with c1:
                    if st.button("🎧 Listen to Summary"):
                        with st.spinner("Generating Audio... 🗣️"):
                            try:
                                response = requests.post(f"{API_URL}/generate/audio", json={"text": summary})
                                if response.status_code == 200:
                                    st.audio(response.content, format="audio/mp3")
                                else:
                                    st.error("Audio failed.")
                            except Exception as e:
                                st.error(f"Error: {e}")

                with c2:
                    st.download_button(
                        label="📥 Download TXT",
                        data=summary,
                        file_name="summary.txt",
                        mime="text/plain",
                        use_container_width=True
                    )

        elif st.session_state['active_tool'] == 'flashcards':
            st.info("🎴 **Study Flashcards**")
            if 'flashcards' in st.session_state:
                for card in st.session_state['flashcards']:
                    with st.expander(f"❓ {card['front']}"):
                        st.success(f"**Answer:** {card['back']}")
                        
        elif st.session_state['active_tool'] == 'quiz':
            st.info("📝 **Knowledge Quiz**")
            if 'quiz' in st.session_state:
                for i, q in enumerate(st.session_state['quiz']):
                    st.write(f"**Q{i+1}: {q['question']}**")
                    
                    user_choice = st.radio(
                        "Options:", 
                        q['options'], 
                        key=f"q_{i}",
                        index=None,
                        label_visibility="collapsed"
                    )
                    
                    if user_choice:
                        if user_choice == q['answer']:
                            st.success("Correct! ✅")
                        else:
                            st.error(f"Wrong! Correct: {q['answer']}")
                    st.divider()

        elif st.session_state['active_tool'] == 'mindmap':
            st.info("🧠 **Interactive Document Structure**")
            
            if 'mindmap_data' in st.session_state:
                data = st.session_state['mindmap_data']
                
                with st.expander(f"📁 {data.get('filename', 'Document')}", expanded=True):
                    for topic in data.get('topics', []):
                        with st.expander(f"📌 {topic['title']}"):
                            for pt in topic.get('points', []):
                                with st.expander(f"🔹 {pt['sub_title']}"):
                                    st.write(f"📖 {pt['description']}")
                                    
        elif st.session_state['active_tool'] == 'slides':
            st.info("📊 **PowerPoint Presentation**")
            st.success("Presentation generated successfully! 🎉")
            
            if 'ppt_data' in st.session_state:
                st.download_button(
                    label="📥 Download PowerPoint (.pptx)",
                    data=st.session_state['ppt_data'],
                    file_name="presentation.pptx",
                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                    use_container_width=True
                )