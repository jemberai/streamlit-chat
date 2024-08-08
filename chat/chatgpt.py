import logging
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.chat_models import ChatOpenAI

class ChatGPT():
    def __init__(self, retriever) -> None:
        self.retriever = retriever

    def ask_llm(self, prompt):
        template = """Answer the question based only on the following context:

        {context}

        Question: {question}
        """
        llm_model = os.environ["LLM_MODEL"]
        template = ChatPromptTemplate.from_template(template)
        model = ChatOpenAI(temperature=0, model=llm_model)

        def format_docs(docs):
            return "\n\n".join([d.page_content for d in docs])

        chain = (
            {"context": self.retriever | format_docs, "question": RunnablePassthrough()}
            | template
            | model
            | StrOutputParser()
        )

        chain_resp = chain.invoke(prompt)
        logging.warn(chain_resp)

        return chain_resp