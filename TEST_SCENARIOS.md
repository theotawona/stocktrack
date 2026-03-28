# StockTrack Test Scenarios

## Test Data Setup
- **Admin User**: `admin` / password (admin@stocktrack.co.za)
- **Manager User**: `manager` / password (manager@stocktrack.co.za)
- **Staff User 1**: `staff` / password (staff@stocktrack.co.za) - Property: Sandton Gardens (ID: 1)
- **Staff User 2**: `staff2` / password (staff2@livethecity.co.za) - Property: Rosebank View (ID: 2)
- **Properties**: 
  - Sandton Gardens (ID: 1) with storerooms and items
  - Rosebank View (ID: 2) with storerooms and items

---

## 1. Authentication & Login

### Test 1.1: Login with Valid Credentials
- [ ] Open app and login as `admin`
- [ ] Verify redirected to Stock page
- [ ] Verify username displayed in sidebar

### Test 1.2: Login with Invalid Credentials
- [ ] Try login with wrong password
- [ ] Verify error message appears
- [ ] Verify user not logged in

### Test 1.3: Session Persistence
- [ ] Login as `staff`
- [ ] Refresh page (F5)
- [ ] Verify still logged in and session maintained

### Test 1.4: Logout
- [ ] Login as any user
- [ ] Click logout button (if available: sidebar)
- [ ] Verify redirected to login page

---

## 2. Role-Based Access Control

### Test 2.1: Admin Access
- [ ] Login as `admin`
- [ ] Verify can access: Stock, Issue, Reconcile, Users, Disperse, Reorder, My Requisitions
- [ ] Verify all pages load without "access denied" messages

### Test 2.2: Manager Access
- [ ] Login as `manager`
- [ ] Verify can access: Stock, Issue, Reconcile, Disperse, Reorder, My Requisitions
- [ ] Verify **cannot** access Users page (should see message or redirect)

### Test 2.3: Staff Access
- [ ] Login as `staff`
- [ ] Verify can access: Stock, Issue, Reconcile, Reorder, My Requisitions
- [ ] Verify **cannot** access Users page
- [ ] Verify data filtered to their property (Sandton Gardens)

### Test 2.4: Unauthorized Page Access
- [ ] Login as `staff`
- [ ] Try manually navigating to `/users` in URL
- [ ] Verify redirected or access denied message

---

## 3. Property-Based Filtering for Staff

