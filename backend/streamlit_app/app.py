import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import date, timedelta, datetime
import re

# ==========================
# CONFIG
# ==========================
API_URL = "http://127.0.0.1:8000/api/v1"
STAGES = ["New", "Contacted", "Proposal Sent", "Negotiation", "Closed - Won", "Closed - Lost"]
STAGE_COLORS = {
    "New": "#007BFF",           # Blue
    "Contacted": "#FFA500",      # Orange
    "Proposal Sent": "#8A2BE2",  # BlueViolet
    "Negotiation": "#20B2AA",    # LightSeaGreen
    "Closed - Won": "#28A745",   # Green
    "Closed - Lost": "#DC3545",  # Red
}
HEADERS = {}
EVENT_TYPES = [
    "", "Wedding", "Betrothal / Engagement", "Birthday Party", "Office Event",
    "Housewarming (Grahapravesam)", "Baby Shower (Valaikappu)", "Ear Piercing (Kathani Vizha)",
    "Puberty Ceremony (Manjal Neerattu Vizha)", "Saree Ceremony", "Get-together", "Other"
]

st.set_page_config(page_title="Catering CRM", layout="wide")

# ==========================
# FUNCTIONS
# ==========================

def initialize_session_state():
    if "comments_db" not in st.session_state:
        st.session_state.comments_db = []
    # This new line adds storage for attachments
    if "attachments_db" not in st.session_state:
        st.session_state.attachments_db = []

