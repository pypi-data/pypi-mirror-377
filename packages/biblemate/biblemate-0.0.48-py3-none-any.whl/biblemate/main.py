from biblemate.core.systems import *
from biblemate.ui.prompts import getInput
from biblemate.ui.info import get_banner
from biblemate.ui.selection_dialog import TerminalModeDialogs
from biblemate import config, AGENTMAKE_CONFIG, OLLAMA_NOT_FOUND
from biblemate.core.bible_db import BibleVectorDatabase
from pathlib import Path
import asyncio, re, os, subprocess, click, shutil, pprint
from copy import deepcopy
from alive_progress import alive_bar
from fastmcp import Client
from agentmake import agentmake, getOpenCommand, getDictionaryOutput, edit_configurations, writeTextFile, getCurrentDateTime, AGENTMAKE_USER_DIR, USER_OS, DEVELOPER_MODE, DEFAULT_AI_BACKEND
from rich.console import Console
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.terminal_theme import MONOKAI
if not USER_OS == "Windows":
    import readline  # for better input experience

# bible data
builtin_bible_data = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data", "bibles")
user_bible_data = os.path.join(AGENTMAKE_USER_DIR, "biblemate", "data", "bibles")
Path(user_bible_data).mkdir(parents=True, exist_ok=True)
user_bible = os.path.join(user_bible_data, "NET.bible")
if not os.path.isfile(user_bible):
    print("# Copying bible data ...")
    shutil.copyfile(os.path.join(builtin_bible_data, "NET.bible"), user_bible)
if os.path.isfile(user_bible) and os.path.getsize(user_bible) < 380000000:
    if shutil.which("ollama"):
        print("# Setting up a bible vector database to support semantic search with BibleMate AI. please kindly wait until it is finished ...")
        db = BibleVectorDatabase(user_bible)
        db.add_vectors()
        db.clean_up()
        del db
    else:
        print(OLLAMA_NOT_FOUND)

# The client that interacts with the Bible Study MCP server
builtin_mcp_server = os.path.join(os.path.dirname(os.path.realpath(__file__)), "bible_study_mcp.py")
user_mcp_server = os.path.join(AGENTMAKE_USER_DIR, "biblemate", "bible_study_mcp.py") # The user path has the same basename as the built-in one; users may copy the built-in server settings to this location for customization. 
client = Client(user_mcp_server if os.path.isfile(user_mcp_server) else builtin_mcp_server)

def main():
    asyncio.run(main_async())

async def initialize_app(client):
    """Initializes the application by fetching tools and prompts from the MCP server."""
    await client.ping()

    tools_raw = await client.list_tools()
    tools = {t.name: t.description for t in tools_raw}
    tools = dict(sorted(tools.items()))
    tools_schema = {}
    for t in tools_raw:
        schema = {
            "name": t.name,
            "description": t.description,
            "parameters": {
                "type": "object",
                "properties": t.inputSchema["properties"],
                "required": t.inputSchema["required"],
            },
        }
        tools_schema[t.name] = schema

    available_tools = list(tools.keys())
    if "get_direct_text_response" not in available_tools:
        available_tools.insert(0, "get_direct_text_response")
    master_available_tools = deepcopy(available_tools)

    tool_descriptions = ""
    if "get_direct_text_response" not in tools:
        tool_descriptions = """# TOOL DESCRIPTION: `get_direct_text_response`
Get a static text-based response directly from a text-based AI model without using any other tools. This is useful when you want to provide a simple and direct answer to a question or request, without the need for online latest updates or task execution.\n\n\n"""
    for tool_name, tool_description in tools.items():
        tool_descriptions += f"""# TOOL DESCRIPTION: `{tool_name}`
{tool_description}\n\n\n"""

    prompts_raw = await client.list_prompts()
    prompts = {p.name: p.description for p in prompts_raw}
    prompts = dict(sorted(prompts.items()))

    prompts_schema = {}
    for p in prompts_raw:
        arg_properties = {}
        arg_required = []
        for a in p.arguments:
            arg_properties[a.name] = {
                "type": "string",
                "description": str(a.description) if a.description else "no description available",
            }
            if a.required:
                arg_required.append(a.name)
        schema = {
            "name": p.name,
            "description": p.description,
            "parameters": {
                "type": "object",
                "properties": arg_properties,
                "required": arg_required,
            },
        }
        prompts_schema[p.name] = schema
    
    return tools, tools_schema, master_available_tools, available_tools, tool_descriptions, prompts, prompts_schema

