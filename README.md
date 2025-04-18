# TC WD 1.4.4 Capstone Project: AI therapy CLI

## Description

### Background
The TC WD 1.4.4 (Module 1 Sprint 4 Part 4) Capstone Project is a Python-based application that integrates key concepts learned in the 
Module:
- Sprint 1:
  - Functions and Variables,
  - Conditionals,
  - Loops.
- Sprint 2:
  - Exceptions,
  - Libraries,
  - APIs,
  - Unit Tests.
- Sprint 3:
  - Files I/O,
  - Object-Oriented Programming,
  - Version Control,
  - Pai Programming.
- Sprint 4:
  - Regular Expressions,
  - Recursion,
  - Algorithms.

### Project Idea

This command-line tool enables users to participate in private therapy session with AI Agent. It uses CLI (`urwid` library) interface for interaction, allows users profiles with passwords and passcodes for privacy (`base64` and `bcrypt` libraries), store previous sessions for memory (`json` library), endeavors to implement AI Agent concepts (`openAI` API) with either:

  - **Workflow patterns:**
    - kas atstitiko
    - kaip jautiesi
    - ko nori

  - **Agent patterns:**

  - KAS ATSITIKO - [augmented LLM building blockK](https://cookbook.openai.com/examples/vector_databases/pinecone/gen_qa):
    - retrieval (query/results) - mimic retrieval augmented generation aka. RAG and semantic search for relevant context retrieval from data source (long-term memory), 
    - tools (call/response) - services (APIs) for aditional context (WHAT API?), 
    - memory (read/write) - passed interaction (previous sessions) saved.

  - KAIP JAUTIESI - prompt chaining ():
    - research,
    - specific topic,
    - define issue,
    - list of stuff,
    - do stuf,


  - KO NORI - routing (match/if cases):

  - parallelization (async) - evaluation from different perspectives

  - orchestrator-workers ():

    1.) CONTEXT: question -> lookup for: crm, history, etc.
    
    2.) What's required to solve -> LLM -> answer (options: .... -> call's)

  - evaluator-optimizer (write -> critticaly review and report of improvements -> repeat)


