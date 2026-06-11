# PayYourPart — Built Architecture

## 1. Product Overview
PayYourPart is a real-time, collaborative web application designed to simplify shared expense tracking among friends, housemates, or travel groups. The app enables users to form groups, log bills with customizable splitting logic (equal, exact amounts, or percentages), calculate net individual balances, and automatically resolve complex group debts down to the minimum number of transactions using a greedy simplification algorithm.

- **Live URL:** [YOUR_RAILWAY_URL](YOUR_RAILWAY_URL)
- **Tech Stack Table:**

| Layer | Technology | Description / Rationale |
| :--- | :--- | :--- |
| **Backend Framework** | [Antigravity](file:///d:/Challagulla%20Dedipya/Vibe%20Coding/PayYourPart/antigravity/__init__.py) | A lightweight Python micro-framework featuring decorator-based routing and a Flask-like API. |
| **Database** | Supabase (PostgreSQL) | Managed database providing built-in auth, REST endpoints, and PostgreSQL Row-Level Security (RLS). |
| **Auth** | Supabase Auth | Handles user credentials verification, registration, and active login sessions. |
| **Frontend Style** | Vanilla HTML + TailwindCSS CDN | Modern, mobile-responsive styling utilizing Tailwind variables without a build process. |
| **Frontend Reactivity** | Alpine.js CDN | Lightweight, reactive client-side interactivity matching backend endpoints. |
| **Real-time Engine** | Supabase Realtime JS CDN | Subscribes to Postgres change events to update group balances live without page refresh. |
| **Hosting** | Railway | Cloud app platform for git-integrated automatic builds and continuous deployment. |

---

## 2. Database Schema
All database tables exist in Supabase (PostgreSQL) under the `public` schema. Row Level Security (RLS) is enabled on all tables, restricting data access based on group membership or profile ownership.

### PostgreSQL RLS Helper Functions

Three custom PostgreSQL security functions are used in policies to verify authorization:
1. **`check_group_membership(gid, uid)`**
   ```sql
   SELECT EXISTS (
     SELECT 1 FROM public.group_members 
     WHERE group_id = gid AND user_id = uid
   );
   ```
2. **`check_group_admin(gid, uid)`**
   ```sql
   SELECT EXISTS (
     SELECT 1 FROM public.group_members 
     WHERE group_id = gid AND user_id = uid AND role = 'admin'
   );
   ```
3. **`check_expense_group_membership(eid, uid)`**
   ```sql
   SELECT EXISTS (
     SELECT 1 FROM public.expenses e
     JOIN public.group_members gm ON e.group_id = gm.group_id
     WHERE e.id = eid AND gm.user_id = uid
   );
   ```

---

### Entity Tables Definition

#### 2.1 `profiles`
Stores public details for registered user profiles, mirroring the primary keys of the Supabase `auth.users` authentication schema.

- **Columns:**
  - `id` (uuid, PRIMARY KEY) - References `auth.users.id`
  - `name` (text, NOT NULL) - Display name
  - `email` (text, UNIQUE, NULLABLE) - Used for group invites
  - `avatar_url` (text, NULLABLE) - Optional profile photo
  - `created_at` (timestamptz, DEFAULT `now()`)
- **RLS Policies:**
  - **SELECT:** `Profiles are viewable by everyone` (Qual: `true`)
  - **INSERT:** `Allow profile creation during registration` (With Check: `true`)
  - **UPDATE:** `Users can update their own profile` (Qual: `auth.uid() = id`)

#### 2.2 `groups`
Stores group metadata circles created by users.

- **Columns:**
  - `id` (uuid, PRIMARY KEY, DEFAULT `gen_random_uuid()`)
  - `name` (text, NOT NULL) - Group title
  - `description` (text, NULLABLE) - Short text summary
  - `created_by` (uuid) - References `profiles.id`
  - `created_at` (timestamptz, DEFAULT `now()`)
- **RLS Policies:**
  - **SELECT:** `Members can view groups` (Qual: `check_group_membership(id, auth.uid()) OR (created_by = auth.uid())`)
  - **INSERT:** `Authenticated users can insert groups` (With Check: `auth.uid() = created_by`)
  - **UPDATE:** `Admins can update groups` (Qual: `check_group_admin(id, auth.uid())`)
  - **DELETE:** `Admins can delete groups` (Qual: `check_group_admin(id, auth.uid())`)

#### 2.3 `group_members`
A join table mapping users to groups with permission roles.

- **Columns:**
  - `id` (uuid, PRIMARY KEY, DEFAULT `gen_random_uuid()`)
  - `group_id` (uuid) - References `groups.id` ON DELETE CASCADE
  - `user_id` (uuid) - References `profiles.id`
  - `role` (text, DEFAULT `'member'`) - Options: `'admin'`, `'member'`
  - `joined_at` (timestamptz, DEFAULT `now()`)
  - **Constraints:** UNIQUE constraint on `(group_id, user_id)`
- **RLS Policies:**
  - **SELECT:** `Members can view group memberships` (Qual: `check_group_membership(group_id, auth.uid()) OR (user_id = auth.uid()) OR (EXISTS (SELECT 1 FROM groups g WHERE g.id = group_members.group_id AND g.created_by = auth.uid()))`)
  - **INSERT:** `Allow membership insertion` (With Check: `check_group_membership(group_id, auth.uid()) OR (EXISTS (SELECT 1 FROM groups g WHERE g.id = group_members.group_id AND g.created_by = auth.uid()))`)
  - **UPDATE:** `Members can update memberships` (Qual: `check_group_membership(group_id, auth.uid())`)
  - **DELETE:** `Members can delete memberships` (Qual: `check_group_membership(group_id, auth.uid())`)

#### 2.4 `expenses`
Contains logged expenses under a specific group.

- **Columns:**
  - `id` (uuid, PRIMARY KEY, DEFAULT `gen_random_uuid()`)
  - `group_id` (uuid) - References `groups.id` ON DELETE CASCADE
  - `paid_by` (uuid) - References `profiles.id` (Who paid the bill)
  - `title` (text, NOT NULL) - Expense description
  - `amount` (numeric, NOT NULL) - Total monetary amount
  - `split_type` (text, DEFAULT `'equal'`) - Modes: `'equal'`, `'exact'`, `'percentage'`
  - `category` (text, DEFAULT `'other'`) - Categories: `'food'`, `'travel'`, `'rent'`, `'other'`
  - `created_at` (timestamptz, DEFAULT `now()`)
- **RLS Policies:**
  - **SELECT:** `Members can view expenses` (Qual: `check_group_membership(group_id, auth.uid())`)
  - **INSERT:** `Members can insert expenses` (With Check: `check_group_membership(group_id, auth.uid())`)
  - **UPDATE:** `Payers can update expenses` (Qual: `paid_by = auth.uid()`)
  - **DELETE:** `Payers can delete expenses` (Qual: `paid_by = auth.uid()`)

#### 2.5 `expense_splits`
Stores individual debts resulting from an expense split.

- **Columns:**
  - `id` (uuid, PRIMARY KEY, DEFAULT `gen_random_uuid()`)
  - `expense_id` (uuid) - References `expenses.id` ON DELETE CASCADE
  - `user_id` (uuid) - References `profiles.id` (Who owes money)
  - `amount_owed` (numeric, NOT NULL) - The debtor's share
- **RLS Policies:**
  - **SELECT:** `Members can view splits` (Qual: `check_expense_group_membership(expense_id, auth.uid())`)
  - **INSERT:** `Members can insert splits` (With Check: `check_expense_group_membership(expense_id, auth.uid())`)
  - **UPDATE:** `Members can update splits` (Qual: `check_expense_group_membership(expense_id, auth.uid())`)
  - **DELETE:** `Members can delete splits` (Qual: `check_expense_group_membership(expense_id, auth.uid())`)

#### 2.6 `settlements`
Logs payment logs made to clear balances between group members.

- **Columns:**
  - `id` (uuid, PRIMARY KEY, DEFAULT `gen_random_uuid()`)
  - `group_id` (uuid) - References `groups.id`
  - `paid_by` (uuid) - References `profiles.id` (Debtor who paid)
  - `paid_to` (uuid) - References `profiles.id` (Creditor who received)
  - `amount` (numeric, NOT NULL) - Total money settled
  - `settled_at` (timestamptz, DEFAULT `now()`)
- **RLS Policies:**
  - **SELECT:** `Members can view settlements` (Qual: `check_group_membership(group_id, auth.uid())`)
  - **INSERT:** `Members can insert settlements` (With Check: `check_group_membership(group_id, auth.uid())`)

---

## 3. Folder & File Structure
```
PayYourPart/
├── app.py                      # Main entrypoint; app initialization, Supabase connection, blueprints, and handlers.
├── .env                        # Configuration secrets: SUPABASE_URL, SUPABASE_KEY, and SECRET_KEY.
├── requirements.txt            # Python dependencies (antigravity, supabase, python-dotenv, gunicorn, etc.).
├── Procfile                    # Startup configuration command for Railway: 'web: gunicorn app:app'.
├── PayYourPart_Brief.md        # Reference project brief and design notes.
├── PayYourPart_Architecture.md  # Comprehensive built architecture document.
│
├── antigravity/
│   └── __init__.py             # Mock lightweight web framework providing Flask-compatible Blueprint and Request objects.
│
├── middleware/
│   └── auth_guard.py           # Guard decorator (@require_login) enforcing login-restricted sessions.
│
├── routes/
│   ├── auth.py                 # Routing for /login, /register, and /logout.
│   ├── groups.py               # Routing for /dashboard, group detail, invites, leaving, and balance JSON endpoints.
│   ├── expenses.py             # Routing for expense logs, creation, detail sheets, edits, deletion, and CSV downloads.
│   └── settlements.py          # Routing for group balances, settle-up greedy lists, recording payments, and user dashboards.
│
├── services/
│   ├── balance_engine.py       # Computes balances and runs the greedy simplified debt transaction algorithm.
│   └── split_calculator.py     # Calculates splitting shares based on equal, exact, or percentage modes.
│
│
├── templates/
│   ├── base.html               # Main layout page loading Tailwind CSS, Alpine.js, base navbar, and footers.
│   ├── 404.html                # Friendly custom 404 not found error view.
│   ├── 500.html                # Friendly custom 500 internal server error view.
│   ├── login.html              # Clean Tailwind styling user login form.
│   ├── register.html           # Clean Tailwind styling registration form.
│   ├── dashboard.html          # Dashboard page displaying active user groups and overall net balances.
│   ├── group_detail.html       # Primary portal; displays rosters, recent bills, Alpine.js tabs, and live updates.
│   ├── add_expense.html        # Responsive form supporting equal, exact, and percentage splitting inputs.
│   ├── expense_detail.html     # Breakdown layout displaying specific payer and member split shares.
│   ├── expense_list.html       # Full paginated history table of bills with category filters and CSV downloads.
│   ├── balances.html           # Renders a clear list of net credit/debit balances for all members in the group.
│   ├── settle_up.html          # Lists simplified transactions to settle group debts with direct payment actions.
│   └── activity.html           # Combined feed of group actions (expenses and settlements) sorted chronologically.
│
├── pages/
│   ├── _app.js                 # Next.js custom application wrapper importing globals.css.
│   └── index.js                # Recreated high-fidelity marketing landing page for PayYourPart.
│
├── components/
│   ├── Navbar.js               # Styled header navigation linking sections and registration routes.
│   ├── Hero.js                 # Impressive main header section with custom graphics and interactive links.
│   ├── Problem.js              # Section outlining dinner drama, trip tension, and roommate rage.
│   ├── Features.js             # Six-grid list of premium product capability cards.
│   ├── HowItWorks.js           # Interactive timeline with step bubbles and assets.
│   ├── InteractiveDemo.js      # React-driven playground simulating expenses ledger, live balances, and simplified settling up.
│   ├── StatsBar.js             # High-impact indigo stats banner.
│   ├── Comparison.js           # "Life is better with us" side-by-side pain vs benefit card comparisons.
│   ├── CTA.js                  # Conversion section prompting downloads and sales queries.
│   ├── Footer.js               # Full multi-column site footer with mockup app store links.
│   └── WatchDemoModal.js       # Lightbox component displaying a product demo guide video player mockup.
│
├── styles/
│   └── globals.css             # Stylesheet containing Tailwind directives, font-faces, and base layout resets.
├── tailwind.config.js          # Configures Tailwind custom brand palettes, Inter font mappings, and content paths.
├── postcss.config.js           # Configures PostCSS plugin chains for CSS preprocessing.
└── package.json                # Defines Node packages, scripts, and build dependencies.
```
```

---

## 4. Route Map

| Method | Path | Blueprint | Action Description | Login Protected |
| :--- | :--- | :--- | :--- | :--- |
| **GET** | `/` | Core (`app.py`) | Redirects to `/dashboard` if user is logged in; otherwise redirects to `/login`. | No |
| **GET / POST** | `/login` | `auth_bp` | Renders form / authenticates credentials via Supabase Auth and saves session data. | No |
| **GET / POST** | `/register` | `auth_bp` | Renders form / registers auth user and inserts public profile row into `profiles`. | No |
| **GET** | `/logout` | `auth_bp` | Clears active cookie session and logs out of Supabase client auth. | No |
| **GET** | `/dashboard` | `groups_bp` | Displays active user groups and net individual balance summaries. | **Yes** |
| **POST** | `/groups/create` | `groups_bp` | Adds group record to table and inserts current user as role `'admin'`. | **Yes** |
| **GET** | `/groups/<id>` | `groups_bp` | Portal page showing rosters, recent expenses, and Alpine.js tabs. | **Yes** |
| **POST** | `/groups/<id>/invite` | `groups_bp` | Queries profile table by email and adds them to `group_members` if found. | **Yes** |
| **POST** | `/groups/<id>/leave` | `groups_bp` | Deletes user membership from `group_members` and redirects to `/dashboard`. | **Yes** |
| **GET** | `/groups/<id>/balances-json`| `groups_bp` | Returns JSON of user balances to power reactive Alpine updates. | **Yes** |
| **GET** | `/groups/<id>/activity` | `groups_bp` | Gathers group expenses and settlements, displaying a chronological feed. | **Yes** |
| **GET** | `/groups/<id>/expenses` | `expenses_bp` | Renders complete log of bills and invoices logged under the group. | **Yes** |
| **GET / POST** | `/expenses/add` | `expenses_bp` | Renders form / calculates splits and inserts expense + split items. | **Yes** |
| **GET** | `/expenses/<id>` | `expenses_bp` | Renders a detailed breakdown of a logged bill and its individual shares. | **Yes** |
| **GET / POST** | `/expenses/<id>/edit` | `expenses_bp` | Renders edit form / replaces splits and updates amount details. | **Yes** |
| **POST** | `/expenses/<id>/delete` | `expenses_bp` | Deletes expense record (cascade deletes related `expense_splits`). | **Yes** |
| **GET** | `/groups/<id>/export` | `expenses_bp` | Compiles expenses into CSV and returns attachment file `payyourpart-<group>.csv`. | **Yes** |
| **GET** | `/groups/<id>/balances` | `settlements_bp` | Renders detailed sheet of group net balances for each member. | **Yes** |
| **GET** | `/groups/<id>/settle-up` | `settlements_bp` | Renders list of simplified payments required to balance the group. | **Yes** |
| **POST** | `/groups/<id>/settle-up` | `settlements_bp` | Inserts a new settlement item into `settlements` table to reduce debts. | **Yes** |
| **GET** | `/me/balances` | `settlements_bp` | Renders a user's balance summary aggregated across all their groups. | **Yes** |

---

## 5. Business Logic

### 5.1 Splitting Calculations (`split_calculator.py`)
The [split_calculator.py](file:///d:/Challagulla%20Dedipya/Vibe%20Coding/PayYourPart/services/split_calculator.py) module supports three splitting configurations. It converts inputs to `Decimal` variables to prevent floating-point issues, and handles remainders to ensure splits sum exactly to the total amount.

- **Equal Split (`equal`):**
  Divides the total amount by the number of members ($N$). Each share is rounded to 2 decimal places using `ROUND_HALF_UP`. The last person takes the remainder ($Amount - (N-1) \times PerPerson$) to prevent round-off leaks.
- **Exact Split (`exact`):**
  Uses user-supplied amount overrides for each member. Validates that the sum of these manual splits equals the total expense amount.
- **Percentage Split (`percentage`):**
  Uses user-supplied percentages. Validates that the percentages sum to exactly $100\%$. Calculates each user's share as $Amount \times Percentage / 100$. The last member's share takes the remainder ($Amount - TotalAssignedSoFar$) to prevent percentage rounding leaks.

---

### 5.2 Balance Calculations (`balance_engine.py`)
The [balance_engine.py](file:///d:/Challagulla%20Dedipya/Vibe%20Coding/PayYourPart/services/balance_engine.py) engine calculates individual net balances.

#### `get_group_balances(group_id)` Step-by-Step:
1. **Initialize:** Queries all members of the group via `group_members`. Initializes each member's net balance to `Decimal('0.00')`.
2. **Process Expenses:** Queries all expenses for the group alongside their related splits from `expense_splits`.
   - For each split, identify the debtor (`split['user_id']`), the payer (`expense['paid_by']`), and the owed share (`amount`).
   - If debtor or payer are not in the initialized balance dict (e.g. they left the group), they are dynamically initialized to `0.00`.
   - Add split amount to the payer's balance ($payer += amount$) and subtract from the debtor's balance ($debtor -= amount$).
3. **Process Settlements:** Queries all payments recorded under the group via `settlements`.
   - For each settlement, identify the payer (debtor reducing debt), the receiver (creditor receiving money), and the settled `amount`.
   - Add amount to the payer's balance ($payer += amount$) and subtract from the receiver's balance ($receiver -= amount$).
4. **Output:** Converts decimal balances to floats and returns a dictionary matching `{user_id: float(balance)}`.

---

### 5.3 Debt Simplification Algorithm (`balance_engine.py`)
Simplifies complex multi-party IOUs down to a minimal set of transactions.

#### `simplify_debts(balances, user_profiles)` Step-by-Step:
1. **Partition:** Iterates over the balances map. Users with balance $> 0.01$ are added to a `creditors` list (`[user_id, balance]`). Users with balance $< -0.01$ are added to a `debtors` list (`[user_id, -balance]`).
2. **Sort:** Sorts both `creditors` and `debtors` arrays in descending order of their positive balance values, so the largest creditor and debtor are at index 0.
3. **Greedy Matching Loop:** Uses two pointers ($i$ for creditors, $j$ for debtors) to match participants:
   - Identify the current credit amount and debt amount: `settle = min(credit, debt)`.
   - If `settle > 0.01`, record a transaction dictionary from `debtor` to `creditor` for the amount `settle`.
   - Subtract `settle` from the current creditor's credit and debtor's debt.
   - If the creditor's remaining credit is $\le 0.01$, advance the creditor pointer ($i += 1$).
   - If the debtor's remaining debt is $\le 0.01$, advance the debtor pointer ($j += 1$).
4. **Return:** Returns a list of simplified transactions mapping debtors directly to creditors.

---

## 6. Frontend Architecture

### 6.1 Skeleton Layout (`base.html`)
The main framework layout [base.html](file:///d:/Challagulla%20Dedipya/Vibe%20Coding/PayYourPart/templates/base.html) wires together CDN scripts and layout templates:
- **TailwindCSS CDN:** Loads classes dynamically without a local build config.
- **Alpine.js CDN:** Loaded with `defer` to enable UI reactivity.
- **Custom Font:** Loads Google Font *Outfit* to style pages.
- **Structure:** Renders a responsive header containing navbar links, a flash message drawer, and a block `{% block content %}` placeholder for template injection.

---

### 6.2 Alpine.js Templates & Reactivity
Alpine.js handles tab switching, forms, dynamic input validation, and live updates without reloading pages:

- **Group Details (`group_detail.html`):**
  Uses `x-data="{ tab: 'expenses', balances: [], loading: false, fetchBalances() { ... } }"` on the column block:
  - Fetches balances from the `/groups/<id>/balances-json` endpoint.
  - Automatically loads on page init (`x-init="fetchBalances()"`).
  - Listens for a custom window event `@expense-updated.window="fetchBalances()"` to trigger auto-updates.
- **Expense Forms (`add_expense.html`):**
  Uses `x-data="{ splitType: 'equal', amount: 0.0, ... }"` to toggle and calculate inputs:
  - Shows/hides inputs for exact and percentage splits depending on the active split type.
  - Dynamically calculates shares and validates sum values in real-time, showing validation errors before submission.

---

### 6.3 Live Balance Sync via Supabase Realtime
A script at the bottom of [group_detail.html](file:///d:/Challagulla%20Dedipya/Vibe%20Coding/PayYourPart/templates/group_detail.html) listens for database changes:
- Instantiates the Supabase client using client credentials (`SUPABASE_URL` and `SUPABASE_KEY`) injected by the backend.
- Subscribes to a channel named `group-balances-refresh`.
- Listens for events on the `expenses` table filtered by the current group ID:
  ```javascript
  supabaseClient
      .channel('group-balances-refresh')
      .on('postgres_changes', { 
          event: '*', 
          schema: 'public', 
          table: 'expenses',
          filter: `group_id=eq.${groupId}`
      }, (payload) => {
          // Dispatch custom event to trigger Alpine.js refresh
          window.dispatchEvent(new CustomEvent('expense-updated'));
      })
      .subscribe();
  ```
- This triggers the Alpine tab component's `@expense-updated.window` event, re-fetching balances asynchronously.

---

## 7. Auth Flow

### 7.1 Registration Flow
1. **User Form Input:** The user submits their name, email, and password to `/register`.
2. **Supabase Auth Sign Up:** The auth blueprint calls `supabase.auth.sign_up({"email": email, "password": password})` to create a user account in Supabase.
3. **Public Profile Insert:** Upon success, a public profile row is inserted into the `profiles` table:
   ```python
   profile_data = {
       "id": auth_response.user.id,
       "name": name,
       "email": email
   }
   supabase.table('profiles').insert(profile_data).execute()
   ```
4. **Redirect:** Redirects the user to the login screen with a success flash message.

---

### 7.2 Login & Decorator Flow
1. **User Form Input:** The user submits their email and password to `/login`.
2. **Credentials Authentication:** The auth blueprint calls `supabase.auth.sign_in_with_password({"email": email, "password": password})`.
3. **Save Session Data:** Saves the session keys:
   - `session['user_id'] = response.user.id`
   - `session['access_token'] = response.session.access_token`
   - `session['user_email'] = response.user.email`
   - Queries `profiles` for the user's name and saves `session['user_name']`.
4. **Access Guard Decorator:** Applied routes are protected by `@require_login` (implemented in [auth_guard.py](file:///d:/Challagulla%20Dedipya/Vibe%20Coding/PayYourPart/middleware/auth_guard.py)):
   - Checks if `user_id` exists in the session.
   - If missing, redirects the request to `/login` with an error flash.
   - If present, authenticates the Supabase client requests with `session['access_token']` to enforce database Row-Level Security policies.

---

### 7.3 Logout Flow
1. **Route Trigger:** The user navigates to `/logout`.
2. **Supabase Sign Out:** Calls `supabase.auth.sign_out()` to invalidate the session on the auth server.
3. **Clear Session Cookies:** Calls `session.clear()` to clear local cookies.
4. **Redirect:** Redirects the user to `/login`.

---

## 8. Environment Variables
To run PayYourPart locally or in production, configure the following `.env` variables:

```bash
# Supabase Project Connection Credentials
SUPABASE_URL=https://your-project-reference.supabase.co
SUPABASE_KEY=your-supabase-anon-key-string

# Session Cookie Encryption Key
SECRET_KEY=your-custom-super-secure-session-key
```

---

## 9. Deployment

PayYourPart is a hybrid repository consisting of a Python/Flask web app (backend logic and dashboard templates) and a Next.js static landing page. They are deployed to separate cloud hosts to ensure optimal loading speeds and zero infrastructure costs.

### 9.1 Backend Web App Deployment (Render)

The core web app containing authentication, groups ledger, splits engine, and settlements is deployed to Render.

1. **GitHub Repository**: Push the project code to your GitHub account.
2. **Create Render Web Service**: Go to the [Render Dashboard](https://render.com), click **New +** → **Blueprint**, and select your GitHub repository.
3. **Configure Blueprint**:
   - Render automatically reads the `render.yaml` configuration file to detect service settings.
   - It will auto-populate the build command (`pip install -r requirements.txt`) and start command (`gunicorn app:app`).
4. **Configure Environment Variables**:
   - Render will prompt you to enter values for:
     - `SUPABASE_URL` = (Your Supabase project URL, e.g., `https://your-project.supabase.co`)
     - `SUPABASE_KEY` = (Your Supabase Anon API Key)
     - `SECRET_KEY` = (Will auto-generate a secure random value, or you can supply your own)
     - `FRONTEND_URL` = (The URL of your deployed Next.js marketing page on Vercel, e.g., `https://payyourpart.vercel.app`)
5. **Deploy**: Confirm the service creation. Render will build and deploy the Flask server, assigning a public `onrender.com` URL (e.g., `https://payyourpart-backend.onrender.com`). Note this URL for the frontend setup.

---

### 9.2 Frontend Marketing Site Deployment (Vercel)

The landing page and interactive mock playground are deployed to Vercel.

1. **Import Project**: Go to the [Vercel Dashboard](https://vercel.com), click **Add New** → **Project**, and import your GitHub repository.
2. **Configure Build Settings**:
   - Framework Preset: **Next.js**
   - Root Directory: **`./`** (keep the default, as the Next.js app is at the repository root).
3. **Configure Environment Variables**:
   - Add the following environment variable to link the landing page action buttons to the backend web app:
     - `NEXT_PUBLIC_BACKEND_URL` = (The public `onrender.com` URL generated by Render in Step 5 of the backend setup, e.g., `https://payyourpart-backend.onrender.com`)
4. **Deploy**: Click **Deploy**. Vercel will build the Next.js site and assign it a production URL (e.g., `https://payyourpart.vercel.app`).
5. **Update Backend**: If you deployed the frontend after the backend, copy your Vercel domain and update the `FRONTEND_URL` variable in your Render dashboard settings.

---

### 9.3 Post-Deployment Steps

1. **Supabase Redirects**: In your Supabase Dashboard, navigate to **Auth** → **URL Configuration** and update:
   - **Site URL**: Point this to your live Render domain (e.g., `https://payyourpart-backend.onrender.com`).
   - **Redirect URLs**: Add `https://payyourpart-backend.onrender.com/**`.
2. **Real-time Configuration**: Ensure database Row-Level Security (RLS) and real-time replication settings are enabled in the Supabase table configuration for the `expenses` table to enable instant balance sync.

---

## 10. Known Limitations & Future Improvements
1. **Email Notifications:** The app currently relies on manual invites. Future iterations could integrate Resend or SendGrid to notify users when they are added to groups or requested to settle balances.
2. **Google OAuth & Social Logins:** Supabase Auth supports social login. This can be integrated by setting client IDs in the Supabase Dashboard and adding OAuth buttons to the frontend.
3. **Multi-Currency Support:** The app currently defaults to Indian Rupees (₹). Future improvements could support multiple currencies and convert balances using real-time exchange rate APIs.
4. **Recurring Expenses:** Logging recurring bills (e.g. monthly rent, subscriptions) automatically.
5. **Receipt Scanning:** OCR integration using services like Tesseract or Google Cloud Vision to automatically scan and parse receipt details during expense logging.
