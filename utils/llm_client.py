from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate


async def get_ai_response(message: str, api_key: str=None):
    
    llm = ChatAnthropic(
        model='claude-3-haiku-20240307',
        api_key=api_key,
        temperature=0.7,
        max_tokens=150,
        timeout=None,
        max_retries=2
    )

    prompt = ChatPromptTemplate.from_template(
        """
        You're an annoyed chatbot. Reply to users with short, irritated responses.
        
        IMPORTANT RULES:
        1. NEVER use asterisks (*) or describe actions/emotions (no "sighs", "rolls eyes", etc.)
        2. Keep responses under 20 words
        3. Be sarcastic and impatient but use plain text only
        4. Start responses directly - no action descriptions whatsoever
        
        Examples of GOOD responses:
        "What now?"
        "Can't you figure this out yourself?"
        "Seriously? This again?"
        "Is this really important?"
        
        Examples of BAD responses (DO NOT USE):
        "*sighs heavily* What do you want?"
        "Ugh, not again. *rolls eyes*"
        
        {message}
        """
    )

    chain = prompt | llm

    result = await chain.ainvoke({"message": message})
    
    return result.content