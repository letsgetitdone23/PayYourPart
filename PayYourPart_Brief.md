# 💸 PayYourPart — Project Brief & Build Architecture

> **Stack:** Antigravity · Supabase · TailwindCSS · Alpine.js · Railway
> **Phases:** 5 · **Tables:** 6 · **Routes:** 20+ · **Cost:** $0

---

## 1. Problem Statement

Managing shared expenses among friends, housemates, or travel groups is painful. People lose track of who paid what, debts accumulate without visibility, and manually reconciling multiple IOUs wastes time. PayYourPart solves this by providing a real-time collaborative expense tracker with automatic debt simplification.

### 1.1 Core Pain Points

- No single source of truth for group spending
- Manual tallying leads to errors and disputes
- Hard to track multiple overlapping debts across many people
- No easy way to settle up with a clear minimal set of transactions
- Existing tools (Splitwise) are paywalled for key features

### 1.2 Solution Overview

PayYourPart is a web app where users create groups, log shared expenses, and get a simplified debt summary — so everyone knows exactly who owes whom, with the fewest possible payments to settle up completely.

---

## 2. Tech Stack

| Layer | Technology | Rationale |
|---|---|---|
| Backend | Antigravity (Python) | Lightweight Python web framework; decorator-based routing |
| Database | Supabase (PostgreSQL) | Free tier, built-in Auth, real-time subscriptions, REST API |
| Auth | Supabase Auth | Email/password + Google OAuth out of the box |
| Frontend | HTML + TailwindCSS CDN | No build step; responsive; free |
| Reactivity | Alpine.js CDN | Lightweight reactive UI without a full SPA framework |
| Hosting | Railway / Render | Free tier with auto-deploy from GitHub |
| Config | python-dotenv | Environment variable management |

---

## 3. Database Schema

All tables live in Supabase (PostgreSQL). Row Level Security (RLS) is enabled on every table.

### Entity Relationship Summary

```
auth.users  ──<  profiles
profiles    ──<  group_members  >──  groups
groups      ──<  expenses
expenses    ──<  expense_splits  >──  profiles
groups      ──<  settlements
```

### 3.1 profiles

| Column | Type | Constraint | Notes |
|---|---|---|---|
| id | uuid | PK, FK auth.users | Mirrors Supabase auth UID |
| name | text | NOT NULL | Display name |
| email | text | UNIQUE | Used for invites |
| avatar_url | text | | Optional profile picture URL |
| created_at | timestamptz | DEFAULT now() | Auto-set on insert |

### 3.2 groups

| Column | Type | Constraint | Notes |
|---|---|---|---|
| id | uuid | PK, DEFAULT gen_random_uuid() | |
| name | text | NOT NULL | Group display name |
| description | text | | Optional |
| created_by | uuid | FK profiles(id) | Creator's user ID |
| created_at | timestamptz | DEFAULT now() | |

### 3.3 group_members

| Column | Type | Constraint | Notes |
|---|---|---|---|
| id | uuid | PK | |
| group_id | uuid | FK groups(id) ON DELETE CASCADE | |
| user_id | uuid | FK profiles(id) | |
| role | text | DEFAULT 'member' | 'admin' or 'member' |
| joined_at | timestamptz | DEFAULT now() | |
| UNIQUE | (group_id, user_id) | | Prevents duplicate members |

### 3.4 expenses

| Column | Type | Constraint | Notes |
|---|---|---|---|
| id | uuid | PK | |
| group_id | uuid | FK groups(id) ON DELETE CASCADE | |
| paid_by | uuid | FK profiles(id) | Who fronted the money |
| title | text | NOT NULL | Description of the expense |
| amount | numeric(10,2) | NOT NULL | Total amount |
| split_type | text | DEFAULT 'equal' | 'equal' \| 'exact' \| 'percentage' |
| category | text | DEFAULT 'other' | 'food' \| 'travel' \| 'rent' \| 'other' |
| created_at | timestamptz | DEFAULT now() | |

### 3.5 expense_splits

| Column | Type | Constraint | Notes |
|---|---|---|---|
| id | uuid | PK | |
| expense_id | uuid | FK expenses(id) ON DELETE CASCADE | |
| user_id | uuid | FK profiles(id) | The person who owes |
| amount_owed | numeric(10,2) | NOT NULL | Their share of the expense |

### 3.6 settlements

| Column | Type | Constraint | Notes |
|---|---|---|---|
| id | uuid | PK | |
| group_id | uuid | FK groups(id) | |
| paid_by | uuid | FK profiles(id) | The one paying off debt |
| paid_to | uuid | FK profiles(id) | The one receiving payment |
| amount | numeric(10,2) | NOT NULL | Amount settled |
| settled_at | timestamptz | DEFAULT now() | |

