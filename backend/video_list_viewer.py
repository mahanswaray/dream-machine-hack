import streamlit as st
import os
from lumaai import LumaAI
from dotenv import load_dotenv

load_dotenv()
# Initialize Luma AI client
client = LumaAI(auth_token=os.environ.get("LUMAAI_API_KEY"))

def get_completed_generations():
    response = client.generations.list(limit=100, offset=0)
    all_gens = response.generations
    return [gen for gen in all_gens if gen.state == "completed"]

def main():
    st.title("Luma AI Video Player")

    # Fetch completed generations
    completed_generations = get_completed_generations()

    # Display generations
    for gen in completed_generations:
        col1, col2 = st.columns([1, 3])
        
        with col1:
            if st.button(f"ID: {gen.id}", key=gen.id):
                st.session_state.selected_gen = gen

        with col2:
            if gen.assets and gen.assets.video:
                st.write(gen.request.prompt)
                st.video(gen.assets.video)
            else:
                st.write("No video available")

    # Display prompt when a generation is selected
    if hasattr(st.session_state, 'selected_gen'):
        st.subheader("Generation Details")
        st.write(f"Prompt: {st.session_state.selected_gen.prompt}")
        st.write(f"Status: {st.session_state.selected_gen.status}")
        st.write(f"Created at: {st.session_state.selected_gen.created_at}")

if __name__ == "__main__":
    main()