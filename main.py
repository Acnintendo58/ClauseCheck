import streamlit as st
from pypdf import PdfReader
import requests
import json


st.set_page_config(
    page_title="ClauseCheck",
    page_icon="📄",
    layout="centered"
)


# ============================================================
# HEADER
# ============================================================

st.title("📄 ClauseCheck")

st.subheader(
    "Understand what you're agreeing to before you sign."
)

st.write(
    "Upload a contract or agreement and ClauseCheck will "
    "help identify important costs, dates, obligations, "
    "restrictions and other provisions in plain English."
)

st.info(
    "ClauseCheck provides automated information from your "
    "document. It is not legal advice and does not determine "
    "whether a provision is legal, illegal or enforceable."
)

st.divider()


# ============================================================
# HOW IT WORKS
# ============================================================

with st.expander("How ClauseCheck works"):

    st.write(
        """
1. Upload a PDF agreement.

2. ClauseCheck extracts the document text.

3. The AI identifies important provisions.

4. Each result can be checked against source wording
   from the document.
        """
    )


# ============================================================
# DOCUMENT TYPE
# ============================================================

st.header("1. Tell us about your document")

document_type = st.selectbox(
    "What type of document are you uploading?",
    [
        "Tenancy agreement",
        "Employment contract",
        "Freelance agreement",
        "Consumer/service agreement",
        "Vehicle agreement",
        "Membership agreement",
        "Other"
    ]
)


# ============================================================
# FILE UPLOAD
# ============================================================

st.header("2. Upload your document")

uploaded_file = st.file_uploader(
    "Choose a PDF",
    type=["pdf"]
)


# ============================================================
# PROCESS DOCUMENT
# ============================================================