---

## 4. Phased Build Architecture

Complete each phase fully before advancing to the next.

---

### Phase 1 — Foundation & Auth

**Goal:** Running server, DB connection, user registration, login, logout, and session management.

#### Deliverables
- Antigravity app scaffolded with blueprint structure
- Supabase project created with all 6 tables and RLS policies
- `.env` file wired up; Supabase client initialised
- Register page: name, email, password → inserts into `profiles`
- Login page: email, password → Supabase Auth → session cookie
- Logout route: clears session
- Auth middleware: `@require_login` decorator that redirects unauthenticated users to `/login`

#### Key Files
```
app.py                    # App factory, blueprint registration
routes/auth.py            # /login  /register  /logout
middleware/auth_guard.py  # @require_login decorator
templates/login.html
templates/register.html
.env                      # SUPABASE_URL, SUPABASE_KEY, SECRET_KEY
```

#### RLS Policies

| Table | Operation | Policy |
|---|---|---|
| profiles | SELECT | auth.uid() = id |
| profiles | INSERT | auth.uid() = id |
| profiles | UPDATE | auth.uid() = id |

---

### Phase 2 — Groups & Members

**Goal:** Create groups, invite members by email, view group roster, and see a groups dashboard.

#### Deliverables
- Dashboard page listing all groups the user belongs to
- Create group form → inserts into `groups` + auto-adds creator to `group_members`
- Group detail page showing member list
- Invite by email: looks up `profiles.email`, adds to `group_members`
- Leave group route

#### Key Routes

| Method | Path | Action |
|---|---|---|
| GET | /dashboard | List user's groups + net balance per group |
| POST | /groups/create | Create group, add creator as admin |
| GET | /groups/\<id\> | Group detail: members + expense feed |
| POST | /groups/\<id\>/invite | Add member by email |
| POST | /groups/\<id\>/leave | Remove self from group |

---

### Phase 3 — Expenses & Splits

**Goal:** Add expenses with equal, exact, or percentage splits. View expense history. Edit and delete expenses.

#### Split Types

| Split Type | Logic | Example |
|---|---|---|
| equal | amount ÷ num_members per person | ₹900 / 3 = ₹300 each |
| exact | User manually enters each person's share | A=₹500, B=₹250, C=₹250 |
| percentage | Each person assigned a %; validated to sum to 100% | A=50%, B=30%, C=20% |

#### Key Routes

| Method | Path | Action |
|---|---|---|
| GET | /groups/\<id\>/expenses | Paginated expense list for a group |
| GET/POST | /expenses/add | Create expense + generate splits |
| GET | /expenses/\<id\> | View expense detail and per-person amounts |
| POST | /expenses/\<id\>/edit | Update title, amount, re-calculate splits |
| POST | /expenses/\<id\>/delete | Delete expense and its splits |

#### Split Calculation Logic

```python
def calculate_splits(expense_id, members, amount, split_type, overrides):
    if split_type == 'equal':
        per_person = round(amount / len(members), 2)
        return [{'user': m, 'owed': per_person} for m in members]
    elif split_type == 'exact':
        assert sum(overrides.values()) == amount
        return [{'user': k, 'owed': v} for k, v in overrides.items()]
    elif split_type == 'percentage':
        assert sum(overrides.values()) == 100
        return [{'user': k, 'owed': round(amount * v / 100, 2)} for k, v in overrides.items()]
```

---

### Phase 4 — Balances & Debt Simplification

**Goal:** Compute per-user net balances per group. Show who owes whom. Simplify debts to minimum transactions.

#### Balance Calculation

For each user in a group:
> **Net Balance** = (sum of splits where `paid_by = user`) − (sum of splits where `user_id = user` and `paid_by ≠ user`)

- Positive = others owe you
- Negative = you owe others

```python
def get_group_balances(group_id):
    balances = {}
    expenses = supabase.table('expenses') \
               .select('*, expense_splits(*)') \
               .eq('group_id', group_id).execute().data
    for exp in expenses:
        payer = exp['paid_by']
        for split in exp['expense_splits']:
            debtor = split['user_id']
            amt = split['amount_owed']
            if debtor != payer:
                balances[payer]  = balances.get(payer,  0) + amt
                balances[debtor] = balances.get(debtor, 0) - amt
    return balances
```

#### Debt Simplification Algorithm (Greedy)

Reduces N×(N-1) pairwise debts to the minimum number of transactions needed.

