from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate


async def get_ai_response(message: str, context: str = None, api_key: str = None):
    
    llm = ChatAnthropic(
        model='claude-3-5-haiku-20241022',  # Updated to 3.5 Haiku for better creativity
        api_key=api_key,
        temperature=0.9,  # Increased for maximum creativity and edge
        max_tokens=120,   # Slightly increased for more elaborate roasts
        timeout=None,
        max_retries=2
    )

    # Check if this is a roast request
    is_roast = "roast" in message.lower() or (context and "roast" in context.lower())

    if is_roast:
        # For roasts, use a more structured prompt that separates target from topic
        prompt = ChatPromptTemplate.from_template(
            """You are ChillBot, a witty roast comedian. You deliver clever, sharp-tongued humor that's brutal but hilarious. Think of the best Comedy Central roasts or gaming trash talk.

Your style:
- Wickedly clever wordplay and observations
- Creative comparisons and metaphors
- Sharp but ultimately harmless humor
- Internet/gaming culture references when relevant
- Make people laugh while giving them a good burn

Target: {instructions}

Deliver your signature roast:"""
        )
        
    elif context:
        # For regular conversations with context
        prompt = ChatPromptTemplate.from_template(
            """You are ChillBot - sarcastic, unimpressed, but helpful. You remember what was said before.

What happened before: {context}
Current message: {message}

Respond with your signature attitude:"""
        )
        
    else:
        # For regular conversations without context
        prompt = ChatPromptTemplate.from_template(
            """You are ChillBot - sarcastic and unimpressed but you answer questions. Be direct and snarky.

User: {message}

Your response:"""
        )

    chain = prompt | llm
    
    if is_roast:
        # For roasts, pass the instructions as a single parameter
        result = await chain.ainvoke({"instructions": message})
    elif context:
        result = await chain.ainvoke({"message": message, "context": context})
    else:
        result = await chain.ainvoke({"message": message})
    
    return result.content.strip()