def login():
    st.title("Coimbatore Caterers CRM - Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            login_data = {"username": username, "password": password}
            resp = requests.post(f"{API_URL}/auth/login", data=login_data)
            if resp.status_code == 200:
                st.session_state["token"] = resp.json()["access_token"]
                st.rerun()
            else:
                st.error("Invalid credentials")

def update_lead_stage(lead_id):
    new_stage = st.session_state[f"move_{lead_id}"]
    payload = {"stage": new_stage}
    resp = requests.patch(f"{API_URL}/leads/{lead_id}/stage", json=payload, headers=HEADERS)
    if resp.status_code == 200:
        st.toast(f"Moved to {new_stage}!", icon="✅")
    else:
        st.toast("Failed to update stage.", icon="❌")

def view_lead_details(lead_id):
    st.session_state['editing_lead_id'] = lead_id

def back_to_pipeline():
    st.session_state['editing_lead_id'] = None

# --- Callback function to handle the file upload automatically ---
def handle_file_upload(lead_id):
    uploaded_file = st.session_state.get(f'file_uploader_{lead_id}')
    if uploaded_file:
        file_bytes = uploaded_file.getvalue()
        
        if len(file_bytes) > 5 * 1024 * 1024: # 5MB limit
            st.error("File is too large. Maximum size is 5MB.")
            return

        # THIS IS THE FIX:
        # Instead of sending to a server, we save the file to our in-memory list.
        new_attachment = {
            "lead_id": lead_id,
            "filename": uploaded_file.name,
            "content": file_bytes, # Store the file's content
            "size_bytes": uploaded_file.size
        }
        st.session_state.attachments_db.append(new_attachment)
        
        st.success(f"File '{uploaded_file.name}' attached successfully!")
        st.rerun()


def delete_attachment(attachment_id, attachment_name):
    """Sends a DELETE request to the backend API to delete an attachment."""
    url = f"{API_URL}/attachments/{attachment_id}"
    try:
        response = requests.delete(url, headers=HEADERS)
        if response.status_code == 200:
            st.toast(f"Attachment '{attachment_name}' deleted.", icon="🗑️")
            st.rerun()
        else:
            st.toast(f"Failed to delete. Server: {response.status_code}", icon="❌")
    except requests.exceptions.RequestException as e:
        st.error(f"Connection to server failed: {e}")

def get_leads_as_csv():
    """Converts the current list of leads into a downloadable CSV format."""
    # Convert the list of lead dictionaries into a pandas DataFrame
    leads_df = pd.DataFrame(st.session_state.leads)
    
    # Convert the DataFrame to a CSV string, and encode it for download
    # index=False means we don't write the row numbers into the file
    return leads_df.to_csv(index=False).encode('utf-8')

# ==========================
# RENDER FUNCTIONS
# ==========================

def render_sidebar_form():
    with st.sidebar:
        st.header("➕ Add Lead")
        # The form code is unchanged and correct.
        with st.form("add_lead_form_sidebar", clear_on_submit=True):
            name = st.text_input("Name*", placeholder="Name")
            ten_digit_phone = st.text_input("10-Digit Mobile Number*", placeholder="9876543210", max_chars=10)
            email = st.text_input("Email*", placeholder="cc@example.com")
            st.markdown("---")
            event_type = st.selectbox("Event Type", options=EVENT_TYPES)
            guests_count = st.number_input("Number of Guests", min_value=0, step=1)
            today = date.today()
            tomorrow = today + timedelta(days=1)
            two_years_from_now = today + timedelta(days=365*2)
            event_date = st.date_input(
                "Event Date", value=None, min_value=tomorrow, max_value=two_years_from_now
            )
            notes = st.text_area("Notes")
            submitted = st.form_submit_button("Create Lead", use_container_width=True)
            if submitted:
                # Form validation and submission logic is unchanged.
                phone_pattern = re.compile(r"^\d{10}$")
                if not name or not ten_digit_phone or not email:
                    st.warning("Please fill out all mandatory fields (*).")
                elif not phone_pattern.match(ten_digit_phone):
                    st.warning("Please enter exactly 10 digits for the mobile number.")
                else:
                    full_phone_number = f"+91{ten_digit_phone}"
                    new_lead_data = { "name": name, "phone": full_phone_number, "email": email, "event_type": event_type, "guests_count": guests_count if guests_count > 0 else None, "event_date": event_date.isoformat() if event_date else None, "notes": notes, "stage": "New" }
                    resp = requests.post(f"{API_URL}/leads/", json=new_lead_data, headers=HEADERS)
                    if resp.status_code == 200:
                        st.success("Lead created!")
                        st.rerun()
                    else:
                        st.error("Failed to create lead.")

def render_dashboard(leads_data):
    st.header("Dashboard")
    # Dashboard rendering logic is unchanged.
    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("Total Leads", len(leads_data))
        if leads_data:
            df = pd.DataFrame(leads_data)
            stage_counts = df['stage'].value_counts().reset_index()
            stage_counts.columns = ['Stage', 'Count']
            st.dataframe(stage_counts, use_container_width=True, hide_index=True)
    with col2:
        if leads_data:
            fig = px.pie(stage_counts, values='Count', names='Stage', title='Leads by Stage')
            st.plotly_chart(fig, use_container_width=True)

def render_lead_management(leads_data):
    # This is your existing code for the header and export button - it is preserved.
    header_col, btn_col = st.columns([3, 1])
    with header_col:
        st.header("Pipeline")
    with btn_col:
        st.download_button(
           label="📥 Export to CSV",
           data=get_leads_as_csv(), 
           file_name=f"catering_leads_{date.today().isoformat()}.csv",
           mime='text/csv',
           use_container_width=True
        )

    st.markdown("---")
    columns = st.columns(len(STAGES))
    for i, stage in enumerate(STAGES):
        with columns[i]:
            # --- CHANGE 1: The header is now colored ---
            color = STAGE_COLORS.get(stage, "black") # Get color from dict, default to black
            st.markdown(f"<h3 style='color: {color};'>{stage}</h3>", unsafe_allow_html=True)
            # --- END OF CHANGE 1 ---

            leads_in_stage = [lead for lead in leads_data if lead['stage'] == stage]
            if not leads_in_stage:
                st.markdown("_No leads in this stage._")
            for lead in leads_in_stage:
                with st.container(border=True):
                    st.subheader(lead['name'])
                    
                    # --- CHANGE 2: The event type is now bold and stylish ---
                    if lead.get('event_type'):
                        st.markdown(f"<p style='font-weight: bold; color: black; font-size: 1.1em;'>🎉 {lead['event_type']}</p>", unsafe_allow_html=True)
                    # --- END OF CHANGE 2 ---

                    # The rest of your code for the card is preserved
                    st.selectbox(
                        "Move:", 
                        options=STAGES, 
                        index=STAGES.index(lead['stage']), 
                        key=f"move_{lead['id']}", 
                        on_change=update_lead_stage, 
                        args=(lead['id'],)
                    )

                    edit_col, menu_col = st.columns([4, 1])
                    with edit_col:
                        st.button(
                            "✏️ Edit Card", 
                            key=f"edit_{lead['id']}", 
                            on_click=view_lead_details, 
                            args=(lead['id'],),
                            use_container_width=True
                        )
                    with menu_col:
                        with st.popover("⋮", use_container_width=True):
                            st.error("This action cannot be undone.")
                            st.button(
                                "Delete Lead", 
                                key=f"delete_{lead['id']}",
                                on_click=delete_lead,
                                args=(lead['id'],),
                                use_container_width=True,
                                type="primary" 
                            )

# --- RENDER LEAD DETAIL VIEW (MODIFIED) ---
def render_lead_detail_view(lead_id):
    lead = next((l for l in st.session_state.leads if l['id'] == lead_id), None)
    if not lead:
        st.error("Lead not found."); st.button("Back to Pipeline", on_click=back_to_pipeline); return

    st.button("← Back to Pipeline", on_click=back_to_pipeline)
    st.title(lead['name'])
    st.markdown(f"**Status:** `{lead['stage']}`")
    st.markdown("---")

    col1, col2 = st.columns([2, 1])

    with col1:
        # Description
        st.subheader("Description")
        description = st.text_area("Lead Notes", value=lead.get('notes', ''), height=150, label_visibility="collapsed")
        if description != lead.get('notes', ''):
            if st.button("Save Description"):
                resp = requests.patch(f"{API_URL}/leads/{lead['id']}", json={"notes": description}, headers=HEADERS)
                if resp.status_code == 200: st.toast("Description saved!", icon="✅"); st.rerun()
                else: st.error("Failed to save description.")

        # Attachments
        st.subheader("Attachments")

        # Read attachments from the in-memory list
        lead_attachments = [a for a in st.session_state.attachments_db if a["lead_id"] == lead_id]
        
        if lead_attachments:
            for att in lead_attachments:
                att_col1, att_col2 = st.columns([4, 1])
                size_mb = att.get('size_bytes', 0) / (1024 * 1024)
                att_col1.markdown(f"📄 **{att['filename']}** (*{size_mb:.2f} MB*)")
                
                # Use st.download_button to provide a download link for the in-memory file
                att_col2.download_button(
                    label="Download",
                    data=att['content'],
                    file_name=att['filename'],
                    mime='application/octet-stream', # Generic type for downloads
                    key=f"download_{att['filename']}_{att['lead_id']}", # Unique key
                    use_container_width=True
                )
        else:
            st.info("No attachments yet.")

        ## CHANGELOG: Corrected the help text to 5MB. The on_change callback is the correct, modern way to do this.
        st.file_uploader(
            "Upload a document", type=['pdf', 'doc', 'docx'], key=f'file_uploader_{lead_id}',
            on_change=handle_file_upload, args=(lead_id,), help="Max file size: 5MB"
        )

        # Comments
        st.subheader("Comments")

        # Read comments from the in-memory list instead of the network
        lead_comments = [c for c in st.session_state.comments_db if c["lead_id"] == lead_id]
        
        if lead_comments:
            # Sort and display the comments that are in memory
            for comment in sorted(lead_comments, key=lambda c: c['created_at'], reverse=True):
                ts = comment['created_at'].strftime('%b %d, %Y at %I:%M %p')
                with st.container(border=True):
                    st.caption(f"**{comment.get('author', 'User')}** on {ts}")
                    st.write(comment['text'])
        else:
            st.info("No comments yet. Add one below!")

        with st.form("comment_form"):
            new_comment_text = st.text_area("Add a comment", label_visibility="collapsed")
            submitted = st.form_submit_button("Add Comment")
            if submitted and new_comment_text.strip():
                # THIS IS THE FIX:
                # Instead of requests.post, we add the comment directly to our in-memory list.
                new_comment = {
                    "lead_id": lead_id,
                    "text": new_comment_text,
                    "author": "Admin",  # You can change this later
                    "created_at": datetime.now() # We add the current timestamp
                }
                st.session_state.comments_db.append(new_comment)
                
                st.toast("Comment added!", icon="💬")
                st.rerun()


    with col2:
        # Contact/Event details display (unchanged)
        st.subheader("Contact Details")
        st.markdown(f"**📞 Phone:** {lead.get('phone', 'N/A')}\n\n**✉️ Email:** {lead.get('email', 'N/A')}")
        st.subheader("Event Details")
        event_date_str = "Not set"
        if lead.get('event_date'):
            event_date_str = datetime.fromisoformat(lead['event_date']).strftime('%B %d, %Y')
        st.markdown(f"**🎉 Type:** {lead.get('event_type') or 'N/A'}\n\n**👥 Guests:** {lead.get('guests_count') or 'N/A'}\n\n**🗓️ Date:** {event_date_str}")

def delete_lead(lead_id):
    """
    Sends a DELETE request to the backend API to delete a lead.
    """
    # Find the lead's name first to give a better success message
    lead_to_delete = next((l for l in st.session_state.leads if l['id'] == lead_id), None)
    lead_name = lead_to_delete['name'] if lead_to_delete else "the lead"

    # Construct the URL for the DELETE request, as specified by your test
    url = f"{API_URL}/leads/{lead_id}"

    try:
        # Make the network call to your backend
        response = requests.delete(url, headers=HEADERS)

        # Check if the backend responded with success (status code 200)
        if response.status_code == 200:
            st.toast(f"Lead '{lead_name}' has been deleted.", icon="🗑️")
            # Rerun the app. This will cause the main page to re-fetch the
            # list of leads from the backend, and the deleted lead will be gone.
            st.rerun()
        else:
            # Show an error if the backend failed to delete the lead
            st.toast(f"Failed to delete lead. Server responded with: {response.status_code}", icon="❌")
            
    except requests.exceptions.RequestException as e:
        # Show an error if the frontend couldn't connect to the backend
        st.error(f"Connection to server failed: {e}")

# ==========================
# MAIN APP
# ==========================
if "token" not in st.session_state:
    login()
else:
    initialize_session_state()
    HEADERS["Authorization"] = f"Bearer {st.session_state['token']}"
    if 'editing_lead_id' not in st.session_state: st.session_state['editing_lead_id'] = None

    # Fetch data only when necessary
    if 'leads' not in st.session_state or st.session_state.get('editing_lead_id') is None:
        try:
            resp = requests.get(f"{API_URL}/leads/", params={"limit": 1000}, headers=HEADERS)
            if resp.status_code != 200:
                st.error("Could not load data. Your session may have expired."); st.stop()
            st.session_state.leads = resp.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Connection to API failed: {e}"); st.stop()

    # Sidebar Navigation
    st.sidebar.title("Navigation")
    st.session_state.view = st.sidebar.radio("Go to", ["Dashboard", "Lead Management"], label_visibility="collapsed")
    st.sidebar.markdown("---")
    # Only show the "Add Lead" form on the main pipeline view
    if st.session_state.view == "Lead Management" and st.session_state.get('editing_lead_id') is None:
        render_sidebar_form()

    # Main Page Content Routing
    if st.session_state.editing_lead_id is not None:
        render_lead_detail_view(st.session_state.editing_lead_id)
    else:
        st.title("Simple Catering CRM")
        if st.session_state.view == "Dashboard":
            render_dashboard(st.session_state.leads)
        elif st.session_state.view == "Lead Management":
            render_lead_management(st.session_state.leads)