```python
def simplify_debts(balances: dict) -> list:
    creditors = sorted([(u, a) for u, a in balances.items() if a > 0], key=lambda x: -x[1])
    debtors   = sorted([(u, -a) for u, a in balances.items() if a < 0], key=lambda x: -x[1])
    txns = []
    i, j = 0, 0
    while i < len(creditors) and j < len(debtors):
        creditor, credit = creditors[i]
        debtor,   debt   = debtors[j]
        settle = min(credit, debt)
        txns.append({'from': debtor, 'to': creditor, 'amount': settle})
        creditors[i] = (creditor, credit - settle)
        debtors[j]   = (debtor,   debt   - settle)
        if creditors[i][1] == 0: i += 1
        if debtors[j][1]   == 0: j += 1
    return txns  # Minimum payments to clear all debts
```

#### Key Routes

| Method | Path | Action |
|---|---|---|
| GET | /groups/\<id\>/balances | Net balances for every member |
| GET | /groups/\<id\>/settle-up | Simplified debt transactions list |
| POST | /groups/\<id\>/settle-up | Record a settlement payment |
| GET | /me/balances | User's net balance across all groups |

---

### Phase 5 — Polish, Real-time & Deploy

**Goal:** Production-ready UX — activity feed, real-time balance updates, CSV export, deployment.

#### Features
- Activity feed per group (expenses + settlements, ordered by time)
- Supabase Realtime: subscribe to `expense_splits` INSERT to refresh balances live
- Alpine.js reactive balance card — updates without page reload
- Category icons and filters (food, travel, rent, utilities, other)
- Export to CSV: all expenses for a group
- Mobile-responsive layouts for all pages
- Error pages: 404, 500 with friendly Tailwind UI

#### Real-time Setup

```javascript
const channel = supabase.channel('group-' + groupId)
  .on('postgres_changes', {
    event: 'INSERT',
    schema: 'public',
    table: 'expenses',
    filter: `group_id=eq.${groupId}`
  }, (payload) => {
    fetchAndRefreshBalances()  // Alpine.js data re-fetch
  })
  .subscribe()
```

#### Deployment Checklist

1. Push code to GitHub repository
2. Create Railway project → connect GitHub repo
3. Set environment variables: `SUPABASE_URL`, `SUPABASE_KEY`, `SECRET_KEY`
4. Add start command: `gunicorn app:app`
5. In Supabase: enable Google OAuth, set redirect URL to production domain
6. Run SQL migration to enable RLS on all tables
7. Smoke test all routes in production
8. Confirm Supabase database backups are active (automatic on free tier)

---

## 5. Complete Route Map

| Phase | Method | Path | Description |
|---|---|---|---|
| 1 | GET | / | Redirect to /dashboard or /login |
| 1 | GET/POST | /login | Login form + Supabase Auth |
| 1 | GET/POST | /register | Registration form |
| 1 | GET | /logout | Clear session, redirect to /login |
| 2 | GET | /dashboard | Groups list + global balance summary |
| 2 | POST | /groups/create | Create a new group |
| 2 | GET | /groups/\<id\> | Group home: members + recent expenses |
| 2 | POST | /groups/\<id\>/invite | Invite member by email |
| 2 | POST | /groups/\<id\>/leave | Leave the group |
| 3 | GET | /groups/\<id\>/expenses | Expense list (paginated) |
| 3 | GET/POST | /expenses/add | Add expense form + submit |
| 3 | GET | /expenses/\<id\> | Expense detail + per-person breakdown |
| 3 | POST | /expenses/\<id\>/edit | Edit expense + recalculate splits |
| 3 | POST | /expenses/\<id\>/delete | Delete expense |
| 4 | GET | /groups/\<id\>/balances | Per-member net balances |
| 4 | GET | /groups/\<id\>/settle-up | Minimum transactions to settle |
| 4 | POST | /groups/\<id\>/settle-up | Record a settlement |
| 4 | GET | /me/balances | User's cross-group balance summary |
| 5 | GET | /groups/\<id\>/activity | Chronological activity feed |
| 5 | GET | /groups/\<id\>/export | Download expenses as CSV |

---

## 6. Project Folder Structure

