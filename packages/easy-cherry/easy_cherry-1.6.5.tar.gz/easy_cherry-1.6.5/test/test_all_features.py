# ==============================================================================
# Comprehensive Test Suite for the easy_cherry Slack Notifier Library 🍒
#
# This script is designed to be a "health check" for every major feature of
# the library. It runs from top to bottom and provides clear, descriptive
# output for each test case.
#
# To Run This Script:
# 1. Make sure you have installed the library (e.g., 'pip install .')
# 2. Set your Slack token as an environment variable:
#    export SLACK_BOT_TOKEN='xoxb-your-secret-token-here'
# 3. Update the CONFIGURATION section below with valid Slack details.
# 4. Run the script: python test_all_features.py
# ==============================================================================

import os
import csv
from easy_cherry import SlackNotifier
import time

# --- CONFIGURATION ---
# IMPORTANT: Before running, change these values to match your Slack workspace.
# Using placeholders will cause tests to fail.
TEST_CHANNEL    = "#test_channel"      # A public channel the bot is a member of.
TEST_USER_EMAIL = "vinay@test.com"       # The email of a real user in your workspace.
TEST_USER_ID    = "UhkddiuKX"           # The Member ID (starts with 'U') of a real user.
# ---------------------

print("--- Starting Full Library Test Suite for easy_cherry 🍒 ---")

# --- Test Case 1: Initialization ---
# Objective: Verify that the SlackNotifier can be initialized correctly
# and that the logging can be controlled.
print("\n[BEGIN TEST 1: INITIALIZATION]")
token = os.getenv("SLACK_BOT_TOKEN")
if not token:
    print("  [FATAL] The 'SLACK_BOT_TOKEN' environment variable is not set. Exiting.")
    exit()

try:
    print("  > Testing initialization with logging ENABLED...")
    # We use log=True here to get detailed output for the rest of the tests.
    notifier = SlackNotifier(token=token, log=True, timeout=60)
    print("  [SUCCESS] Notifier initialized with logging.")
    
    print("  > Testing initialization with logging DISABLED...")
    silent_notifier = SlackNotifier(token=token, log=False)
    print("  [SUCCESS] Notifier initialized silently.")

except Exception as e:
    print(f"  [FATAL] Could not initialize SlackNotifier. Error: {e}")
    exit()
print("[END TEST 1]")
time.sleep(1) # Brief pause to respect API rate limits

# --- Test Case 2: Basic Messaging ---
# Objective: Test sending simple text, markdown, and auto-detected HTML.
print("\n[BEGIN TEST 2: BASIC MESSAGING]")
print("  > 2a: Sending plain text message...")
notifier.send(TEST_CHANNEL, "Test 2a: This is a plain text message.")
print("  [SUCCESS] Plain text message sent.")
time.sleep(1)

print("  > 2b: Sending a message with Slack's `mrkdwn`...")
mrkdwn_message = "Test 2b: This message uses *bold text* and _italic text_."
notifier.send(TEST_CHANNEL, mrkdwn_message)
print("  [SUCCESS] Markdown message sent.")
time.sleep(1)

print("  > 2c: Sending an HTML message to test auto-detection...")
html_message = "<h1>Test 2c: HTML Report</h1><p>This was sent as an <b>HTML</b> string and should be <i>formatted</i> by easy_cherry automatically.</p>"
notifier.send(TEST_CHANNEL, html_message)
print("  [SUCCESS] HTML message sent and auto-detection worked.")
print("[END TEST 2]")
time.sleep(1)

# --- Test Case 3: Multi-Recipient Send ---
# Objective: Verify that a single message can be sent to a mix of target types.
print("\n[BEGIN TEST 3: MULTI-RECIPIENT SEND]")
recipients = [TEST_CHANNEL, TEST_USER_EMAIL, TEST_USER_ID]
print(f"  > Sending a single alert to multiple recipients: {recipients}")
multi_send_results = notifier.send(recipients, "Test 3: This is a high-priority alert sent to a channel, an email, and a user ID simultaneously.")

print("  > Analyzing multi-send results:")
for target, response in multi_send_results.items():
    if response and response.get("ok"):
        print(f"    ✅ [SUCCESS] Message successfully sent to '{target}'.")
    else:
        error = response.get('error', 'unknown') if response else 'unknown'
        print(f"    ❌ [FAILURE] Could not send to '{target}'. Reason: {error}")
print("[END TEST 3]")
time.sleep(1)

# --- Test Case 4: Advanced Messaging with Block Kit ---
# Objective: Test the sending of rich, structured messages.
print("\n[BEGIN TEST 4: ADVANCED MESSAGING (BLOCK KIT)]")
print("  > Constructing a rich message using Block Kit helpers...")
report_blocks = [
    notifier.create_header_block("Test 4: Quarterly Performance Review 📊"),
    {"type": "divider"},
    notifier.create_fields_section({
        "Revenue Growth": "+15%",
        "New Customers": "1,200",
        "Market Sentiment": "Positive",
        "Overall Status": "✅ On Track"
    })
]
notifier.send_blocks(TEST_CHANNEL, report_blocks, fallback_text="Quarterly Performance Review is ready.")
print("  [SUCCESS] Rich Block Kit message sent.")
print("[END TEST 4]")
time.sleep(1)

# --- Test Case 5: File Uploads ---
# Objective: Test uploading various common file types, both individually and together.
print("\n[BEGIN TEST 5: FILE UPLOADS]")
temp_files_to_clean = []
try:
    # Create a set of diverse, temporary files for testing
    print("  > Creating temporary files for upload: .txt, .csv, .pdf, .docx")
    
    # 5a: Simple Text File
    with open("report.txt", "w") as f:
        f.write("This is the main text report for Test 5.\n")
    temp_files_to_clean.append("report.txt")

    # 5b: CSV File
    with open("data.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["ProductID", "Revenue", "Region"])
        writer.writerow(["A101", "50000", "North"])
    temp_files_to_clean.append("data.csv")

    # 5c & 5d: PDF and Word Document (as simple text files for testing purposes)
    # Note: We create simple text files and name them with .pdf and .docx extensions.
    # This is sufficient to test the library's upload mechanism, as it just handles the file bytes.
    with open("document.pdf", "w") as f:
        f.write("This is the content of the test PDF file.\n")
    temp_files_to_clean.append("document.pdf")
    
    with open("meeting_notes.docx", "w") as f:
        f.write("These are the meeting notes in the test DOCX file.\n")
    temp_files_to_clean.append("meeting_notes.docx")

    print("  > 5a: Testing single file upload...")
    notifier.send(TEST_CHANNEL, "Test 5a: Here is the weekly text report.", file_paths=["report.txt"])
    print("  [SUCCESS] Single file uploaded.")
    time.sleep(2) # Give Slack a bit more time for file uploads

    print("  > 5b: Testing multi-file upload with diverse types...")
    notifier.send(
        TEST_CHANNEL, 
        "Test 5b: Here is a package of project files (.csv, .pdf, .docx).", 
        file_paths=["data.csv", "document.pdf", "meeting_notes.docx"]
    )
    print("  [SUCCESS] Multiple, diverse files uploaded.")
    
finally:
    # This 'finally' block ensures our temporary files are always deleted,
    # even if one of the tests above fails.
    print("  > Cleaning up temporary files...")
    for f in temp_files_to_clean:
        if os.path.exists(f):
            os.remove(f)
    print("  [SUCCESS] Cleanup complete.")
print("[END TEST 5]")

print("\n--- All Tests Finished Successfully ---")

