from autocoder_nano.agent.agentic_ask import AgenticAsk
from autocoder_nano.agent.agentic_edit import AgenticEdit
from autocoder_nano.agent.agentic_cost import AgenticCost
from autocoder_nano.agent.agentic_report import AgenticReport
from autocoder_nano.agent.agentic_edit_types import AgenticEditRequest, AgenticEditConversationConfig
from autocoder_nano.core import AutoLLM
from autocoder_nano.actypes import SourceCodeList, AutoCoderArgs


def run_edit_agentic(llm: AutoLLM, args: AutoCoderArgs, conversation_config: AgenticEditConversationConfig):
    sources = SourceCodeList([])
    agentic_editor = AgenticEdit(
        args=args, llm=llm, files=sources, history_conversation=[], conversation_config=conversation_config,
    )
    request = AgenticEditRequest(user_input=args.query)
    agentic_editor.run_in_terminal(request)


def run_ask_agentic(llm: AutoLLM, args: AutoCoderArgs, conversation_config: AgenticEditConversationConfig):
    sources = SourceCodeList([])
    agentic_asker = AgenticAsk(
        args=args, llm=llm, files=sources, history_conversation=[], conversation_config=conversation_config,
    )
    request = AgenticEditRequest(user_input=args.query)
    agentic_asker.run_in_terminal(request)


def run_cost_agentic(llm: AutoLLM, args: AutoCoderArgs, conversation_config: AgenticEditConversationConfig) -> str:
    sources = SourceCodeList([])
    agentic_coster = AgenticCost(
        args=args, llm=llm, files=sources, history_conversation=[], conversation_config=conversation_config,
    )
    request = AgenticEditRequest(user_input=args.query)
    return agentic_coster.run_in_terminal(request)


def run_report_agentic(llm: AutoLLM, args: AutoCoderArgs, conversation_config: AgenticEditConversationConfig):
    sources = SourceCodeList([])
    agentic_reporter = AgenticReport(
        args=args, llm=llm, files=sources, history_conversation=[], conversation_config=conversation_config,
    )
    request = AgenticEditRequest(user_input=args.query)
    agentic_reporter.run_in_terminal(request)


__all__ = ["run_edit_agentic",
           "AgenticEditConversationConfig",
           "run_ask_agentic",
           "run_cost_agentic",
           "run_report_agentic"]