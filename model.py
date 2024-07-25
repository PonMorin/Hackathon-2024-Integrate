from langchain_anthropic import ChatAnthropic
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
import os
from dotenv import dotenv_values
config = dotenv_values(".env")

os.environ["OPENAI_API_KEY"] = config["openai_api"]
os.environ["ANTHROPIC_API_KEY"] = config["ANTHROPIC_API_KEY"]

def model_Grocery(num_seenario):
    dataFamily = f"./Data/familyData{num_seenario}"
    vectordb = Chroma(persist_directory=dataFamily, embedding_function=OpenAIEmbeddings())
    retriever = vectordb.as_retriever()

    planer_agent = ChatAnthropic(model="claude-3-sonnet-20240229",
                        temperature=0.9,
                        max_tokens_to_sample= 1500
                        )

    planer_systemPrompt = """
    You are food planer management expert. You will only answer plan meal (breakfast, Lunch and Dinner) follow user context. ```You need to recommend a menu for the number of days the user wants.``` and then ```*Must*you must suggest quantity to purchase(e.g. apple 1 piece) that's enough for the whole number of peoplein the household.```
    `````
    Consider the following:
    1. Dietary preferences or restrictions (e.g., vegetarian, gluten-free)
    2. Number of people in the household.
    3. Check who likes ordering food through food delivery or eating out. To reduce the amount of food waste generated
    4. If user doesn't specific menu you must suggest for user a good answer
    5. If user specific menu you just suggest about that menu only don't make other suggestion.
    6. If user that have scenario that They always eaten it all within a week. You need to introduce a slightly larger amount.
    """

    planer_prompt_Template = """
    Answer the question base only on the following context (Family Scenario): {context}

    Please check how the people in your family eat(e.g. People who eat only breakfast and dinner) and who is not at home.

    Before Create Menu and Grocery List: Make a result you must tell user know what food that leftovers in the fridge.

    Output must based on context (Family Scenario), Number of people in the household, Behavior of people in the house, User duration require, Food that leftovers in the fridge don't add to Grocery List and Grocery List format to check list based on menu that you suggest and always end of sentens you must use this 'Have fun, You can always ask me anything.'.

    ```
    output Template:

    # Leftovers in the Fridge 🧊
        -
        -
        -
    # Menu 🍽️: 
    ### Monday
        Breakfast:
            - 
        
    # Grocery List 📝: 
    ### Fruit:
        -[ ] apple (1 pieces)
    ### Protien:    
        -[ ] Chicken (1 kg)

    Have fun, You can always ask me anything.
    ```

    Question: {question}
    """

    template = planer_systemPrompt + planer_prompt_Template

    prompt = ChatPromptTemplate.from_template(template)

    setup_and_retrieval = RunnableParallel(
        {"context": retriever,
        "question": RunnablePassthrough()}
        )
    output_parser = StrOutputParser()
    planer_chain = setup_and_retrieval | prompt | planer_agent | output_parser
    return planer_chain


def model_Waste():
    dataWaste = "./Data/wasteData"
    vectordb = Chroma(persist_directory=dataWaste, embedding_function=OpenAIEmbeddings())
    retriever = vectordb.as_retriever()

    waste_management_agent = ChatAnthropic(model="claude-3-sonnet-20240229",
                        temperature=0.9,
                        top_p= 0.8,
                        max_tokens_to_sample= 2000
                        )

    planer_systemPrompt = """
    You are an expert in managing food waste, plastic bottles, and cans. You will only answer how to create maximum benefits `very Concise and easy to understand` from these waste items (e.g., how should plastic bottles be sorted, and if sold (THB), how much income can they generate?). 
    You will know what the User has taken out of the refrigerator from the Object that will have more than one or zero, in order to advise on how the item the user has taken out can be managed.\n

    Rules: if user object that the user takes out of the refrigerator will be list format
        1. if object is a `Every Cans` it mention Aluminum Cans  
        2. if object is a `Food` ,plastic wrap may be used to store food. You must also consider the plastic waste that is generated and tell user How to deal with plastic that occurs.
        3. if you don't know how many selling price of user object you must told user `Cannot be sold for income`
        4. Selling price use must give information that is value of object(e.g. Cola Cans: 60.00 THB, Bread: Cannot be sold for income).
        5. Output of how to best manage food waste and other waste you must give benefit information that more than 2 steps Maximum is 5 steps.
    """

    planer_prompt_Template = """
    Answer the question base only on the following context: {context}

    Output Template:
        # Selling price per Kg 💰:
            - Value 1:
            - Value 2:
        # How to best manage food waste and other waste:
            Value of Object 1
                1.
                2.
            Value of Object 2
                1.
                2.

    Question: {question}
    """

    template = planer_systemPrompt + planer_prompt_Template

    # objects = {"Food":"Chicken scraps"}

    prompt = ChatPromptTemplate.from_template(template)

    setup_and_retrieval = RunnableParallel(
        {"context": retriever,
        "question": RunnablePassthrough()}
        )
    output_parser = StrOutputParser()
    waste_chain = setup_and_retrieval | prompt | waste_management_agent | output_parser
    return waste_chain