if uploaded_file is not None:

    try:

        reader = PdfReader(uploaded_file)

        text = ""

        for page_number, page in enumerate(
            reader.pages,
            start=1
        ):

            page_text = page.extract_text()

            if page_text:

                text += (
                    f"\n--- Page {page_number} ---\n"
                    + page_text
                )


        if not text.strip():

            st.error(
                "ClauseCheck could not extract readable text "
                "from this PDF."
            )

            st.stop()


        st.success(
            "Document uploaded successfully."
        )


        # ========================================================
        # DOCUMENT DETAILS
        # ========================================================

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "Document type",
                document_type
            )

        with col2:

            st.metric(
                "Pages",
                len(reader.pages)
            )


        # ========================================================
        # EXTRACTED TEXT
        # ========================================================

        with st.expander(
            "View extracted document text"
        ):

            st.text_area(
                "Extracted text",
                text,
                height=300
            )


        st.divider()


        # ========================================================
        # ANALYSIS
        # ========================================================

        st.header("3. Understand your document")

        st.write(
            "ClauseCheck will identify provisions that may "
            "be useful to understand before you sign."
        )

        analyse = st.button(
            "🔍 Understand this document",
            type="primary",
            use_container_width=True
        )


        if analyse:

            # ====================================================
            # LIMIT DOCUMENT SIZE
            # ====================================================

            max_characters = 12000

            document_for_ai = text[:max_characters]

            if len(text) > max_characters:

                st.info(
                    "This prototype analyses the first part of "
                    "longer documents to keep processing time "
                    "manageable on your computer."
                )


            # ====================================================
            # AI PROMPT
            # ====================================================

            prompt = f"""
You are ClauseCheck, a document-understanding assistant.

Your job is to help an ordinary person understand what a
document actually says.

DOCUMENT TYPE:
{document_type}

You are NOT a lawyer.

Do NOT provide legal advice.

Do NOT decide whether anything is legal, illegal, valid,
invalid, enforceable or unenforceable.

Do NOT predict what a court or other decision-maker would do.

Only report information explicitly supported by the document.

STRICT ACCURACY RULES:

1. Never invent facts.

2. Never invent prices.

3. Never invent dates.

4. Never invent deadlines.

5. Never invent obligations.

6. Never invent restrictions.

7. Never invent penalties.

8. Never infer facts simply because they are common for
this type of document.

9. Every factual result must include supporting wording
from the document in the "source" field.

10. The source must actually support the statement.

11. If you are uncertain whether something appears in the
document, leave it out.

12. Do not turn a request into an automatic right.

13. Do not turn a possibility into a fact.

14. Do not create headings that imply facts the document
does not state.

15. Questions must relate to something actually mentioned
in the document.

16. Do not introduce entirely new legal issues through
the questions.

17. Keep explanations concise.

Return ONLY valid JSON.

Do not use Markdown.

Use exactly this structure:

{{
    "summary": "",

    "money": [
        {{
            "item": "",
            "explanation": "",
            "source": ""
        }}
    ],

    "dates_and_deadlines": [
        {{
            "item": "",
            "explanation": "",
            "source": ""
        }}
    ],

    "things_you_must_do": [
        {{
            "item": "",
            "explanation": "",
            "source": ""
        }}
    ],

    "things_you_must_not_do": [
        {{
            "item": "",
            "explanation": "",
            "source": ""
        }}
    ],

    "cancellation_and_termination": [
        {{
            "item": "",
            "explanation": "",
            "source": ""
        }}
    ],

    "renewal": [
        {{
            "item": "",
            "explanation": "",
            "source": ""
        }}
    ],

    "potentially_important": [
        {{
            "item": "",
            "explanation": "",
            "source": ""
        }}
    ],

    "questions_to_consider": [
        ""
    ]
}}

CATEGORY GUIDANCE:

MONEY:
Identify explicitly stated payments, deposits, fees and
charges.

DATES AND DEADLINES:
Identify explicitly stated dates, deadlines, notice periods
and time periods.

THINGS YOU MUST DO:
Identify obligations explicitly imposed on the reader.

THINGS YOU MUST NOT DO:
Identify restrictions explicitly imposed on the reader.

CANCELLATION AND TERMINATION:
Describe only cancellation or termination mechanisms actually
contained in the document.

Be precise about whether something is a request, right,
condition or notice process.

RENEWAL:
Only include renewal information if the document actually
mentions renewal or continuation.

POTENTIALLY IMPORTANT:
Include provisions that may be useful for the reader to
understand carefully.

Do not describe anything as illegal, unfair or unenforceable.

QUESTIONS:
Questions should help the reader investigate something
actually mentioned in the document.

Do not answer the question yourself.

FINAL CHECK:

Before returning the JSON, remove anything that is not
directly supported by the document.

DOCUMENT:

{document_for_ai}
"""


            # ====================================================
            # CALL OLLAMA
            # ====================================================

            with st.spinner(
                "ClauseCheck is reading your document..."
            ):

                try:

                    response = requests.post(
                        "http://localhost:11434/api/generate",
                        json={
                            "model": "llama3.2",
                            "prompt": prompt,
                            "stream": False
                        },
                        timeout=180
                    )


                    if response.status_code != 200:

                        st.error(
                            "There was a problem communicating "
                            "with the AI."
                        )

                        st.code(
                            response.text
                        )

                        st.stop()


                    raw_response = response.json()[
                        "response"
                    ].strip()


                    # =================================================
                    # REMOVE CODE FENCES
                    # =================================================

                    if raw_response.startswith(
                        "```json"
                    ):

                        raw_response = raw_response[7:]


                    elif raw_response.startswith(
                        "```"
                    ):

                        raw_response = raw_response[3:]


                    if raw_response.endswith(
                        "```"
                    ):

                        raw_response = raw_response[:-3]


                    raw_response = raw_response.strip()


                    # =================================================
                    # READ JSON
                    # =================================================

                    try:

                        result = json.loads(
                            raw_response
                        )

                    except json.JSONDecodeError:

                        st.error(
                            "ClauseCheck received a response "
                            "that it could not understand."
                        )

                        with st.expander(
                            "Show AI response"
                        ):

                            st.code(
                                raw_response
                            )

                        st.stop()


                    st.success(
                        "Your document has been analysed."
                    )


                    # =================================================
                    # SUMMARY
                    # =================================================

                    st.header(
                        "📄 What does this document do?"
                    )

                    st.write(
                        result.get(
                            "summary",
                            "No summary available."
                        )
                    )


                    # =================================================
                    # DISPLAY FUNCTION
                    # =================================================

                    def show_section(
                        title,
                        icon,
                        key
                    ):

                        items = result.get(
                            key,
                            []
                        )

                        if not items:
                            return


                        st.divider()

                        st.header(
                            f"{icon} {title}"
                        )


                        for item in items:

                            if not isinstance(
                                item,
                                dict
                            ):

                                continue


                            st.subheader(
                                item.get(
                                    "item",
                                    "Provision"
                                )
                            )

                            st.write(
                                item.get(
                                    "explanation",
                                    ""
                                )
                            )


                            source = item.get(
                                "source",
                                ""
                            )


                            if source:

                                with st.expander(
                                    "View source wording"
                                ):

                                    st.caption(
                                        "Wording taken from "
                                        "the uploaded document:"
                                    )

                                    st.write(
                                        source
                                    )


                    # =================================================
                    # RESULTS
                    # =================================================

                    show_section(
                        "Money",
                        "💰",
                        "money"
                    )

                    show_section(
                        "Dates & deadlines",
                        "📅",
                        "dates_and_deadlines"
                    )

                    show_section(
                        "Things you must do",
                        "✅",
                        "things_you_must_do"
                    )

                    show_section(
                        "Things you must not do",
                        "🚫",
                        "things_you_must_not_do"
                    )

                    show_section(
                        "Cancellation & termination",
                        "🚪",
                        "cancellation_and_termination"
                    )

                    show_section(
                        "Renewal",
                        "🔄",
                        "renewal"
                    )


                    # =================================================
                    # POTENTIALLY IMPORTANT
                    # =================================================

                    important = result.get(
                        "potentially_important",
                        []
                    )


                    if important:

                        st.divider()

                        st.header(
                            "⚠️ Potentially important"
                        )

                        st.caption(
                            "These provisions may be worth "
                            "understanding more carefully. "
                            "This does not mean they are legally "
                            "wrong or problematic."
                        )


                        for item in important:

                            if not isinstance(
                                item,
                                dict
                            ):

                                continue


                            st.subheader(
                                item.get(
                                    "item",
                                    "Important provision"
                                )
                            )

                            st.write(
                                item.get(
                                    "explanation",
                                    ""
                                )
                            )


                            source = item.get(
                                "source",
                                ""
                            )


                            if source:

                                with st.expander(
                                    "View source wording"
                                ):

                                    st.caption(
                                        "Wording taken from "
                                        "the uploaded document:"
                                    )

                                    st.write(
                                        source
                                    )


                    # =================================================
                    # QUESTIONS
                    # =================================================

                    questions = result.get(
                        "questions_to_consider",
                        []
                    )


                    if questions:

                        st.divider()

                        st.header(
                            "❓ Questions you may want to consider"
                        )

                        st.caption(
                            "These are questions to investigate "
                            "further, not legal conclusions."
                        )


                        for question in questions:

                            st.write(
                                f"• {question}"
                            )


                    # =================================================
                    # FOOTER
                    # =================================================

                    st.divider()

                    st.caption(
                        "ClauseCheck is an experimental AI "
                        "document-understanding tool. Its output "
                        "may contain errors or omissions. It is "
                        "not legal advice."
                    )


                except requests.exceptions.ConnectionError:

                    st.error(
                        "ClauseCheck could not connect to Ollama."
                    )

                    st.write(
                        "Make sure Ollama is running."
                    )


                except requests.exceptions.Timeout:

                    st.error(
                        "The AI took too long to respond."
                    )


                except Exception as error:

                    st.error(
                        "Something unexpected happened."
                    )

                    st.write(
                        str(error)
                    )


    except Exception as error:

        st.error(
            "ClauseCheck could not read this PDF."
        )

        st.write(
            str(error)
        )