# Triage Decisions

## **General Triage Guidelines**

### 1. Action Required (`action-required`)

Apply this label to emails that are urgent and require a direct, timely response or action from me.

- **High-Priority Senders:** Emails from my child's school, such as **Beneylu School**, are always considered action required.
- **Urgent Financial Requests:** Look for emails from financial institutions like **Revolut** that explicitly state an action is needed. Keywords and indicators include "Action Required," "confirm your information," "expired," or warning emojis like ⚠️.

### 2. To Review (`review`)**

Apply this label to emails that are important to read but do not require an immediate interactive response. This is for awareness and non-urgent decisions.

- **Security and Account Alerts:** All security alerts (e.g., from **Google**) and updates to account privacy policies (e.g., from **Nintendo**) should be reviewed.
- **Direct Messages & Communications:** Notifications of new messages from platforms like **LinkedIn** or **CoFoundersLab**.
- **Calendar reminders:** Google Calendar notifications for events I set reminders for.
- **Transactional & Order Updates:** Emails concerning a recent purchase, like order confirmations or shipping updates (e.g., from **Boulanger**).
- **Important Service Provider Updates:**
  - Critical system-generated reports, such as abuse alerts from my hosting provider (**abuse@hetzner.com**).
  - Communications from essential services like my water utility provider (**veolia.com**).
  - Updates to service terms or sub-processor lists (e.g., from **Make**).
- **Local & Community Organizations:** Emails from known local organizations, like my child's tennis club (**HERBLAY (AST)**), which may contain timely information.

### 3. Newsletter (`newsletter`)

Apply this label to newsletters from specific sources that I want to read and keep.

- **Known & Liked Authors:** Newsletters from senders I value, such as **Ray Dalio**, **Luca Dellanna**, **Jeremy Howard (fast.ai)**, and **Abhinav Agarwal**.

### 4. Archive
Archive emails that are purely for my records and do not require any action. These are typically confirmations or receipts that I may need to reference later.

- **Receipts and Invoices:** Any email that is a receipt, invoice, or confirmation of a successful payment (e.g., from **Apple**, **Setapp**, **Paddle.com**).
- **Completed Transaction Notifications:** Automated notifications confirming that a process is complete, such as a "Withdrawal Completed" email from **BitGo Notifications**.
- **Payments label required:** For any payment-related email, apply the `payments` label before archiving.

### 5. Trash (`trashed`)

This is the default action for any email that doesn't fit the criteria above.

- **Promotional & Marketing Content:** General marketing emails, special offers, and promotional content (e.g., from **eBay**, **Boulanger**, **Parallels**, **PayPal**, **Speedy**).
- **Uninteresting Newsletters:** All newsletters that are not on the approved list for the `newsletter` label (e.g., from **Jeff Sauer**, **Fireworks AI**, **Vinh Giang**).
- **Low-Priority Automated Updates:** Non-critical, routine notifications and digests that I don't need to review, such as weekly **GitHub** Dependabot alerts or general informational emails from brokers like **Interactive Brokers** (e.g., "Reminder to Think Before You Click!").
- **Unimportant Policy Updates:** Updates to operating agreements oozr program policies for services I don't actively manage, such as the **Amazon Influencer & Associates Program**.

---

**MAKE SURE YOU PROCESS ALL MARK PROCESSED EMAILS AS READ AND ARCHIVE THEM.**
Also make sure you process all emails in inbox. At the end, the inbox must be empty.

**When you archive emails (holiday rental messages, invoices, shipping confirmations, and similar), you MUST provide a short end-of-run summary of what was archived (sender + subject + 1-line gist), so I don’t have to open the archive to know what happened.**

---

## Additional Decision References

- **Action required (`action-required`)**
  - OpenRouter security alerts about exposed/compromised keys.
  - GitHub security alerts about possible secrets exposure.
- **Review (`review`)**
  - Service policy updates and account privacy/terms changes (e.g., Link policy updates).
  - LinkedIn connection requests (e.g., “Je viens de vous envoyer une demande de connexion”).
  - Assurance Maladie messages (could be transactional or informational—review case-by-case).
  - Utility/usage summaries from TotalEnergies (“Votre bilan mensuel de consommation d'électricité”).
  - Default bucket: any email not explicitly covered elsewhere goes to review.
- **Trash (`trashed`)**
  - LinkedIn InMail solicitations (commercial 99% of the time, e.g., from Matt Fullerton).
  - Quora engagement/vote notifications.
- **Archive directly (mark read, do not keep in review)**
  - Account creation/order confirmations and shipping/transactional updates (e.g., Grand Rex confirmations/account creation, Chaussures Rieker order, Vision Direct order, similar shopping sites).
- **Post-review disposition rules**
  - After reviewing, most items in `review` can be deleted except the following must be archived and kept:
    - Réservations LES BALCONS ski holiday messages.
    - TotalEnergies monthly consumption/billing summaries.
    - Critical security alerts kept for record (GitHub secrets alerts, OpenRouter key compromise alerts).
    - Account creation/order update transactional emails (Grand Rex, Chaussures Rieker, Vision Direct, other shopping sites).
    - Wire transfer notifications (e.g., Revolut or Boursorama).
    - Invoices (e.g., Orange “Votre facture Internet est arrivée”).

