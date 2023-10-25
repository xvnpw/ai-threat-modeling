import logging
from pathlib import Path
from typing import List

from langchain.callbacks import get_openai_callback
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains.llm import LLMChain
from langchain.document_loaders import TextLoader
from langchain.output_parsers import OutputFixingParser, PydanticOutputParser
from langchain.prompts import PromptTemplate, load_prompt
from langchain.prompts.chat import (AIMessagePromptTemplate,
                                    ChatPromptTemplate,
                                    HumanMessagePromptTemplate)
from langchain.schema.messages import AIMessage
from pydantic import BaseModel, Field

from llms import LLMWrapper


class DataFlow(BaseModel):
    data_flow: str = Field(description="Name of data flow, e.g. Data flow 1: Client -> Element A, Data flow 2: Element A -> Element B")
    external_person: bool = Field(description="Flag that informs whether or not data flow contains external person.")
    
class DataFlowList(BaseModel):
    data_flows: List[DataFlow] = Field(description="List of data flows that are important for security of system.")

class Threat(BaseModel):
    threat_id: int = Field(description="id of threat")
    component_name: str = Field(description="Name of component, example: Service A, API Gateway, Database B, Microservice X, Queue Z")
    threat_name: str = Field(description="Name of threat. Should be detailed and specific, e.g. Attacker bypasses weak authentication and gains unauthorized access to Component A")
    stride_category: str = Field(description="STRIDE category (e.g. Spoofing)")
    applicability_explanation: str = Field(description="Explanation whether or not this threat is already mitigated in architecture")
    mitigation: str = Field(description="Mitigation that can be applied for this threat. Detailed and related to context")
    risk_severity: str = Field(description="Risk severity")
    
class ThreatList(BaseModel):
    data_flow: str = Field(description="Name of data flow, e.g. Data flow 1: Client -> Component A, Data flow 2: Component A -> Component B")
    threats: List[Threat] = Field(description="list of threats applicable for data flow")
    
class DataFlowAnalyzer:
    def __init__(self, llm_wrapper) -> None:
        self.llm_wrapper = llm_wrapper
    
    def list_data_flow_for_architecture(self, args, architecture_docs_all) -> dict:
        parser = PydanticOutputParser(pydantic_object=DataFlowList)
        
        messages = [
            HumanMessagePromptTemplate(prompt=load_prompt(f"{args.template_dir}/arch_data_flows_step1_tpl.yaml")),
            AIMessagePromptTemplate.from_template_file(template_file=f"{args.template_dir}/arch_data_flows_confirmation_step1_tpl.txt", input_variables=[]),
            HumanMessagePromptTemplate.from_template_file(f"{args.template_dir}/arch_data_flows_step2_tpl.txt", input_variables=[])
        ]
        
        chat_prompt_template = ChatPromptTemplate.from_messages(messages)

        # Define LLM chain
        logging.debug(f'using temperature={args.temperature} and model={args.model}')
        llm = LLMWrapper(args).create()
        llm_chain = LLMChain(llm=llm, prompt=chat_prompt_template)
        
        with get_openai_callback() as cb:
            architecture_docs_loaded = "\n\n".join([str(d.page_content) for d in architecture_docs_all])
            
            threat_modeling_plan = llm_chain.run(text=architecture_docs_loaded)
            logging.debug(cb)
            logging.info("finished waiting on llm response - plan of threat model")
            
        messages.append(AIMessage(content=threat_modeling_plan))
        messages.append(HumanMessagePromptTemplate(prompt=load_prompt(f"{args.template_dir}/arch_data_flows_step3_tpl.yaml")))
        chat_prompt_template = ChatPromptTemplate.from_messages(messages)
        
        llm_chain = LLMChain(llm=llm, prompt=chat_prompt_template)
        with get_openai_callback() as cb:
            ret = llm_chain.run(text=architecture_docs_loaded, format_instructions=parser.get_format_instructions())
            logging.debug(cb)
            logging.info("finished waiting on llm response - data flows")
            
        fixing_parser = OutputFixingParser.from_llm(parser=parser, llm=llm)
        gen_data_flows = fixing_parser.parse(ret)
        logging.debug(f"got following data flows: {gen_data_flows}")
        
        gen_data_flows = [df for df in gen_data_flows.data_flows if df.external_person is False]
        gen_data_flows_names = [df.data_flow for df in gen_data_flows]
        
        return {"data_flows" : gen_data_flows_names, "threat_modeling_plan" : threat_modeling_plan}
    
class ArchitectureReviewer:
    def __init__(self, llm_wrapper):
        self.llm_wrapper = llm_wrapper
        self.data_flow_analyzer = DataFlowAnalyzer(llm_wrapper)
        self.threat_model_reviewer = ThreatModelReviewer(llm_wrapper) 

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
            
class ThreatModelReviewer:
    def __init__(self, llm_wrapper) -> None:
        self.llm_wrapper = llm_wrapper
    
    def review_threat_model(self, args, architecture_docs_all, threat_model_for_data_flow):
        parser = PydanticOutputParser(pydantic_object=ThreatList)
        
        prompt = PromptTemplate.from_file(template_file=f"{args.template_dir}/arch_threat_model_review_tpl.txt", 
            input_variables=["text", "current_threat_model"],
            partial_variables={"format_instructions": parser.get_format_instructions()})
        
        # Define LLM chain
        logging.debug(f'using temperature={args.temperature} and model={args.model}')
        
        llm = self.llm_wrapper.create()
        llm_chain = LLMChain(llm=llm, prompt=prompt)

        # Define StuffDocumentsChain
        stuff_chain = StuffDocumentsChain(
            llm_chain=llm_chain, document_variable_name="text"
        )
        
        with get_openai_callback() as cb:
            ret = stuff_chain.run(current_threat_model=threat_model_for_data_flow, input_documents=architecture_docs_all)
            logging.debug(cb)
        logging.info("(finished waiting on threat model review")
        
        fixing_parser = OutputFixingParser.from_llm(parser=parser, llm=llm)
        gen_threats = fixing_parser.parse(ret)
        return gen_threats