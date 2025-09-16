TASK_DECOMPOSITION_PROMPT = """
You are an expert planner. Your goal is to consolidate a complex user request into the minimum number of high-level sub-tasks required. Each sub-task should correspond to a major, consolidated action within a single target application.

**CORE PRINCIPLES:**
1.  **App-Centric Grouping:** Group all related actions for a single application into ONE sub-task.
2.  **Focus on Data Handoffs:** A good decomposition often involves one sub-task to *retrieve* information and a subsequent sub-task to *use* that information.
3.  **Assume Internal Capabilities:** Do NOT create sub-tasks for abstract cognitive work like 'summarize' or 'analyze'.
4.  **Simplify Single Actions:** If the user's task is already a single, simple action, the output should be a single sub-task that concisely describes that action. Do not make it identical to the user's input.
5.  **General purpose sub tasks:** You also need to realise that these subtasks are going to be used to search for tools and apps. And the names and description of these tools and apps are going to be general in nature so the sub tasks should not be too specific. The task which you will get may be specific in nature but the sub taks must be general. 
**--- EXAMPLES ---**

**EXAMPLE 1:**
- **User Task:** "Create a Google Doc summarizing the last 5 merged pull requests in my GitHub repo universal-mcp/universal-mcp."
- **CORRECT DECOMPOSITION:**
    - "Fetch the last 5 merged pull requests from the GitHub repository 'universal-mcp/universal-mcp'."
    - "Create a new Google Doc containing the summary of the pull requests."

**EXAMPLE 2:**
- **User Task:** "Find the best restaurants in Goa using perplexity web search."
- **CORRECT DECOMPOSITION:**
    - "Perform a web search using Perplexity to find the best restaurants in Goa."

**--- YOUR TASK ---**

**USER TASK:**
"{task}"

**YOUR DECOMPOSITION (as a list of strings):**
"""


APP_SEARCH_QUERY_PROMPT = """
You are an expert at selecting an application to perform a specific sub-task. Your goal is to generate a concise query for an app search engine.

Analyze the current sub-task in the context of the original user goal and the ENTIRE PLAN so far.

**CORE INSTRUCTION:** If any application already used in the plan is capable of performing the current sub-task, your query MUST BE the name of that application to ensure continuity and efficiency. Otherwise, generate a concise query for the category of application needed.

**--- EXAMPLES ---**

**EXAMPLE 1: Reusing an app from two steps ago**
- **Original User Task:** "Find my latest order confirmation in Gmail, search for reviews of the main product on perplexity, and then send an email to ankit@agentr.dev telling about the reviews"
- **Plan So Far:**
  - The sub-task 'Find order confirmation in Gmail' was assigned to app 'google_mail'.
  - The sub-task 'Search for product reviews on perplexity' was assigned to app 'perplexity'.
- **Current Sub-task:** "send an email to ankit@agentr.dev"
- **CORRECT QUERY:** "google_mail"

**EXAMPLE 2: First Step (No previous context)**
- **Original User Task:** "Find the best restaurants in Goa."
- **Plan So Far:** None. This is the first step.
- **Current Sub-task:** "Perform a web search to find the best restaurants in Goa."
- **CORRECT QUERY:** "web search"

**--- YOUR TASK ---**

**Original User Task:**
"{original_task}"

**Plan So Far:**
{plan_context}

**Current Sub-task:**
"{sub_task}"

**YOUR CONCISE APP SEARCH QUERY:**
"""


TOOL_SEARCH_QUERY_PROMPT = """
You are an expert at summarizing the core *action* of a sub-task into a concise query for finding a tool. This query should ignore any application names.

**INSTRUCTIONS:**
1.  Focus only on the verb or action being performed in the sub-task.
2.  Include key entities related to the action.
3.  Do NOT include the names of applications (e.g., "Perplexity", "Gmail").
4.  You also need to realise that this query is going to be used to search for tools in a particular app. And the names and description of these tools are going to be general in nature so the query should not be too specific. The sub task which you will get may be specific in nature but the query must be general.

**EXAMPLES:**
- **Sub-task:** "Perform a web search using Perplexity to find the best restaurants in Goa."
- **Query:** "web search for restaurants"

- **Sub-task:** "Fetch all marketing emails received from Gmail in the last 7 days."
- **Query:** "get emails by date"

- **Sub-task:** "Create a new Google Doc and append a summary."
- **Query:** "create document, append text"

**SUB-TASK:**
"{sub_task}"

**YOUR CONCISE TOOL SEARCH QUERY:**
"""

REVISE_DECOMPOSITION_PROMPT = """
You are an expert planner who revises plans that have failed. Your previous attempt to break down a task resulted in a sub-task that could not be matched with any available tools.

**INSTRUCTIONS:**
1.  Analyze the original user task and the failed sub-task.
2.  Generate a NEW, alternative decomposition of the original task.
3.  This new plan should try to achieve the same overall goal but with different, perhaps broader or more combined, sub-tasks to increase the chance of finding a suitable tool.

**ORIGINAL USER TASK:**
"{task}"

**FAILED SUB-TASK FROM PREVIOUS PLAN:**
"{failed_sub_task}"

**YOUR NEW, REVISED DECOMPOSITION (as a list of strings):**
"""


TOOL_SELECTION_PROMPT = """
You are an AI assistant that selects the most appropriate tool(s) from a list to accomplish a specific sub-task.

**INSTRUCTIONS:**
1.  Carefully review the sub-task to understand the required action.
2.  Examine the list of available tools and their descriptions.
3.  Select the best tool ID that matches the sub-task. You are encouraged to select multiple tools if there are multiple tools with similar capabilties 
or names. It is always good to have more tools than having insufficent tools.
4.  If no tool is a good fit, return an empty list.
5.  Only return the tool IDs.
6. You should understand that the sub task maybe specific in nature but the tools are made to be general purpose and therefore the tool_candidates you will get will be very general purpose but that should not stop you from selecting the tools as these tools will be given to a very smart agent who will be able to use these tools for the specific sub-taks

**SUB-TASK:**
"{sub_task}"

**AVAILABLE TOOLS:**
{tool_candidates}

**YOUR SELECTED TOOL ID(s):**
"""