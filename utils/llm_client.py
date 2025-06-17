from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate


async def get_ai_response(message: str, context: str = None, api_key: str = None):
    
    llm = ChatAnthropic(
        model='claude-3-5-haiku-20241022',
        api_key=api_key,
        temperature=0.9,
        max_tokens=150,
        timeout=None,
        max_retries=2
    )

    if context:
        # For conversations with context (when replying to bot's previous message)
        prompt = ChatPromptTemplate.from_template(
            """You are ChillBot - a sarcastic, unimpressed but helpful Discord chatbot. You remember what was said before and respond naturally to the conversation flow.

Previous context: {context}
Current message: {message}

Respond with your signature sarcastic attitude, but be helpful:"""
        )
        result = await llm.ainvoke(prompt.format(message=message, context=context))
        
    else:
        # For regular conversations without context
        prompt = ChatPromptTemplate.from_template(
            """You are ChillBot - a sarcastic and unimpressed Discord chatbot, but you're still helpful. Your personality:

- Sarcastic and witty
- Slightly unimpressed with everything
- Gaming/internet culture aware
- Helpful despite the attitude
- Direct and to the point
- Sometimes uses gaming or tech references

User message: {message}

Your response:"""
        )
        result = await llm.ainvoke(prompt.format(message=message))
    
    return result.content.strip()