def backup_conversation(console, messages, master_plan):
    """Backs up the current conversation to the user's directory."""
    timestamp = getCurrentDateTime()
    storagePath = os.path.join(AGENTMAKE_USER_DIR, "biblemate", timestamp)
    Path(storagePath).mkdir(parents=True, exist_ok=True)
    # Save full conversation
    conversation_file = os.path.join(storagePath, "conversation.py")
    writeTextFile(conversation_file, pprint.pformat(messages))
    # Save master plan
    writeTextFile(os.path.join(storagePath, "master_plan.md"), master_plan)
    # Save markdown
    markdown_file = os.path.join(storagePath, "conversation.md")
    markdown_text = "\n\n".join([f"```{i["role"]}\n{i["content"]}\n```" for i in messages if i.get("role", "") in ("user", "assistant")])
    writeTextFile(markdown_file, markdown_text)
    # Save html
    html_file = os.path.join(storagePath, "conversation.html")
    console.save_html(html_file, inline_styles=True, theme=MONOKAI)
    # Inform users of the backup location
    print(f"Conversation backup saved to {storagePath}")
    print(f"Report saved to {html_file}\n")

def write_user_config():
    """Writes the current configuration to the user's config file."""
    config_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "config.py")
    configurations = f"""agent_mode={config.agent_mode}
prompt_engineering={config.prompt_engineering}
max_steps={config.max_steps}
hide_tools_order={config.hide_tools_order}
default_bible="{config.default_bible}"
max_semantic_matches={config.max_semantic_matches}"""
    writeTextFile(config_file, configurations)

