import streamlit as st
import asyncio
from fastmcp import Client
import json
import re

# --- Page Configuration ---
st.set_page_config(page_title="🧑‍⚖️ MCP Judge", layout="wide")

# --- Custom CSS for professional look ---
st.markdown("""
<style>
    .reportview-container .main .block-container{
        padding-top: 2rem;
        padding-right: 2rem;
        padding-left: 2rem;
        padding-bottom: 2rem;
    }
    .st-emotion-cache-1kyx2k1.e1nzilvr3 {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    .st-emotion-cache-1l48y3z {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .st-emotion-cache-121p250 {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    .st-emotion-cache-1kyx2k1.e1nzilvr3 {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
    }
    .stButton>button {
        background-color: #2e8b57;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 10px 24px;
        cursor: pointer;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #3cb371;
    }
    .st-emotion-cache-1c70e28 {
        border-radius: 10px;
    }
    .stExpander {
        border-radius: 10px;
        border: 1px solid #d3d3d3;
        padding: 1rem;
    }
    .st-emotion-cache-19p3w16 {
        font-size: 1.5rem;
        font-weight: bold;
        color: #1a1a1a;
    }
</style>
""", unsafe_allow_html=True)


# --- Main App Title and Description ---
st.title("🛠️ MCP Judge")
st.markdown("An interactive interface for testing and inspecting your MCP tools.")
st.divider()

# --- Async Helper Functions ---
def get_client(url):
    return Client(url)

def run_async(coro):
    return asyncio.run(coro)

async def fetch_tools(client):
    async with client:
        return await client.list_tools()

async def call_tool(client, tool_name: str, inputs: dict = None):
    async with client:
        if inputs:
            return await client.call_tool(tool_name, inputs)
        else:
            return await client.call_tool(tool_name)

# Helper function to remove Markdown special characters
def remove_markdown_formatting(text):
    text = re.sub(r'(\*\*|__)(.*?)\1', r'\2', text)  # bold
    text = re.sub(r'(\*|_)(.*?)\1', r'\2', text)   # italics
    text = re.sub(r'#+\s*(.*)', r'\1', text)       # headers
    return text

# --- Main Layout: Two Columns with a Separator ---
left_col, separator_col, right_col = st.columns([1, 0.05, 1])

# --- Left Column: Connection and Tool Selection ---
with left_col:
    # --- Left Top: Server Connection with Form ---
    with st.container():
        st.subheader("🔌 Connection")
        with st.form(key='mcp_form'):
            mcp_url = st.text_input("Enter MCP Server URL", help="Enter the URL of your MCP server.", key="url_input")
            submit_button = st.form_submit_button(label='Connect')
        
        if submit_button:
            st.session_state.connected_url = mcp_url
            # Clear other session state variables when a new URL is submitted
            if 'tools' in st.session_state:
                del st.session_state['tools']
            if 'selected_tool' in st.session_state:
                del st.session_state['selected_tool']
            if 'show_result' in st.session_state:
                del st.session_state['show_result']

        st.divider()

    # --- Left Bottom: Tool Selection ---
    with st.container():
        if "connected_url" in st.session_state and st.session_state.connected_url:
            st.subheader("🎯 Tool Selection")
            try:
                client = get_client(st.session_state.connected_url)
                if "tools" not in st.session_state:
                    with st.spinner("Fetching tools..."):
                        st.session_state.tools = run_async(fetch_tools(client))
                tools = st.session_state.tools
            except Exception as e:
                st.error(f"❌ Failed to connect to MCP server: {e}")
                del st.session_state.connected_url # Clear URL on failure
                st.stop()

            # Helper to truncate long descriptions
            def truncate(text, max_len=60):
                return text if len(text) <= max_len else text[:max_len] + "..."

            # Create a list of tuples for display and tool object
            options_with_tools = [(f"{tool.name} — {truncate(tool.description)}", tool) for tool in tools]
            options = [""] + [o[0] for o in options_with_tools]
            display_to_tool = {o[0]: o[1] for o in options_with_tools}

            selected_display = st.selectbox(
                "Choose a Tool to Test",
                options,
                index=0
            )

            if selected_display:
                tool = display_to_tool[selected_display]
                st.session_state.selected_tool = tool

                st.markdown(f"**Selected Tool:** `{tool.name}`")
                clean_description = remove_markdown_formatting(tool.description)
                st.info(f"**Description:** {clean_description}")
        else:
            st.info("Please enter a URL and click 'Connect' to begin.")


# --- Right Column: Inputs and Outputs ---
with right_col:
    # --- Right Top: Inputs ---
    with st.container():
        st.subheader("⌨️ Provide Inputs")
        if "selected_tool" in st.session_state:
            tool = st.session_state.selected_tool
            user_inputs = {}
            with st.expander("Expand to provide inputs...", expanded=True):
                if hasattr(tool, "inputSchema") and tool.inputSchema:
                    properties = tool.inputSchema.get("properties", {})
                    required_fields = tool.inputSchema.get("required", [])

                    for input_name, prop in properties.items():
                        input_type = prop.get("type", "string")
                        input_desc = prop.get("description", "")
                        is_required = input_name in required_fields

                        label = f"{input_name}"
                        if is_required:
                            label += " *"

                        if input_type == "string":
                            user_inputs[input_name] = st.text_input(label, help=input_desc, key=f"input_{input_name}")
                        elif input_type == "integer":
                            user_inputs[input_name] = st.number_input(label, step=1, help=input_desc, key=f"input_{input_name}")
                        elif input_type == "boolean":
                            user_inputs[input_name] = st.checkbox(label, help=input_desc, key=f"input_{input_name}")
                        else:
                            user_inputs[input_name] = st.text_input(f"{label} (type: {input_type})", help=input_desc, key=f"input_{input_name}")
                else:
                    st.info("ℹ️ This tool does not require any inputs.")

            # --- Run Button ---
            if st.button("🚀 Run Tool", use_container_width=True):
                with st.spinner("Calling tool..."):
                    try:
                        client = get_client(st.session_state.connected_url)
                        selected_tool_name = tool.name
                        result = run_async(call_tool(client, selected_tool_name, user_inputs or None))
                        st.session_state.tool_result = result
                        st.session_state.show_result = True
                    except Exception as e:
                        st.error(f"❌ Error while calling tool: {e}")
                        st.session_state.show_result = False
        else:
            st.info("Please select a tool on the left to view and provide inputs.")

    st.divider()

    # --- Right Bottom: Output ---
    with st.container():
        st.subheader("📦 Tool Result")
        if "show_result" in st.session_state and st.session_state.show_result:
            result = st.session_state.tool_result
            with st.expander("View JSON Output...", expanded=True):
                if result and hasattr(result, 'content') and result.content:
                    first_item = result.content[0]
                    try:
                        parsed = json.loads(first_item.text)
                        st.json(parsed, expanded=True)
                    except (json.JSONDecodeError, TypeError):
                        st.code(first_item.text or "[Empty Result]", language="text")
                else:
                    st.info("ℹ️ No content returned by the tool.")
        else:
            st.info("ℹ️ The result will appear here after you run the tool.")