```
PayYourPart/
├── app.py                        # App factory + blueprint registration
├── .env                          # SUPABASE_URL, SUPABASE_KEY, SECRET_KEY
├── requirements.txt              # antigravity, supabase, python-dotenv, gunicorn
├── Procfile                      # web: gunicorn app:app
│
├── routes/
│   ├── auth.py                   # Phase 1: /login /register /logout
│   ├── groups.py                 # Phase 2: /groups/*
│   ├── expenses.py               # Phase 3: /expenses/*
│   └── settlements.py            # Phase 4: /settle-up
│
├── middleware/
│   └── auth_guard.py             # @require_login decorator
│
├── services/
│   ├── balance_engine.py         # get_group_balances(), simplify_debts()
│   └── split_calculator.py       # calculate_splits() for all split types
│
├── templates/
│   ├── base.html                 # Nav, footer, Tailwind CDN, Alpine.js CDN
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── group_detail.html
│   ├── add_expense.html
│   ├── expense_detail.html
│   ├── balances.html
│   ├── settle_up.html
│   └── activity.html
│
└── static/
    └── app.js                    # Supabase Realtime subscription
```

---

## 7. Full Supabase SQL Migration

Run this in the Supabase SQL Editor to create all tables and RLS policies in one step.

```sql
-- 1. PROFILES
create table profiles (
  id uuid references auth.users primary key,
  name text not null,
  email text unique,
  avatar_url text,
  created_at timestamptz default now()
);
alter table profiles enable row level security;
create policy 'Self only' on profiles
  using (auth.uid() = id);

-- 2. GROUPS
create table groups (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  description text,
  created_by uuid references profiles(id),
  created_at timestamptz default now()
);
alter table groups enable row level security;
create policy 'Members can view' on groups for select
  using (id in (select group_id from group_members where user_id = auth.uid()));

-- 3. GROUP_MEMBERS
create table group_members (
  id uuid primary key default gen_random_uuid(),
  group_id uuid references groups(id) on delete cascade,
  user_id uuid references profiles(id),
  role text default 'member',
  joined_at timestamptz default now(),
  unique(group_id, user_id)
);
alter table group_members enable row level security;
create policy 'Members can view memberships' on group_members for select
  using (group_id in (select group_id from group_members where user_id = auth.uid()));

-- 4. EXPENSES
create table expenses (
  id uuid primary key default gen_random_uuid(),
  group_id uuid references groups(id) on delete cascade,
  paid_by uuid references profiles(id),
  title text not null,
  amount numeric(10,2) not null,
  split_type text default 'equal',
  category text default 'other',
  created_at timestamptz default now()
);
alter table expenses enable row level security;
create policy 'Group members can view expenses' on expenses for select
  using (group_id in (select group_id from group_members where user_id = auth.uid()));

-- 5. EXPENSE_SPLITS
create table expense_splits (
  id uuid primary key default gen_random_uuid(),
  expense_id uuid references expenses(id) on delete cascade,
  user_id uuid references profiles(id),
  amount_owed numeric(10,2) not null
);
alter table expense_splits enable row level security;

-- 6. SETTLEMENTS
create table settlements (
  id uuid primary key default gen_random_uuid(),
  group_id uuid references groups(id),
  paid_by uuid references profiles(id),
  paid_to uuid references profiles(id),
  amount numeric(10,2) not null,
  settled_at timestamptz default now()
);
alter table settlements enable row level security;
```

---

## 8. Antigravity Prompts (Paste Phase by Phase)

### Phase 1 Prompt
```
Build a Python web app called PayYourPart using the Antigravity framework with Supabase as the backend.

Set up the following:
- App factory in app.py that initialises Antigravity and the Supabase client using SUPABASE_URL and SUPABASE_KEY from a .env file
- Blueprint structure with a routes/ folder
- Auth routes in routes/auth.py:
  - GET/POST /login — email + password login using Supabase Auth, stores user ID and access token in session
  - GET/POST /register — takes name, email, password; signs up via Supabase Auth; inserts a row into a "profiles" table with id, name, email
  - GET /logout — clears session, calls supabase.auth.sign_out()
- A @require_login decorator in middleware/auth_guard.py that redirects unauthenticated users to /login
- templates/base.html with TailwindCSS CDN, Alpine.js CDN, a teal navbar with "PayYourPart" branding and Logout link
- templates/login.html and templates/register.html — clean forms using Tailwind

The Supabase "profiles" table has: id (uuid, PK, FK to auth.users), name (text), email (text, unique), avatar_url (text), created_at (timestamptz).
```

### Phase 2 Prompt
```
Continuing the PayYourPart Antigravity app. Add groups functionality.

Add routes/groups.py with:
- GET /dashboard — requires login; queries all groups the current user belongs to via "group_members" table; shows group name, member count, and a placeholder net balance; renders templates/dashboard.html
- POST /groups/create — creates a row in "groups" (name, description, created_by); then inserts the creator into "group_members" as role "admin"; redirects to /groups/<id>
- GET /groups/<id> — shows group detail: member list with names, and a button to invite; renders templates/group_detail.html
- POST /groups/<id>/invite — looks up profiles by email; inserts into group_members with role "member"; redirects back to group page
- POST /groups/<id>/leave — removes current user from group_members; redirects to /dashboard

Tables involved:
- groups: id, name, description, created_by, created_at
- group_members: id, group_id, user_id, role, joined_at — unique(group_id, user_id)
- profiles: id, name, email

All routes protected by @require_login.
```

