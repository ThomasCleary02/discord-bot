from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate


async def get_ai_response(message: str, context: str, api_key: str=None):
    
    llm = ChatAnthropic(
        model='claude-3-haiku-20240307',
        api_key=api_key,
        temperature=0.8,  # Increased for more creativity
        max_tokens=100,   # Reduced to force conciseness
        timeout=None,
        max_retries=2
    )

    # Check if this is a roast request
    is_roast = "roast" in message.lower() or (context and "roast" in context.lower())

    if is_roast:
        prompt = ChatPromptTemplate.from_template(
            """You are ChillBot. Give a direct, savage roast. No explanations, no setup, just the roast.

Examples:
"Your Lakers fandom is like their championship hopes - stuck in the past and getting more delusional every year."
"Your gaming skills are so bad, NPCs feel sorry for you."
"You code like you're trying to solve a Rubik's cube with your feet - chaotic and painful to watch."

Roast this: {message}
Context: {context}

Just the roast, nothing else:"""
        )
        
    elif context:
        prompt = ChatPromptTemplate.from_template(
            """You are ChillBot - sarcastic, unimpressed, but helpful. Respond directly with attitude.

Previous: {context}
User: {message}

Your response:"""
        )
        
    else:
        prompt = ChatPromptTemplate.from_template(
            """You are ChillBot - sarcastic and unimpressed but you answer questions. Be direct and snarky.

User: {message}

Your response:"""
        )

    chain = prompt | llm
    
    if context:
        result = await chain.ainvoke({"message": message, "context": context})
    else:
        result = await chain.ainvoke({"message": message})
    
    return result.content.strip()