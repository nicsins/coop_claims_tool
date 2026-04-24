# ⚖️ Co-op Claims Assistant (v1.0)

**Automated Deductive Reasoning for No-Proof Lawsuit Claims.**

The Co-op Claims Assistant is a specialized AI agent environment designed to handle the high-friction task of filling out lawsuit claim forms. It goes beyond simple data entry by using RAG (Retrieval-Augmented Generation) to deduce valid parameters and ensure submissions meet legal criteria.

## ✨ Key Features

*   **Deductive Logic:** Automatically maps vague user history to specific valid form parameters.
*   **Privacy First:** Designed to run locally on your hardware. No third-party data hosting.
*   **Human-in-the-Loop:** A dedicated verification UI allows you to audit every claim before final submission.
*   **On-the-Job Training:** The agent learns from your corrections, refining its logic for future batches.

## 🛠️ Quick Start

1.  **Clone & Setup:**

    ```bash
    chmod +x setup.sh
    ./setup.sh
    ```

**Project Options:**

*   **claims-maximizer:** Auto-locate and file zero-proof claims.
*   **Coop Claims Tool – Continuous No-Proof Lawsuit Capital Engine**

    1.  pip install -r requirements.txt
    2.  python main.py

    *   Runs forever, scrapes daily, fills via your MCP/Agent Zero, logs everything.
    *   First run processes Inova (deadline TODAY) + Panda.
    *   Add more claimants to claims\[] with "consent\_received": true + raw\_user\_data.

    ```bash
    cd coop_claims_tool
    pip install -r requirements.txt
    python main.py
    ```

*   **coop-claims-paperclip:**

    ```bash
    npx paperclipai onboard --yes --name "CoopClaimsMaximizer"
    # or if you prefer clone:
    # git clone [############################################] && cd paperclip && pnpm install
    ```

    1.  Start your Python bridge first:

        ```bash
        python api_server.py
        ```

    2.  Then launch Paperclip (it will auto-run the org chart).
