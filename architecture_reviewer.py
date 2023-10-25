import logging
from pathlib import Path

from langchain.callbacks import get_openai_callback
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains.llm import LLMChain
from langchain.document_loaders import TextLoader
from langchain.prompts import PromptTemplate

class ArchitectureReviewer:
    def __init__(self, llm_wrapper):
        self.llm_wrapper = llm_wrapper

    def review_architecture(self, args, inputs: Path, output: Path):
        logging.info("review of architecture started...")
        logging.debug(f"loading file: {inputs}...")
        
        loader = TextLoader(str(inputs.resolve()))
        arch_doc = loader.load()
        
        prompt = PromptTemplate.from_file(template_file=f"{args.template_dir}/arch_review_tpl.txt", 
            input_variables=["text"])
        
        # Define LLM chain
        logging.debug(f'using temperature={args.temperature} and model={args.model}')
        
        llm = self.llm_wrapper.create()
        llm_chain = LLMChain(llm=llm, prompt=prompt)

        # Define StuffDocumentsChain
        stuff_chain = StuffDocumentsChain(
            llm_chain=llm_chain, document_variable_name="text"
        )
        
        with get_openai_callback() as cb:
            ret = stuff_chain.run(arch_doc)
            logging.debug(cb)
        logging.info("finished waiting on llm response")
            
        return self._saveOutput(ret, output)

    def _saveOutput(self, review: str, output):
        with open(str(output.resolve()), "w") as f:
            f.write("# (AI Generated) Architecture Review\n\n")
            f.write(review)
                    
            f.close()
            logging.info("response written to file")
            