### Phase 3 Prompt
```
Continuing PayYourPart. Add expense tracking with three split modes.

Add routes/expenses.py and services/split_calculator.py.

split_calculator.py should have a calculate_splits(expense_id, members, amount, split_type, overrides) function:
- equal: divide amount by number of members, round to 2 decimal places
- exact: use overrides dict {user_id: amount}; validate they sum to total amount
- percentage: use overrides dict {user_id: pct}; validate they sum to 100; compute each share

Routes in expenses.py:
- GET /groups/<id>/expenses — list all expenses for the group, newest first
- GET/POST /expenses/add?group_id=<id> — form with title, amount, split_type, category; on POST insert into "expenses" then call calculate_splits and bulk-insert into "expense_splits"
- GET /expenses/<id> — detail view showing title, amount, paid_by name, and each member's share
- POST /expenses/<id>/edit — update title, amount, split_type; delete old expense_splits; recalculate and reinsert
- POST /expenses/<id>/delete — delete expense (cascade deletes splits)

Tables: expenses (id, group_id, paid_by, title, amount, split_type, category, created_at), expense_splits (id, expense_id, user_id, amount_owed)

All routes protected by @require_login.
```

### Phase 4 Prompt
```
Continuing PayYourPart. Add balance calculation and the settle-up flow.

Create services/balance_engine.py with two functions:

1. get_group_balances(group_id) — queries all expenses and their splits for the group; for each split where paid_by != user_id, adds amount_owed to the payer's balance and subtracts from the debtor's balance; returns a dict {user_id: net_amount} where positive = owed money, negative = owes money

2. simplify_debts(balances) — greedy algorithm: separate into creditors (positive) and debtors (negative); repeatedly match the largest creditor with the largest debtor; settle the minimum of the two; return a list of {from, to, amount} transactions

Add routes in routes/settlements.py:
- GET /groups/<id>/balances — calls get_group_balances; displays each member's net balance in green (owed) or red (owes)
- GET /groups/<id>/settle-up — calls simplify_debts; shows minimum transaction list with "Mark as Settled" buttons
- POST /groups/<id>/settle-up — inserts a row into "settlements"; redirects back
- GET /me/balances — aggregates net balances across all user's groups

Table: settlements (id, group_id, paid_by, paid_to, amount, settled_at). All routes protected by @require_login.
```

### Phase 5 Prompt
```
Continuing PayYourPart. Final phase: real-time updates, activity feed, and deployment.

1. Activity feed — GET /groups/<id>/activity: query expenses and settlements ordered by created_at DESC; merge into a chronological list; render with event type icons (💸 expense, ✅ settlement)

2. Real-time balances — in templates/group_detail.html add a Supabase JS CDN script that subscribes to INSERT events on the "expenses" table filtered by group_id; on event, fetch /groups/<id>/balances and update the balance card using Alpine.js x-data

3. CSV export — GET /groups/<id>/export: query all expenses with splits; build CSV with columns: date, title, paid_by, total_amount, your_share; return as file download with Content-Disposition: attachment

4. Add requirements.txt: antigravity, supabase, python-dotenv, gunicorn

5. Add Procfile: web: gunicorn app:app

6. Add 404 and 500 error handlers in app.py that render simple Tailwind error pages

7. Review all templates for mobile responsiveness — overflow-x-auto on tables, touch-friendly buttons (min h-10), collapsible navbar on small screens using Alpine.js
```

---

## 9. Acceptance Criteria

| Phase | Feature | Acceptance Criteria |
|---|---|---|
| 1 | Auth | User can register, login, logout. Unauthenticated routes redirect to /login. |
| 2 | Groups | Create group, invite 2 members, see all 3 on the group detail page. |
| 3 | Expenses | Add equal, exact, and percentage expenses. Splits sum equals total amount. |
| 4 | Balances | Add 3 expenses across 3 users. Simplified debts produce ≤ N-1 transactions. |
| 4 | Settle Up | Mark a debt as settled. Balance updates. Settlement recorded in DB. |
| 5 | Realtime | Add expense in Tab A; Tab B's balance card refreshes without page reload. |
| 5 | Deploy | App live on Railway URL. All routes accessible. No 500 errors. |

---

*Built with Antigravity + Supabase · Free tier · $0 infrastructure cost*