### Test 3.1: Staff Views Only Their Property Stock
- [ ] Login as `staff` (Sandton Gardens property)
- [ ] Go to Stock page
- [ ] Verify only items from Block A Storeroom and Basement Store (Sandton Gardens) appear
- [ ] Verify items from Rosebank View (staff2's property) do NOT appear

### Test 3.2: Staff Cannot Add Stock for Other Properties
- [ ] Login as `staff` (Sandton Gardens)
- [ ] Try to add item to storeroom
- [ ] Verify only Sandton Gardens storerooms available in dropdown

### Test 3.3: Staff Cannot Issue Stock from Other Properties
- [ ] Login as `staff` (Sandton Gardens)
- [ ] Go to Issue page
- [ ] Try to select items
- [ ] Verify only Sandton Gardens items available

### Test 3.4: Different Staff See Different Data
- [ ] Logout and login as `staff2` (Rosebank View)
- [ ] Go to Stock page
- [ ] Verify only Rosebank View items shown (e.g., Paint, Shower Heads, Plumber's Tape)
- [ ] Verify Sandton Gardens items NOT visible

---

## 4. User Management & Property Assignment

### Test 4.1: Add New Staff User with Property
- [ ] Login as `admin`
- [ ] Go to Users page
- [ ] Click "Add user"
- [ ] Fill form:
  - Username: `newstaff`
  - Full name: `New Staff Member`
  - Email: `newstaff@example.com`
  - Role: `staff`
  - Property: `Sandton Gardens`
  - Password: `password123`
- [ ] Click "Add user"
- [ ] Verify success message
- [ ] Verify new user appears in user table with property showing "Sandton Gardens"

### Test 4.2: Add Staff User Without Property Assignment
- [ ] Login as `admin`
- [ ] Add user with Role: `staff`
- [ ] Select "Assign property" → "(None)"
- [ ] Verify user created with property showing "(None)"

### Test 4.3: Assign Property to Existing User
- [ ] Login as `admin`
- [ ] Go to Users page
- [ ] Select user: `staff2`
- [ ] Action: "Assign property"
- [ ] Select property: `Rosebank View`
- [ ] Click "Apply"
- [ ] Verify success message
- [ ] Verify table shows "Rosebank View" for staff2

### Test 4.4: Change User's Assigned Property
- [ ] Login as `admin`
- [ ] Select user: `staff`
- [ ] Action: "Assign property"
- [ ] Change from "Sandton Gardens" to "Rosebank View"
- [ ] Click "Apply"
- [ ] Verify property updated in table
- [ ] **Important**: Logout and login as `staff` to verify session updates with new property

### Test 4.5: Clear Property Assignment
- [ ] Login as `admin`
- [ ] Select user: `newstaff`
- [ ] Action: "Assign property" → "(None)"
- [ ] Click "Apply"
- [ ] Verify property shown as "(None)"

### Test 4.6: Change User Role
- [ ] Login as `admin`
- [ ] Select user: `newstaff`
- [ ] New role: `manager`
- [ ] Action: "Change role"
- [ ] Click "Apply"
- [ ] Verify role changed in table

### Test 4.7: Delete User
- [ ] Login as `admin`
- [ ] Select user: `newstaff`
- [ ] Action: "Delete user"
- [ ] Click "Apply"
- [ ] Verify user removed from table
- [ ] Try to login as deleted user → should fail

---

## 5. Stock Management

### Test 5.1: Admin/Manager Can Add Stock
- [ ] Login as `admin`
- [ ] Go to Stock page
- [ ] Add new item:
  - Storeroom: `Block A Storeroom`
  - Name: `Test Item`
  - Category: `Testing`
  - QTY: `10`
  - Min QTY: `3`
  - Unit Cost: `5.00`
- [ ] Click "Add item"
- [ ] Verify item appears in stock table

### Test 5.2: Staff Cannot Add Stock
- [ ] Login as `staff`
- [ ] Go to Stock page
- [ ] Verify "Add item" form NOT visible or disabled

### Test 5.3: View Item Details
- [ ] Login as `admin`
- [ ] Go to Stock page
- [ ] Click on any item row
- [ ] Verify item details displayed (name, qty, cost, etc.)

### Test 5.4: Low Stock Alert
- [ ] Login as `admin`
- [ ] Add item with QTY: 2, Min QTY: 5
- [ ] Go to Stock page
- [ ] Verify status badge shows "Low" for this item

### Test 5.5: Out of Stock
- [ ] Login as `admin`
- [ ] Add item with QTY: 0
- [ ] Go to Stock page
- [ ] Verify status badge shows "Out of stock"

---

## 6. Issue Stock

### Test 6.1: Manager Issues Stock
- [ ] Login as `manager`
- [ ] Go to Issue Stock page
- [ ] Select item: `LED Bulbs (E27)`
- [ ] Enter recipient: `John Dlamini`
- [ ] Enter quantity: `4`
- [ ] Click "Issue"
- [ ] Verify success message
- [ ] Verify stock quantity decreased

### Test 6.2: Staff Can Issue Stock (For Their Property)
- [ ] Login as `staff` (Sandton Gardens)
- [ ] Go to Issue Stock page
- [ ] Issue item from Sandton Gardens storeroom
- [ ] Verify succeeds

### Test 6.3: Staff Cannot Issue from Other Property Stock
- [ ] Login as `staff` (Sandton Gardens)
- [ ] Go to Issue Stock page
- [ ] Verify only Sandton Gardens items available
- [ ] Cannot select Rosebank View items

### Test 6.4: Cannot Issue More Than Available
- [ ] Login as `admin`
- [ ] Select item with qty: 5
- [ ] Try to issue: 10
- [ ] Verify error: "Only 5 unit(s) of 'XXX' in stock"

### Test 6.5: Issue History
- [ ] Login as `admin`
- [ ] Go to Stock page
- [ ] Click on item that has been issued
- [ ] Verify issuance history shows recent issues

---

## 7. Reconciliation

### Test 7.1: Perform Reconciliation
- [ ] Login as `admin`
- [ ] Go to Reconcile page
- [ ] Select storeroom: `Block A Storeroom`
- [ ] For each item, enter counted quantity
- [ ] Click "Save Reconciliation"
- [ ] Verify success message

### Test 7.2: View Reconciliation History
- [ ] Login as `admin`
- [ ] Go to Reconcile page
- [ ] Verify past reconciliations listed
- [ ] Click on reconciliation to see details

### Test 7.3: Reconciliation Discrepancies
- [ ] Perform reconciliation with counted qty different from recorded
- [ ] Verify diff calculated correctly (e.g., recorded 10, counted 8 = diff -2)
- [ ] Verify report shows discrepancies

---

## 8. Requisitions & My Requisitions

### Test 8.1: Staff Creates Requisition
- [ ] Login as `staff` (Sandton Gardens)
- [ ] Go to My Requisitions page
- [ ] Click "Create requisition"
- [ ] Fill form:
  - Storeroom: `Block A Storeroom`
  - Purpose: `Monthly supplies restock`
  - Urgency: `Normal`
  - Add items: Select 2-3 items, enter quantities
- [ ] Click "Create"
- [ ] Verify requisition created with status "Pending"
- [ ] Verify reference number generated (e.g., RQ-2026-001)

### Test 8.2: View Own Requisitions
- [ ] Login as `staff`
- [ ] Go to My Requisitions page
- [ ] Verify all requisitions created by this user listed
- [ ] Click on requisition to see full details

### Test 8.3: Manager Reviews Requisition
- [ ] Login as `manager` (property: null, sees all)
- [ ] Go to Reorder page (or similar manager view)
- [ ] Find pending requisition from staff
- [ ] Click to review
- [ ] Enter review note: `Approved for dispersal`
- [ ] Click "Approve"
- [ ] Verify status changed to "Approved"

### Test 8.4: Admin Disperses Stock
- [ ] Login as `admin`
- [ ] Go to Disperse Stock page
- [ ] Select approved requisition
- [ ] Verify quantities match approved amounts
- [ ] Click "Disperse"
- [ ] Verify status changed to "Dispersed"
- [ ] Verify stock quantities updated

### Test 8.5: Staff Cannot See Other Property Requisitions
- [ ] Login as `staff` (Sandton Gardens)
- [ ] Go to My Requisitions page
- [ ] Verify only requisitions from Sandton Gardens shown
- [ ] Create requisition, verify it only appears for Sandton Gardens staff

---

## 9. Staff Features

### Test 9.1: Add Usage Report to Requisition
- [ ] Login as `staff`
- [ ] Go to My Requisitions
- [ ] Click on dispersed requisition
- [ ] Scroll to "Add usage report" section
- [ ] Enter report: `Items used for quarterly maintenance. All stock accounted for.`
- [ ] Click "Add report"
- [ ] Verify report appears below with username and timestamp

### Test 9.2: View Usage Reports
- [ ] Click on same requisition
- [ ] Verify all usage reports displayed chronologically

### Test 9.3: Upload Document to Requisition
- [ ] Go to My Requisitions
- [ ] Click on requisition
- [ ] Scroll to "Upload document" section
- [ ] Select a file (e.g., test PDF or image)
- [ ] Click "Upload"
- [ ] Verify document appears with filename and timestamp

### Test 9.4: Download Document
- [ ] Verify uploaded document shown in requisition
- [ ] Click download button next to document
- [ ] Verify file downloads correctly

### Test 9.5: Add Comment to Requisition
- [ ] Go to My Requisitions
- [ ] Click on requisition
- [ ] Scroll to "Comments" section
- [ ] Enter comment: `This requisition was for the kitchen renovation project.`
- [ ] Click "Add comment"
- [ ] Verify comment appears with username and timestamp

### Test 9.6: Multiple Comments & Threading
- [ ] Add 2-3 comments as different staff members (logout/login)
- [ ] Verify all comments displayed in chronological order
- [ ] Verify each shows correct username

### Test 9.7: Staff Data Persistence
- [ ] Add usage report, document, and comment to requisition
- [ ] Logout and login again
- [ ] Navigate to same requisition
- [ ] Verify all data (reports, documents, comments) still present

---

## 10. Data Filtering & Security

### Test 10.1: Staff Cannot See Admin Pages
- [ ] Login as `staff`
- [ ] Try to manually navigate to `/users` or other admin-only URL
- [ ] Verify access denied or redirected

### Test 10.2: Manager Cannot Bulk Edit All Properties
- [ ] Login as `manager` (property: null)
- [ ] Go to Stock page
- [ ] Verify shows all properties (since manager role allows it)
- [ ] Add item to different properties
- [ ] Verify items persist for those properties

### Test 10.3: Staff Requisition Filtered to Property
- [ ] Login as `staff` (Sandton Gardens)
- [ ] Create requisition
- [ ] Go to Reorder page as `manager`
- [ ] Verify requisition shows with property: Sandton Gardens
- [ ] Login as `staff2` (Rosebank View)
- [ ] Verify requisition from staff NOT visible in their Reorder view

### Test 10.4: Admin Sees All Data
- [ ] Login as `admin`
- [ ] Go to Stock page
- [ ] Verify items from both Sandton Gardens and Rosebank View visible
- [ ] Go to Reorder page
- [ ] Verify requisitions from all properties listed
- [ ] Go to My Requisitions
- [ ] Verify all requisitions shown (not just admin's own)

---

## 11. Edge Cases & Error Handling

### Test 11.1: Empty Property Assignment
- [ ] Create staff user with no property assigned
- [ ] Login as that user
- [ ] Go to Stock page
- [ ] Verify appropriate message (no data to display OR data handling)

### Test 11.2: Case Sensitivity
- [ ] Try logging in with username `Admin` (uppercase)
- [ ] Verify login fails or succeeds based on system design

### Test 11.3: Special Characters in Forms
- [ ] Try adding user with name: `O'Brien`
- [ ] Try adding item with name: `Item (Test) & More`
- [ ] Verify data stored and displayed correctly (no XSS)

### Test 11.4: Concurrent Changes
- [ ] Open app in 2 browser tabs as same user
- [ ] Tab 1: Issue stock
- [ ] Tab 2: Refresh page
- [ ] Verify Tab 2 shows updated quantities

### Test 11.5: Large Quantities
- [ ] Try issuing 999999 units
- [ ] Verify validation catches (should be > available qty)

---

## 12. Performance & Load

### Test 12.1: Many Items
- [ ] Go to Stock page with 50+ items
- [ ] Verify page loads and scrolls smoothly
- [ ] Verify search/filter works

### Test 12.2: Many Requisitions
- [ ] View My Requisitions with 20+ requisitions
- [ ] Verify pagination or scrolling works
- [ ] Click on one to verify details load

---

## 13. UI/UX Validation

### Test 13.1: Responsive Design
- [ ] Test on different screen sizes (desktop, tablet)
- [ ] Verify buttons and forms resize appropriately

### Test 13.2: Form Validation
- [ ] Try submitting form with empty required fields
- [ ] Verify error messages appear
- [ ] Verify form does not submit

### Test 13.3: Success/Error Messages
- [ ] Perform action that succeeds (e.g., add item)
- [ ] Verify green success message appears
- [ ] Perform action that fails (e.g., duplicate username)
- [ ] Verify red error message appears

---

## Summary Checklist

**Critical Path (Must Test First)**
- [ ] Login/Logout
- [ ] Role-based access for all roles
- [ ] Property filtering for staff
- [ ] Add user and assign property
- [ ] Admin can issue stock
- [ ] Staff can view own requisitions
- [ ] Usage reports, documents, comments persist

**Extended Testing**
- [ ] All reconciliation flows
- [ ] All requisition workflows
- [ ] Edge cases and error handling
- [ ] Performance with large datasets

**UAT Considerations**
- [ ] Manager property assignment flow
- [ ] Multi-user concurrent access
- [ ] Report generation accuracy
- [ ] Data export/backup functionality (if applicable)
