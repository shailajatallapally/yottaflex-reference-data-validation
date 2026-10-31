# AI Prompt History
## Versioned Reference Data Validation Pipeline

### 1. AI Tool Used
- ChatGPT (OpenAI)
- No other AI tools were used.

### 2. Purpose of AI Assistance

ChatGPT was used as a development assistant to support project planning, implementation guidance, debugging, testing, documentation, and performance optimization.

### 3. Development Prompt History

The following are reconstructed summaries of the prompts used during development.

**Prompt 1 – Project Planning**

Help me understand the requirements for a versioned reference data validation pipeline and break the project into manageable development stages.

**Prompt 2 – Validation Logic**

Help implement Python validation logic to check product codes, reference versions, effective dates, expired entries, and deprecated reference data.

**Prompt 3 – Error Handling**

Help identify and handle invalid dates, missing required fields, unknown codes, duplicate record IDs, and duplicate reference keys.

**Prompt 4 – Pipeline Development**

Help structure a reusable Python pipeline that reads CSV files, validates records, separates accepted and rejected records, and generates output reports.

**Prompt 5 – Automated Testing**

Help create pytest unit tests and pipeline tests to verify validation rules, rejection reasons, output generation, and run logging.

**Prompt 6 – Debugging**

Help investigate Python errors, test failures, data handling issues, and unexpected validation results without unnecessarily replacing working code.

**Prompt 7 – Performance Optimization**

Help improve reference data lookup performance and evaluate the pipeline using synthetic datasets, including a 100,000-record experiment.

**Prompt 8 – Safe Output Publishing**

Help implement safer output file writing, repeatable run identifiers, and reconciliation checks.

**Prompt 9 – Documentation**

Help prepare project documentation, installation instructions, execution commands, testing instructions, and project limitations.

### 4. Human Contributions and Responsibilities

The project developer:
- Reviewed the project requirements.
- Made implementation and design decisions.
- Executed and tested the Python code.
- Reviewed validation results and rejection reports.
- Ran the synthetic performance experiment.
- Verified test results and pipeline reconciliation.
- Reviewed AI suggestions and incorporated relevant changes.

### 5. Verification

The completed development work included:
- 10 automated tests passing.
- End-to-end validation checks.
- Duplicate and missing-value handling checks.
- Repeatable run ID verification.
- A synthetic 100,000-record performance experiment.
- Accepted and rejected record reconciliation.

### 6. Responsible AI Usage

ChatGPT assistance was used for guidance and development support. The developer remains responsible for understanding, reviewing, testing, and explaining the submitted implementation.

This document summarizes the AI-assisted development process. It is not a verbatim transcript of the original conversations.