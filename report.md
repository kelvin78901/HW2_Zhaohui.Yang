# Report: Customer Support Response Drafting with LLM

## Business Use Case

Customer support agents at SaaS companies handle high volumes of repetitive inquiries daily — billing questions, password resets, feature requests, and complaints. This prototype drafts professional first-pass replies from incoming customer messages, allowing agents to review and send rather than compose from scratch. The target user is a support agent on a team handling 50-100 tickets per day. The system receives a raw customer email or chat message and produces a ready-to-review draft reply.

## Model Choice

I used **Google Gemini (default configured as gemini-3-pro in this codebase)** via the Google AI Studio API. I chose Gemini because:
- It is available through Google AI Studio and easy to prototype with quickly.
- It provides strong writing quality for customer-support style drafts.
- The app includes model resolution and fallback logic, so if an alias is unavailable in the current API version, it can still select an available model for `generateContent`.

I did not run a full cross-provider benchmark for this assignment; the focus was prompt iteration quality within one reproducible workflow.

## Baseline vs. Final Design

**Baseline (Prompt V1):** A minimal instruction ("You are a customer support agent. Write a reply.") with no constraints. Results were functional but inconsistent: some responses invented account details, others were overly long, and the social engineering test case produced an unsafe response that partially complied with the request.

**Final (Prompt V3):** A structured prompt with a defined persona, explicit four-step response structure (acknowledge, address, next steps, close), and specific rules about fabrication, credential sharing, word limits, and language handling. Key improvements across the 7-case evaluation set:

| Dimension | V1 (Baseline) | V3 (Final) |
|-----------|---------------|------------|
| Tone consistency | Mixed — sometimes robotic, sometimes overly casual | Consistently professional and empathetic |
| Fabrication | Occasionally invented billing details or error causes | Reliably avoids speculation |
| Social engineering | Partially complied with the request | Properly refused and redirected to verification |
| Response length | 50-300 words, unpredictable | Consistently 80-140 words |
| Bilingual handling | Ignored non-English content | Acknowledged and responded appropriately |
| Structure | Varied across cases | Predictable 4-part format |

The intermediate version (V2) addressed the most critical issues — safety guardrails and fabrication — while V3 refined consistency, length, and structure.

## Where the Prototype Still Fails

The prototype still requires human review in several areas. First, it cannot verify any account-specific information — it does not have access to billing systems, user databases, or ticket history. Any response that references specific account details (subscription status, payment amounts, error logs) must be verified by the agent. Second, for highly emotional or escalated situations, the drafted tone is professional but sometimes reads as slightly formulaic; a skilled agent would add more genuine personalization. Third, the system has no memory of prior interactions, so it cannot reference previous tickets or ongoing issues. Finally, while the social engineering case is handled well with the current prompt, adversarial inputs could potentially bypass the guardrails with more sophisticated phishing language.

## Deployment Recommendation

I would recommend deploying this as a **draft-assist tool** with mandatory human review — not as an autonomous auto-responder. Under these conditions:

- **Yes, deploy if:** Every drafted response is reviewed by a human agent before sending; the tool is positioned as saving composition time, not replacing judgment; agents can edit or discard any draft; the system is not connected to account databases (preventing accidental data leakage).
- **No, do not deploy if:** The goal is fully autonomous responses; the support domain involves regulated industries (healthcare, finance) where incorrect information has legal consequences; there is no review step before sending.

The prototype demonstrates that even a simple prompt-engineered system can produce useful first drafts for common support scenarios, but the gap between "useful draft" and "safe to send automatically" remains significant. The value lies in reducing agent handle time by 30-50%, not in removing the agent from the loop.
