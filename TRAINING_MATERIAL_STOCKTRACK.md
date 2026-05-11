# StockTrack Training Manual
## Complete User Guide & Trainer Reference

**Version:** 1.0  
**Date:** April 2026  
**App:** StockTrack Stock & Requisition Management System  
**Organization:** Corporate Analytica

---

## Table of Contents
1. Getting Started (Login & Account Management)
2. System Basics & Navigation
3. Staff Workflow Guide
4. Manager Workflow Guide
5. Admin Workflow Guide
6. Common Tasks Reference
7. Troubleshooting & Support
8. Hands-On Exercises
9. Quick Reference Cards

---

## 1. Getting Started

### 1.1 Logging In

**Access URL:**  
Visit: `https://ca-stocktrack.com/app` (or your organization's StockTrack URL)

**Step-by-Step Login:**
1. Open your web browser
2. Navigate to the StockTrack application URL
3. You will see a login form with two fields:
   - **Username:** Enter your username (case-insensitive, e.g., "john_smith" or "John_Smith")
   - **Password:** Enter your password
4. Click the **Login** button
5. You will be taken to the StockTrack dashboard

**If Login Fails:**
- Verify your username and password are correct
- Check that CAPS LOCK is not enabled
- If you forget your password, contact your System Administrator
- If you still cannot log in, check the "Troubleshooting" section below

### 1.2 Password Management

**First Time Login:**
- Your System Administrator will provide your initial username and temporary password
- On your first login, you will see a notice asking you to change your password
- **You must change this password before you can use the system**

**How to Change Your Password:**

1. After logging in, look for the **"⚙️ Password Management"** section in the left sidebar
2. Click on it to expand the password management options
3. Enter:
   - **Current Password:** The password you're currently using to log in
   - **New Password:** Your new password (must be at least 8 characters with 1 uppercase letter, 1 number, and 1 special character)
   - **Confirm New Password:** Re-enter your new password to verify
4. Click **"Change Password"**
5. If successful, you'll see a green success message: "Password changed successfully!"
6. If there's an error, read the red error message and try again

**Password Requirements:**
- Minimum 8 characters long
- At least 1 uppercase letter (A-Z)
- At least 1 digit (0-9)
- At least 1 special character (!@#$%^&*)

**Example valid passwords:**
- `Secure@Pass1`
- `MyStock#2024`
- `Req$uest99`

### 1.3 Account Overview

**Your Profile:**
- Your role (Staff, Manager, or Admin) determines which pages you can see
- Your assigned property controls which stock and requisitions you work with
- Only System Administrators can change your role or property assignment

### Training Overview

**Audience:**
- Staff users (requesters and reporters)
- Managers (approvers and issuers)
- Admin users (system configuration and governance)

**Training Duration:**
- Full session: 2 hours 15 minutes
- Staff-only version: 60 minutes
- Manager-only version: 75 minutes
- Admin-only version: 90 minutes

**Training Goal:**
By the end of training, every user can complete their daily workflow in StockTrack without support.

**Learning Outcomes:**
Participants will be able to:
- Log in and navigate the system confidently
- Find stock, interpret status, and use filters
- Create and track requisitions
- Approve and issue requisitions correctly (manager/admin)
- Manage stock master data and users safely (admin)
- Report usage and upload supporting documents
- Troubleshoot common issues

---

## 2. System Basics & Navigation

### 2.1 Understanding User Roles

**Three Main Roles:**

| Role | Purpose | Key Responsibilities | Who Uses It |
|------|---------|--------|-----------|
| **Staff** | Request and report | Submit requisitions, add usage reports, upload documents | Operational staff, cleaners, handlers |
| **Manager** | Review and approve | Approve/reject requisitions, issue stock, handle shortfalls | Department heads, inventory coordinators |
| **Admin** | System setup & governance | Create users, maintain master data, reconciliation | System administrator, finance team |

### 2.2 The Main Dashboard

**After Login, You See:**
1. **Left Sidebar:** Navigation menu with pages available to your role
2. **Main Content Area:** Your current page (starts with Overview)
3. **Top Bar:** App title, user menu, and support information

### 2.3 Navigation Sidebar

**The left sidebar shows different pages based on your role:**

**Staff Users See:**
- Overview (dashboard with key information)
- Stock (view available items)
- My Requisitions (create and track your requests)
- My Requisition History (view past requests)

**Manager Users See:**
- Overview
- Stock (view available items and current inventory)
- Requisition Approvals (review and approve requests)
- Issue Stock (issue approved stock)
- My Requisitions (view their own requests)
- Issuance Log (view history of issued stock)
- Reorder List (see items below restock levels)

**Admin Users See:**
- All Manager pages PLUS:
- Storerooms (manage storage locations)
- Suppliers (manage vendor information)
- Properties (manage facility/property information)
- Users (create and manage user accounts)
- Reconciliation (verify inventory accuracy)

### 2.4 Key Status Definitions

**Understanding Requisition Status:**

| Status | What It Means | Who Sees It | Action Needed |
|--------|-------------|-----------|--------------|
| **Pending** | Waiting for manager review | Staff, Manager | Manager must review and approve/reject |
| **Approved** | Manager approved, ready to issue | Staff, Manager, Admin | Manager issues the stock |
| **Partially Issued** | Some of the approved quantity has been issued | All | May need more issuing or tracking usage |
| **Issued** | All approved stock has been issued | All | Staff should add usage report |
| **Rejected** | Manager declined the request | Staff, Manager | Staff can modify and resubmit if needed |
| **Cancelled** | Staff withdrew the request | All | Request is closed; staff can create new one if needed |

### 2.5 Understanding Stock Status

**Stock Status Indicators:**
- **In Stock / Available:** Item is available for issue
- **Low Stock:** Item quantity is below the reorder level (reorder needed soon)
- **Out of Stock:** Item currently unavailable
- **Unlisted:** Item not in the stock master database (must be procured specially)

---

## 3. Session Flow (Trainer Reference)

### Module 1: Welcome and System Basics (15 min)
**Trainer Actions:**
- Welcome participants and explain session goal
- Show login screen; have each participant log in
- Explain what StockTrack is used for: "StockTrack controls how we request, approve, and issue stock. Every step is tracked, so we always know what's happening."
- Explain user roles and their daily work
- Show menu layout and where to find key pages
- Explain important statuses (use the table above)
- Answer clarification questions
- **Transition:** "Now let's see how staff use the system to request what they need."

### Module 2: Staff Workflow (35 min)
**Trainer Actions:**
- Walk through each staff page together
- **Stock page:** Show filters, search, and how to interpret availability
- **My Requisitions:** Create a sample requisition live; explain each field
- Add stocked items; add unlisted items
- Explain when to use each type
- Submit the sample requisition
- Show how status changes when manager approves
- Participants practice: each creates a test requisition
- Review common mistakes
- **Transition:** "Great. Now let's see how managers review and approve these requests."

### Module 3: Manager Workflow (35 min)
**Trainer Actions:**
- Show Requisition Approvals page
- Demonstrate the approval process: review purpose, check stock, decide quantity, add notes
- Explain the difference between "stocked lines" and "procurement lines"
- Show approval vs. rejection vs. partial approval
- Move to Issue Stock page
- Demonstrate issuing: select requisition, enter issued quantity, confirm
- Show what happens when quantity requested exceeds stock available
- Review shortfall and restock-needed tables
- Participants practice: approve and issue a requisition
- Q&A
- **Transition:** "Finally, let's look at admin controls that keep the system secure and accurate."

### Module 4: Admin Workflow (30 min)
**Trainer Actions:**
- Show Overview page: alerts, critical information
- Show Properties and Storerooms: explain structure and purpose
- Show Suppliers: add/edit vendor information
- Show Stock master data management
- Show Users page: create user, assign role, assign property
- Explain access control: users only see their assigned property
- Show Reconciliation basics: why it matters, what discrepancies mean
- Participants practice: create a test user
- Demo update user role and property assignment
- Q&A

### Module 5: Assessment and Q&A (20 min)
**Trainer Actions:**
- Short practical challenge per role (use Exercises A, B, C below)
- Recap the golden rules (see section below)
- Recap common mistakes and how to avoid them
- Open floor for questions
- Collect feedback for improvement
- Provide take-away materials: quick reference cards, contact info for support

---

## 4. Role-Based Daily Workflows & Step-by-Step Guides

### 4.1 Staff Workflow (Requesters)

**Daily Flow:**
1. Log in
2. Check Stock page for available items
3. Create requisitions as needed
4. Track status and manager feedback
5. When stock is received, add usage report
6. Upload supporting documents if required

**Step-by-Step: View Stock Availability**
1. Click **"Stock"** in the left sidebar
2. You see a table showing:
   - Item name
   - Quantity available
   - Reorder level
   - Current status (In Stock, Low Stock, Out of Stock)
3. To search for a specific item, use the search box at the top
4. Items marked "Low Stock" are below reorder level (procurement pending)

**Step-by-Step: Create a Requisition**
1. Click **"My Requisitions"** in the left sidebar
2. Click the **"New Requisition"** button (top right or clearly marked)
3. Fill in the form:
   - **Purpose:** Describe what the stock is for (e.g., "Cleaning supplies for monthly deep clean", not "needed urgently")
   - **Urgency:** Select Low, Medium, or High
4. **Add Stocked Items:**
   - Click **"Add Stocked Item"**
   - Select item from dropdown (items currently in stock)
   - Enter quantity needed
   - Click to confirm
5. **Add Unlisted Items (if needed):**
   - Click **"Add Unlisted Item"**
   - Enter item description (e.g., "Industrial mop handles, heavy duty")
   - Enter quantity needed
   - Add notes about specifications (optional but helpful)
   - Click to confirm
6. Review your basket to ensure all items are correct
7. Click **"Submit Requisition"** button
8. You'll see a success message; requisition now shows in your list as "Pending"

**Step-by-Step: Track Your Requisition Status**
1. Click **"My Requisitions"** in the left sidebar
2. Find your requisition in the list
3. Click on it to see:
   - Current status (Pending, Approved, Partially Issued, Issued, Rejected, Cancelled)
   - Lines requested and their approval status
   - Manager's review notes and comments
   - Your comments section to reply
4. If status is **Approved:** Wait for manager to issue
5. If status is **Partially Issued:** You received some items; manager may issue more
6. If status is **Issued:** All approved quantity has been issued
7. If status is **Rejected:** Read manager's notes; you can modify and resubmit

**Step-by-Step: Add Usage Report**
1. After you have received and used the stock, go to **"My Requisition History"**
2. Find the completed requisition (status: "Issued")
3. Click on it to open details
4. Scroll to the **"Usage Report"** section
5. Enter:
   - **Report Date:** When you used/completed the stock
   - **Quantity Used:** How much was actually used
   - **Remaining:** How much is left (if not all used)
   - **Comments:** Any relevant notes (e.g., "2 rolls damaged on arrival")
6. Click **"Submit Usage Report"**
7. If you have documents (photos, receipts, evidence), you can upload them:
   - Click **"Upload Document"** or similar button
   - Select file from your computer
   - Add document name/description
   - Confirm upload

### 4.2 Manager Workflow (Approvers & Issuers)

**Daily Flow:**
1. Log in
2. Check Overview for pending requisitions
3. Open Requisition Approvals
4. Review and approve/reject/partially approve each
5. Open Issue Stock page
6. Issue approved stock against approved requisitions
7. Review shortfall/restock-needed alerts
8. Communicate shortfalls to procurement/admin

**Step-by-Step: Review and Approve Requisitions**
1. Click **"Requisition Approvals"** in the left sidebar
2. You see a list of all pending requisitions (from all staff in your view)
3. For each requisition:
   - Read the **Purpose** field carefully
   - Review the **Urgency** level
   - Check **Stocked Lines:** See what's available vs. requested
   - Check **Procurement Lines:** Items not in stock (requires procurement)
4. To approve a requisition:
   - Click on it to open details
   - Review all lines and available stock
   - For each stocked line:
     - Enter **Approved Quantity** (can be less than requested if stock is limited)
     - Enter **Allocated Storeroom** (where to issue from)
   - For procurement lines:
     - Add notes like "Source from Supplier ABC" or "Defer to next month"
   - In the **Review Notes** field, explain your decision (if different from requested)
     - Example: "Approved 8 instead of 10; allocate from Main Storeroom. Procurement team to source heavy-duty mops."
   - Click **"Approve"** button
5. Requisition status changes to **"Approved"**; staff can see your notes
6. To partially approve or reject:
   - Follow same process but reduce quantities significantly or leave all at 0
   - Add clear notes explaining why
   - Click **"Reject"** or approve with reduced quantities

**Step-by-Step: Issue Stock**
1. Click **"Issue Stock"** in the left sidebar
2. You see approved requisitions ready to issue
3. For each one you want to issue:
   - Click on the requisition to open it
   - You see each approved line item
   - For each line:
     - The system shows: Approved Quantity vs. Available Stock
     - Enter **Quantity to Issue** (cannot exceed approved or available)
     - Enter **Actual Storeroom** (where you're issuing from)
     - Add **Notes** if there's anything unusual (e.g., "Issued 8; 2 units not available")
   - Review the totals before confirming
   - Click **"Issue"** to confirm
4. System shows what was issued and if there's a shortfall (couldn't issue full approved amount)
5. Requisition status changes to:
   - **"Partially Issued"** if you issued some but not all approved quantity
   - **"Issued"** if you issued all approved quantity

**Step-by-Step: Handle Shortfalls and Restocking**
1. After issuing, review the **"Shortfall"** and **"Restock Needed"** alerts/tables
2. **Shortfall:** Approved quantity could not be fully issued (insufficient stock)
3. **Restock Needed:** Items are below reorder level and need procurement
4. For each shortfall or restock-needed item:
   - Note the item name and quantity
   - Communicate with your Procurement/Admin team
   - Example: "Need 5 more mop handles for Req #1234; also general stock low"
   - Wait for procurement to source and add to inventory

### 4.3 Admin Workflow (System Setup & Governance)

**Daily Flow:**
1. Log in
2. Check Overview for critical alerts
3. Review pending requisitions and issued stock
4. Maintain master data (as needed):
   - Properties, Storerooms, Suppliers, Stock items
5. Maintain user accounts (as needed):
   - Create users, assign roles, assign property
6. Run reconciliation to verify accuracy
7. Handle user support and data issues

**Step-by-Step: Create a New User**
1. Click **"Users"** in the left sidebar
2. Click **"Add New User"** or **"Create User"** button
3. Fill in the form:
   - **Full Name:** User's full name (e.g., "Sipho Mthembu")
   - **Username:** Short unique identifier (e.g., "sipho_m", "smthembu")
     - Use lowercase, underscores OK, no spaces
   - **Role:** Select from dropdown:
     - Staff (can request and report usage)
     - Manager (can approve and issue)
     - Admin (can manage system, users, and master data)
   - **Property:** Select which property they work at (e.g., "Main Facility", "Branch 2")
   - **Password:** System generates initial password (show to user separately)
4. Click **"Create User"**
5. Confirm user was created successfully
6. **Important:** Provide the username and initial password to the new user via secure channel (never in email)
7. User must change password on first login

**Step-by-Step: Update User Role or Property**
1. Click **"Users"** in the left sidebar
2. Find the user in the list (search/filter if needed)
3. Click on the user to open their profile
4. To change role:
   - Click the **"Role"** field
   - Select new role from dropdown
   - Click **"Save"** or confirm
5. To change property:
   - Click the **"Property"** field
   - Select new property from dropdown
   - Click **"Save"** or confirm
6. User's access will update automatically

**Step-by-Step: Delete a User**
1. Click **"Users"** in the left sidebar
2. Find the user in the list
3. Click on the user to open their profile
4. Click **"Delete User"** button (usually at the bottom or marked with ⚠️)
5. Confirm deletion (you'll be asked "Are you sure?")
6. User account is removed; they cannot log in anymore

**Step-by-Step: Manage Properties and Storerooms**
1. Click **"Properties"** in the left sidebar
2. View existing facilities/properties
3. To add a new property:
   - Click **"Add Property"** button
   - Enter property name (e.g., "Main Office", "Branch 1")
   - Enter location details
   - Click **"Save"**
4. Click **"Storerooms"** to manage storage locations
5. Each storeroom should be assigned to a property
6. Storerooms determine where stock is physically stored and issued from

**Step-by-Step: Manage Suppliers**
1. Click **"Suppliers"** in the left sidebar
2. View existing supplier list
3. To add a new supplier:
   - Click **"Add Supplier"** button
   - Enter supplier name, contact info, address
   - Click **"Save"**
4. Suppliers are used when requisitions need procurement

**Step-by-Step: Manage Stock Master Data**
1. In the admin menu (if available), find "Stock" or "Inventory Settings"
2. View current stock items
3. To add a new stock item:
   - Enter item name
   - Set reorder level (quantity at which restock is needed)
   - Assign to supplier
   - Set unit of measure
   - Click **"Save"**
4. To edit existing item:
   - Click on the item
   - Update information
   - Click **"Save"**

**Step-by-Step: Run Reconciliation**
1. Click **"Reconciliation"** in the left sidebar
2. You'll see options to:
   - View reconciliation history
   - Run a new reconciliation check
3. To reconcile:
   - The system compares stock records with requisition/issuance transactions
   - Any discrepancies are flagged
   - Review flagged items
   - Investigate: Was stock recorded correctly? Are transactions accurate?
   - Correct any errors in the system
   - Mark reconciliation as complete
4. Use reconciliation to catch data entry errors early

---

## 5. Common Tasks Reference

### 5.1 Golden Rules (Always Follow These)

- ✅ Always enter a **clear purpose** when requesting (not "needed urgently" but "10 rolls for monthly cleaning")
- ✅ Use **stocked items** for regular inventory requests
- ✅ Use **unlisted items** ONLY for special procurement needs
- ✅ **Never bypass approval** before issuing stock
- ✅ **Managers:** Always add review notes when approving (especially if reducing quantity)
- ✅ **Managers:** Check stock availability before approving
- ✅ **Staff:** Add usage reports after stock is received and used
- ✅ Treat comments and notes as **official communication** (be specific and professional)
- ✅ Keep data **clean and specific** (no abbreviations, no vague descriptions)
- ✅ Follow the workflow order: **Request → Approve → Issue → Report**

### 5.2 Common Questions Answered

**Q: Can I request items not in the system?**  
A: Yes! Use "Add Unlisted Item" when creating a requisition. This tells your manager that procurement is needed.

**Q: What if the manager approves less than I requested?**  
A: Read their review notes to understand why. You can accept the reduced quantity or resubmit a new requisition for the remainder.

**Q: What if I don't use all the stock I received?**  
A: When adding your usage report, enter the actual quantity used. This keeps our records accurate.

**Q: Can I cancel a submitted requisition?**  
A: Yes. Go to "My Requisitions", find the requisition, and click "Cancel" if it's still pending approval.

**Q: What if I forget my password?**  
A: Contact your System Administrator. They can reset your password and provide a temporary one. You'll change it on next login.

**Q: Why can't I see certain menu items?**  
A: Your role determines which pages you can see. Staff users see fewer pages than managers. Contact your admin if you need additional access.

**Q: Why does the system show "Out of Stock" for an item I know we have?**  
A: The inventory might not have been entered into the system yet. Ask your manager or admin to check and update stock records.

---

## 6. Troubleshooting & Support

### 6.1 Login Issues

| Problem | Likely Cause | Solution |
|---------|-------------|----------|
| "Incorrect username or password" | Wrong credentials entered | Verify username (case doesn't matter) and password. Check CAPS LOCK is off. Try again carefully. |
| Cannot access the URL | Network or app is down | Check your internet connection. Try a different browser. Wait a few minutes and try again. |
| Browser shows "404 Page Not Found" | Wrong URL | Verify the correct URL with your admin. Bookmark it for future use. |
| Login works but page keeps reloading | Browser cache issue | Clear browser cache and cookies, then reload. Try a different browser. |
| First login shows mandatory password change | Normal first-time process | You must change your temporary password before using the system. Follow the password change steps in section 1.2. |

### 6.2 Requisition Issues

| Problem | Likely Cause | Solution |
|---------|-------------|----------|
| "Could not submit requisition" | Missing required field | Ensure you have: filled Purpose, entered at least one item, entered quantities. All fields marked with * are required. |
| Cannot find item in stocked items dropdown | Item not in system | Use "Add Unlisted Item" instead. Type the item description you need. |
| Approved quantity is different from what I requested | Manager made a decision | Read manager's review notes. They explain why quantity was changed. If you disagree, discuss with your manager. |
| Requisition status hasn't changed for days | Waiting for manager action | Check with your manager to see if they've reviewed it. Sometimes approval takes time due to workload. |
| Cannot add more items after first item | May have hit a system limit | Try refreshing the page. If still stuck, contact admin. |

### 6.3 Stock & Issuance Issues

| Problem | Likely Cause | Solution |
|---------|-------------|----------|
| Cannot issue full approved quantity | Insufficient stock available | Issue what's available (partial issue). Create a shortfall note. Coordinate with procurement for the remainder. |
| Stock shows but requisition shows as "Unlisted" | Item legitimately not in system | This is correct. Procurement team will source it separately. You'll receive it when ordered. |
| Shortfall alert keeps appearing | Insufficient restock has occurred | Contact your procurement/admin team. Items are below reorder level. They need to order more. |
| Cannot find requisition to issue | Requisition not approved yet | Only approved requisitions appear. Manager must review and approve first. |

### 6.4 Password & Account Issues

| Problem | Likely Cause | Solution |
|---------|-------------|----------|
| Password change shows error | Password doesn't meet requirements | Ensure new password has: 8+ characters, 1 uppercase letter, 1 digit, 1 special character (!@#$%^&*). Example: `StrongPass1!` |
| "Current password incorrect" when changing password | Wrong current password entered | Double-check current password. It must be exactly right. Try again. |
| Locked out of account | Too many failed login attempts | Wait 15-30 minutes. If still locked, contact admin to unlock. |
| Cannot see password change option | May be first-time login flow | If you see a notice about mandatory password change, follow those instructions instead. |
| Admin reset your password but you forgot temporary password | Temporary password lost | Contact admin to reset again. Ask them to provide it in a secure way. |

### 6.5 Menu Access Issues

| Problem | Likely Cause | Solution |
|---------|-------------|----------|
| "Cannot see Requisition Approvals page" | You don't have Manager role | Only managers and admins see this page. Your role is Staff. Contact admin if this is incorrect. |
| "Cannot see Users page" | You don't have Admin role | Only admins see this page. Contact your system administrator. |
| Sidebar menu disappeared | Browser rendering issue | Refresh the page (press F5 or Ctrl+R). Try a different browser. |
| Menu items are grayed out | Item not available for your role | Your role doesn't have permission to access. This is intentional for data security. |

### 6.6 Data & Reporting Issues

| Problem | Likely Cause | Solution |
|---------|-------------|----------|
| Cannot upload supporting document | File format not supported or file too large | Check file format (usually PDF, image, or Word). File should be under 10MB. Try a different file. |
| Missing historical data in reports | Data not entered yet or role doesn't have access | If you can't see data from a certain date, ask your manager or admin if it was entered. Staff only see their own requisitions. |
| Reconciliation shows discrepancy | Data entry error or missing transaction | Review the flagged items carefully. Check if all transactions were recorded. Correct as needed with admin help. |

### 6.7 General Troubleshooting Steps

**If something isn't working:**

1. **Refresh the page:** Press F5 or Ctrl+R
2. **Log out and log in again:** Go to top-right user menu, select "Logout", then log in again
3. **Try a different browser:** Chrome, Firefox, Edge, Safari—most modern browsers work
4. **Clear browser cache:** Go to browser settings > Clear browsing data. Clear cookies and cache. Reload app.
5. **Check your internet connection:** Make sure you have stable internet
6. **Wait a moment:** Sometimes the app is temporarily slow. Wait 30 seconds and try again.
7. **Contact your admin:** If issue persists, contact your System Administrator with:
   - What you were trying to do
   - What error you saw (screenshot if possible)
   - When the issue started
   - Any other details that might help

### 6.8 Getting Help

**For Login/Password Help:**  
Contact your System Administrator

**For Workflow Questions:**  
Ask your Manager or Trainer

**For System Issues:**  
Contact your System Administrator with details of the problem

**Support Contact Information:**  
- System Administrator: [Contact info provided by organization]
- Manager: [Manager contact info]
- Help Desk: [If available]

---

## 7. Hands-On Exercises

### Exercise A: Staff Requisition with Mixed Basket

**Scenario:**  
A cleaner needs 10 toilet rolls and 2 heavy-duty mops. Toilet rolls are in stock, but mops are not regularly stocked and need to be sourced from a supplier.

**Tasks:**
1. Log in as a Staff user
2. Create a new requisition
3. Enter Purpose: "Supplies for monthly deep clean of Main Building"
4. Set Urgency: "Medium"
5. Add Stocked Item: "Toilet Rolls" - quantity 10
6. Add Unlisted Item: "Heavy-duty mops" - quantity 2, with note "Industrial grade, long handle"
7. Submit requisition
8. Confirm the requisition appears in "My Requisitions" with status "Pending"
9. Note the requisition ID for next exercise

**Expected Result:**
- Requisition created successfully
- Status shows "Pending"
- Two lines visible: one stocked, one unlisted
- No errors in submission

### Exercise B: Manager Approval and Issue

**Scenario:**  
You are the manager. Review the requisition from Exercise A and issue what is available.

**Tasks:**
1. Log in as a Manager user
2. Go to "Requisition Approvals"
3. Find the requisition from Exercise A
4. Review the purpose and items
5. For the toilet rolls line:
   - Approve quantity: 10 (or less if stock is lower)
   - Select storeroom to allocate from
   - Add note: "Approved as requested"
6. For the mops line:
   - Add note: "Defer procurement. Will source next month."
7. Approve the requisition
8. Go to "Issue Stock"
9. Find the approved requisition
10. Issue the approved quantity of toilet rolls
11. Note any shortage for the mops
12. Check if "Restock Needed" alert appears

**Expected Result:**
- Requisition status changes to "Approved"
- After issuing: status changes to "Partially Issued" (mops still pending procurement)
- No errors during approval or issue
- Staff member can see manager's notes

### Exercise C: Admin User Creation

**Scenario:**  
A new staff member joins your organization. They work at the Main Facility.

**Tasks:**
1. Log in as an Admin user
2. Go to "Users"
3. Click "Add New User"
4. Enter:
   - Full Name: "Jane Doe"
   - Username: "jane_d"
   - Role: "Staff"
   - Property: "Main Facility"
5. Create the user
6. Provide username and temporary password to the new user (in person or secure message)
7. Have new user log in with temporary credentials
8. New user changes their password (using section 1.2 steps)
9. Verify new user can see "Stock" and "My Requisitions" pages
10. Verify new user cannot see "Requisition Approvals" (Staff role doesn't have access)

**Expected Result:**
- User account created successfully
- New user can log in with temporary password
- New user can change password successfully
- Role-based access control works: Staff sees only Staff pages
- User only has access to "Main Facility" data

### Exercise D: Multi-Step Workflow (Full Cycle)

**Scenario:**  
Complete an end-to-end workflow: request → approve → issue → report usage

**Tasks:**
1. **Staff:** Create a requisition requesting 5 cleaning cloths (stocked) and 1 floor wax (unlisted)
   - Purpose: "Maintenance supplies for weekly cleaning"
   - Urgency: "Low"
2. **Manager:** Review and approve: "Approve 5 cloths. Wax: defer to next delivery. Check shortfall on wax."
3. **Manager:** Issue the 5 cloths to the requisition
4. **Staff:** Check "My Requisitions" and see status is "Partially Issued"
5. **Staff:** Add a usage report: "Used 5 cloths, no waste. All items in good condition."
6. **Admin:** Run a reconciliation check to verify all transactions are recorded
7. All participants review the full audit trail of this single requisition

**Expected Result:**
- Full workflow completes without errors
- Audit trail is complete and accurate
- All statuses update correctly
- Data remains consistent throughout

---

## 8. Trainer Resources

### 8.1 Trainer Script

**Opening Script (3 minutes)**

"Welcome everyone. Today we are learning StockTrack by following the same steps you do in real work. We will keep this practical and real. By the end of this session, you should be able to complete your role-specific tasks confidently and independently.

StockTrack is not complicated, but it is important. It controls how we request stock, approve requests, and issue items. Every step is tracked, so we always know what was requested, who approved it, when it was issued, and how it was used. This helps us manage our budget, control access to resources, and stay accountable.

We'll start with staff because this is where everything begins: identifying what you need and submitting a clear request. Then we'll move to manager activities: reviewing, approving, and issuing with proper controls. Finally, we'll cover admin setup, which keeps the system secure and accurate. Ready? Let's begin."

**Transition to Staff Module**

"We start with the staff journey because this is where demand begins: identifying what is needed and submitting clear requisitions. Managers can't approve if they don't understand what you need, and they can't issue if approval hasn't happened. So good staff requisitions are the foundation of good stock control."

**Transition to Manager Module**

"Now that requests are submitted, we move to manager actions: review, approve, and issue with stock controls. Managers are the gatekeepers. They make sure we don't run out of essential items, they allocate available stock fairly, and they flag procurement needs so admin can source missing items."

**Transition to Admin Module**

"Finally, we cover admin controls that keep data clean and secure: creating and managing users, setting up properties and storerooms, maintaining supplier and stock data, and running reconciliation checks. Admins are the librarians of StockTrack—everything stays organized, accurate, and accessible."

**Closing Script (2 minutes)**

"Great work, everyone. You've learned the system and practiced the main workflows. Here are the takeaways:

1. The workflow order is: **Request → Approve → Issue → Report**. If every role does this consistently, our stock data stays accurate and reliable.

2. **Clear communication** matters. Write a good purpose, add notes when you approve or reject, add usage reports when you receive items. These notes are how we all stay on the same page.

3. **Follow the rules.** Don't bypass approval. Don't issue before it's approved. Don't create fake users. These controls protect our resources and keep us accountable.

4. **When you're stuck**, reference the quick guide, ask a colleague, or contact your admin. There's no shame in asking.

I'll leave each of you with a quick reference guide you can keep on your desk. Use it whenever you need a reminder. Thank you for your attention, and I look forward to seeing you use StockTrack confidently starting tomorrow."

### 8.2 Trainer Checklist Before Session

- [ ] Confirm StockTrack app is running and accessible
- [ ] Test login with demo users (staff, manager, admin)
- [ ] Confirm password change functionality works
- [ ] Prepare demo requisition data
- [ ] Ensure at least one low-stock item exists for demo
- [ ] Check that test users have correct role assignments
- [ ] Prepare test supplier and property data
- [ ] Print or distribute quick reference guides (see section 9 below)
- [ ] Test projector/screen sharing if presenting
- [ ] Have backup plan if app is unavailable
- [ ] Prepare flip chart or whiteboard for notes
- [ ] Keep this guide open during facilitation for quick reference

### 8.3 Trainer Checklist After Session

- [ ] Collect feedback from participants (what went well, what needs improvement)
- [ ] Document top 5 questions asked (update FAQ section next time)
- [ ] Verify all participants can log in on their own
- [ ] Confirm all participants have changed their temporary password
- [ ] Log any system issues or data problems encountered
- [ ] Schedule follow-up refresher session (1 week, 2 weeks, 1 month out)
- [ ] Share quick reference guide with all participants (email or printed)
- [ ] Capture improvement requests for next app update
- [ ] Update this training manual based on what you learned

---

## 9. Quick Reference Cards (Print & Keep at Your Desk)

### QUICK REFERENCE: STAFF WORKFLOW

**In 5 Steps:**
1. Click **Stock** → See what's available
2. Click **My Requisitions** → Click **New Requisition**
3. Enter **Purpose** (be specific!), add items, click **Submit**
4. Status changes from Pending → Approved → Issued
5. Add **Usage Report** after you receive and use items

**Key Pages:**
- **Stock:** View available items and quantities
- **My Requisitions:** Create requests, track status, see manager notes
- **My Requisition History:** View past requests, add usage reports

**Password:** ⚙️ Password Management → Enter old password → Enter new (8+ chars, 1 uppercase, 1 number, 1 special char)

**Common Errors & Fixes:**
| Error | Fix |
|-------|-----|
| "Cannot submit" | Ensure Purpose is filled and at least 1 item is added |
| Status not changing | Refresh page; manager may not have reviewed yet |
| Cannot find item | Use "Add Unlisted Item" for items not in dropdown |

---

### QUICK REFERENCE: MANAGER WORKFLOW

**In 6 Steps:**
1. Click **Requisition Approvals** → Review pending requests
2. For each request: Read purpose, check stock availability
3. Decide: Approve full quantity, partial, or reject
4. Add **Review Notes** explaining your decision
5. Click **Approve**; move to **Issue Stock**
6. Issue the approved quantity; handle shortfalls

**Key Pages:**
- **Overview:** See pending requisitions at a glance
- **Requisition Approvals:** Review and approve/reject requests
- **Issue Stock:** Issue approved stock to requisitions
- **Reorder List:** See items below restock level
- **Issuance Log:** View history of what was issued

**Decision Guide:**
- **Full Approve:** Stock available, request reasonable, urgent
- **Partial Approve:** Stock limited; approve what's available; note reason
- **Reject:** Request unclear or no valid need; add clear explanation
- **Defer Unlisted Items:** "Will source next month" or "Check with procurement"

**Common Errors & Fixes:**
| Error | Fix |
|-------|-----|
| Cannot issue full approved amount | Insufficient stock; issue what you have (partial issue OK) |
| Shortfall alert | Coordinate with procurement; items need reordering |
| Requisition missing | Check if it's been approved yet; only approved ones show in Issue Stock |

---

### QUICK REFERENCE: ADMIN WORKFLOW

**In 6 Steps:**
1. Click **Users** → Manage user accounts, roles, properties
2. Click **Properties** & **Storerooms** → Configure locations
3. Click **Suppliers** → Maintain vendor list
4. Monitor **Overview** for alerts and pending items
5. Click **Reconciliation** → Verify inventory accuracy
6. Address discrepancies and update records

**Key Pages:**
- **Overview:** Dashboard with alerts and critical info
- **Users:** Create users, assign role, assign property
- **Properties:** Configure facilities/locations
- **Storerooms:** Configure storage areas
- **Suppliers:** Manage vendors
- **Reconciliation:** Verify inventory accuracy
- **Issuance Log:** Audit all issued stock
- **Reorder List:** Track items below reorder level

**User Creation:**
1. Full Name, Username (lowercase, no spaces), Role, Property
2. System generates temp password → give to user securely
3. User changes password on first login
4. User can now access system with new password

**Common Errors & Fixes:**
| Error | Fix |
|-------|-----|
| User can't see a page | Check their role; Staff users don't see Approvals or Users pages |
| User can't see certain data | Check their Property assignment; users see only their assigned property |
| Cannot create user | Ensure all required fields are filled; username must be unique |

---

### QUICK REFERENCE: KEY TERMS

| Term | Means |
|------|-------|
| **Stocked Item** | Item currently in the system and available for issue |
| **Unlisted Item** | Item not normally stocked; requires special procurement |
| **Reorder Level** | Quantity at which stock needs to be reordered |
| **Low Stock** | Current quantity is below reorder level |
| **Out of Stock** | Item currently not available |
| **Shortfall** | Quantity approved but cannot be issued due to insufficient stock |
| **Restock Needed** | Items below reorder level that should be ordered soon |
| **Approval** | Manager's decision to approve a request (full, partial, or rejection) |
| **Issuance** | Physical removal of stock from storeroom against an approved requisition |
| **Usage Report** | Staff record of how much they actually used and any issues |
| **Reconciliation** | Audit to verify stock records match actual transactions |

---

### QUICK REFERENCE: PASSWORD REQUIREMENTS

**Must Include:**
✓ At least 8 characters  
✓ At least 1 uppercase letter (A-Z)  
✓ At least 1 digit (0-9)  
✓ At least 1 special character (!@#$%^&*)

**Examples:**
- ✓ `StockTrack1!`
- ✓ `Req@uest2024`
- ✓ `Secure#Pass99`
- ✗ `password` (no uppercase, digit, or special char)
- ✗ `Pass1` (too short, no special char)
- ✗ `PASSWORD!` (no digit)

---

### QUICK REFERENCE: GOLDEN RULES

1. ✅ Always enter a **clear purpose** (not "needed urgently" but "10 rolls for monthly cleaning")
2. ✅ Use **stocked items** for regular requests
3. ✅ Use **unlisted items** ONLY for special procurement
4. ✅ **Managers:** Approve only against available stock
5. ✅ **Never bypass approval** before issuing
6. ✅ **Always add notes** when approving with changes (e.g., why you reduced qty)
7. ✅ **Staff:** Add usage reports after receiving items
8. ✅ Be **specific and professional** in all comments
9. ✅ Follow the order: **Request → Approve → Issue → Report**
10. ✅ When stuck, **ask your manager or admin**—never guess

---

### QUICK REFERENCE: EMERGENCY CONTACTS

**Password Help:**  
Contact: ___________________________

**Workflow Questions:**  
Contact: ___________________________

**System Issues:**  
Contact: ___________________________

**Emergency / Data Issues:**  
Contact: ___________________________

---

## 10. Post-Training Adoption Plan

### Week 1: Onboarding
- Daily 15-minute check-in with user champions from each role
- Capture questions and document common confusion points
- Provide real-time support as users complete their first transactions

### Week 2: Quality Assurance
- Spot-check 5–10 requisitions for:
  - Clear purpose description
  - Appropriate use of stocked vs. unlisted items
  - Accurate item quantities
- Spot-check issue transactions for:
  - Approval compliance (no unapproved issues)
  - Accurate stock reduction
- Provide feedback to users on quality

### Week 3: Reinforcement
- Mini-session on weak areas identified in Week 2
- Demonstrate best practices with real examples from system
- Confirm all users can complete their role workflow independently

### Month 1 Milestone
- Spot audit of 20 transactions (requisitions, approvals, issues, reports)
- Verify data accuracy and control compliance
- Collect metrics:
  - Avg time from submit to approval
  - % of requisitions approved vs. rejected
  - % of requisitions with clear purpose
  - Stock discrepancies (if any)
- Schedule refresher session if significant issues found

---

## 11. Additional Resources

### 11.1 Frequently Asked Questions (FAQ)

**Q: How long should a requisition take to be approved?**  
A: Usually 24–48 hours. During busy periods, it may take longer. Check with your manager if it's been more than 2 business days.

**Q: Can I edit a requisition after I submit it?**  
A: Only if it's still pending (not yet approved). If approved, you'll need to cancel and create a new one.

**Q: What happens if I request too much and waste it?**  
A: Usage reports help us track this. Be honest in your reports. Multiple waste reports will be reviewed with you and your manager to improve planning.

**Q: Can multiple people access the same property?**  
A: Yes, many staff can be assigned to the same property. They can see each other's requisitions and usage reports for that property.

**Q: Do I need to attach a document to every requisition?**  
A: No, documents are optional. Attach them only when you have supporting evidence (e.g., photos of damage, proof of cost).

**Q: What if manager approved but didn't issue for a week?**  
A: It happens sometimes due to workload or pending stock arrivals. Check with your manager. If you need the item urgently, follow up.

**Q: Can I submit a requisition for someone else?**  
A: No, each user submits their own requisitions. If your colleague needs items, they must log in and submit themselves.

**Q: What if I discover a data error (wrong quantity, wrong item)?**  
A: Contact your admin immediately. They can correct the records. Don't assume it's right just because the system shows it.

**Q: Is there a way to see trends (e.g., which items are used most)?**  
A: Yes, if your system admin has enabled reports. Ask them for reports on usage trends, costs, and requisition patterns.

**Q: What's the difference between "Partially Issued" and "Rejected"?**  
A: **Partially Issued** = Approved and some stock was issued, but not all approved qty yet (more may come).  
**Rejected** = Not approved; request was declined by manager.

### 11.2 Best Practices

**For Staff:**
- Plan your requests ahead when possible (don't wait until you run out)
- Group similar items into one requisition (easier for manager to review)
- Be specific about item specifications (size, color, quantity, quality)
- Read manager's notes even if approved; you might learn why they changed quantities

**For Managers:**
- Review pending requisitions at the start of each day
- Approve quickly if the request is reasonable and stock is available
- When rejecting, always explain why (helps staff learn what requests are acceptable)
- When reducing quantity, explain the business reason (helps staff understand constraints)
- Coordinate with admin on shortfalls; communicate timelines to staff

**For Admins:**
- Ensure master data is accurate (suppliers, properties, storerooms, stock items)
- Set reorder levels based on historical usage
- Create new users promptly; provide credentials securely
- Run reconciliation monthly (or more often if you discover discrepancies)
- Keep audit trail clean; don't delete old records (use reconciliation instead)

### 11.3 Compliance & Governance

**Data Integrity:**
- Every transaction (request, approval, issue, report) is logged
- Do not attempt to circumvent the workflow (e.g., issuing without approval)
- Admins audit transactions for compliance monthly

**Access Control:**
- Users can only see their assigned property's data
- Staff see only their own requisitions and requisitions they can contribute to
- Managers see all requisitions for their property(ies)
- Admins see all data but should only edit what's necessary

**Privacy:**
- Usernames and hashed passwords are stored securely
- Password is never displayed in plain text
- Each user is responsible for keeping their password confidential
- If you share your password, you are responsible for all actions taken under your account

**Record Retention:**
- All records (requisitions, issuances, usage reports) are retained indefinitely for audit purposes
- Deleted records cannot be recovered (only use delete in exceptional cases, approved by admin)
- Reconciliation creates audit snapshots; keep these for compliance

---

## 12. Appendix: Technical Information

### 12.1 Supported Browsers
- Google Chrome (recommended)
- Mozilla Firefox
- Microsoft Edge
- Safari (Mac/iOS)

**Recommended Screen Resolution:** 1024×768 or higher

### 12.2 File Upload Specifications
- **Max file size:** 10 MB
- **Supported formats:** PDF, JPEG, PNG, GIF, Microsoft Word (.docx), Excel (.xlsx)
- **Recommended:** PDF for formal documents, JPEG/PNG for photos

### 12.3 Reports & Analytics (If Enabled)
Ask your admin if the following reports are available:
- Requisition Summary by Date Range
- Stock Usage by Item
- Stock Usage by Department/Property
- Manager Approval Metrics
- Inventory Reconciliation Report

---

## Document Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | April 2026 | Initial comprehensive training manual | Corporate Analytica |

---

## Contact & Support

**Questions About This Manual?**  
Contact your System Administrator or Training Lead

**Technical Support:**  
Contact your System Administrator

**Training Feedback:**  
Email your manager or speak with your training coordinator

---

**Last Updated:** April 28, 2026  
**Recommended Review Date:** July 2026  
**Manual Owner:** Corporate Analytica StockTrack Administration Team

© 2026 Corporate Analytica. All rights reserved. StockTrack™ is proprietary software.