async def main_async():

    APP_START = True
    DEFAULT_SYSTEM = "You are BibleMate AI, an autonomous agent designed to assist users with their Bible study."
    DEFAULT_MESSAGES = [{"role": "system", "content": DEFAULT_SYSTEM}, {"role": "user", "content": "Hello!"}, {"role": "assistant", "content": "Hello! I'm BibleMate AI, your personal assistant for Bible study. How can I help you today?"}] # set a tone for bible study; it is userful when auto system is used.

    console = Console(record=True)
    console.clear()
    console.print(get_banner())
    dialogs = TerminalModeDialogs(None)

    async with client:
        tools, tools_schema, master_available_tools, available_tools, tool_descriptions, prompts, prompts_schema = await initialize_app(client)
        
        available_tools_pattern = "|".join(available_tools)
        prompt_list = [f"/{p}" for p in prompts.keys()]
        prompt_pattern = "|".join(prompt_list)
        prompt_pattern = f"""^({prompt_pattern}) """

        user_request = ""
        master_plan = ""
        messages = deepcopy(DEFAULT_MESSAGES) # set the tone

        while not user_request == ".quit":

            # spinner while thinking
            async def thinking(process, description=None):
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    transient=True  # This makes the progress bar disappear after the task is done
                ) as progress:
                    # Add an indefinite task (total=None)
                    task_id = progress.add_task(description if description else "Thinking ...", total=None)
                    # Create and run the async task concurrently
                    async_task = asyncio.create_task(process())
                    # Loop until the async task is done
                    while not async_task.done():
                        progress.update(task_id)
                        await asyncio.sleep(0.01)
                await async_task
            # progress bar for processing steps
            async def async_alive_bar(task):
                """
                A coroutine that runs a progress bar while awaiting a task.
                """
                with alive_bar(title="Processing...", spinner='dots') as bar:
                    while not task.done():
                        bar() # Update the bar
                        await asyncio.sleep(0.01) # Yield control back to the event loop
                return task.result()
            async def process_tool(tool, tool_instruction, step_number=None):
                """
                Manages the async task and the progress bar.
                """
                if step_number:
                    print(f"# Starting Step [{step_number}]...")
                # Create the async task but don't await it yet.
                task = asyncio.create_task(run_tool(tool, tool_instruction))
                # Await the custom async progress bar that awaits the task.
                await async_alive_bar(task)

            if not len(messages) == len(DEFAULT_MESSAGES):
                console.rule()
            elif APP_START:
                print()
                APP_START = False
                while True:
                    try:
                        agentmake("Hello!", system=DEFAULT_SYSTEM)
                        break
                    except Exception as e:
                        print("Connection failed! Please ensure that you have a stable internet connection and that my AI backend and model are properly configured.")
                        print("Viist https://github.com/eliranwong/agentmake#supported-backends for help about the backend configuration.\n")
                        if click.confirm("Do you want to configure my AI backend and model now?", default=True):
                            edit_configurations()
                            console.rule()
                            console.print("Restart to make the changes in the backend effective!", justify="center")
                            console.rule()
                            exit()
            # Original user request
            # note: `python3 -m rich.emoji` for checking emoji
            console.print("Enter your request :smiley: :" if len(messages) == len(DEFAULT_MESSAGES) else "Enter a follow-up request :flexed_biceps: :")
            action_list = {
                ".new": "new conversation",
                ".quit": "quit",
                ".backend": "change backend",
                ".mode": "change AI mode",
                ".tools": "list available tools",
                ".plans": "list available plans",
                #".resources": "list available resources", # TODO explore relevant usage for this project
                ".promptengineering": "toggle auto prompt engineering",
                ".steps": "configure the maximum number of steps",
                ".matches": "configure the maximum number of semantic matches",
                ".backup": "backup conversation",
                ".load": "load a saved conversation",
                ".open": "open a file or directory",
                ".help": "help page",
            }
            input_suggestions = list(action_list.keys())+[f"@{t} " for t in available_tools]+prompt_list
            user_request = await getInput("> ", input_suggestions)
            while not user_request.strip():
                # Generate ideas for `prompts to try`
                ideas = ""
                async def generate_ideas():
                    nonlocal ideas
                    if len(messages) == len(DEFAULT_MESSAGES):
                        ideas = agentmake("Generate three `prompts to try` for bible study. Each one should be one sentence long.", **AGENTMAKE_CONFIG)[-1].get("content", "").strip()
                    else:
                        ideas = agentmake(messages, follow_up_prompt="Generate three follow-up questions according to the on-going conversation.", **AGENTMAKE_CONFIG)[-1].get("content", "").strip()
                await thinking(generate_ideas, "Generating ideas ...")
                console.rule()
                console.print(Markdown(f"## Ideas\n\n{ideas}\n\n"))
                console.rule()
                # Get input agin
                user_request = await getInput("> ", input_suggestions)

            # system command
            if user_request == ".open":
                user_request = f".open {os.getcwd()}"
            if user_request.startswith(".open ") and os.path.exists(user_request[6:]):
                cmd = f'''{getOpenCommand()} "{user_request[6:]}"'''
                subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                continue
            elif user_request.startswith(".load") and re.search('''.py['" ]*?$''', user_request) and os.path.isfile(re.sub('''^['" ]*?([^'" ].+?)['" ]*?$''', r"\1", user_request[6:])):
                try:
                    file_path = re.sub('''^['" ]*?([^'" ].+?)['" ]*?$''', r"\1", user_request[6:])
                    backup_conversation(console, messages, master_plan) 
                    with open(file_path, "r", encoding="utf-8") as f:
                        messages = eval(f.read())
                    user_request = ""
                    master_plan = ""
                    console.clear()
                    console.print(get_banner())
                    if messages:
                        for i in messages:
                            if i.get("role", "") in ("user", "assistant"):
                                console.rule()
                                console.print(Markdown(f"# {i['role']}\n\n{i['content']}"))
                    continue
                except Exception as e:
                    pass

            # predefined operations with `.` commands
            if user_request in action_list:
                if user_request == ".backup":
                    backup_conversation(console, messages, master_plan)
                elif user_request == ".help":
                    console.rule()
                    console.print(Markdown("Viist https://github.com/eliranwong/biblemate for help."))
                    console.rule()
                elif user_request == ".tools":
                    enabled_tools = await dialogs.getMultipleSelection(
                        default_values=available_tools,
                        options=master_available_tools,
                        title="Tool Options",
                        text="Select tools to enable:"
                    )
                    if enabled_tools is not None:
                        available_tools = enabled_tools
                    console.rule()
                    tools_descriptions = [f"- `{name}`: {description}" for name, description in tools.items()]
                    console.print(Markdown("## Available Tools\n\n"+"\n".join(tools_descriptions)))
                    console.rule()
                elif user_request == ".plans":
                    console.rule()
                    prompts_descriptions = [f"- `{name}`: {description}" for name, description in prompts.items()]
                    console.print(Markdown("## Available Plans\n\n"+"\n".join(prompts_descriptions)))
                    console.rule()
                elif user_request == ".backend":
                    edit_configurations()
                    console.rule()
                    console.print("Restart to make the changes in the backend effective!", justify="center")
                    console.rule()
                elif user_request == ".steps":
                    console.rule()
                    console.print("Enter below the maximum number of steps allowed:")
                    max_steps = await getInput("> ", number_validator=True, default_entry=str(config.max_steps))
                    if max_steps:
                        config.max_steps = int(max_steps)
                        write_user_config()
                        console.print("Maximum number of steps set to", config.max_steps, justify="center")
                    console.rule()
                elif user_request == ".matches":
                    console.rule()
                    console.print("Enter below the maximum number of semantic matches allowed:")
                    max_semantic_matches = await getInput("> ", number_validator=True, default_entry=str(config.max_semantic_matches))
                    if max_semantic_matches:
                        config.max_semantic_matches = int(max_semantic_matches)
                        write_user_config()
                        console.print("Maximum number of semantic matches set to", config.max_semantic_matches, justify="center")
                    console.rule()
                elif user_request == ".promptengineering":
                    config.prompt_engineering = not config.prompt_engineering
                    write_user_config()
                    console.rule()
                    console.print("Prompt Engineering Enabled" if config.prompt_engineering else "Prompt Engineering Disabled", justify="center")
                    console.rule()
                elif user_request == ".mode":
                    default_ai_mode = "chat" if config.agent_mode is None else "agent" if config.agent_mode else "partner"
                    ai_mode = await dialogs.getValidOptions(
                        default=default_ai_mode,
                        options=["agent", "partner", "chat"],
                        descriptions=["Fully automated", "Semi-automated, with review and edit prompts", "Direct text responses"],
                        title="AI Modes",
                        text="Select an AI mode:"
                    )
                    if ai_mode:
                        if ai_mode == "agent":
                            config.agent_mode = True
                        elif ai_mode == "partner":
                            config.agent_mode = False
                        else:
                            config.agent_mode = None
                        write_user_config()
                        console.rule()
                        console.print(f"`{ai_mode.capitalize()}` Mode Enabled", justify="center")
                        console.rule()
                elif user_request in (".new", ".quit"):
                    backup_conversation(console, messages, master_plan) # backup
                # reset
                if user_request == ".new":
                    user_request = ""
                    master_plan = ""
                    messages = deepcopy(DEFAULT_MESSAGES)
                    console.clear()
                    console.print(get_banner())
                continue

            # Check if a single tool is specified
            specified_prompt = ""
            specified_tool = ""
            if re.search(prompt_pattern, user_request):
                specified_prompt = re.search(prompt_pattern, user_request).group(1)
                user_request = user_request[len(specified_prompt):]
            elif re.search(f"""^@({available_tools_pattern}) """, user_request):
                specified_tool = re.search(f"""^@({available_tools_pattern}) """, user_request).group(1)
                user_request = user_request[len(specified_tool)+2:]
            elif user_request.startswith("@@"):
                specified_tool = "@@"
                master_plan = user_request[2:].strip()
                async def refine_custom_plan():
                    nonlocal messages, user_request, master_plan
                    # Summarize user request in one-sentence instruction
                    user_request = agentmake(master_plan, tool="biblemate/summarize_task_instruction", **AGENTMAKE_CONFIG)[-1].get("content", "").strip()
                    if "```" in user_request:
                        user_request = re.sub(r"^.*?(```instruction|```)(.+?)```.*?$", r"\2", user_request, flags=re.DOTALL).strip()
                await thinking(refine_custom_plan)
                # display info
                console.print(Markdown(f"# User Request\n\n{user_request}\n\n# Master plan\n\n{master_plan}"))

            # Prompt Engineering
            if not specified_tool == "@@" and config.prompt_engineering:
                async def run_prompt_engineering():
                    nonlocal user_request
                    try:
                        user_request = agentmake(messages if messages else user_request, follow_up_prompt=user_request if messages else None, tool="improve_prompt", **AGENTMAKE_CONFIG)[-1].get("content", "").strip()
                        if "```" in user_request:
                            user_request = re.sub(r"^.*?(```improved_version|```)(.+?)```.*?$", r"\2", user_request, flags=re.DOTALL).strip()
                    except:
                        user_request = agentmake(messages if messages else user_request, follow_up_prompt=user_request if messages else None, system="improve_prompt_2")[-1].get("content", "").strip()
                        user_request = re.sub(r"^.*?(```improved_prompt|```)(.+?)```.*?$", r"\2", user_request, flags=re.DOTALL).strip()
                await thinking(run_prompt_engineering, "Prompt Engineering ...")

            if not messages:
                messages = [
                    {"role": "system", "content": DEFAULT_SYSTEM},
                    {"role": "user", "content": user_request},
                ]
            else:
                messages.append({"role": "user", "content": user_request})

            async def run_tool(tool, tool_instruction):
                nonlocal messages
                if tool == "get_direct_text_response":
                    messages = agentmake(messages, system="auto", **AGENTMAKE_CONFIG)
                else:
                    try:
                        tool_schema = tools_schema[tool]
                        tool_properties = tool_schema["parameters"]["properties"]
                        if len(tool_properties) == 1 and "request" in tool_properties: # AgentMake MCP Servers or alike
                            tool_result = await client.call_tool(tool, {"request": tool_instruction})
                        else:
                            structured_output = getDictionaryOutput(messages=messages, schema=tool_schema, backend=DEFAULT_AI_BACKEND)
                            tool_result = await client.call_tool(tool, structured_output)
                        tool_result = tool_result.content[0].text
                        messages[-1]["content"] += f"\n\n[Using tool `{tool}`]"
                        messages.append({"role": "assistant", "content": tool_result if tool_result.strip() else "Tool error!"})
                    except Exception as e:
                        if DEVELOPER_MODE:
                            console.print(f"Error: {e}\nFallback to direct response...\n\n")
                        messages = agentmake(messages, system="auto", **AGENTMAKE_CONFIG)

            # user specify a single tool
            if specified_tool and not specified_tool == "@@":
                await process_tool(specified_tool, user_request)
                console.print(Markdown(f"# User Request\n\n{messages[-2]['content']}\n\n# AI Response\n\n{messages[-1]['content']}"))
                continue

            # Chat mode
            if config.agent_mode is None and not specified_tool == "@@":
                async def run_chat_mode():
                    nonlocal messages, user_request
                    messages = agentmake(messages if messages else user_request, system="auto", **AGENTMAKE_CONFIG)
                await thinking(run_chat_mode)
                console.print(Markdown(f"# User Request\n\n{messages[-2]['content']}\n\n# AI Response\n\n{messages[-1]['content']}"))
                continue

            # agent mode or partner mode

            # generate master plan
            if not master_plan:
                if specified_prompt:
                    # Call the MCP prompt
                    prompt_schema = prompts_schema[specified_prompt[1:]]
                    prompt_properties = prompt_schema["parameters"]["properties"]
                    if len(prompt_properties) == 1 and "request" in prompt_properties: # AgentMake MCP Servers or alike
                        result = await client.get_prompt(specified_prompt[1:], {"request": user_request})
                    else:
                        structured_output = getDictionaryOutput(messages=messages, schema=prompt_schema, backend=DEFAULT_AI_BACKEND)
                        result = await client.get_prompt(specified_prompt[1:], structured_output)
                    #print(result, "\n\n")
                    master_plan = result.messages[0].content.text
                    # display info# display info
                    console.print(Markdown(f"# User Request\n\n{user_request}\n\n# Master plan\n\n{master_plan}"))
                else:
                    # display info
                    console.print(Markdown(f"# User Request\n\n{user_request}"), "\n")
                    # Generate master plan
                    master_plan = ""
                    async def generate_master_plan():
                        nonlocal master_plan
                        # Create initial prompt to create master plan
                        initial_prompt = f"""Provide me with the `Preliminary Action Plan` and the `Measurable Outcome` for resolving `My Request`.
    
# Available Tools

Available tools are: {available_tools}.

{tool_descriptions}

# My Request

{user_request}"""
                        console.print(Markdown("# Master plan"), "\n")
                        print()
                        master_plan = agentmake(messages+[{"role": "user", "content": initial_prompt}], system="create_action_plan", **AGENTMAKE_CONFIG)[-1].get("content", "").strip()
                    await thinking(generate_master_plan)

                    # partner mode
                    if config.agent_mode == False:
                        console.rule()
                        console.print(Markdown("# Review & Confirm"))
                        console.print("Please review and confirm the master plan, or make any changes you need:", justify="center")
                        console.rule()
                        master_plan_edit = await getInput(default_entry=master_plan)
                        if not master_plan_edit or master_plan_edit == ".quit":
                            if messages and messages[-1].get("role", "") == "user":
                                messages = messages[:-1]
                            console.rule()
                            console.print("I've stopped processing for you.")
                            continue
                        else:
                            master_plan_edit = master_plan_edit
                        console.rule()

                    # display info
                    console.print(Markdown(master_plan), "\n\n")

            # Step suggestion system message
            system_progress = get_system_progress(original_request=user_request, master_plan=master_plan)
            system_make_suggestion = get_system_make_suggestion(original_request=user_request, master_plan=master_plan)

            # Tool selection systemm message
            system_tool_selection = get_system_tool_selection(available_tools, tool_descriptions)

            # Get the first suggestion
            next_suggestion = "START"

            step = 1
            while not ("STOP" in next_suggestion or re.sub("^[^A-Za-z]*?([A-Za-z]+?)[^A-Za-z]*?$", r"\1", next_suggestion).upper() == "STOP"):

                async def make_next_suggestion():
                    nonlocal next_suggestion, system_make_suggestion, messages, step
                    console.print(Markdown(f"## Suggestion [{step}]"), "\n")
                    next_suggestion = agentmake(user_request if next_suggestion == "START" else [{"role": "system", "content": system_make_suggestion}]+messages[len(DEFAULT_MESSAGES):], system=system_make_suggestion, follow_up_prompt=None if next_suggestion == "START" else "Please provide me with the next step suggestion, based on the action plan.", **AGENTMAKE_CONFIG)[-1].get("content", "").strip()
                await thinking(make_next_suggestion)
                console.print(Markdown(next_suggestion), "\n\n")

                # Get tool suggestion for the next iteration
                suggested_tools = []
                async def get_tool_suggestion():
                    nonlocal suggested_tools, next_suggestion, system_tool_selection
                    if DEVELOPER_MODE and not config.hide_tools_order:
                        console.print(Markdown(f"## Tool Selection (descending order by relevance) [{step}]"), "\n")
                    else:
                        console.print(Markdown(f"## Tool Selection [{step}]"), "\n")
                    # Extract suggested tools from the step suggestion
                    suggested_tools = agentmake(next_suggestion, system=system_tool_selection, **AGENTMAKE_CONFIG)[-1].get("content", "").strip() # Note: suggested tools are printed on terminal by default, could be hidden by setting `print_on_terminal` to false
                    suggested_tools = re.sub(r"^.*?(\[.*?\]).*?$", r"\1", suggested_tools, flags=re.DOTALL)
                    try:
                        suggested_tools = eval(suggested_tools.replace("`", "'")) if suggested_tools.startswith("[") and suggested_tools.endswith("]") else ["get_direct_text_response"] # fallback to direct response
                    except:
                        suggested_tools = ["get_direct_text_response"]
                await thinking(get_tool_suggestion)
                if DEVELOPER_MODE and not config.hide_tools_order:
                    console.print(Markdown(str(suggested_tools)))

                # Use the next suggested tool
                # partner mode
                if config.agent_mode:
                    next_tool = suggested_tools[0] if suggested_tools else "get_direct_text_response"
                else: # `partner` mode when config.agent_mode is set to False
                    next_tool = await dialogs.getValidOptions(options=suggested_tools if suggested_tools else available_tools, title="Suggested Tools", text="Select a tool:")
                prefix = f"## Next Tool [{step}]\n\n" if DEVELOPER_MODE and not config.hide_tools_order else ""
                console.print(Markdown(f"{prefix}`{next_tool}`"))
                print()

                # Get next step instruction
                next_step = ""
                async def get_next_step():
                    nonlocal next_step, next_tool, next_suggestion, tools
                    console.print(Markdown(f"## Next Instruction [{step}]"), "\n")
                    if next_tool == "get_direct_text_response":
                        next_step = agentmake(next_suggestion, system="biblemate/direct_instruction", **AGENTMAKE_CONFIG)[-1].get("content", "").strip()
                    else:
                        next_tool_description = tools.get(next_tool, "No description available.")
                        system_tool_instruction = get_system_tool_instruction(next_tool, next_tool_description)
                        next_step = agentmake(next_suggestion, system=system_tool_instruction, **AGENTMAKE_CONFIG)[-1].get("content", "").strip()
                await thinking(get_next_step)
                # partner mode
                if config.agent_mode == False:
                    console.rule()
                    console.print(Markdown("# Review & Confirm"))
                    console.print("Please review and confirm the next step, or make any changes you need:")
                    console.rule()
                    next_step_edit = await getInput(default_entry=next_step)
                    if not next_step_edit or next_step_edit == ".quit":
                        console.rule()
                        console.print("I've stopped processing for you.")
                        break
                    else:
                        next_step = next_step_edit
                    console.rule()
                console.print(Markdown(next_step), "\n\n")

                if messages[-1]["role"] != "assistant": # first iteration
                    messages.append({"role": "assistant", "content": "Please provide me with an initial instruction to begin."})
                messages.append({"role": "user", "content": next_step})

                await process_tool(next_tool, next_step, step_number=step)
                console.print(Markdown(f"\n## Output [{step}]\n\n{messages[-1]['content']}"))

                # iteration count
                step += 1
                if step > config.max_steps:
                    console.rule()
                    console.print("I've stopped processing for you, as the maximum steps allowed is currently set to", config.max_steps, "steps. Enter `.steps` to configure more.")
                    console.rule()
                    break

                # Get the next suggestion
                async def get_next_suggestion():
                    nonlocal next_suggestion, messages, system_progress
                    next_suggestion = agentmake([{"role": "system", "content": system_progress}]+messages[len(DEFAULT_MESSAGES):], system=system_progress, follow_up_prompt="Please decide either to `CONTINUE` or `STOP` the process.", **AGENTMAKE_CONFIG)[-1].get("content", "").strip()
                await thinking(get_next_suggestion, description="Checking the progress ...")
            
            if messages[-1].get("role") == "user":
                messages.append({"role": "assistant", "content": next_suggestion})
            
            # write the final answer
            console.rule()
            console.print(Markdown("# Wrapping up ..."))
            messages = agentmake(
                messages,
                system="write_final_answer",
                follow_up_prompt=f"""# Instruction
Please provide me with the final answer to my original request based on the work that has been completed.

# Original Request
{user_request}""",
                stream=True)
            console.rule()
            console.print(Markdown(messages[-1]['content']))

            # Backup
            print()
            backup_conversation(console, messages, master_plan)

if __name__ == "__main__":
    asyncio.run(main())
